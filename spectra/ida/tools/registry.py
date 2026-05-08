"""IDA tool registry: wires IDA-specific tool modules into the shared ToolRegistry."""

from __future__ import annotations

from spectra.core.host import HAS_HEXRAYS
from spectra.core.thread_safety import idasync
from spectra.tools.registry import ToolRegistry

from . import (
    advanced_decomp,
    annotations,
    collaboration,
    database,
    decompiler,
    disassembly,
    functions,
    kernel_analysis,
    microcode,
    navigation,
    obfuscation_detect,
    scripting,
    strings,
    types_tools,
    xrefs,
)

_TOOL_MODULES = (
    navigation,
    functions,
    strings,
    database,
    disassembly,
    decompiler,
    xrefs,
    annotations,
    types_tools,
    scripting,
    microcode,
    advanced_decomp,
    kernel_analysis,
    obfuscation_detect,
    collaboration,
)


def create_default_registry() -> ToolRegistry:
    """Create a registry with all built-in IDA tools."""
    registry = ToolRegistry(dispatch_wrapper=idasync)
    registry.set_capabilities({"hexrays": HAS_HEXRAYS})
    for mod in _TOOL_MODULES:
        registry.register_module(mod)
    return registry
