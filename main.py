"""Головний модуль запуску графічного застосунку PyQt5."""

import sys
import random
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
    QComboBox, QSpinBox, QMessageBox, QTabWidget, QLabel, QDialog, QFormLayout, QHeaderView
)

import database
import services

# --- ТЕМА ТА СТИЛІ (QSS) ---
MODERN_STYLE = """
QMainWindow, QDialog {
    background-color: #f4f6f9;
}
QTabWidget::pane {
    border: 1px solid #dcdfe6;
    background: #ffffff;
    border-radius: 8px;
}
QTabBar::tab {
    background: #e4e7ed;
    color: #2c3e50;
    padding: 10px 20px;
    font-weight: bold;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #3498db;
    border-bottom: 2px solid #3498db;
}
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2980b9;
}
QPushButton:pressed {
    background-color: #1f618d;
}
QLineEdit, QComboBox, QSpinBox {
    border: 1px solid #dcdfe6;
    border-radius: 6px;
    padding: 6px 12px;
    background-color: #ffffff;
    font-size: 13px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #3498db;
}
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
    gridline-color: #ecf0f1;
    border-radius: 6px;
}
QHeaderView::section {
    background-color: #34495e;
    color: white;
    font-weight: bold;
    padding: 6px;
    border: none;
}
"""


