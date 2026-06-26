#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import threading

COLORS = {
    "bg_dark":       "#0A1428",
    "bg_secondary":  "#1A2332",
    "primary":       "#0077B6",
    "primary_light": "#00B4D8",
    "success":       "#06D6A0",
    "error":         "#EF233C",
    "warning":       "#FFB703",
    "text_light":    "#E8F4FD",
    "text_muted":    "#6C757D",
    "border":        "#023E8A",
    "accent":        "#00B4D8",
}


class XMLValidatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Validator Pro")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        self.root.configure(bg=COLORS["bg_dark"])
        self.setup_styles()
        self.build_ui()
        self.validating = False
        self.current_file = None

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=COLORS["bg_dark"])
        style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_light"])
        style.configure("TButton", background=COLORS["primary"], foreground=COLORS["text_light"])
        style.map("TButton",
                  foreground=[('pressed', COLORS["text_light"]), ('active', COLORS["text_light"])],
                  background=[('pressed', COLORS["primary_light"]), ('active', COLORS["border"])])
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground=COLORS["primary_light"])
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12), foreground=COLORS["text_muted"])
        style.configure("Info.TLabel", font=("Segoe UI", 10), foreground=COLORS["text_light"])

    def build_ui(self):
        self.build_header()
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.build_file_section(main_frame)
        self.build_validation_options(main_frame)
        self.build_actions(main_frame)
        self.build_results(main_frame)

    def build_header(self):
        header = tk.Frame(self.root, bg=COLORS["bg_secondary"], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="XML Validator Pro",
                 font=("Segoe UI", 24, "bold"),
                 fg=COLORS["primary_light"], bg=COLORS["bg_secondary"]).pack(pady=10)
        tk.Label(header, text="v1.0 - Validacao Automatica de Arquivos XML",
                 font=("Segoe UI", 10),
                 fg=COLORS["text_muted"], bg=COLORS["bg_secondary"]).pack()

    def build_file_section(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg_secondary"], relief=tk.FLAT, bd=1)
        frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(frame, text="Selecionar Arquivo XML",
                 font=("Segoe UI", 12, "bold"),
                 fg=COLORS["primary_light"], bg=COLORS["bg_secondary"]).pack(anchor=tk.W, padx=15, pady=(10, 5))
        file_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        file_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
        self.file_var = tk.StringVar(value="Nenhum arquivo selecionado...")
        tk.Entry(file_frame, textvariable=self.file_var,
                 font=("Segoe UI", 10),
                 bg=COLORS["bg_dark"], fg=COLORS["text_light"],
                 relief=tk.FLAT, bd=2, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Button(file_frame, text="Procurar", command=self.browse_file,
                  bg=COLORS["primary"], fg=COLORS["text_light"],
                  font=("Segoe UI", 10, "bold"), relief=tk.FLAT,
                  padx=20, pady=8, cursor="hand2").pack(side=tk.LEFT)

    def build_validation_options(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg_secondary"], relief=tk.FLAT, bd=1)
        frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(frame, text="Opcoes de Validacao",
                 font=("Segoe UI", 12, "bold"),
                 fg=COLORS["primary_light"], bg=COLORS["bg_secondary"]).pack(anchor=tk.W, padx=15, pady=(10, 10))
        options_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        options_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        self.validation_mode = tk.StringVar(value="wellformed")
        mode_frame = tk.Frame(options_frame, bg=COLORS["bg_dark"])
        mode_frame.pack(fill=tk.X, pady=5)
        for text, value in [("Bem-Formado", "wellformed"), ("Com XSD", "xsd"), ("Com XPath", "xpath")]:
            tk.Radiobutton(mode_frame, text=text, variable=self.validation_mode,
                           value=value, bg=COLORS["bg_dark"], fg=COLORS["text_light"],
                           activebackground=COLORS["primary"], activeforeground=COLORS["text_light"],
                           selectcolor=COLORS["primary"], font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 20))
        xsd_frame = tk.Frame(options_frame, bg=COLORS["bg_dark"])
        xsd_frame.pack(fill=tk.X, pady=10)
        tk.Label(xsd_frame, text="Arquivo XSD (se necessario):",
                 font=("Segoe UI", 9), fg=COLORS["text_muted"], bg=COLORS["bg_dark"]).pack(anchor=tk.W)
        xsd_input = tk.Frame(xsd_frame, bg=COLORS["bg_dark"])
        xsd_input.pack(fill=tk.X, pady=(5, 0))
        self.xsd_var = tk.StringVar()
        tk.Entry(xsd_input, textvariable=self.xsd_var,
                 font=("Segoe UI", 9),
                 bg=COLORS["bg_secondary"], fg=COLORS["text_light"],
                 relief=tk.FLAT, bd=1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Button(xsd_input, text="Selecionar", command=self.browse_xsd,
                  bg=COLORS["accent"], fg=COLORS["bg_dark"],
                  font=("Segoe UI", 9), relief=tk.FLAT, padx=15).pack(side=tk.LEFT)

    def build_actions(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg_dark"])
        frame.pack(fill=tk.X, pady=(0, 15))
        self.validate_btn = tk.Button(frame, text="Validar", command=self.validate,
                                      bg=COLORS["success"], fg=COLORS["bg_dark"],
                                      font=("Segoe UI", 12, "bold"),
                                      relief=tk.FLAT, padx=30, pady=10, cursor="hand2")
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.batch_btn = tk.Button(frame, text="Lote", command=self.batch_validate,
                                   bg=COLORS["primary"], fg=COLORS["text_light"],
                                   font=("Segoe UI", 12, "bold"),
                                   relief=tk.FLAT, padx=30, pady=10, cursor="hand2")
        self.batch_btn.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(frame, text="Relatorio", command=self.open_report,
                  bg=COLORS["accent"], fg=COLORS["bg_dark"],
                  font=("Segoe UI", 12, "bold"),
                  relief=tk.FLAT, padx=30, pady=10, cursor="hand2").pack(side=tk.LEFT)

    def build_results(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg_secondary"], relief=tk.FLAT, bd=1)
        frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame, text="Resultados",
                 font=("Segoe UI", 12, "bold"),
                 fg=COLORS["primary_light"], bg=COLORS["bg_secondary"]).pack(anchor=tk.W, padx=15, pady=(10, 5))
        text_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))
        self.result_text = scrolledtext.ScrolledText(text_frame,
                                                     font=("Consolas", 9),
                                                     bg=COLORS["bg_dark"],
                                                     fg=COLORS["text_light"],
                                                     relief=tk.FLAT, bd=0,
                                                     wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.tag_config("success", foreground=COLORS["success"])
        self.result_text.tag_config("error", foreground=COLORS["error"])
        self.result_text.tag_config("warning", foreground=COLORS["warning"])
        self.result_text.tag_config("info", foreground=COLORS["primary_light"])
        self.result_text.tag_config("muted", foreground=COLORS["text_muted"])

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo XML",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.file_var.set(file_path)

    def browse_xsd(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo XSD",
            filetypes=[("XSD files", "*.xsd"), ("All files", "*.*")]
        )
        if file_path:
            self.xsd_var.set(file_path)

    def validate(self):
        if not self.current_file:
            messagebox.showwarning("Atencao", "Selecione um arquivo XML primeiro!")
            return
        if not os.path.exists(self.current_file):
            messagebox.showerror("Erro", "Arquivo nao encontrado!")
            return
        self.validate_btn.config(state=tk.DISABLED)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        threading.Thread(target=self._validate_thread).start()

    def _validate_thread(self):
        try:
            mode = self.validation_mode.get()
            cmd = ['C:/Python313/python.exe',
                   'c:\\Users\\João\\Desktop\\validaxml\\validaXML.py',
                   '-f', self.current_file, '--no-banner']
            if mode == "xsd" and self.xsd_var.get():
                cmd.extend(['--xsd', self.xsd_var.get()])
            elif mode == "xpath":
                cmd.extend(['--xpath', '//'])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            self.result_text.config(state=tk.NORMAL)
            if result.stdout:
                self.result_text.insert(tk.END, result.stdout, "success")
            if result.stderr:
                self.result_text.insert(tk.END, "\n" + result.stderr, "error")
            tag = "success" if result.returncode == 0 else "error"
            msg = "\nValidacao concluida com sucesso!" if result.returncode == 0 else "\nValidacao falhou!"
            self.result_text.insert(tk.END, msg, tag)
        except Exception as e:
            self.result_text.insert(tk.END, f"Erro: {str(e)}", "error")
        finally:
            self.result_text.config(state=tk.DISABLED)
            self.validate_btn.config(state=tk.NORMAL)

    def batch_validate(self):
        folder = filedialog.askdirectory(title="Selecionar pasta com XMLs")
        if not folder:
            return
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Processando lote...", "info")
        threading.Thread(target=self._batch_thread, args=(folder,)).start()

    def _batch_thread(self, folder):
        try:
            output_file = os.path.join(folder, f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            cmd = ['C:/Python313/python.exe',
                   'c:\\Users\\João\\Desktop\\validaxml\\validaXML.py',
                   '--batch', folder,
                   '-o', output_file,
                   '--no-banner']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result.stdout, "success")
            if os.path.exists(output_file):
                self.result_text.insert(tk.END, f"\nRelatorio salvo em: {output_file}", "info")
        except Exception as e:
            self.result_text.insert(tk.END, f"Erro: {str(e)}", "error")
        finally:
            self.result_text.config(state=tk.DISABLED)

    def open_report(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar relatorio JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            summary = data.get("summary", {})
            self.result_text.insert(tk.END, "RELATORIO\n\n", "info")
            self.result_text.insert(tk.END, f"Total: {summary.get('total', 0)}\n", "muted")
            self.result_text.insert(tk.END, f"Validos: {summary.get('valid', 0)}\n", "success")
            self.result_text.insert(tk.END, f"Invalidos: {summary.get('invalid', 0)}\n\n", "error")
            for r in data.get("results", []):
                status = "OK" if r["valid"] else "ERRO"
                self.result_text.insert(tk.END, f"[{status}] {r['file']}\n",
                                        "success" if r["valid"] else "error")
                for err in r.get("errors", []):
                    self.result_text.insert(tk.END, f"  {err}\n", "warning")
            self.result_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Erro", f"Nao foi possivel abrir o relatorio: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = XMLValidatorGUI(root)
    root.mainloop()
