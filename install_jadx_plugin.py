#!/usr/bin/env python3
"""
Rikugan JADX Plugin Installer

Automatically installs Rikugan as a JADX plugin.
Supports Linux, macOS, and Windows.
"""

import os
import shutil
import sys
import json
import platform
from pathlib import Path

__version__ = "1.0.0"


def get_jadx_plugin_dir() -> Path:
    """Find JADX plugin directory."""

    # Check for JADX in common locations
    possible_paths = [
        Path.home() / ".jadx" / "plugins",
        Path("/usr/local/share/jadx/plugins"),
        Path("/opt/jadx/plugins"),
        Path.home() / "AppData" / "Local" / "jadx" / "plugins",  # Windows
    ]

    for path in possible_paths:
        if path.exists() or path.parent.exists():
            return path

    # Default to ~/.jadx/plugins
    default_path = Path.home() / ".jadx" / "plugins"
    default_path.mkdir(parents=True, exist_ok=True)
    return default_path


def install_plugin() -> int:
    """Install Rikugan as JADX plugin."""

    print("="*60)
    print("  Rikugan JADX Plugin Installer")
    print("="*60)

    # Get current directory (Rikugan root)
    rikugan_root = Path(__file__).parent.absolute()
    plugin_dir = get_jadx_plugin_dir()

    # Create plugin directory
    rikugan_plugin_dir = plugin_dir / "rikugan"
    rikugan_plugin_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 Installing to: {rikugan_plugin_dir}")

    # Copy main script
    script_source = rikugan_root / "rikugan_jadx.py"
    script_dest = rikugan_plugin_dir / "rikugan_jadx.py"

    if script_source.exists():
        shutil.copy2(script_source, script_dest)
        print(f"✅ Copied: rikugan_jadx.py")
    else:
        print(f"❌ Error: {script_source} not found")
        return 1

    # Copy rikugan module
    rikugan_module_source = rikugan_root / "rikugan"
    rikugan_module_dest = rikugan_plugin_dir / "rikugan"

    if rikugan_module_source.exists():
        if rikugan_module_dest.exists():
            shutil.rmtree(rikugan_module_dest)
        shutil.copytree(rikugan_module_source, rikugan_module_dest)
        print(f"✅ Copied: rikugan/ module")
    else:
        print(f"❌ Error: {rikugan_module_source} not found")
        return 1

    # Create plugin.json
    plugin_config = {
        "name": "Rikugan",
        "version": __version__,
        "description": "AI-powered Android APK analysis assistant",
        "author": "Ali Can Gönüllü",
        "main": "rikugan_jadx.py",
        "enabled": True,
        "dependencies": [
            "anthropic>=0.18.0",
            "httpx>=0.24.0"
        ],
        "capabilities": [
            "apk_analysis",
            "string_search",
            "manifest_parsing",
            "security_assessment",
            "native_library_detection",
            "interactive_mode"
        ]
    }

    config_path = rikugan_plugin_dir / "plugin.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(plugin_config, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: plugin.json")

    # Create default config
    default_config = {
        "auto_analyze": True,
        "ai_provider": "anthropic",
        "api_key": "",
        "max_tokens": 8192,
        "security_checks": {
            "permissions": True,
            "hardcoded_secrets": True,
            "network_security": True,
            "native_libraries": True,
            "debuggable_check": True,
            "backup_check": True
        }
    }

    config_file_path = rikugan_plugin_dir / "config.json"
    with open(config_file_path, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: config.json")

    # Create README
    readme_content = """# Rikugan JADX Plugin

AI-powered Android APK analysis assistant for JADX decompiler.

## Usage

### From JADX GUI:
Tools → Rikugan → Analyze APK

### From CLI:
```bash
python rikugan_jadx.py analyze app.apk -o output
python rikugan_jadx.py search app.apk "API_KEY"
python rikugan_jadx.py interactive app.apk
```

## Features

- Automatic APK decompilation and analysis
- String search for API keys, endpoints, credentials
- AndroidManifest parsing and permission analysis
- Native library detection
- Security assessment
- Interactive AI mode

## Configuration

Edit `config.json` to customize:
- AI provider (anthropic, openai, etc.)
- API keys
- Security check preferences
- Analysis options

## Requirements

- JADX 1.4.7+
- Python 3.10+
- anthropic>=0.18.0
- httpx>=0.24.0

## Support

For issues and updates:
https://github.com/alicangnll/Rikugan
"""

    readme_path = rikugan_plugin_dir / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"✅ Created: README.md")

    print("\n" + "="*60)
    print("  Installation Complete!")
    print("="*60)
    print(f"\n📦 Plugin installed to: {rikugan_plugin_dir}")
    print(f"🔧 Plugin config: {config_file_path}")
    print(f"\n📖 Next steps:")
    print(f"   1. Configure API key in: {config_file_path}")
    print(f"   2. Restart JADX if running")
    print(f"   3. Check Tools → Rikugan menu in JADX GUI")
    print(f"\n📚 Documentation: See README.md in plugin directory")

    return 0


def uninstall_plugin() -> int:
    """Uninstall Rikugan JADX plugin."""

    print("="*60)
    print("  Rikugan JADX Plugin Uninstaller")
    print("="*60)

    plugin_dir = get_jadx_plugin_dir()
    rikugan_plugin_dir = plugin_dir / "rikugan"

    if not rikugan_plugin_dir.exists():
        print("❌ Rikugan plugin not found")
        return 1

    print(f"\n🗑️  Removing: {rikugan_plugin_dir}")

    try:
        shutil.rmtree(rikugan_plugin_dir)
        print("✅ Plugin uninstalled successfully")
        return 0
    except Exception as e:
        print(f"❌ Error uninstalling: {e}")
        return 1


def main() -> int:
    """Main entry point."""

    import argparse

    parser = argparse.ArgumentParser(
        description="Install/uninstall Rikugan as JADX plugin"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Uninstall the plugin"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    if args.uninstall:
        return uninstall_plugin()
    else:
        return install_plugin()


if __name__ == "__main__":
    sys.exit(main())