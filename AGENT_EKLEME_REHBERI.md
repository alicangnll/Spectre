# Rikugan Agent Ekleme Rehberi

Rikugan'a yeni agent'lar eklemenin 3 ana yolu vardır:

## 1. Yeni Skill Oluşturma (En Kolay)

Skill'ler aslında agent olarak davranır. Yeni bir skill oluşturarak yeni agent ekleyebilirsiniz.

### Skill Yapısı:

```
my-custom-agent/
├── skill.md           # Agent tanımı ve talimatlar
└── (opsiyonel)       # Ek dosyalar (varsa)
```

### Örnek: Yeni Agent Oluşturma

```bash
# 1. Yeni skill dizini oluştur
cd /path/to/Rikugan/rikugan/skills/builtins
mkdir my-custom-agent
cd my-custom-agent

# 2. skill.md oluştur
cat > skill.md << 'EOF'
---
name: My Custom Agent
description: Özel analiz agent'i - belirli bir alanda uzmanlaşır
tags: [custom, analysis, specialized]
mode: plan
---
Task: Bu agent X analizini yapar.

## Approach
- Adım 1: ...
- Adım 2: ...
- Adım 3: ...

## Tools Used
- tool_name_1
- tool_name_2

## Workflow
1. tool_name_1 → ...
2. tool_name_2 → ...
3. ...

## Expected Output
- ...
EOF
```

### 3. Skill'i Kaydet

```bash
# Skill otomatik olarak yüklenir
# Rikugan bir sonraki açılışında skill'i keşfeder
```

### 4. IDA Pro İçinde Kullanma

```
// Rikugan panelinde (Ctrl+Shift+I)
/my-custom-analyze

// Veya otomatik olarak
/my-custom-analyze this function
```

## 2. Mevcut Skill'i Kopyalama ve Değiştirme

Mevcut bir skill'i kopyalayı ihtiyaclarınıza göre değiştirin.

### Örnek: Vuln-Audit Skill'ini Özelleştirme

```bash
# 1. Vuln-audit skill'ini kopyala
cd /path/to/Rikugan/rikugan/skills/builtins
cp -r vuln-audit my-vuln-audit
cd my-vuln-audit

# 2. skill.md'yi düzenle
nano skill.md

# 3. Yeni isim ve açıklama
---
name: My Vulnerability Audit
description: Özel güvenlik açığı taraması
tags: [security, vuln-audit, custom]
mode: plan
---
Task: Bu özel vulnerability audit agent'i şunları yapar:
- Stack overflow ara
- Heap overflow ara  
- SQL injection taraması
- XSS taraması

## Approach
...
```

### 4. Skill'i Kaydet

Skill otomatik yüklenir, özel kayıt gerekmez.

## 3. A2A (Agent-to-Agent) Agent Ekleme

Rikugan dışındaki agent'ları Rikugan'a entegre edin.

### Konfigürasyon Dosyası:

```json
// ~/.idapro/rikugan/config.json
{
  "a2a_agents": [
    {
      "name": "Ghidra Agent",
      "type": "external",
      "endpoint": "http://localhost:8080/agent",
      "api_key": "ghidra-api-key",
      "capabilities": ["decompile", "analyze", "disassemble"]
    },
    {
      "name": "Binary Ninja Cloud Agent",
      "type": "external",
      "endpoint": "https://api.binary.ninja.com/v1/agent",
      "api_key": "bn-api-key",
      "capabilities": ["lift", "analyze", "decompile"]
    }
  ]
}
```

### Kullanım:

```
// Rikugan panelinde
/ask Ghidra Agent: Decompile this function at 0x401000

// Otomatik yönlendirme
Rikugan external agent'a görevi yönlendirir
```

## 4. Custom Agent Handler Yazma (İleri Seviye)

Python kodu ile özel agent handler yazabilirsiniz.

### Agent Handler Örneği:

```python
# /path/to/Rikugan/rikugan/agents/custom_agent.py

from typing import Any, Dict
from ..agent.base import AgentHandler

class CustomAnalyzerAgent(AgentHandler):
    """Özel analiz agent handler."""
    
    def __init__(self):
        super().__init__()
        self.name = "Custom Analyzer"
        self.version = "1.0.0"
    
    def can_handle(self, task: str) -> bool:
        """Bu agent görevi handle edebilir mi?"""
        keywords = ["analyze", "scan", "examine"]
        return any(keyword in task.lower() for keyword in keywords)
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Görevi gerçekleştir."""
        
        # 1. Görevi analiz et
        analysis_result = self._analyze_task(task)
        
        # 2. IDA API'sini kullan
        results = []
        for address in analysis_result["addresses"]:
            result = self._analyze_address(address)
            results.append(result)
        
        # 3. Sonuçları döndür
        return {
            "agent": self.name,
            "task": task,
            "results": results,
            "status": "completed"
        }
    
    def _analyze_task(self, task: str) -> Dict[str, Any]:
        """Görevi analiz et."""
        # Görevden adres çıkar
        import re
        addresses = re.findall(r'0x[0-9a-fA-F]+', task)
        return {"addresses": addresses}
    
    def _analyze_address(self, address: int) -> Dict[str, Any]:
        """Adresi analiz et."""
        # IDA API kullan
        try:
            import idaapi
            func_name = idaapi.get_func_name(address)
            return {
                "address": address,
                "function": func_name,
                "analysis": "manual review needed"
            }
        except:
            return {
                "address": address,
                "error": "Failed to analyze"
            }
```

### Agent'i Kaydetme:

