"""MCP via API integration module for Chainlit chat interface."""

import json
import os

from collections.abc import Callable

import chainlit as cl
import requests

from mcp import ClientSession
from mcp.client.sse import sse_client
from openai import AsyncAzureOpenAI


class CredentialsReaderKong:
    """A class to read credentials for Kong from Azure Key Vault.

    Methods
    -------
    get_token() -> str
        Retrieves token for the specific instance based on provided credentials.
    """

    @staticmethod
    def token_provider(client_id: str, client_secret: str) -> Callable[[], str]:
        """Retrieve token for the specific instance.

        Parameters
        ----------
        client_id : str
            Client id for OAuth that will be used to create token.
        client_secret : str
            Secret for OAuth that will be used to create token.

        Returns
        -------
        str
            Access token retrieved.
        """

        def get_token(client_id: str, client_secret: str) -> str:
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
                "scope": "openid email profile",
            }

            response = requests.post(
                "https://federation-qa.gsk.com/as/token.oauth2",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=data,
            )

            if not response.ok:
                msg = f"Error: {response.status_code}, {response.text}"
                raise Exception(msg)

            return json.loads(response.text).get("access_token")

        return lambda: get_token(client_id, client_secret)


@cl.on_chat_start
async def start() -> None:
    """Initialize chat session with MCP server connection and OpenAI client."""
    # Initialize session variables
    cl.user_session.set("conversation_state", "normal")
    cl.user_session.set("pending_tool_call", None)

    # Initialize conversation history with enhanced system message
    conversation_history = [
        {
            "role": "system",
            "content": """You are a helpful assistant with access to several tools. You MUST make separate tool calls for each distinct request or piece of information asked for.""",
        },
    ]
    cl.user_session.set("conversation_history", conversation_history)
    cl.user_session.set("message_history", conversation_history.copy())

    # Initialize Azure OpenAI client and store in session
    token_provider = CredentialsReaderKong.token_provider(
        os.getenv("CLIENT_ID"), os.getenv("KONG_SECRET"),
    )
    aoi_client = AsyncAzureOpenAI(
        azure_endpoint="https://dev.api.gsk.com/co/rd/cmc/us6",
        api_version="2025-01-01-preview",
        azure_ad_token_provider=token_provider,
    )
    cl.user_session.set("aoi_client", aoi_client)

    # Connect to MCP server and get available tools
    try:
        async with sse_client("http://localhost:3000/sse") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Get available tools from MCP server
                tools_result = await session.list_tools()
                mcp_tools = tools_result.tools

                # Convert MCP tools to OpenAI format
                openai_tools = []
                for tool in mcp_tools:
                    openai_tool = {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                    openai_tools.append(openai_tool)

                # Store tools and server params in session
                cl.user_session.set("openai_tools", openai_tools)
                cl.user_session.set("mcp_tools", mcp_tools)
                cl.user_session.set("server_params", ("http://localhost:3000/sse",))

                await cl.Message(
                    f"Hello! I'm your assistant with access to {len(mcp_tools)} tools. How can I help you today?"
                ).send()

    except Exception as e:
        await cl.Message(
            f"Warning: Could not connect to MCP server: {e}. I'll work without tools for now."
        ).send()
        cl.user_session.set("openai_tools", [])
        cl.user_session.set("mcp_tools", [])
        cl.user_session.set("server_params", None)


@cl.on_message
async def main(message: cl.Message) -> None:
    """Handle incoming messages with OpenAI chat completions."""
    # Get session data with proper defaults
    aoi_client = cl.user_session.get("aoi_client")
    message_history = cl.user_session.get("message_history")
    server_params = cl.user_session.get("server_params")
    openai_tools = cl.user_session.get("openai_tools")
    cl.user_session.get("mcp_tools")

    # Initialize message_history if it's None
    if message_history is None:
        message_history = [
            {
                "role": "system",
                "content": """You are a helpful assistant with access to several tools. You MUST make separate tool calls for each distinct request or piece of information asked for.""",
            },
        ]
        cl.user_session.set("message_history", message_history)

    # Add user message to history
    message_history.append({"role": "user", "content": message.content})

    # Create message placeholder
    msg = cl.Message(content="")
    await msg.send()

    # Call OpenAI API with tools
    response = await aoi_client.chat.completions.create(
        model="o3-mini",  # or your preferred model
        messages=message_history,
        tools=openai_tools if openai_tools else None,
        stream=True,
    )

    # Handle streaming response
    full_response = ""
    tool_calls = []

    async for chunk in response:
        # Check if chunk has choices before accessing
        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta

            if delta.content:
                content = delta.content
                full_response += content
                await msg.stream_token(content)

            # Check for tool calls
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    if len(tool_calls) <= tool_call.index:
                        tool_calls.append(
                            {"id": "", "function": {"name": "", "arguments": ""}},
                        )

                    if tool_call.id:
                        tool_calls[tool_call.index]["id"] = tool_call.id
                    if tool_call.function.name:
                        tool_calls[tool_call.index]["function"]["name"] = (
                            tool_call.function.name
                        )
                    if tool_call.function.arguments:
                        tool_calls[tool_call.index]["function"]["arguments"] += (
                            tool_call.function.arguments
                        )

    await msg.update()

    # If there are tool calls, execute them via MCP
    if tool_calls:
        message_history.append(
            {
                "role": "assistant",
                "content": full_response if full_response else None,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"],
                        },
                    }
                    for tc in tool_calls
                ],
            },
        )

        # Execute tools via MCP
        if server_params:
            async with sse_client(server_params[0]) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    for tool_call in tool_calls:
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])

                        # Execute tool via MCP
                        result = await session.call_tool(tool_name, tool_args)

                        # Add tool result to history
                        message_history.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": json.dumps(result.content) if hasattr(result, "content") else str(result),
                            },
                        )

        # Get final response with tool results
        final_msg = cl.Message(content="")
        await final_msg.send()

        final_response = await aoi_client.chat.completions.create(
            model="gpt-4", messages=message_history, stream=True,
        )

        final_content = ""
        async for chunk in final_response:
            # Check if chunk has choices before accessing
            if chunk.choices and len(chunk.choices) > 0:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    final_content += content
                    await final_msg.stream_token(content)

        await final_msg.update()
        message_history.append({"role": "assistant", "content": final_content})
    else:
        # No tool calls, just add assistant response
        message_history.append({"role": "assistant", "content": full_response})

    # Update session
    cl.user_session.set("message_history", message_history)
