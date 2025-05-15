import sys
import os
import numpy as np
from PIL import Image
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QScrollArea, QSlider,
                             QTextEdit, QMessageBox)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import math


class SteganographyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Стеганография LSB Matching Revisited")
        self.setGeometry(100, 100, 1200, 800)

        # Инициализация переменных
        self.original_image = None
        self.stego_image = None
        self.zoom_factor = 1

        # Создание интерфейса
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Верхняя панель с кнопками
        button_layout = QHBoxLayout()

        self.load_image_btn = QPushButton("Загрузить изображение")
        self.load_image_btn.clicked.connect(self.load_image)

        self.load_message_btn = QPushButton("Загрузить сообщение")
        self.load_message_btn.clicked.connect(self.load_message)
        self.load_message_btn.setEnabled(False)

        self.hide_data_btn = QPushButton("Скрыть данные")
        self.hide_data_btn.clicked.connect(self.hide_data)
        self.hide_data_btn.setEnabled(False)

        self.save_stego_btn = QPushButton("Сохранить стегоконтейнер")
        self.save_stego_btn.clicked.connect(self.save_stego_image)
        self.save_stego_btn.setEnabled(False)

        button_layout.addWidget(self.load_image_btn)
        button_layout.addWidget(self.load_message_btn)
        button_layout.addWidget(self.hide_data_btn)
        button_layout.addWidget(self.save_stego_btn)

        main_layout.addLayout(button_layout)

        # Слайдер для увеличения
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Увеличение:")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(10)
        self.zoom_slider.setValue(1)
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.setTickInterval(1)
        self.zoom_slider.valueChanged.connect(self.update_zoom)

        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_slider)

        main_layout.addLayout(zoom_layout)

        # Область для отображения изображений
        images_layout = QHBoxLayout()

        # Оригинальное изображение
        original_layout = QVBoxLayout()
        original_label = QLabel("Оригинальное изображение:")
        self.original_image_label = QLabel()
        self.original_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.original_scroll_area = QScrollArea()
        self.original_scroll_area.setWidgetResizable(True)
        self.original_scroll_area.setWidget(self.original_image_label)

        original_layout.addWidget(original_label)
        original_layout.addWidget(self.original_scroll_area)

        # Стегоконтейнер
        stego_layout = QVBoxLayout()
        stego_label = QLabel("Стегоконтейнер:")
        self.stego_image_label = QLabel()
        self.stego_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stego_scroll_area = QScrollArea()
        self.stego_scroll_area.setWidgetResizable(True)
        self.stego_scroll_area.setWidget(self.stego_image_label)

        stego_layout.addWidget(stego_label)
        stego_layout.addWidget(self.stego_scroll_area)

        images_layout.addLayout(original_layout)
        images_layout.addLayout(stego_layout)

        main_layout.addLayout(images_layout)

        # Область для ввода/вывода текста и информации
        text_layout = QHBoxLayout()

        self.message_text = QTextEdit()
        self.message_text.setPlaceholderText("Введите сообщение для скрытия или загрузите файл...")

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setPlaceholderText("Информация о стеганографическом процессе будет отображаться здесь...")

        text_layout.addWidget(self.message_text)
        text_layout.addWidget(self.info_text)

        main_layout.addLayout(text_layout)

        self.setCentralWidget(central_widget)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Image Files (*.bmp *.jpg *.jpeg)")
        if file_path:
            try:
                # Загрузка и проверка изображения
                img = Image.open(file_path)
                if img.mode != "L":
                    img = img.convert('L')
                

                self.original_image = img
                self.display_image(img, self.original_image_label)

                # Обновление информации
                width, height = img.size
                self.info_text.setText(f"Загружено изображение: {os.path.basename(file_path)}\n"
                                       f"Размер: {width}x{height} пикселей\n"
                                       f"Формат: {img.mode}\n"
                                       f"Максимальная емкость: {(width * height) // 2} бит "
                                       f"({(width * height) // 16} символов)")

                self.load_message_btn.setEnabled(True)
                self.message_text.setEnabled(True)
                self.hide_data_btn.setEnabled(True)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение: {str(e)}")

    def load_message(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите текстовый файл", "", "Text Files (*.txt)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    message = file.read()
                self.message_text.setText(message)

                # Проверка размера сообщения
                if self.original_image:
                    width, height = self.original_image.size
                    max_chars = (width * height) // 16  # предполагаем, что на один символ нужно 8 бит
                    if len(message) > max_chars:
                        QMessageBox.warning(self, "Предупреждение",
                                            f"Сообщение слишком длинное! Максимальная длина: {max_chars} символов.\n"
                                            f"Сообщение будет обрезано.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить сообщение: {str(e)}")

    def hide_data(self):
        if not self.original_image:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение!")
            return

        message = self.message_text.toPlainText()
        if not message:
            QMessageBox.warning(self, "Ошибка", "Введите сообщение для скрытия!")
            return

        # Преобразование сообщения в биты
        message_bits = self.text_to_bits(message)

        # Проверка размера сообщения
        width, height = self.original_image.size
        max_bits = (width * height) // 2
        if len(message_bits) > max_bits:
            QMessageBox.warning(self, "Предупреждение",
                                f"Сообщение слишком длинное! Будет сохранено только {max_bits // 8} символов.")
            message_bits = message_bits[:max_bits]

        # Применение LSB Matching Revisited
        img_array = np.array(self.original_image)
        stego_array = self.lsb_matching_revisited(img_array, message_bits)

        # Создание стегоконтейнера
        self.stego_image = Image.fromarray(stego_array)
        self.display_image(self.stego_image, self.stego_image_label)

        # Расчет PSNR
        psnr = self.calculate_psnr(np.array(self.original_image), stego_array)

        # Обновление информации
        embedding_capacity = (width * height) // 2
        actual_embedded = len(message_bits)

        self.info_text.append(f"\n--- Результаты встраивания ---\n"
                              f"Размер сообщения: {len(message)} символов ({actual_embedded} бит)\n"
                              f"Емкость встраивания: {embedding_capacity} бит\n"
                              f"Использовано: {actual_embedded / embedding_capacity * 100:.2f}% емкости\n"
                              f"PSNR: {psnr:.2f} дБ")

        self.save_stego_btn.setEnabled(True)

    def text_to_bits(self, text):
        """Преобразует текст в последовательность бит"""
        bits = []
        for char in text:
            # Преобразование символа в 8 бит
            byte = format(ord(char), '08b')
            for bit in byte:
                bits.append(int(bit))
        return bits

    def lsb_matching_revisited(self, img_array, message_bits):
        """Реализация метода LSB Matching Revisited"""
        height, width = img_array.shape
        stego_array = img_array.copy()

        # Добавляем длину сообщения в начало
        message_length = len(message_bits)
        length_bits = format(message_length, '032b')
        full_message = [int(bit) for bit in length_bits] + message_bits

        # Встраивание данных
        idx = 0
        for i in range(height):
            for j in range(0, width, 2):
                if j + 1 < width and idx < len(full_message):
                    # Получаем пару пикселей
                    x1 = stego_array[i, j]
                    x2 = stego_array[i, j + 1]

                    # Извлекаем LSB
                    lsb1 = x1 & 1
                    lsb2 = x2 & 1

                    # Бит для встраивания
                    m = full_message[idx]

                    # Применение LSB Matching Revisited
                    if lsb1 != m:
                        # Если LSB первого пикселя не равен биту сообщения
                        if (x1 % 2 == 0 and x2 % 2 == 0) or (x1 % 2 == 1 and x2 % 2 == 1):
                            # Оба пикселя имеют одинаковую четность
                            x1 = x1 + 1 if x1 < 255 else x1 - 1
                        else:
                            # Пиксели имеют разную четность
                            x2 = x2 + 1 if x2 < 255 else x2 - 1

                    # Обновляем пиксели
                    stego_array[i, j] = x1
                    stego_array[i, j + 1] = x2

                    idx += 1

                    if idx >= len(full_message):
                        break
            if idx >= len(full_message):
                break

        return stego_array

    def calculate_psnr(self, original, stego):
        """Расчет PSNR (Peak Signal-to-Noise Ratio)"""
        mse = np.mean((original - stego) ** 2)
        if mse == 0:
            return float('inf')
        max_pixel = 255.0
        psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
        return psnr

    def display_image(self, img, label):
        """Отображение изображения с учетом масштаба"""
        if img:
            # Применение масштаба
            width, height = img.size
            scaled_width = int(width * self.zoom_factor)
            scaled_height = int(height * self.zoom_factor)

            # Преобразование в QImage
            img_array = np.array(img)
            h, w = img_array.shape
            bytes_per_line = w
            q_img = QImage(img_array.data, w, h, bytes_per_line, QImage.Format.Format_Grayscale8)

            # Создание и масштабирование QPixmap
            pixmap = QPixmap.fromImage(q_img)
            pixmap = pixmap.scaled(scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio)

            label.setPixmap(pixmap)
            label.resize(pixmap.size())

    def update_zoom(self):
        """Обновление масштаба изображений"""
        self.zoom_factor = self.zoom_slider.value()
        if self.original_image:
            self.display_image(self.original_image, self.original_image_label)
        if self.stego_image:
            self.display_image(self.stego_image, self.stego_image_label)

    def save_stego_image(self):
        """Сохранение стегоконтейнера"""
        if not self.stego_image:
            QMessageBox.warning(self, "Ошибка", "Стегоконтейнер не создан!")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить стегоконтейнер", "", "BMP Files (*.bmp)")
        if file_path:
            try:
                # Убедимся, что файл имеет расширение .bmp
                if not file_path.lower().endswith('.bmp'):
                    file_path += '.bmp'

                self.stego_image.save(file_path)
                QMessageBox.information(self, "Успех", f"Стегоконтейнер успешно сохранен в {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить стегоконтейнер: {str(e)}")

    def extract_data(self):
        """Извлечение данных из стегоконтейнера (дополнительная функция)"""
        if not self.stego_image:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте стегоконтейнер!")
            return

        # Преобразование в массив
        stego_array = np.array(self.stego_image)
        height, width = stego_array.shape

        # Извлечение данных
        extracted_bits = []

        # Сначала извлекаем 32 бита длины сообщения
        idx = 0
        length_bits = []

        for i in range(height):
            for j in range(0, width, 2):
                if j + 1 < width and idx < 32:
                    x1 = stego_array[i, j]
                    x2 = stego_array[i, j + 1]

                    # Извлекаем бит согласно алгоритму LSB Matching Revisited
                    extracted_bit = x1 & 1
                    length_bits.append(extracted_bit)

                    idx += 1

                    if idx >= 32:
                        break
            if idx >= 32:
                break

        # Преобразуем биты длины в число
        message_length = 0
        for bit in length_bits:
            message_length = (message_length << 1) | bit

        # Теперь извлекаем само сообщение
        idx = 0
        for i in range(height):
            for j in range(0, width, 2):
                if j + 1 < width:
                    # Пропускаем первые 32 бита (длина)
                    if idx < 32:
                        idx += 1
                        continue

                    if len(extracted_bits) >= message_length:
                        break

                    x1 = stego_array[i, j]
                    x2 = stego_array[i, j + 1]

                    # Извлекаем бит
                    extracted_bit = x1 & 1
                    extracted_bits.append(extracted_bit)

                    if len(extracted_bits) >= message_length:
                        break
            if len(extracted_bits) >= message_length:
                break

        # Преобразуем биты в текст
        extracted_text = self.bits_to_text(extracted_bits)

        return extracted_text

    def bits_to_text(self, bits):
        """Преобразует последовательность бит в текст"""
        text = ""
        # Группируем биты по 8 (один символ)
        for i in range(0, len(bits), 8):
            byte = bits[i:i + 8]
            if len(byte) == 8:  # Проверяем, что у нас полный байт
                # Преобразуем 8 бит в символ
                char_code = 0
                for bit in byte:
                    char_code = (char_code << 1) | bit
                text += chr(char_code)
        return text

def main():
    app = QApplication(sys.argv)
    window = SteganographyApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()