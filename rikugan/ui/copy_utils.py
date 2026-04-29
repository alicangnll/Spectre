"""Copy functionality utilities for IDA Pro Rikugan panel."""

from .qt_compat import QApplication


def add_copy_to_clipboard(text: str) -> None:
    """Copy text to system clipboard."""
    clipboard = QApplication.clipboard()
    # Use the clipboard mode constant - works for both Qt5 and Qt6
    try:
        # Qt6 mode
        clipboard.setText(text, mode=clipboard.Mode.Clipboard)
    except AttributeError:
        # Qt5 fallback
        clipboard.setText(text, mode=1)  # QClipboard::Clipboard = 1


def get_clipboard_text() -> str:
    """Get text from system clipboard."""
    clipboard = QApplication.clipboard()
    try:
        # Qt6 mode
        return clipboard.text(mode=clipboard.Mode.Clipboard)
    except AttributeError:
        # Qt5 fallback
        return clipboard.text(mode=1)  # QClipboard::Clipboard = 1


def create_copy_button_html(block_id: str, raw_code: str) -> str:
    """Create HTML copy button for code blocks."""
    return f'''
    <button
        onclick="RikuganCopyBlock('{block_id}')"
        style="
            position: absolute;
            top: 6px;
            right: 6px;
            background: rgba(86, 156, 214, 0.2);
            border: 1px solid rgba(86, 156, 214, 0.4);
            color: #569cd6;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-family: sans-serif;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 10;
        "
        onmouseover="this.style.opacity='1'"
        onmouseout="this.style.opacity='0'"
        data-block-id="{block_id}"
    >📋</button>
    '''