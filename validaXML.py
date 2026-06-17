#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════╗
║        XML Validator Pro v1.0            ║
║   Validação automática de arquivos XML   ║
╚══════════════════════════════════════════╝
"""

import sys
import os
import argparse
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# Forçar UTF-8 no Windows
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    from rich.prompt import Prompt, Confirm
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    from rich.align import Align
    from rich.rule import Rule
    from rich.columns import Columns
    from rich.syntax import Syntax
    from rich import box
    from rich.padding import Padding
    from rich.style import Style
    from rich.markup import escape
    import rich
except ImportError:
    print("Erro: biblioteca 'rich' não encontrada. Execute: pip install rich")
    sys.exit(1)

try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False
    import xml.etree.ElementTree as ET

try:
    import xmlschema
    XMLSCHEMA_AVAILABLE = True
except ImportError:
    XMLSCHEMA_AVAILABLE = False

console = Console()

# ─── Paleta de Cores ─────────────────────────────────────────────────────────
THEME = {
    "primary":   "#00B4D8",
    "success":   "#06D6A0",
    "error":     "#EF233C",
    "warning":   "#FFD166",
    "info":      "#8338EC",
    "muted":     "#6C757D",
    "bg_panel":  "#1A1A2E",
    "accent":    "#E94560",
}


# ─── Banner ───────────────────────────────────────────────────────────────────
def print_banner():
    banner = """
 ██╗  ██╗███╗   ███╗██╗         ██╗   ██╗ █████╗ ██╗     ██╗██████╗  █████╗ ████████╗ ██████╗ ██████╗ 
 ╚██╗██╔╝████╗ ████║██║         ██║   ██║██╔══██╗██║     ██║██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
  ╚███╔╝ ██╔████╔██║██║         ██║   ██║███████║██║     ██║██║  ██║███████║   ██║   ██║   ██║██████╔╝
  ██╔██╗ ██║╚██╔╝██║██║         ╚██╗ ██╔╝██╔══██║██║     ██║██║  ██║██╔══██║   ██║   ██║   ██║██╔══██╗
 ██╔╝ ██╗██║ ╚═╝ ██║███████╗     ╚████╔╝ ██║  ██║███████╗██║██████╔╝██║  ██║   ██║   ╚██████╔╝██║  ██║
 ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝      ╚═══╝  ╚═╝  ╚═╝╚══════╝╚═╝╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝"""

    console.print()
    console.print(Text(banner, style=f"bold {THEME['primary']}"))

    subtitle = Align.center(
        Text("◆  Validação Automática de Arquivos XML  ◆", style=f"bold {THEME['accent']}"),
    )
    version = Align.center(
        Text("v1.0  │  Suporte: bem-formado · XSD · XPath · Lote", style=f"dim {THEME['muted']}"),
    )
    console.print(subtitle)
    console.print(version)
    console.print()


# ─── Resultado de Validação ───────────────────────────────────────────────────
class ValidationResult:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.filename = Path(file_path).name
        self.is_valid = False
        self.errors = []
        self.warnings = []
        self.info = {}
        self.duration_ms = 0
        self.file_size_kb = 0
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "file": self.file_path,
            "valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "duration_ms": self.duration_ms,
            "file_size_kb": self.file_size_kb,
            "timestamp": self.timestamp,
        }


# ─── Validações ───────────────────────────────────────────────────────────────
def validate_wellformed(xml_path: str) -> ValidationResult:
    """Valida se o XML é bem-formado (sintaxe básica)."""
    result = ValidationResult(xml_path)
    start = time.time()

    try:
        size = os.path.getsize(xml_path)
        result.file_size_kb = round(size / 1024, 2)
    except Exception:
        pass

    try:
        if LXML_AVAILABLE:
            parser = etree.XMLParser(recover=False)
            with open(xml_path, "rb") as f:
                tree = etree.parse(f, parser)
            root = tree.getroot()
            result.info["root_element"] = root.tag
            result.info["namespace"] = root.nsmap.get(None, "Nenhum")
            result.info["children_count"] = len(list(root))
            result.info["encoding"] = tree.docinfo.encoding or "UTF-8"
            result.info["xml_version"] = tree.docinfo.xml_version or "1.0"
        else:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            result.info["root_element"] = root.tag
            result.info["children_count"] = len(list(root))

        result.is_valid = True
    except Exception as e:
        result.errors.append(f"Erro de sintaxe XML: {str(e)}")
        result.is_valid = False

    result.duration_ms = round((time.time() - start) * 1000, 2)
    return result


def validate_xsd(xml_path: str, xsd_path: str) -> ValidationResult:
    """Valida XML contra um schema XSD."""
    result = ValidationResult(xml_path)
    start = time.time()

    # primeiro verifica se é bem-formado
    wf = validate_wellformed(xml_path)
    result.info = wf.info
    result.file_size_kb = wf.file_size_kb

    if not wf.is_valid:
        result.errors = wf.errors
        result.duration_ms = round((time.time() - start) * 1000, 2)
        return result

    if not XMLSCHEMA_AVAILABLE and not LXML_AVAILABLE:
        result.errors.append("Nenhuma biblioteca de validação XSD disponível. Instale: pip install xmlschema ou lxml")
        result.duration_ms = round((time.time() - start) * 1000, 2)
        return result

    try:
        if LXML_AVAILABLE:
            with open(xsd_path, "rb") as f:
                xsd_doc = etree.parse(f)
            xsd = etree.XMLSchema(xsd_doc)
            with open(xml_path, "rb") as f:
                xml_doc = etree.parse(f)

            is_valid = xsd.validate(xml_doc)
            result.is_valid = is_valid

            if not is_valid:
                for err in xsd.error_log:
                    result.errors.append(f"Linha {err.line}: {err.message}")

        elif XMLSCHEMA_AVAILABLE:
            schema = xmlschema.XMLSchema(xsd_path)
            is_valid, errors = schema.is_valid(xml_path), []
            try:
                schema.validate(xml_path)
                result.is_valid = True
            except xmlschema.XMLSchemaValidationError as e:
                result.is_valid = False
                result.errors.append(str(e))

    except Exception as e:
        result.errors.append(f"Erro ao validar XSD: {str(e)}")
        result.is_valid = False

    result.duration_ms = round((time.time() - start) * 1000, 2)
    return result


def validate_xpath(xml_path: str, xpath_expressions: list) -> ValidationResult:
    """Valida expressões XPath dentro do XML."""
    result = ValidationResult(xml_path)
    start = time.time()

    wf = validate_wellformed(xml_path)
    result.info = wf.info
    result.file_size_kb = wf.file_size_kb

    if not wf.is_valid:
        result.errors = wf.errors
        result.duration_ms = round((time.time() - start) * 1000, 2)
        return result

    if not LXML_AVAILABLE:
        result.errors.append("lxml necessário para validação XPath. Instale: pip install lxml")
        result.duration_ms = round((time.time() - start) * 1000, 2)
        return result

    try:
        tree = etree.parse(xml_path)
        xpath_results = {}
        all_ok = True

        for expr in xpath_expressions:
            try:
                nodes = tree.xpath(expr)
                count = len(nodes) if isinstance(nodes, list) else (1 if nodes else 0)
                xpath_results[expr] = {"found": count, "ok": count > 0}
                if count == 0:
                    result.warnings.append(f"XPath não encontrou resultados: {expr}")
                    all_ok = False
            except etree.XPathError as e:
                result.errors.append(f"Expressão XPath inválida '{expr}': {str(e)}")
                all_ok = False

        result.info["xpath_results"] = xpath_results
        result.is_valid = len(result.errors) == 0

    except Exception as e:
        result.errors.append(f"Erro ao executar XPath: {str(e)}")
        result.is_valid = False

    result.duration_ms = round((time.time() - start) * 1000, 2)
    return result


def validate_batch(xml_paths: list, xsd_path: Optional[str] = None, xpath_expressions: Optional[list] = None) -> list:
    """Valida um lote de arquivos XML."""
    results = []
    for path in xml_paths:
        if xsd_path:
            r = validate_xsd(path, xsd_path)
        elif xpath_expressions:
            r = validate_xpath(path, xpath_expressions)
        else:
            r = validate_wellformed(path)
        results.append(r)
    return results


# ─── Renderização ─────────────────────────────────────────────────────────────
def render_result(result: ValidationResult, show_info: bool = True):
    """Exibe o resultado de uma validação de forma visual."""

    # Status badge
    if result.is_valid:
        status_icon = "✅"
        status_text = Text("VÁLIDO", style=f"bold {THEME['success']}")
        panel_border = THEME["success"]
    else:
        status_icon = "❌"
        status_text = Text("INVÁLIDO", style=f"bold {THEME['error']}")
        panel_border = THEME["error"]

    # Cabeçalho do painel
    header = Text()
    header.append(f" {status_icon} ")
    header.append(result.filename, style=f"bold white")
    header.append("  ")
    header.append_text(status_text)
    header.append(f"  [{result.duration_ms}ms]", style=f"dim {THEME['muted']}")

    content_parts = []

    # Info técnica
    if show_info and result.info:
        info_table = Table(
            box=box.SIMPLE,
            show_header=False,
            padding=(0, 1),
        )
        info_table.add_column("Chave", style=f"dim {THEME['primary']}", width=22)
        info_table.add_column("Valor", style="white")

        for key, val in result.info.items():
            if key == "xpath_results":
                for xp, xr in val.items():
                    icon = "✔" if xr["ok"] else "✘"
                    color = THEME["success"] if xr["ok"] else THEME["warning"]
                    info_table.add_row(
                        f"XPath",
                        Text(f"[{icon}] {xp}  →  {xr['found']} nó(s)", style=color)
                    )
            else:
                display_key = key.replace("_", " ").title()
                info_table.add_row(display_key, str(val))

        info_table.add_row("Tamanho", f"{result.file_size_kb} KB")
        content_parts.append(info_table)

    # Erros
    if result.errors:
        console.print()
        err_table = Table(
            title=Text(f"  Erros encontrados ({len(result.errors)})", style=f"bold {THEME['error']}"),
            box=box.ROUNDED,
            border_style=THEME["error"],
            show_header=False,
            padding=(0, 1),
        )
        err_table.add_column("Descrição", style="white")
        for err in result.errors:
            err_table.add_row(Text(f"⚠  {err}", style=f"{THEME['error']}"))

    # Avisos
    if result.warnings:
        warn_table = Table(
            title=Text(f"  Avisos ({len(result.warnings)})", style=f"bold {THEME['warning']}"),
            box=box.ROUNDED,
            border_style=THEME["warning"],
            show_header=False,
            padding=(0, 1),
        )
        warn_table.add_column("Descrição", style="white")
        for w in result.warnings:
            warn_table.add_row(Text(f"⚡  {w}", style=f"{THEME['warning']}"))

    # Renderiza tudo dentro de um painel
    panel_content = Table.grid(padding=(0, 0))
    panel_content.add_column()

    if content_parts:
        for part in content_parts:
            panel_content.add_row(part)

    if result.errors:
        panel_content.add_row(err_table)

    if result.warnings:
        panel_content.add_row(warn_table)

    try:
        console.print(Panel(
            panel_content,
            title=header,
            border_style=panel_border,
            padding=(1, 2),
        ))
    except UnicodeEncodeError:
        # Fallback para modo simples em caso de erro de codificação (Windows)
        status_txt = "VALIDO" if result.is_valid else "INVALIDO"
        console.print(f"\n{result.filename} - {status_txt}")
        if result.info:
            for key, val in result.info.items():
                if key != "xpath_results":
                    console.print(f"  {key}: {val}")
        if result.errors:
            for err in result.errors:
                console.print(f"  ERRO: {err}")
        if result.warnings:
            for w in result.warnings:
                console.print(f"  AVISO: {w}")


def render_batch_summary(results: list):
    """Exibe resumo de validação em lote."""
    total = len(results)
    valid = sum(1 for r in results if r.is_valid)
    invalid = total - valid
    total_ms = sum(r.duration_ms for r in results)
    total_kb = sum(r.file_size_kb for r in results)

    try:
        console.print()
        console.print(Rule(Text("  RELATÓRIO DE LOTE  ", style=f"bold {THEME['primary']}"), style=THEME["primary"]))
        console.print()

        # Cards de resumo
        summary_table = Table(
            box=box.SIMPLE_HEAVY,
            show_header=False,
            padding=(1, 4),
            border_style=THEME["primary"],
        )
        summary_table.add_column("", justify="center", min_width=18)
        summary_table.add_column("", justify="center", min_width=18)
        summary_table.add_column("", justify="center", min_width=18)
        summary_table.add_column("", justify="center", min_width=18)

        summary_table.add_row(
            Text(f"{total}", style=f"bold {THEME['primary']} on default"),
            Text(f"{valid}", style=f"bold {THEME['success']} on default"),
            Text(f"{invalid}", style=f"bold {THEME['error']} on default"),
            Text(f"{round(total_ms)}ms", style=f"bold {THEME['warning']} on default"),
        )
        summary_table.add_row(
            Text("Total", style=f"dim {THEME['muted']}"),
            Text("Validos", style=f"dim {THEME['success']}"),
            Text("Invalidos", style=f"dim {THEME['error']}"),
            Text("Tempo Total", style=f"dim {THEME['muted']}"),
        )

        console.print(Align.center(summary_table))
        console.print()

        # Taxa de sucesso
        pct = (valid / total * 100) if total > 0 else 0
        bar_filled = int(pct / 5)  # 20 chars total
        bar_empty = 20 - bar_filled
        bar = Text()
        bar.append("  Taxa de sucesso  ", style=f"bold {THEME['muted']}")
        bar.append("=" * bar_filled, style=f"bold {THEME['success']}")
        bar.append("-" * bar_empty, style=f"dim {THEME['muted']}")
        bar.append(f"  {pct:.1f}%", style=f"bold {THEME['success'] if pct == 100 else THEME['warning']}")
        console.print(Align.center(bar))
        console.print()

        # Tabela de arquivos
        tbl = Table(
            title=Text("  Detalhamento por Arquivo", style=f"bold {THEME['primary']}"),
            box=box.ROUNDED,
            border_style=THEME["primary"],
            header_style=f"bold {THEME['primary']}",
            show_lines=False,
            padding=(0, 1),
        )
        tbl.add_column("#", style=f"dim {THEME['muted']}", width=4, justify="right")
        tbl.add_column("Arquivo", style="white", min_width=25)
        tbl.add_column("Status", justify="center", width=12)
        tbl.add_column("Erros", justify="center", width=8)
        tbl.add_column("Avisos", justify="center", width=8)
        tbl.add_column("Tamanho", justify="right", width=10)
        tbl.add_column("Tempo", justify="right", width=10)

        for i, r in enumerate(results, 1):
            if r.is_valid:
                status = Text("[OK] VALIDO", style=THEME["success"])
            else:
                status = Text("[!] INVALIDO", style=THEME["error"])

            err_cell = Text(str(len(r.errors)), style=THEME["error"] if r.errors else THEME["muted"])
            warn_cell = Text(str(len(r.warnings)), style=THEME["warning"] if r.warnings else THEME["muted"])

            tbl.add_row(
                str(i),
                r.filename,
                status,
                err_cell,
                warn_cell,
                f"{r.file_size_kb} KB",
                f"{r.duration_ms}ms",
            )

        console.print(tbl)
        console.print()
    
    except UnicodeEncodeError:
        # Fallback para modo simples
        console.print(f"\n=== RELATORIO DE LOTE ===")
        console.print(f"Total: {total} | Validos: {valid} | Invalidos: {invalid}")
        console.print(f"Taxa de sucesso: {pct:.1f}%")
        console.print("\nDetalhamento:")
        for i, r in enumerate(results, 1):
            status = "OK" if r.is_valid else "ERRO"
            console.print(f"{i}. {r.filename} - {status}")
        console.print()


def save_report(results: list, output_path: str):
    """Salva relatório em JSON."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "valid": sum(1 for r in results if r.is_valid),
            "invalid": sum(1 for r in results if not r.is_valid),
        },
        "results": [r.to_dict() for r in results],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    console.print(f"\n[bold {THEME['success']}][SALVO] Relatório em:[/] [underline white]{output_path}[/]")


