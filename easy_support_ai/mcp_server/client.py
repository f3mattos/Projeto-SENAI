"""Cliente MCP para invocação de ferramentas com transporte stdio."""
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_tool(tool_name: str, arguments: dict) -> dict:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server/server.py"],
    )

    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            return result.model_dump()


def call_tool_sync(tool_name: str, arguments: dict) -> dict:
    # Se chamado em ambiente com loop ativo, cria nova tarefa
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(call_tool(tool_name, arguments))
    except Exception:
        pass
    return asyncio.run(call_tool(tool_name, arguments))
