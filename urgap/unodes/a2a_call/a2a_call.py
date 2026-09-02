"""Urgap A2ACall wrapper.

The A2A call is performed in process with the official a2a-sdk, hence this
UNode has no separate resource and overwrites execute instead of building a
command list in preflight.
"""

from __future__ import annotations

import asyncio
import logging
import mimetypes
import time
import uuid

from typing import TYPE_CHECKING
from urllib.parse import quote

import urgap

if TYPE_CHECKING:
    from pathlib import Path

    import httpx2 as httpx

    from a2a.client import Client
    from a2a.types import Message, Part, Task

logger = logging.getLogger(__name__)

ACCEPTED_OUTPUT_MODES = ("text", "text/plain", "application/json")
DEFAULT_MEDIA_TYPE = "application/octet-stream"
# Every other state either finished the task or needs input a UNode cannot give
PENDING_TASK_STATES = frozenset({"TASK_STATE_SUBMITTED", "TASK_STATE_WORKING"})


def build_message(question: str, input_files: list[Path]) -> Message:
    """Build the A2A message which is sent to the agent.

    Args:
        question: Question that is asked to the agent.
        input_files: Files that are attached as file parts.

    Returns:
        A2A message with the question as text part and one file part per file.
    """
    from a2a.types import Message, Part, Role

    parts = [Part(text=question)]
    for file_path in input_files:
        media_type, _encoding = mimetypes.guess_type(file_path.name)
        msg = f"Attaching {file_path.name} as file part."
        logger.info(msg)
        parts.append(
            Part(
                raw=file_path.read_bytes(),
                filename=file_path.name,
                media_type=media_type or DEFAULT_MEDIA_TYPE,
            ),
        )
    return Message(
        message_id=str(uuid.uuid4()),
        role=Role.ROLE_USER,
        parts=parts,
    )


def iter_parts(result: Task | Message) -> list[Part]:
    """Collect all parts of an A2A task or message.

    Parts of the agent status message are collected first, followed by the parts
    of all artifacts in the order they were reported by the agent.

    Args:
        result: A2A task or message answered by the agent.

    Returns:
        List of A2A parts.
    """
    from a2a.types import Message

    if isinstance(result, Message):
        return list(result.parts)
    parts = list(result.status.message.parts)
    for artifact in result.artifacts:
        parts.extend(artifact.parts)
    return parts


async def create_agent_client(
    agent_url: str,
    httpx_client: httpx.AsyncClient,
    card_path: str | None = None,
) -> Client:
    """Create an A2A client for an agent URL.

    The agent card is resolved by the SDK, which also determines the transport
    and the protocol version the agent is talked to with. A card is therefore
    required, it cannot be synthesized from the URL alone.

    Args:
        agent_url: Base URL of the A2A agent.
        httpx_client: HTTP client used for card resolution and all A2A calls.
        card_path: Relative path of the agent card, defaults to the well known
            path of the SDK.

    Returns:
        An A2A client for the agent.
    """
    from a2a.client import ClientConfig, create_client

    return await create_client(
        agent_url,
        ClientConfig(
            # Streaming is optional for A2A agents, message/send is not, and a
            # UNode run has nobody watching incremental updates anyway.
            streaming=False,
            httpx_client=httpx_client,
            accepted_output_modes=list(ACCEPTED_OUTPUT_MODES),
        ),
        relative_card_path=card_path,
    )


async def send_question(
    client: Client,
    question: str,
    input_files: list[Path],
) -> Task | Message:
    """Send the question and its file parts to the agent.

    Args:
        client: A2A client for the agent.
        question: Question that is asked to the agent.
        input_files: Files that are attached as file parts.

    Returns:
        The task or message the agent answered with.

    Raises:
        RuntimeError: If the agent did not answer at all.
    """
    from a2a.types import SendMessageRequest

    request = SendMessageRequest(
        message=build_message(question=question, input_files=input_files),
    )
    last_response = None
    async for stream_response in client.send_message(request):
        last_response = stream_response
    if last_response is None:
        msg = "Agent did not answer the message at all."
        raise RuntimeError(msg)
    if last_response.HasField("task"):
        return last_response.task
    return last_response.message