class AddStudentDialog(QDialog):
    """Окреме вікно для додавання нового студента з автогенерацією квитка."""
    def __init__(self, groups, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додавання нового студента")
        self.resize(380, 240)

        layout = QFormLayout(self)

        self.input_last_name = QLineEdit()
        self.input_last_name.setPlaceholderText("Введіть прізвище")
        layout.addRow("Прізвище:", self.input_last_name)

        self.input_first_name = QLineEdit()
        self.input_first_name.setPlaceholderText("Введіть ім'я")
        layout.addRow("Ім'я:", self.input_first_name)

        auto_ticket = f"KB-{random.randint(100000, 999999)}"
        self.input_ticket = QLineEdit(auto_ticket)
        layout.addRow("№ квитка (авто):", self.input_ticket)

        self.combo_group = QComboBox()
        self.combo_group.addItem("Без групи", None)
        for g_id, g_name in groups:
            self.combo_group.addItem(g_name, g_id)
        layout.addRow("Група:", self.combo_group)

        btn_save = QPushButton("Зберегти студента")
        btn_save.clicked.connect(self.accept)
        layout.addRow(btn_save)

    def get_data(self):
        return (
            self.input_first_name.text().strip(),
            self.input_last_name.text().strip(),
            self.input_ticket.text().strip(),
            self.combo_group.currentData()
        )


class EditStudentDialog(QDialog):
    """Окреме вікно для редагування існуючого студента."""
    def __init__(self, student_data, groups, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редагування студента")
        self.resize(380, 240)

        self.student_id = student_data[0]
        
        layout = QFormLayout(self)

        self.input_last_name = QLineEdit(student_data[6])
        layout.addRow("Прізвище:", self.input_last_name)

        self.input_first_name = QLineEdit(student_data[5])
        layout.addRow("Ім'я:", self.input_first_name)

        self.input_ticket = QLineEdit(student_data[2])
        layout.addRow("№ квитка:", self.input_ticket)

        self.combo_group = QComboBox()
        self.combo_group.addItem("Без групи", None)
        for g_id, g_name in groups:
            self.combo_group.addItem(g_name, g_id)
        
        current_group_id = student_data[7]
        if current_group_id:
            index = self.combo_group.findData(current_group_id)
            if index >= 0:
                self.combo_group.setCurrentIndex(index)

        layout.addRow("Група:", self.combo_group)

        btn_save = QPushButton("Зберегти зміни")
        btn_save.clicked.connect(self.accept)
        layout.addRow(btn_save)

    def get_data(self):
        return (
            self.student_id,
            self.input_first_name.text().strip(),
            self.input_last_name.text().strip(),
            self.input_ticket.text().strip(),
            self.combo_group.currentData()
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Облік студентів та їх успішності")
        self.resize(980, 600)

        database.init_db()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Вкладка 1: Студенти
        self.tab_students = QWidget()
        self.tabs.addTab(self.tab_students, "Студенти")
        self.init_students_tab()

        # Вкладка 2: Оцінки
        self.tab_grades = QWidget()
        self.tabs.addTab(self.tab_grades, "Виставити оцінку")
        self.init_grades_tab()

        # Вкладка 3: Адміністрування
        self.tab_admin = QWidget()
        self.tabs.addTab(self.tab_admin, "Групи та Предмети")
        self.init_admin_tab()

        self.update_comboboxes()
        self.load_students_data()

    def init_students_tab(self):
        layout = QVBoxLayout(self.tab_students)

        # Панель пошуку
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("Пошук:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Прізвище, ім'я або № квитка...")
        search_layout.addWidget(self.search_input)

        search_layout.addWidget(QLabel("Група:"))
        self.combo_filter_group = QComboBox()
        search_layout.addWidget(self.combo_filter_group)

        search_layout.addWidget(QLabel("Сортування:"))
        self.combo_sort = QComboBox()
        self.combo_sort.addItem("За прізвищем (А-Я)", "name_asc")
        self.combo_sort.addItem("За найвищим балом ⬇", "grade_desc")
        self.combo_sort.addItem("За найнижчим балом ⬆", "grade_asc")
        self.combo_sort.currentIndexChanged.connect(self.load_students_data)
        search_layout.addWidget(self.combo_sort)

        btn_search = QPushButton("🔍 Шукати")
        btn_search.clicked.connect(self.load_students_data)
        search_layout.addWidget(btn_search)

        btn_refresh = QPushButton("🔄 Оновити")
        btn_refresh.clicked.connect(self.refresh_all_data)
        search_layout.addWidget(btn_refresh)

        layout.addLayout(search_layout)

        # Таблиця
        self.table_students = QTableWidget()
        self.table_students.setColumnCount(5)
        self.table_students.setHorizontalHeaderLabels(["ID", "ПІБ", "№ Квитка", "Група", "Сер. бал (1-12)"])
        self.table_students.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_students)

        # Кнопки дій
        btn_layout = QHBoxLayout()
        
        btn_open_add_dialog = QPushButton("➕ Додати нового студента")
        btn_open_add_dialog.clicked.connect(self.open_add_student_dialog)
        btn_layout.addWidget(btn_open_add_dialog)

        btn_edit = QPushButton("✏️ Редагувати обраного")
        btn_edit.clicked.connect(self.edit_student_action)
        btn_layout.addWidget(btn_edit)

        btn_delete = QPushButton("❌ Видалити обраного")
        btn_delete.setStyleSheet("background-color: #e74c3c;")
        btn_delete.clicked.connect(self.delete_student_action)
        btn_layout.addWidget(btn_delete)

        layout.addLayout(btn_layout)

    def init_grades_tab(self):
        layout = QVBoxLayout(self.tab_grades)
        form_layout = QHBoxLayout()

        self.combo_grade_student = QComboBox()
        form_layout.addWidget(QLabel("Студент:"))
        form_layout.addWidget(self.combo_grade_student)

        self.combo_grade_subject = QComboBox()
        form_layout.addWidget(QLabel("Предмет:"))
        form_layout.addWidget(self.combo_grade_subject)

        self.spin_grade = QSpinBox()
        self.spin_grade.setRange(1, 12)
        self.spin_grade.setValue(10)
        form_layout.addWidget(QLabel("Оцінка (1-12 балів):"))
        form_layout.addWidget(self.spin_grade)

        btn_save_grade = QPushButton("Зберегти оцінку")
        btn_save_grade.clicked.connect(self.add_grade_action)
        form_layout.addWidget(btn_save_grade)

        layout.addLayout(form_layout)

    def init_admin_tab(self):
        layout = QVBoxLayout(self.tab_admin)

        group_layout = QHBoxLayout()
        self.input_group_name = QLineEdit()
        self.input_group_name.setPlaceholderText("Назва групи (напр. ІСТ-21)")
        btn_add_group = QPushButton("Додати групу")
        btn_add_group.clicked.connect(self.add_group_action)
        group_layout.addWidget(self.input_group_name)
        group_layout.addWidget(btn_add_group)
        layout.addLayout(group_layout)

        subject_layout = QHBoxLayout()
        self.input_subject_name = QLineEdit()
        self.input_subject_name.setPlaceholderText("Назва предмета (напр. ООП)")
        self.spin_subject_hours = QSpinBox()
        self.spin_subject_hours.setRange(1, 300)
        self.spin_subject_hours.setValue(60)

        btn_add_subject = QPushButton("Додати предмет")
        btn_add_subject.clicked.connect(self.add_subject_action)

        subject_layout.addWidget(self.input_subject_name)
        subject_layout.addWidget(QLabel("Годин:"))
        subject_layout.addWidget(self.spin_subject_hours)
        subject_layout.addWidget(btn_add_subject)

        layout.addLayout(subject_layout)

    # --- СЕРВІСНІ ФУНКЦІЇ ---

    def refresh_all_data(self):
        self.update_comboboxes()
        self.load_students_data()
        QMessageBox.information(self, "Оновлено", "Дані успішно оновлено!")

    def load_students_data(self):
        query = self.search_input.text().strip()
        group_filter_id = self.combo_filter_group.currentData()
        sort_order = self.combo_sort.currentData()

        self.students_raw = services.get_all_students_with_info(query, group_filter_id, sort_order)
        self.table_students.setRowCount(len(self.students_raw))

        for row_idx, row_data in enumerate(self.students_raw):
            for col_idx in range(5):
                val_str = str(row_data[col_idx]) if row_data[col_idx] is not None else "-"
                self.table_students.setItem(row_idx, col_idx, QTableWidgetItem(val_str))

    def update_comboboxes(self):
        groups = services.get_all_groups()
        current_filter = self.combo_filter_group.currentData()

        self.combo_filter_group.clear()
        self.combo_filter_group.addItem("Усі групи", None)
        for g_id, g_name in groups:
            self.combo_filter_group.addItem(g_name, g_id)
        
        if current_filter:
            idx = self.combo_filter_group.findData(current_filter)
            if idx >= 0:
                self.combo_filter_group.setCurrentIndex(idx)

        self.combo_grade_student.clear()
        students = services.get_all_students_with_info()
        for s in students:
            self.combo_grade_student.addItem(f"{s[1]} ({s[3]})", s[0])

        self.combo_grade_subject.clear()
        subjects = services.get_all_subjects()
        for sub_id, sub_name, _ in subjects:
            self.combo_grade_subject.addItem(sub_name, sub_id)

    def open_add_student_dialog(self):
        groups = services.get_all_groups()
        dialog = AddStudentDialog(groups, self)
        
        if dialog.exec_() == QDialog.Accepted:
            fn, ln, ticket, g_id = dialog.get_data()
            if not fn or not ln or not ticket:
                QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")
                return
            try:
                services.add_student(fn, ln, ticket, g_id)
                self.refresh_all_data()
                QMessageBox.information(self, "Успіх", "Студента успішно додано!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося додати студента:\n{e}")

    def edit_student_action(self):
        row = self.table_students.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Помилка", "Оберіть студента для редагування!")
            return

        student_data = self.students_raw[row]
        groups = services.get_all_groups()

        dialog = EditStudentDialog(student_data, groups, self)
        if dialog.exec_() == QDialog.Accepted:
            s_id, fn, ln, ticket, g_id = dialog.get_data()
            if not fn or not ln or not ticket:
                QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")
                return
            try:
                services.update_student(s_id, fn, ln, ticket, g_id)
                self.refresh_all_data()
                QMessageBox.information(self, "Успіх", "Дані студента оновлено!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося оновити дані:\n{e}")

    def delete_student_action(self):
        row = self.table_students.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Помилка", "Оберіть студента у таблиці!")
            return

        student_id = int(self.table_students.item(row, 0).text())
        student_name = self.table_students.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "Підтвердження",
            f"Ви дійсно бажаєте видалити студента '{student_name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            services.delete_student(student_id)
            self.refresh_all_data()

    def add_group_action(self):
        g_name = self.input_group_name.text().strip()
        if not g_name:
            QMessageBox.warning(self, "Помилка", "Введіть назву групи!")
            return
        try:
            services.add_group(g_name)
            self.input_group_name.clear()
            self.refresh_all_data()
            QMessageBox.information(self, "Успіх", "Групу додано!")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка створення групи:\n{e}")

    def add_subject_action(self):
        s_name = self.input_subject_name.text().strip()
        hours = self.spin_subject_hours.value()
        if not s_name:
            QMessageBox.warning(self, "Помилка", "Введіть назву предмета!")
            return
        try:
            services.add_subject(s_name, hours)
            self.input_subject_name.clear()
            self.refresh_all_data()
            QMessageBox.information(self, "Успіх", "Предмет додано!")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка створення предмета:\n{e}")

    def add_grade_action(self):
        student_id = self.combo_grade_student.currentData()
        subject_id = self.combo_grade_subject.currentData()
        grade = self.spin_grade.value()
        today = datetime.now().strftime("%Y-%m-%d")

        if not student_id or not subject_id:
            QMessageBox.warning(self, "Помилка", "Спочатку створіть студента та предмет!")
            return

        try:
            services.add_grade(student_id, subject_id, grade, today)
            self.refresh_all_data()
            QMessageBox.information(self, "Успіх", "Оцінку збережено!")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти оцінку:\n{e}")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_STYLE)  # Застосування стилів QSS
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()