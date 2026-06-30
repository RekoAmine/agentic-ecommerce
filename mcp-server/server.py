# ruff: noqa: E402
"""Repository-level executable wrapper for the MCP server."""

import sys
from pathlib import Path

src_path = Path(__file__).resolve().parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from fba_mcp_server.server import main  # noqa: E402

if __name__ == "__main__":
    main()
