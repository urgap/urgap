"""Git clone-based subclass of urgap's UIO submodule.

Unlike the ``github`` scheme, which reads every file through the GitHub REST API
(and thus consumes the API rate limit), this scheme clones the repository once to
a persistent location on disk and serves individual files from the local
checkout.
"""

import logging
import re
import shutil
import subprocess
import uuid

from pathlib import Path
from typing import ClassVar, ParamSpec

from github import Auth, Github, GithubException

import urgap

from urgap.ufile.io._base import UIOBase

P = ParamSpec("P")
logger = logging.getLogger(__name__)

GIT_TIMEOUT_SECONDS = 300


class IOGit(UIOBase):
    """UIO class interface for git-cloned repository file objects.

    git://<github_host>/<org_name>/<repo_name>/<branch>#path/to/dir/<object_name>
    """

    SCHEMA = "git"

    # Tracks (clone_dir, branch) pairs already refreshed in this process so that
    # reading many files from the same repo does not trigger repeated fetches.
    _refreshed: ClassVar[set[tuple[str, str]]] = set()

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create a new UIO class for processing the git scheme.

        Args:
            **kwargs: Requires the parsed ``uuri`` to set respective attributes.
        """
        super().__init__(**kwargs)
        self.query_params = self.uuri.query

        self.org_name = self.uuri.get_github_resource_name("org")
        self.repo_name = self.uuri.get_github_resource_name("repo")
        self.repo_full_name = f"{self.org_name}/{self.repo_name}"
        self.branch_name = self.uuri.get_github_resource_name("branch")
        self.object_filepath = self.uuri.fragment
        self.host = self.uuri.netloc

        self.clone_args = self._resolve_clone_args()
        self.remote_url = self._build_remote_url()
        self.force = bool(self.query_params.get("force", False))
        self._cloned = False
        if self.force:
            self.scratch_path.unlink(missing_ok=True)

    def _resolve_clone_args(self) -> list[str]:
        """Get custom ``git clone`` flags from the ``clone-args`` query param.

        Returns:
            List of raw CLI flags, empty when none were supplied.
        """
        raw = self.query_params.get("clone-args", [])
        if isinstance(raw, (list, tuple)):
            return [str(arg) for arg in raw]
        return [str(raw)]

    def _build_remote_url(self) -> str:
        """Build the clone URL, embedding the token when available.

        Returns:
            An https clone URL for the repository.
        """
        token = self.uuri.password
        if token:
            return f"https://{token}@{self.host}/{self.repo_full_name}.git"
        return f"https://{self.host}/{self.repo_full_name}.git"

    @property
    def clone_dir(self) -> Path:
        """Get the clone directory for this repository.

        Clones live under the per-run scratch base, so they are shared across
        all downloads in a single run and removed at interpreter exit.

        Returns:
            ``<scratch_disk_base>/git_clones/<host>/<org>/<repo>``.
        """
        return (
            Path(urgap.scratch_disk_base)
            / "git_clones"
            / self.host
            / self.org_name
            / self.repo_name
        ).resolve()

    def _redact(self, text: str) -> str:
        """Remove the auth token from text before logging or raising.

        Args:
            text: Text that may contain the token.

        Returns:
            Text with the token replaced.
        """
        token = self.uuri.password
        if token:
            return text.replace(token, "***")
        return text

    @staticmethod
    def _ensure_git_available() -> None:
        """Verify the ``git`` executable is installed and on PATH.

        Raises:
            RuntimeError: If git cannot be found.
        """
        if shutil.which("git") is None:
            msg = (
                "The 'git' scheme requires the git command-line tool, which is a "
                "system dependency and cannot be installed via pip. Install it "
                "(e.g. 'brew install git', 'apt-get install git', or "
                "'conda install git') and ensure it is on your PATH."
            )
            raise RuntimeError(msg)

    def _run_git(
        self,
        args: list[str],
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess:
        """Run a git subcommand, raising RuntimeError on failure.

        Args:
            args: Arguments passed to the ``git`` executable.
            cwd: Working directory for the command.

        Returns:
            The completed process.

        Raises:
            RuntimeError: If git is missing, times out, or exits non-zero.
        """
        cmd = ["git", *args]
        self._ensure_git_available()
        # Skip the "-C <dir>" prefix so the label is the actual subcommand.
        label_args = args[2:] if args[:1] == ["-C"] else args
        label = next((a for a in label_args if not a.startswith("-")), args[0])
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=GIT_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as e:
            msg = f"Failed to run 'git {label}': {self._redact(str(e))}"
            logger.exception(msg)
            raise RuntimeError(msg) from e
        if result.returncode != 0:
            msg = (
                f"'git {label}' failed (exit {result.returncode}): "
                f"{self._redact(result.stderr)}"
            )
            logger.error(msg)
            raise RuntimeError(msg)
        return result

    def ensure_clone(self) -> None:
        """Clone the repository if needed, otherwise refresh the branch.

        The clone is idempotent per repository: if the repo is already cloned
        (by an earlier download of another file, or a previous run), it is not
        cloned again. When the ``force`` query param is set, any existing clone
        is deleted and the repository is cloned again from scratch.
        """
        if self._cloned:
            return
        clone_dir = self.clone_dir
        if self.force and clone_dir.exists():
            shutil.rmtree(clone_dir)
            IOGit._refreshed.discard((str(clone_dir), self.branch_name))
        if (clone_dir / ".git").is_dir():
            self._refresh_branch(clone_dir)
        else:
            clone_dir.parent.mkdir(parents=True, exist_ok=True)
            self._run_git(["clone", *self.clone_args, self.remote_url, str(clone_dir)])
            self._checkout_branch(clone_dir)
            IOGit._refreshed.add((str(clone_dir), self.branch_name))
        self._cloned = True

    def _refresh_branch(self, clone_dir: Path) -> None:
        """Fetch and check out the requested branch on an existing clone.

        Skips network calls when the repo/branch was already refreshed this
        process, unless the ``refresh`` query param forces it.

        Args:
            clone_dir: The existing clone directory.
        """
        key = (str(clone_dir), self.branch_name)
        force = bool(self.query_params.get("refresh", False))
        if key in IOGit._refreshed and not force:
            return
        self._run_git(["-C", str(clone_dir), "fetch", "--all", "--prune"])
        self._checkout_branch(clone_dir)
        self._run_git(["-C", str(clone_dir), "pull", "--ff-only"])
        IOGit._refreshed.add(key)

    def _checkout_branch(self, clone_dir: Path) -> None:
        """Check out the requested branch, disambiguating from same-named paths.

        The trailing ``--`` ensures git treats the name as a ref rather than a
        file when a path with the same name exists (e.g. a ``dev`` directory).

        Args:
            clone_dir: The clone directory to run the checkout in.
        """
        self._run_git(
            ["-C", str(clone_dir), "checkout", self.branch_name, "--"],
        )

    @property
    def local_object_path(self) -> Path:
        """Get the path to the referenced object inside the local clone.

        Returns:
            Path to the file within the checkout.
        """
        return self.clone_dir / self.object_filepath

    @property
    def remote_path(self) -> str | None:
        """Get the local path of the referenced object, if it exists.

        Returns:
            Path to the file within the checkout, or None.
        """
        if self.remote_object_exists() is True:
            return str(self.local_object_path)
        return None

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with the referenced file.

        The git scheme keeps no tag store; always returns None.

        Returns:
            None.
        """
        return None

    def get_object(self) -> str | None:
        """Get the local path of the referenced object, if it exists.

        Returns:
            Path to the file within the checkout, or None.
        """
        return self.remote_path

    def download(self) -> None:
        """Copy the referenced object from the local clone into scratch."""
        self.ensure_clone()
        source = self.local_object_path
        if not source.is_file():
            self.scratch_path.unlink(missing_ok=True)
            msg = f"Unable to find {self.object_filepath} in {self.repo_full_name}"
            raise RuntimeError(msg)
        try:
            shutil.copyfile(source, self.scratch_path)
        except OSError as e:
            self.scratch_path.unlink(missing_ok=True)
            msg = f"Failed to copy {self.object_filepath}: {e}"
            raise RuntimeError(msg) from e

    def remote_object_exists(self) -> bool:
        """Verify the referenced object exists in the local checkout.

        Returns:
            True if the object exists.
        """
        self.ensure_clone()
        return self.local_object_path.is_file()

    def _remote_path_exists(self) -> bool:
        """Verify the referenced remote path exists.

        Returns:
            True if the remote object exists.
        """
        return self.remote_object_exists()

    def list_container_items(
        self,
        pattern: str | None = None,
        full_string: bool = True,
        **_kwargs: P.kwargs,
    ) -> list:
        """Get objects in the repository from the local checkout.

        Args:
            pattern: Regex pattern for filtering.
            full_string: Whether to return full URIs or just fragments.

        Returns:
            List of object names after filtering.
        """
        self.ensure_clone()
        clone_dir = self.clone_dir
        container_objects = [
            f"{self.uuri.scheme}://{self.host}/{self.repo_full_name}/{self.branch_name}"
            f"#{path.relative_to(clone_dir).as_posix()}"
            for path in sorted(clone_dir.rglob("*"))
            if path.is_file() and ".git" not in path.relative_to(clone_dir).parts
        ]
        if pattern is not None:
            container_objects = [
                f for f in container_objects if re.search(pattern, f) is not None
            ]
        if full_string is True:
            return container_objects
        logger.warning(
            "DeprecationWarning: list_container_items with full_string=False will be "
            "deprecated soon, use full_string=True instead.",
        )
        return [obj.split("#")[1] for obj in container_objects]

    def upload(self, tags: dict | None = None) -> None:
        """Commit and push the scratch object to a feature branch and open a PR."""
        if tags is not None:
            msg = f"tags will be skipped. {tags}!"
            logger.warning(msg)
        self.ensure_clone()
        target_branch = self.query_params.get(
            "target-branch",
            f"feature/new_ufile_{str(uuid.uuid4())[:8]}",
        )
        self._prepare_target_branch(target_branch)
        self._stage_object()
        if self._commit_staged():
            self._push_branch(target_branch)
        self._create_pull_request(target_branch)

    def _prepare_target_branch(self, target_branch: str) -> None:
        """Check out the target branch, basing it on the remote branch if it exists.

        Basing on an existing remote branch keeps the later push a fast-forward,
        so re-running an upload with the same ``target-branch`` does not fail.

        Args:
            target_branch: The feature branch to create/reuse.
        """
        clone_dir = str(self.clone_dir)
        self._run_git(["-C", clone_dir, "fetch", "origin", "--prune"])
        remote_ref = f"origin/{target_branch}"
        remote_exists = (
            self._run_git(
                ["-C", clone_dir, "ls-remote", "--heads", "origin", target_branch],
            ).stdout.strip()
            != ""
        )
        if remote_exists:
            self._run_git(
                ["-C", clone_dir, "checkout", "-B", target_branch, remote_ref, "--"],
            )
        else:
            self._run_git(["-C", clone_dir, "checkout", "-B", target_branch, "--"])

    def _stage_object(self) -> None:
        """Copy the scratch object into the checkout and stage it."""
        dest = self.local_object_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.scratch_path, dest)
        self._run_git(["-C", str(self.clone_dir), "add", self.object_filepath])

    def _commit_staged(self) -> bool:
        """Commit staged changes if there are any.

        Returns:
            True if a commit was created, False when nothing changed.
        """
        clone_dir = str(self.clone_dir)
        staged = self._run_git(
            ["-C", clone_dir, "status", "--porcelain"],
        ).stdout.strip()
        if not staged:
            logger.info("No changes to commit; skipping commit and push.")
            return False
        self._run_git(["-C", clone_dir, "commit", "-m", "New ufile is available"])
        return True

    def _push_branch(self, target_branch: str) -> None:
        """Push the target branch to origin.

        Args:
            target_branch: The branch to push.
        """
        self._run_git(
            [
                "-C",
                str(self.clone_dir),
                "push",
                "--set-upstream",
                "origin",
                target_branch,
            ],
        )

    def _create_pull_request(self, target_branch: str) -> None:
        """Open a pull request for the pushed branch via PyGithub.

        A pre-existing PR for the same branch is treated as success.

        Args:
            target_branch: The branch that was pushed.

        Raises:
            RuntimeError: If the PR cannot be created.
        """
        token = self.uuri.password
        github_io = Github(auth=Auth.Token(token)) if token else Github()
        try:
            repo = github_io.get_repo(self.repo_full_name)
            pr = repo.create_pull(
                title="New ufile is available",
                body="This pull request adds a new ufile.",
                head=target_branch,
                base=self.branch_name,
            )
            msg = f"PR #{pr.number} is created"
            logger.info(msg)
        except GithubException as e:
            if self._pull_request_already_exists(e):
                msg = f"A pull request for '{target_branch}' already exists."
                logger.info(msg)
                return
            msg = f"Unable to create pull request. {e}!"
            raise RuntimeError(msg) from e
        finally:
            github_io.close()

    @staticmethod
    def _pull_request_already_exists(error: GithubException) -> bool:
        """Detect the 'PR already exists' response from GitHub.

        Args:
            error: The GithubException raised by create_pull.

        Returns:
            True when the error indicates an existing pull request.
        """
        errors = error.data.get("errors", []) if isinstance(error.data, dict) else []
        return any(
            "already exists" in str(item.get("message", "")).lower()
            for item in errors
            if isinstance(item, dict)
        )
