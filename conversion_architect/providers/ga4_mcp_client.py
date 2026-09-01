"""
GA4 MCP Client

Stdio-based MCP client for Google Analytics 4 MCP server.
Launches the analytics-mcp subprocess and exposes run_report and other tools.
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
from contextlib import asynccontextmanager
from typing import Any

logger = logging.getLogger(__name__)


class GA4MCPClientError(Exception):
    """Error communicating with GA4 MCP server."""
    pass


class GA4MCPClient:
    """Async client for Google Analytics MCP server.
    
    Wraps the analytics-mcp stdio server using the MCP Python SDK.
    
    Usage:
        client = GA4MCPClient(
            credentials_path="/path/to/credentials.json",
            project_id="my-gcp-project"
        )
        await client.connect()
        
        result = await client.run_report(
            property_id="properties/123456789",
            start_date="30daysAgo",
            end_date="today",
            dimensions=["sessionSource", "sessionMedium"],
            metrics=["sessions", "conversions"]
        )
        
        await client.disconnect()
    
    The MCP server is launched as a subprocess via stdio. Tools are:
    - run_report: Standard GA4 Data API report
    - run_funnel_report: Funnel analysis report
    - run_realtime_report: Real-time data
    - get_account_summaries: List accounts and properties
    - get_property_details: Property configuration
    - get_custom_dimensions_and_metrics: Custom dimensions
    """
    
    def __init__(
        self,
        credentials_path: str | None = None,
        project_id: str | None = None,
        mcp_command: str | None = None,
    ):
        """Initialize GA4 MCP client.
        
        Args:
            credentials_path: Path to Google OAuth credentials JSON
            project_id: Google Cloud project ID
            mcp_command: Override the MCP server command (default: analytics-mcp)
        """
        self._credentials_path = credentials_path or os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        self._project_id = project_id or os.environ.get("GOOGLE_PROJECT_ID")
        self._mcp_command = mcp_command or self._find_mcp_command()
        self._session = None
        self._read_stream = None
        self._write_stream = None
        self._process: asyncio.subprocess.Process | None = None
        self._connected = False
    
    def _find_mcp_command(self) -> str:
        """Find the analytics-mcp command."""
        # Check PATH first
        cmd = shutil.which("analytics-mcp")
        if cmd:
            return cmd
        cmd = shutil.which("google-analytics-mcp")
        if cmd:
            return cmd
        # Fallback to known pipx location
        home = os.path.expanduser("~")
        candidates = [
            f"{home}/.local/bin/analytics-mcp",
            f"{home}/.local/bin/google-analytics-mcp",
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        # Last resort
        return "analytics-mcp"
    
    async def connect(self) -> bool:
        """Connect to GA4 MCP server.

        Returns:
            True if connection successful

        Raises:
            GA4MCPClientError if connection fails (or times out)
        """
        import asyncio

        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError:
            raise GA4MCPClientError(
                "mcp package not installed. Run: pip install mcp"
            )

        if not self._credentials_path:
            logger.warning(
                "GOOGLE_APPLICATION_CREDENTIALS not set. "
                "GA4 API calls will fail without valid credentials."
            )

        env = os.environ.copy()
        if self._credentials_path:
            env["GOOGLE_APPLICATION_CREDENTIALS"] = self._credentials_path
        if self._project_id:
            env["GOOGLE_PROJECT_ID"] = self._project_id

        try:
            params = StdioServerParameters(
                command=self._mcp_command,
                args=[],
                env=env,
            )

            async def _do_connect() -> None:
                self._stdio_context = stdio_client(params)
                self._read_stream, self._write_stream = await self._stdio_context.__aenter__()
                self._session = ClientSession(self._read_stream, self._write_stream)
                await self._session.__aenter__()
                await self._session.initialize()

            # Bound the entire MCP handshake. Without this, an auth-failing
            # subprocess hangs the whole FastAPI startup and /health never
            # responds, which Railway marks as a failed deploy.
            await asyncio.wait_for(_do_connect(), timeout=15.0)

            self._connected = True
            logger.info(f"Connected to GA4 MCP server: {self._mcp_command}")
            return True

        except asyncio.TimeoutError:
            logger.warning(
                "GA4 MCP connect timed out after 15s. "
                "Continuing without MCP; adapter will return mock data."
            )
            raise GA4MCPClientError("MCP connect timed out")
        except Exception as e:
            logger.error(f"Failed to connect to GA4 MCP: {e}")
            raise GA4MCPClientError(f"Connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from GA4 MCP server."""
        try:
            if self._session:
                await self._session.__aexit__(None, None, None)
            if hasattr(self, "_stdio_context"):
                await self._stdio_context.__aexit__(None, None, None)
            self._connected = False
            logger.info("Disconnected from GA4 MCP server")
        except Exception as e:
            logger.warning(f"Error during MCP disconnect: {e}")
    
    async def _call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """Call an MCP tool.
        
        Args:
            tool_name: Name of the MCP tool
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        if not self._connected or not self._session:
            raise GA4MCPClientError("Not connected to MCP server")
        
        try:
            result = await self._session.call_tool(tool_name, arguments or {})
            return result
        except Exception as e:
            logger.error(f"MCP tool call failed ({tool_name}): {e}")
            raise GA4MCPClientError(f"Tool call failed: {e}")
    
    async def list_tools(self) -> list[dict[str, Any]]:
        """List available MCP tools."""
        if not self._connected or not self._session:
            raise GA4MCPClientError("Not connected to MCP server")
        
        try:
            tools_response = await self._session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
                for tool in tools_response.tools
            ]
        except Exception as e:
            raise GA4MCPClientError(f"Failed to list tools: {e}")
    
    async def get_account_summaries(self) -> list[dict[str, Any]]:
        """List Google Analytics accounts and properties.
        
        Returns:
            List of account/property summaries
        """
        result = await self._call_tool("get_account_summaries", {})
        return self._extract_content(result)
    
    async def get_property_details(self, property_id: str) -> dict[str, Any]:
        """Get details for a specific GA4 property.
        
        Args:
            property_id: GA4 property ID (e.g., 'properties/123456789')
            
        Returns:
            Property details
        """
        result = await self._call_tool(
            "get_property_details",
            {"property_id": property_id}
        )
        return self._extract_content(result)
    
    async def run_report(
        self,
        property_id: str,
        start_date: str,
        end_date: str,
        dimensions: list[str] | None = None,
        metrics: list[str] | None = None,
        dimension_filter: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Run a GA4 Data API report.
        
        Args:
            property_id: GA4 property ID
            start_date: Start date (YYYY-MM-DD or relative like '30daysAgo')
            end_date: End date (YYYY-MM-DD or 'today')
            dimensions: List of dimension names
            metrics: List of metric names
            dimension_filter: Optional filter expression
            limit: Max rows to return
            
        Returns:
            Report data with rows, headers, and metadata
        """
        args = {
            "property_id": property_id,
            "date_ranges": [
                {"start_date": start_date, "end_date": end_date}
            ],
            "dimensions": [{"name": d} for d in (dimensions or [])],
            "metrics": [{"name": m} for m in (metrics or [])],
        }
        if dimension_filter:
            args["dimension_filter"] = dimension_filter
        if limit:
            args["limit"] = str(limit)
        
        result = await self._call_tool("run_report", args)
        return self._extract_content(result)
    
    async def run_funnel_report(
        self,
        property_id: str,
        start_date: str,
        end_date: str,
        funnel_steps: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Run a funnel analysis report.
        
        Args:
            property_id: GA4 property ID
            start_date: Start date
            end_date: End date
            funnel_steps: List of funnel step definitions
            
        Returns:
            Funnel report data
        """
        args = {
            "property_id": property_id,
            "date_ranges": [
                {"start_date": start_date, "end_date": end_date}
            ],
            "funnel": {"steps": funnel_steps},
        }
        result = await self._call_tool("run_funnel_report", args)
        return self._extract_content(result)
    
    async def run_realtime_report(
        self,
        property_id: str,
        dimensions: list[str] | None = None,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run a real-time report.
        
        Args:
            property_id: GA4 property ID
            dimensions: Optional dimensions
            metrics: Optional metrics
            
        Returns:
            Real-time report data
        """
        args = {
            "property_id": property_id,
            "dimensions": [{"name": d} for d in (dimensions or [])],
            "metrics": [{"name": m} for m in (metrics or [])],
        }
        result = await self._call_tool("run_realtime_report", args)
        return self._extract_content(result)
    
    def _extract_content(self, result: Any) -> Any:
        """Extract content from MCP tool result.
        
        MCP tool results come as a list of content blocks.
        """
        if hasattr(result, "content"):
            content = result.content
            # Concatenate text blocks
            if isinstance(content, list):
                texts = []
                for block in content:
                    if hasattr(block, "text"):
                        texts.append(block.text)
                    elif isinstance(block, dict) and "text" in block:
                        texts.append(block["text"])
                    else:
                        texts.append(str(block))
                combined = "\n".join(texts)
                # Try to parse as JSON
                import json
                try:
                    return json.loads(combined)
                except json.JSONDecodeError:
                    return combined
            return content
        return result
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to MCP server."""
        return self._connected


def create_ga4_mcp_client(
    credentials_path: str | None = None,
    project_id: str | None = None,
) -> GA4MCPClient:
    """Create GA4 MCP client instance."""
    return GA4MCPClient(
        credentials_path=credentials_path,
        project_id=project_id,
    )