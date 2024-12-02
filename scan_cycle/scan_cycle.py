import re
from components.counter import Counter
from components.timer import Timer

class ScanCycle:
    def __init__(self):
        self.cycles = 0  # Número de ciclos de varredura executados
        # Inicialização de atributos relacionados às entradas, saídas e memórias do PLC
        self.inputs = [False] * 8  # Supondo 8 entradas digitais
        self.outputs = [False] * 8  # Supondo 8 saídas digitais
        self.memory_image_inputs = [False] * 8  # Memória imagem das entradas
        self.memory_image_outputs = [False] * 8  # Memória imagem das saídas
        self.boolean_memories = [False] * 32  # Memórias booleanas locais (32)

        # Dicionários de Temporizadores e Contadores
        self.timers = {
            f"T{i+1}": Timer(name=f"T{i+1}") for i in range(32)
        }  # Temporizadores nomeados T1, T2, ..., T32

        self.counters = {
            f"C{i+1}": Counter(name=f"C{i+1}", counter_type='UP') for i in range(8)
        }  # Contadores nomeados C1, C2, ..., C8

        self.mode = 'STOP'  # Modo inicial do PLC
        self.user_program = []  # Lista para armazenar o programa do usuário

    def initialize_system(self):
        """
        Inicializa o sistema, configurando memórias e estados iniciais.
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
        for counter in self.counters.values():
            counter.count = 0
        print("Sistema inicializado com sucesso.")

    def read_inputs(self):
        """
        Lê o estado das entradas e armazena na memória imagem das entradas.
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
                    continue  # Pula linhas vazias ou comentários
                if '=' not in line:
                    print(f"Linha inválida: {line}")
                    continue
                identifier, expression = line.split('=', 1)
                identifier = identifier.strip()
                expression = expression.strip()
                rpn_instructions = self._convert_to_rpn(expression)
                # Adiciona o identificador para definir a saída ou memória
                rpn_instructions.append(identifier)
                self._execute_rpn(rpn_instructions)

    def update_outputs(self):
        """
        Atualiza o estado das saídas físicas ou simuladas a partir da memória imagem das saídas.
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

    def start_timer(self, timer_name, delay, timer_type='ON DELAY'):
        """
        Inicia um temporizador com um atraso especificado (ON DELAY ou OFF DELAY).
        """
        if timer_name in self.timers:
            timer = self.timers[timer_name]
            timer.preset = delay
            timer.type = timer_type
            timer.isActive = True
            timer.triggered = False

    def scan(self):
        """
        Executa o ciclo completo de varredura do PLC.
        """
        if self.mode == 'RUN':
            self.read_inputs()
            self.update_timers()  # Atualiza os temporizadores como parte de cada ciclo de varredura
            self.process_user_program()
            self.update_outputs()
            self.cycles += 1

    def set_mode(self, mode):
        """
        Altera o modo de operação do PLC (RUN, STOP, PROGRAM).
        """
        if mode in ['RUN', 'STOP', 'PROGRAM']:
            self.mode = mode
            print(f"Modo alterado para: {self.mode}")
        else:
            print("Modo inválido. Modos válidos: RUN, STOP, PROGRAM.")

    def _get_value(self, token):
        """
        Retorna o valor associado a um token (IN1, I1, M1, T1, etc.).
        """
        token_upper = token.upper()
        if token_upper.startswith("IN") or token_upper.startswith("I"):
            index_str = token_upper.lstrip("IN").lstrip("I")
            if index_str.isdigit():
                index = int(index_str) - 1
                return self.memory_image_inputs[index]
            else:
                raise ValueError(f"Token de entrada inválido: {token}")
        elif token_upper.startswith("M"):
            index = int(token_upper[1:]) - 1
            return self.boolean_memories[index]
        elif token_upper.startswith("T"):
            timer_name = token_upper
            timer = self.timers.get(timer_name)
            if timer:
                return timer.triggered
            else:
                raise ValueError(f"Temporizador desconhecido: {token}")
        elif token_upper.startswith("O"):
            index = int(token_upper[1:]) - 1
            return self.memory_image_outputs[index]
        else:
            raise ValueError(f"Token desconhecido: {token}")

    def _set_output(self, token, value):
        """
        Define o valor de uma saída (O1, O2, etc.) ou memória (M1, M2, etc.).
        """
        token_upper = token.upper()
        if token_upper.startswith("O"):
            index = int(token_upper[1:]) - 1
            self.memory_image_outputs[index] = value
        elif token_upper.startswith("M"):
            index = int(token_upper[1:]) - 1
            self.boolean_memories[index] = value
        else:
            raise ValueError(f"Token de saída desconhecido: {token}")

    def _convert_to_rpn(self, expression):
        """
        Converte uma expressão lógica em Notação Polonesa Reversa (RPN) usando o algoritmo Shunting Yard.
        """
        # Remover espaços em branco
        expression = expression.replace(' ', '')
        # Definir o padrão regex para tokenização
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
        """
        stack = []
        for token in rpn_instructions:
            token_upper = token.upper()
            if token_upper in ['^', '|', 'NOT']:
                if token_upper == 'NOT':
                    operand = stack.pop()
                    result = not operand
                    stack.append(result)
                else:
                    operand2 = stack.pop()
                    operand1 = stack.pop()
                    if token_upper == '^':
                        result = operand1 and operand2
                    elif token_upper == '|':
                        result = operand1 or operand2
                    stack.append(result)
            elif token_upper.startswith('O') or token_upper.startswith('M'):
                # É uma saída ou memória, define seu valor
                value = stack.pop()
                self._set_output(token_upper, value)
            else:
                # É um operando, empurra seu valor na pilha
                value = self._get_value(token_upper)
                stack.append(value)
