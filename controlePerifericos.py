import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Periféricos - Suporte Corporativo")
        self.root.geometry("1000x700")
        
        # Conectar ao banco de dados
        self.conn = sqlite3.connect('inventory.db')
        self.c = self.conn.cursor()
        
        # Criar tabelas se não existirem
        self.create_tables()
        
        # Adicionar itens padrão se a tabela estiver vazia
        self.add_default_items()
        
        # Interface do usuário
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
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para exibir os periféricos
        self.tree = ttk.Treeview(main_frame, columns=('Name', 'Current', 'Min', 'Need'), show='headings')
        self.tree.heading('Name', text='Periférico')
        self.tree.heading('Current', text='Em Estoque')
        self.tree.heading('Min', text='Mínimo')
        self.tree.heading('Need', text='Precisa Solicitar')
        self.tree.column('Name', width=300)
        self.tree.column('Current', width=100, anchor=tk.CENTER)
        self.tree.column('Min', width=100, anchor=tk.CENTER)
        self.tree.column('Need', width=150, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Frame para controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Botões
        ttk.Button(control_frame, text="Adicionar Item", command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Remover Item", command=self.remove_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Registrar Saída", command=self.register_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Registrar Entrada", command=self.register_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Gerar Relatório", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Atualizar Estoque Mínimo", command=self.update_min_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Consultar por Ticket", command=self.search_by_ticket).pack(side=tk.LEFT, padx=5)
        
        # Atualizar a visualização
        self.update_view()
    
    def update_view(self):
        # Limpar a treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Buscar dados do banco de dados
        self.c.execute("SELECT name, current_stock, min_stock FROM peripherals ORDER BY name")
        items = self.c.fetchall()
        
        # Adicionar itens à treeview
        for item in items:
            name, current, min_stock = item
            need = max(0, min_stock - current) if current < min_stock else 0
            self.tree.insert('', tk.END, values=(name, current, min_stock, need if need > 0 else "-"))
    
    def add_item(self):
        # Janela para adicionar novo item
        add_window = tk.Toplevel(self.root)
        add_window.title("Adicionar Novo Periférico")
        
        # Campos do formulário
        ttk.Label(add_window, text="Nome do Periférico:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(add_window, width=40)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_window, text="Estoque Atual:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        current_entry = ttk.Entry(add_window, width=10)
        current_entry.insert(0, "0")
        current_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(add_window, text="Estoque Mínimo:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        min_entry = ttk.Entry(add_window, width=10)
        min_entry.insert(0, "1")
        min_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Botão para confirmar
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
        
        ttk.Button(add_window, text="Adicionar", command=confirm_add).grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)
    
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
        
        ttk.Label(out_window, text=f"Quantidade atual: {current}").pack(padx=10, pady=5)
        
        ttk.Label(out_window, text="Quantidade a retirar:").pack(padx=10, pady=5)
        qty_entry = ttk.Entry(out_window, width=10)
        qty_entry.pack(padx=10, pady=5)
        
        ttk.Label(out_window, text="Número do Ticket/Chamado:").pack(padx=10, pady=5)
        ticket_entry = ttk.Entry(out_window, width=20)
        ticket_entry.pack(padx=10, pady=5)
        
        ttk.Label(out_window, text="Destinatário:").pack(padx=10, pady=5)
        recipient_entry = ttk.Entry(out_window, width=30)
        recipient_entry.pack(padx=10, pady=5)
        
        ttk.Label(out_window, text="Observações:").pack(padx=10, pady=5)
        notes_entry = ttk.Entry(out_window, width=40)
        notes_entry.pack(padx=10, pady=5)
        
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
                self.c.execute("INSERT INTO history (date, peripheral, operation, quantity, ticket, recipient, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (now, name, "Saída", qty, ticket, recipient, notes))
                
                self.conn.commit()
                messagebox.showinfo("Sucesso", f"Saída de {qty} unidades de {name} registrada para {recipient} (Ticket: {ticket}).")
                out_window.destroy()
                self.update_view()
            except ValueError:
                messagebox.showerror("Erro", "A quantidade deve ser um número inteiro.")
        
        ttk.Button(out_window, text="Confirmar", command=confirm_output).pack(padx=10, pady=10)
    
    def register_input(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para registrar entrada.")
            return
        
        item = self.tree.item(selected[0])
        name = item['values'][0]
        current = item['values'][1]
        
        # Janela para registrar entrada
        in_window = tk.Toplevel(self.root)
        in_window.title(f"Registrar Entrada - {name}")
        
        ttk.Label(in_window, text=f"Quantidade atual: {current}").pack(padx=10, pady=5)
        
        ttk.Label(in_window, text="Quantidade a adicionar:").pack(padx=10, pady=5)
        qty_entry = ttk.Entry(in_window, width=10)
        qty_entry.pack(padx=10, pady=5)
        
        ttk.Label(in_window, text="Fornecedor:").pack(padx=10, pady=5)
        supplier_entry = ttk.Entry(in_window, width=30)
        supplier_entry.pack(padx=10, pady=5)
        
        ttk.Label(in_window, text="Nota Fiscal (opcional):").pack(padx=10, pady=5)
        invoice_entry = ttk.Entry(in_window, width=30)
        invoice_entry.pack(padx=10, pady=5)
        
        def confirm_input():
            try:
                qty = int(qty_entry.get())
                supplier = supplier_entry.get().strip()
                invoice = invoice_entry.get().strip()
                
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
                
                self.c.execute("INSERT INTO history (date, peripheral, operation, quantity, recipient, notes) VALUES (?, ?, ?, ?, ?, ?)",
                              (now, name, "Entrada", qty, supplier, notes))
                
                self.conn.commit()
                messagebox.showinfo("Sucesso", f"Entrada de {qty} unidades de {name} registrada.")
                in_window.destroy()
                self.update_view()
            except ValueError:
                messagebox.showerror("Erro", "A quantidade deve ser um número inteiro.")
        
        ttk.Button(in_window, text="Confirmar", command=confirm_input).pack(padx=10, pady=10)
    
    def generate_report(self):
        # Janela para exibir relatório
        report_window = tk.Toplevel(self.root)
        report_window.title("Relatório de Estoque")
        report_window.geometry("1000x700")
        
        # Frame para o relatório
        report_frame = ttk.Frame(report_window)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Abas para diferentes relatórios
        notebook = ttk.Notebook(report_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba 1: Estoque atual
        stock_frame = ttk.Frame(notebook)
        notebook.add(stock_frame, text="Estoque Atual")
        
        stock_tree = ttk.Treeview(stock_frame, columns=('Name', 'Current', 'Min', 'Need'), show='headings')
        stock_tree.heading('Name', text='Periférico')
        stock_tree.heading('Current', text='Em Estoque')
        stock_tree.heading('Min', text='Mínimo')
        stock_tree.heading('Need', text='Precisa Solicitar')
        stock_tree.column('Name', width=300)
        stock_tree.column('Current', width=100, anchor=tk.CENTER)
        stock_tree.column('Min', width=100, anchor=tk.CENTER)
        stock_tree.column('Need', width=150, anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(stock_frame, orient="vertical", command=stock_tree.yview)
        stock_tree.configure(yscrollcommand=vsb.set)
        
        stock_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher com dados
        self.c.execute("SELECT name, current_stock, min_stock FROM peripherals ORDER BY name")
        items = self.c.fetchall()
        
        for item in items:
            name, current, min_stock = item
            need = max(0, min_stock - current) if current < min_stock else 0
            stock_tree.insert('', tk.END, values=(name, current, min_stock, need if need > 0 else "-"))
        
        # Aba 2: Itens para solicitar
        request_frame = ttk.Frame(notebook)
        notebook.add(request_frame, text="Itens para Solicitar")
        
        request_tree = ttk.Treeview(request_frame, columns=('Name', 'Current', 'Min', 'Need'), show='headings')
        request_tree.heading('Name', text='Periférico')
        request_tree.heading('Current', text='Em Estoque')
        request_tree.heading('Min', text='Mínimo')
        request_tree.heading('Need', text='Quantidade a Solicitar')
        request_tree.column('Name', width=300)
        request_tree.column('Current', width=100, anchor=tk.CENTER)
        request_tree.column('Min', width=100, anchor=tk.CENTER)
        request_tree.column('Need', width=150, anchor=tk.CENTER)
        
        vsb2 = ttk.Scrollbar(request_frame, orient="vertical", command=request_tree.yview)
        request_tree.configure(yscrollcommand=vsb2.set)
        
        request_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher com dados
        self.c.execute("SELECT name, current_stock, min_stock FROM peripherals WHERE current_stock < min_stock ORDER BY name")
        items = self.c.fetchall()
        
        for item in items:
            name, current, min_stock = item
            need = min_stock - current
            request_tree.insert('', tk.END, values=(name, current, min_stock, need))
        
        # Aba 3: Histórico completo
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="Histórico Completo")
        
        history_tree = ttk.Treeview(history_frame, 
                                  columns=('Date', 'Peripheral', 'Operation', 'Qty', 'Ticket', 'Recipient', 'Notes'), 
                                  show='headings')
        history_tree.heading('Date', text='Data')
        history_tree.heading('Peripheral', text='Periférico')
        history_tree.heading('Operation', text='Operação')
        history_tree.heading('Qty', text='Quantidade')
        history_tree.heading('Ticket', text='Ticket/Chamado')
        history_tree.heading('Recipient', text='Destinatário/Fornecedor')
        history_tree.heading('Notes', text='Observações')
        history_tree.column('Date', width=120)
        history_tree.column('Peripheral', width=150)
        history_tree.column('Operation', width=80)
        history_tree.column('Qty', width=70, anchor=tk.CENTER)
        history_tree.column('Ticket', width=100)
        history_tree.column('Recipient', width=150)
        history_tree.column('Notes', width=200)
        
        vsb3 = ttk.Scrollbar(history_frame, orient="vertical", command=history_tree.yview)
        history_tree.configure(yscrollcommand=vsb3.set)
        
        history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb3.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher com dados
        self.c.execute("SELECT date, peripheral, operation, quantity, ticket, recipient, notes FROM history ORDER BY date DESC LIMIT 100")
        records = self.c.fetchall()
        
        for record in records:
            history_tree.insert('', tk.END, values=record)
        
        # Aba 4: Relatório por ticket
        ticket_frame = ttk.Frame(notebook)
        notebook.add(ticket_frame, text="Relatório por Ticket")
        
        # Controles para pesquisa
        search_frame = ttk.Frame(ticket_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Pesquisar Ticket:").pack(side=tk.LEFT)
        self.ticket_search_entry = ttk.Entry(search_frame, width=20)
        self.ticket_search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Buscar", command=lambda: self.search_ticket_in_report(self.ticket_search_entry.get(), ticket_tree)).pack(side=tk.LEFT)
        
        # Treeview para resultados
        ticket_tree = ttk.Treeview(ticket_frame, 
                                 columns=('Date', 'Peripheral', 'Operation', 'Qty', 'Recipient', 'Notes'), 
                                 show='headings')
        ticket_tree.heading('Date', text='Data')
        ticket_tree.heading('Peripheral', text='Periférico')
        ticket_tree.heading('Operation', text='Operação')
        ticket_tree.heading('Qty', text='Quantidade')
        ticket_tree.heading('Recipient', text='Destinatário')
        ticket_tree.heading('Notes', text='Observações')
        ticket_tree.column('Date', width=120)
        ticket_tree.column('Peripheral', width=150)
        ticket_tree.column('Operation', width=80)
        ticket_tree.column('Qty', width=70, anchor=tk.CENTER)
        ticket_tree.column('Recipient', width=150)
        ticket_tree.column('Notes', width=200)
        
        vsb4 = ttk.Scrollbar(ticket_frame, orient="vertical", command=ticket_tree.yview)
        ticket_tree.configure(yscrollcommand=vsb4.set)
        
        ticket_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb4.pack(side=tk.RIGHT, fill=tk.Y)
    
    def search_ticket_in_report(self, ticket_number, treeview):
        # Limpar a treeview
        for item in treeview.get_children():
            treeview.delete(item)
        
        if not ticket_number:
            messagebox.showwarning("Aviso", "Digite um número de ticket para pesquisar.")
            return
        
        # Buscar no banco de dados
        self.c.execute("SELECT date, peripheral, operation, quantity, recipient, notes FROM history WHERE ticket=? ORDER BY date DESC", (ticket_number,))
        records = self.c.fetchall()
        
        if not records:
            messagebox.showinfo("Informação", f"Nenhum registro encontrado para o ticket {ticket_number}.")
            return
        
        for record in records:
            treeview.insert('', tk.END, values=record)
    
    def search_by_ticket(self):
        # Janela para pesquisa por ticket
        search_window = tk.Toplevel(self.root)
        search_window.title("Consultar por Ticket")
        search_window.geometry("800x500")
        
        # Frame de pesquisa
        search_frame = ttk.Frame(search_window)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Número do Ticket:").pack(side=tk.LEFT)
        ticket_entry = ttk.Entry(search_frame, width=20)
        ticket_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Buscar", command=lambda: self.search_ticket(ticket_entry.get(), result_tree)).pack(side=tk.LEFT)
        
        # Treeview para resultados
        result_tree = ttk.Treeview(search_window, 
                                  columns=('Date', 'Peripheral', 'Operation', 'Qty', 'Recipient', 'Notes'), 
                                  show='headings')
        result_tree.heading('Date', text='Data')
        result_tree.heading('Peripheral', text='Periférico')
        result_tree.heading('Operation', text='Operação')
        result_tree.heading('Qty', text='Quantidade')
        result_tree.heading('Recipient', text='Destinatário')
        result_tree.heading('Notes', text='Observações')
        result_tree.column('Date', width=120)
        result_tree.column('Peripheral', width=150)
        result_tree.column('Operation', width=80)
        result_tree.column('Qty', width=70, anchor=tk.CENTER)
        result_tree.column('Recipient', width=150)
        result_tree.column('Notes', width=200)
        
        vsb = ttk.Scrollbar(search_window, orient="vertical", command=result_tree.yview)
        result_tree.configure(yscrollcommand=vsb.set)
        
        result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
    
    def search_ticket(self, ticket_number, treeview):
        # Limpar a treeview
        for item in treeview.get_children():
            treeview.delete(item)
        
        if not ticket_number:
            messagebox.showwarning("Aviso", "Digite um número de ticket para pesquisar.")
            return
        
        # Buscar no banco de dados
        self.c.execute("SELECT date, peripheral, operation, quantity, recipient, notes FROM history WHERE ticket=? ORDER BY date DESC", (ticket_number,))
        records = self.c.fetchall()
        
        if not records:
            messagebox.showinfo("Informação", f"Nenhum registro encontrado para o ticket {ticket_number}.")
            return
        
        for record in records:
            treeview.insert('', tk.END, values=record)
    
    def update_min_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para atualizar o estoque mínimo.")
            return
        
        item = self.tree.item(selected[0])
        name = item['values'][0]
        current_min = item['values'][2]
        
        # Janela para atualizar estoque mínimo
        min_window = tk.Toplevel(self.root)
        min_window.title(f"Atualizar Estoque Mínimo - {name}")
        
        ttk.Label(min_window, text=f"Estoque mínimo atual: {current_min}").pack(padx=10, pady=5)
        
        ttk.Label(min_window, text="Novo estoque mínimo:").pack(padx=10, pady=5)
        min_entry = ttk.Entry(min_window, width=10)
        min_entry.insert(0, str(current_min))
        min_entry.pack(padx=10, pady=5)
        
        def confirm_update():
            try:
                new_min = int(min_entry.get())
                
                if new_min < 0:
                    messagebox.showerror("Erro", "O estoque mínimo não pode ser negativo.")
                    return
                
                self.c.execute("UPDATE peripherals SET min_stock=? WHERE name=?", (new_min, name))
                self.conn.commit()
                messagebox.showinfo("Sucesso", f"Estoque mínimo de {name} atualizado para {new_min}.")
                min_window.destroy()
                self.update_view()
            except ValueError:
                messagebox.showerror("Erro", "O estoque mínimo deve ser um número inteiro.")
        
        ttk.Button(min_window, text="Atualizar", command=confirm_update).pack(padx=10, pady=10)
    
    def __del__(self):
        # Fechar conexão com o banco de dados
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()