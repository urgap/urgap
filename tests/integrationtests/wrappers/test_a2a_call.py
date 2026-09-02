"""Integration tests for A2ACall, run against a stub A2A agent."""

import base64
import json
import threading

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from a2a.client import AgentCardResolutionError

import urgap

AGENT_ANSWER = "Here is the summary of the attached files."
AGENT_NAME = "UrgapStubAgent"


class StubA2AHandler(BaseHTTPRequestHandler):
    """Minimal A2A agent, its answer is defined by the mode of the server."""

    def log_message(self, *args) -> None:  # noqa: ANN002
        """Silence the default request logging of the stub agent."""

    def _reply(self, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _echo_artifact(self, request: dict) -> dict:
        """Return all received file parts as a single artifact."""
        return {
            "artifactId": "urgap-stub-artifact",
            "name": "echo",
            "parts": [
                {
                    "kind": "file",
                    "file": {
                        "name": f"echo_{n}.txt",
                        "mimeType": "text/plain",
                        "bytes": part["file"]["bytes"],
                    },
                }
                for n, part in enumerate(
                    [
                        part
                        for part in request["params"]["message"]["parts"]
                        if part["kind"] == "file"
                    ],
                    start=1,
                )
            ],
        }

    def _task(self, state: str, request: dict | None = None) -> dict:
        task = {
            "kind": "task",
            "id": "urgap-stub-task",
            "contextId": "urgap-stub-context",
            "status": {
                "state": state,
                "message": {
                    "role": "agent",
                    "kind": "message",
                    "messageId": "urgap-stub-status-message",
                    "parts": [{"kind": "text", "text": AGENT_ANSWER}],
                },
            },
        }
        if request is not None:
            task["artifacts"] = [self._echo_artifact(request)]
        return task

    def do_GET(self) -> None:  # noqa: N802
        """Serve the agent card, unless the stub agent runs without one."""
        if self.path != "/.well-known/agent-card.json" or self.server.mode == "no_card":
            self.send_error(404)
            return
        host, port = self.server.server_address
        self._reply(
            {
                "protocolVersion": "0.3.0",
                "name": AGENT_NAME,
                "description": "Echoes every file part it receives.",
                "version": "1.0.0",
                "url": f"http://{host}:{port}/",
                "preferredTransport": "JSONRPC",
                "capabilities": {},
                "defaultInputModes": ["text"],
                "defaultOutputModes": ["text"],
                "skills": [],
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        """Answer a message/send or tasks/get call according to the server mode."""
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.received_requests.append(request)
        if request["method"] == "tasks/get":
            result = self._task(state="completed")
        elif self.server.mode == "message_only":
            result = {
                "kind": "message",
                "role": "agent",
                "messageId": "urgap-stub-message",
                "parts": [{"kind": "text", "text": AGENT_ANSWER}],
            }
        elif self.server.mode == "working":
            result = self._task(state="working")
        elif self.server.mode == "failed":
            result = self._task(state="failed")
        else:
            result = self._task(state="completed", request=request)
        self._reply({"jsonrpc": "2.0", "id": request["id"], "result": result})


@pytest.fixture
def stub_a2a_agent(request: pytest.FixtureRequest) -> ThreadingHTTPServer:
    """Serve a stub A2A agent on a free localhost port."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), StubA2AHandler)
    server.mode = getattr(request, "param", "completed")
    server.received_requests = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()
    thread.join()


def get_input_ufiles() -> urgap.UFileList:
    """Get the UFiles which are attached to the question as file parts."""
    return urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype=.any.txt#compressions/test.txt",  # noqa: SLF001
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype=.any.txt#compressions/test2.txt",  # noqa: SLF001
            ),
        ],
    )


def get_urun_dict(agent_url: str, tmp_dir: urgap.Path, **parameters) -> urgap.URunDict:  # noqa: ANN003
    """Get a URunDict for an A2ACall run against the given agent URL."""
    return urgap.URunDict(
        {
            "parameters": {
                "A2ACall:1.0.0": {
                    "agent_url": agent_url,
                    "question": "Summarize the attached files.",
                    **parameters,
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )


def get_agent_url(stub_a2a_agent: ThreadingHTTPServer) -> str:
    """Get the base URL of the stub agent."""
    host, port = stub_a2a_agent.server_address
    return f"http://{host}:{port}"


def test_wrapper_a2a_call(
    tmp_dir: urgap.Path,
    stub_a2a_agent: ThreadingHTTPServer,
) -> None:
    """Input files are sent as file parts and returned files are written back."""
    ufiles = get_input_ufiles()
    expected_contents = {ufile.path.read_bytes() for ufile in ufiles}
    a2a_node = urgap.init_unode("A2ACall:1.0.0")
    output_files = a2a_node.run(
        urun_dict=get_urun_dict(get_agent_url(stub_a2a_agent), tmp_dir),
        ufiles=ufiles,
    )

    response_path = output_files.get_path_objects_by_uftype(urgap.uftypes.any.TXT)[0]
    assert response_path.read_text() == AGENT_ANSWER

    artifact_paths = output_files.get_path_objects_by_uftype(urgap.uftypes.any.BLOB)
    assert len(artifact_paths) == 2
    assert all(path.exists() for path in artifact_paths)
    assert {path.read_bytes() for path in artifact_paths} == expected_contents

    sent_request = stub_a2a_agent.received_requests[0]
    assert sent_request["method"] == "message/send"
    sent_parts = sent_request["params"]["message"]["parts"]
    assert sent_parts[0] == {"kind": "text", "text": "Summarize the attached files."}
    assert {
        base64.b64decode(part["file"]["bytes"])
        for part in sent_parts
        if part["kind"] == "file"
    } == expected_contents


def test_wrapper_a2a_call_is_skipped_on_rerun(
    tmp_dir: urgap.Path,
    stub_a2a_agent: ThreadingHTTPServer,
) -> None:
    """A rerun is skipped and recovers the dynamic number of returned files."""
    agent_url = get_agent_url(stub_a2a_agent)
    a2a_node = urgap.init_unode("A2ACall:1.0.0")
    first_run = a2a_node.run(
        urun_dict=get_urun_dict(agent_url, tmp_dir),
        ufiles=get_input_ufiles(),
    )
    second_run = a2a_node.run(
        urun_dict=get_urun_dict(agent_url, tmp_dir),
        ufiles=get_input_ufiles(),
    )
    assert len(stub_a2a_agent.received_requests) == 1
    assert second_run.as_uri_list() == first_run.as_uri_list()
    assert len(second_run.get_path_objects_by_uftype(urgap.uftypes.any.BLOB)) == 2


@pytest.mark.parametrize("stub_a2a_agent", ["message_only"], indirect=True)
def test_wrapper_a2a_call_with_message_answer(
    tmp_dir: urgap.Path,
    stub_a2a_agent: ThreadingHTTPServer,
) -> None:
    """Agents answering with a message instead of a task return no files."""
    a2a_node = urgap.init_unode("A2ACall:1.0.0")
    output_files = a2a_node.run(
        urun_dict=get_urun_dict(get_agent_url(stub_a2a_agent), tmp_dir),
        ufiles=get_input_ufiles(),
    )

    response_path = output_files.get_path_objects_by_uftype(urgap.uftypes.any.TXT)[0]
    assert response_path.read_text() == AGENT_ANSWER
    assert output_files.get_path_objects_by_uftype(urgap.uftypes.any.BLOB) == []


@pytest.mark.parametrize("stub_a2a_agent", ["no_card"], indirect=True)
def test_wrapper_a2a_call_crashes_without_agent_card(
    tmp_dir: urgap.Path,
    stub_a2a_agent: ThreadingHTTPServer,
) -> None:
    """An agent which serves no agent card cannot be talked to."""
    a2a_node = urgap.init_unode("A2ACall:1.0.0")
    with pytest.raises(AgentCardResolutionError):
        a2a_node.run(
            urun_dict=get_urun_dict(get_agent_url(stub_a2a_agent), tmp_dir),
            ufiles=get_input_ufiles(),
        )
    assert stub_a2a_agent.received_requests == []


@pytest.mark.parametrize("stub_a2a_agent", ["working"], indirect=True)
def test_wrapper_a2a_call_polls_until_task_is_done(
    tmp_dir: urgap.Path,
    stub_a2a_agent: ThreadingHTTPServer,
) -> None:
    """Tasks which are not completed right away are polled via tasks/get."""
    a2a_node = urgap.init_unode("A2ACall:1.0.0")
    output_files = a2a_node.run(
        urun_dict=get_urun_dict(
            get_agent_url(stub_a2a_agent),
            tmp_dir,
            poll_interval=1,
        ),
        ufiles=get_input_ufiles(),
    )

    response_path = output_files.get_path_objects_by_uftype(urgap.uftypes.any.TXT)[0]
    assert response_path.read_text() == AGENT_ANSWER
    assert [request["method"] for request in stub_a2a_agent.received_requests] == [
        "message/send",
        "tasks/get",
    ]


@pytest.mark.parametrize("stub_a2a_agent", ["failed"], indirect=True)
def test_wrapper_a2a_call_crashes_on_failed_task(
    tmp_dir: urgap.Path,
    stub_a2a_agent: ThreadingHTTPServer,
) -> None:
    """A task which does not complete successfully crashes the UNode run."""
    a2a_node = urgap.init_unode("A2ACall:1.0.0")
    with pytest.raises(RuntimeError, match="TASK_STATE_FAILED"):
        a2a_node.run(
            urun_dict=get_urun_dict(get_agent_url(stub_a2a_agent), tmp_dir),
            ufiles=get_input_ufiles(),
        )
