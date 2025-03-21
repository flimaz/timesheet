from datetime import datetime
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QPushButton, QTableWidgetItem, QFileDialog, QCheckBox, QWidget, QHBoxLayout
import time
from PyQt6.QtCore import QTime, Qt
from utils.db import inserir_registro, excluir_registro as excluir_do_banco, listar_registros, atualizar_registro_no_bd, listar_registros_intervalo 
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer
from reportlab.lib.units import cm
import os
import platform
import subprocess
from PyQt6 import QtGui

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

    for _, _, hora_inicio, hora_fim, _, _ in registros:
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
    dia_filtro = window.data_filtro.date().toString("dd/MM/yy")
    registros = listar_registros(dia_filtro)

    window.grid.setRowCount(0)
    window.grid.setColumnCount(6)
    window.grid.setHorizontalHeaderLabels(["Hora Inicial", "Hora Final", "Duração", "Atividade", "Ações", "Lançado"])

    if registros:
        window.grid.setRowCount(len(registros))
        for row_idx, (id_registro, _, hora_inicio, hora_fim, atividade, lancado) in enumerate(registros):
            # ... (hora inicial, final, duração, atividade)

            for col_idx, value in enumerate([hora_inicio, hora_fim, calcular_duracao(hora_inicio, hora_fim), atividade]):
                item = QTableWidgetItem(value)
                window.grid.setItem(row_idx, col_idx, item)

            # Botão de excluir
            delete_button = QPushButton("🗑️ Excluir")
            delete_button.clicked.connect(lambda _, id=id_registro: excluir_registro(window, id))
            window.grid.setCellWidget(row_idx, 4, delete_button)

            # Checkbox de Lançado
            checkbox = QCheckBox()
            checkbox.setChecked(bool(lancado))
            checkbox.stateChanged.connect(lambda state, row=row_idx, id=id_registro: atualizar_lancado(window, row, id, state))
            
            checkbox = QCheckBox()
            checkbox.setChecked(bool(lancado))
            checkbox.stateChanged.connect(lambda state, row=row_idx, id=id_registro: atualizar_lancado(window, row, id, state))

            checkbox.setStyleSheet(""" 
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 1px solid #aaa;
                    background-color: #444;
                }
                QCheckBox::indicator:checked {
                    background-color: #00cc66;
                    border: 1px solid #00cc66;
                }
            """)

            # Centralizar o checkbox com layout
            checkbox_widget = QWidget()
            layout = QHBoxLayout(checkbox_widget)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget.setLayout(layout)

            window.grid.setCellWidget(row_idx, 5, checkbox_widget)
            
            verificar_overlaps(window)



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
        hora_inicio = datetime.fromtimestamp(hora_inicio).strftime("%H:%M")

        hora_fim = datetime.now().strftime("%H:%M")

        # ✅ Data real do sistema, ignorando o calendário
        dia_hoje = datetime.now().strftime("%d/%m/%y")

        inserir_registro(hora_inicio, hora_fim, "Atividade registrada", dia_hoje)

        # 🔄 Atualizar grid somente se o usuário estiver no dia atual
        if window.data_filtro.date().toString("dd/MM/yy") == dia_hoje:
            carregar_grid(window)

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

            verificar_overlaps(window)
            
            # 🔹 Reconectar itemChanged após a atualização
            window.grid.itemChanged.connect(lambda item: atualizar_registro(window, item.row(), item.column()))

    


