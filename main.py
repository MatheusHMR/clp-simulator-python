import PySimpleGUI as sg
from views import authors, error, program_help, compile_success, confirm_new, file_controller
import automata.sentence_interpreter as senInt
# from reverse_polish_notation import create_notation, logical_structure
import reverse_polish_notation.create_notation as create_notation
import reverse_polish_notation.logical_structure as logical_structure
import communication as comm
from components.timer import Timer  # Importação corrigida
sg.theme('DarkBlue')  # Adiciona um toque de cor
logicalStructure = logical_structure.LogicalStructure([])  # Cria uma LogicalStructure vazia
inExecution = False
isConnected = False
serialPort = comm.initializeSerial()

# Inicializa os valores dos temporizadores
timerValues = {f'T{i+1}': 0 for i in range(32)}

# Todas as configurações dentro da janela.
menu_def = [['Programa', ['Novo', 'Abrir', 'Salvar']],
            ['Comandos', ['Compilar', 'Configurar Temporizadores']],
            ['CLP', ['Conectar', 'Executar', 'Parar']],
            ['Ajuda', ['Sobre...', 'Programar']],
            ]

# Colunas de layout
input_col = sg.Column([
    [sg.Text('Entradas:')],
    [sg.Text("I1:"), sg.Text('False', key='k_i1_state')],
    [sg.Text("I2:"), sg.Text('False', key='k_i2_state')],
    [sg.Text("I3:"), sg.Text('False', key='k_i3_state')],
    [sg.Text("I4:"), sg.Text('False', key='k_i4_state')],
    [sg.Text("I5:"), sg.Text('False', key='k_i5_state')],
    [sg.Text("I6:"), sg.Text('False', key='k_i6_state')],
    [sg.Text("I7:"), sg.Text('False', key='k_i7_state')],
    [sg.Text("I8:"), sg.Text('False', key='k_i8_state')]
])

output_col = sg.Column([
    [sg.Text('Saídas:')],
    [sg.Text("O1:"), sg.Text('False', key='k_o1_state')],
    [sg.Text("O2:"), sg.Text('False', key='k_o2_state')],
    [sg.Text("O3:"), sg.Text('False', key='k_o3_state')],
    [sg.Text("O4:"), sg.Text('False', key='k_o4_state')],
    [sg.Text("O5:"), sg.Text('False', key='k_o5_state')],
    [sg.Text("O6:"), sg.Text('False', key='k_o6_state')],
    [sg.Text("O7:"), sg.Text('False', key='k_o7_state')],
    [sg.Text("O8:"), sg.Text('False', key='k_o8_state')]
])

boolean_col_left = sg.Column([
    [sg.Text('B1:'), sg.Text('False', key='k_b1_state')],
    [sg.Text('B2:'), sg.Text('False', key='k_b2_state')],
    [sg.Text('B3:'), sg.Text('False', key='k_b3_state')],
    [sg.Text('B4:'), sg.Text('False', key='k_b4_state')],
    [sg.Text('B5:'), sg.Text('False', key='k_b5_state')],
    [sg.Text('B6:'), sg.Text('False', key='k_b6_state')],
    [sg.Text('B7:'), sg.Text('False', key='k_b7_state')],
    [sg.Text('B8:'), sg.Text('False', key='k_b8_state')],
])

boolean_col_right = sg.Column([
    [sg.Text('B9:'), sg.Text('False', key='k_b9_state')],
    [sg.Text('B10:'), sg.Text('False', key='k_b10_state')],
    [sg.Text('B11:'), sg.Text('False', key='k_b11_state')],
    [sg.Text('B12:'), sg.Text('False', key='k_b12_state')],
    [sg.Text('B13:'), sg.Text('False', key='k_b13_state')],
    [sg.Text('B14:'), sg.Text('False', key='k_b14_state')],
    [sg.Text('B15:'), sg.Text('False', key='k_b15_state')],
    [sg.Text('B16:'), sg.Text('False', key='k_b16_state')],
])

left_col = sg.Column([
    [sg.Text('Área de Programação')],
    [sg.Multiline('', size=(50), expand_y=True, key='k_input_area')]
], expand_y=True)

