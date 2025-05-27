import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QTabWidget, QMessageBox, QFileDialog, QDockWidget,
    QTextEdit, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QClipboard

class BookManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku")
        self.setGeometry(80, 80, 800, 600)
        self.statusBar().showMessage("I Gede Manik Ariyasa - F1D022046")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setup_ui()
        self.create_db()
        self.load_data()
        self.setup_dock()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tab_data = QWidget()
        self.tab_export = QWidget()
        self.tabs.addTab(self.tab_data, "Data Buku")
        self.tabs.addTab(self.tab_export, "Ekspor")

        layout.addWidget(self.tabs)
        self.central_widget.setLayout(layout)

        self.setup_data_tab()
        self.setup_export_tab()

    def setup_data_tab(self):
        tab_layout = QVBoxLayout()

        # Scrollable content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        form_layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Judul")
        self.paste_btn = QPushButton("Paste from Clipboard")
        self.paste_btn.clicked.connect(self.paste_from_clipboard)

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Pengarang")
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Kategori")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Tahun Terbit")

        self.save_btn = QPushButton("Simpan")
        self.save_btn.setFixedWidth(150)
        self.save_btn.clicked.connect(self.save_data)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul...")
        self.search_input.textChanged.connect(self.search_data)

        form_layout.addWidget(self.title_input)
        form_layout.addWidget(self.paste_btn)
        form_layout.addWidget(self.author_input)
        form_layout.addWidget(self.category_input)
        form_layout.addWidget(self.year_input)
        form_layout.addWidget(self.save_btn)
        form_layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Kategori", "Tahun"])
        self.table.cellChanged.connect(self.update_data)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        form_layout.addWidget(self.table)

        # Delete Button
        self.delete_btn = QPushButton("Hapus Data")
        self.delete_btn.setFixedWidth(150)
        self.delete_btn.setStyleSheet("background-color: orange; font-weight: bold;")
        self.delete_btn.clicked.connect(self.delete_data)
        form_layout.addWidget(self.delete_btn)

        content_widget.setLayout(form_layout)
        scroll_area.setWidget(content_widget)
        tab_layout.addWidget(scroll_area)

        self.tab_data.setLayout(tab_layout)

    def setup_export_tab(self):
        layout = QVBoxLayout()
        export_btn = QPushButton("Ekspor ke CSV")
        export_btn.clicked.connect(self.export_csv)
        layout.addWidget(export_btn)
        self.tab_export.setLayout(layout)

    def setup_dock(self):
        self.dock = QDockWidget("Petunjuk / Info", self)
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText("Gunakan form untuk menambah buku, gunakan pencarian untuk menemukan judul.")
        self.dock.setWidget(info_text)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

    def create_db(self):
        self.conn = sqlite3.connect("books.db")
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                category TEXT,
                year INTEGER
            )
        ''')
        self.conn.commit()

    def save_data(self):
        title = self.title_input.text()
        author = self.author_input.text()
        category = self.category_input.text()
        year = self.year_input.text()

        if not (title and author and category and year):
            QMessageBox.warning(self, "Error", "Semua field harus diisi.")
            return

        try:
            self.c.execute("INSERT INTO books (title, author, category, year) VALUES (?, ?, ?, ?)",
                           (title, author, category, int(year)))
            self.conn.commit()
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def clear_inputs(self):
        self.title_input.clear()
        self.author_input.clear()
        self.category_input.clear()
        self.year_input.clear()

    def load_data(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.c.execute("SELECT * FROM books")
        for row_index, row_data in enumerate(self.c.fetchall()):
            self.table.insertRow(row_index)
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                if col_index == 0:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row_index, col_index, item)
        self.table.blockSignals(False)

    def search_data(self, text):
        self.table.setRowCount(0)
        self.c.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + text + '%',))
        for row_index, row_data in enumerate(self.c.fetchall()):
            self.table.insertRow(row_index)
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                if col_index == 0:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row_index, col_index, item)

    def update_data(self, row, column):
        if column == 0:
            return

        record_id = int(self.table.item(row, 0).text())
        new_value = self.table.item(row, column).text()
        field = ["title", "author", "category", "year"][column - 1]

        if field == "year":
            try:
                new_value = int(new_value)
            except ValueError:
                QMessageBox.warning(self, "Error", "Tahun harus berupa angka.")
                self.load_data()
                return

        self.c.execute(f"UPDATE books SET {field} = ? WHERE id = ?", (new_value, record_id))
        self.conn.commit()

    def delete_data(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Pilih Baris", "Pilih data yang ingin dihapus.")
            return

        record_id = int(self.table.item(selected, 0).text())
        self.c.execute("DELETE FROM books WHERE id = ?", (record_id,))
        self.conn.commit()
        self.load_data()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv)")
        if not path:
            return

        self.c.execute("SELECT * FROM books")
        records = self.c.fetchall()
        with open(path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Judul", "Pengarang", "Kategori", "Tahun"])
            writer.writerows(records)
        QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {path}")

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.title_input.setText(clipboard.text())

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookManager()
    window.show()
    sys.exit(app.exec_())