async def wait_for_task(
    client: Client,
    task: Task,
    task_timeout: int,
    poll_interval: int,
) -> Task:
    """Poll an A2A task until it is neither submitted nor working anymore.

    Args:
        client: A2A client for the agent.
        task: Task as answered by the agent.
        task_timeout: Maximum number of seconds to wait for the task to finish.
        poll_interval: Number of seconds between two get_task calls.

    Returns:
        The last state of the task that was retrieved.

    Raises:
        RuntimeError: If the task is still pending after task_timeout seconds.
    """
    from a2a.types import GetTaskRequest, TaskState

    deadline = time.time() + task_timeout
    while TaskState.Name(task.status.state) in PENDING_TASK_STATES:
        if time.time() > deadline:
            msg = (
                f"A2A task {task.id} did not finish within {task_timeout} seconds, "
                f"last state was {TaskState.Name(task.status.state)}."
            )
            raise RuntimeError(msg)
        msg = (
            f"A2A task {task.id} is in state {TaskState.Name(task.status.state)}, "
            "waiting ..."
        )
        logger.info(msg)
        await asyncio.sleep(poll_interval)
        task = await client.get_task(GetTaskRequest(id=task.id))
    return task


async def download_part(part: Part, httpx_client: httpx.AsyncClient) -> bytes:
    """Download the content of a file part which is referenced by URL.

    Args:
        part: A2A part with a url content field.
        httpx_client: HTTP client used for the download.

    Returns:
        Content of the file part.

    Raises:
        RuntimeError: If the content cannot be downloaded.
    """
    import httpx2 as httpx

    msg = f"Downloading file part {part.filename} from {part.url}"
    logger.info(msg)
    try:
        response = await httpx_client.get(part.url)
        response.raise_for_status()
    except httpx.HTTPError as e:
        msg = f"Could not download file part from {part.url}: {e}"
        raise RuntimeError(msg) from e
    return response.content


async def collect_response(
    result: Task | Message,
    httpx_client: httpx.AsyncClient,
) -> tuple[str, list[tuple[str, bytes]]]:
    """Split an A2A result into its text answer and the files it returned.

    File parts keep the name the agent reported, data parts become json files.

    Args:
        result: A2A task or message answered by the agent.
        httpx_client: HTTP client used to download file parts by URL.

    Returns:
        Tuple of the joined text answer and a list of (file name, content)
        tuples for every non-text part the agent returned.
    """
    from google.protobuf.json_format import MessageToJson

    text_chunks = []
    returned_files = []
    for part in iter_parts(result):
        content = part.WhichOneof("content")
        file_name = part.filename.rsplit("/", 1)[-1]
        if content == "text":
            text_chunks.append(part.text)
        elif content == "data":
            returned_files.append(
                (
                    file_name or f"a2a_data_{len(returned_files) + 1}.json",
                    MessageToJson(part.data).encode(),
                ),
            )
        elif content in {"raw", "url"}:
            returned_files.append(
                (
                    file_name or f"a2a_file_{len(returned_files) + 1}",
                    part.raw
                    if content == "raw"
                    else await download_part(part=part, httpx_client=httpx_client),
                ),
            )
        else:
            msg = f"Skipping part without content, its metadata was {part.metadata}."
            logger.warning(msg)
    return "\n".join(chunk for chunk in text_chunks if chunk), returned_files


async def ask_agent(
    agent_url: str,
    question: str,
    input_files: list[Path],
    headers: dict[str, str] | None = None,
    request_timeout: int = 300,
    task_timeout: int = 1800,
    poll_interval: int = 5,
    card_path: str | None = None,
) -> tuple[str, list[tuple[str, bytes]]]:
    """Ask an A2A agent a question and collect everything it answered.

    Args:
        agent_url: Base URL of the A2A agent.
        question: Question that is asked to the agent.
        input_files: Files that are attached to the question as file parts.
        headers: Additional HTTP headers, e.g. for authentication.
        request_timeout: Timeout in seconds for a single HTTP request.
        task_timeout: Maximum number of seconds to wait for the task to finish.
        poll_interval: Number of seconds between two get_task calls.
        card_path: Relative path of the agent card.

    Returns:
        Tuple of the text answer and a list of (file name, content) tuples for
        every non-text part the agent returned.

    Raises:
        RuntimeError: If the agent task did not complete successfully.
    """
    import httpx2 as httpx

    from a2a.types import Task, TaskState

    async with httpx.AsyncClient(
        headers=headers or {},
        timeout=request_timeout,
    ) as httpx_client:
        client = await create_agent_client(
            agent_url=agent_url,
            httpx_client=httpx_client,
            card_path=card_path,
        )
        try:
            result = await send_question(
                client=client,
                question=question,
                input_files=input_files,
            )
            if isinstance(result, Task):
                result = await wait_for_task(
                    client=client,
                    task=result,
                    task_timeout=task_timeout,
                    poll_interval=poll_interval,
                )
            text, returned_files = await collect_response(
                result=result,
                httpx_client=httpx_client,
            )
        finally:
            await client.close()

    if (
        isinstance(result, Task)
        and result.status.state != TaskState.TASK_STATE_COMPLETED
    ):
        msg = (
            f"A2A task {result.id} finished in state "
            f"{TaskState.Name(result.status.state)}: {text}"
        )
        raise RuntimeError(msg)
    return text, returned_files


