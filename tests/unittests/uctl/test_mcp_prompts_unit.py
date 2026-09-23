import pytest

from fastmcp import Client, FastMCP

from urgap.uctl.mcp.prompts import register_prompts


@pytest.fixture
def prompt_client():
    """Provide an in-memory client connected to a server with the urgap prompts."""
    server = FastMCP("urgap prompts test server")
    register_prompts(server)
    return Client(server)


def _first_text(result):
    """Extract the text of the first message of a get_prompt result."""
    assert result.messages, "Prompt has no messages"
    return result.messages[0].content.text


@pytest.mark.asyncio
async def test_register_prompts_registers_all(prompt_client):
    async with prompt_client as client:
        prompts = {prompt.name for prompt in await client.list_prompts()}

    assert {
        "mylabdata_urgap_storage_base_uri_pattern",
        "google_bucket_urgap_storage_base_uri_pattern",
        "urun_default_dict",
    }.issubset(prompts)


@pytest.mark.asyncio
async def test_prompt_arguments_are_derived_from_the_signature(prompt_client):
    """Name, description and arguments come from FastMCP, not from hand written metadata."""
    async with prompt_client as client:
        prompts = {prompt.name: prompt for prompt in await client.list_prompts()}

    mylabdata = prompts["mylabdata_urgap_storage_base_uri_pattern"]
    arguments = {argument.name: argument for argument in mylabdata.arguments}

    assert set(arguments) == {"equipment_id", "task_id", "env"}
    assert arguments["equipment_id"].required is True
    assert arguments["task_id"].required is True
    assert arguments["env"].required is False
    assert "Mylabdata equipment ID" in arguments["equipment_id"].description


@pytest.mark.asyncio
async def test_mylabdata_prompt_variants(prompt_client):
    async with prompt_client as client:
        # UAT (and DEV)
        p_uat = await client.get_prompt(
            "mylabdata_urgap_storage_base_uri_pattern",
            {"equipment_id": "354557", "task_id": "24-10000864-C4", "env": "uat"},
        )
        assert (
            _first_text(p_uat)
            == "mylabdata://mylabdata-files.uat.corpnet2.com/354557/24-10000864-C4"
        )

        p_dev = await client.get_prompt(
            "mylabdata_urgap_storage_base_uri_pattern",
            {"equipment_id": "EID", "task_id": "TID", "env": "dev"},
        )
        assert (
            _first_text(p_dev) == "mylabdata://mylabdata-files.uat.corpnet2.com/EID/TID"
        )

        # PROD
        p_prod = await client.get_prompt(
            "mylabdata_urgap_storage_base_uri_pattern",
            {"equipment_id": "EID", "task_id": "TID", "env": "prod"},
        )
        assert _first_text(p_prod) == "mylabdata://mylabdata-files.corpnet2.com/EID/TID"

        p_unknown = await client.get_prompt(
            "mylabdata_urgap_storage_base_uri_pattern",
            {"equipment_id": "EID", "task_id": "TID", "env": "qa"},
        )
        txt_unknown = _first_text(p_unknown).lower()
        assert "unknown" in txt_unknown
        assert "uat" in txt_unknown
        assert "prod" in txt_unknown

        # env defaults to uat
        p_default = await client.get_prompt(
            "mylabdata_urgap_storage_base_uri_pattern",
            {"equipment_id": "EID", "task_id": "TID"},
        )
        assert (
            _first_text(p_default)
            == "mylabdata://mylabdata-files.uat.corpnet2.com/EID/TID"
        )
        assert p_default.description == (
            "Mylabdata urgap storage base uri pattern for EID TID in uat"
        )


@pytest.mark.asyncio
async def test_google_bucket_prompt(prompt_client):
    async with prompt_client as client:
        result = await client.get_prompt(
            "google_bucket_urgap_storage_base_uri_pattern",
            {"project_id": "my-project", "bucket": "my-bucket"},
        )

    assert _first_text(result) == "gcs://my-project/my-bucket"


@pytest.mark.asyncio
async def test_urun_default_dict_prompt_contains_key_sections(prompt_client):
    async with prompt_client as client:
        result = await client.get_prompt("urun_default_dict", {})

    text = _first_text(result)
    assert "The urgap configuration dictionary" in text
    assert '"parameters": {' in text
    assert '"unode_parameters": {' in text
