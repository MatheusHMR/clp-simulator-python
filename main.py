import PySimpleGUI as sg
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
    def __init__(self):
        self.scan_cycle = ScanCycle(logical_structure=logical_structure.LogicalStructure([]))
        self.in_execution = False
        self.is_connected = False
        self.serial_port = comm.initializeSerial()

        # Dicionário para armazenar os valores de preset dos timers
        self.timer_values = {f'T{i+1}': 0 for i in range(32)}
        # Dicionário para armazenar os valores de preset dos contadores
        self.counter_values = {f'C{i+1}': 0 for i in range(8)}

        self.setup_gui()

    def setup_gui(self):
        sg.theme('DarkBlue14')
        menu_layout = [
            ['Arquivo', ['Novo      Ctrl+N', 'Abrir     Ctrl+O', 'Salvar    Ctrl+S', '---', 'Sair']],
            ['Ferramentas', ['Compilar  F9', 'Configurar Temporizadores', 'Configurar Contadores']],
            ['CLP', ['Conectar', 'Executar  F5', 'Parar']],
            ['Ajuda', ['Sobre', 'Como Programar']],
        ]

        toolbar = [
            sg.Button('🗎 Novo', tooltip='Novo (Ctrl+N)', key='Novo'),
            sg.Button('📂 Abrir', tooltip='Abrir (Ctrl+O)', key='Abrir'),
            sg.Button('💾 Salvar', tooltip='Salvar (Ctrl+S)', key='Salvar'),
            sg.Button('🔄 Compilar', tooltip='Compilar (F9)', key='Compilar'),
            sg.Button('▶ Executar', tooltip='Executar (F5)', key='Executar'),
            sg.Button('⏹ Parar', tooltip='Parar', key='Parar'),
            sg.Button('⚙ Configurar Temporizadores', tooltip='Defina o valor do timer em múltiplos de 0.1s (ex: 100 = 10s)', key='Configurar Temporizadores'),
            sg.Button('⚙ Configurar Contadores', tooltip='Defina o valor do contador (inteiro) que ele deve contar até atingir', key='Configurar Contadores'),
            sg.Button('🔌 Conectar', tooltip='Conectar', key='Conectar'),
            sg.Button('❓ Ajuda', tooltip='Ajuda', key='Sobre'),
        ]

        programming_area = sg.Frame('', [
            [sg.Multiline('', size=(80, 25), key='-PROGRAM-', font='Consolas 12', autoscroll=True, expand_x=True, expand_y=True)]
        ], relief=sg.RELIEF_SUNKEN)

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

        layout = [
            [sg.Menu(menu_layout)],
            toolbar,
            [sg.Pane([programming_area, plc_viewer], orientation='h', relief=sg.RELIEF_RIDGE, expand_x=True, expand_y=True)]
        ]

        self.window = sg.Window('PLC Programmer', layout, finalize=True, resizable=True)

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
            elif event in ('Novo', 'Abrir', 'Salvar', 'Compilar', 'Configurar Temporizadores', 'Configurar Contadores', 'Conectar', 'Executar', 'Parar', 'Sobre', 'Como Programar'):
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
        elif event == 'Configurar Contadores':
            self.configure_counters()
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
        index = int(event.replace('-IN-', '').replace('-', '')) - 1
        self.scan_cycle.inputs[index] = values[event]
        self.scan_cycle.memory_image_inputs[index] = values[event]

    def new_program(self):
        if confirm_new.confirmNewProgram():
            self.window['-PROGRAM-'].update('')
            self.in_execution = self.update_execution_status(False)
            self.scan_cycle.initialize_system()

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
            res = senInt.interpretSentence(line)
            if res == 1:
                errors.append(f'Erro de sintaxe na linha {idx + 1}')
            elif res == 2:
                errors.append(f'Erro de rótulo na linha {idx + 1}')
        if errors:
            error.errorWindow('Erro!', '\n'.join(errors))
        else:
            self.scan_cycle.user_program = program_lines
            compile_success.compileSuccessWindow()

    def configure_timers(self):
        timer_layout = [
            [sg.Text(f'T{i+1}:', size=(5, 1)), 
             sg.InputText(self.timer_values[f'T{i+1}'], key=f'T{i+1}', size=(5, 1))]
            for i in range(32)
        ]
        layout = [
            [sg.Text('Temporizadores contam valores inteiros em múltiplos de 0.1s', tooltip='Temporizadores contam valores inteiros em múltiplos de 0.1s')],
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
                        self.scan_cycle.timers[key].preset = int(values[key])
                    except ValueError:
                        sg.popup(f'Valor inválido para {key}. Por favor, insira um número inteiro.')
                sg.popup('Temporizadores atualizados com sucesso.')
                break
        window.close()

    def configure_counters(self):
        counter_layout = [
            [sg.Text(f'C{i+1}:', size=(5, 1)), 
             sg.InputText(self.counter_values[f'C{i+1}'], key=f'C{i+1}', size=(5, 1))]
            for i in range(8)
        ]
        layout = [
            [sg.Text('Contadores contam valores inteiros até atingir o preset', tooltip='Contadores contam valores inteiros até atingir o preset')],
            [sg.Column(counter_layout, scrollable=True, vertical_scroll_only=True, size=(250, 200))],
            [sg.Button('Salvar'), sg.Button('Cancelar')]
        ]
        window = sg.Window('Configurar Contadores', layout, modal=True)
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Cancelar'):
                break
            elif event == 'Salvar':
                for key in self.counter_values.keys():
                    try:
                        self.counter_values[key] = int(values[key])
                        self.scan_cycle.counters[key].preset = self.counter_values[key]
                    except ValueError:
                        sg.popup(f'Valor inválido para {key}. Por favor, insira um número inteiro.')
                sg.popup('Contadores atualizados com sucesso.')
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
        self.scan_cycle.set_mode('RUN')
        self.in_execution = self.update_execution_status(True)

    def stop_program(self):
        self.scan_cycle.set_mode('STOP')
        self.scan_cycle.initialize_system()
        self.update_io_values([False]*8, [False]*8, [False]*32)
        self.in_execution = self.update_execution_status(False)
        self.is_connected = self.update_connection_status(False)

    def show_about(self):
        sg.popup('PLC Programmer\nVersão 1.0\nDesenvolvido por:\nEmanuel Carlos de Mello\nFúlvio Diniz Santos\nGilmar dos Reis Júnior\nMatheus Henrique Maia Ramos\nBaseado no trabalho de Nathan Rodrigues', title='Sobre')

    def show_help(self):
        program_help.programHelpWindow()

    def execute_cycle(self):
        inputs = [self.window[f'-IN-{i+1}-'].get() for i in range(8)]
        self.scan_cycle.inputs = inputs
        self.scan_cycle.read_inputs()
        self.scan_cycle.update_timers()
        self.scan_cycle.process_user_program()
        self.scan_cycle.update_outputs()
        for i, val in enumerate(self.scan_cycle.outputs):
            self.window[f'-OUT-{i+1}-'].update(value=val)
        for i, val in enumerate(self.scan_cycle.boolean_memories):
            self.window[f'-BOOL-{i+1}-'].update(value=str(val))
        for i in range(32):
            timer_name = f'T{i+1}'
            timer_value = self.scan_cycle.timers[timer_name].remaining_time
            self.window[f'-TIMER-{i+1}-'].update(value=str(timer_value))

    def update_io_values(self, inputs, outputs, booleans):
        for i, val in enumerate(inputs):
            self.window[f'-IN-{i+1}-'].update(value=val)
            self.scan_cycle.inputs[i] = val
            self.scan_cycle.memory_image_inputs[i] = val
        for i, val in enumerate(outputs):
            self.window[f'-OUT-{i+1}-'].update(value=val)
            self.scan_cycle.outputs[i] = val
            self.scan_cycle.memory_image_outputs[i] = val
        for i, val in enumerate(booleans):
            self.window[f'-BOOL-{i+1}-'].update(value=str(val))
            self.scan_cycle.boolean_memories[i] = val

    def update_connection_status(self, status):
        self.window['-CONN_STATUS-'].update('Conectado' if status else 'Desconectado', text_color='green' if status else 'red')
        return status

    def update_execution_status(self, status):
        self.window['-EXEC_STATUS-'].update('Executando' if status else 'Parado', text_color='green' if status else 'red')
        return status


if __name__ == '__main__':
    app = PLCProgrammer()
    app.start()
