# Class Counter

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
        Increments the counter value.
        """
        if self.type == 'UP':
            self.count += 1
            print(f"Counter {self.name} incremented to {self.count}.")
            # Check if the counter has reached the preset value
            if self.count >= self.preset:
                print(f"Counter {self.name} reached the preset value {self.preset}.")

    def decrement(self):
        """
        Decrements the counter value.
        """
        if self.type == 'DOWN':
            self.count -= 1
            print(f"Counter {self.name} decremented to {self.count}.")
            # Check if the counter has reached zero or the preset value
            if self.count <= self.preset:
                print(f"Counter {self.name} reached the preset value {self.preset}.")
