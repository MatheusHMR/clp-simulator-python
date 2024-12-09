import re
from components.counter import Counter
from components.timer import Timer

class ScanCycle:
    def __init__(self, logical_structure):
        self.cycles = 0  # Número de ciclos de varredura executados
        # Inicialização de atributos relacionados às entradas, saídas e memórias do PLC
        self.inputs = [False] * 8  # 8 entradas digitais
        self.outputs = [False] * 8  # 8 saídas digitais
        self.memory_image_inputs = [False] * 8  # Memória imagem das entradas
        self.memory_image_outputs = [False] * 8  # Memória imagem das saídas
        self.boolean_memories = [False] * 32  # Memórias booleanas locais (32)
        self.logical_structure = logical_structure

        # Dicionários de Temporizadores e Contadores
        self.timers = {
            f"T{i+1}": Timer(name=f"T{i+1}") for i in range(32)
        }  # Temporizadores T1, T2, ..., T32

        self.counters = {
            f"C{i+1}": Counter(name=f"C{i+1}", counter_type='UP') for i in range(8)
        }  # Contadores C1, C2, ..., C8

        self.mode = 'STOP'  # Modo inicial do PLC
        self.user_program = []  # Lista para armazenar o programa do usuário

        # Para detecção de bordas em contadores
        self.counter_coils = {}       # Estado atual das bobinas CUPx/CDNx
        self.prev_counter_coils = {}  # Estado anterior das bobinas CUPx/CDNx

    def initialize_system(self):
        """
        Inicializa o sistema, resetando memórias e timers.
        """
        print("Inicializando o sistema...")
        self.cycles = 0
        self.memory_image_inputs = [False] * len(self.memory_image_inputs)
        self.memory_image_outputs = [False] * len(self.memory_image_outputs)
        self.boolean_memories = [False] * len(self.boolean_memories)
        for timer in self.timers.values():
            timer.preset = 0
            timer.remaining_time = 0
            timer.isActive = False
            timer.triggered = False
            timer.type = 'ON DELAY'  # default, pode ser alterado depois
        for counter in self.counters.values():
            counter.count = 0
        print("Sistema inicializado com sucesso.")

    def read_inputs(self):
        """
        Lê o estado das entradas e armazena na memória imagem.
        """
        if self.mode == 'RUN':
            self.memory_image_inputs = self.inputs.copy()

    def process_user_program(self):
        """
        Processa o programa do usuário e aplica a lógica às saídas usando RPN.
        """
        if self.mode == 'RUN':
            for line in self.user_program:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue  # Pule linhas vazias ou comentários
                if '=' not in line:
                    print(f"Linha inválida: {line}")
                    continue
                identifier, expression = line.split('=', 1)
                identifier = identifier.strip()
                expression = expression.strip()
                rpn_instructions = self._convert_to_rpn(expression)
                # Adiciona o identificador para definir a saída ou memória no final
                rpn_instructions.append(identifier)
                self._execute_rpn(rpn_instructions)

    def update_outputs(self):
        """
        Atualiza as saídas físicas ou simuladas a partir da memória imagem.
        """
        if self.mode == 'RUN':
            self.outputs = self.memory_image_outputs.copy()

    def update_timers(self):
        """
        Atualiza o estado de todos os temporizadores.
        """
        for timer in self.timers.values():
            timer.update()

    def increment_counter(self, counter_name):
        """
        Incrementa o contador especificado.
        """
        if counter_name in self.counters:
            self.counters[counter_name].increment()

    def decrement_counter(self, counter_name):
        """
        Decrementa o contador especificado.
        """
        if counter_name in self.counters:
            self.counters[counter_name].decrement()

    def start_timer(self, timer_name, delay, timer_type='ON DELAY'):
        """
        Inicia um temporizador com um delay especificado.
        """
        if timer_name in self.timers:
            timer = self.timers[timer_name]
            timer.start(delay)
            timer.type = timer_type

    def scan(self):
        """
        Executa um ciclo completo de varredura do PLC.
        """
        if self.mode == 'RUN':
            self.read_inputs()
            self.update_timers()  # Atualiza temporizadores
            self.process_user_program()
            # Após processar o programa, analisar bobinas de contadores
            self._process_counters_coils()
            self.update_outputs()
            self.cycles += 1
            # Atualiza estado anterior dos contadores
            self.prev_counter_coils = self.counter_coils.copy()

    def set_mode(self, mode):
        """
        Altera o modo de operação do PLC (RUN, STOP, PROGRAM).
        """
        if mode in ['RUN', 'STOP', 'PROGRAM']:
            self.mode = mode
            print(f"Modo alterado para: {self.mode}")
        else:
            print("Modo inválido. Modos válidos: RUN, STOP, PROGRAM.")

    def _process_counters_coils(self):
        """
        Verifica todos os contadores definidos em counter_coils e detecta bordas de subida.
        Incrementa ou decrementa o contador correspondente com base no tipo (CUP ou CDN).
        """
        for coil_name, current_state in self.counter_coils.items():
            previous_state = self.prev_counter_coils.get(coil_name, False)
            # Detectar borda de subida
            if not previous_state and current_state:
                match = re.match(r'^(CUP|CDN)(\d+)$', coil_name.upper())
                if match:
                    coil_type = match.group(1)  # CUP ou CDN
                    coil_num = match.group(2)
                    counter_name = f"C{coil_num}"
                    if counter_name in self.counters:
                        if coil_type == 'CUP':
                            self.counters[counter_name].increment()
                        elif coil_type == 'CDN':
                            self.counters[counter_name].decrement()

    def _get_value(self, token):
        """
        Retorna o valor associado a um token (entradas, memórias, timers, etc.).
        """
        token_upper = token.upper()

        # Verifica padrões para temporizadores contato
        # Contato: TONOx ou TOFOx
        contact_pattern = r'^(TON|TOF)O(\d+)$'
        contact_match = re.match(contact_pattern, token_upper)
        if contact_match:
            timer_type = contact_match.group(1)
            timer_num = contact_match.group(2)
            timer_name = f"T{timer_num}"
            timer = self.timers.get(timer_name)
            if not timer:
                raise ValueError(f"Temporizador desconhecido: {timer_name}")
            # Contato retorna estado triggered
            return timer.triggered

        # Bobina de temporizador: TONx ou TOFx
        coil_pattern = r'^(TON|TOF)(\d+)$'
        coil_match = re.match(coil_pattern, token_upper)
        if coil_match:
            # Bobina não é valor lógico de leitura, é um comando (feita em _execute_rpn)
            raise ValueError(f"O token {token} representa uma bobina de temporizador e não pode ser lido como valor.")

        # Padrões para contadores (CUPx, CUPOx, CDNx, CDNOx)
        counter_pattern = r'^(CUP|CDN)(O?)(\d+)$'
        counter_match = re.match(counter_pattern, token_upper)
        if counter_match:
            counter_type = counter_match.group(1)  # CUP ou CDN
            output_requested = (counter_match.group(2) == 'O')
            counter_num = counter_match.group(3)
            counter_name = f"C{counter_num}"
            counter = self.counters.get(counter_name)
            if not counter:
                raise ValueError(f"Contador desconhecido: {counter_name}")
            # Se for CUPO ou CDNO, retornamos True se count > 0
            return (counter.count > 0)

        # Entradas (I)
        if token_upper.startswith("I") and token_upper[1:].isdigit():
            index = int(token_upper[1:]) - 1
            return self.memory_image_inputs[index]

        # Saídas (O)
        if token_upper.startswith("O") and token_upper[1:].isdigit():
            index = int(token_upper[1:]) - 1
            return self.memory_image_outputs[index]

        # Memórias Booleanas (B)
        if token_upper.startswith("B") and token_upper[1:].isdigit():
            index = int(token_upper[1:]) - 1
            return self.boolean_memories[index]

        raise ValueError(f"Token desconhecido: {token}")

    def _set_output(self, token, value):
        """
        Define o valor de uma saída (O) ou memória (B).
        """
        token_upper = token.upper()
        if token_upper.startswith("O"):
            index = int(token_upper[1:]) - 1
            self.memory_image_outputs[index] = value
        elif token_upper.startswith("B"):
            index = int(token_upper[1:]) - 1
            self.boolean_memories[index] = value
        else:
            raise ValueError(f"Token de saída desconhecido: {token}")

    def _convert_to_rpn(self, expression):
        """
        Converte uma expressão lógica em RPN usando um algoritmo tipo Shunting Yard simplificado.
        """
        expression = expression.replace(' ', '')
        token_pattern = r'(\bNOT\b|\(|\)|\^|\||\b[A-Za-z][A-Za-z0-9]*\b)'
        tokens = re.findall(token_pattern, expression)
        output_queue = []
        operator_stack = []
        precedence = {'NOT': 3, '^': 2, '|': 1}
        associativity = {'NOT': 'right', '^': 'left', '|': 'left'}

        for token in tokens:
            token_upper = token.upper()
            if token_upper in precedence:
                while (operator_stack and operator_stack[-1] != '(' and
                       ((associativity[token_upper] == 'left' and precedence[token_upper] <= precedence[operator_stack[-1]]) or
                        (associativity[token_upper] == 'right' and precedence[token_upper] < precedence[operator_stack[-1]]))):
                    output_queue.append(operator_stack.pop())
                operator_stack.append(token_upper)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output_queue.append(operator_stack.pop())
                operator_stack.pop()  # Remove '('
            else:
                output_queue.append(token_upper)
        while operator_stack:
            output_queue.append(operator_stack.pop())

        return output_queue

    def _execute_rpn(self, rpn_instructions):
        """
        Executa as instruções em RPN e atualiza as saídas.
        Diferencia bobinas e contatos de timers, e registra bobinas de contadores.
        """
        stack = []
        for token in rpn_instructions:
            token_upper = token.upper()

            coil_pattern_timer = r'^(TON|TOF)(\d+)$'
            coil_match_timer = re.match(coil_pattern_timer, token_upper)

            contact_pattern_timer = r'^(TON|TOF)O(\d+)$'
            contact_match_timer = re.match(contact_pattern_timer, token_upper)

            coil_pattern_counter = r'^(CUP|CDN)(\d+)$'
            coil_match_counter = re.match(coil_pattern_counter, token_upper)

            if token_upper in ['^', '|', 'NOT']:
                # Operadores lógicos
                if token_upper == 'NOT':
                    operand = stack.pop()
                    stack.append(not operand)
                else:
                    operand2 = stack.pop()
                    operand1 = stack.pop()
                    if token_upper == '^':  # AND
                        result = operand1 and operand2
                    else:  # '|'
                        result = operand1 or operand2
                    stack.append(result)

            elif contact_match_timer:
                # Contato de timer (ex: TONO1, TOFO1)
                value = self._get_value(token_upper)
                stack.append(value)

            elif coil_match_timer:
                # Bobina de timer (ex: TON1, TOF1)
                coil_value = stack.pop()
                timer_type = coil_match_timer.group(1)
                timer_num = coil_match_timer.group(2)
                timer_name = f"T{timer_num}"
                self._set_timer(timer_name, timer_type, coil_value)

            elif coil_match_counter:
                # Bobina de contador (CUPx ou CDNx)
                coil_value = stack.pop()
                coil_type = coil_match_counter.group(1)  # CUP ou CDN
                coil_num = coil_match_counter.group(2)
                coil_full_name = f"{coil_type.upper()}{coil_num}"
                # Armazena o estado dessa bobina no ciclo atual
                self.counter_coils[coil_full_name] = coil_value

            elif token_upper.startswith('O') or token_upper.startswith('M'):
                # É uma saída ou memória
                value = stack.pop()
                self._set_output(token_upper, value)

            else:
                # Operando (entrada, memória, contador contato, etc.)
                value = self._get_value(token_upper)
                stack.append(value)

    def _set_timer(self, timer_name, timer_type, coil_value):
        """
        Ajusta o estado do temporizador conforme a bobina recebida.
        """
        timer = self.timers.get(timer_name)
        if not timer:
            raise ValueError(f"Temporizador desconhecido: {timer_name}")

        # Ajusta o tipo do temporizador baseado no token
        if timer_type == "TON":
            timer.type = 'ON DELAY'
        elif timer_type == "TOF":
            timer.type = 'OFF DELAY'

        if coil_value:
            # Se a bobina estiver energizada
            if not timer.isActive and not timer.triggered:
                # Reinicia o timer se não estava ativo
                timer.start(timer.preset)
        else:
            # Desenergiza a bobina
            if timer.type == 'ON DELAY':
                # ON DELAY resetado se bobina desligada
                timer.isActive = False
                timer.remaining_time = timer.preset
                timer.triggered = False
            elif timer.type == 'OFF DELAY':
                # Para OFF DELAY, ao desligar a bobina, o timer continua até terminar o delay
                if not timer.isActive:
                    # Se não estava ativo, pode-se iniciar o timer para OFF DELAY aqui
                    timer.start(timer.preset)
                # Se já estava ativo, apenas continua contando até o final.
                pass