```python
# /path/to/Rikugan/rikugan/agents/__init__.py

from .custom_agent import CustomAnalyzerAgent

# Agent'i kaydet
AGENT_REGISTRY.register(CustomAnalyzerAgent)
```

## 5. Subagent Tanımlama (Exploration Modu İçin)

Exploration modunda kullanılan subagent'lar tanımlayabilirsiniz.

```python
# /path/to/Rikugan/rikugan/agents/subagents.py

from typing import Any, Dict

class FunctionAnalyzerSubagent:
    """Fonksiyon analiz subagent'ı."""
    
    def analyze_functions(self, addresses: list[int]) -> Dict[str, Any]:
        """Fonksiyonları analiz et."""
        results = {}
        
        for addr in addresses:
            try:
                # IDA API kullanarak analiz
                import idaapi
                func = idaapi.get_func(addr)
                results[addr] = {
                    "name": func.get_name(),
                    "size": func.get_size(),
                    "bounds": func.get_bounds()
                }
            except:
                results[addr] = {"error": "Failed to analyze"}
        
        return results
```

## 6. En Pratik: Hızlı Agent Oluşturma

### Şablon Skill Dosyası:

```markdown
---
name: Hızlı Analiz Agent
description: Otomatik ve hızlı binary analizi
tags: [fast, analysis, automated]
mode: auto
---
Task: Bu agent binary'i hızlı bir şekilde analiz eder.

## Auto-Analysis Workflow
1. `get_binary_info` → genel bilgi al
2. `list_imports` → import'ları tara
3. `list_exports` → export'ları tara
4. `search_functions` → kritik fonksiyonları bul
5. Auto-report oluştur

## Speed Optimization
- Paralel analiz yap
- Sadece kritik bölgelere odaklan
- Derinlemeyi takip etme

## Quick Report
- Özet analiz sonucu
- Risk skorları
- Önerilen sonraki adımlar
```

## 7. Agent Test Etme

### Test Komutu:

```bash
# Agent'ı test et
cd /path/to/Rikugan
python -m pytest tests/agent/test_agent.py -v

# Belirli skill'i test et
python -m pytest tests/tools/test_skills.py::test_my_custom_agent -v
```

### IDA Pro İçinde Test:

```
// Rikugan panelinde
/test-agent my-custom-agent "Analyze 0x401000"
```

## 8. Agent Yönetimi

### Aktif Agent'ları Görüntüle:

```
// Rikugan panelinde
/agents list

// Çıktı:
Active Agents: 3
- Main Orchestrator
- Function Analyzer (0x401000)
- String Searcher
```

### Agent'ları Kontrol Etme:

```
/agents pause          // Tüm agent'ları durdur
/agents resume         // Agent'ları devam ettir
/agents stop           // Tüm agent'ları durdur
```

## 9. Agent Konfigürasyonu

### Agent Davranışını Ayarlama:

```json
// ~/.idapro/rikugan/config.json
{
  "exploration_turn_limit": 100,    // Kaç tur sonrası durdurulacak
  "max_concurrent_agents": 5,      // Maksimum paralel agent sayısı
  "agent_timeout": 300,          // Agent zaman aşımı (saniye)
  "subagent_auto_cleanup": true  // Tamamlanan agent'ları otomatik temizle
}
```

## 10. Örnek: Kriptografik Analiz Agent'i

### Kripto Analiz Skill'i:

```markdown
---
name: Crypto Analyst
description: Kriptografik primitive ve algoritma analizi
tags: [crypto, encryption, analysis]
mode: plan
---
Task: Bu agent binary'deki kriptografik kullanımlarını analiz eder.

## Crypto Patterns
- Block cipher kullanımı (AES, DES)
- Stream cipher kullanımı (RC4, ChaCha20)
- Hash function kullanımı (SHA-1, SHA-256, MD5)
- Public key kriptografi (RSA, ECC)
- Random number generation

## Detection Methods
1. API tespiti: CryptEncrypt, CryptDecrypt, etc.
2. Sabit anahtar tespiti
3. Mode ve padding tespiti
4. Key length analizi

## Analysis Workflow
1. `search_functions` → crypto fonksiyonlarını bul
2. `decompile_function` → her fonksiyonu analiz et
3. Constant taraması → anahtar ve IV ara
4. Cross-reference → kripto kullanım alanlarını bul
```

### Kullanım:

```
// IDA Pro'da
/crypto Analyze encryption usage in this binary

// Otomatik
/crypto Find all AES-256 implementations
```

## Özet: Hangi Yöntem Ne Zaman Kullanılmalı?

| Yöntem | Zorluk | Esneklik | Kullanım Senaryosu |
|--------|--------|----------|------------------|
| **Skill Oluşturma** | Kolay | Yüksek | Özel analiz ihtiyaçları |
| **Skill Kopyalama** | Çok Kolay | Orta | Mevcut agent'i özelleştirme |
| **A2A Agent** | Orta | Düşük | Dış araç entegrasyonu |
| **Custom Handler** | Zor | Çok Yüksek | Tam kontrol, ileri seviye |

**Başlangıç için öneri:** İlk olarak mevcut bir skill'i kopyalayı değiştirin, sonra kendi skill'inizi oluşturun.

**Dökümantasyon:**
- Skill yazma: `/path/to/Rikugan/rikugan/skills/builtins/` dizinindeki skill.md dosyalarına bakın
- Agent API: `/path/to/Rikugan/rikugan/agent/` dizinindeki modüllere inceleyin
- Test örnekleri: `/path/to/Rikugan/tests/agent/` dizinindeki test dosyalarına bakın