class A2ACall(urgap.unode.UNodeBase):
    """Urgap wrapper for Agent2Agent (A2A) calls.

    Asks a question to an A2A agent, attaches all input UFiles as A2A file
    parts and writes the agent answer as well as all files that are returned by
    the agent back into urgap storage.

    The answer is written as a single text UFile, the returned files are written
    as a dynamic number of UFiles. Their type is only known at runtime, hence
    they are typed as ``any.BLOB``, which keeps them distinct from the answer
    while still being consumable by all UNodes accepting ``any.ANY``. The name
    the agent reported is kept in the ``original_name`` tag of each UFile.

    The A2A call is done in process by the official a2a-sdk, which is part of
    the ``agents`` extra.
    """

    META_INFO = {
        "name": "A2ACall",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        # This UNode has no resource of its own, the system resource it runs on
        # is the python interpreter urgap itself is running in.
        "versions": [
            {"version": "1.0.0", "exe_path": "$python"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.any.ANY: {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.any.TXT: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.any.BLOB: {
                "min": 0,
                "max": -1,
            },
        },
        "engine": None,
        "engine_type": ("agent",),
        "requires": {
            "other_uftypes": {
                "python_packages": ["a2a-sdk"],
            },
        },
        "citation": "Urgap team (2026)",
        "parameter_examples": """
            These are possible unode_execution_parameters for A2ACall.

            agent_url: Base URL of the A2A agent, its agent card is resolved
                from /.well-known/agent-card.json. Required.
            question: Question that is asked to the agent. Required.

            For example:
            {
                "agent_url": "https://my-agent.example.com",
                "question": "Summarize the attached results as a csv file."
            }

            Optional parameters:
            {
                "headers": {"Authorization": "Bearer <token>"},
                "request_timeout": 300, # seconds per HTTP request
                "task_timeout": 1800,   # seconds to wait for the agent task
                "poll_interval": 5,     # seconds between two get_task calls
                "card_path": ".well-known/my-agent.json",
            }
        """,
    }

    def __init__(self) -> None:
        """Initialize A2ACall class."""
        super().__init__()

    def write_answer(self, utrace: urgap.UTrace, text: str) -> None:
        """Write the text answer of the agent into the text output UFile.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
            text: Text answer of the agent.
        """
        answer_path = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.any.TXT,
        )[0]
        answer_path.write_text(text)

    def write_returned_files(
        self,
        utrace: urgap.UTrace,
        returned_files: list[tuple[str, bytes]],
    ) -> None:
        """Write every file the agent returned into its own output UFile.

        The output UFileList is extended by one UFile per returned file and the
        content is written directly to the scratch path of that UFile, so no
        temporary location is involved.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
            returned_files: List of (file name, content) tuples.
        """
        for file_name, content in returned_files:
            utrace.extend_output_files_by_uftype(
                uftype=urgap.uftypes.any.BLOB,
                max_n=len(returned_files),
            )
            output_ufile = utrace.output_files[-1]
            output_ufile.path.write_bytes(content)
            output_ufile.tags.update({"original_name": quote(file_name)})
            msg = f"Wrote {file_name} returned by the agent to {output_ufile.path}"
            logger.info(msg)

    def execute(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Execute routine for A2ACall, performs the A2A call in process.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.

        Raises:
            KeyError: If a required unode_execution_parameter is missing.
        """
        parameters = utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ]
        try:
            agent_url = parameters["agent_url"]
            question = parameters["question"]
        except KeyError as e:
            msg = (
                f"A2ACall requires the unode_execution_parameter {e}, "
                f"see META_INFO['parameter_examples']."
            )
            raise KeyError(msg) from e

        msg = f"Asking {agent_url}: {question}"
        logger.info(msg)
        try:
            text, returned_files = asyncio.run(
                ask_agent(
                    agent_url=agent_url,
                    question=question,
                    input_files=[ufile.path for ufile in utrace.input_files],
                    headers=parameters.get("headers"),
                    request_timeout=parameters.get("request_timeout", 300),
                    task_timeout=parameters.get("task_timeout", 1800),
                    poll_interval=parameters.get("poll_interval", 5),
                    card_path=parameters.get("card_path"),
                ),
            )
        except Exception:
            logger.exception("A2A call to %s failed", agent_url)
            utrace.output_files = urgap.UFileList([None])
            utrace.set_stop_time(crashed=True)
            if utrace.urun_dict.unode_parameters["crash_on_resource_crash"] is True:
                raise
            return utrace

        self.write_answer(utrace=utrace, text=text)
        self.write_returned_files(utrace=utrace, returned_files=returned_files)
        utrace.set_stop_time()
        return utrace
