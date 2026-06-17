# 🔍 XML Validator Pro

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()

Ferramenta profissional de validação de arquivos XML com interface CLI moderna e GUI opcional. Suporte completo a validação bem-formada, XSD schemas, expressões XPath e processamento em lote.

---

## ✨ Características

- ✅ **Validação Bem-Formada** - Verifica sintaxe XML básica
- 🎯 **Validação XSD** - Valida contra XML Schema Definition
- 🔍 **Validação XPath** - Executa e verifica expressões XPath
- 📦 **Processamento em Lote** - Valida múltiplos arquivos simultaneamente
- 🎨 **Interface Visual** - Terminal rich com cores e formatação profissional
- 🖥️ **GUI Moderna** - Interface Tkinter com design azul profissional
- 📊 **Relatórios JSON** - Exporta resultados estruturados
- 🪟 **Compatível com Windows** - Suporte completo a codificação UTF-8
- ⚡ **CLI Silenciosa** - Ideal para pipelines e automações

---

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.10+
- pip

### Setup
```bash
# Clonar repositório
git clone https://github.com/seu-usuario/xml-validator-pro.git
cd xml-validator-pro

# Instalar dependências
pip install -r requirements.txt
```

---

## 📖 Uso

### 1️⃣ CLI - Validação Simples
```bash
python validaXML.py -f arquivo.xml
```

### 2️⃣ CLI - Validação com XSD
```bash
python validaXML.py -f arquivo.xml --xsd schema.xsd
```

### 3️⃣ CLI - Validação com XPath
```bash
python validaXML.py -f arquivo.xml --xpath "//elemento" "//outro[@atributo]"
```

### 4️⃣ CLI - Processamento em Lote
```bash
python validaXML.py --batch ./xmls/ --xsd schema.xsd -o relatorio.json
```

### 5️⃣ CLI - Modo Silencioso (Exit Code)
```bash
python validaXML.py -f arquivo.xml --quiet
# Exit code: 0 = válido, 1 = inválido
```

### 6️⃣ GUI - Interface Visual
```bash
python validador_gui.py
```

---

## 📋 Exemplos

### Validar arquivo bem-formado
```bash
$ python validaXML.py -f dados.xml
```

**Output:**
```
✅ dados.xml  VÁLIDO  [8.23ms]

Root Element        dados
Namespace           http://example.com
Children Count      5
Encoding            UTF-8
Xml Version         1.0
Tamanho             2.45 KB
```

### Validar contra schema
```bash
$ python validaXML.py -f nfe.xml --xsd nfe-schema.xsd
```

### Validar com XPath
```bash
$ python validaXML.py -f dados.xml --xpath "//produto[@id]" "//preco[.>100]"
```

### Lote com relatório
```bash
$ python validaXML.py --batch ./xmls/ -o relatorio.json

📂 Processando 10 arquivo(s)...

═══════════ RELATÓRIO DE LOTE ═══════════

Total: 10 | Válidos: 9 | Inválidos: 1
Taxa de sucesso: 90.0%

[SALVO] Relatório em: relatorio.json
```

---

## 🎨 Estrutura do Projeto

```
xml-validator-pro/
├── validaXML.py                          # Script principal CLI
├── validador_gui.py                      # Interface Tkinter moderna
├── requirements.txt                      # Dependências Python
├── package.json                          # Metadados Node.js (opcional)
├── XML_Validator_Pro_Casos_Uso.docx     # Documentação completa
├── README.md                             # Este arquivo
└── LICENSE                               # MIT License
```

---

## 🔧 Dependências

### Python
- **rich** (15.0.0+) - Terminal formatting e UI avançada
- **lxml** (6.1.0+) - Parser XML com suporte a XSD
- **xmlschema** (4.3.1+) - Validação de XML Schema

### Node.js (Opcional)
- **docx** - Para gerar documentação

---

## 📦 Requirements.txt

```txt
rich==15.0.0
lxml==6.1.0
xmlschema==4.3.1
```

---

## 🖼️ Interface GUI

A aplicação inclui uma interface gráfica moderna com:
- 🎨 Design em azul profissional
- 📁 Seleção de arquivos com diálogo
- ⚙️ Múltiplos modos de validação
- 📊 Visualizador de relatórios
- 🔄 Processamento em lote visual

**Iniciar GUI:**
```bash
python validador_gui.py
```

---

## 📊 Relatório JSON

Exemplo de saída JSON:
```json
{
  "generated_at": "2026-06-17T15:18:03.162987",
  "summary": {
    "total": 3,
    "valid": 2,
    "invalid": 1
  },
  "results": [
    {
      "file": "arquivo1.xml",
      "valid": true,
      "errors": [],
      "warnings": [],
      "info": {
        "root_element": "root",
        "namespace": "http://example.com",
        "encoding": "UTF-8"
      },
      "duration_ms": 8.23,
      "file_size_kb": 2.45
    }
  ]
}
```

---

## 🛠️ Modos de Operação

| Modo | Descrição | Comando |
|------|-----------|---------|
| **Interativo** | Menu visual com prompts | `python validaXML.py` |
| **CLI Simples** | Parâmetros diretos | `python validaXML.py -f arquivo.xml` |
| **CLI Lote** | Múltiplos arquivos | `python validaXML.py --batch ./xmls/` |
| **Silencioso** | Apenas exit code | `python validaXML.py --quiet` |
| **GUI** | Interface gráfica | `python validador_gui.py` |

---

## ✅ Exit Codes

- `0` - Validação bem-sucedida (arquivo válido)
- `1` - Validação falhou (arquivo inválido)
- `2` - Erro de arquivo ou parâmetro

---

## 🐛 Solução de Problemas

### UnicodeEncodeError no Windows
A aplicação foi otimizada para Windows com suporte completo a UTF-8. Se encontrar erro de codificação:

```bash
# Execute com UTF-8 explícito
python -c "import os; os.environ['PYTHONIOENCODING']='utf-8'" && python validaXML.py -f arquivo.xml
```

### Módulo 'rich' não encontrado
```bash
pip install --upgrade rich
```

### Erro de XSD/XPath
Certifique-se de que:
- O arquivo XSD/XPath é válido
- Os caminhos estão corretos
- Use aspas para expressões XPath complexas

---

## 📚 Documentação Completa

Para documentação detalhada com casos de uso, cenários e exemplos avançados, consulte:
```
XML_Validator_Pro_Casos_Uso.docx
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para reportar bugs ou sugerir features:

1. Abra uma [Issue](https://github.com/seu-usuario/xml-validator-pro/issues)
2. Fork o projeto
3. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
4. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
5. Push para a branch (`git push origin feature/MinhaFeature`)
6. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👤 Autor

Desenvolvido com ❤️ como ferramenta profissional de validação XML.

---

## 🔗 Links Úteis

- [Especificação XML](https://www.w3.org/XML/)
- [XML Schema (XSD)](https://www.w3.org/XML/Schema)
- [XPath Tutorial](https://www.w3schools.com/xml/xpath_intro.asp)
- [Rich Library](https://rich.readthedocs.io/)
- [lxml Documentation](https://lxml.de/)

---

## 📈 Roadmap

- [ ] Integração com CI/CD (GitHub Actions)
- [ ] Suporte a RELAXNG e DTD
- [ ] API REST para validação
- [ ] Dashboard web
- [ ] Plugins customizados
- [ ] Validação de performance

---

**Versão**: 1.0  
**Status**: Production Ready ✅  
**Última atualização**: Junho 2026