right_col = sg.Column([
    [sg.Text('Informações do CLP')],
    [sg.Text('Não Conectado', key='k_conn_text')],
    [sg.Text('Não Executando', key='k_exec_text')],
    [input_col, output_col],
    [sg.Text('Mem. Booleanas:')],
    [boolean_col_left, boolean_col_right],
], vertical_alignment='top')

# Layout da janela
layout = [[sg.Menu(menu_def)],
          [left_col, right_col]]

# Cria a janela
window = sg.Window('clp-programmer v0.1', layout)

# Funções
def compileProgram(program):  # Compila o programa. Cada linha individual é submetida à verificação de sintaxe
    programLines = program.splitlines()
    errorList = []
    i = 1
    for line in programLines:  # Testa cada linha do programa
        res = senInt.interpretSentece(line)
        if res != 0:
            if res == 1:
                errorList.append(f'Erro de sintaxe linha {i}')
            if res == 2:
                errorList.append(f'Erro de rótulo linha {i}')
        i += 1

    if len(errorList) != 0:  # Lista de erros não está vazia
        error.errorWindow('Erro!', 'Erros de compilação detectados, verifique a ajuda.')
    else:
        polishNotations = []
        for line in programLines:  # Gera uma tupla polonesa para cada linha no programa
            line = line.replace(' ', '')
            line = line.upper()
            newPolish = create_notation.reverse_polish_notation(line)
            identifier = line.split('=')[0]
            polishNotations.append((identifier, newPolish))  # Adiciona a tupla ao array

        logicalStructure.updatePolishNotations(polishNotations)
        print(logicalStructure)
        compile_success.compileSuccessWindow()

def executeProgram():
    byte = comm.readButtons(serialPort)
    string = byte.decode('ascii')
    string = string[1:9]
    print(f'EXEC> {string}')
    if len(string) == 8:
        stringList = list(string)
        i = 0
        while i < len(stringList):
            if stringList[i] == '1':
                stringList[i] = True
            else:
                stringList[i] = False
            i += 1
        logicalStructure.updateInputs(stringList)
        # Aqui passamos os valores dos temporizadores para a estrutura lógica
        outputList = logicalStructure.updateOutputs(timerValues)

        responseString = '@'
        for item in outputList:
            if item == True:
                responseString = responseString + '1'
            else:
                responseString = responseString + '0'

        responseString = responseString + '#'
        encodedString = responseString.encode('utf-8')
        comm.sendLedByte(serialPort, encodedString)
        updateScreenValues(logicalStructure.inputs, logicalStructure.outputs, logicalStructure.booleans)

def updateScreenValues(inputs, outputs, bools):  # Atualiza os valores mostrados na tela
    i = 0
    while i < 8:
        keyInput = f'k_i{i+1}_state'
        keyOutput = f'k_o{i+1}_state'
        window[keyInput].update(inputs[i])
        window[keyOutput].update(outputs[i])
        i += 1

    i = 0
    while i < 16:
        keyBoolean = f'k_b{i+1}_state'
        window[keyBoolean].update(bools[i])
        i += 1

def saveProgram():
    path = file_controller.saveFileWindow()
    program = window['k_input_area'].get()
    print(f'Filepath: {path}')
    try:
        file = open(path, 'w')
        file.write(program)
        file.close()
    except:
        error.errorWindow('Erro!', 'Não foi possivel salvar o arquivo no caminho especificado.')

def openProgram():
    path = file_controller.openFileWindow()
    try:
        file = open(path, 'r')
        program = file.read()
        file.close()
        return program
    except:
        error.errorWindow('Erro!', 'Não foi possível abrir o arquivo especificado.')
        return ''

def setConnected(bool):
    if bool == True:
        window['k_conn_text'].update(f'Conectado ao CLP ({serialPort.port})')
        return True
    else:
        window['k_conn_text'].update('Não Conectado')
        return False

def setExecution(bool):
    if bool == True:
        window['k_exec_text'].update('Em Execução')
        return True
    else:
        window['k_exec_text'].update('Não Executando')
        return False

