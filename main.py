
from utils.config import carregar_caminho_bd, salvar_caminho_bd
from PyQt6.QtWidgets import QFileDialog
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, 
    QHeaderView, QHBoxLayout, QDateEdit, QTimeEdit, QLineEdit, QSizePolicy, QMessageBox, QFrame
)
from PyQt6.QtCore import QTimer, QDate, QSize
from PyQt6.QtGui import QFont, QIcon
from utils.funcoes import (
    aplicar_tema_escuro, carregar_grid, adicionar_registro,
    iniciar_cronometro, parar_cronometro, atualizar_tempo, atualizar_registro, exportar_para_excel, exportar_para_pdf, mostrar_sobre, fazer_backup_banco
)

class TimesheetApp(QWidget):
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Fechar Aplicativo",
            "Deseja realmente sair do Timesheet?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
        
    
    def __init__(self):
        super().__init__()

        # Definir Ícone do Aplicativo
        self.setWindowIcon(QIcon("assets/TS.ico"))  # Caminho para o ícone

        self.setWindowTitle("Timesheet Tracker")
        self.setGeometry(200, 200, 900, 600)

        self.layout = QVBoxLayout()

        # Aplicar Tema Escuro
        aplicar_tema_escuro(app)

        # Cronômetro (Fonte maior e em negrito)
        self.timer_label = QLabel("Tempo: 00:00:00")
        self.timer_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.layout.addWidget(self.timer_label)

        self.start_button = QPushButton("▶️ Iniciar")
        self.start_button.clicked.connect(lambda: iniciar_cronometro(self))
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("⏹️ Parar")
        self.stop_button.clicked.connect(lambda: parar_cronometro(self))
        self.layout.addWidget(self.stop_button)

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: atualizar_tempo(self))
        self.start_time = None
        self.elapsed_time = 0
        self.running = False

        # Tempo Total Trabalhado do Dia Filtrado
        self.total_trabalho_label = QLabel("Total Trabalhado: 00h 00m")
        self.total_trabalho_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.layout.addWidget(self.total_trabalho_label)

        # 🔹 Layout horizontal para calendário e botões
        calendario_layout = QHBoxLayout()

        self.data_filtro = QDateEdit()
        self.data_filtro.setCalendarPopup(True)
        self.data_filtro.setDate(QDate.currentDate())
        self.data_filtro.dateChanged.connect(lambda: carregar_grid(self))
        calendario_layout.addWidget(self.data_filtro)

        # 🔧 Estilo comum para botões pequenos
        def configurar_botao(botao):
            botao.setFixedSize(QSize(30, 30))
            botao.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            botao.setStyleSheet("font-size: 12px; padding: 2px;")

        # 🔘 Botão ⬅️ Voltar 1 dia
        btn_voltar = QPushButton("←")
        btn_voltar.clicked.connect(lambda: self.data_filtro.setDate(self.data_filtro.date().addDays(-1)))
        configurar_botao(btn_voltar)
        calendario_layout.addWidget(btn_voltar)

        # 🔘 Botão ➡️ Avançar 1 dia
        btn_avancar = QPushButton("→")
        btn_avancar.clicked.connect(lambda: self.data_filtro.setDate(self.data_filtro.date().addDays(1)))
        configurar_botao(btn_avancar)
        calendario_layout.addWidget(btn_avancar)

        # 🔘 Botão 📅 Hoje
        btn_hoje = QPushButton("📅")
        btn_hoje.clicked.connect(lambda: self.data_filtro.setDate(QDate.currentDate()))
        configurar_botao(btn_hoje)
        calendario_layout.addWidget(btn_hoje)

        # 🔹 Adiciona o layout no layout principal
        self.layout.addLayout(calendario_layout)

        # Grid de Registros
        self.grid = QTableWidget()
        self.grid.setColumnCount(5)
        self.grid.setHorizontalHeaderLabels(["Hora Inicial", "Hora Final", "Duração", "Atividade", "Ações"])
        self.grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Ativa ordenação das colunas        
        self.grid.setSortingEnabled(True)

        
        # Definindo tamanho das colunas 
        self.grid.setColumnWidth(0, 70)     # Hora Inicial
        self.grid.setColumnWidth(1, 70)     # Hora Final
        self.grid.setColumnWidth(2, 100)    # Duracao
        self.grid.setColumnWidth(3, 420)    # Atividade
        self.grid.setColumnWidth(4, 100)    # Acoes
        self.grid.setColumnWidth(5, 50)     # Checkbox 
        
        self.grid.itemChanged.connect(lambda item: atualizar_registro(self, item.row(), item.column()))  # 🔹 Monitorar edições    
        self.layout.addWidget(self.grid)

        # Formulário para Adicionar Registros Manualmente
        form_layout = QHBoxLayout()

        self.hora_inicio_input = QTimeEdit()
        self.hora_inicio_input.setDisplayFormat("HH:mm")
        form_layout.addWidget(self.hora_inicio_input)

        self.hora_fim_input = QTimeEdit()
        self.hora_fim_input.setDisplayFormat("HH:mm")
        form_layout.addWidget(self.hora_fim_input)

        self.atividade_input = QLineEdit()
        self.atividade_input.setPlaceholderText("Descrição da Atividade")
        self.atividade_input.setStyleSheet("color: white;")
        form_layout.addWidget(self.atividade_input)

        self.add_button = QPushButton("➕ Adicionar Registro")
        self.add_button.clicked.connect(lambda: adicionar_registro(self))
        form_layout.addWidget(self.add_button)

        self.layout.addLayout(form_layout)
        
        
        # 🔹 Linha de divisão antes dos filtros de data
        linha_divisoria = QFrame()
        linha_divisoria.setFrameShape(QFrame.Shape.HLine)
        linha_divisoria.setFrameShadow(QFrame.Shadow.Sunken)
        linha_divisoria.setStyleSheet("background-color: #2e2e2e; max-height: 1px; margin-top: 10px; margin-bottom: 10px; border: none;")
        self.layout.addWidget(linha_divisoria)

        
        
        # Label para status da exportação
        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        carregar_grid(self)  # 🔹 Carregar registros ao iniciar a aplicação

        # Layout para os campos de data
        export_layout = QHBoxLayout()
        self.data_de_filtro = QDateEdit()
        self.data_de_filtro.setCalendarPopup(True)
        self.data_de_filtro.setDate(QDate.currentDate())
        export_layout.addWidget(QLabel("De:"))
        export_layout.addWidget(self.data_de_filtro)

        self.data_ate_filtro = QDateEdit()
        self.data_ate_filtro.setCalendarPopup(True)
        self.data_ate_filtro.setDate(QDate.currentDate())
        export_layout.addWidget(QLabel("Até:"))
        export_layout.addWidget(self.data_ate_filtro)

        self.layout.addLayout(export_layout)  # 🔹 Adiciona os filtros abaixo da GRID

        # 🔹 Layout horizontal para botões de exportação
        export_buttons_layout = QHBoxLayout()

        self.export_button = QPushButton("📤 Exportar para Excel")
        self.export_button.clicked.connect(lambda: exportar_para_excel(self))
        export_buttons_layout.addWidget(self.export_button)

        self.pdf_button = QPushButton("📄 Exportar para PDF")
        self.pdf_button.clicked.connect(lambda: exportar_para_pdf(self))
        export_buttons_layout.addWidget(self.pdf_button)

        # Adiciona os dois botões no layout principal
        self.layout.addLayout(export_buttons_layout)


        # 🔹 Layout horizontal para botões inferiores
        rodape_layout = QHBoxLayout()

        self.backup_button = QPushButton("🗂️ Backup BD")
        self.backup_button.clicked.connect(lambda: fazer_backup_banco(self))
        rodape_layout.addWidget(self.backup_button)

        self.sobre_button = QPushButton("ℹ️ Sobre")
        self.sobre_button.clicked.connect(lambda: mostrar_sobre(self))
        rodape_layout.addWidget(self.sobre_button)

        self.layout.addLayout(rodape_layout)

        self.setLayout(self.layout)
        
                




