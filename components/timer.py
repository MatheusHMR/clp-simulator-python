# Class Timer

class Timer:
    def __init__(self, name="T1", preset=0, timer_type='ON DELAY'):
        self.name = name
        self.preset = preset  # Preset value for delay time
        self.remaining_time = 0  # Time remaining for the current countdown
        self.isActive = False
        self.type = timer_type
        self.triggered = False

    def start(self, delay):
        """
        Starts the timer with the specified delay.
        """
        self.preset = delay  # Set the preset time
        self.remaining_time = delay  # Set the remaining time to preset value
        self.isActive = True
        self.triggered = False if self.type == 'ON DELAY' else True
        print(f"Started {self.type} timer {self.name} with delay {delay * 0.1} seconds.")

    def update(self):
        """
        Updates the timer countdown.
        """
        if self.isActive and self.remaining_time > 0:
            self.remaining_time -= 1
            print(f"Timer ({self.type}) countdown: {self.remaining_time * 0.1}s remaining.")

            # Check if the timer has reached zero
            if self.remaining_time == 0:
                self.isActive = False
                if self.type == 'ON DELAY':
                    self.triggered = True
                    print(f"ON DELAY of Timer {self.name} completed. Activating output.")
                elif self.type == 'OFF DELAY':
                    self.triggered = False
                    print(f"OFF DELAY of Timer {self.name} completed. Deactivating output.")

