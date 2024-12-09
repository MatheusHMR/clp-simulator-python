
class Counter:
    def __init__(self, name="C1", preset=0, counter_type='UP'):
        self.name = name
        self.count = 0  # Current count value
        self.preset = preset  # Preset value for the counter
        self.type = counter_type

    def start(self, preset):
        """
        Sets the preset value and initializes the counter.
        """
        self.preset = preset
        self.count = 0  # Reset the count when starting
        print(f"Started {self.type} counter {self.name} with preset {preset}.")

    def increment(self):
        """
        Increments the counter value if type is 'UP'.
        """
        if self.type == 'UP':
            self.count += 1
            print(f"Counter {self.name} incremented to {self.count}.")
            # Check if the counter has reached the preset value
            if self.count >= self.preset:
                print(f"Counter {self.name} reached the preset value {self.preset}.")

    def decrement(self):
        """
        Decrements the counter value if type is 'DOWN'.
        """
        if self.type == 'DOWN':
            self.count -= 1
            print(f"Counter {self.name} decremented to {self.count}.")
            # Check if the counter has reached or gone below the preset value
            if self.count <= self.preset:
                print(f"Counter {self.name} reached the preset value {self.preset}.")

    @property
    def triggered(self):
        """
        Returns True if the counter has reached or passed the preset.
        For an UP counter: True if count >= preset.
        For a DOWN counter: True if count <= preset.
        If preset is 0 and it's an UP counter, True means count >= 0 (praticamente sempre True após iniciar).
        Ajuste conforme sua necessidade.
        """
        if self.type == 'UP':
            return self.count >= self.preset
        elif self.type == 'DOWN':
            return self.count <= self.preset
        else:
            # Caso futuramente haja outro tipo de contador, retorne False ou implemente a lógica desejada
            return False