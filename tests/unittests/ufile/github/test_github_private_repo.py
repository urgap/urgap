from pathlib import Path
import pytest



def test_github_private_repo():
    try:
        )
    except KeyError:
        pytest.skip("Github backend not available")
    content = Path("test_node_data/test.txt")

    )
    # Test uploading the file from "main" to "new_ufile"
    uf.rebase(
        upload=True,
    )

    object_name = uf.object_name
    uf.purge_local()

    )

    # Test the existence on remote
    assert new_uf.remote_object_exists() is True
    # Test downloading the file
    new_uf.purge_local()
    assert new_uf.io.scratch_path.exists() is False
    new_uf.path
    assert new_uf.io.scratch_path.exists() is True

    # Test reading the content of the remote file
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
    )
    assert uf.remote_object_exists() is False

    # Test existince of file
    )
    )