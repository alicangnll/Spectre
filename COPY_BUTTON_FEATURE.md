# Rikugan Copy Button Feature

## 📋 Code Block Copy Functionality

All code blocks in Rikugan documentation now include **one-click copy** functionality!

### Features

**🔥 Smart Copy Buttons:**
- ✅ **Block-level code** - Hover over any code block to reveal the copy button
- ✅ **Inline code** - Click directly on inline code snippets to copy
- ✅ **Visual feedback** - Success/error states with animations
- ✅ **Keyboard shortcuts** - `Ctrl/Cmd + Shift + C` to copy focused code
- ✅ **Mobile support** - Touch-friendly with long-press support
- ✅ **Batch copy** - Copy all code blocks at once

### How to Use

**Desktop:**
1. **Block code**: Hover over any code block and click the "📋" button
2. **Inline code**: Click directly on the code snippet
3. **Keyboard**: Focus a code block and press `Ctrl/Cmd + Shift + C`

**Mobile:**
1. Tap the copy button that appears above code blocks
2. For inline code, tap directly on the code snippet

### Supported Code Types

✅ **Markdown code blocks**:
```python
def example():
    return "Click to copy me!"
```

✅ **Syntax highlighted blocks**:
```javascript
function copyMe() {
  return "Easy!";
}
```

✅ **Inline code**: `copy-this-function()`

✅ **Multi-language support**: Python, JavaScript, Java, C++, Bash, SQL, JSON, XML, HTML, CSS, and more

### Visual Feedback

**Default State:**
- 📋 Copy button (hover only on desktop)
- Subtle border and background
- "Click to copy" tooltip

**Success State:**
- ✓ Green checkmark
- "Copied!" feedback
- Smooth animation

**Error State:**
- ❌ Error indicator
- "Failed to copy" message
- Auto-retry available

### Accessibility

- ⌨️ **Keyboard navigation**: Tab to buttons, Enter to copy
- 🎯 **ARIA labels**: Screen reader support
- 📱 **Touch targets**: Minimum 44x44 pixels for mobile
- 🔊 **Status announcements**: Copy success/failure feedback

### Technical Details

**Browser Support:**
- ✅ Modern Clipboard API (HTTPS)
- ✅ Fallback for older browsers (execCommand)
- ✅ Cross-platform compatibility

**Performance:**
- 🚀 Lazy loading (only when needed)
- ⚡ Efficient DOM updates
- 🔄 Automatic content detection

**Privacy:**
- 🔒 No data collection or tracking
- 📊 Optional analytics integration
- 🔐 Secure clipboard access only

### Developer Integration

**For Rikugan Developers:**
```javascript
// Manual initialization
window.RikuganCopyButton.init();

// Copy specific code block
window.RikuganEnhancedCopy.copyBlock(codeElement);

// Copy inline code
window.RikuganEnhancedCopy.copyInline(codeElement);

// Detect language
const lang = window.RikuganEnhancedCopy.detectLanguage(codeElement);
```

### Files Added

- `webpage/assets/copy-button.css` - Copy button styling
- `webpage/assets/copy-button.js` - Core copy functionality
- `webpage/assets/enhanced-copy.js` - Enhanced features for all code types

### Browser Compatibility

| Browser | Version | Notes |
|---------|---------|-------|
| Chrome | 90+ | Full support |
| Firefox | 88+ | Full support |
| Safari | 14+ | Full support |
| Edge | 90+ | Full support |
| Opera | 76+ | Full support |

### Known Issues

- ⚠️ **HTTP sites**: Clipboard API requires HTTPS (fallback available)
- ⚠️ **Very old browsers**: execCommand fallback may not work
- ⚠️ **Frame restrictions**: Copy buttons may not work in iframes

### Future Enhancements

- 📋 **Copy with line numbers** option
- 🔍 **Search and highlight** in copied code
- 📊 **Usage analytics** dashboard
- 🎨 **Custom button themes**
- 🌐 **Multi-language support** for button text

---

**Status**: ✅ Active and maintained
**Last Updated**: 2025-04-29
**Version**: 1.0.0