def exportar_para_excel(window):
    data_de = window.data_de_filtro.date().toString("dd/MM/yy")
    data_ate = window.data_ate_filtro.date().toString("dd/MM/yy")
    registros = listar_registros_intervalo(data_de, data_ate)

    if not registros:
        window.status_label.setText("⚠️ Nenhum registro encontrado no período selecionado.")
        return

    # Ajustar colunas para refletir o novo campo "Lançado"
    df = pd.DataFrame(registros, columns=["ID", "Dia", "Hora Inicial", "Hora Final", "Atividade", "Lançado"])
    df["Lançado"] = df["Lançado"].apply(lambda x: "Sim" if x else "Não")

    # Sugere nome padrão com base na data de hoje
    hoje = datetime.now().strftime("%d-%m-%Y")
    nome_sugerido = f"{hoje}_Timesheet.xlsx"

    nome_arquivo, _ = QFileDialog.getSaveFileName(window, "Salvar Relatório em Excel", nome_sugerido, "Excel Files (*.xlsx)")
    if not nome_arquivo:
        return

    try:
        df.drop(columns=["ID"]).to_excel(nome_arquivo, index=False, sheet_name="Relatório")
        window.status_label.setText(f"✅ Excel gerado com sucesso: {nome_arquivo}")

        # Abrir automaticamente após exportar
        if platform.system() == "Windows":
            os.startfile(nome_arquivo)
        elif platform.system() == "Darwin":
            subprocess.call(["open", nome_arquivo])
        else:
            subprocess.call(["xdg-open", nome_arquivo])
    except Exception as e:
        window.status_label.setText("❌ Erro ao gerar o Excel.")
        
def atualizar_lancado(window, row, id_registro, state):
    """Atualiza o campo 'lancado' no banco e ajusta o estilo visual."""
    valor = 1 if state == 2 else 0  # Qt.Checked == 2
    atualizar_registro_no_bd(id_registro, "lancado", valor)

    # Estiliza apenas a célula do checkbox (coluna 5)
    cell_widget = window.grid.cellWidget(row, 5)
    if cell_widget:
        if valor:
            cell_widget.setStyleSheet("background-color: rgba(0, 255, 0, 50); border-radius: 4px;")
        else:
            cell_widget.setStyleSheet("background-color: transparent;")
  
 # Exportação para PDF           
