import PySimpleGUI as sg
from components.timer import Timer
from components.counter import Counter
from reverse_polish_notation.create_notation import reverse_polish_notation
from reverse_polish_notation.logical_structure import LogicalStructure
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

class PLCProgrammer:
    def __init__(self):
        # Inicialização de variáveis
        self.logical_structure = LogicalStructure([])
        self.in_execution = False
        self.is_connected = False
        self.serial_port = comm.initializeSerial()
        self.timer_values = {f'T{i+1}': 0 for i in range(32)}
        self.setup_gui()

    def setup_gui(self):
        sg.theme('DarkBlue14')  # Tema mais moderno
        # Definir ícones e fontes para um visual mais profissional
        menu_layout = [
            ['Arquivo', ['Novo      Ctrl+N', 'Abrir     Ctrl+O', 'Salvar    Ctrl+S', '---', 'Sair']],
            ['Ferramentas', ['Compilar  F9', 'Configurar Temporizadores']],
            ['CLP', ['Conectar', 'Executar  F5', 'Parar']],
            ['Ajuda', ['Sobre', 'Como Programar']],
        ]

        # Barra de ferramentas com botões usando símbolos Unicode
        toolbar = [
            sg.Button('🗎 Novo', tooltip='Novo (Ctrl+N)', key='Novo'),
            sg.Button('📂 Abrir', tooltip='Abrir (Ctrl+O)', key='Abrir'),
            sg.Button('💾 Salvar', tooltip='Salvar (Ctrl+S)', key='Salvar'),
            sg.Button('🔄 Compilar', tooltip='Compilar (F9)', key='Compilar'),
            sg.Button('▶ Executar', tooltip='Executar (F5)', key='Executar'),
            sg.Button('⏹ Parar', tooltip='Parar', key='Parar'),
            sg.Button('⚙ Configurar Temporizadores', tooltip='Configurar Temporizadores', key='Configurar Temporizadores'),
            sg.Button('🔌 Conectar', tooltip='Conectar', key='Conectar'),
            sg.Button('❓ Ajuda', tooltip='Ajuda', key='Sobre'),
        ]

        # Área de programação com numeração de linhas
        programming_area = sg.Frame('', [
            [sg.Multiline('', size=(80, 25), key='-PROGRAM-', font='Consolas 12', autoscroll=True, expand_x=True, expand_y=True)]
        ], relief=sg.RELIEF_SUNKEN)

        # Visualização gráfica do CLP
        plc_viewer = sg.Frame('Monitoramento do CLP', [
            [sg.Text('Status de Conexão:', size=(20, 1)), sg.Text('Desconectado', key='-CONN_STATUS-', text_color='red')],
            [sg.Text('Status de Execução:', size=(20, 1)), sg.Text('Parado', key='-EXEC_STATUS-', text_color='red')],
            [sg.HorizontalSeparator()],
            [sg.TabGroup([
                [sg.Tab('Entradas/Saídas', self.create_io_layout())],
                [sg.Tab('Memórias', self.create_memory_layout())],
                [sg.Tab('Temporizadores', self.create_timer_layout())],
            ], expand_x=True, expand_y=True)]
        ], expand_x=True, expand_y=True)

        # Layout principal
        layout = [
            [sg.Menu(menu_layout)],
            toolbar,
            [sg.Pane([programming_area, plc_viewer], orientation='h', relief=sg.RELIEF_RIDGE, expand_x=True, expand_y=True)]
        ]

        self.window = sg.Window('PLC Programmer', layout, finalize=True, resizable=True)

        # Bindings dos atalhos de teclado
        self.window.bind('<Control-n>', 'Novo')
        self.window.bind('<Control-o>', 'Abrir')
        self.window.bind('<Control-s>', 'Salvar')
        self.window.bind('<F5>', 'Executar')
        self.window.bind('<F9>', 'Compilar')

    def create_io_layout(self):
        inputs = [[sg.Checkbox(f'I{i+1}', key=f'-IN-{i+1}-', enable_events=True)] for i in range(8)]
        outputs = [[sg.Checkbox(f'O{i+1}', key=f'-OUT-{i+1}-', disabled=True)] for i in range(8)]
        layout = [
            [sg.Frame('Entradas Digitais', inputs, expand_y=True), sg.Frame('Saídas Digitais', outputs, expand_y=True)]
        ]
        return layout

    def create_memory_layout(self):
        booleans = [[sg.Text(f'B{i+1}:', size=(5, 1)), sg.Text('False', key=f'-BOOL-{i+1}-')] for i in range(32)]
        layout = [
            [sg.Column(booleans, scrollable=True, vertical_scroll_only=True, size=(200, 300))]
        ]
        return layout

    def create_timer_layout(self):
        timers = [[sg.Text(f'T{i+1}:', size=(5, 1)), sg.Text('0', key=f'-TIMER-{i+1}-')] for i in range(32)]
        layout = [
            [sg.Column(timers, scrollable=True, vertical_scroll_only=True, size=(200, 300))]
        ]
        return layout

    def start(self):
        while True:
            event, values = self.window.read(timeout=100)
            if event in (sg.WIN_CLOSED, 'Sair'):
                break
            elif event in ('Novo', 'Abrir', 'Salvar', 'Compilar', 'Configurar Temporizadores', 'Conectar', 'Executar', 'Parar', 'Sobre', 'Como Programar'):
                self.handle_menu_events(event, values)
            elif event.startswith('-IN-'):
                self.handle_input_change(event, values)
            if self.in_execution:
                self.execute_cycle()
        self.window.close()

    def handle_menu_events(self, event, values):
        if event == 'Novo':
            self.new_program()
        elif event == 'Abrir':
            self.open_program()
        elif event == 'Salvar':
            self.save_program()
        elif event == 'Compilar':
            self.compile_program(values['-PROGRAM-'])
        elif event == 'Configurar Temporizadores':
            self.configure_timers()
        elif event == 'Conectar':
            self.connect_clp()
        elif event == 'Executar':
            self.run_program()
        elif event == 'Parar':
            self.stop_program()
        elif event == 'Sobre':
            self.show_about()
        elif event == 'Como Programar':
            self.show_help()

    def handle_input_change(self, event, values):
        # Atualiza o estado das entradas na estrutura lógica
        index = int(event.replace('-IN-', '').replace('-', '')) - 1
        self.logical_structure.inputs[index] = values[event]

    def new_program(self):
        if confirm_new.confirmNewProgram():
            self.window['-PROGRAM-'].update('')
            self.in_execution = self.update_execution_status(False)

    def open_program(self):
        self.window.hide()
        if confirm_new.confirmNewProgram():
            path = file_controller.openFileWindow()
            if path:
                try:
                    with open(path, 'r') as file:
                        program = file.read()
                    self.window['-PROGRAM-'].update(program)
                except:
                    error.errorWindow('Erro!', 'Não foi possível abrir o arquivo especificado.')
        self.window.un_hide()

    def save_program(self):
        self.window.hide()
        path = file_controller.saveFileWindow()
        if path:
            program = self.window['-PROGRAM-'].get()
            try:
                with open(path, 'w') as file:
                    file.write(program)
            except:
                error.errorWindow('Erro!', 'Não foi possível salvar o arquivo no caminho especificado.')
        self.window.un_hide()

    def compile_program(self, program_text):
        if not program_text.strip():
            error.errorWindow('Erro!', 'A área de programação está vazia.')
            return
        self.in_execution = self.update_execution_status(False)
        program_lines = program_text.strip().splitlines()
        errors = []
        for idx, line in enumerate(program_lines):
            res = senInt.interpretSentece(line)
            if res == 1:
                errors.append(f'Erro de sintaxe na linha {idx + 1}')
            elif res == 2:
                errors.append(f'Erro de rótulo na linha {idx + 1}')
        if errors:
            error.errorWindow('Erro!', '\n'.join(errors))
        else:
            polish_notations = []
            for line in program_lines:
                clean_line = line.replace(' ', '').upper()
                identifier = clean_line.split('=')[0]
                notation = reverse_polish_notation(clean_line)
                polish_notations.append((identifier, notation))
            self.logical_structure.updatePolishNotations(polish_notations)
            compile_success.compileSuccessWindow()

    def configure_timers(self):
        timer_layout = [
            [sg.Text(f'T{i+1}:', size=(5, 1)), sg.InputText(self.timer_values[f'T{i+1}'], key=f'T{i+1}', size=(5, 1))]
            for i in range(32)
        ]
        layout = [
            [sg.Column(timer_layout, scrollable=True, vertical_scroll_only=True, size=(250, 400))],
            [sg.Button('Salvar'), sg.Button('Cancelar')]
        ]
        window = sg.Window('Configurar Temporizadores', layout, modal=True)
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Cancelar'):
                break
            elif event == 'Salvar':
                for key in self.timer_values.keys():
                    try:
                        self.timer_values[key] = int(values[key])
                        self.window[f'-TIMER-{key[1:]}-'].update(values[key])
                    except ValueError:
                        sg.popup(f'Valor inválido para {key}. Por favor, insira um número inteiro.')
                sg.popup('Temporizadores atualizados com sucesso.')
                break
        window.close()

    def connect_clp(self):
        if self.serial_port != 'none':
            if comm.estabilishConnection(self.serial_port):
                self.is_connected = self.update_connection_status(True)
            else:
                self.is_connected = self.update_connection_status(False)
                error.errorWindow('Erro!', 'Não foi possível conectar ao dispositivo.')
        else:
            error.errorWindow('Erro!', 'Nenhum dispositivo foi detectado.')

    def run_program(self):
        if self.is_connected:
            self.in_execution = self.update_execution_status(True)
        else:
            error.errorWindow('Erro!', 'Nenhum dispositivo conectado.')

    def stop_program(self):
        self.logical_structure.resetStructure()
        comm.sendLedByte(self.serial_port, b'@00000000#')
        self.update_io_values([False]*8, [False]*8, [False]*32)
        self.in_execution = self.update_execution_status(False)
        self.is_connected = self.update_connection_status(False)

    def show_about(self):
        sg.popup('PLC Programmer\nVersão 1.0\nDesenvolvido por Sua Empresa', title='Sobre')

    def show_help(self):
        program_help.programHelpWindow()

    def execute_cycle(self):
        # Simulação de leitura de entradas
        inputs = [self.window[f'-IN-{i+1}-'].get() for i in range(8)]
        self.logical_structure.updateInputs(inputs)
        # Atualização dos temporizadores
        self.logical_structure.updateTimers(self.timer_values)
        # Atualização das saídas
        outputs = self.logical_structure.updateOutputs(self.timer_values)
        for i, val in enumerate(outputs):
            self.window[f'-OUT-{i+1}-'].update(value=val)
        # Atualização das memórias booleanas
        for i, val in enumerate(self.logical_structure.booleans):
            self.window[f'-BOOL-{i+1}-'].update(value=str(val))
        # Atualização dos temporizadores na interface
        for i in range(32):
            timer_name = f'T{i+1}'
            timer_value = self.logical_structure.timers.get(timer_name, 0)
            self.window[f'-TIMER-{i+1}-'].update(value=str(timer_value))

    def update_io_values(self, inputs, outputs, booleans):
        for i, val in enumerate(inputs):
            self.window[f'-IN-{i+1}-'].update(value=val)
        for i, val in enumerate(outputs):
            self.window[f'-OUT-{i+1}-'].update(value=val)
        for i, val in enumerate(booleans):
            self.window[f'-BOOL-{i+1}-'].update(value=str(val))

    def update_connection_status(self, status):
        self.window['-CONN_STATUS-'].update('Conectado' if status else 'Desconectado', text_color='green' if status else 'red')
        return status

    def update_execution_status(self, status):
        self.window['-EXEC_STATUS-'].update('Executando' if status else 'Parado', text_color='green' if status else 'red')
        return status

if __name__ == '__main__':
    app = PLCProgrammer()
    app.start()
