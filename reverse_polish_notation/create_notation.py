from .constants import OPERATORS, OPERATOR_PRECEDENCE

def reverse_polish_notation(output):
    polish = []
    stack = []

    # Remove spaces
    output = output.replace(" ", "")
    exp = output.split("=")[1]
    exp_end = len(exp)

    i_exp = 0

    while i_exp < exp_end:
        if exp[i_exp] not in OPERATORS and exp[i_exp] not in "()":
            # Handle operands (TON, TONO2, I1, etc.)
            if exp[i_exp] in ['B', 'O', 'I']:
                polish.append(exp[i_exp:i_exp+2])
                i_exp += 1
            elif exp[i_exp] == 'T':  # Example: TON1
                polish.append(exp[i_exp:i_exp+5])
                i_exp += 4
            else:
                polish.append(exp[i_exp])
        elif exp[i_exp] == "(":
            stack.append(exp[i_exp])  # Add the parenthesis to the stack
        elif exp[i_exp] == ")":
            # Pop elements until the corresponding parenthesis is found
            while stack and stack[-1] != "(":
                polish.append(stack.pop())
            if stack and stack[-1] == "(":
                stack.pop()  # Remove the opening parenthesis
            # Check if there is a unary operator at the top of the stack
            if stack and stack[-1] == "!":
                polish.append(stack.pop())
        else:
            # Handle operators
            if exp[i_exp] in OPERATORS:
                while (stack and stack[-1] in OPERATORS and
                       OPERATOR_PRECEDENCE[stack[-1]] >= OPERATOR_PRECEDENCE[exp[i_exp]]):
                    polish.append(stack.pop())
                stack.append(exp[i_exp])
        i_exp += 1

    # Add remaining operators from the stack
    while stack:
        polish.append(stack.pop())

    return polish