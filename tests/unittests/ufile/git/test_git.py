"""Unit tests for urgap.ufile.io.git.IOGit using real git repositories."""

import subprocess

from pathlib import Path

import pytest

import urgap

from urgap.ufile.io.git import IOGit


def _git(args: list[str], cwd: Path) -> None:
    """Run a git command in cwd, failing the test on error."""
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture
def remote_repo(tmp_path: Path) -> Path:
    """Create a real bare remote repo seeded with files on branch 'main'.

    Returns:
        Path to the bare repository usable as a clone source.
    """
    work = tmp_path / "work"
    work.mkdir()
    _git(["init", "-b", "main"], cwd=work)
    _git(["config", "user.email", "test@example.com"], cwd=work)
    _git(["config", "user.name", "Test"], cwd=work)
    (work / "README.md").write_text("hello world")
    (work / "sub").mkdir()
    (work / "sub" / "data.txt").write_text("nested content")
    _git(["add", "."], cwd=work)
    _git(["commit", "-m", "init"], cwd=work)

    bare = tmp_path / "remote.git"
    _git(["clone", "--bare", str(work), str(bare)], cwd=tmp_path)
    return bare


@pytest.fixture(autouse=True)
def _clone_disk(tmp_path: Path) -> None:
    """Point git_clone_disk at a temp dir and reset the process refresh cache."""
    urgap.config["git_clone_disk"] = str(tmp_path / "clones")
    IOGit._refreshed.clear()


def _make_io(fragment: str, remote: Path, query: str = "") -> IOGit:
    """Build an IOGit for a file, pointing the clone source at the local remote."""
    query_part = f"?{query}" if query else ""
    uri = f"git://github.com/testorg/testrepo/main{query_part}#{fragment}"
    io = IOGit(uuri=urgap.UUri(uri=uri))
    io.remote_url = str(remote)
    return io


def test_download_reads_from_clone(remote_repo: Path) -> None:
    """Download copies the file contents from the local checkout."""
    io = _make_io("README.md", remote_repo)
    io.download()
    assert io.scratch_path.read_text() == "hello world"


def test_force_deletes_and_reclones(remote_repo: Path) -> None:
    """force query param wipes the existing clone and clones again."""
    io1 = _make_io("README.md", remote_repo)
    io1.download()
    marker = io1.clone_dir / "local_only.txt"
    marker.write_text("stale")

    io2 = _make_io("README.md", remote_repo, query="force=True")
    io2.download()

    assert io2.scratch_path.read_text() == "hello world"
    # Force wiped the previous clone, so the stale marker is gone.
    assert not marker.exists()


def test_force_purges_scratch_copy(remote_repo: Path) -> None:
    """force drops any cached scratch copy so the file is re-fetched."""
    io1 = _make_io("README.md", remote_repo)
    io1.download()
    assert io1.scratch_path.exists()

    io2 = _make_io("README.md", remote_repo, query="force=True")
    # Constructing with force must have removed the shared scratch copy.
    assert not io2.scratch_path.exists()


def test_download_nested_file(remote_repo: Path) -> None:
    """Download works for a nested file path."""
    io = _make_io("sub/data.txt", remote_repo)
    io.download()
    assert io.scratch_path.read_text() == "nested content"


def test_remote_object_exists(remote_repo: Path) -> None:
    """remote_object_exists reflects presence in the checkout."""
    assert _make_io("README.md", remote_repo).remote_object_exists() is True
    assert _make_io("missing.txt", remote_repo).remote_object_exists() is False


def test_download_missing_raises(remote_repo: Path) -> None:
    """Download raises RuntimeError when the file is absent."""
    io = _make_io("missing.txt", remote_repo)
    with pytest.raises(RuntimeError, match="Unable to find"):
        io.download()


def test_list_container_items(remote_repo: Path) -> None:
    """list_container_items returns git URIs for tracked files, skipping .git."""
    items = _make_io("README.md", remote_repo).list_container_items()
    assert (
        "git://github.com/testorg/testrepo/main#README.md" in items
    )
    assert "git://github.com/testorg/testrepo/main#sub/data.txt" in items
    assert all(".git/" not in item for item in items)


def test_list_container_items_pattern(remote_repo: Path) -> None:
    """list_container_items filters by regex pattern."""
    items = _make_io("README.md", remote_repo).list_container_items(pattern=r"\.txt$")
    assert items == ["git://github.com/testorg/testrepo/main#sub/data.txt"]


def test_list_container_items_fragments(remote_repo: Path) -> None:
    """list_container_items returns fragments when full_string is False."""
    items = _make_io("README.md", remote_repo).list_container_items(full_string=False)
    assert "README.md" in items
    assert "sub/data.txt" in items


def test_clone_is_reused_for_other_file(remote_repo: Path) -> None:
    """A second file in the same repo reuses the clone without re-cloning."""
    io1 = _make_io("README.md", remote_repo)
    io1.download()
    clone_dir = io1.clone_dir
    marker = clone_dir / "local_only.txt"
    marker.write_text("do not lose me")

    io2 = _make_io("sub/data.txt", remote_repo)
    io2.download()

    assert io2.scratch_path.read_text() == "nested content"
    # Clone was not wiped/re-created, proving reuse.
    assert marker.read_text() == "do not lose me"


def test_clone_args_are_used(remote_repo: Path) -> None:
    """clone-args query param is parsed into flags forwarded to git clone."""
    io = _make_io("README.md", remote_repo, query="clone-args=['--depth', '1']")
    assert io.clone_args == ["--depth", "1"]
    io.download()
    assert io.scratch_path.read_text() == "hello world"


def test_get_object(remote_repo: Path) -> None:
    """get_object returns the local path or None."""
    io = _make_io("README.md", remote_repo)
    assert io.get_object() == str(io.clone_dir / "README.md")
    missing = _make_io("missing.txt", remote_repo)
    assert missing.get_object() is None


def test_get_remote_tags_is_none(remote_repo: Path) -> None:
    """get_remote_tags always returns None for the git scheme."""
    assert _make_io("README.md", remote_repo).get_remote_tags() is None


def test_run_git_failure_raises(remote_repo: Path) -> None:
    """A failing git command surfaces as RuntimeError."""
    io = _make_io("README.md", remote_repo)
    io.ensure_clone()
    with pytest.raises(RuntimeError, match="failed"):
        io._run_git(["checkout", "does-not-exist"], cwd=io.clone_dir)


@pytest.fixture
def _git_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide a git commit identity via environment for isolated tests."""
    for var in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(var, "Test")
    for var in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(var, "test@example.com")


def _remote_has_branch(remote: Path, branch: str) -> bool:
    """Return True if the bare remote has the given branch."""
    out = subprocess.run(
        ["git", "ls-remote", "--heads", str(remote), branch],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return out != ""


def test_upload_pushes_new_file(
    remote_repo: Path,
    _git_identity: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """upload creates the branch, commits the new file, and pushes it."""
    monkeypatch.setattr(IOGit, "_create_pull_request", lambda self, branch: None)
    io = _make_io("added/new.txt", remote_repo, query="target-branch=feat/add")
    io.ensure_clone()
    io.scratch_path.write_text("fresh content", encoding="utf-8")

    io.upload()

    assert _remote_has_branch(remote_repo, "feat/add")
