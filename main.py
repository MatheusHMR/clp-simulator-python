import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from components.timer import Timer
from components.counter import Counter
from reverse_polish_notation import logical_structure
from views import (
    authors,
    error,
    program_help,
    compile_success,
    confirm_new,
    file_controller,
)
import automata.sentence_interpreter as senInt
import communication as comm
from scan_cycle.scan_cycle import ScanCycle

class PLCProgrammer:
    def __init__(self, root):
        self.root = root
        self.root.title("PLC Programmer (Tkinter)")

        self.scan_cycle = ScanCycle(logical_structure=logical_structure.LogicalStructure([]))
        self.in_execution = False
        self.is_connected = False
        self.serial_port = comm.initializeSerial()

        # Valores default
        self.timer_values = {f'T{i+1}': 0 for i in range(32)}
        self.counter_values = {f'C{i+1}': 0 for i in range(32)}

        # Listas de timers e counters usados
        self.used_timers = []
        self.used_counters = []  # Nova lista para contadores
        self.timers_need_config = False

        # Vars para entradas/saídas
        self.input_vars = [tk.BooleanVar(value=False) for _ in range(8)]
        self.output_vars = [tk.BooleanVar(value=False) for _ in range(8)]

        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()

        self.update_status_bar()

    def create_scrollable_frame(self, parent):
        # Cria um frame rolável
        container = tk.Frame(parent)
        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return container, scrollable_frame

    def create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Novo", accelerator="Ctrl+N", command=self.new_program)
        filemenu.add_command(label="Abrir", accelerator="Ctrl+O", command=self.open_program)
        filemenu.add_command(label="Salvar", accelerator="Ctrl+S", command=self.save_program)
        filemenu.add_separator()
        filemenu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=filemenu)

        toolsmenu = tk.Menu(menubar, tearoff=0)
        toolsmenu.add_command(label="Compilar", accelerator="F9", command=lambda: self.compile_program(self.program_text.get("1.0", tk.END)))
        toolsmenu.add_command(label="Configurar Temporizadores", command=self.configure_timers)
        menubar.add_cascade(label="Ferramentas", menu=toolsmenu)

        clpmenu = tk.Menu(menubar, tearoff=0)
        clpmenu.add_command(label="Conectar", command=self.connect_clp)
        clpmenu.add_command(label="Executar", accelerator="F5", command=self.run_program)
        clpmenu.add_command(label="Parar", command=self.stop_program)
        menubar.add_cascade(label="CLP", menu=clpmenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Sobre", command=self.show_about)
        helpmenu.add_command(label="Como Programar", command=self.show_help)
        menubar.add_cascade(label="Ajuda", menu=helpmenu)

        self.root.config(menu=menubar)

    def create_toolbar(self):
        toolbar_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(toolbar_frame, text="Novo", command=self.new_program).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar_frame, text="Abrir", command=self.open_program).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar_frame, text="Salvar", command=self.save_program).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar_frame, text="Compilar", command=lambda: self.compile_program(self.program_text.get("1.0", tk.END))).pack(side=tk.LEFT, padx=2, pady=2)

        self.run_button = tk.Button(toolbar_frame, text="Executar", command=self.run_program)
        self.run_button.pack(side=tk.LEFT, padx=2, pady=2)

        tk.Button(toolbar_frame, text="Parar", command=self.stop_program).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar_frame, text="Config. Temporizadores", command=self.configure_timers).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar_frame, text="Config. Contadores", command=self.configure_counters).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar_frame, text="Conectar", command=self.connect_clp).pack(side=tk.LEFT, padx=2, pady=2)

    def create_main_layout(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="Programa:").pack(anchor=tk.W)
        self.program_text = tk.Text(left_frame, width=80, height=25)
        self.program_text.pack(fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.conn_status_label = tk.Label(right_frame, text="Status de Conexão: Desconectado", fg="red")
        self.conn_status_label.pack(anchor=tk.W)
        self.exec_status_label = tk.Label(right_frame, text="Status de Execução: Parado", fg="red")
        self.exec_status_label.pack(anchor=tk.W)

        io_frame = tk.LabelFrame(right_frame, text="Entradas/Saídas")
        io_frame.pack(fill=tk.BOTH, expand=True)

        self.io_canvas = tk.Canvas(io_frame, width=300, height=300, bg="white")
        self.io_canvas.pack(fill=tk.BOTH, expand=True)

        self.input_click_areas = []
        self.output_positions = []
        self.draw_io()

        self.io_canvas.bind("<Button-1>", self.on_canvas_click)

        mem_frame = tk.LabelFrame(right_frame, text="Memórias (B1-B8)")
        mem_frame.pack(fill=tk.BOTH, expand=True)
        self.boolean_labels = []
        for i in range(8):
            l = tk.Label(mem_frame, text=f"B{i+1}: False")
            l.pack(anchor=tk.W)
            self.boolean_labels.append(l)

        # Notebook para Temporizadores/Contadores usados
        notebook_frame = tk.Frame(right_frame)
        notebook_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Abas serão criadas após compilação, quando soubermos quais timers/counters usados
        # Inicialmente podem estar vazias

        self.timer_tab = tk.Frame(self.notebook)
        self.notebook.add(self.timer_tab, text="Temporizadores")

        self.counter_tab = tk.Frame(self.notebook)
        self.notebook.add(self.counter_tab, text="Contadores")

        self.timer_container, self.timer_frame = self.create_scrollable_frame(self.timer_tab)
        self.timer_container.pack(fill=tk.BOTH, expand=True)

        self.counter_container, self.counter_frame = self.create_scrollable_frame(self.counter_tab)
        self.counter_container.pack(fill=tk.BOTH, expand=True)

        self.timer_labels = []
        self.counter_labels = []

        self.root.after(100, self.periodic_update)

    def draw_io(self):
        self.io_canvas.delete("all")
        self.input_click_areas.clear()
        self.output_positions.clear()

        start_x, start_y = 20, 30
        dist_y = 40

        for i in range(8):
            y = start_y + i*dist_y
            state = self.input_vars[i].get()
            color = "red" if state else "black"

            if state:
                line_text = "______"
            else:
                line_text = "_/--\\_"

            self.io_canvas.create_text(60, y, text=line_text, font=("Consolas",10), fill=color, anchor="center")
            self.io_canvas.create_text(60, y+15, text=f"I{i+1}", font=("Consolas",10), fill=color, anchor="center")

            text_width = 50
            x1, y1 = 60 - text_width//2, y-10
            x2, y2 = 60 + text_width//2, y+25
            self.io_canvas.create_rectangle(x1, y1, x2, y2, outline="", fill="", tags=f"input{i}")
            self.input_click_areas.append((x1, y1, x2, y2, i))

        start_x_out = 200
        for i in range(8):
            y = start_y + i*dist_y
            state = self.output_vars[i].get()
            coil_color = "red" if state else "black"
            coil_char = "(X)" if state else "( )"

            self.io_canvas.create_text(start_x_out, y, text=f"O{i+1} {coil_char}", font=("Consolas",10), fill=coil_color, anchor="w")

            self.output_positions.append((start_x_out, y, start_x_out+50, y+20))

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        for area in self.input_click_areas:
            x1, y1, x2, y2, idx = area
            if x1 <= x <= x2 and y1 <= y <= y2:
                current = self.input_vars[idx].get()
                self.input_vars[idx].set(not current)
                self.update_input(idx)
                self.draw_io()
                break

    def update_input(self, idx):
        self.scan_cycle.inputs[idx] = self.input_vars[idx].get()
        self.scan_cycle.memory_image_inputs[idx] = self.input_vars[idx].get()

    def periodic_update(self):
        if self.in_execution:
            self.execute_cycle()

        for i, val in enumerate(self.scan_cycle.outputs):
            self.output_vars[i].set(val)

        self.draw_io()

        for i, val in enumerate(self.scan_cycle.boolean_memories[:8]):
            self.boolean_labels[i].config(text=f"B{i+1}: {val}")

        # Atualiza timers usados
        for (t_type, t_num), l in zip(self.used_timers, self.timer_labels):
            t_name = f"T{t_num}"
            timer_value = self.scan_cycle.timers[t_name].remaining_time
            l.config(text=f"{t_type}{t_num}: {timer_value}")

        # Atualiza counters usados
        # Lembre-se que CUP1 e CDN1 referem-se ao contador C1
        # Então extraímos o número e usamos self.scan_cycle.counters para pegar o count
        for (c_type, c_num), l in zip(self.used_counters, self.counter_labels):
            c_name = f"C{c_num}"
            count_value = self.scan_cycle.counters[c_name].count
            l.config(text=f"{c_type}{c_num}: {count_value}")

        self.root.after(100, self.periodic_update)

    def update_status_bar(self):
        self.conn_status_label.config(text=f"Status de Conexão: {'Conectado' if self.is_connected else 'Desconectado'}",
                                      fg=("green" if self.is_connected else "red"))
        self.exec_status_label.config(text=f"Status de Execução: {'Executando' if self.in_execution else 'Parado'}",
                                      fg=("green" if self.in_execution else "red"))

    def new_program(self):
        if confirm_new.confirmNewProgram(self.root):
            self.program_text.delete("1.0", tk.END)
            self.in_execution = False
            self.scan_cycle.initialize_system()

    def open_program(self):
        if confirm_new.confirmNewProgram(self.root):
            path = filedialog.askopenfilename()
            if path:
                try:
                    with open(path, 'r') as file:
                        content = file.read()
                    self.program_text.delete("1.0", tk.END)
                    self.program_text.insert("1.0", content)
                except:
                    messagebox.showerror("Erro", "Não foi possível abrir o arquivo especificado.")

    def save_program(self):
        path = filedialog.asksaveasfilename()
        if path:
            program = self.program_text.get("1.0", tk.END)
            try:
                with open(path, 'w') as file:
                    file.write(program)
            except:
                messagebox.showerror("Erro", "Não foi possível salvar o arquivo.")

    def compile_program(self, program_text):
        if not program_text.strip():
            messagebox.showerror("Erro", "A área de programação está vazia.")
            return
        self.in_execution = False
        program_lines = program_text.strip().splitlines()
        errors = []
        self.used_timers.clear()
        self.used_counters.clear()

        for idx, line in enumerate(program_lines):
            res = senInt.interpretSentence(line)
            if res == 1:
                errors.append(f'Erro de sintaxe na linha {idx + 1}')
            elif res == 2:
                errors.append(f'Erro de rótulo na linha {idx + 1}')

            # Procurar por TONx e TOFx
            found_timers = re.findall(r'(TON|TOF)(\d+)', line.upper())
            for t_type, t_num in found_timers:
                if (t_type, t_num) not in self.used_timers:
                    self.used_timers.append((t_type, t_num))

            # Procurar por contadores CUPx, CDNx
            found_counters = re.findall(r'(CUP|CDN)(\d+)', line.upper())
            for c_type, c_num in found_counters:
                if (c_type, c_num) not in self.used_counters:
                    self.used_counters.append((c_type, c_num))

        if errors:
            messagebox.showerror("Erro", "\n".join(errors))
        else:
            self.scan_cycle.user_program = program_lines
            messagebox.showinfo("Sucesso", "Programa compilado com sucesso!")

            if self.used_timers:
                self.timers_need_config = True
                self.run_button.config(state=tk.DISABLED)
            else:
                self.timers_need_config = False
                self.run_button.config(state=tk.NORMAL)

            # Atualiza a aba de temporizadores e contadores utilizados
            for widget in self.timer_frame.winfo_children():
                widget.destroy()
            self.timer_labels.clear()
            for (t_type, t_num) in self.used_timers:
                l = tk.Label(self.timer_frame, text=f"{t_type}{t_num}: 0")
                l.pack(anchor=tk.W)
                self.timer_labels.append(l)

            for widget in self.counter_frame.winfo_children():
                widget.destroy()
            self.counter_labels.clear()
            for (c_type, c_num) in self.used_counters:
                l = tk.Label(self.counter_frame, text=f"{c_type}{c_num}: 0")
                l.pack(anchor=tk.W)
                self.counter_labels.append(l)

    def configure_timers(self):
        if not self.used_timers:
            messagebox.showinfo("Aviso", "Nenhum temporizador foi utilizado no programa.")
            return

        top = tk.Toplevel(self.root)
        top.title("Configurar Temporizadores")
        timer_entries = {}

        for i, (t_type, t_num) in enumerate(self.used_timers):
            timer_name = f"T{t_num}"
            current_val = self.timer_values.get(timer_name, 0)
            tk.Label(top, text=f"{t_type}{t_num}:").grid(row=i, column=0, sticky=tk.W)
            e = tk.Entry(top)
            e.insert(0, str(current_val))
            e.grid(row=i, column=1)
            timer_entries[timer_name] = e

        def salvar():
            all_valid = True
            for t_name, entry in timer_entries.items():
                val = entry.get()
                try:
                    val_int = int(val)
                    self.timer_values[t_name] = val_int
                    self.scan_cycle.timers[t_name].preset = val_int
                except ValueError:
                    messagebox.showerror("Erro", f"Valor inválido para {t_name}. Insira um número inteiro.")
                    all_valid = False
                    break
            if all_valid:
                messagebox.showinfo("Sucesso", "Temporizadores configurados com sucesso.")
                self.timers_need_config = False
                self.run_button.config(state=tk.NORMAL)
                top.destroy()

        tk.Button(top, text="Salvar", command=salvar).grid(row=len(self.used_timers)+1, column=0)
        tk.Button(top, text="Cancelar", command=top.destroy).grid(row=len(self.used_timers)+1, column=1)

    def configure_counters(self):
        top = tk.Toplevel(self.root)
        top.title("Configurar Contadores")
        counter_entries = {}
        if not self.used_counters:
            messagebox.showinfo("Aviso", "Nenhum contador foi utilizado no programa.")
            return

        for i, (c_type, c_num) in enumerate(self.used_counters):
            c_name = f"C{c_num}"
            tk.Label(top, text=f"{c_type}{c_num}:").grid(row=i, column=0, sticky=tk.W)
            e = tk.Entry(top)
            e.insert(0, str(self.counter_values[c_name]))
            e.grid(row=i, column=1)
            counter_entries[c_name] = e

        def salvar():
            for c_name, entry in counter_entries.items():
                val = entry.get()
                try:
                    self.counter_values[c_name] = int(val)
                except:
                    pass
                self.scan_cycle.counters[c_name].preset = self.counter_values[c_name]
            messagebox.showinfo("Sucesso", "Contadores atualizados com sucesso.")
            top.destroy()

        tk.Button(top, text="Salvar", command=salvar).grid(row=len(self.used_counters)+1, column=0)
        tk.Button(top, text="Cancelar", command=top.destroy).grid(row=len(self.used_counters)+1, column=1)

    def connect_clp(self):
        if self.serial_port != 'none':
            if comm.estabilishConnection(self.serial_port):
                self.is_connected = True
            else:
                self.is_connected = False
                messagebox.showerror("Erro", "Não foi possível conectar ao dispositivo.")
        else:
            messagebox.showerror("Erro", "Nenhum dispositivo foi detectado.")
        self.update_status_bar()

    def run_program(self):
        if self.timers_need_config:
            messagebox.showwarning("Aviso", "Configure primeiro os temporizadores antes de executar.")
            return
        self.scan_cycle.set_mode('RUN')
        self.in_execution = True
        self.update_status_bar()

    def stop_program(self):
        self.scan_cycle.set_mode('STOP')
        self.scan_cycle.initialize_system()
        self.update_io_values([False]*8, [False]*8, [False]*32)
        self.in_execution = False
        self.is_connected = False
        self.update_status_bar()

    def show_about(self):
        messagebox.showinfo("Sobre", "PLC Programmer\nVersão 1.0\nDesenvolvido por:\nEmanuel Carlos de Mello\nFúlvio Diniz Santos\nGilmar dos Reis Júnior\nMatheus Henrique Maia Ramos\n\nBaseado no trabalho de Nathan Silva Rodrigues")

    def show_help(self):
        program_help.programHelpWindow(self.root)

    def execute_cycle(self):
        inputs = [var.get() for var in self.input_vars]
        self.scan_cycle.inputs = inputs
        self.scan_cycle.read_inputs()
        self.scan_cycle.update_timers()
        self.scan_cycle.process_user_program()
        self.scan_cycle.update_outputs()

    def update_counters(self):
        # Este método incrementa counters no UI, mas o funcionamento real dos counters depende da lógica RPN
        # e da detecção de borda no scan_cycle. Ajuste se necessário.
        pass

    def update_io_values(self, inputs, outputs, booleans):
        self.scan_cycle.inputs = inputs
        self.scan_cycle.outputs = outputs
        for i, val in enumerate(booleans):
            self.scan_cycle.boolean_memories[i] = val

if __name__ == '__main__':
    root = tk.Tk()
    app = PLCProgrammer(root)
    root.mainloop()
