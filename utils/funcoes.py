from datetime import datetime
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QPushButton, QTableWidgetItem, QFileDialog
import time
from PyQt6.QtCore import QTime
from utils.db import inserir_registro, excluir_registro as excluir_do_banco, listar_registros, atualizar_registro_no_bd, listar_registros_intervalo # 🔹 Correção na importação
import pandas as pd


def aplicar_tema_escuro(app):
    """Aplica um tema escuro minimalista usando Fusion."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(40, 40, 40))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    app.setPalette(palette)

def calcular_tempo_total(registros):
    """Calcula o tempo total trabalhado no dia filtrado."""
    total_segundos = 0
    formato = "%H:%M"

    for _, _, hora_inicio, hora_fim, _ in registros:
        try:
            inicio = datetime.strptime(hora_inicio, formato)
            fim = datetime.strptime(hora_fim, formato)
            total_segundos += (fim - inicio).total_seconds()
        except ValueError:
            continue

    horas, segundos = divmod(total_segundos, 3600)
    minutos = segundos // 60
    return f"{int(horas)}h {int(minutos)}m"

def calcular_duracao(hora_inicio, hora_fim):
    """Calcula a duração entre Hora Inicial e Hora Final."""
    formato = "%H:%M"
    try:
        inicio = datetime.strptime(hora_inicio, formato)
        fim = datetime.strptime(hora_fim, formato)
        duracao = fim - inicio
        horas, segundos = divmod(duracao.total_seconds(), 3600)
        minutos = segundos // 60
        return f"{int(horas)}h {int(minutos)}m"
    except ValueError:
        return "Erro"

def carregar_grid(window):
    """Carrega os registros na grid e exibe o tempo total trabalhado."""
    dia_filtro = window.data_filtro.date().toString("dd/MM/yy")
    registros = listar_registros(dia_filtro)

    window.grid.setRowCount(0)  # Limpa a grid antes de carregar novos registros

    if registros:
        window.grid.setRowCount(len(registros))
        for row_idx, (id_registro, _, hora_inicio, hora_fim, atividade) in enumerate(registros):
            duracao = calcular_duracao(hora_inicio, hora_fim)

            window.grid.setItem(row_idx, 0, QTableWidgetItem(hora_inicio))
            window.grid.setItem(row_idx, 1, QTableWidgetItem(hora_fim))
            window.grid.setItem(row_idx, 2, QTableWidgetItem(duracao))
            window.grid.setItem(row_idx, 3, QTableWidgetItem(atividade))

            delete_button = QPushButton("🗑️ Excluir")
            delete_button.clicked.connect(lambda _, id_registro=id_registro: excluir_registro(window, id_registro))
            window.grid.setCellWidget(row_idx, 4, delete_button)

    # 🔹 Atualizar tempo total trabalhado do dia
    total_trabalho = calcular_tempo_total(registros)
    window.total_trabalho_label.setText(f"Total Trabalhado: {total_trabalho}")

def adicionar_registro(window):
    """Adiciona um novo registro manualmente na grid e no banco."""
    hora_inicio = window.hora_inicio_input.time().toString("HH:mm")
    hora_fim = window.hora_fim_input.time().toString("HH:mm")
    atividade = window.atividade_input.text().strip()
    dia_filtro = window.data_filtro.date().toString("dd/MM/yy")

    if atividade:
        inserir_registro(hora_inicio, hora_fim, atividade, dia_filtro)
        window.hora_inicio_input.setTime(QTime.currentTime())
        window.hora_fim_input.setTime(QTime.currentTime().addSecs(3600))
        window.atividade_input.clear()
        carregar_grid(window)
    else:
        if hasattr(window, "timer_label"):  # 🔹 Corrigindo erro de referência inexistente
            window.timer_label.setText("⚠️ Preencha a descrição da atividade!")

def excluir_registro(window, id_registro):
    """Exclui um registro do banco de dados e atualiza a grid."""
    excluir_do_banco(id_registro)  # 🔹 Chama a função correta do banco
    carregar_grid(window)
    
def iniciar_cronometro(window):
    """Inicia o cronômetro e desativa o botão de iniciar."""
    if not window.running:
        window.start_time = time.time()
        window.timer.start(1000)
        window.running = True
        window.start_button.setEnabled(False)

def atualizar_tempo(window):
    """Atualiza o tempo decorrido no cronômetro."""
    if window.start_time:
        elapsed = int(time.time() - window.start_time)
        window.timer_label.setText(f"Tempo: {elapsed // 3600:02}:{(elapsed % 3600) // 60:02}:{elapsed % 60:02}")
        
def parar_cronometro(window):
    """✅ Para o cronômetro e registra o tempo corretamente no banco de dados."""
    if window.running:
        window.elapsed_time = int(time.time() - window.start_time)
        window.start_time = None
        window.running = False
        window.timer.stop()
        window.timer_label.setText("Tempo: 00:00:00")

        # ✅ Garantir que pegamos a hora correta do sistema local
        hora_inicio = (datetime.now().timestamp() - window.elapsed_time)
        hora_inicio = datetime.fromtimestamp(hora_inicio).strftime("%H:%M")  # 🔹 Converte para hora correta

        hora_fim = datetime.now().strftime("%H:%M")  # 🔹 Captura a hora correta do término

        inserir_registro(hora_inicio, hora_fim, "Atividade registrada", window.data_filtro.date().toString("dd/MM/yy"))
        carregar_grid(window)  # Atualiza a tabela
        window.start_button.setEnabled(True)
        
def atualizar_registro(window, row, col):
    """Atualiza o registro no banco de dados após a edição da célula."""
    
    # 🔹 Verificar se a célula editada tem um valor antes de continuar
    item_editado = window.grid.item(row, col)
    if item_editado is None:
        return  # Se a célula for None, não faz nada para evitar erro

    novo_valor = item_editado.text().strip()

    # 🔹 Buscar o ID do registro baseado no índice da linha
    registros = listar_registros(window.data_filtro.date().toString("dd/MM/yy"))
    if row >= len(registros):
        return  # Evita erro se o índice estiver fora do intervalo

    id_registro = registros[row][0]  # Obter o ID do registro correto

    # 🔹 Determinar qual campo foi atualizado
    campos = ["hora_inicio", "hora_fim", None, "atividade"]  # Índice 2 (Duração) não pode ser editado
    campo_atualizado = campos[col]

    if campo_atualizado:
        atualizar_registro_no_bd(id_registro, campo_atualizado, novo_valor)

    # 🔹 Atualizar a duração na linha editada se as horas forem alteradas
    if col in [0, 1]:  # Se a edição foi na Hora Inicial ou Hora Final
        hora_inicio_item = window.grid.item(row, 0)
        hora_fim_item = window.grid.item(row, 1)

        if hora_inicio_item and hora_fim_item:  # Verifica se as células não estão vazias
            hora_inicio = hora_inicio_item.text().strip()
            hora_fim = hora_fim_item.text().strip()

            # 🔹 Desconectar temporariamente itemChanged para evitar loop infinito
            window.grid.itemChanged.disconnect()

            duracao = calcular_duracao(hora_inicio, hora_fim)
            window.grid.setItem(row, 2, QTableWidgetItem(duracao))

            # 🔹 Recalcular o tempo total trabalhado sem recursão
            total_trabalho = calcular_tempo_total(listar_registros(window.data_filtro.date().toString("dd/MM/yy")))
            window.total_trabalho_label.setText(f"Total Trabalhado: {total_trabalho}")

            # 🔹 Reconectar itemChanged após a atualização
            window.grid.itemChanged.connect(lambda item: atualizar_registro(window, item.row(), item.column()))


def exportar_para_excel(window):
    """Exporta os registros para um arquivo Excel, agrupados por dia."""

    # 🔹 Obter intervalo de datas
    data_de = window.data_de_filtro.date().toString("dd/MM/yy")
    data_ate = window.data_ate_filtro.date().toString("dd/MM/yy")

    # 🔹 Buscar registros no intervalo selecionado
    registros = listar_registros_intervalo(data_de, data_ate)

    if not registros:
        window.status_label.setText("⚠️ Nenhum registro encontrado no período selecionado.")
        return

    # 🔹 Criar um DataFrame para exportação
    df = pd.DataFrame(registros, columns=["ID", "Dia", "Hora Inicial", "Hora Final", "Atividade"])
    df.drop(columns=["ID"], inplace=True)  # Remover a coluna ID

    # 🔹 Agrupar por dia e ordenar por hora inicial
    df = df.sort_values(by=["Dia", "Hora Inicial"])

    # 🔹 Criar um dicionário para estruturar os dados no Excel
    dados_excel = {}
    for dia, grupo in df.groupby("Dia"):
        nome_aba = dia.replace("/", "_")  # 🔹 Substituir "/" por "_"
        dados_excel[nome_aba] = grupo.drop(columns=["Dia"])  # Remove a coluna 'Dia' para evitar repetição

    # 🔹 Criar um arquivo Excel
    nome_arquivo, _ = QFileDialog.getSaveFileName(window, "Salvar Relatório", "", "Excel Files (*.xlsx)")
    
    if nome_arquivo:
        with pd.ExcelWriter(nome_arquivo, engine="openpyxl") as writer:
            for dia, dados in dados_excel.items():
                dados.to_excel(writer, sheet_name=dia, index=False)  # Agora o nome da aba está correto!

        window.status_label.setText(f"✅ Relatório exportado para {nome_arquivo}")