from __future__ import annotations

import json
import sys
from typing import Any, Callable

from authoring import service


SERVER_INFO = {"name": "oldtupi-authoring", "version": "0.1.0"}


def tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "list_sources",
            "description": "List historic corpus sources and their approved-ground-truth record counts.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_source_context",
            "description": "Get one source record, rendered output, and neighboring approved targets. Use this before proposing a Pydicate expression.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "record_id": {"oneOf": [{"type": "string"}, {"type": "integer"}]},
                    "radius": {"type": "integer", "minimum": 0, "maximum": 20},
                },
                "required": ["source", "record_id"],
            },
        },
        {
            "name": "render_candidate",
            "description": "Safely render one candidate Pydicate expression in the context of a trusted historic source. This tool never edits files.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "expression": {"type": "string"},
                    "record_id": {"oneOf": [{"type": "string"}, {"type": "integer"}]},
                },
                "required": ["source", "expression"],
            },
        },
        {
            "name": "search_rendered_expressions",
            "description": "Find previously rendered historic expressions by surface form, translation, or recorded analysis.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                "required": ["query"],
            },
        },
        {
            "name": "search_lexicon",
            "description": "Search runtime Old Tupi lexicon entries by variable name, rendered form, or definition.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                "required": ["query"],
            },
        },
        {
            "name": "verify_ground_truth",
            "description": "Compare all approved targets for one historic source, or all sources, with current renderings. This tool never edits files.",
            "inputSchema": {
                "type": "object",
                "properties": {"source": {"type": "string"}},
            },
        },
    ]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    handlers: dict[str, Callable[..., Any]] = {
        "list_sources": service.list_sources,
        "get_source_context": service.get_source_context,
        "render_candidate": service.render_candidate,
        "search_rendered_expressions": service.search_rendered_expressions,
        "search_lexicon": service.search_lexicon,
        "verify_ground_truth": service.verify_ground_truth,
    }
    handler = handlers.get(name)
    if handler is None:
        raise KeyError(f"Unknown tool: {name}")
    return handler(**arguments)


def result_message(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_message(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return result_message(
            request_id,
            {
                "protocolVersion": request.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
            },
        )
    if method == "tools/list":
        return result_message(request_id, {"tools": tool_definitions()})
    if method == "tools/call":
        params = request.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(name, str) or not isinstance(arguments, dict):
            return error_message(request_id, -32602, "tools/call needs a string name and object arguments.")
        try:
            structured = call_tool(name, arguments)
        except Exception as exc:
            return result_message(
                request_id,
                {
                    "content": [{"type": "text", "text": f"{exc.__class__.__name__}: {exc}"}],
                    "isError": True,
                },
            )
        text = json.dumps(structured, ensure_ascii=False, indent=2, sort_keys=True)
        return result_message(
            request_id,
            {
                "content": [{"type": "text", "text": text}],
                "structuredContent": structured,
                "isError": False,
            },
        )
    return error_message(request_id, -32601, f"Method not found: {method}")


def main() -> int:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            request = json.loads(raw)
            if not isinstance(request, dict):
                raise ValueError("Request must be a JSON object.")
            response = handle_request(request)
        except Exception as exc:
            response = error_message(None, -32700, f"Parse error: {exc}")
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
