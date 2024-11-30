# clp-programmer-python

Authors: Alexandre Monteiro Londe, Esdras Santos de Oliveira (Arduino/Hardware)
           Júlia Cordeiro e Silva, Nathan Silva Rodrigues (Python Interface)

__ENGLISH__

This code simulates a PLC programming interface, allowing the user to create a simple program using logic operators AND (^), OR (|) and NOT (!), and interact with eight digital inputs and outputs, as well as thirty-two boolean memories. The simulation runs fully in Python, using a graphical interface built with PySimpleGUI. The PLC simulator follows the traditional scan cycle: initializing, reading inputs, processing user logic, and updating outputs.

The simulator also supports different modes of operation: PROGRAM, which allows editing the user program; STOP, which stops the execution; and RUN, which executes the user logic. The Python interface allows users to load and save programs in simple text files, and to track the state of inputs, outputs, and boolean memories.

__PORTUGUÊS__

Este código simula uma interface de programação e simulação de CLP, permitindo que o usuário crie programas simples utilizando os operadores lógicos AND (^), OR (|) e NOT (!), e interaja com oito entradas e saídas digitais, além de trinta e duas memórias booleanas. A simulação é feita inteiramente em Python, usando uma interface gráfica construída com PySimpleGUI. O simulador de CLP segue o ciclo de varredura tradicional: inicialização, leitura das entradas, processamento da lógica do usuário e atualização das saídas.

O simulador também suporta diferentes modos de operação: PROGRAM, que permite editar o programa do usuário; STOP, que interrompe a execução; e RUN, que executa a lógica do usuário. A interface em Python permite que os usuários salvem e carreguem programas em arquivos de texto simples, e acompanhem o estado das entradas, saídas e memórias booleanas.

Engenharia de Computação, IFTM, Campus Uberaba Parque Tecnológico 2024/2