def verificar_banco_dados():
    caminho_salvo = carregar_caminho_bd()
    if caminho_salvo:
        return caminho_salvo

    msg = QMessageBox()
    msg.setWindowTitle("Banco de Dados")
    msg.setText("Nenhum banco de dados foi configurado.")
    msg.setInformativeText("Você gostaria de criar um novo banco ou escolher um existente?")
    criar = msg.addButton("Criar Novo", QMessageBox.ButtonRole.AcceptRole)
    escolher = msg.addButton("Escolher Existente", QMessageBox.ButtonRole.YesRole)
    cancelar = msg.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
    msg.setDefaultButton(criar)
    msg.exec()

    if msg.clickedButton() == criar:
        caminho, _ = QFileDialog.getSaveFileName(None, "Criar novo banco", "timesheet.db", "SQLite Database (*.db)")
        if caminho:
            salvar_caminho_bd(caminho)
            return caminho

    elif msg.clickedButton() == escolher:
        caminho, _ = QFileDialog.getOpenFileName(None, "Selecionar banco existente", "", "SQLite Database (*.db)")
        if caminho:
            salvar_caminho_bd(caminho)
            return caminho

    return None


if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        caminho_bd = verificar_banco_dados()
        if not caminho_bd:
            sys.exit()

        from utils.db import criar_tabela
        criar_tabela(caminho_bd)

        window = TimesheetApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        # Evita qualquer crash feio no PyQt
        QMessageBox.critical(None, "Erro Fatal",
            f"Ocorreu um erro inesperado:\n{str(e)}")
        sys.exit(1)