def exportar_para_pdf(window):
    data_de = window.data_de_filtro.date().toString("dd/MM/yy")
    data_ate = window.data_ate_filtro.date().toString("dd/MM/yy")
    registros = listar_registros_intervalo(data_de, data_ate)

    if not registros:
        window.status_label.setText("⚠️ Nenhum registro encontrado no período selecionado.")
        return

    df = pd.DataFrame(registros, columns=["ID", "Dia", "Hora Inicial", "Hora Final", "Atividade", "Lançado"])
    df.drop(columns=["ID"], inplace=True)
    df["Lançado"] = df["Lançado"].apply(lambda x: "Sim" if x else "Não")

    hoje = datetime.now().strftime("%d-%m-%Y")
    nome_sugerido = f"{hoje}_Timesheet.pdf"
    nome_arquivo, _ = QFileDialog.getSaveFileName(window, "Salvar Relatório em PDF", nome_sugerido, "PDF Files (*.pdf)")
    if not nome_arquivo:
        return

    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    # Fonte menor e minimalista
    normal_style = ParagraphStyle(name='NormalSmall', fontSize=9, leading=11)
    heading_style = ParagraphStyle(name='Heading', fontSize=11, leading=14, spaceAfter=6, fontName='Helvetica-Bold')

    # Título principal
    story.append(Paragraph("Relatório de Atividades - Timesheet", styles["Title"]))
    story.append(Spacer(1, 12))

    for dia, grupo in df.groupby("Dia"):
        story.append(Paragraph(f"DIA: {dia}", heading_style))
        story.append(Paragraph("Lançamentos:", normal_style))
        story.append(Spacer(1, 4))

        data = [["Hora Inicial", "Hora Final", "Duração", "Atividade", "Lançado"]]

        total_segundos = 0
        for _, row in grupo.iterrows():
            hi, hf = row["Hora Inicial"], row["Hora Final"]
            try:
                h_ini = datetime.strptime(hi, "%H:%M")
                h_fim = datetime.strptime(hf, "%H:%M")
                duracao = h_fim - h_ini
                segundos = duracao.total_seconds()
                total_segundos += segundos
                horas = int(segundos // 3600)
                minutos = int((segundos % 3600) // 60)
                dur = f"{horas}h {minutos}m"
            except:
                dur = "--"

            data.append([hi, hf, dur, row["Atividade"], row["Lançado"]])

        # Colunas otimizadas
        tabela = Table(data, colWidths=[2.3*cm, 2.3*cm, 2.6*cm, 8.3*cm, 2*cm])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),                # Fonte padrão
            ("FONTSIZE", (3, 1), (3, -1), 7),                 # Fonte menor para a coluna Atividade
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 1), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
            ("WORDWRAP", (3, 1), (3, -1), True),  # Atividade
        ]))

        story.append(tabela)
        story.append(Spacer(1, 6))

        total_horas = int(total_segundos // 3600)
        total_minutos = int((total_segundos % 3600) // 60)
        story.append(Paragraph(f"Tempo Trabalhado: {total_horas}h {total_minutos}m", normal_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<hr width='100%'/>", styles["Normal"]))
        story.append(Spacer(1, 8))

    doc.build(story)
    window.status_label.setText(f"✅ PDF gerado com sucesso: {nome_arquivo}")

    # Abrir o PDF automaticamente
    try:
        if platform.system() == "Windows":
            os.startfile(nome_arquivo)
        elif platform.system() == "Darwin":
            subprocess.call(["open", nome_arquivo])
        else:
            subprocess.call(["xdg-open", nome_arquivo])
    except:
        window.status_label.setText("PDF salvo, mas não foi possível abrir automaticamente.")
        
# Funcoes para detectar overlaps
def horario_para_minutos(hora_str):
    try:
        h, m = map(int, hora_str.split(":"))
        return h * 60 + m
    except:
        return None

from PyQt6 import QtGui
from PyQt6.QtWidgets import QCheckBox

def horario_para_minutos(hora_str):
    try:
        h, m = map(int, hora_str.split(":"))
        return h * 60 + m
    except:
        return None

def verificar_overlaps(window):
    registros = []
    tem_overlap = False  # ✅ Flag para exibir mensagem

    # 🔁 Coleta os horários da grid
    for i in range(window.grid.rowCount()):
        hi_item = window.grid.item(i, 0)
        hf_item = window.grid.item(i, 1)

        if hi_item and hf_item:
            inicio = horario_para_minutos(hi_item.text())
            fim = horario_para_minutos(hf_item.text())

            if inicio is not None and fim is not None and fim > inicio:
                registros.append((inicio, fim, i))

    # 🔁 Resetar cores de Hora Inicial e Hora Final (colunas 0 e 1)
    for i in range(window.grid.rowCount()):
        for col in [0, 1]:
            item = window.grid.item(i, col)
            if item:
                checkbox_widget = window.grid.cellWidget(i, 5)
                if isinstance(checkbox_widget, QCheckBox) and checkbox_widget.isChecked():
                    cor = QtGui.QColor("red")
                else:
                    cor = QtGui.QColor("white")
                item.setForeground(QtGui.QBrush(cor))

    # 🔍 Verificar conflitos de horário e pintar de vermelho se houver
    for i, (ini1, fim1, row1) in enumerate(registros):
        for j, (ini2, fim2, row2) in enumerate(registros):
            if i != j and ini1 < fim2 and ini2 < fim1:
                tem_overlap = True  # ✅ Marcar que há conflito
                for col in [0, 1]:  # Hora Inicial e Final
                    item1 = window.grid.item(row1, col)
                    item2 = window.grid.item(row2, col)
                    if item1:
                        item1.setForeground(QtGui.QBrush(QtGui.QColor("red")))
                    if item2:
                        item2.setForeground(QtGui.QBrush(QtGui.QColor("red")))

    # ✅ Exibir ou limpar mensagem no status_label
    if tem_overlap:
        window.status_label.setStyleSheet("color: red;")
        window.status_label.setText("⚠️ Overlap detectado entre horários.")
    else:
        window.status_label.setText("")






