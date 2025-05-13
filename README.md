# 🕒 Timesheet Tracker

O **Timesheet Tracker** é uma aplicação desktop desenvolvida em Python com PyQt6 para controle de atividades e gestão de tempo. Ideal para quem deseja registrar, visualizar e exportar tarefas diárias de forma prática e organizada.

---

## ✨ Funcionalidades

- ✅ Registro de atividades com hora inicial, final e descrição e checkbox para lançamento em sistema externo (ex. service Max)
- ⏱️ Cálculo automático da duração de cada tarefa
- 📅 Filtros por período (De / Até)
- 📤 Exportação para **Excel** e **PDF**
- 🗂️ Backup manual do banco de dados (SQLite)
- ❌ Tratamento de erros (ex: arquivo aberto durante exportação)

---

## 🛠️ Tecnologias

- Python 3
- PyQt6
- SQLite
- Pandas
- ReportLab
- PyInstaller

---

## 🚀 Executável

O sistema pode ser gerado como `.exe` usando o PyInstaller:

```bash
pyinstaller --noconfirm --onefile --windowed --icon=assets/TS.ico main.py
