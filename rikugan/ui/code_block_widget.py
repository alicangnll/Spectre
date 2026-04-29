"""Code block widget with copy button for IDA Pro Rikugan panel."""

from .qt_compat import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class CodeBlockWidget(QFrame):
    """A code block display widget with built-in copy button."""

    def __init__(self, code: str, language: str = "", parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("code_block_widget")

        self._code = code
        self._language = language

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with language and copy button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 4, 8, 4)
        header_layout.setSpacing(8)

        # Language label
        if language:
            lang_label = QLabel(language)
            lang_label.setStyleSheet(
                "color: #808080; font-size: 10px; "
                "font-weight: 500; text-transform: uppercase;"
            )
            header_layout.addWidget(lang_label)

        header_layout.addStretch()

        # Copy button
        self._copy_btn = QPushButton("📋 Copy")
        self._copy_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(86, 156, 214, 0.2);
                border: 1px solid rgba(86, 156, 214, 0.4);
                color: #569cd6;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(86, 156, 214, 0.3);
                border: 1px solid rgba(86, 156, 214, 0.6);
            }
            QPushButton:pressed {
                background-color: rgba(86, 156, 214, 0.4);
            }
        """)
        self._copy_btn.setCursor(True)
        self._copy_btn.clicked.connect(self._copy_to_clipboard)

        header_layout.addWidget(self._copy_btn)
        layout.addWidget(header)

        # Code content
        code_label = QLabel(code)
        code_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                white-space: pre-wrap;
                word-break: break-all;
            }
        """)
        code_label.setTextInteractionFlags(
            0x1 | 0x2  # TextSelectableByMouse | TextSelectableByKeyboard
        )
        layout.addWidget(code_label)

    def _copy_to_clipboard(self) -> None:
        """Copy code to clipboard and show feedback."""
        try:
            from .copy_utils import add_copy_to_clipboard
            add_copy_to_clipboard(self._code)

            # Show success state
            self._copy_btn.setText("✓ Copied!")
            self._copy_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(80, 200, 120, 0.3);
                    border: 1px solid #50c878;
                    color: #50c878;
                }
            """)

            # Reset after 1.5 seconds
            from .qt_compat import QTimer
            QTimer.singleShot(1500, self._reset_button)

        except Exception as e:
            self._copy_btn.setText("❌ Failed")
            import sys
            print(f"Failed to copy code: {e}", file=sys.stderr)

            QTimer.singleShot(2000, self._reset_button)

    def _reset_button(self) -> None:
        """Reset button to default state."""
        self._copy_btn.setText("📋 Copy")
        self._copy_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(86, 156, 214, 0.2);
                border: 1px solid rgba(86, 156, 214, 0.4);
                color: #569cd6;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(86, 156, 214, 0.3);
                border: 1px solid rgba(86, 156, 214, 0.6);
            }
            QPushButton:pressed {
                background-color: rgba(86, 156, 214, 0.4);
            }
        """)

    def get_code(self) -> str:
        """Get the code content."""
        return self._code

    def set_language(self, language: str) -> None:
        """Update the language label."""
        self._language = language
        # Update header language label if it exists
        # This would require storing the label reference


def create_code_block_widget(code: str, language: str = "", parent: QWidget = None) -> CodeBlockWidget:
    """Factory function to create a code block widget."""
    return CodeBlockWidget(code, language, parent)