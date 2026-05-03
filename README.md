# Spectra (六眼)

*Forked from [Rikugan](https://github.com/buzzer-re/Rikugan)*

A reverse-engineering agent for **IDA Pro**, **Binary Ninja**, and **VSCode** that integrates a multi-provider LLM directly into your analysis workflow. This project was vibecoded together with my friend, Claude Code.

![Spectra IDA Pro](assets/ida_showcase.png)

![Spectra Binary Ninja](assets/binja_showcase.png)

[Documentation](https://spectra.reversing.codes/docs.html) | [Architecture](https://spectra.reversing.codes/ARCHITECTURE.html) | [Issues](https://github.com/alicangnll/Spectra/issues)

## Quick Start

### Accessing Spectra from Different Interfaces

**IDA Pro:**
- Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (macOS)
- Or navigate to: `Edit → Plugins → Spectra`
- Chat panel appears in the IDA UI

**Binary Ninja:**
- Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (macOS)
- Or navigate to: `Tools → Spectra → Open Chat`
- Chat panel appears in the Binary Ninja UI

**VSCode Extension:**
- Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (macOS)
- Or use the Command Palette: `Ctrl+Shift+P` → "Spectra: Open Chat"
- Right-click on code → "Ask Spectra"
- Sidebar chat interface integrated with VSCode

**CLI Mode:**
```bash
# Standalone CLI mode
spectra-cli --help

# Analyze binary directly
spectra-cli analyze /path/to/binary

# Interactive chat mode
spectra-cli chat
```

**JADX CLI (Android APK Analysis):**
```bash
# Analyze Android APKs with JADX integration
python spectra_jadx.py analyze app.apk -o ./decompiled

# Search for strings in decompiled code
python spectra_jadx.py search app.apk "API_KEY"

# Show package structure
python spectra_jadx.py structure app.apk

# Analyze specific class
python spectra_jadx.py class app.apk com.example.MainActivity

# Interactive AI mode for APK analysis
python spectra_jadx.py interactive app.apk
```

## Install

Auto-detects IDA Pro, Binary Ninja, or both.

**Linux / macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/alicangnll/Spectra/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/alicangnll/Spectra/main/install.ps1 | iex
```

For host-specific install, manual setup, and configuration, see the [docs](https://spectra.reversing.codes/docs.html).

## Uninstall

**Linux / macOS:**
```bash
# From the repository
./uninstall.sh

# Or download and run directly
curl -fsSL https://raw.githubusercontent.com/alicangnll/Spectra/main/uninstall.sh | bash
```

**Uninstall Options:**
```bash
# Uninstall from all hosts (default)
./uninstall.sh

# Uninstall from IDA Pro only
./uninstall.sh --ida

# Uninstall from Binary Ninja only
./uninstall.sh --binja

# Uninstall but keep Python dependencies
./uninstall.sh --keep-deps

# Uninstall without confirmation prompts
./uninstall.sh --force
```

**Windows:**
Manual removal required - delete plugin files from IDA/Binary Ninja plugins directories and remove configuration folders.

## Is this another MCP client?

No, Spectra is an ***agent*** built to live inside your RE host. It does not consume an MCP server to interact with the host database; it has its own agentic loop, context management, role prompt ([source](spectra/agent/system_prompt.py)), and an in-process tool orchestration layer.

The agent loop is a generator-based turn cycle: each user message kicks off a stream→execute→repeat pipeline where the LLM response is streamed token-by-token and tool calls are intercepted and dispatched. It supports automatic error recovery, mid-run user questions, plan mode for multi-step workflows, and message queuing — all without leaving the disassembler.

The agent really ***lives*** and ***breathes*** reversing.

- No need to switch to an external MCP client
- Assistant-first, not designed to do your job (unless you ask it to)
- Extensible to many LLM providers and local installations (Ollama)
- Quick to enable — just hit Ctrl+Shift+I and the chat will appear

## Features

**60+ tools** covering navigation, decompiler, disassembly, cross-references, strings, annotations, types, scripting, and host-specific IL/microcode manipulation. The agent always asks permission before running scripts and will never execute the target binary. Full tool reference in the [docs](https://spectra.reversing.codes/docs.html).

**Advanced Memory Corruption & Exploitation Analysis** — v1.2.5+!

The enhanced **Memory Corruption** skill provides comprehensive coverage of modern binary exploitation and mitigation bypass techniques:

- **Out-of-Bounds (OOB) Exploitation** — Array bounds detection, info leaks, corruption chains
- **Use-After-Free (UAF)** — Vtable hijacking, function pointer overwrite, partial overwrite
- **PAC Bypass** — Pointer Authentication Code bypass on ARM64 (iOS, Android)
- **ASLR Bypass** — Address Space Layout Randomization bypass via info leaks, partial overwrite
- **CFI Bypass** — Control Flow Integrity bypass with compatible gadgets
- **CET/Shadow Stack** — Control-flow Enforcement Technology bypass
- **MTE Bypass** — Memory Tagging Extension bypass on Android 14+
- **Remote Code Execution (RCE)** — Network-based exploitation and remote shell techniques
- **Kernel Exploitation** — Kernel-mode exploitation with SMEP/SMAP/KPTI bypass
- **ROP Chain Building** — Automatic ROP gadget discovery and chain construction
- **Modern Mitigation Matrix** — 14+ mitigation bypass strategies with quick reference

**Supported Exploitation Scenarios:**
- ARM64 iOS exploitation with PAC (iPhone 12+)
- Modern Linux with Full RELRO, PIE, Canaries, NX, ASLR
- Windows CFG/CET/ASLR bypass
- Android MTE+PAC exploitation (Android 14+)
- Remote network exploitation with ASLR bypass
- Kernel exploitation with SMEP/SMAP/KPTI

**Advanced Decompilation Integration** — New in v1.2.5! Smart analysis tools that understand your binary:

- **Cross-Reference Visualizer** — Interactive call graphs with complexity metrics and path finding
- **Smart Function Naming** — AI-powered pattern recognition suggests meaningful names for `sub_XXX` functions
- **Type Library Auto-Detection** — Automatically detects platform (Windows/Linux) and recovers structure definitions
- **Code Bookmarking** — Mark important locations with categories, tags, and notes
- **Advanced Search** — Find similar functions using Jaccard similarity, search by patterns/strings/imports

**Security-Focused Analysis Tools** — New in v1.2.5! Malware analysis and vulnerability detection enhancements:

- **Findings Bookmarking** — Bookmark important findings with addresses, notes, tags, and categories (Critical, Suspicious, Verified, Interesting, False Positive, Question). Export findings as markdown reports for documentation.

- **Suspicious API Highlighting** — Automatic color-coded highlighting of dangerous APIs in AI responses based on severity:
  - [CRIT] Critical APIs (red): CreateRemoteThread, WriteProcessMemory, VirtualAllocEx, NtAllocateVirtualMemory
  - [HIGH] High severity APIs (orange): VirtualProtect, GetProcAddress, LoadLibrary
  - [MED] Medium severity APIs (yellow): InternetConnect, HttpSendRequest, socket, CryptEncrypt
  - Each API includes MITRE ATT&CK technique references (T1055, T1014, T1071, etc.)

- **Anti-Debugging Detection** — Automatically detect common anti-debugging techniques used in malware:
  - Windows API checks: IsDebuggerPresent, CheckRemoteDebuggerPresent, NtQueryInformationProcess
  - PEB (Process Environment Block) checks: fs:[30h]/gs:[60h] BeingDebugged access patterns
  - Assembly instructions: rdtsc (timing checks), int 2d (exception-based), int 3 (software breakpoints)
  - Exception handlers: SetUnhandledExceptionFilter, AddVectoredExceptionHandler

- **Hex Address Navigation** — All hex addresses in AI responses become clickable links for quick navigation:
  - Supported formats: 0x401000, 00401000, 401000h, :00401000
  - Click any address to jump to that location in IDA/Binary Ninja disassembly view
  - Use `[FINDING:0x401000]` for bookmarked locations with custom labels

- **Function Name Navigation** — Function names are automatically detected and become clickable:
  - CamelCase functions (e.g., `generatePWFOTP`, `GenerateOTP`) are linked
  - snake_case functions with 8+ characters (e.g., `verify_password`, `calculate_hash`) are linked
  - Common C/C++/Python keywords and types are excluded (int, char, printf, etc.)
  - Click any function name to jump directly to that function's definition in IDA
  - Smart matching avoids linking common words and short identifiers

  **Example Usage:**
  ```
  User: What does the generatePWFOTP function do?
  Spectra: Let me analyze generatePWFOTP for you...
  [Click on generatePWFOTP to jump to the function]

  User: Check the verify_password function
  Spectra: I'll examine verify_password()...
  [Click on verify_password to jump to the function]
  ```

- **Auto-Reload Development Mode** — Automatically reload Spectra when source files change:
  - Enable via environment variable: `export SPECTRA_AUTO_RELOAD=1`
  - Or use keyboard shortcut: `Ctrl+Shift+R` in IDA to toggle on/off
  - Monitors all Python source files and reloads after 2 seconds of inactivity
  - Preserves session state across reloads for rapid development iteration

**Exploration** — Inspired by how code agents work, but applied to binaries. The orchestrator maps the binary (imports, exports, strings, key functions), then spawns isolated subagents to analyze in parallel. Each reports back, and the orchestrator synthesizes a complete picture.

|![Spectra Exploration](assets/subagents_example_3.png)|
|:--:|
|Orchestrator spawning subagents in parallel|

**Natural Language Patches** (Experimental) — `/modify` lets you describe what you want changed in plain English. Spectra explores the binary, builds context, and applies the patches.

|![Spectra Natural Language Patches](assets/maze_solve.gif)|
|:--:|
|`/modify make this maze game easy, let me pass through walls`|

**Deobfuscation** (Experimental, Binary Ninja) — The `/deobfuscation` skill activates plan mode to recognize and remove control flow flattening, opaque predicates, MBA expressions, and junk code using IL read/write primitives.

|![Spectra Deobfuscation](assets/cff_remove_example.gif)|
|:--:|
|~3x speed of the workflow, original process took ~4:30 min|

**JADX Integration - Android APK Analysis** — v1.2.5+!

Comprehensive Android APK reverse engineering with JADX decompiler integration:

- **APK Decompilation** — Automatic decompilation to Java source code using JADX
- **Package Structure Analysis** — Complete package hierarchy, component detection, class/method counting
- **Manifest Parsing** — Extract permissions, components, version info, SDK requirements
- **String Search** — Search decompiled Java sources for API keys, endpoints, credentials
- **Class Analysis** — Analyze dependencies, methods, fields, inheritance hierarchy
- **Native Library Detection** — Find and analyze .so files across different architectures
- **Security Assessment** — Detect debuggable builds, hardcoded secrets, insecure storage
- **Malware Analysis** — Identify suspicious permissions, C2 communication, obfuscation techniques

**CLI Usage:**
```bash
# Analyze APK structure
python spectra_jadx.py analyze app.apk -o ./decompiled

# Search for API endpoints
python spectra_jadx.py search app.apk "http://"

# Analyze specific class
python spectra_jadx.py class app.apk com.example.MainActivity

# Interactive AI mode
python spectra_jadx.py interactive app.apk
```

**Skill Integration:**
```
/jadx Analyze this APK at /path/to/app.apk
/jadx What permissions does this app request?
/jadx Find the MainActivity class
/jadx Search for hardcoded API keys
/jadx Check for native libraries
```

**Memory** — Findings are saved to `SPECTRA.md` next to your database, persisting across sessions.

**Skills & MCP** — 42+ total skills (33 built-in + 9 external), custom skill support, and MCP server integration. Reuse skills and MCP servers from Claude Code and Codex. 

**Latest Skills (v1.2.5+):**
- **Memory Corruption & Mitigation Bypass** — Comprehensive coverage of UAF, OOB, PAC, ASLR, CFI, CET, MTE exploitation
- **Reverse Engineering** — Binary analysis, decompilation, assembly understanding
- **Protocol Analysis** — Network protocol reverse engineering and parsing
- **Crypto Analysis** — Cryptographic algorithm identification and analysis
- **Firmware RE** — Firmware extraction, analysis, and exploitation
- **Web App Security** — Web application vulnerability analysis
- **Binary Exploitation** — OOB, UAF, stack overflow, heap exploitation techniques
- **Kernel Exploit** — Kernel-mode exploitation and privilege escalation
- **ROP Builder** — Automatic ROP chain construction and DEP bypass
- **Android/iOS Exploit** — Mobile platform exploitation techniques
- **Auto Exploit** — Automated exploit generation
- **Malware Analysis** — Malware analysis and reverse engineering
- **CTF Tools** — CTF competition utilities and exploit helpers

**All Built-in Skills:**
```
android-exploit, app-shielding-bypass, auto-exploit, automated-exploit-gen,
binja-scripting, cloud-mobile-security, crypto-analysis, ctf, deobfuscation,
driver-analysis, firmware-re, generic-re, ida-scripting, ios-exploit,
jadx-analysis, (NEW! Android APK reverse engineering)
kernel-exploit, linux-malware, malware-analysis, memory-corruption, (Enhanced)
mobile-malware-analysis, mobile-pentest, modify, protocol-analysis,
race-condition, reverse-engineering, rop-builder, shellcode-generator,
smart-patch-binja, smart-patch-ida, vuln-audit, web-app-security
```

**External Skill Integration:**
- **Claude Code Skills** — Auto-import from `~/.claude/skills/`
- **MCP Servers** — Connect to external MCP servers for extended capabilities
- **Custom Skills** — Create your own skills with custom tools and workflows
- **Codex Skills** — Import skills from Codex editors

## Configuration & Setup

**Provider Configuration:**
```bash
# Claude (Recommended)
export ANTHROPIC_API_KEY="your-key"

# OpenAI-compatible
export OPENAI_API_KEY="your-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"

# Ollama (Local)
export OLLAMA_BASE_URL="http://localhost:11434"

# Custom provider
export CUSTOM_API_KEY="your-key"
export CUSTOM_BASE_URL="https://your-endpoint.com/v1"
```

**MCP Server Integration:**
```json
// ~/.spectra/mcp_servers.json
{
  "servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

**Custom Skills:**
```bash
# Create custom skill directory
mkdir -p ~/.spectra/skills/my-skill

# Add skill.md
cat > ~/.spectra/skills/my-skill/skill.md << 'EOF'
---
name: My Custom Skill
description: Custom analysis workflow
tags: [custom, analysis]
---
Task: Custom analysis task.
EOF
```

**Profile Customization:**
```json
// ~/.spectra/profiles/restricted.json
{
  "name": "restricted",
  "description": "Limited tool access",
  "allowed_tools": ["decompile_function", "get_disasm"],
  "data_filters": {
    "exclude_strings": true,
    "exclude_imports": false
  }
}
```

## Usage Examples

**Basic Reverse Engineering:**
```
User: Analyze this binary and find the main functionality
Spectra: [Explores binary, maps imports/exports, analyzes key functions]

User: What does the function at 0x401000 do?
Spectra: [Decompiles function, explains logic, identifies algorithms]

User: Rename all crypto functions based on their purpose
Spectra: [Identifies crypto functions, suggests meaningful names]
```

**Vulnerability Analysis:**
```
User: Check for memory corruption vulnerabilities
Spectra: [Activates memory-corruption skill, scans for dangerous functions]

User: Analyze this buffer overflow at 0x402000
Spectra: [Activates binary-exploit skill, builds exploitation chain]

User: Can this binary be exploited on modern Linux?
Spectra: [Checks mitigations, suggests bypass strategies]
```

**Malware Analysis:**
```
User: What type of malware is this?
Spectra: [Activates malware-analysis skill, classifies malware family]

User: Find the C2 communication code
Spectra: [Locates network functions, decodes C2 protocol]

User: Extract the configuration
Spectra: [Identifies config structures, decodes encrypted data]
```

## Recommended Providers

| Provider | Notes |
|----------|-------|
| **Claude Opus 4.6** | Best overall. Recommend Claude Pro/Max plan with OAuth over API. |
| **Claude Sonnet 4.6** | Strong at lower cost. Both Anthropic models use prompt caching. |
| **MiniMax M2.5 / Highspeed** | On par with Opus in local tests. Generous limits, low cost. |
| **Gemini 2.5 / 3 / 3.1 Pro** | Solid results. Hallucinates more than Anthropic/MiniMax. |
| **Kimi 2.5** | Strong coding, but lacks rigor for complex RE tasks. |
| **LLAMA 70B / GPT 120B OSS** | Interesting but not production-ready for RE. |

Also supports any OpenAI-compatible endpoint and Ollama for local models.

## Keyboard Shortcuts

**Global Shortcuts (All Interfaces):**
- `Ctrl+Shift+I` / `Cmd+Shift+I` — Open Spectra chat
- `Esc` — Close chat panel (in most interfaces)
- `Ctrl+Enter` — Send message

**IDA Pro Specific:**
- `Edit → Plugins → Spectra` — Menu access
- `Alt+T` — Focus chat input (when chat is open)
- `Ctrl+Tab` — Switch between IDA and chat

**Binary Ninja Specific:**
- `Tools → Spectra → Open Chat` — Menu access
- `Ctrl+Shift+R` — Quick analysis of current function
- `Ctrl+Shift+D` — Decompile and explain current function

**VSCode Extension:**
- `Ctrl+Shift+P` → "Spectra: Open Chat" — Command palette
- `Right-click → Ask Spectra` — Context menu
- `Ctrl+Shift+A` — Analyze selected code
- `Ctrl+Shift+E` — Explain selected function

## Tips & Tricks

**Performance Optimization:**
```
1. Use prompt caching — Anthropic models cache automatically
2. Limit context window — Reduce "max_tokens" for faster responses
3. Batch similar queries — Combine related questions
4. Use profiles — Restrict tools for faster analysis
5. Local models — Use Ollama for offline analysis
```

**Best Practices:**
```
1. Start with exploration — Let Spectra map the binary first
2. Use plan mode — For complex multi-step workflows
3. Leverage memory — Important findings persist across sessions
4. Combine skills — Use multiple skills for comprehensive analysis
5. Verify suggestions — Always verify AI-generated analysis
```

**Advanced Workflows:**
```
# Automated vulnerability assessment
User: /skill vuln-audit
Spectra: [Scans binary, identifies potential vulnerabilities]

# Custom exploitation chain
User: /skill memory-corruption
User: Find OOB vulnerabilities and build RCE exploit
Spectra: [Activates skill, finds bugs, builds exploitation chain]

# Batch analysis
User: Analyze all functions in this binary
Spectra: [Spawns subagents, parallel analysis, comprehensive report]

# Protocol reverse engineering
User: /skill protocol-analysis
User: Decode this network protocol
Spectra: [Identifies protocol structure, builds parser]
```

## Troubleshooting

**Common Issues:**

**Plugin not appearing in IDA/Binary Ninja:**
```bash
# Check installation
spectra-doctor --check-install

# Reinstall plugin
spectra-install --force

# Check Python compatibility
python --version  # Should be 3.10+
```

**API connection issues:**
```bash
# Test API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY"

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test with direct endpoint
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

**Performance issues:**
```bash
# Clear cache
rm -rf ~/.spectra/cache/*

# Reduce context size
# In settings.json: "max_context_tokens": 8192

# Use faster model
export SPECTRA_DEFAULT_MODEL="claude-sonnet-4-6"
```

**Memory/context issues:**
```bash
# Increase memory limit
export SPECTRA_MAX_MEMORY="4096"

# Use streaming mode
export SPECTRA_STREAMING=true

# Enable prompt caching
export SPECTRA_PROMPT_CACHING=true
```

## Requirements

- IDA Pro 9.0+ with Hex-Rays decompiler or Binary Ninja (UI mode)
- Python 3.10+
- At least one LLM provider
- Windows, macOS, or Linux

> **IDA Pro + Python >= 3.14:** Shiboken has a known UAF bug. Spectra includes a workaround, but Python 3.10 is still the safest choice. See the [upstream report](https://community.hex-rays.com/t/ida-9-3-b1-macos-arm64-uaf-crash/646).

## Roadmap

**Near-term (v1.3.x):**
- [ ] Enhanced deobfuscation with ML-based pattern recognition
- [ ] Automated exploit generation with symbolic execution
- [ ] Advanced kernel analysis capabilities
- [ ] Mobile app analysis improvements (iOS/Android)
- [ ] Firmware analysis pipeline enhancements

**Mid-term (v1.4.x):**
- [ ] Multi-binary analysis workflow
- [ ] Collaborative analysis features
- [ ] Enhanced visualization and graphing
- [ ] Integration with more disassemblers (Ghidra, Radare2)
- [ ] Cloud-based analysis options

**Long-term:**
- [ ] Community skill marketplace
- [ ] Plugin system for custom tools
- [ ] Advanced ML-based vulnerability detection
- [ ] Real-time collaboration features
- [ ] Enterprise deployment options

## Contributing

Contributions are welcome! Areas where you can help:

**Skills Development:**
- Create new analysis skills
- Improve existing skill coverage
- Add platform-specific techniques
- Share custom workflows

**Bug Reports & Feature Requests:**
- [Open an issue](https://github.com/alicangnll/Spectra/issues) for bugs
- Suggest new features or improvements
- Share interesting use cases
- Report documentation issues

**Code Contributions:**
- Fork the repository
- Create a feature branch
- Make your changes with tests
- Submit a pull request

**Documentation:**
- Improve documentation
- Add examples and tutorials
- Translate documentation
- Create video tutorials

## Community & Support

**Getting Help:**
- [Documentation](https://spectra.reversing.codes/docs.html)
- [GitHub Issues](https://github.com/alicangnll/Spectra/issues)
- [Discord Community](https://discord.gg/spectra) (coming soon)

**Showcase:**
- Share your analysis workflows
- Post interesting findings
- Demonstrate new techniques
- Contribute to skill library

**Stay Updated:**
- ⭐ Star the repository on GitHub
- 👀 Watch for releases and updates
- 🐦 Follow [@spectra_re](https://twitter.com/spectra_re) for news
- 📧 Subscribe to updates at [spectra.reversing.codes](https://spectra.reversing.codes)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Claude Code** — For being an amazing pair programmer and friend
- **Anthropic** — For building incredible AI models that make this possible
- **Binary Ninja Team** — For the excellent API and support
- **Hex-Rays** — For IDA Pro and the powerful Hex-Rays decompiler
- **Community** — For feedback, testing, and contributions

Special thanks to everyone who provided feedback, reported bugs, and suggested improvements during the development process.

## Conclusion

If you'd asked me last year what I thought about AI doing reverse engineering, I'd probably have said something like "Nah, impossible — it hallucinates, and reverse engineering is not something as simple as writing code." But this year I completely changed my mind when I saw what was achievable. AI is not the ChatGPT from 2023 anymore; it's something entirely different.

For that reason, I decided to invest this year in researching this topic. It's amazing what we can build with agentic coding — it's surreal how quickly I'm learning topics that I simply "didn't have time" to study before.

Spectra is just one of many projects I've built in the last three months. The first version was built in a single night. Within two days it already supported both IDA and Binary Ninja. Within three days, it was essentially what you see here, with only minor tweaks since.

This is a work in progress with many areas for improvement. I took care to ensure this wouldn't be another AI slop project, but I'm certain there is still room to grow. I hope you use it for good. If you find bugs, have suggestions, or want quality-of-life improvements, please open an issue.

That's all — thanks.

---

**Made with passion by [Ali Can Gönüllü](https://github.com/alicangnll)**

*"The future of reverse engineering is automated, intelligent, and accessible to everyone."*
