import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import random
from bitarray import bitarray
import os

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography Tool")
        self.container_image = None
        self.stego_image = None
        self.message_bits = []
        self.key = 12345
        self.extract_mode_standard = tk.BooleanVar(value=True)
        self.extract_mode_hash = tk.BooleanVar(value=False)
        self.colors = {
            "primary": "#4a6fa5",
            "primary_dark": "#3d5d8a",
            "secondary": "#6c757d",
            "bg": "#f8f9fa",
            "text": "#212529",
            "light_accent": "#e9ecef",
            "success": "#28a745",
            "warning": "#ffc107"
        }
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_style()
        self.setup_ui()

    def configure_style(self):
        self.style.configure('TButton', background=self.colors["primary"], foreground='white', font=('Segoe UI', 10), padding=6)
        self.style.map('TButton', background=[('active', self.colors["primary_dark"])])
        self.style.configure('TLabel', background=self.colors["bg"], foreground=self.colors["text"], font=('Segoe UI', 10))
        self.style.configure('TEntry', fieldbackground=self.colors["light_accent"], font=('Segoe UI', 10))
        self.style.configure('TFrame', background=self.colors["bg"])
        self.style.configure('Primary.TButton', background=self.colors["primary"], foreground='white')
        self.style.configure('Success.TButton', background=self.colors["success"], foreground='white')
        self.style.map('Success.TButton', background=[('active', '#218838')])
        self.style.configure('Secondary.TButton', background=self.colors["secondary"], foreground='white')
        self.style.map('Secondary.TButton', background=[('active', '#5a6268')])

    def setup_ui(self):
        self.root.geometry("800x600")
        self.root.configure(bg=self.colors["bg"])

        main_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(header_frame, text="Steganography Tool", font=('Segoe UI', 16, 'bold'), bg=self.colors["bg"], fg=self.colors["primary"])
        title_label.pack(side=tk.LEFT)

        file_frame = ttk.LabelFrame(main_frame, text="Image", padding="10 10 10 10")
        file_frame.pack(fill=tk.X, pady=(0, 15))

        self.file_status = tk.StringVar(value="Image not loaded")
        file_status_label = ttk.Label(file_frame, textvariable=self.file_status)
        file_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        load_btn = ttk.Button(file_frame, text="Load Image", command=self.load_image, style='TButton')
        load_btn.pack(side=tk.LEFT, padx=(10, 0))

        message_frame = ttk.LabelFrame(main_frame, text="Message", padding="10 10 10 10")
        message_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(message_frame, text="Enter text to embed:").pack(anchor=tk.W, pady=(0, 5))

        self.message_entry = ttk.Entry(message_frame, width=80, font=('Segoe UI', 10))
        self.message_entry.pack(fill=tk.X, pady=(0, 10))

        btn_frame = ttk.Frame(message_frame, style='TFrame')
        btn_frame.pack(fill=tk.X)

        embed_standard_btn = ttk.Button(btn_frame, text="Embed Message (Standard)", command=self.embed_message_standard, style='Success.TButton')
        embed_standard_btn.pack(side=tk.LEFT)

        embed_hash_btn = ttk.Button(btn_frame, text="Embed Message (with Hash)", command=self.embed_with_hash, style='Primary.TButton')
        embed_hash_btn.pack(side=tk.LEFT, padx=(10, 0))

        extract_btn = ttk.Button(btn_frame, text="Extract Message", command=self.extract_message, style='Secondary.TButton')
        extract_btn.pack(side=tk.LEFT, padx=(10, 0))

        result_frame = ttk.LabelFrame(main_frame, text="Result", padding="10 10 10 10")
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(result_frame, wrap=tk.WORD, bg=self.colors["light_accent"], relief=tk.FLAT, font=('Segoe UI', 10), height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state='normal')
        self.output_text.bind("<Control-c>", lambda e: self.root.clipboard_append(self.output_text.selection_get()))

        # ---------------------------
        mode_frame = ttk.Frame(message_frame, style='TFrame')
        mode_frame.pack(anchor=tk.W, pady=(10, 0))

        ttk.Label(mode_frame, text="Extraction mode:").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Checkbutton(
            mode_frame, text="Standard", variable=self.extract_mode_standard
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Checkbutton(
            mode_frame, text="With Hash", variable=self.extract_mode_hash
        ).pack(side=tk.LEFT)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.bmp")])
        if path:
            try:
                image = Image.open(path).convert('L')
                image_array = np.array(image)
                self.container_image = image_array.copy()
                self.stego_image = image_array.copy()  # сохраняем исходное изображение
                self.file_status.set("Image loaded successfully.")
                print(self.container_image)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")


    def embed_with_hash(self):
        pass

    def embed_message_standard(self):
        if self.stego_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return

        message = self.message_entry.get()
        if not message:
            messagebox.showerror("Error", "Please enter a message.")
            return

        # 1. Преобразуем сообщение в биты
        message_bits = self.text_to_bits(message)

        # 2. Добавляем длину сообщения (в 32 битах)
        length_bits = format(len(message_bits), '032b')  # строка из 0 и 1
        length_bits = [int(b) for b in length_bits]

        full_message_bits = length_bits + message_bits

        # 3. Встраиваем сообщение
        self.stego_image = self.interpolation_method(self.stego_image.copy(), full_message_bits)

        # 4. Сохраняем изображение
        output_dir = "lab7/src/img_out/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, "stego_standard.png")
        self.save_image(self.stego_image, output_path)

        messagebox.showinfo("Success", f"Message successfully embedded.\nSaved to {output_path}")
    
    def text_to_bits(self, text):
        result = bitarray()
        result.frombytes(text.encode('utf-8'))
        return list(result)
    
    def save_image(self, array, path):
        image = Image.fromarray(array.astype(np.uint8))
        image.save(path)


    def interpolation_method(self, img_array, full_message_bits):
        print(full_message_bits)
        height, width = img_array.shape
        stego_array = img_array.copy()

        idx = 0
        for i in range(height):
            for j in range(width):
                if idx < len(full_message_bits):
                    pixel_value = stego_array[i, j]


                    if j < width - 1:
                        next_pixel_value = stego_array[i, j + 1]
                        interpolated_value = (int(pixel_value) + int(next_pixel_value)) // 2

                        if full_message_bits[idx] == 1:
                            if interpolated_value % 2 == 0:
                                # Проверяем, не приведет ли добавление к переполнению
                                if pixel_value < 255:
                                    stego_array[i, j] = pixel_value+1
                            else:
                                if pixel_value > 0:
                                    stego_array[i, j] = pixel_value-1
                        else:
                            if interpolated_value % 2 == 1:
                                if pixel_value > 0:
                                    stego_array[i, j] = pixel_value-1
                            else:
                                if pixel_value < 255:
                                    stego_array[i, j] = pixel_value+1

                        idx += 1
                else:
                    break
        return stego_array


    def extract_message(self):
        use_standard = self.extract_mode_standard.get()
        use_hash = self.extract_mode_hash.get()

        if not (use_standard or use_hash):
            messagebox.showerror("Error", "Please select at least one extraction mode.")
            return
        if use_standard:
            self.extract_standard(self.stego_image)
    

    def extract_standard(self, stego_array):
        height, width = stego_array.shape
        message_bits = []

        # Извлечение длины сообщения (первые 32 бита)
        idx = 0
        for i in range(height):
            for j in range(width):
                if idx < 32:  # Читаем только первые 32 бита
                    pixel_value = stego_array[i, j]

                    # Пропускаем пиксели со значениями 255, 254, 0 и 1
                    

                    if j < width - 1:
                        next_pixel_value = stego_array[i, j + 1]
                        interpolated_value = (int(pixel_value) + int(next_pixel_value)) // 2

                        # Определяем, является ли пиксель четным или нечетным
                        if interpolated_value % 2 == 0:
                            message_bits.append(0)
                        else:
                            message_bits.append(1)

                        idx += 1
                else:
                    break
            if idx >= 32:
                break

        print(message_bits)
        # Получаем длину сообщения
        message_length = int(''.join(map(str, message_bits)), 2)
        print(message_length)

        # Извлечение сообщения
        message_bits = []
        idx = 0
        for i in range(height):
            for j in range(width):
                if idx < message_length * 8:  # Читаем только нужное количество битов
                    pixel_value = stego_array[i, j]

                    # Пропускаем пиксели со значениями 255, 254, 0 и 1
                    if pixel_value in [255, 254, 0, 1]:
                        continue

                    if j < width - 1:
                        next_pixel_value = stego_array[i, j + 1]
                        interpolated_value = (int(pixel_value) + int(next_pixel_value)) // 2

                        # Определяем, является ли пиксель четным или нечетным
                        if interpolated_value % 2 == 0:
                            message_bits.append(0)
                        else:
                            message_bits.append(1)

                        idx += 1
                else:
                    break
            if idx >= message_length * 8:
                break

        # Преобразование битов в текст
        message = ''
        for i in range(0, len(message_bits), 8):
            byte = message_bits[i:i + 8]
            if len(byte) < 8:
                break
            message += chr(int(''.join(map(str, byte)), 2))

        print(message)
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, message)



if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
