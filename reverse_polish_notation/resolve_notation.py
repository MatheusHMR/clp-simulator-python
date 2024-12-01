from .constants import OPERATORS

def resolve(notation, inputs, outputs, booleans, 
timers_on, timers_on_out, 
timers_of, timers_of_out, 
counters_up, counters_up_out,
counters_dn, counters_dn_out,):
    in_out = []
    
    index = 0
    notation_resolve = []

    for index in range(0, len(notation)):
        if notation[index] not in OPERATORS:
            address = int(notation[index][1])
            if notation[index][0] == 'I':
                notation_resolve.insert(index, inputs[address - 1])
            elif notation[index][0] == 'O':
                notation_resolve.insert(index, outputs[address - 1])
            elif notation[index][0] == 'B':
                if len(notation[index]) == 3:
                    address = int(notation[index][1::])
                notation_resolve.insert(index, booleans[address - 1])
            elif notation[index][0] == 'TON':
                notation_resolve.insert(index, timers_on[address - 1])
            elif notation[index][0] == 'TONO':
                notation_resolve.insert(index, timers_on_out[address - 1])
            elif notation[index][0] == 'TOF':
                notation_resolve.insert(index, timers_of[address - 1])
            elif notation[index][0] == 'TOFO':
                notation_resolve.insert(index, timers_of_out[address - 1])    
            elif notation[index][0] == 'CUP':
                notation_resolve.insert(index, counters_up[address - 1])
            elif notation[index][0] == 'CUPO':
                notation_resolve.insert(index, counters_up_out[address - 1])
            elif notation[index][0] == 'CDN':
                notation_resolve.insert(index, counters_dn[address - 1])
            elif notation[index][0] == 'CDNO':
                notation_resolve.insert(index, counters_dn_out[address - 1])
        else:
            notation_resolve.insert(index, notation[index])
        index += 1

    for item in notation_resolve:
        if item not in OPERATORS:
            in_out.append(item)
        else:
            if item == OPERATORS[2]:
                operand = in_out.pop()
                operation = not operand
                in_out.append(operation)
            else:
                frist_op = in_out.pop()
                second_op = in_out.pop()
                if item == OPERATORS[0]:
                    operation = frist_op and second_op
                    in_out.append(operation)
                elif item == OPERATORS[1]:
                    operation = frist_op or second_op
                    in_out.append(operation)

    return in_out[0]
