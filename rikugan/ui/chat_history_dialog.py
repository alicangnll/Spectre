"""Chat history dialog for browsing and managing old conversations."""

from __future__ import annotations

import json
import os
from datetime import datetime

from ..core.config import RikuganConfig
from ..core.logging import log_debug, log_info
from ..state.history import SessionHistory
from ..state.session import SessionState
from .qt_compat import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    Qt,
    QVBoxLayout,
    QWidget,
)


class ChatHistoryDialog(QDialog):
    """Dialog for browsing and managing old chat sessions."""

    def __init__(self, config: RikuganConfig, parent: QWidget = None):
        super().__init__(parent)
        self._config = config
        self._history = SessionHistory(config)
        self._selected_session_id: str | None = None
        self._sessions: list[dict] = []

        self.setWindowTitle("Rikugan - Old Chats")
        self.setMinimumSize(900, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QLabel {
                color: #d4d4d4;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #569cd6;
            }
            QListWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3c3c3c;
            }
            QListWidget::item:selected {
                background-color: #264f78;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
            QTextEdit {
                background-color: #1a1a1a;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
            QPushButton#delete_btn {
                background-color: #2d1a1a;
                color: #f44747;
                border: 1px solid #f44747;
            }
            QPushButton#delete_btn:hover {
                background-color: #3a2a2a;
            }
            QPushButton#export_btn {
                background-color: #1a2d1a;
                color: #4ec9b0;
                border: 1px solid #4ec9b0;
            }
            QPushButton#export_btn:hover {
                background-color: #2a3a2a;
            }
        """)

        self._build_ui()
        self._load_sessions()

    def _build_ui(self) -> None:
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header with search
        header = QHBoxLayout()
        title_label = QLabel("💬 Chat History")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #569cd6;")
        header.addWidget(title_label)
        header.addStretch()

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("🔍 Search chats...")
        self._search_edit.setFixedWidth(250)
        self._search_edit.textChanged.connect(self._on_search_changed)
        header.addWidget(self._search_edit)

        layout.addLayout(header)

        # Splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Session list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_header = QHBoxLayout()
        self._count_label = QLabel("0 chats")
        self._count_label.setStyleSheet("color: #808080; font-size: 10px;")
        list_header.addWidget(self._count_label)
        list_header.addStretch()

        self._refresh_btn = QPushButton("🔄 Refresh")
        self._refresh_btn.setFixedWidth(80)
        self._refresh_btn.clicked.connect(self._load_sessions)
        list_header.addWidget(self._refresh_btn)

        left_layout.addLayout(list_header)

        self._session_list = QListWidget()
        self._session_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._session_list.itemClicked.connect(self._on_session_selected)
        left_layout.addWidget(self._session_list)

        # Action buttons for selected session
        action_layout = QHBoxLayout()
        action_layout.setSpacing(4)

        self._view_btn = QPushButton("👁️ View")
        self._view_btn.setEnabled(False)
        self._view_btn.clicked.connect(self._view_selected_session)
        action_layout.addWidget(self._view_btn)

        self._export_btn = QPushButton("📥 Export")
        self._export_btn.setObjectName("export_btn")
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._export_selected_session)
        action_layout.addWidget(self._export_btn)

        self._delete_btn = QPushButton("🗑️ Delete")
        self._delete_btn.setObjectName("delete_btn")
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._delete_selected_session)
        action_layout.addWidget(self._delete_btn)

        left_layout.addLayout(action_layout)

        splitter.addWidget(left_panel)

        # Right side: Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        preview_header = QLabel("Preview")
        preview_header.setStyleSheet("font-weight: bold; color: #808080;")
        right_layout.addWidget(preview_header)

        self._preview_text = QTextEdit()
        self._preview_text.setReadOnly(True)
        self._preview_text.setPlaceholderText("Select a chat to preview...")
        right_layout.addWidget(self._preview_text)

        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_sessions(self) -> None:
        """Load all sessions from history."""
        self._sessions = self._history.list_sessions()
        self._update_session_list()

    def _update_session_list(self, search_term: str = "") -> None:
        """Update the session list widget, optionally filtered by search."""
        self._session_list.clear()
        self._count_label.setText(f"{len(self._sessions)} chats")

        search_lower = search_term.lower()
        for session in self._sessions:
            # Apply search filter
            if search_term:
                searchable_text = f"{session.get('description', '')} {session.get('model', '')} {session.get('provider', '')}"
                if search_lower not in searchable_text.lower():
                    continue

            item = self._create_session_item(session)
            self._session_list.addItem(item)

        self._count_label.setText(f"{self._session_list.count()} chats")

    def _create_session_item(self, session: dict) -> QListWidgetItem:
        """Create a list item for a session."""
        # Format date
        created_at = session.get("created_at", 0)
        if created_at:
            date_str = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M")
        else:
            date_str = "Unknown"

        # Format description
        description = session.get("description", "")
        if not description:
            # Generate from first user message if available
            description = "New Chat"

        # Count messages
        msg_count = session.get("messages", 0)

        # Model info
        model = session.get("model", "unknown")
        provider = session.get("provider", "")

        # Create item text
        item_text = f"📅 {date_str}\n💭 {description}\n📊 {msg_count} messages • {provider}/{model}"

        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, session["id"])

        return item

    def _on_search_changed(self, text: str) -> None:
        """Handle search text changes."""
        self._update_session_list(text)

    def _on_session_selected(self, item: QListWidgetItem) -> None:
        """Handle session selection."""
        session_id = item.data(Qt.ItemDataRole.UserRole)
        self._selected_session_id = session_id

        # Enable buttons
        self._view_btn.setEnabled(True)
        self._export_btn.setEnabled(True)
        self._delete_btn.setEnabled(True)

        # Load preview
        self._load_session_preview(session_id)

    def _load_session_preview(self, session_id: str) -> None:
        """Load and display a preview of the session."""
        session = self._history.load_session(session_id)
        if not session:
            self._preview_text.setPlainText("Failed to load session.")
            return

        # Build preview text
        lines = []
        lines.append(f"Session ID: {session.id}")
        lines.append(f"Created: {datetime.fromtimestamp(session.created_at).strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Provider: {session.provider_name}")
        lines.append(f"Model: {session.model_name}")
        if session.idb_path:
            lines.append(f"File: {os.path.basename(session.idb_path)}")
        lines.append(f"Messages: {len(session.messages)}")
        lines.append("")
        lines.append("─" * 60)
        lines.append("")

        # Show first few messages
        preview_count = 0
        max_preview = 10  # Show first 10 messages

        for msg in session.messages:
            role = msg.role.capitalize()
            content = msg.content

            # Truncate long messages
            if len(content) > 200:
                content = content[:200] + "..."

            lines.append(f"**{role}**:")
            lines.append(content)
            lines.append("")
            lines.append("─" * 40)
            lines.append("")

            preview_count += 1
            if preview_count >= max_preview:
                remaining = len(session.messages) - max_preview
                if remaining > 0:
                    lines.append(f"... and {remaining} more messages")
                break

        preview_text = "\n".join(lines)
        self._preview_text.setPlainText(preview_text)

    def _view_selected_session(self) -> None:
        """View the full selected session."""
        if not self._selected_session_id:
            return

        session = self._history.load_session(self._selected_session_id)
        if not session:
            QMessageBox.warning(self, "Error", "Failed to load session.")
            return

        # Create a detailed view dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Session: {self._selected_session_id[:8]}")
        dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout(dialog)

        # Session info
        info_text = f"""
        <b>Session ID:</b> {session.id}<br>
        <b>Created:</b> {datetime.fromtimestamp(session.created_at).strftime('%Y-%m-%d %H:%M:%S')}<br>
        <b>Provider:</b> {session.provider_name}<br>
        <b>Model:</b> {session.model_name}<br>
        <b>Messages:</b> {len(session.messages)}
        """

        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)

        # Full conversation
        from .markdown import md_to_html

        conversation = QTextEdit()
        conversation.setReadOnly(True)

        lines = []
        for msg in session.messages:
            role = msg.role.capitalize()
            lines.append(f"**{role}**:")
            lines.append(msg.content)
            lines.append("")

        full_text = "\n".join(lines)
        conversation.setHtml(md_to_html(full_text))

        layout.addWidget(conversation)

        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec()

    def _export_selected_session(self) -> None:
        """Export the selected session to a file."""
        if not self._selected_session_id:
            return

        session = self._history.load_session(self._selected_session_id)
        if not session:
            QMessageBox.warning(self, "Error", "Failed to load session.")
            return

        # Generate default filename
        date_str = datetime.fromtimestamp(session.created_at).strftime("%Y%m%d-%H%M%S")
        default_name = f"rikugan-chat-{date_str}.md"

        # Get save path
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Chat",
            default_name,
            "Markdown (*.md);;Text (*.txt);;All Files (*)",
        )

        if not path:
            return

        try:
            # Export using the panel's export method
            from ..ui.panel_core import RikuganPanelCore

            RikuganPanelCore._export_session_to_file(session, path, include_subagents=True)
            log_info(f"Exported chat to {path}")
            QMessageBox.information(self, "Success", f"Chat exported to:\n{path}")
        except Exception as e:
            log_error(f"Failed to export chat: {e}")
            QMessageBox.warning(self, "Export Failed", f"Failed to export chat:\n{e}")

    def _delete_selected_session(self) -> None:
        """Delete the selected session after confirmation."""
        if not self._selected_session_id:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this chat? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Delete session
        if self._history.delete_session(self._selected_session_id):
            log_info(f"Deleted session {self._selected_session_id}")

            # Refresh list
            self._load_sessions()

            # Clear preview
            self._preview_text.clear()
            self._selected_session_id = None
            self._view_btn.setEnabled(False)
            self._export_btn.setEnabled(False)
            self._delete_btn.setEnabled(False)

            QMessageBox.information(self, "Deleted", "Chat deleted successfully.")
        else:
            QMessageBox.warning(self, "Error", "Failed to delete chat.")


def show_chat_history(config: RikuganConfig, parent: QWidget = None) -> None:
    """Convenience function to show the chat history dialog."""
    dialog = ChatHistoryDialog(config, parent)
    dialog.exec()