def configureTimers():
    # Cria o layout para a janela de configuração dos temporizadores
    layout = []
    # Cria colunas para os temporizadores
    timer_columns = []
    timers_per_column = 8
    num_columns = 4

    for col in range(num_columns):
        column_layout = []
        for i in range(timers_per_column):
            timer_num = col * timers_per_column + i + 1
            timer_name = f'T{timer_num}'
            # Adiciona uma linha com um label e um campo de entrada
            current_value = timerValues[timer_name]
            column_layout.append([sg.Text(timer_name), sg.InputText(default_text=str(current_value), key=timer_name, size=(5,1))])
        # Adiciona a coluna à lista de colunas
        timer_columns.append(sg.Column(column_layout, pad=(10,10)))

    # Adiciona as colunas ao layout
    layout.append(timer_columns)

    # Adiciona botões de submissão e cancelamento
    layout.append([sg.Button('Enviar'), sg.Button('Cancelar')])

    # Cria a janela
    window_timers = sg.Window('Configurar Temporizadores', layout)

    # Loop de eventos
    while True:
        event, values = window_timers.read()
        if event == sg.WIN_CLOSED or event == 'Cancelar':
            break
        elif event == 'Enviar':
            # Lê os valores e atualiza os temporizadores
            for timer_name in timerValues.keys():
                preset_value = values.get(timer_name)
                if preset_value is not None and preset_value != '':
                    try:
                        preset_value = int(preset_value)
                        if preset_value < 0:
                            raise ValueError
                        # Atualiza o valor do temporizador em timerValues
                        timerValues[timer_name] = preset_value
                    except ValueError:
                        sg.popup(f'Valor inválido para {timer_name}. Por favor, insira um número inteiro não negativo.')
            sg.popup('Temporizadores atualizados com sucesso.')
            break

    window_timers.close()

# Loop de eventos para processar "eventos" e obter os "valores" das entradas
while True:
    event, values = window.read(timeout=250)  # Aguarda 250ms por um evento
    if event == sg.WIN_CLOSED:  # Se o usuário fechar a janela
        break

    # Respondendo aos comandos no menu da tela
    if event == 'Novo':
        if confirm_new.confirmNewProgram():
            window['k_input_area'].update('')
            inExecution = setExecution(False)
    elif event == 'Abrir':
        print('Abrir')
        window.disappear()
        if confirm_new.confirmNewProgram():
            program = openProgram()
            window['k_input_area'].update(program)
        window.reappear()
    elif event == 'Salvar':
        print('Salvar')
        window.disappear()
        saveProgram()
        window.reappear()
    elif event == 'Compilar':
        print('Compilar')
        setExecution(False)
        program = window['k_input_area'].get()
        if len(program) == 0:
            error.errorWindow('Erro!', 'A área de programação está vazia.')
        else:
            compileProgram(program)
    elif event == 'Configurar Temporizadores':
        print('Configurar Temporizadores')
        window.disappear()
        configureTimers()
        window.reappear()
        # Teste do temporizador
        timer = Timer(name='T1')
        timer.start(delay=timerValues['T1'])

        for cycle in range(timerValues['T1'] + 1):
            timer.update()
            print(f"Ciclo {cycle+1}: Remaining Time = {timer.remaining_time}, Triggered = {timer.triggered}")

    elif event == 'Conectar':
        print('Conectar')
        if serialPort != 'none':
            if comm.estabilishConnection(serialPort) == True:
                isConnected = setConnected(True)
            else:
                isConnected = setConnected(False)
                error.errorWindow('Erro!', 'Não foi possível conectar ao dispositivo')
        else:
            error.errorWindow('Erro!', 'Nenhum dispositivo foi detectado')
    elif event == 'Executar':
        print('Executar')
        if isConnected:
            inExecution = setExecution(True)
        else:
            error.errorWindow('Erro!', 'Não há dispositivo conectado')
    elif event == 'Parar':
        print('Parar')
        logicalStructure.resetStructure()
        comm.sendLedByte(serialPort, b'@00000000#')
        updateScreenValues(logicalStructure.inputs, logicalStructure.outputs, logicalStructure.booleans)
        inExecution = setExecution(False)
        isConnected = setConnected(False)
    elif event == 'Sobre...':
        window.disappear()
        authors.authorsWindow()
        window.reappear()
    elif event == 'Programar':
        window.disappear()
        program_help.programHelpWindow()
        window.reappear()

    if inExecution:
        executeProgram()

window.close()
