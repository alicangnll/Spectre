"""MCP settings tab: enable/disable Rikugan and external MCP servers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...core.config import RikuganConfig
from ...core.logging import log_debug
from ...mcp.config import MCPServerConfig
from ..qt_compat import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from ..settings_service import SettingsService


class MCPTab(QWidget):
    """Tab for managing MCP servers: Rikugan configured + external MCP."""

    def __init__(self, config: RikuganConfig, service: SettingsService, parent: QWidget = None):
        super().__init__(parent)
        self._config = config
        self._service = service
        self._rikugan_checks: dict[str, QCheckBox] = {}
        self._external_checks: dict[str, QCheckBox] = {}
        self._rikugan_servers: list[MCPServerConfig] = list(service.mcp.rikugan)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)

        # Rikugan MCP servers (pre-loaded by service)
        rikugan_group = self._build_rikugan_group()
        layout.addWidget(rikugan_group)

        # External MCP (pre-loaded by service)
        for source_key, servers in sorted(self._service.mcp.external.items()):
            group = self._build_external_group(source_key, servers)
            layout.addWidget(group)

        layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    def _build_rikugan_group(self) -> QGroupBox:
        """Build the Rikugan MCP servers group box."""
        group = QGroupBox("Rikugan MCP Servers")
        layout = QVBoxLayout(group)

        if not self._rikugan_servers:
            layout.addWidget(QLabel("No MCP servers configured"))
            return group

        # Add "Select All" button row
        button_row = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.setToolTip("Enable all Rikugan MCP servers")
        select_all_btn.clicked.connect(lambda: self._select_all_rikugan_mcp(True))
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setToolTip("Disable all Rikugan MCP servers")
        deselect_all_btn.clicked.connect(lambda: self._select_all_rikugan_mcp(False))
        button_row.addWidget(select_all_btn)
        button_row.addWidget(deselect_all_btn)
        button_row.addStretch()
        layout.addLayout(button_row)

        for server in sorted(self._rikugan_servers, key=lambda s: s.name):
            cb = QCheckBox(f"{server.name}  —  {server.command}")
            cb.setChecked(server.enabled)
            self._rikugan_checks[server.name] = cb
            layout.addWidget(cb)

        return group

    def _select_all_rikugan_mcp(self, checked: bool) -> None:
        """Select or deselect all Rikugan MCP servers."""
        for checkbox in self._rikugan_checks.values():
            checkbox.setChecked(checked)

    def _build_external_group(self, source_key: str, servers: list[MCPServerConfig]) -> QGroupBox:
        """Build a group box for external MCP servers from one source."""
        if source_key == "claude":
            title = "Claude Code MCP Servers"
        elif source_key == "codex":
            title = "Codex MCP Servers"
        else:
            title = f"{source_key} MCP Servers"

        group = QGroupBox(title)
        layout = QVBoxLayout(group)

        if not servers:
            layout.addWidget(QLabel("No MCP servers found"))
            return group

        enabled_set = set(self._config.enabled_external_mcp)

        # Add "Select All" button row for this source
        button_row = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.setToolTip(f"Enable all {source_key} MCP servers")
        select_all_btn.clicked.connect(lambda: self._select_all_external_mcp(source_key, True))
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setToolTip(f"Disable all {source_key} MCP servers")
        deselect_all_btn.clicked.connect(lambda: self._select_all_external_mcp(source_key, False))
        button_row.addWidget(select_all_btn)
        button_row.addWidget(deselect_all_btn)
        button_row.addStretch()
        layout.addLayout(button_row)

        for server in sorted(servers, key=lambda s: s.name):
            ext_id = f"{source_key}:{server.name}"
            cb = QCheckBox(f"{server.name}  —  {server.command}")
            cb.setChecked(ext_id in enabled_set)
            self._external_checks[ext_id] = cb
            layout.addWidget(cb)

        return group

    def _select_all_external_mcp(self, source_key: str, checked: bool) -> None:
        """Select or deselect all external MCP servers from a specific source."""
        for ext_id, checkbox in self._external_checks.items():
            if ext_id.startswith(f"{source_key}:"):
                checkbox.setChecked(checked)

    def apply_to_config(self, config: RikuganConfig) -> None:
        """Write checkbox state back to config fields."""
        # Update Rikugan MCP server enabled state
        for server in self._rikugan_servers:
            cb = self._rikugan_checks.get(server.name)
            if cb is not None:
                server.enabled = cb.isChecked()

        # Persist Rikugan MCP config changes via the service
        if self._rikugan_servers:
            self._service.save_mcp_servers(self._rikugan_servers)

        # Enabled external MCP (checked = enabled)
        config.enabled_external_mcp = [ext_id for ext_id, cb in self._external_checks.items() if cb.isChecked()]

        log_debug(f"MCP config: {len(config.enabled_external_mcp)} external enabled")
