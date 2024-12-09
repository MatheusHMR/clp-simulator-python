import tkinter as tk
from tkinter import messagebox

def confirmNewProgram(root):
    # Cria uma nova janela modal (Toplevel) para confirmar a ação
    top = tk.Toplevel(root)
    top.title("Novo Programa")
    top.grab_set()  # Faz a janela ser modal, impedindo interação com a janela principal até ser fechada.

    # Variável interna para armazenar o valor de retorno (True/False)
    returnVal = tk.BooleanVar(value=False)

    # Cria a mensagem de aviso
    label = tk.Label(top, text='Criar/Abrir um novo programa irá apagar o que não foi salvo.')
    label.pack(padx=10, pady=10)

    # Frame para botões
    btn_frame = tk.Frame(top)
    btn_frame.pack(pady=10)

    def on_voltar():
        returnVal.set(False)
        top.destroy()

    def on_confirmar():
        returnVal.set(True)
        top.destroy()

    btn_voltar = tk.Button(btn_frame, text='Voltar', command=on_voltar)
    btn_voltar.pack(side=tk.LEFT, padx=5)

    btn_confirmar = tk.Button(btn_frame, text='Confirmar', command=on_confirmar)
    btn_confirmar.pack(side=tk.LEFT, padx=5)

    # Espera a janela ser fechada
    top.wait_window(top)

    # Retorna o valor escolhido pelo usuário
    return returnVal.get()
