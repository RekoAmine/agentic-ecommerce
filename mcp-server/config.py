# ruff: noqa: E402
"""Compatibility wrapper for MCP server configuration."""

import sys
from pathlib import Path

src_path = Path(__file__).resolve().parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from fba_mcp_server.config import McpServerSettings, get_settings  # noqa: E402,F401
