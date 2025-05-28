from pathlib import Path
import pytest



    try:
    except KeyError:
        pytest.skip("Github backend not available")
    content = Path("test_node_data/test.txt")

    )
    uf.rebase(
        upload=True,
    )

    object_name = uf.object_name
    uf.purge_local()

    )

    assert new_uf.remote_object_exists() is True
    # Test downloading the file
    new_uf.purge_local()
    assert new_uf.io.scratch_path.exists() is False
    new_uf.path
    assert new_uf.io.scratch_path.exists() is True

    )
    uf.purge_local()
    uf.download()
    assert "tables" in uf.path.read_text()