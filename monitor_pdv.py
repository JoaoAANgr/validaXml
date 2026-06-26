import io
import json
import os
import shutil
import smtplib
import subprocess
import sys
import logging
import threading
import time
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PASTA_ERRO        = os.getenv("PASTA_ERRO",        "./xml_erro")
PASTA_PROCESSADO  = os.getenv("PASTA_PROCESSADO",  "./xml_processado")
N8N_WEBHOOK_URL   = os.getenv("N8N_WEBHOOK_URL",   "")
EMAIL_REMETENTE   = os.getenv("EMAIL_REMETENTE",   "")
SENHA_APP         = os.getenv("SENHA_APP",         "")
EMAIL_DESTINO     = os.getenv("EMAIL_DESTINO",     "")
VALIDADOR_CMD     = os.getenv("VALIDADOR_CMD",     "python")
VALIDADOR_SCRIPT  = os.getenv("VALIDADOR_SCRIPT",  "validaXML.py")
VALIDADOR_TIMEOUT = int(os.getenv("VALIDADOR_TIMEOUT", "60"))
EMAIL_RETRY_MAX   = int(os.getenv("EMAIL_RETRY_MAX",   "3"))

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_file_handler = logging.FileHandler("monitor_pdv.log", encoding="utf-8")
_file_handler.setFormatter(_fmt)
_console_handler = logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace"))
_console_handler.setFormatter(_fmt)
logging.basicConfig(level=logging.INFO, handlers=[_file_handler, _console_handler])
log = logging.getLogger(__name__)

os.makedirs(PASTA_ERRO, exist_ok=True)
os.makedirs(PASTA_PROCESSADO, exist_ok=True)


def aguardar_arquivo_estavel(caminho: str, intervalo: float = 0.5, tentativas: int = 10) -> bool:
    tamanho_anterior = -1
    for _ in range(tentativas):
        try:
            tamanho_atual = os.path.getsize(caminho)
        except OSError:
            time.sleep(intervalo)
            continue
        if tamanho_atual == tamanho_anterior and tamanho_atual > 0:
            return True
        tamanho_anterior = tamanho_atual
        time.sleep(intervalo)
    return False


def _carregar_relatorio(caminho_json: str) -> dict:
    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def disparar_alerta(caminho_json: str, nome_xml: str) -> bool:
    if N8N_WEBHOOK_URL:
        if _chamar_webhook(caminho_json, nome_xml):
            return True
        log.warning("Webhook falhou — tentando e-mail direto...")
    return _enviar_email_direto(caminho_json, nome_xml)


def _chamar_webhook(caminho_json: str, nome_xml: str) -> bool:
    relatorio = _carregar_relatorio(caminho_json)
    payload = {
        "arquivo":   nome_xml,
        "timestamp": datetime.now().isoformat(),
        "erros":     relatorio.get("results", [{}])[0].get("errors", []),
        "relatorio": relatorio,
    }
    for tentativa in range(1, EMAIL_RETRY_MAX + 1):
        try:
            resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
            resp.raise_for_status()
            log.info("Webhook n8n acionado (HTTP %s).", resp.status_code)
            return True
        except requests.RequestException as e:
            log.warning("Tentativa %d/%d do webhook falhou: %s", tentativa, EMAIL_RETRY_MAX, e)
            if tentativa < EMAIL_RETRY_MAX:
                time.sleep(2 ** tentativa)
    log.error("Webhook n8n indisponivel para: %s", nome_xml)
    return False


def _enviar_email_direto(caminho_json: str, nome_xml: str) -> bool:
    if not all([EMAIL_REMETENTE, SENHA_APP, EMAIL_DESTINO]):
        log.warning("Nem webhook nem credenciais de e-mail configurados — alerta nao enviado.")
        return False

    msg = EmailMessage()
    msg["Subject"] = f"ALERTA PDV: Erro detectado no arquivo {nome_xml}"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINO
    msg.set_content(
        f"Ola, equipe de Suporte!\n\n"
        f"O monitor de PDV detectou uma falha em um XML.\n"
        f"Arquivo com falha: {nome_xml}\n\n"
        f"O relatorio com os detalhes do erro (JSON) segue em anexo."
    )
    if os.path.exists(caminho_json):
        with open(caminho_json, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="json",
                               filename="relatorio_erro.json")

    for tentativa in range(1, EMAIL_RETRY_MAX + 1):
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_REMETENTE, SENHA_APP)
                smtp.send_message(msg)
            log.info("E-mail enviado com sucesso.")
            return True
        except smtplib.SMTPAuthenticationError as e:
            log.error("Credenciais invalidas — verifique SENHA_APP no .env: %s", e)
            return False
        except Exception as e:
            log.warning("Tentativa %d/%d de e-mail falhou: %s", tentativa, EMAIL_RETRY_MAX, e)
            if tentativa < EMAIL_RETRY_MAX:
                time.sleep(2 ** tentativa)

    log.error("Todas as tentativas de e-mail falharam para: %s", nome_xml)
    return False


class MonitorPDV(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self._em_processamento: set = set()
        self._lock = threading.Lock()

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".xml"):
            return

        caminho_xml = str(Path(event.src_path).resolve())
        nome_arquivo = os.path.basename(caminho_xml)

        with self._lock:
            if caminho_xml in self._em_processamento:
                return
            self._em_processamento.add(caminho_xml)
        log.info("Novo XML detectado: %s", nome_arquivo)

        if not aguardar_arquivo_estavel(caminho_xml):
            log.warning("Arquivo instavel ou ilegivel, pulando: %s", nome_arquivo)
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        nome_base = Path(nome_arquivo).stem
        caminho_json = f"relatorio_{nome_base}_{timestamp}.json"

        log.info("Executando validacao...")
        try:
            resultado = subprocess.run(
                [VALIDADOR_CMD, VALIDADOR_SCRIPT, "-f", caminho_xml, "-o", caminho_json, "--quiet"],
                timeout=VALIDADOR_TIMEOUT,
            )
            xml_invalido = resultado.returncode != 0
        except subprocess.TimeoutExpired:
            log.error("Validacao expirou apos %ds: %s", VALIDADOR_TIMEOUT, nome_arquivo)
            xml_invalido = True
        except Exception as e:
            log.error("Erro ao executar validador: %s", e)
            xml_invalido = True

        if xml_invalido:
            log.warning("XML invalido — enviando alerta: %s", nome_arquivo)
            disparar_alerta(caminho_json, nome_arquivo)
        else:
            log.info("XML valido: %s", nome_arquivo)

        destino = os.path.join(PASTA_PROCESSADO, nome_arquivo)
        try:
            shutil.move(caminho_xml, destino)
            log.info("Movido para: %s", destino)
        except Exception as e:
            log.error("Falha ao mover arquivo: %s", e)
        finally:
            self._em_processamento.discard(caminho_xml)


def iniciar():
    event_handler = MonitorPDV()
    observer = Observer()
    observer.schedule(event_handler, PASTA_ERRO, recursive=False)
    observer.start()
    log.info("Monitor iniciado. Aguardando arquivos em: %s", PASTA_ERRO)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    iniciar()
