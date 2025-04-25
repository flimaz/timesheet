import sqlite3
from datetime import datetime

from utils.config import carregar_caminho_bd

# 🔹 Conectar ao banco de dados
def conectar(caminho=None):
    if not caminho:
        caminho = carregar_caminho_bd()
    if not caminho:
        raise ValueError("Caminho do banco de dados não definido.")
    return sqlite3.connect(caminho, check_same_thread=False)


# 🔹 Criar a tabela corretamente com ID automático
def criar_tabela(caminho=None):
    conn = conectar(caminho)
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
    conexao = conectar()
    cursor = conexao.cursor()

    query = f"UPDATE registros SET {campo} = ? WHERE id = ?"
    cursor.execute(query, (novo_valor, id_registro))

    conexao.commit()
    conexao.close()
    
def listar_registros_intervalo(data_de, data_ate):
    # Converter dd/MM/yy → yy-MM-dd para comparação correta
    def converter(data_str):
        dia, mes, ano = data_str.split("/")
        return f"{ano}-{mes}-{dia}"

    data_de_sql = converter(data_de)
    data_ate_sql = converter(data_ate)

    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT id, dia, hora_inicio, hora_fim, atividade, lancado
    FROM registros 
    WHERE substr(dia, 7, 2) || '-' || substr(dia, 4, 2) || '-' || substr(dia, 1, 2)
          BETWEEN ? AND ?
    ORDER BY substr(dia, 7, 2) || '-' || substr(dia, 4, 2) || '-' || substr(dia, 1, 2),
             hora_inicio
    """

    cursor.execute(query, (data_de_sql, data_ate_sql))
    registros = cursor.fetchall()

    conn.close()
    return registros



