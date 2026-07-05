"""Runtime compatibility shims.

This project relies on LangChain which (in recent versions) imports
`InjectedState`, `InjectedStore`, and `ToolRuntime` from `langgraph.prebuilt`.

Some LangGraph versions keep these symbols under `langgraph.prebuilt.tool_node`
without re-exporting them at the package root.

Python automatically imports `sitecustomize` (if present on `sys.path`) at
startup, so we can safely patch the module exports before LangChain is imported.
"""

from __future__ import annotations


def _patch_langgraph_prebuilt_exports() -> None:
    try:
        import langgraph.prebuilt as prebuilt
        from langgraph.prebuilt import tool_node

        for name in ("InjectedState", "InjectedStore", "ToolRuntime"):
            if not hasattr(prebuilt, name) and hasattr(tool_node, name):
                setattr(prebuilt, name, getattr(tool_node, name))
    except Exception:
        # Best-effort shim only; never block app startup.
        return


_patch_langgraph_prebuilt_exports()
