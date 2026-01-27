from pathlib import Path

import urgap


def test_accessing_path_downloads_file(tmp_scratch_disk):
    url = "https://git-scm.com/images/logos/downloads?uftype=.asdf.asdf"
    urn = Path("Git-Icon-1788C.png")
    uf = urgap.UFile(uri=f"{url}#{urn}")
    assert uf.io.scratch_path.exists() is False
    uf.path
    assert uf.io.scratch_path.exists() is True
    with open(uf.path, "rb") as f:
        assert f.read(1) == b"\x89"
