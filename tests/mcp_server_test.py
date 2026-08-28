from __future__ import annotations

import unittest

from authoring.mcp_server import handle_request


class McpServerTest(unittest.TestCase):
    def test_initialize_advertises_tool_capability(self) -> None:
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05"},
            }
        )
        self.assertEqual(
            response["result"]["capabilities"], {"tools": {"listChanged": False}}
        )
        self.assertEqual(response["result"]["serverInfo"]["name"], "oldtupi-authoring")

    def test_tools_list_contains_only_read_or_evaluation_tools(self) -> None:
        response = handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertEqual(
            names,
            {
                "list_sources",
                "get_source_context",
                "render_candidate",
                "search_rendered_expressions",
                "search_lexicon",
                "verify_ground_truth",
            },
        )


if __name__ == "__main__":
    unittest.main()
