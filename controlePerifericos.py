import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import os

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Periféricos - Suporte Corporativo")
        
        # Fixar o tamanho da janela e centralizar
        window_width = 1200
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.resizable(False, False)  # Desabilitar redimensionamento
        
        # Configurar ícone da janela
        try:
            self.root.iconbitmap("uol_icon.ico")
        except:
            print("Ícone não encontrado")
        
        # Conectar ao banco de dados
        self.conn = sqlite3.connect('inventory.db')
        self.c = self.conn.cursor()
        
        # Definir cores do Grupo UOL e cores complementares
        self.colors = {
            'yellow': '#FFD700',      # Amarelo UOL
            'orange': '#FF6B00',      # Laranja UOL
            'blue': '#0066CC',        # Azul UOL
            'dark_blue': '#1E1E2D',   # Azul escuro para fundo
            'light_yellow': '#FFEB3B', # Amarelo claro
            'dark_gray': '#2D2D3A',   # Cinza escuro
            'light_gray': '#3F3F4D',  # Cinza claro
            'white': '#FFFFFF',       # Branco
            'black': '#000000'        # Preto
        }

        # Configurar o fundo da janela principal
        self.root.configure(bg=self.colors['dark_blue'])
        
        # Configurar estilos
        self.style = ttk.Style()
        
        # Estilo geral
        self.style.configure('.',
                           background=self.colors['dark_blue'],
                           foreground=self.colors['white'])
        
        # Estilo dos botões
        self.style.configure('Action.TButton',
                           background=self.colors['yellow'],
                           foreground=self.colors['black'],
                           padding=(20, 10),
                           font=('Arial', 10, 'bold'))
        
        self.style.map('Action.TButton',
                      background=[('active', self.colors['orange'])],
                      foreground=[('active', self.colors['white'])])
        
        # Estilo dos labels
        self.style.configure('Label.TLabel',
                           background=self.colors['dark_blue'],
                           foreground=self.colors['white'],
                           font=('Arial', 10))
        
        # Estilo do título
        self.style.configure('Title.TLabel',
                           background=self.colors['dark_blue'],
                           foreground=self.colors['yellow'],
                           font=('Arial', 24, 'bold'))
        
        # Estilo da Treeview
        self.style.configure('Treeview',
                           background=self.colors['light_gray'],
                           foreground=self.colors['white'],
                           fieldbackground=self.colors['light_gray'],
                           rowheight=25)
        
        self.style.configure('Treeview.Heading',
                           background=self.colors['dark_gray'],
                           foreground=self.colors['yellow'],
                           font=('Arial', 10, 'bold'))
        
        self.style.map('Treeview',
                      background=[('selected', self.colors['yellow'])],
                      foreground=[('selected', self.colors['black'])])
        
        # Estilo dos frames
        self.style.configure('Main.TFrame',
                           background=self.colors['dark_blue'])
        
        self.style.configure('Control.TFrame',
                           background=self.colors['dark_blue'])
        
        # Inicializar banco de dados e interface
        self.create_tables()
        self.add_default_items()
        self.create_widgets()
        
    def create_tables(self):
        # Tabela de periféricos
        self.c.execute('''CREATE TABLE IF NOT EXISTS peripherals
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT UNIQUE,
                         current_stock INTEGER,
                         min_stock INTEGER)''')
        
        # Tabela de histórico com campo para ticket/chamado
        self.c.execute('''CREATE TABLE IF NOT EXISTS history
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         date TEXT,
                         peripheral TEXT,
                         operation TEXT,
                         quantity INTEGER,
                         ticket TEXT,
                         recipient TEXT,
                         notes TEXT)''')
        
        self.conn.commit()
    
    def add_default_items(self):
        default_items = [
            ("Mouse Dell", 0, 5),
            ("Mouse Logitech", 0, 5),
            ("Mouse Multilazer", 0, 5),
            ("Teclado Dell", 0, 5),
            ("Teclado Multilazer", 0, 5),
            ("Headset Jabra", 0, 3),
            ("Headset Logitech", 0, 3),
            ("Pilhas AA", 0, 10),
            ("Pilhas AAA", 0, 10),
            ("Carregador de notebook Dell Type C", 0, 2),
            ("Carregador de notebook Lenovo Type C", 0, 2),
            ("Carregador de notebook Dell 3420", 0, 2),
            ("Carregador de notebook Dell 7490", 0, 2),
            ("Carregador de MacBook", 0, 2),
            ("Dockstation Prata", 0, 2),
            ("Dockstation Preta", 0, 2),
            ("Cabo de Rede", 0, 5),
            ("Cabo de Energia", 0, 5),
            ("Cabo HDMI", 0, 5),
            ("Monitor Dell 24 polegadas", 0, 2),
            ("Monitor Lenovo 23 polegadas", 0, 2)
        ]
        
        try:
            self.c.executemany("INSERT OR IGNORE INTO peripherals (name, current_stock, min_stock) VALUES (?, ?, ?)", default_items)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao adicionar itens padrão: {e}")
        
    def create_widgets(self):
        # Container principal
        main_container = ttk.Frame(self.root, style='Main.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame do cabeçalho com logo
        header_frame = ttk.Frame(main_container, style='Main.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Carregar e exibir o logo do UOL
        try:
            logo_path = os.path.join('assets', 'uol_logo.png')
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                # Ajustar o tamanho do logo mantendo a proporção
                logo_width = 80  # Largura desejada
                logo_height = 80  # Altura desejada
                logo_image = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = ttk.Label(header_frame, image=self.logo_photo, background=self.colors['dark_blue'])
                logo_label.pack(side=tk.LEFT, padx=(20, 40))
            else:
                print("Arquivo do logo não encontrado")
        except Exception as e:
            print(f"Erro ao carregar o logo: {e}")
        
        # Título com padding ajustado
        title_label = ttk.Label(header_frame,
                              text="Controle de Periféricos - Suporte Corporativo",
                              style='Title.TLabel',
                              font=('Arial', 24, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Frame para a tabela com borda
        table_frame = ttk.Frame(main_container, style='Main.TFrame')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Treeview e Scrollbar
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(table_frame,
                                columns=('Name', 'Current', 'Min', 'Need'),
                                show='headings',
                                style='Treeview',
                                yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree.yview)
        
        # Configurar colunas
        self.tree.heading('Name', text='Periférico')
        self.tree.heading('Current', text='Em Estoque')
        self.tree.heading('Min', text='Mínimo')
        self.tree.heading('Need', text='Precisa Solicitar')
        
        # Configurar larguras das colunas
        self.tree.column('Name', width=300, minwidth=200)
        self.tree.column('Current', width=100, minwidth=80, anchor=tk.CENTER)
        self.tree.column('Min', width=100, minwidth=80, anchor=tk.CENTER)
        self.tree.column('Need', width=150, minwidth=100, anchor=tk.CENTER)
        
        # Frame para os botões com borda e padding
        button_container = ttk.Frame(main_container, style='Main.TFrame')
        button_container.pack(fill=tk.X, pady=(0, 10))
        
        # Criar um estilo especial para o frame dos botões com borda
        button_frame = tk.Frame(button_container, 
                              bg=self.colors['dark_blue'],
                              bd=2,
                              relief=tk.GROOVE)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame para botões da esquerda
        left_buttons = tk.Frame(button_frame, bg=self.colors['dark_blue'])
        left_buttons.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Frame para botões da direita
        right_buttons = tk.Frame(button_frame, bg=self.colors['dark_blue'])
        right_buttons.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Botões de gerenciamento de estoque (esquerda)
        stock_buttons = [
            ("Registrar Entrada", self.register_input),
            ("Registrar Saída", self.register_output),
            ("Atualizar Estoque Mínimo", self.update_min_stock)
        ]
        
        # Botões de gerenciamento de itens (direita)
        item_buttons = [
            ("Adicionar Item", self.add_item),
            ("Remover Item", self.remove_item),
            ("Gerar Relatório", self.generate_report),
            ("Consultar por Ticket", self.search_by_ticket)
        ]
        
        # Estilo especial para os botões
        button_style = ttk.Style()
        button_style.configure('Action.TButton',
                             padding=(15, 8),
                             font=('Arial', 10))
        
        # Adicionar botões com espaçamento consistente
        for text, command in stock_buttons:
            btn = ttk.Button(left_buttons,
                           text=text,
                           command=command,
                           style='Action.TButton')
            btn.pack(side=tk.LEFT, padx=5)
        
        for text, command in item_buttons:
            btn = ttk.Button(right_buttons,
                           text=text,
                           command=command,
                           style='Action.TButton')
            btn.pack(side=tk.LEFT, padx=5)
        
        # Atualizar a visualização
        self.update_view()
    
    def on_window_configure(self, event=None):
        """Ajusta o layout quando a janela é redimensionada"""
        if event and event.widget == self.root:
            # Atualizar tamanhos das colunas da tabela
            width = event.width
            self.tree.column('Name', width=int(width * 0.4))
            self.tree.column('Current', width=int(width * 0.2))
            self.tree.column('Min', width=int(width * 0.2))
            self.tree.column('Need', width=int(width * 0.2))
    
    def update_view(self):
        # Limpar a treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar dados do banco de dados
        self.c.execute("SELECT name, current_stock, min_stock FROM peripherals ORDER BY name")
        items = self.c.fetchall()
        
        # Adicionar itens à treeview com cores alternadas
        for i, item in enumerate(items):
            name, current, min_stock = item
            need = max(0, min_stock - current) if current < min_stock else 0
            
            # Alternar cores das linhas
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Destacar itens que precisam de reposição
            if need > 0:
                tag = 'needstock'
            
            self.tree.insert('', tk.END, 
                           values=(name, current, min_stock, need if need > 0 else "-"),
                           tags=(tag,))
    
    def add_item(self):
        # Janela para adicionar novo item
        add_window = tk.Toplevel(self.root)
        add_window.title("Adicionar Novo Periférico")
        add_window.configure(bg=self.colors['dark_blue'])
        
        # Fixar tamanho e centralizar
        dialog_width = 500
        dialog_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width - dialog_width) / 2)
        center_y = int((screen_height - dialog_height) / 2)
        
        add_window.geometry(f'{dialog_width}x{dialog_height}+{center_x}+{center_y}')
        add_window.resizable(False, False)
        add_window.transient(self.root)  # Tornar modal
        add_window.grab_set()  # Forçar foco
        
        # Frame principal com padding
        main_frame = ttk.Frame(add_window, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame,
                              text="Adicionar Novo Periférico",
                              style='Title.TLabel',
                              font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Frame para o formulário com grid
        form_frame = ttk.Frame(main_frame, style='Main.TFrame')
        form_frame.pack(fill=tk.X, padx=20)
        
        # Campos do formulário usando grid para melhor alinhamento
        ttk.Label(form_frame, 
                 text="Nome do Periférico:", 
                 style='Label.TLabel',
                 wraplength=200).grid(row=0, column=0, padx=5, pady=10, sticky='w')
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, padx=5, pady=10, sticky='w')
        
        ttk.Label(form_frame, 
                 text="Estoque Atual:", 
                 style='Label.TLabel').grid(row=1, column=0, padx=5, pady=10, sticky='w')
        current_entry = ttk.Entry(form_frame, width=10)
        current_entry.insert(0, "0")
        current_entry.grid(row=1, column=1, padx=5, pady=10, sticky='w')
        
        ttk.Label(form_frame, 
                 text="Estoque Mínimo:", 
                 style='Label.TLabel').grid(row=2, column=0, padx=5, pady=10, sticky='w')
        min_entry = ttk.Entry(form_frame, width=10)
        min_entry.insert(0, "1")
        min_entry.grid(row=2, column=1, padx=5, pady=10, sticky='w')
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame, style='Control.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botões
        def confirm_add():
            name = name_entry.get().strip()
            try:
                current = int(current_entry.get())
                min_stock = int(min_entry.get())
                
                if not name:
                    messagebox.showerror("Erro", "O nome do periférico não pode estar vazio.")
                    return
                
                self.c.execute("INSERT INTO peripherals (name, current_stock, min_stock) VALUES (?, ?, ?)", 
                             (name, current, min_stock))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Periférico adicionado com sucesso!")
                add_window.destroy()
                self.update_view()
            except ValueError:
                messagebox.showerror("Erro", "Estoque atual e mínimo devem ser números inteiros.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Já existe um periférico com esse nome.")
        
        ttk.Button(button_frame,
                  text="Adicionar",
                  command=confirm_add,
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame,
                  text="Cancelar",
                  command=add_window.destroy,
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
    
    def remove_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return
        
        item = self.tree.item(selected[0])
        name = item['values'][0]
        
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover '{name}'?"):
            self.c.execute("DELETE FROM peripherals WHERE name=?", (name,))
            self.conn.commit()
            self.update_view()
    
    def register_output(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para registrar saída.")
            return
        
        item = self.tree.item(selected[0])
        name = item['values'][0]
        current = item['values'][1]
        
        # Janela para registrar saída
        out_window = tk.Toplevel(self.root)
        out_window.title(f"Registrar Saída - {name}")
        out_window.configure(bg=self.colors['dark_blue'])
        
        # Fixar tamanho e centralizar
        dialog_width = 600
        dialog_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width - dialog_width) / 2)
        center_y = int((screen_height - dialog_height) / 2)
        
        out_window.geometry(f'{dialog_width}x{dialog_height}+{center_x}+{center_y}')
        out_window.resizable(False, False)
        out_window.transient(self.root)
        out_window.grab_set()
        
        # Frame principal com padding
        main_frame = ttk.Frame(out_window, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame,
                              text=f"Registrar Saída - {name}",
                              style='Title.TLabel',
                              font=('Arial', 16, 'bold'),
                              wraplength=500)  # Permitir quebra de linha se necessário
        title_label.pack(pady=(0, 20))
        
        # Informação do estoque atual
        stock_label = ttk.Label(main_frame,
                              text=f"Quantidade atual em estoque: {current}",
                              style='Label.TLabel',
                              font=('Arial', 12))
        stock_label.pack(pady=(0, 20))
        
        # Frame para o formulário com grid
        form_frame = ttk.Frame(main_frame, style='Main.TFrame')
        form_frame.pack(fill=tk.X, padx=20)
        
        # Campos usando grid
        labels = [
            "Quantidade a retirar:",
            "Número do Ticket/Chamado:",
            "Destinatário:",
            "Observações:"
        ]
        
        entries = []
        for i, label in enumerate(labels):
            ttk.Label(form_frame, 
                     text=label, 
                     style='Label.TLabel').grid(row=i, column=0, padx=5, pady=10, sticky='w')
            
            width = 10 if i == 0 else 40  # Quantidade menor, outros campos maiores
            entry = ttk.Entry(form_frame, width=width)
            entry.grid(row=i, column=1, padx=5, pady=10, sticky='w')
            entries.append(entry)
        
        qty_entry, ticket_entry, recipient_entry, notes_entry = entries
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame, style='Control.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def confirm_output():
            try:
                qty = int(qty_entry.get())
                ticket = ticket_entry.get().strip()
                recipient = recipient_entry.get().strip()
                notes = notes_entry.get().strip()
                
                if qty <= 0:
                    messagebox.showerror("Erro", "A quantidade deve ser maior que zero.")
                    return
                
                if current < qty:
                    messagebox.showerror("Erro", "Quantidade em estoque insuficiente.")
                    return
                
                if not ticket:
                    messagebox.showerror("Erro", "O número do ticket/chamado é obrigatório.")
                    return
                
                if not recipient:
                    messagebox.showerror("Erro", "O destinatário não pode estar vazio.")
                    return
                
                # Atualizar estoque
                new_qty = current - qty
                self.c.execute("UPDATE peripherals SET current_stock=? WHERE name=?", (new_qty, name))
                
                # Registrar no histórico
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.c.execute("""
                    INSERT INTO history 
                    (date, peripheral, operation, quantity, ticket, recipient, notes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (now, name, "Saída", qty, ticket, recipient, notes))
                
                self.conn.commit()
                messagebox.showinfo("Sucesso", 
                                  f"Saída de {qty} unidades de {name} registrada para {recipient}\n(Ticket: {ticket})")
                out_window.destroy()
                self.update_view()
            except ValueError:
                messagebox.showerror("Erro", "A quantidade deve ser um número inteiro.")
        
        ttk.Button(button_frame,
                  text="Confirmar Saída",
                  command=confirm_output,
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame,
                  text="Cancelar",
                  command=out_window.destroy,
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
    
    def register_input(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para registrar entrada.")
            return
        
        item = self.tree.item(selected[0])
        name = item['values'][0]
        current = item['values'][1]
        
        # Criar janela de diálogo
        dialog = self.create_dialog_window(f"Registrar Entrada - {name}", 400, 450)
        
        # Frame principal com padding
        main_frame = ttk.Frame(dialog, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame,
                              text=f"Registrar Entrada - {name}",
                              style='Title.TLabel',
                              font=('Arial', 14, 'bold'),
                              wraplength=350)
        title_label.pack(pady=(0, 20))
        
        # Informação do estoque atual
        current_label = ttk.Label(main_frame,
                               text=f"Quantidade atual: {current}",
                               style='Label.TLabel',
                               font=('Arial', 12))
        current_label.pack(pady=(0, 20))
        
        # Frame para o formulário
        form_frame = ttk.Frame(main_frame, style='Main.TFrame')
        form_frame.pack(fill=tk.X, padx=20)
        
        # Campos do formulário
        fields = [
            ("Quantidade a adicionar:", 10),
            ("Fornecedor:", 40),
            ("Nota Fiscal (opcional):", 40)
        ]
        
        entries = {}
        for i, (label_text, width) in enumerate(fields):
            label = ttk.Label(form_frame,
                            text=label_text,
                            style='Label.TLabel',
                            font=('Arial', 10, 'bold'))
            label.pack(anchor='w', pady=(10, 5))
            
            entry = ttk.Entry(form_frame, width=width)
            entry.pack(fill=tk.X, pady=(0, 10))
            entries[label_text] = entry
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame, style='Control.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def confirm_input():
            try:
                qty = int(entries["Quantidade a adicionar:"].get())
                supplier = entries["Fornecedor:"].get().strip()
                invoice = entries["Nota Fiscal (opcional):"].get().strip()
                
                if qty <= 0:
                    messagebox.showerror("Erro", "A quantidade deve ser maior que zero.")
                    return
                
                if not supplier:
                    messagebox.showerror("Erro", "O fornecedor não pode estar vazio.")
                    return
                
                # Atualizar estoque
                new_qty = current + qty
                self.c.execute("UPDATE peripherals SET current_stock=? WHERE name=?", (new_qty, name))
                
                # Registrar no histórico
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                notes = f"Fornecedor: {supplier}"
                if invoice:
                    notes += f", NF: {invoice}"
                
                self.c.execute("""
                    INSERT INTO history 
                    (date, peripheral, operation, quantity, recipient, notes) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (now, name, "Entrada", qty, supplier, notes))
                
                self.conn.commit()
                messagebox.showinfo("Sucesso", f"Entrada de {qty} unidades de {name} registrada.")
                self.close_dialog(dialog)
                self.update_view()
            except ValueError:
                messagebox.showerror("Erro", "A quantidade deve ser um número inteiro.")
        
        # Botões
        ttk.Button(button_frame,
                  text="Confirmar",
                  command=confirm_input,
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame,
                  text="Cancelar",
                  command=lambda: self.close_dialog(dialog),
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
    
    def generate_report(self):
        # Criar janela de diálogo
        dialog = self.create_dialog_window("Relatório de Estoque", 1000, 700)
        
        # Frame principal com padding
        main_frame = ttk.Frame(dialog, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame,
                              text="Relatório de Estoque",
                              style='Title.TLabel',
                              font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Frame para botões no topo
        top_button_frame = ttk.Frame(main_frame, style='Control.TFrame')
        top_button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botão de exportação
        export_btn = ttk.Button(top_button_frame,
                              text="Exportar Lista de Solicitações",
                              command=self.export_requests,
                              style='Action.TButton')
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba 1: Estoque atual
        stock_frame = ttk.Frame(notebook, style='Main.TFrame')
        notebook.add(stock_frame, text="Estoque Atual")
        
        # Treeview para o estoque
        tree_scroll = ttk.Scrollbar(stock_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        stock_tree = ttk.Treeview(stock_frame,
                                columns=('Name', 'Current', 'Min', 'Need'),
                                show='headings',
                                style='Treeview',
                                yscrollcommand=tree_scroll.set)
        
        # Configurar colunas
        headers = {
            'Name': ('Periférico', 300),
            'Current': ('Em Estoque', 100),
            'Min': ('Mínimo', 100),
            'Need': ('Precisa Solicitar', 150)
        }
        
        for col, (text, width) in headers.items():
            stock_tree.heading(col, text=text)
            stock_tree.column(col, width=width, minwidth=width, anchor=tk.CENTER)
        
        stock_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=stock_tree.yview)
        
        # Preencher dados do estoque
        self.c.execute("SELECT name, current_stock, min_stock FROM peripherals ORDER BY name")
        for item in self.c.fetchall():
            name, current, min_stock = item
            need = max(0, min_stock - current) if current < min_stock else 0
            stock_tree.insert('', tk.END, values=(name, current, min_stock, need if need > 0 else "-"))
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame, style='Control.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame,
                  text="Fechar",
                  command=lambda: self.close_dialog(dialog),
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
    
    def export_requests(self):
        """Exporta uma lista formatada dos itens que precisam ser solicitados ao estoque."""
        # Buscar itens que precisam ser solicitados
        self.c.execute("""
            SELECT name, current_stock, min_stock,
                   (min_stock - current_stock) as need
            FROM peripherals 
            WHERE current_stock < min_stock
            ORDER BY need DESC
        """)
        items = self.c.fetchall()
        
        if not items:
            messagebox.showinfo("Informação", "Não há itens para solicitar no momento.")
            return
        
        # Criar lista formatada
        export_list = []
        export_list.append("=== SOLICITAÇÃO DE PERIFÉRICOS - SUPORTE CORPORATIVO ===")
        export_list.append(f"\nData: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        export_list.append("\nItens para solicitar:")
        export_list.append("\n{:<40} {:>10} {:>10} {:>15}".format(
            "Periférico", "Em Estoque", "Mínimo", "Quantidade"))
        export_list.append("-" * 75)
        
        for item in items:
            name, current, min_stock, need = item
            export_list.append("{:<40} {:>10} {:>10} {:>15}".format(
                name, current, min_stock, need))
        
        export_list.append("\n" + "-" * 75)
        export_list.append("\nObservações:")
        export_list.append("1. Esta lista contém apenas itens abaixo do estoque mínimo")
        export_list.append("2. A quantidade solicitada é baseada na diferença entre estoque mínimo e atual")
        
        # Exibir lista em uma nova janela
        export_window = tk.Toplevel(self.root)
        export_window.title("Lista de Solicitações")
        export_window.geometry("800x600")
        export_window.configure(bg=self.colors['dark_blue'])
        
        # Frame principal
        main_frame = ttk.Frame(export_window, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Text widget para exibir a lista
        text_widget = tk.Text(main_frame, 
                            wrap=tk.NONE,
                            font=('Courier New', 11),
                            bg='white',
                            fg=self.colors['white'])
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=text_widget.yview)
        x_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=text_widget.xview)
        text_widget.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Inserir lista formatada
        text_widget.insert(tk.END, '\n'.join(export_list))
        text_widget.config(state=tk.DISABLED)
        
        # Frame para botões
        button_frame = ttk.Frame(export_window, style='Control.TFrame')
        button_frame.pack(fill=tk.X, pady=10)
        
        # Botão para copiar
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append('\n'.join(export_list))
            messagebox.showinfo("Sucesso", "Lista copiada para a área de transferência!")
        
        ttk.Button(button_frame,
                  text="Copiar Lista",
                  command=copy_to_clipboard,
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
        
        # Botão para salvar em arquivo
        def save_to_file():
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivo de Texto", "*.txt")],
                title="Salvar Lista de Solicitações"
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(export_list))
                messagebox.showinfo("Sucesso", "Lista salva com sucesso!")
        
        ttk.Button(button_frame,
                  text="Salvar em Arquivo",
                  command=save_to_file,
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
    
    def search_by_ticket(self):
        # Criar janela de diálogo
        dialog = self.create_dialog_window("Consultar por Ticket", 800, 600)
        
        # Frame principal com padding
        main_frame = ttk.Frame(dialog, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame de pesquisa
        search_frame = ttk.Frame(main_frame, style='Main.TFrame')
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Label e entrada para o ticket
        ttk.Label(search_frame,
                 text="Número do Ticket:",
                 style='Label.TLabel',
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        ticket_entry = ttk.Entry(search_frame, width=30, font=('Arial', 10))
        ticket_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame para a tabela
        table_frame = ttk.Frame(main_frame, style='Main.TFrame')
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview e Scrollbar
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ('Date', 'Peripheral', 'Operation', 'Qty', 'Recipient', 'Notes')
        result_tree = ttk.Treeview(table_frame,
                                 columns=columns,
                                 show='headings',
                                 style='Treeview',
                                 yscrollcommand=tree_scroll.set)
        
        # Configurar colunas
        headers = {
            'Date': ('Data', 150),
            'Peripheral': ('Periférico', 200),
            'Operation': ('Operação', 100),
            'Qty': ('Quantidade', 100),
            'Recipient': ('Destinatário', 150),
            'Notes': ('Observações', 200)
        }
        
        for col, (text, width) in headers.items():
            result_tree.heading(col, text=text)
            result_tree.column(col, width=width, minwidth=width)
        
        result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=result_tree.yview)
        
        def search():
            # Limpar a treeview
            for item in result_tree.get_children():
                result_tree.delete(item)
            
            ticket_number = ticket_entry.get().strip()
            if not ticket_number:
                messagebox.showwarning("Aviso", "Digite um número de ticket para pesquisar.")
                return
            
            # Buscar no banco de dados
            self.c.execute("""
                SELECT date, peripheral, operation, quantity, recipient, notes 
                FROM history 
                WHERE ticket=? 
                ORDER BY date DESC
            """, (ticket_number,))
            records = self.c.fetchall()
            
            if not records:
                messagebox.showinfo("Informação", f"Nenhum registro encontrado para o ticket {ticket_number}.")
                return
            
            for record in records:
                result_tree.insert('', tk.END, values=record)
        
        # Botões
        button_frame = ttk.Frame(main_frame, style='Control.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame,
                  text="Buscar",
                  command=search,
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame,
                  text="Fechar",
                  command=lambda: self.close_dialog(dialog),
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
    
    def update_min_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para atualizar o estoque mínimo.")
            return
        
        item = self.tree.item(selected[0])
        name = item['values'][0]
        current_min = item['values'][2]
        
        # Criar janela de diálogo
        dialog = self.create_dialog_window(f"Atualizar Estoque Mínimo - {name}", 400, 300)
        
        # Frame principal com padding
        main_frame = ttk.Frame(dialog, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame,
                              text=f"Atualizar Estoque Mínimo\n{name}",
                              style='Title.TLabel',
                              font=('Arial', 14, 'bold'),
                              wraplength=350,
                              justify='center')
        title_label.pack(pady=(0, 20))
        
        # Frame para o formulário
        form_frame = ttk.Frame(main_frame, style='Main.TFrame')
        form_frame.pack(fill=tk.X, padx=20)
        
        # Estoque mínimo atual
        ttk.Label(form_frame,
                 text=f"Estoque mínimo atual: {current_min}",
                 style='Label.TLabel',
                 font=('Arial', 12)).pack(pady=(0, 20))
        
        # Novo estoque mínimo
        ttk.Label(form_frame,
                 text="Novo estoque mínimo:",
                 style='Label.TLabel',
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        min_entry = ttk.Entry(form_frame, width=10, font=('Arial', 10))
        min_entry.insert(0, str(current_min))
        min_entry.pack(pady=(0, 20))
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame, style='Control.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def confirm_update():
            try:
                new_min = int(min_entry.get())
                
                if new_min < 0:
                    messagebox.showerror("Erro", "O estoque mínimo não pode ser negativo.")
                    return
                
                self.c.execute("UPDATE peripherals SET min_stock=? WHERE name=?", (new_min, name))
                self.conn.commit()
                messagebox.showinfo("Sucesso", f"Estoque mínimo de {name} atualizado para {new_min}.")
                self.close_dialog(dialog)
                self.update_view()
            except ValueError:
                messagebox.showerror("Erro", "O estoque mínimo deve ser um número inteiro.")
        
        ttk.Button(button_frame,
                  text="Atualizar",
                  command=confirm_update,
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame,
                  text="Cancelar",
                  command=lambda: self.close_dialog(dialog),
                  style='Action.TButton').pack(side=tk.RIGHT, padx=5)
    
    def create_dialog_window(self, title, width=500, height=300):
        """Cria uma janela de diálogo padrão"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg=self.colors['dark_blue'])
        
        # Centralizar a janela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width - width) / 2)
        center_y = int((screen_height - height) / 2)
        
        dialog.geometry(f'{width}x{height}+{center_x}+{center_y}')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Impedir minimização
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_dialog(dialog))
        
        # Configurar ícone
        try:
            icon_path = os.path.join('assets', 'uol_icon.ico')
            dialog.iconbitmap(icon_path)
        except Exception as e:
            print(f"Erro ao carregar o ícone: {e}")
        
        return dialog

    def close_dialog(self, dialog):
        """Fecha a janela de diálogo"""
        dialog.grab_release()
        dialog.destroy()
    
    def __del__(self):
        # Fechar conexão com o banco de dados
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()