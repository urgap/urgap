import pytest

from urgap.uctl.mcp.prompts import register_prompts


class DummyServer:
    """Minimal stand-in for FastMCP that captures prompt functions."""

    def __init__(self):
        self.prompts = {}

    def prompt(self):
        def _decorator(fn):
            self.prompts[fn.__name__] = fn
            return fn

        return _decorator


def _first_text(prompt_obj):
    """Extract text from the first AssistantMessage, handling TextContent or dict."""
    assert hasattr(prompt_obj, "messages") and prompt_obj.messages, (
        "Prompt has no messages"
    )
    msg0 = prompt_obj.messages[0]
    content = getattr(msg0, "content", None)

    if hasattr(content, "text"):
        return content.text

    if isinstance(content, dict) and "text" in content:
        return content["text"]
    if (
        isinstance(content, list)
        and content
        and isinstance(content[0], dict)
        and "text" in content[0]
    ):
        return content[0]["text"]

    raise AssertionError(f"Unexpected message content shape: {type(content)}")


@pytest.mark.asyncio
async def test_register_prompts_registers_all():
    srv = DummyServer()
    register_prompts(srv)
    assert {
        "mylabdata_urgap_storage_base_uri_pattern",
        "google_bucket_urgap_storage_base_uri_pattern",
        "urun_default_dict",
    }.issubset(set(srv.prompts))


@pytest.mark.asyncio
async def test_mylabdata_prompt_variants():
    srv = DummyServer()
    register_prompts(srv)
    fn = srv.prompts["mylabdata_urgap_storage_base_uri_pattern"]

    # UAT (and DEV)
    p_uat = await fn(equipment_id="354557", task_id="24-10000864-C4", env="uat")
    assert (
        _first_text(p_uat)
        == "mylabdata://mylabdata-files.uat.corpnet2.com/354557/24-10000864-C4"
    )

    p_dev = await fn(equipment_id="EID", task_id="TID", env="dev")
    assert _first_text(p_dev) == "mylabdata://mylabdata-files.uat.corpnet2.com/EID/TID"

    # PROD
    p_prod = await fn(equipment_id="EID", task_id="TID", env="prod")
    assert _first_text(p_prod) == "mylabdata://mylabdata-files.corpnet2.com/EID/TID"

    p_unknown = await fn(equipment_id="EID", task_id="TID", env="qa")
    txt_unknown = _first_text(p_unknown).lower()
    assert "unknown" in txt_unknown and "uat" in txt_unknown and "prod" in txt_unknown


@pytest.mark.asyncio
async def test_google_bucket_prompt():
    srv = DummyServer()
    register_prompts(srv)
    fn = srv.prompts["google_bucket_urgap_storage_base_uri_pattern"]

    p = await fn(project_id="proj", bucket="bkt")
    text = _first_text(p)
    assert text == "gcs-libcloud://proj/bkt"

    arg_names = {a.name for a in p.arguments}
    assert {"project_id", "bucket"} <= arg_names


@pytest.mark.asyncio
async def test_urun_default_dict_prompt_contains_key_sections():
    srv = DummyServer()
    register_prompts(srv)
    fn = srv.prompts["urun_default_dict"]

    p = await fn()
    text = _first_text(p)

    assert "The urgap configuration dictionary" in text
    assert '"parameters": {' in text
    assert '"unode_parameters": {' in text
