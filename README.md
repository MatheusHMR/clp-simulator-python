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

## Configuração do Ambiente com Poetry

Este projeto utiliza o Poetry para gerenciar dependências e configurar o ambiente virtual de desenvolvimento. Siga os passos abaixo para configurar o ambiente e executar o projeto.

### 1. Instalar o Poetry

Para instalar o Poetry, execute o seguinte comando no terminal:

> curl -sSL https://install.python-poetry.org | python3 -

Verifique se a instalação foi bem-sucedida:

> poetry --version

### 2. Criar e Ativar o Ambiente Virtual

Com o Poetry instalado, siga os passos abaixo para configurar o ambiente virtual do projeto:

Inicializar o Ambiente Virtual e Instalar Dependências:

No diretório raiz do projeto, execute:

> poetry install

Isso criará o ambiente virtual e instalará todas as dependências necessárias especificadas no arquivo pyproject.toml.

Ativar o Ambiente Virtual:

Para entrar no ambiente virtual, use:

> poetry shell

Você verá algo como (clp-simulator-python) no início do seu terminal, indicando que está no ambiente virtual.

3. Adicionar Dependências ao Projeto

Se precisar adicionar novas dependências ao projeto, use o seguinte comando:

> poetry add <nome-da-dependencia>

Por exemplo, para adicionar a biblioteca requests (não é pra adicionar no projeto nosso):

> poetry add requests

4. Executar o Projeto

Para executar o simulador de CLP, certifique-se de que o ambiente virtual está ativado e, em seguida, rode o comando:

> python main.py

Se preferir executar sem ativar manualmente o ambiente virtual, você pode usar:

> poetry run python main.py

5. Informações Adicionais

Como Instalar Dependências: Todas as dependências estão listadas no arquivo pyproject.toml. Para instalar, execute poetry install.

Contribuidores: Se você é um colaborador, siga as etapas acima para configurar o ambiente e contribuir para o projeto.