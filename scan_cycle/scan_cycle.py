from components.counter import Counter
from components.timer import Timer

class ScanCycle:
    def __init__(self):
        self.cycles = 0 # Number of scan cycles executed
        # Initialization of attributes related to PLC inputs, outputs, and memories
        self.inputs = [False] * 8  # Assuming 8 digital inputs
        self.outputs = [False] * 8  # Assuming 8 digital outputs
        self.memory_image_inputs = [False] * 8  # Input image memory
        self.memory_image_outputs = [False] * 8  # Output image memory
        self.boolean_memories = [False] * 32  # Local boolean memories (32)

        # Timers and Counters dictionaries
        self.timers = {
            f"T{i+1}": Timer(name=f"T{i+1}") for i in range(8)
        }  # Timers named T1, T2, ..., T8

        self.counters = {
            f"C{i+1}": Counter(name=f"C{i+1}", counter_type='UP') for i in range(8)
        }  # Counters named C1, C2, ..., C8

        self.mode = 'STOP'  # Initial mode of the PLC

    def initialize_system(self):
        """
        Initializes the system, configuring memories and initial states.
        """
        print("Initializing the system...")
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
        print("System initialized successfully.")

    def read_inputs(self):
        """
        Reads the state of the inputs and stores it in the input image memory.
        """
        if self.mode == 'RUN':
            print("Reading inputs...")
            self.memory_image_inputs = self.inputs.copy()
            print(f"Inputs read: {self.memory_image_inputs}")

    def process_user_program(self):
        """
        Processes the user program and applies the logic to the outputs using RPN.
        """
        if self.mode == 'RUN':
            print("Processing the user program...")
            # TODO: Add logic for AND, OR, NOT, counters, timers, etc.

            rpn_instructions = [
            "IN1", "M1", "AND", "T1", "OR", "O1"
            ]
                # Pilha para armazenar operandos durante a avaliação
        stack = []

        # Loop através dos elementos da RPN
        for token in rpn_instructions:
            if token.startswith("IN") or token.startswith("M") or token.startswith("T"):
                # Caso seja um operando (entrada, memória ou temporizador)
                value = self._get_value(token)
                stack.append(value)

            elif token in ["AND", "OR", "NOT"]:
                # Caso seja um operador, desempilhar operandos e aplicar operação
                if token == "NOT":
                    # NOT precisa de apenas um operando
                    operand = stack.pop()
                    result = not operand
                    stack.append(result)
                else:
                    # AND e OR precisam de dois operandos
                    operand2 = stack.pop()
                    operand1 = stack.pop()
                    if token == "AND":
                        result = operand1 and operand2
                    elif token == "OR":
                        result = operand1 or operand2
                    stack.append(result)

            elif token.startswith("OUT"):
                # Caso seja uma saída, armazenar o valor atual da pilha na saída especificada
                output_value = stack.pop()
                self._set_output(token, output_value)

        print(f"Output image memory after processing: {self.memory_image_outputs}")

    def update_outputs(self):
        """
        Updates the state of the physical or simulated outputs from the output image memory.
        """
        if self.mode == 'RUN':
            print("Updating outputs...")
            self.outputs = self.memory_image_outputs.copy()
            print(f"Outputs updated: {self.outputs}")

    def update_timers(self):
        """
        Updates the state of all timers.
        """
        for timer in self.timers.values():
            timer.update()

    def increment_counter(self, counter_name):
        """
        Increments the specified counter.
        """
        if counter_name in self.counters:
            self.counters[counter_name].increment()

    def start_timer(self, timer_name, delay, timer_type='ON DELAY'):
        """
        Starts a timer with a specified delay (ON DELAY or OFF DELAY).
        """
        if timer_name in self.timers:
            self.timers[timer_name].start(delay)
            self.timers[timer_name].type = timer_type
            print(f"Started {timer_type} timer {timer_name} with delay {delay * 0.1} seconds.")

    def scan(self):
        """
        Executes the complete PLC scan cycle.
        """
        if self.mode == 'RUN':
            print("Starting PLC scan cycle...")
            self.read_inputs()
            self.process_user_program()
            self.update_timers()  # Update timers as part of each scan cycle
            self.update_outputs()
            self.cycles += 1
            print(f"Scan cycle completed. Made {self.cycles} cycles already. Returning to the beginning of the cycle...\n")

    def set_mode(self, mode):
        """
        Changes the PLC operation mode (RUN, STOP, PROGRAM).
        """
        if mode in ['RUN', 'STOP', 'PROGRAM']:
            self.mode = mode
            print(f"Changed mode to: {self.mode}")
        else:
            print("Invalid mode. Valid modes: RUN, STOP, PROGRAM.")


# Example of usage
if __name__ == "__main__":
    scan_cycle = ScanCycle()
    scan_cycle.initialize_system()

    # Simulating inputs
    scan_cycle.set_mode('RUN')
    scan_cycle.inputs = [True, False, True, False, True, True, False, False]

    # Start ON DELAY timer T1 with a delay of 5 cycles (0.5 seconds)
    scan_cycle.start_timer("T1", 5, 'ON DELAY')
    # Start OFF DELAY timer T2 with a delay of 8 cycles (0.8 seconds)
    scan_cycle.start_timer("T2", 8, 'OFF DELAY')

    # Executing the scan cycle multiple times to observe timer behavior
    for _ in range(10):
        scan_cycle.scan()
