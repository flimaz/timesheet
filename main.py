import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, 
    QHeaderView, QHBoxLayout, QDateEdit, QTimeEdit, QLineEdit
)
from PyQt6.QtCore import QTimer, QDate
from PyQt6.QtGui import QFont, QIcon
from utils.funcoes import (
    aplicar_tema_escuro, carregar_grid, adicionar_registro,
    iniciar_cronometro, parar_cronometro, atualizar_tempo, atualizar_registro, exportar_para_excel, exportar_para_pdf
)

class TimesheetApp(QWidget):
    def __init__(self):
        super().__init__()

        # Definir Ícone do Aplicativo
        self.setWindowIcon(QIcon("assets/TS.ico"))  # Caminho para o ícone

        self.setWindowTitle("Timesheet Tracker - By: Luiz Lima")
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

        # Seletor de Data com Calendário
        self.data_filtro = QDateEdit()
        self.data_filtro.setCalendarPopup(True)
        self.data_filtro.setDate(QDate.currentDate())
        self.data_filtro.dateChanged.connect(lambda: carregar_grid(self))
        self.layout.addWidget(self.data_filtro)

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
        
        
        # Label para status da exportação
        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        carregar_grid(self)  # 🔹 Carregar registros ao iniciar a aplicação

        # NOVO RECURSO: EXPORTAR PARA EXCEL

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

        # Botão para exportar para Excel
        self.export_button = QPushButton("📤 Exportar para Excel")
        self.export_button.clicked.connect(lambda: exportar_para_excel(self))
        self.layout.addWidget(self.export_button)
        
        # Botão para exportar para PDF
        self.pdf_button = QPushButton("📄 Exportar para PDF")
        self.pdf_button.clicked.connect(lambda: exportar_para_pdf(self))
        self.layout.addWidget(self.pdf_button)


        self.setLayout(self.layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimesheetApp()
    window.show()
    sys.exit(app.exec())
