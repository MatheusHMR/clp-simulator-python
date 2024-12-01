from .automaton import Automaton
from .constants import *
import re

def simplifySentece(sentence):
    #Removing spaces
    sentence = sentence.replace(' ','') 

    #Sentence to uppercase
    sentence = sentence.upper()

    #Replaces I1, I2, ..., I8 with i:
    i = 0
    while i < len(INPUT_LABELS):
        print(f"SIMP: Replacing {INPUT_LABELS[i]} with i")
        sentence = sentence.replace(INPUT_LABELS[i], 'i')
        i += 1

    #Replaces O1, O2, ..., O8 with o:
    i = 0
    while i < len(OUTPUT_LABELS):
        print(f"SIMP: Replacing {OUTPUT_LABELS[i]} with o")
        sentence = sentence.replace(OUTPUT_LABELS[i], 'o')
        i += 1

    #Replaces B1, B2, ..., B8 with b:
    i = 0
    while i < len(BOOLEAN_LABELS):
        print(f"SIMP: Replacing {BOOLEAN_LABELS[i]} with b")
        sentence = sentence.replace(BOOLEAN_LABELS[i], 'b')
        i += 1

    i = 0
    while i < len(TIMER_ON_LABELS):
        print(f"SIMP: Replacing {TIMER_ON_LABELS[i]} with ton")
        sentence = sentence.replace(TIMER_ON_LABELS[i], 'ton')
        i += 1

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
        sentence = sentence.replace(COUNTER_DOWN_LABELS[i], 'cdno')
        i += 1
    
    i = 0
    while i < len(COUNTER_UP_OUTS_LABELS):
        print(f"SIMP: Replacing {COUNTER_UP_OUTS_LABELS[i]} with cupo")
        sentence = sentence.replace(COUNTER_UP_OUTS_LABELS[i], 'cupo')
        i += 1


    #Checking if every char in sentence is present in the alphabet
    error = True
    sorted_alphabet = sorted(ALPHABET, key=len, reverse=True)

    print(sorted_alphabet)

    # Criar um regex para capturar tokens do alfabeto
    pattern = r"|".join(rf"\b{re.escape(token)}\b" for token in sorted_alphabet)


    # Verificar e capturar os tokens
    tokens = re.findall(pattern, sentence.lower())

    if (all(token in ALPHABET for token in tokens)):
        error = False
        
    return (sentence, error)

        
def interpretSentece(sentence):
    automaton = Automaton()


    tokenIndex = 0
    stateIndex = 0
    error = False
    accepted = False

    original_sentence = sentence
    # Não é necessário simplificar sentença aqui, porque já tokenizamos
    (sentence, simplifyError) = simplifySentece(sentence)

    sorted_alphabet = sorted(ALPHABET, key=len, reverse=True)

    # Criar um regex para capturar tokens do alfabeto
    pattern = r"|".join(re.escape(token) for token in sorted_alphabet)

    # Verificar e capturar os tokens
    tokens = re.findall(pattern, sentence)

    print(tokens)

    if not simplifyError:
        while not error and not accepted and tokenIndex < len(tokens):

            currentToken = tokens[tokenIndex]  # Obter o token atual
            currentState = automaton.states[stateIndex]
            transitionIndex = -1

            i = 0
            
            print("VERYFING SENTENCE...")
            print(f"currentToken: {currentToken}")
            print(f"currentState: {stateIndex}")

            # Procurar uma transição que leia o currentToken
            while i < len(currentState.transitions):
                if currentState.transitions[i].char == currentToken:
                    transitionIndex = i
                i += 1

            # Encontrou uma transição - ESTA NÃO É UMA TRANSIÇÃO VAZIA
            if transitionIndex != -1:
                transition = currentState.transitions[transitionIndex]
                print(f"Found normal transition: {transition}")

                # Esta transição lê da pilha
                if transition.read != '?':
                    if automaton.readFromStack(transition.read):
                        stateIndex = transition.targetState
                        tokenIndex += 1
                    else:
                        error = True  # Erro: não conseguiu ler da pilha
                elif transition.push != '?':  # Esta transição empilha
                    automaton.pushToStack(transition.push)
                    stateIndex = transition.targetState
                    tokenIndex += 1
                else:  # Esta transição não faz nada com a pilha
                    stateIndex = transition.targetState
                    tokenIndex += 1
            else:  # Não encontrou uma transição normal, procurar uma transição vazia
                i = 0
                while i < len(currentState.transitions):
                    if currentState.transitions[i].char == '?':
                        transitionIndex = i
                    i += 1

                # Encontrou uma transição vazia - NÃO INCREMENTA tokenIndex
                if transitionIndex != -1:
                    transition = currentState.transitions[transitionIndex]
                    print(f"Found empty transition: {transition}")

                    # Esta transição lê da pilha
                    if transition.read != '?':
                        if automaton.readFromStack(transition.read):
                            stateIndex = transition.targetState
                        else:
                            error = True  # Erro: não conseguiu ler da pilha
                    elif transition.push != '?':  # Esta transição empilha
                        automaton.pushToStack(transition.push)
                        stateIndex = transition.targetState
                    else:  # Esta transição não faz nada com a pilha
                        stateIndex = transition.targetState
                else:  # Não encontrou nenhuma transição vazia. Isso é um erro.
                    error = True

        print("FINAL STEP...")
        print(f"stopState: {stateIndex}")
        if ((stateIndex == 4 or stateIndex == 7 or stateIndex == 9) and not error):
            if automaton.readFromStack('$'):
                return 0  # Aceita a sentença
            else:
                return 1  # Rejeita a sentença
        else:
            return 1  # Rejeita a sentença
    else:
        return 2  # Erro de simplificação