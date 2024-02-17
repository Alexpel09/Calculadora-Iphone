import flet as ft
from flet import colors
from decimal import Decimal
import sqlite3
import threading

# Criar um contexto de thread local para a conexão com o banco de dados
db_lock = threading.Lock()
db_conn = threading.local()

def get_db_conn():
    if not hasattr(db_conn, 'conn'):
        with db_lock:
            db_conn.conn = sqlite3.connect('historico.db')
    return db_conn.conn

def close_db_conn():
    if hasattr(db_conn, 'conn'):
        with db_lock:
            db_conn.conn.close()
        del db_conn.conn

# Definir o esquema do banco de dados
def setup_database():
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS historico
                 (expressao TEXT, resultado TEXT)''')
    conn.commit()

# Função para adicionar uma entrada ao histórico
def add_to_history(expression, result):
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("INSERT INTO historico (expressao, resultado) VALUES (?, ?)", (expression, result))
    conn.commit()

# Função para recuperar o histórico de cálculos
def get_history():
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM historico ORDER BY ROWID DESC")
    return c.fetchall()

# Definir os botões da calculadora
botoes = [
    {'operador': 'AC', 'fonte': colors.BLACK, 'fundo': colors.BLUE_GREY_100},
    {'operador': '+/-', 'fonte': colors.BLACK, 'fundo': colors.BLUE_GREY_100},
    {'operador': '%', 'fonte': colors.BLACK, 'fundo': colors.BLUE_GREY_100},
    {'operador': '÷', 'fonte': colors.WHITE, 'fundo': colors.ORANGE},
    {'operador': '7', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': '8', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': '9', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': 'x', 'fonte': colors.WHITE, 'fundo': colors.ORANGE},
    {'operador': '4', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': '5', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': '6', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': '-', 'fonte': colors.WHITE, 'fundo': colors.ORANGE},
    {'operador': '1', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': '2', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': '3', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': '+', 'fonte': colors.WHITE, 'fundo': colors.ORANGE},
    {'operador': '0', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': ',', 'fonte': colors.WHITE, 'fundo': colors.WHITE24},
    {'operador': '=', 'fonte': colors.WHITE, 'fundo': colors.ORANGE}
]

# Funções para as operações matemáticas básicas
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return '0'
    return x / y

# Função para calcular a expressão
def calculate(expression):
    try:
        if '%' in expression:
            # Se a expressão contém '%', calculamos a porcentagem
            value, percent = map(Decimal, expression.split('%'))
            result = value * (percent / 100)
            return str(result)
        elif '+' in expression:
            x, y = map(Decimal, expression.split('+'))
            return str(add(x, y))
        elif '-' in expression:
            x, y = map(Decimal, expression.split('-'))
            return str(subtract(x, y))
        elif 'x' in expression:
            x, y = map(Decimal, expression.split('x'))
            return str(multiply(x, y))
        elif '÷' in expression:
            x, y = map(Decimal, expression.split('÷'))
            return str(divide(x, y))
        else:
            return expression
    except Exception as e:
        return 'Error'

# Função principal da aplicação
def main(page: ft.Page):
    page.bgcolor = '#000'
    page.window_resizable = False
    page.window_width = 280
    page.window_height = 400
    page.title = 'Calculadora'
    page.window_always_on_top = True

    # Configurar o banco de dados
    setup_database()

    # Elemento de texto para exibir o resultado da operação atual
    result = ft.Text(value='0', color=colors.WHITE, size=30)

    # Função chamada quando um botão da calculadora é clicado
    def select(e):
        value_at = result.value
        value = e.control.content.value

        if value.isdigit():
            if value_at == '0' or value_at == 'Error':
                result.value = value
            else:
                result.value += value
        elif value == 'AC':
            result.value = '0'
        elif value == '+/-':
            if value_at and value_at[0] == '-':
                result.value = value_at[1:]
            else:
                result.value = '-' + value_at
        elif value == '%':
            # Adicionamos o '%' ao final da expressão para facilitar o cálculo
            result.value += '%'
        elif value == '=':
            # Ao clicar em '=', calculamos a expressão e a adicionamos ao histórico
            calculated_value = calculate(value_at)
            add_to_history(value_at, calculated_value)
            result.value = calculated_value
        elif value in ('+', '-', 'x', '÷'):
            if value_at and value_at[-1] in ('+', '-', 'x', '÷'):
                result.value = value_at[:-1] + value
            else:
                result.value += value
        elif value == ',':
            if '.' not in value_at and ',' not in value_at:
            # Adiciona a vírgula apenas se não houver nenhum ponto ou vírgula na expressão atual
                if value_at == '0':
            # Se o valor atual for '0' ou 'Error', substituí-lo por '0,'
                    result.value = '0' + ','
        else:
            result.value += value

        result.update()

    # Layout da interface da calculadora
    display = ft.Row(
        width=250,
        controls=[result],
        alignment='end'
    )

    # Criar os botões da calculadora
    btn = [ft.Container(
        content=ft.Text(value=btn['operador'], color=btn['fonte']),
        width=110 if btn['operador'] == '0' else 50,
        height=50,
        bgcolor=btn['fundo'],
        border_radius=100,
        alignment=ft.alignment.center,
        on_click=select
    ) for btn in botoes]

    # Layout do teclado
    keyboard = ft.Row(
        width=250,
        wrap=True,
        controls=btn,
        alignment='end'
    )

    # Elemento de texto para exibir o histórico de cálculos
    historico_text = ft.Text(value='', color=colors.WHITE, size=14)
    historico_display = ft.Row(
        width=250,
        controls=[historico_text],
        alignment='start'
    )

    # Função para atualizar o texto do histórico
    def atualizar_historico():
        historico = get_history()
        historico_text.value = '\n'.join([f"{calc[0]} = {calc[1]}" for calc in historico])

    # Adicionar elementos à página
    page.add(display, keyboard, historico_display)
    atualizar_historico()

# Iniciar a aplicação
ft.app(target=main)
