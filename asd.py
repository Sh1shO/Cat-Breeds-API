import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QComboBox, QPushButton, QDialog, QFormLayout, QTextEdit, QLineEdit)
from PySide6.QtCore import Qt

class CatDetailDialog(QDialog):
    def __init__(self, cat_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подробная информация о коте")
        self.setModal(True)
        self.cat_data = cat_data
        self.is_editing = False
        
        # Основной layout
        layout = QFormLayout()
        
        # Поля для отображения/редактирования
        self.name_edit = QLineEdit(cat_data.get('name', ''))
        self.origin_edit = QLineEdit(cat_data.get('origin', ''))
        self.temperament_edit = QTextEdit(cat_data.get('temperament', ''))
        self.description_edit = QTextEdit(cat_data.get('description', ''))
        
        # Начально делаем поля только для чтения
        self.set_read_only(True)
        
        # Добавляем поля в layout
        layout.addRow("Название породы:", self.name_edit)
        layout.addRow("Происхождение:", self.origin_edit)
        layout.addRow("Темперамент:", self.temperament_edit)
        layout.addRow("Описание:", self.description_edit)
        
        # Кнопка редактирования
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.toggle_edit)
        layout.addWidget(self.edit_button)
        
        self.setLayout(layout)
        self.resize(400, 300)
    
    def set_read_only(self, value):
        self.name_edit.setReadOnly(value)
        self.origin_edit.setReadOnly(value)
        self.temperament_edit.setReadOnly(value)
        self.description_edit.setReadOnly(value)
    
    def toggle_edit(self):
            # Переключение между режимами редактирования и просмотра
            if self.is_editing:
                # Сохранение изменений в исходные данные кота
                self.cat_data['name'] = self.name_edit.text()
                self.cat_data['origin'] = self.origin_edit.text()
                self.cat_data['temperament'] = self.temperament_edit.toPlainText()
                self.cat_data['description'] = self.description_edit.toPlainText()
                self.edit_button.setText("Редактировать")  # Возвращаем текст кнопки
            else:
                self.edit_button.setText("Сохранить")  # Устанавливаем текст кнопки для сохранения
            
            self.is_editing = not self.is_editing  # Переключаем флаг редактирования
            self.set_read_only(not self.is_editing)  # Переключаем режим полей

class CatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cat Breeds")
        self.resize(800, 400)
        
        # Получаем данные из API
        self.cat_data = self.fetch_cat_data()
        
        # Основной widget и layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Фильтр по происхождению
        self.origin_filter = QComboBox()
        self.origin_filter.addItem("Все страны")
        origins = sorted(set(cat.get('origin', '') for cat in self.cat_data))
        self.origin_filter.addItems(origins)
        self.origin_filter.currentTextChanged.connect(self.filter_table)
        layout.addWidget(self.origin_filter)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Origin", "Temperament"])
        self.populate_table(self.cat_data)
        self.table.doubleClicked.connect(self.show_details)
        layout.addWidget(self.table)
        
        # Кнопка удаления
        self.delete_button = QPushButton("Удалить выбранного кота")
        self.delete_button.clicked.connect(self.delete_selected)
        layout.addWidget(self.delete_button)
    
    def fetch_cat_data(self):
        try:
            response = requests.get("https://api.thecatapi.com/v1/breeds")
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при загрузке данных: {e}")
            return []
    
    def populate_table(self, data):
        self.table.setRowCount(len(data))
        for row, cat in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(cat.get('name', '')))
            self.table.setItem(row, 1, QTableWidgetItem(cat.get('origin', '')))
            self.table.setItem(row, 2, QTableWidgetItem(cat.get('temperament', '')))
        self.table.resizeColumnsToContents()
    
    def filter_table(self):
            # Фильтрация данных в таблице по выбранному происхождению
            selected_origin = self.origin_filter.currentText()  # Получаем выбранное значение фильтра
            if selected_origin == "Все страны":
                filtered_data = self.cat_data  # Показываем все данные, если выбраны "Все страны"
            else:
                # Фильтруем данные по выбранной стране происхождения
                filtered_data = [cat for cat in self.cat_data if cat.get('origin', '') == selected_origin]
            self.populate_table(filtered_data)  # Обновляем таблицу с отфильтрованными данными
    
    def show_details(self):
        row = self.table.currentRow()
        if row >= 0:
            selected_name = self.table.item(row, 0).text()
            cat_info = next(cat for cat in self.cat_data if cat.get('name') == selected_name)
            dialog = CatDetailDialog(cat_info, self)
            dialog.exec()
            self.filter_table()
    
    def delete_selected(self):
            # Удаление выбранной породы из списка
            row = self.table.currentRow()  # Получаем индекс выбранной строки
            if row >= 0:
                selected_name = self.table.item(row, 0).text()  # Получаем название породы
                # Удаляем породу из списка данных
                self.cat_data = [cat for cat in self.cat_data if cat.get('name') != selected_name]
                self.filter_table()  # Обновляем таблицу после удаления

app = QApplication([])
window = CatApp()
window.show()
app.exec()
