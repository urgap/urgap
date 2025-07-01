from pathlib import Path

import pytest

import urgap


def test_github_private_repo():
    try:
        urgap.instances.ucredential_manager.get_password(
            "github://dso.github.com/gsk-tech/dso-dval-r2d2",
        )
    except KeyError:
        pytest.skip("Github backend not available")
    base_folder = Path(f"{urgap._test_folder}/data")
    content = Path("test_node_data/test.txt")

    uf = urgap.UFile(
        uri=f"file://{base_folder.resolve()}?target-branch={git_target_branch}#{content}",
    )
    # Test uploading the file from "main" to "new_ufile"
    uf.rebase(
        upload=True,
    )

    object_name = uf.object_name
    uf.purge_local()

    new_uf = urgap.UFile(
    )

    # Test the existence on remote
    assert new_uf.remote_object_exists() is True
    # Test downloading the file
    new_uf.purge_local()
    assert new_uf.io.scratch_path.exists() is False
    new_uf.path
    assert new_uf.io.scratch_path.exists() is True

    # Test reading the content of the remote file
    uf = urgap.UFile(
    )
    uf.purge_local()
    uf.download()
    assert "tables" in uf.path.read_text()

    assert (
        uf.io.remote_path
        == "https://api.github.com/repos/gsk-tech/dso-dval-r2d2/contents/configuration/parameters.json?ref=main"
    )

    assert uf.io.get_file_properties() == "configuration/parameters.json"
    assert uf.io.get_object() == "configuration/parameters.json"

    # Test the file that doesn't exist
    uf = urgap.UFile(
    )
    assert uf.remote_object_exists() is False

    # Test existince of file
    uf = urgap.UFile(
    )
    assert uf.remote_object_exists() is True

    uf = urgap.UFile(
        uri="github://dso.github.com/gsk-tech/dso-dval-r2d2/main#configuration/parameters.json",
    )
    assert uf.remote_object_exists() is True