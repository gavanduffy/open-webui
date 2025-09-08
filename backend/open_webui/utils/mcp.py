import json
import aiohttp
import logging
from typing import List, Optional

# Inspired by MCP client implementations in LibreChat and LobeHub

from open_webui.env import (
    SRC_LOG_LEVELS,
    AIOHTTP_CLIENT_TIMEOUT,
    AIOHTTP_CLIENT_TIMEOUT_TOOL_SERVER_DATA,
    AIOHTTP_CLIENT_SESSION_TOOL_SERVER_SSL,
)

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])


async def fetch_mcp_tools(url: str, server_type: str, token: Optional[str] = None) -> List[str]:
    """Fetch the list of tools exposed by an MCP server."""
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    timeout = aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT_TOOL_SERVER_DATA)
    tools: List[str] = []
    async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
        async with session.get(url, headers=headers, ssl=AIOHTTP_CLIENT_SESSION_TOOL_SERVER_SSL) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to connect to MCP server: {resp.status}")
            if server_type == "sse":
                async for line in resp.content:
                    line = line.decode().strip()
                    if line.startswith("data:"):
                        data = line.split("data:", 1)[1].strip()
                        if data:
                            try:
                                payload = json.loads(data)
                                name = payload.get("name") or payload.get("tool")
                                if name:
                                    tools.append(name)
                            except Exception:
                                continue
            else:
                text = await resp.text()
                try:
                    payload = json.loads(text)
                    if isinstance(payload, dict):
                        tools = payload.get("tools", [])
                    elif isinstance(payload, list):
                        tools = payload
                except Exception:
                    pass
    return tools


async def execute_mcp_tool(
    url: str,
    server_type: str,
    tool: str,
    params: dict,
    token: Optional[str] = None,
):
    """Execute a tool on an MCP server and stream the response."""
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    timeout = aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT)
    session = aiohttp.ClientSession(timeout=timeout, trust_env=True)
    async with session.post(
        url,
        headers=headers,
        json={"tool": tool, "input": params},
        ssl=AIOHTTP_CLIENT_SESSION_TOOL_SERVER_SSL,
    ) as resp:
        if resp.status != 200:
            await session.close()
            raise Exception(f"Failed to call tool: {resp.status}")

        async def stream():
            try:
                if server_type == "sse":
                    async for line in resp.content:
                        line = line.decode().strip()
                        if line.startswith("data:"):
                            yield line.split("data:", 1)[1].strip()
                else:
                    async for chunk in resp.content.iter_any():
                        yield chunk.decode()
            finally:
                await session.close()

        return stream()
