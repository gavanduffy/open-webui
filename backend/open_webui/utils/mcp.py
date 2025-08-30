import aiohttp
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])


async def get_mcp_server_data(
    url: str, token: Optional[str], connection_type: str
) -> Dict[str, Any]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            if connection_type == "sse" or resp.headers.get(
                "content-type", ""
            ).startswith("text/event-stream"):
                data_str = ""
                async for line in resp.content:
                    if line:
                        decoded = line.decode().strip()
                        if decoded.startswith("data:"):
                            payload = decoded[5:].strip()
                            if payload == "[DONE]":
                                break
                            data_str += payload
                if data_str:
                    return json.loads(data_str)
                return {}
            else:
                return await resp.json()


async def get_mcp_servers_data(servers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    entries = []
    for idx, server in enumerate(servers):
        if server.get("config", {}).get("enable", True):
            entries.append((idx, server))

    tasks = [
        get_mcp_server_data(s["url"], s.get("key"), s.get("type", "http"))
        for (_, s) in entries
    ]

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    for (idx, server), response in zip(entries, responses):
        if isinstance(response, Exception):
            log.error(f"Failed to connect to {server.get('url')} mcp server")
            continue
        results.append(
            {
                "idx": idx,
                "url": server.get("url"),
                "info": response.get("info", {}),
                "tools": response.get("tools", []),
            }
        )
    return results


async def execute_mcp_server(
    token: Optional[str],
    url: str,
    name: str,
    params: Dict[str, Any],
    connection_type: str,
) -> Any:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.post(f"{url}/{name}", json=params, headers=headers) as resp:
            resp.raise_for_status()
            if connection_type == "sse" or resp.headers.get(
                "content-type", ""
            ).startswith("text/event-stream"):
                data_str = ""
                async for line in resp.content:
                    if line:
                        decoded = line.decode().strip()
                        if decoded.startswith("data:"):
                            payload = decoded[5:].strip()
                            if payload == "[DONE]":
                                break
                            data_str += payload
                if not data_str:
                    return {}
                try:
                    return json.loads(data_str)
                except Exception:
                    return {"result": data_str}
            else:
                return await resp.json()
