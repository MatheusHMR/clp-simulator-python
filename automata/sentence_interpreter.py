from .automaton import Automaton
from .constants import *
import re

def tokenize(sentence):

    # Build regex to match tokens based on the ALPHABET
    regex = '|'.join(re.escape(word) for word in sorted(ALPHABET, key=len, reverse=True))

    pattern = rf"({regex})"
    
    # Find tokens in the sentence using regex
    tokens = re.findall(pattern, sentence)

    print(tokens)

    return tokens

def validateSentence(sentence):

    error = True
    pattern = r"[A-Z]"
    uppercase_letters = re.findall(pattern, sentence)

    tokens = tokenize(sentence)

    # Check if all tokens are valid and there are no uppercase letters
    if (all(token in ALPHABET for token in tokens) and not uppercase_letters):
        error = False

    return error

def simplifySentece(sentence):
    # Remove spaces
    sentence = sentence.replace(' ','') 

    # Convert sentence to uppercase
    sentence = sentence.upper()

    print(sentence)

    i = 0
    while i < len(TIMER_ON_LABELS):
        print(f"SIMP: Replacing {TIMER_ON_LABELS[i]} with ton")
        sentence = sentence.replace(TIMER_ON_LABELS[i], 'ton')
        i += 1

    print(sentence)

    i = 0
    while i < len(TIMER_ON_OUTS_LABELS):
        print(f"SIMP: Replacing {TIMER_ON_OUTS_LABELS[i]} with tono")
        sentence = sentence.replace(TIMER_ON_OUTS_LABELS[i], 'tono')
        i += 1

    i = 0
    while i < len(TIMER_OF_LABELS):
        print(f"SIMP: Replacing {TIMER_OF_LABELS[i]} with tof")
        sentence = sentence.replace(TIMER_OF_LABELS[i], 'tof')
        i += 1

    i = 0
    while i < len(TIMER_OF_OUTS_LABELS):
        print(f"SIMP: Replacing {TIMER_OF_OUTS_LABELS[i]} with tofo")
        sentence = sentence.replace(TIMER_OF_OUTS_LABELS[i], 'tofo')
        i += 1

    i = 0
    while i < len(COUNTER_UP_LABELS):
        print(f"SIMP: Replacing {COUNTER_UP_LABELS[i]} with cup")
        sentence = sentence.replace(COUNTER_UP_LABELS[i], 'cup')
        i += 1
    
    i = 0
    while i < len(COUNTER_UP_OUTS_LABELS):
        print(f"SIMP: Replacing {COUNTER_UP_OUTS_LABELS[i]} with cupo")
        sentence = sentence.replace(COUNTER_UP_OUTS_LABELS[i], 'cupo')
        i += 1

    i = 0
    while i < len(COUNTER_DOWN_LABELS):
        print(f"SIMP: Replacing {COUNTER_DOWN_LABELS[i]} with cdn")
        sentence = sentence.replace(COUNTER_DOWN_LABELS[i], 'cdn')
        i += 1
    
    i = 0
    while i < len(COUNTER_DOWN_OUTS_LABELS):
        print(f"SIMP: Replacing {COUNTER_DOWN_OUTS_LABELS[i]} with cdno")
        sentence = sentence.replace(COUNTER_DOWN_OUTS_LABELS[i], 'cdno')
        i += 1

    # Replace I1, I2, ..., I8 with i
    i = 0
    while i < len(INPUT_LABELS):
        print(f"SIMP: Replacing {INPUT_LABELS[i]} with i")
        sentence = sentence.replace(INPUT_LABELS[i], 'i')
        i += 1

    # Replace O1, O2, ..., O8 with o
    i = 0
    while i < len(OUTPUT_LABELS):
        print(f"SIMP: Replacing {OUTPUT_LABELS[i]} with o")
        sentence = sentence.replace(OUTPUT_LABELS[i], 'o')
        i += 1

    # Replace B1, B2, ..., B8 with b
    i = 0
    while i < len(BOOLEAN_LABELS):
        print(f"SIMP: Replacing {BOOLEAN_LABELS[i]} with b")
        sentence = sentence.replace(BOOLEAN_LABELS[i], 'b')
        i += 1

    # Check if every character in the sentence is present in the alphabet
    error = validateSentence(sentence)
    return (sentence, error)

        
def interpretSentece(sentence):
    automaton = Automaton()
    
    tokenIndex = 0
    stateIndex = 0
    error = False
    accepted = False

    original_sentence = sentence
    # No need to simplify the sentence here since it was already tokenized
    (sentence, simplifyError) = simplifySentece(sentence)

    tokens = tokenize(sentence)

    if not simplifyError:
        while not error and not accepted and tokenIndex < len(tokens):

            currentToken = tokens[tokenIndex]  # Get the current token
            currentState = automaton.states[stateIndex]
            transitionIndex = -1

            i = 0
            
            print("VERIFYING SENTENCE...")
            print(f"currentToken: {currentToken}")
            print(f"currentState: {stateIndex}")

            # Search for a transition that reads the currentToken
            while i < len(currentState.transitions):
                if currentState.transitions[i].char == currentToken:
                    transitionIndex = i
                i += 1

            # Found a transition - THIS IS NOT AN EMPTY TRANSITION
            if transitionIndex != -1:
                transition = currentState.transitions[transitionIndex]
                print(f"Found normal transition: {transition}")

                # This transition reads from the stack
                if transition.read != '?':
                    if automaton.readFromStack(transition.read):
                        stateIndex = transition.targetState
                        tokenIndex += 1
                    else:
                        error = True  # Error: unable to read from the stack
                elif transition.push != '?':  # This transition pushes to the stack
                    automaton.pushToStack(transition.push)
                    stateIndex = transition.targetState
                    tokenIndex += 1
                else:  # This transition does nothing with the stack
                    stateIndex = transition.targetState
                    tokenIndex += 1
            else:  # Did not find a normal transition, search for an empty transition
                i = 0
                while i < len(currentState.transitions):
                    if currentState.transitions[i].char == '?':
                        transitionIndex = i
                    i += 1

                # Found an empty transition - DO NOT INCREMENT tokenIndex
                if transitionIndex != -1:
                    transition = currentState.transitions[transitionIndex]
                    print(f"Found empty transition: {transition}")

                    # This transition reads from the stack
                    if transition.read != '?':
                        if automaton.readFromStack(transition.read):
                            stateIndex = transition.targetState
                        else:
                            error = True  # Error: unable to read from the stack
                    elif transition.push != '?':  # This transition pushes to the stack
                        automaton.pushToStack(transition.push)
                        stateIndex = transition.targetState
                    else:  # This transition does nothing with the stack
                        stateIndex = transition.targetState
                else:  # Did not find any empty transition. This is an error.
                    error = True

        print("FINAL STEP...")
        print(f"stopState: {stateIndex}")
        if ((stateIndex == 4 or stateIndex == 7 or stateIndex == 9) and not error):
            if automaton.readFromStack('$'):
                return 0  # Accept the sentence
            else:
                return 1  # Reject the sentence
        else:
            return 1  # Reject the sentence
    else:
        return 2  # Simplification error
