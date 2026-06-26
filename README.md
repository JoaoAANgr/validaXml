# Monitor PDV — XML Validator Pro

Validador automático de arquivos XML com monitor de pasta, alertas via n8n e log de erros em CSV.  
Pensado para PDV: XML inválido cai na pasta → sistema detecta, valida, notifica e arquiva. Tudo automático.

---

## Como funciona

```
Windows inicia
    → n8n sobe (http://localhost:5678)
    → monitor_pdv.py começa a escutar xml_erro/

XML inválido cai em xml_erro/
    → monitor detecta e valida
    → chama webhook do n8n
    → n8n: formata os dados
           ├── envia e-mail HTML com detalhes do erro
           └── grava linha no erros_pdv.csv
    → XML movido para xml_processado/
```

---

## Instalação (única vez)

**Requisitos:** Python 3.10+, Node.js 18+

```bash
# Dependências Python
pip install rich lxml xmlschema watchdog python-dotenv requests

# n8n
npm install -g n8n
```

---

## Configuração

Edite o `.env` na raiz:

```env
PASTA_ERRO=./xml_erro
PASTA_PROCESSADO=./xml_processado

# n8n (modo principal)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/xml-alerta

# E-mail direto (fallback se n8n estiver offline)
EMAIL_REMETENTE=seu@gmail.com
SENHA_APP=xxxx xxxx xxxx xxxx
EMAIL_DESTINO=destino@gmail.com

VALIDADOR_TIMEOUT=60
EMAIL_RETRY_MAX=3
```

> Gere a `SENHA_APP` em: Conta Google → Segurança → Senhas de app

---

## Iniciar automaticamente com o Windows

Execute **como Administrador** (uma vez só):

```
instalar_autostart.bat
```

Pronto. No próximo login o n8n e o monitor sobem sozinhos em background, sem janela.

Para remover o autostart:
```
desinstalar_autostart.bat
```

---

## Iniciar manualmente (sem autostart)

| Script | O que faz |
|---|---|
| `start_n8n.bat` | Abre o n8n com janela de console |
| `start_monitor.bat` | Abre o monitor com janela de console |

---

## Workflow n8n

Acesse `http://localhost:5678` e faça login com as credenciais definidas na instalação do n8n.

O workflow **Monitor PDV - Alerta XML** tem 4 nós:

```
Webhook XML Erro
    └── Formatar Dados (Code)
            ├── Enviar Email  → e-mail HTML estilizado com lista de erros
            └── Gravar Log CSV → appenda linha em erros_pdv.csv
```

Para adicionar novos canais (Slack, Teams, WhatsApp…), arraste um nó novo após **Formatar Dados** — os dados já estão estruturados.

---

## Validador CLI (uso avulso)

```bash
# Sintaxe básica
python validaXML.py -f arquivo.xml

# Contra XSD
python validaXML.py -f arquivo.xml --xsd schema.xsd

# XPath
python validaXML.py -f arquivo.xml --xpath "//NFe" "//ide/cNF"

# Lote com relatório
python validaXML.py --batch ./xmls/ --xsd schema.xsd -o relatorio.json

# Silencioso (exit code: 0=válido, 1=inválido)
python validaXML.py -f arquivo.xml --quiet
```

---

## Interface gráfica

```bash
python validador_gui.py
```

---

## Estrutura do projeto

```
validaxml/
├── validaXML.py              # Validador CLI
├── validador_gui.py          # Interface gráfica (Tkinter)
├── monitor_pdv.py            # Monitor de pasta + webhook n8n
├── gerar_relatorio_bi.py     # Gerador de relatório BI em CSV
├── rotina_dados.bat          # Automação de coleta de dados
│
├── instalar_autostart.bat    # Registra autostart no Windows (rodar como Admin)
├── desinstalar_autostart.bat # Remove o autostart
├── iniciar_silencioso.vbs    # Inicializador sem janela (usado pelo autostart)
├── start_n8n.bat             # Inicia n8n manualmente
├── start_monitor.bat         # Inicia monitor manualmente
│
├── .env                      # Configurações locais (não versionado)
├── exemplos/                 # XMLs e XSD de exemplo
└── xml_processado/           # XMLs já processados (runtime)
```

---

## Saídas geradas em runtime

| Arquivo | Descrição |
|---|---|
| `erros_pdv.csv` | Log de todos os XMLs inválidos detectados |
| `relatorio_<nome>_<timestamp>.json` | Relatório detalhado por XML |
| `monitor_pdv.log` | Log de execução do monitor |
| `xml_processado/` | Arquivos processados |

---

## Exemplos incluídos

```
exemplos/
├── venda_ok.xml     # XML de venda válido — sem alerta
├── venda_erro.xml   # XML com erros — dispara alerta completo
└── schema_pdv.xsd  # Schema XSD de validação de PDV
```

Copie qualquer XML para `xml_erro/` para simular um evento.

---

## Exit codes (CLI)

| Código | Significado |
|---|---|
| `0` | XML válido |
| `1` | XML inválido |
| `2` | Arquivo ou parâmetro não encontrado |
