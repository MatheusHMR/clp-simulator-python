from .resolve_notation import resolve

class LogicalStructure:
    polishNotations = []
    inputs = [False]*8
    outputs = [False]*8
    booleans = [False]*8
    timers_on = [False]*8
    timers_on_out= [False]*8
    timers_of = [False]*8
    timers_of_out = [False]*8
    counter_up = [False]*8
    counter_up_out = [False]*8
    counter_dn = [False]*8
    counter_dn_out = [False]*8

    def __init__(self, polishNotations):
        self.polishNotations = polishNotations

    def __str__(self):
        return f'LogicalStructure: [inputs: {self.inputs}, outputs: {self.outputs}, polishNotations: {self.polishNotations}'
    
    def updateOutputs(self):
        for polishTuple in self.polishNotations:
            identifier = polishTuple[0]
            polish = polishTuple[1]
            resolvedValue = resolve(polish, self.inputs, self.outputs, self.booleans, self.timers_on, self.timers_on_out, self.timers_of, self.timers_of_out, self.counter_up, self.counter_up_out, self.counter_dn, self.counter_dn_out)
            print(f"\t>RESOLVING: identifier:{identifier} polish:{polish} resolvedValue:{resolvedValue}")
            address = int(identifier[1]) - 1
            if(identifier[0] == 'O'):
                self.outputs[address] = resolvedValue
            elif(identifier[0] == 'B'):
                self.booleans[address] = resolvedValue
        print(f"Outputs updated in LogicalStructure, outputs: {self.outputs}")
        return self.outputs

    def clearPolish(self):
        self.polishNotations.clear()
        print("Polish notations cleared in LogicalStructure")

    def updatePolishNotations(self, polishNotations):
        self.clearPolish()
        self.polishNotations = polishNotations
        print(f"Polish notations updated in LogicalStructure, polishNotations: {self.polishNotations}")

    def updateInputs(self, inputs):
        self.inputs = inputs
        print(f"Inputs updated in LogicalStructure, inputs: {self.inputs}")

    def updateBooleans(self, booleans):
        self.booleans = booleans
        print(f"Booleans updated in LogicalStructure, booleans: {self.booleans}")

    def updateTimersOn(self, timers):
        self.timers_on = timers

    def updateTimersOnOut(self, timers_on_out):
        self.timers_on_out = timers_on_out

    def updateTimersOf(self, timers):
        self.timers_on = timers

    def updateTimersOfOut(self, timers_of_out):
        self.timers_on_out = timers_of_out

    def updateCounterUp(self, counters):
        self.counter_up = counters

    def updateCounterUpOut(self, counters_up_out):
        self.counter_up_out = counters_up_out
    
    def updateCounterDn(self, counters):
        self.counter_dn = counters

    def updateCounterDnOut(self, counters_dn_out):
        self.counter_dn_out = counters_dn_out

    def resetStructure(self):
        self.inputs = [False]*8
        self.outputs = [False]*8
        self.booleans = [False]*8
        self.timers_on = [False]*8
        self.timers_on_out= [False]*8
        self.timers_of = [False]*8
        self.timer_of_out = [False]*8
        self.counter_up = [False]*8
        self.counter_up_out = [False]*8
        self.counter_dn = [False]*8
        self.counter_dn_out = [False]*8