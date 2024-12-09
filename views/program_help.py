import tkinter as tk

def programHelpWindow(root):
    top = tk.Toplevel(root)
    top.title('Como Programar?')

    info_text = """Cada linha do programa deve ser composta de uma sentença lógica com 
parênteses balanceados corretamente, vinculada a uma porta ou memória booleana.
Exemplo: O1 = (!I1 ^ (O2 | B3))

As portas disponíveis são definidas por: O1 até O8.
As entradas são indicadas por: I1 até I8.
Memórias booleanas são indicadas por: B1 a B16.

A forma de configurar o timer é pela configuração de temporizador.
Exemplo de Temporizador ON DELAY: TON1 (bobina) e TONO1 (contato do timer).
Se for OFF DELAY: TOF1 (bobina) e TOFO1 (contato do timer).
"""

    # Label de título
    title_label = tk.Label(top, text='Como programar?', font=('Arial', 12, 'bold'))
    title_label.pack(anchor='w', padx=10, pady=(10,0))

    # Label com as instruções
    instructions_label = tk.Label(top, text=info_text, justify='left', font=('Arial', 10))
    instructions_label.pack(anchor='w', padx=10, pady=10)

    # Botão Voltar
    btn_frame = tk.Frame(top)
    btn_frame.pack(pady=10)

    btn_voltar = tk.Button(btn_frame, text='Voltar', command=top.destroy)
    btn_voltar.pack()

    top.geometry("650x300")
