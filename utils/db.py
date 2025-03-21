import sqlite3
from datetime import datetime

DB_NAME = "timesheet.db"

# 🔹 Conectar ao banco de dados
def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# 🔹 Criar a tabela corretamente com ID automático
def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dia TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fim TEXT NOT NULL,
            atividade TEXT NOT NULL,
            lancado INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# 🔹 Criar um novo registro (ID gerado automaticamente)
def inserir_registro(hora_inicio, hora_fim, atividade, dia=None):
    if not dia:
        dia = datetime.now().strftime("%d/%m/%y")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO registros (dia, hora_inicio, hora_fim, atividade)
        VALUES (?, ?, ?, ?)
    ''', (dia, hora_inicio, hora_fim, atividade))
    conn.commit()
    conn.close()

def listar_registros(dia=None):
    conn = conectar()
    cursor = conn.cursor()
    if dia:
        cursor.execute("""
            SELECT id, dia, hora_inicio, hora_fim, atividade, lancado
            FROM registros
            WHERE dia = ?
            ORDER BY hora_inicio
        """, (dia,))
    else:
        cursor.execute("""
            SELECT id, dia, hora_inicio, hora_fim, atividade, lancado
            FROM registros
            ORDER BY hora_inicio
        """)
    
    registros = cursor.fetchall()
    conn.close()
    return registros

# 🔹 Atualizar um registro existente
def atualizar_registro(id_registro, hora_inicio, hora_fim, atividade):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE registros
        SET hora_inicio = ?, hora_fim = ?, atividade = ?
        WHERE id = ?
    ''', (hora_inicio, hora_fim, atividade, id_registro))
    conn.commit()
    conn.close()

# 🔹 Excluir um registro pelo ID
def excluir_registro(id_registro):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros WHERE id = ?", (id_registro,))
    conn.commit()
    conn.close()
    
   
def atualizar_registro_no_bd(id_registro, campo, novo_valor):
    """Atualiza um campo específico de um registro no banco de dados."""
    conexao = sqlite3.connect("timesheet.db")
    cursor = conexao.cursor()

    query = f"UPDATE registros SET {campo} = ? WHERE id = ?"
    cursor.execute(query, (novo_valor, id_registro))

    conexao.commit()
    conexao.close()
    
def listar_registros_intervalo(data_de, data_ate):
    """Retorna os registros dentro de um intervalo de datas."""
    conexao = sqlite3.connect("timesheet.db")
    cursor = conexao.cursor()

    query = """
    SELECT id, dia, hora_inicio, hora_fim, atividade, lancado
    FROM registros 
    WHERE dia BETWEEN ? AND ?
    ORDER BY dia, hora_inicio
    """
    
    cursor.execute(query, (data_de, data_ate))
    registros = cursor.fetchall()

    conexao.close()
    return registros


# Criar a tabela ao iniciar
criar_tabela()

