#!/usr/bin/env python3
"""
XML Validator Pro - Interface GUI Moderna
Tkinter com design moderno, cores azuis escuras e funcionalidade completa
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import threading

# ─── Paleta de Cores ──────────────────────────────────────────────────────────
COLORS = {
    "bg_dark":      "#0A1428",      # Fundo muito escuro
    "bg_secondary": "#1A2332",      # Fundo secundário
    "primary":      "#0077B6",      # Azul profissional
    "primary_light":"#00B4D8",      # Azul claro
    "success":      "#06D6A0",      # Verde
    "error":        "#EF233C",      # Vermelho
    "warning":      "#FFB703",      # Amarelo
    "text_light":   "#E8F4FD",      # Texto claro
    "text_muted":   "#6C757D",      # Texto tênue
    "border":       "#023E8A",      # Azul muito escuro
    "accent":       "#00B4D8",      # Ciano
}

class XMLValidatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Validator Pro - Interface Moderna")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Configurar tema
        self.root.configure(bg=COLORS["bg_dark"])
        self.setup_styles()
        self.build_ui()
        
        # Estado
        self.validating = False
        self.current_file = None
        
    def setup_styles(self):
        """Configura estilos TTK com cores azuis escuras"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores personalizadas
        style.configure("TFrame", background=COLORS["bg_dark"])
        style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_light"])
        style.configure("TButton", background=COLORS["primary"], foreground=COLORS["text_light"])
        
        style.map("TButton",
                 foreground=[('pressed', COLORS["text_light"]),
                           ('active', COLORS["text_light"])],
                 background=[('pressed', COLORS["primary_light"]),
                           ('active', COLORS["border"])])
        
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), 
                       foreground=COLORS["primary_light"])
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12), 
                       foreground=COLORS["text_muted"])
        style.configure("Info.TLabel", font=("Segoe UI", 10), 
                       foreground=COLORS["text_light"])
    
    def build_ui(self):
        """Constrói a interface"""
        # Header
        self.build_header()
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Conteúdo
        self.build_file_section(main_frame)
        self.build_validation_options(main_frame)
        self.build_actions(main_frame)
        self.build_results(main_frame)
    
    def build_header(self):
        """Constrói o cabeçalho"""
        header = tk.Frame(self.root, bg=COLORS["bg_secondary"], height=80)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        # Título
        title_label = tk.Label(header, text="◆ XML Validator Pro ◆", 
                              font=("Segoe UI", 24, "bold"),
                              fg=COLORS["primary_light"], bg=COLORS["bg_secondary"])
        title_label.pack(pady=10)
        
        # Subtítulo
        sub_label = tk.Label(header, text="v1.0 – Validação Automática de Arquivos XML",
                            font=("Segoe UI", 10),
                            fg=COLORS["text_muted"], bg=COLORS["bg_secondary"])
        sub_label.pack()
    
    def build_file_section(self, parent):
        """Seção de seleção de arquivo"""
        frame = tk.Frame(parent, bg=COLORS["bg_secondary"], relief=tk.FLAT, bd=1)
        frame.pack(fill=tk.X, pady=(0, 15))
        
        label = tk.Label(frame, text="📁 Selecionar Arquivo XML", 
                        font=("Segoe UI", 12, "bold"),
                        fg=COLORS["primary_light"], bg=COLORS["bg_secondary"])
        label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Linha de arquivo
        file_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        file_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        self.file_var = tk.StringVar(value="Nenhum arquivo selecionado...")
        file_entry = tk.Entry(file_frame, textvariable=self.file_var, 
                             font=("Segoe UI", 10),
                             bg=COLORS["bg_dark"], fg=COLORS["text_light"],
                             relief=tk.FLAT, bd=2, state='readonly')
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(file_frame, text="Procurar", command=self.browse_file,
                              bg=COLORS["primary"], fg=COLORS["text_light"],
                              font=("Segoe UI", 10, "bold"), relief=tk.FLAT, 
                              padx=20, pady=8, cursor="hand2")
        browse_btn.pack(side=tk.LEFT)
    
    def build_validation_options(self, parent):
        """Opções de validação"""
        frame = tk.Frame(parent, bg=COLORS["bg_secondary"], relief=tk.FLAT, bd=1)
        frame.pack(fill=tk.X, pady=(0, 15))
        
        label = tk.Label(frame, text="⚙️  Opções de Validação",
                        font=("Segoe UI", 12, "bold"),
                        fg=COLORS["primary_light"], bg=COLORS["bg_secondary"])
        label.pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        options_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        options_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Validação bem-formado (padrão)
        self.validation_mode = tk.StringVar(value="wellformed")
        
        mode_frame = tk.Frame(options_frame, bg=COLORS["bg_dark"])
        mode_frame.pack(fill=tk.X, pady=5)
        
        modes = [
            ("Bem-Formado", "wellformed"),
            ("Com XSD", "xsd"),
            ("Com XPath", "xpath"),
        ]
        
        for text, value in modes:
            rb = tk.Radiobutton(mode_frame, text=text, variable=self.validation_mode,
                               value=value, bg=COLORS["bg_dark"], fg=COLORS["text_light"],
                               activebackground=COLORS["primary"],
                               activeforeground=COLORS["text_light"],
                               selectcolor=COLORS["primary"], font=("Segoe UI", 10))
            rb.pack(side=tk.LEFT, padx=(0, 20))
        
        # Arquivo XSD
        xsd_frame = tk.Frame(options_frame, bg=COLORS["bg_dark"])
        xsd_frame.pack(fill=tk.X, pady=10)
        
        xsd_label = tk.Label(xsd_frame, text="Arquivo XSD (se necessário):",
                            font=("Segoe UI", 9), fg=COLORS["text_muted"],
                            bg=COLORS["bg_dark"])
        xsd_label.pack(anchor=tk.W)
        
        xsd_input = tk.Frame(xsd_frame, bg=COLORS["bg_dark"])
        xsd_input.pack(fill=tk.X, pady=(5, 0))
        
        self.xsd_var = tk.StringVar()
        xsd_entry = tk.Entry(xsd_input, textvariable=self.xsd_var,
                            font=("Segoe UI", 9),
                            bg=COLORS["bg_secondary"], fg=COLORS["text_light"],
                            relief=tk.FLAT, bd=1)
        xsd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        xsd_btn = tk.Button(xsd_input, text="Selecionar", command=self.browse_xsd,
                           bg=COLORS["accent"], fg=COLORS["bg_dark"],
                           font=("Segoe UI", 9), relief=tk.FLAT, padx=15)
        xsd_btn.pack(side=tk.LEFT)
    
    def build_actions(self, parent):
        """Botões de ação"""
        frame = tk.Frame(parent, bg=COLORS["bg_dark"])
        frame.pack(fill=tk.X, pady=(0, 15))
        
        self.validate_btn = tk.Button(frame, text="✓ Validar", 
                                     command=self.validate,
                                     bg=COLORS["success"], fg=COLORS["bg_dark"],
                                     font=("Segoe UI", 12, "bold"),
                                     relief=tk.FLAT, padx=30, pady=10, cursor="hand2")
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.batch_btn = tk.Button(frame, text="📂 Lote", 
                                  command=self.batch_validate,
                                  bg=COLORS["primary"], fg=COLORS["text_light"],
                                  font=("Segoe UI", 12, "bold"),
                                  relief=tk.FLAT, padx=30, pady=10, cursor="hand2")
        self.batch_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        report_btn = tk.Button(frame, text="📊 Relatório", 
                              command=self.open_report,
                              bg=COLORS["accent"], fg=COLORS["bg_dark"],
                              font=("Segoe UI", 12, "bold"),
                              relief=tk.FLAT, padx=30, pady=10, cursor="hand2")
        report_btn.pack(side=tk.LEFT)
    
    def build_results(self, parent):
        """Área de resultados"""
        frame = tk.Frame(parent, bg=COLORS["bg_secondary"], relief=tk.FLAT, bd=1)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = tk.Label(frame, text="📋 Resultados",
                        font=("Segoe UI", 12, "bold"),
                        fg=COLORS["primary_light"], bg=COLORS["bg_secondary"])
        label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Área de texto com scroll
        text_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))
        
        self.result_text = scrolledtext.ScrolledText(text_frame,
                                                     font=("Consolas", 9),
                                                     bg=COLORS["bg_dark"],
                                                     fg=COLORS["text_light"],
                                                     relief=tk.FLAT, bd=0,
                                                     wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Tags para colorização
        self.result_text.tag_config("success", foreground=COLORS["success"])
        self.result_text.tag_config("error", foreground=COLORS["error"])
        self.result_text.tag_config("warning", foreground=COLORS["warning"])
        self.result_text.tag_config("info", foreground=COLORS["primary_light"])
        self.result_text.tag_config("muted", foreground=COLORS["text_muted"])
    
    def browse_file(self):
        """Abre diálogo de seleção de arquivo"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo XML",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.file_var.set(file_path)
    
    def browse_xsd(self):
        """Abre diálogo para selecionar XSD"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo XSD",
            filetypes=[("XSD files", "*.xsd"), ("All files", "*.*")]
        )
        if file_path:
            self.xsd_var.set(file_path)
    
    def validate(self):
        """Executa validação"""
        if not self.current_file:
            messagebox.showwarning("Atenção", "Selecione um arquivo XML primeiro!")
            return
        
        if not os.path.exists(self.current_file):
            messagebox.showerror("Erro", "Arquivo não encontrado!")
            return
        
        self.validate_btn.config(state=tk.DISABLED)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self._validate_thread)
        thread.start()
    
    def _validate_thread(self):
        """Thread para validação"""
        try:
            mode = self.validation_mode.get()
            cmd = ['C:/Python313/python.exe', 
                   'c:\\Users\\João\\Desktop\\validaxml\\validaXML.py',
                   '-f', self.current_file, '--no-banner']
            
            if mode == "xsd" and self.xsd_var.get():
                cmd.extend(['--xsd', self.xsd_var.get()])
            elif mode == "xpath":
                cmd.extend(['--xpath', '//'])  # XPath básico
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            self.result_text.config(state=tk.NORMAL)
            
            if result.stdout:
                self.result_text.insert(tk.END, result.stdout, "success")
            
            if result.stderr:
                self.result_text.insert(tk.END, "\n" + result.stderr, "error")
            
            if result.returncode == 0:
                self.result_text.insert(tk.END, "\n✓ Validação concluída com sucesso!", "success")
            else:
                self.result_text.insert(tk.END, "\n❌ Validação falhou!", "error")
        
        except Exception as e:
            self.result_text.insert(tk.END, f"Erro: {str(e)}", "error")
        
        finally:
            self.result_text.config(state=tk.DISABLED)
            self.validate_btn.config(state=tk.NORMAL)
    
    def batch_validate(self):
        """Validação em lote"""
        folder = filedialog.askdirectory(title="Selecionar pasta com XMLs")
        if not folder:
            return
        
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Processando lote...", "info")
        
        thread = threading.Thread(target=self._batch_thread, args=(folder,))
        thread.start()
    
    def _batch_thread(self, folder):
        """Thread para lote"""
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
                self.result_text.insert(tk.END, f"\n✓ Relatório salvo em: {output_file}", "info")
        
        except Exception as e:
            self.result_text.insert(tk.END, f"Erro: {str(e)}", "error")
        
        finally:
            self.result_text.config(state=tk.DISABLED)
    
    def open_report(self):
        """Abre arquivo de relatório"""
        file_path = filedialog.askopenfilename(
            title="Selecionar relatório JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            
            # Exibir sumário
            summary = data.get("summary", {})
            self.result_text.insert(tk.END, "═ RELATÓRIO ═\n\n", "info")
            self.result_text.insert(tk.END, f"Total: {summary.get('total', 0)}\n", "muted")
            self.result_text.insert(tk.END, f"Válidos: {summary.get('valid', 0)}\n", "success")
            self.result_text.insert(tk.END, f"Inválidos: {summary.get('invalid', 0)}\n\n", "error")
            
            # Detalhes
            for r in data.get("results", []):
                status = "✓" if r["valid"] else "✗"
                self.result_text.insert(tk.END, f"{status} {r['file']}\n", 
                                       "success" if r["valid"] else "error")
                
                if r.get("errors"):
                    for err in r["errors"]:
                        self.result_text.insert(tk.END, f"  ⚠ {err}\n", "warning")
            
            self.result_text.config(state=tk.DISABLED)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o relatório: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = XMLValidatorGUI(root)
    root.mainloop()
