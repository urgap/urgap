# tests/unittests/ufile/test_uio_mylabdata.py
import json
import types

import urgap

from urgap.ufile.io.mylabdata import IOMyLabData, make_expiration_safe_request

HOST = "mylabdata-files.uat.corpnet2.com"
EQUIP = "354557"
TASK = "24-10000864-C4"
OBJECT = "demo.txt"
URI = f"mylabdata://{HOST}/{EQUIP}/{TASK}#{OBJECT}"


class DummyResp:
    def __init__(
        self,
        status_code=200,
        data=None,
        content=b"",
        headers=None,
        chunks=None,
        next_page="",
    ):
        self.status_code = status_code
        self._data = data or {}
        if "data" not in self._data:
            self._data = {"data": self._data}
        self.content = content
        self.headers = headers or {}
        self._chunks = chunks or [b""]
        if "files" in self._data.get("data", {}):
            self._data["data"].setdefault("nextPage", next_page)

    def json(self):
        return self._data

    def iter_content(self, _):
        for c in self._chunks:
            yield c


def _mk_io(tmp_path, monkeypatch):
    """Create an IOMyLabData instance with creds configured & token method stubbed."""
    urgap.config.setdefault("certificates", {})
    urgap.config["certificates"][HOST] = True

    urgap.instances.ucredential_manager.add_credentials(
        [
            {
                "scheme": "mylabdata",
                "host": HOST,
                "user": "user",
                "password": "pw",
                "secure": True,
                "description": "test",
                "secret_store": "env",
            }
        ]
    )

    calls = {"n": 0}

    def dummy_get_token(self):
        calls["n"] += 1
        self._api_token = {"Authorization": "Bearer dummy"}

    monkeypatch.setattr(
        IOMyLabData, "_get_token_bearer", dummy_get_token, raising=False
    )

    uf = urgap.UFile(uri=URI)
    io = IOMyLabData(uuri=uf.uuri)

    sp = io.scratch_path
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_bytes(b"dummy")

    return io, calls


def test_upload_with_and_without_tag_paths(tmp_path, monkeypatch):
    io, calls = _mk_io(tmp_path, monkeypatch)

    post_calls = []

    def dummy_post_no_tags(url, *a, **k):
        post_calls.append(url)
        return DummyResp(200)

    monkeypatch.setattr("requests.post", dummy_post_no_tags)
    r = io.upload(tags=None)
    assert r.status_code == 200
    assert len(post_calls) == 1

    post_calls.clear()

    def dummy_post_with_tags(url, *a, **k):
        post_calls.append(url)
        return DummyResp(200)

    monkeypatch.setattr("requests.post", dummy_post_with_tags)
    r2 = io.upload(tags={"a": 1})
    assert r2.status_code == 200
    assert len(post_calls) == 2
    assert post_calls[1].endswith(".tag")


def test_download_writes_file_and_fetches_tags(tmp_path, monkeypatch):
    io, _ = _mk_io(tmp_path, monkeypatch)

    chunks = [b"hello ", b"world"]
    monkeypatch.setattr(
        "requests.get",
        lambda url, **k: DummyResp(200, chunks=chunks),
    )

    fetched = {"called": False}

    def dummy_get_remote_tags(self):
        fetched["called"] = True
        return {"ok": 1}

    monkeypatch.setattr(
        IOMyLabData, "get_remote_tags", dummy_get_remote_tags, raising=False
    )

    resp = io.download()
    assert resp.status_code == 200
    assert io.scratch_path.read_bytes() == b"".join(chunks)
    assert fetched["called"] is True


def test_list_container_items_paginates_and_filters(monkeypatch, tmp_path):
    io, _ = _mk_io(tmp_path, monkeypatch)

    monkeypatch.setattr(
        IOMyLabData,
        "add_storage_uri_to_container_items",
        lambda self, items: items,
        raising=False,
    )

    page1 = {
        "files": [
            {"downloadUrl": "https://domain/x/y/a/b/c/file_a.csv"},
            {"downloadUrl": "https://domain/x/y/a/b/c/file_b.txt"},
        ],
        "nextPage": "/api/files?page=2",
    }
    page2 = {
        "files": [
            {"downloadUrl": "https://domain/x/y/a/b/c/file_a2.csv"},
        ],
        "nextPage": "",
    }

    gets = [
        DummyResp(200, data=page1),
        DummyResp(200, data=page2),
    ]

    def dummy_get(url, **k):
        return gets.pop(0)

    monkeypatch.setattr("requests.get", dummy_get)

    out = io.list_container_items(pattern=r"\.csv$")
    assert any("file_a.csv" in s for s in out)
    assert any("file_a2.csv" in s for s in out)
    assert not any("file_b.txt" in s for s in out)


def test_remote_object_exists_true(monkeypatch, tmp_path):
    io, _ = _mk_io(tmp_path, monkeypatch)

    monkeypatch.setattr(
        IOMyLabData,
        raising=False,
    )

    def dummy_get(url, **k):
        data = {
            "files": [
                {"downloadUrl": f"https://d/x/y/{OBJECT}"},
            ],
            "nextPage": "",
        }
        return DummyResp(200, data=data)

    monkeypatch.setattr("requests.get", dummy_get)

    assert io.remote_object_exists() is True