# ─── Modo Interativo ──────────────────────────────────────────────────────────
def interactive_mode():
    """Menu interativo para uso sem linha de comando."""
    print_banner()

    console.print(Panel(
        Text.from_markup(
            f"[bold {THEME['primary']}]Bem-vindo ao XML Validator Pro![/]\n\n"
            f"[{THEME['muted']}]Selecione o modo de validação desejado.[/]"
        ),
        box=box.ROUNDED,
        border_style=THEME["primary"],
        padding=(1, 3),
    ))

    console.print()
    options_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    options_table.add_column("Opção", style=f"bold {THEME['accent']}", width=6)
    options_table.add_column("Modo", style=f"bold white", width=30)
    options_table.add_column("Descrição", style=f"dim {THEME['muted']}")

    options_table.add_row("[1]", "Validação Bem-Formado", "Verifica sintaxe XML básica")
    options_table.add_row("[2]", "Validação com XSD", "Valida contra um Schema XSD")
    options_table.add_row("[3]", "Validação com XPath", "Verifica expressões XPath")
    options_table.add_row("[4]", "Validação em Lote", "Valida múltiplos arquivos")
    options_table.add_row("[0]", "Sair", "Encerra o programa")

    console.print(options_table)
    console.print()

    while True:
        choice = Prompt.ask(
            f"[bold {THEME['primary']}]Escolha uma opção[/]",
            choices=["0", "1", "2", "3", "4"],
            default="1"
        )

        if choice == "0":
            console.print(f"\n[bold {THEME['accent']}]Até logo! 👋[/]\n")
            sys.exit(0)

        elif choice == "1":
            xml_path = Prompt.ask(f"\n[bold {THEME['primary']}]Caminho do arquivo XML[/]")
            if not os.path.exists(xml_path):
                console.print(f"[bold {THEME['error']}]❌ Arquivo não encontrado: {xml_path}[/]")
                continue

            console.print()
            with Progress(
                SpinnerColumn(style=THEME["primary"]),
                TextColumn(f"[{THEME['primary']}]Validando..."),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("", total=None)
                result = validate_wellformed(xml_path)
                time.sleep(0.3)  # visual feedback

            render_result(result)

            if Confirm.ask(f"\n[{THEME['muted']}]Salvar relatório JSON?[/]", default=False):
                out = Prompt.ask("Caminho do relatório", default="relatorio.json")
                save_report([result], out)

        elif choice == "2":
            xml_path = Prompt.ask(f"\n[bold {THEME['primary']}]Caminho do arquivo XML[/]")
            xsd_path = Prompt.ask(f"[bold {THEME['primary']}]Caminho do arquivo XSD[/]")

            for p, label in [(xml_path, "XML"), (xsd_path, "XSD")]:
                if not os.path.exists(p):
                    console.print(f"[bold {THEME['error']}]❌ Arquivo {label} não encontrado: {p}[/]")
                    break
            else:
                console.print()
                with Progress(
                    SpinnerColumn(style=THEME["primary"]),
                    TextColumn(f"[{THEME['primary']}]Validando contra XSD..."),
                    TimeElapsedColumn(),
                    console=console,
                ) as progress:
                    progress.add_task("", total=None)
                    result = validate_xsd(xml_path, xsd_path)
                    time.sleep(0.3)

                render_result(result)

                if Confirm.ask(f"\n[{THEME['muted']}]Salvar relatório JSON?[/]", default=False):
                    out = Prompt.ask("Caminho do relatório", default="relatorio.json")
                    save_report([result], out)

        elif choice == "3":
            xml_path = Prompt.ask(f"\n[bold {THEME['primary']}]Caminho do arquivo XML[/]")
            if not os.path.exists(xml_path):
                console.print(f"[bold {THEME['error']}]❌ Arquivo não encontrado: {xml_path}[/]")
                continue

            console.print(f"[{THEME['muted']}]Digite as expressões XPath (uma por linha, linha vazia para terminar):[/]")
            expressions = []
            while True:
                expr = Prompt.ask(f"[{THEME['info']}]XPath[/]", default="")
                if not expr:
                    break
                expressions.append(expr)

            if not expressions:
                console.print(f"[bold {THEME['warning']}]Nenhuma expressão fornecida.[/]")
                continue

            console.print()
            with Progress(
                SpinnerColumn(style=THEME["primary"]),
                TextColumn(f"[{THEME['primary']}]Executando XPath..."),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                progress.add_task("", total=None)
                result = validate_xpath(xml_path, expressions)
                time.sleep(0.3)

            render_result(result)

            if Confirm.ask(f"\n[{THEME['muted']}]Salvar relatório JSON?[/]", default=False):
                out = Prompt.ask("Caminho do relatório", default="relatorio.json")
                save_report([result], out)

        elif choice == "4":
            folder = Prompt.ask(f"\n[bold {THEME['primary']}]Pasta com arquivos XML[/]", default=".")
            if not os.path.isdir(folder):
                console.print(f"[bold {THEME['error']}]❌ Pasta não encontrada: {folder}[/]")
                continue

            xml_files = list(Path(folder).glob("**/*.xml"))
            if not xml_files:
                console.print(f"[bold {THEME['warning']}]⚠ Nenhum arquivo XML encontrado em: {folder}[/]")
                continue

            console.print(f"\n[{THEME['success']}]✔ Encontrados {len(xml_files)} arquivo(s) XML[/]")

            use_xsd = Confirm.ask(f"[{THEME['muted']}]Usar schema XSD?[/]", default=False)
            xsd_path = None
            if use_xsd:
                xsd_path = Prompt.ask(f"[bold {THEME['primary']}]Caminho do XSD[/]")
                if not os.path.exists(xsd_path):
                    console.print(f"[bold {THEME['error']}]❌ XSD não encontrado[/]")
                    continue

            save_json = Confirm.ask(f"[{THEME['muted']}]Salvar relatório JSON ao final?[/]", default=True)
            output_path = None
            if save_json:
                output_path = Prompt.ask("Caminho do relatório", default="relatorio_lote.json")

            console.print()
            results = []
            with Progress(
                SpinnerColumn(style=THEME["primary"]),
                TextColumn(f"[{THEME['primary']}]{{task.description}}"),
                BarColumn(style=THEME["muted"], complete_style=THEME["primary"]),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Validando arquivos...", total=len(xml_files))
                for xml_file in xml_files:
                    progress.update(task, description=f"[{THEME['primary']}]{xml_file.name[:30]}...")
                    if xsd_path:
                        r = validate_xsd(str(xml_file), xsd_path)
                    else:
                        r = validate_wellformed(str(xml_file))
                    results.append(r)
                    progress.advance(task)
                    time.sleep(0.05)  # visual feedback

            render_batch_summary(results)

            detail = Confirm.ask(f"[{THEME['muted']}]Ver detalhes de cada arquivo?[/]", default=False)
            if detail:
                for r in results:
                    render_result(r, show_info=False)

            if save_json and output_path:
                save_report(results, output_path)

        console.print()
        if not Confirm.ask(f"[{THEME['muted']}]Fazer outra validação?[/]", default=True):
            console.print(f"\n[bold {THEME['accent']}]Até logo! 👋[/]\n")
            break


# ─── CLI ─────────────────────────────────────────────────────────────────────
def cli_mode():
    parser = argparse.ArgumentParser(
        description="XML Validator Pro – Validação automática de XML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Validação bem-formado
  python xml_validator.py -f arquivo.xml

  # Validação com XSD
  python xml_validator.py -f arquivo.xml --xsd schema.xsd

  # Validação XPath
  python xml_validator.py -f arquivo.xml --xpath "//nfeProc/NFe" "//ide/cNF"

  # Lote de arquivos
  python xml_validator.py --batch ./xmls/ --xsd schema.xsd -o relatorio.json

  # Modo silencioso (apenas código de saída)
  python xml_validator.py -f arquivo.xml --quiet
        """
    )

    parser.add_argument("-f", "--file", help="Arquivo XML para validar")
    parser.add_argument("--xsd", help="Schema XSD para validação")
    parser.add_argument("--xpath", nargs="+", help="Expressões XPath para verificar")
    parser.add_argument("--batch", help="Pasta para validação em lote")
    parser.add_argument("-o", "--output", help="Arquivo de saída JSON com o relatório")
    parser.add_argument("--quiet", action="store_true", help="Saída mínima (apenas exit code)")
    parser.add_argument("--no-banner", action="store_true", help="Omite banner de abertura")

    args = parser.parse_args()

    if not args.no_banner and not args.quiet:
        print_banner()

    results = []

    if args.batch:
        # Modo lote
        folder = Path(args.batch)
        if not folder.is_dir():
            console.print(f"[bold {THEME['error']}]❌ Pasta não encontrada: {args.batch}[/]")
            sys.exit(2)

        xml_files = list(folder.glob("**/*.xml"))
        if not xml_files:
            console.print(f"[bold {THEME['warning']}]⚠ Nenhum XML encontrado em: {args.batch}[/]")
            sys.exit(2)

        if not args.quiet:
            console.print(f"[{THEME['info']}]📂 Processando {len(xml_files)} arquivo(s)...[/]\n")

        with Progress(
            SpinnerColumn(style=THEME["primary"]),
            TextColumn(f"[{THEME['primary']}]{{task.description}}"),
            BarColumn(style=THEME["muted"], complete_style=THEME["primary"]),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            disable=args.quiet,
        ) as progress:
            task = progress.add_task("Validando...", total=len(xml_files))
            for xf in xml_files:
                progress.update(task, description=f"{xf.name[:30]}...")
                if args.xsd:
                    r = validate_xsd(str(xf), args.xsd)
                elif args.xpath:
                    r = validate_xpath(str(xf), args.xpath)
                else:
                    r = validate_wellformed(str(xf))
                results.append(r)
                progress.advance(task)

        if not args.quiet:
            render_batch_summary(results)

    elif args.file:
        if not os.path.exists(args.file):
            console.print(f"[bold {THEME['error']}]❌ Arquivo não encontrado: {args.file}[/]")
            sys.exit(2)

        if args.xsd:
            result = validate_xsd(args.file, args.xsd)
        elif args.xpath:
            result = validate_xpath(args.file, args.xpath)
        else:
            result = validate_wellformed(args.file)

        results.append(result)
        if not args.quiet:
            render_result(result)

    else:
        # Sem argumentos: modo interativo
        interactive_mode()
        return

    if args.output:
        save_report(results, args.output)

    # Exit code: 0 = tudo válido, 1 = algum inválido
    all_valid = all(r.is_valid for r in results)
    sys.exit(0 if all_valid else 1)


# ─── Entrypoint ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        cli_mode()