#!/usr/bin/env python3
"""Simple DateTime MCP Server for AgenticScrum using stdio."""

import asyncio
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from datetime_tools import DateTimeTools


class DateTimeServer:
    """DateTime MCP Server for AgenticScrum."""
    
    def __init__(self):
        self.server = Server("datetime-mcp")
        self.dt_tools = DateTimeTools()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up request handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Return list of available datetime tools."""
            return [
                types.Tool(
                    name="get_current_time",
                    description="Get current time in specified timezone (or UTC if not specified)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timezone": {
                                "type": "string",
                                "description": "Timezone name (e.g., 'US/Eastern', 'Europe/London', 'UTC')"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="format_datetime",
                    description="Format datetime string in various standard formats",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timestamp": {
                                "type": "string",
                                "description": "ISO format timestamp or parseable date string"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["ISO8601", "RFC3339", "human", "date", "time", "short", "log", "filename"],
                                "description": "Output format type"
                            }
                        },
                        "required": ["timestamp"]
                    }
                ),
                types.Tool(
                    name="calculate_duration",
                    description="Calculate duration between two timestamps",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "start": {
                                "type": "string",
                                "description": "Start timestamp"
                            },
                            "end": {
                                "type": "string",
                                "description": "End timestamp"
                            }
                        },
                        "required": ["start", "end"]
                    }
                ),
                types.Tool(
                    name="calculate_sprint_dates",
                    description="Calculate Agile sprint start/end dates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "Proposed start date"
                            },
                            "sprint_length_days": {
                                "type": "integer",
                                "description": "Sprint length in days",
                                "default": 14
                            }
                        },
                        "required": ["start_date"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Optional[Dict[str, Any]] = None
        ) -> List[types.TextContent]:
            """Handle tool execution."""
            args = arguments or {}
            
            try:
                if name == "get_current_time":
                    result = self.dt_tools.get_current_time(args.get("timezone"))
                
                elif name == "format_datetime":
                    result = self.dt_tools.format_datetime(
                        args["timestamp"],
                        args.get("format", "ISO8601")
                    )
                
                elif name == "calculate_duration":
                    result = self.dt_tools.calculate_duration(
                        args["start"],
                        args["end"]
                    )
                
                elif name == "calculate_sprint_dates":
                    result = self.dt_tools.calculate_sprint_dates(
                        args["start_date"],
                        args.get("sprint_length_days", 14)
                    )
                
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}, indent=2)
                )]
    
    async def run(self):
        """Run the server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="datetime-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point."""
    server = DateTimeServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())