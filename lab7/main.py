import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import random
from bitarray import bitarray
import os
from collections import Counter

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography Lab7")
        self.container_image = None
        self.stego_image = None
        self.text_input = None
        self.message_bits = []
        self.key = [1, 0, 1, 1, 0, 1, 0, 0]
        self.A =  self.generate_random_binary_matrix(m=4, N=8, seed=42)
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

    # --- Интерфейс - визуальная соостовляющая
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

    # --- Интерфейс - настройка кнопок/полей
    def setup_ui(self):
        self.root.geometry("800x600")
        self.root.configure(bg=self.colors["bg"])

        main_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(header_frame, text="Steganography Tool", font=('Segoe UI', 16, 'bold'), bg=self.colors["bg"], fg=self.colors["primary"])
        title_label.pack(side=tk.LEFT)
        # --- блок изображения
        file_frame = ttk.LabelFrame(main_frame, text="Image", padding="10 10 10 10")
        file_frame.pack(fill=tk.X, pady=(0, 15))

        self.file_status = tk.StringVar(value="Image not loaded")
        file_status_label = ttk.Label(file_frame, textvariable=self.file_status)
        file_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        load_btn = ttk.Button(file_frame, text="Load Image", command=self.load_image, style='TButton')
        load_btn.pack(side=tk.LEFT, padx=(10, 0))

        # --- блок текста
        message_frame = ttk.LabelFrame(main_frame, text="Message", padding="10 10 10 10")
        message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.text_status = tk.StringVar(value="Text not loaded")
        text_status_label = ttk.Label(message_frame, textvariable=self.text_status)
        text_status_label.pack(anchor=tk.W, pady=(0, 5))

        self.text_display = tk.Text(message_frame, height=6, wrap=tk.WORD, font=('Segoe UI', 10))
        self.text_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        load_text_btn = ttk.Button(message_frame, text="Load Text", command=self.load_text, style='TButton')
        load_text_btn.pack(anchor=tk.E, padx=(0, 5))



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
        # Кнопка очистки результата
        clear_result_btn = ttk.Button(result_frame, text="Clear Result", command=lambda: self.output_text.delete(1.0, tk.END), style='Danger.TButton')
        clear_result_btn.pack(anchor=tk.E, pady=(5, 0))
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

    # --- изображение
    def load_image(self):
        path = filedialog.askopenfilename(
            initialdir="src/img_in",
            filetypes=[("Image files", "*.png *.bmp")])
        if path:
            try:
                image = Image.open(path).convert('L')
                image_array = np.array(image)
                self.container_image = image_array.copy()
                self.stego_image = image_array.copy()  # сохраняем исходное изображение
                self.file_status.set("Image loaded successfully.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    # --- текст
    def load_text(self):
        path = filedialog.askopenfilename(
            initialdir="src/texts",
            filetypes=[("Text files", "*.txt")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    self.text_input = file.read()
                    self.text_display.delete(1.0, tk.END)  # очистить поле
                    self.text_display.insert(tk.END, self.text_input)  # вставить текст
                    self.text_status.set("Text loaded successfully.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load text: {e}")


    def save_image(self, array, nameOutImg):
        # 4. Сохраняем изображение
        output_dir = "src/img_out/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_dir = os.path.join(output_dir, nameOutImg+".bmp")
        image = Image.fromarray(array.astype(np.uint8))
        image.save(output_dir)
        self.output_text.insert(tk.END,f"Message successfully embedded.\nSaved to {output_dir}"+'\n')

    # --- Битовые утилиты ---
    def str_to_bits(self, s):
        return [int(b) for c in s for b in format(ord(c), '08b')]

    def bits_to_str(self, bits):
        chars = []
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) < 8:
                break
            chars.append(chr(int(''.join(map(str, byte)), 2)))
        return ''.join(chars)

    def xor_bits(self, bits, key):
        return [b ^ key[i % len(key)] for i, b in enumerate(bits)]
    
    def get_full_bits(self, message_bits):
        length_bits = [int(b) for b in format(len(message_bits), '032b')]
        return length_bits + message_bits
    
    def extracted_bits_message(self, extracted_bits):
        extracted_len = int("".join(map(str, extracted_bits[:32])), 2)
        print(f"Extracted length: {extracted_len}")
        return extracted_bits[32:32 + extracted_len]

    # --- Хэш-функция (линейная) ---
    def linear_hash_matrix(self, block, A):
        x = np.array(block, dtype=int)
        result = (A @ x) % 2
        return result.tolist()

    # --- Линейная хэш-функция: lambda(x) = A * x mod 2 ---
    def generate_random_binary_matrix(self, m, N, seed=None):
        if seed is not None:
            np.random.seed(seed)
        return np.random.randint(0, 2, size=(m, N), dtype=int)

    def add_matrix_hash_blocks(self, bits, block_size=8, A=None):
        assert A is not None, "Матрица A обязательна"
        m = A.shape[0]
        hashed = []

        for i in range(0, len(bits), block_size):
            block = bits[i:i+block_size]
            if len(block) < block_size:
                break
            h = self.linear_hash_matrix(block, A)
            hashed.extend(block + h)

        return hashed

    def check_and_extract_matrix_hash_blocks(self, bits, block_size=8, A=None):
        assert A is not None, "Матрица A обязательна"
        m = A.shape[0]
        recovered = []

        for i in range(0, len(bits), block_size + m):
            block = bits[i:i+block_size]
            h = bits[i+block_size:i+block_size+m]
            if len(block) < block_size or len(h) < m:
                break
            expected_h = self.linear_hash_matrix(block, A)
            if h == expected_h:
                recovered.extend(block)
        return recovered

    # --- Анализ распределения битов ---
    def analyze_bit_distribution(self, img_array):
        height, width = img_array.shape
        prob_map = []
        for i in range(0, height, 8):
            for j in range(0, width, 8):
                block = img_array[i:i+8, j:j+8].flatten()
                binarized = [(int(p1) + int(p2)) // 2 % 2 for p1, p2 in zip(block[::2], block[1::2])]
                count = Counter(binarized)
                p0 = count.get(0, 0) / len(binarized)
                p1 = count.get(1, 0) / len(binarized)
                entropy = -(p0*np.log2(p0 + 1e-10) + p1*np.log2(p1 + 1e-10))
                prob_map.append(entropy)
        return np.mean(prob_map)

    def calculate_capacity_with_hash(self, image_array, hash_bits=256, length_prefix_bits=32):
        total_bits = image_array.size  # например, 1 бит на пиксель (в твоём коде container_image.size)
        capacity_bits = total_bits - hash_bits - length_prefix_bits
        if capacity_bits < 0:
            capacity_bits = 0
        return capacity_bits

    # --- Встраивание интерполяцией 
    def interpolation_method(self, img_array, full_message_bits):
        height, width = img_array.shape
        stego_array = img_array.copy()
        idx = 0
        total_bits = len(full_message_bits)

        for i in range(height):
            for j in range(0, width - 1, 2):
                if idx >= total_bits:
                    return stego_array

                p1 = int(stego_array[i, j])
                p2 = int(stego_array[i, j + 1])
                mid = (p1 + p2) // 2
                desired_bit = full_message_bits[idx]

                current_bit = mid % 2
                if current_bit != desired_bit:
                    if mid % 2 == 0:
                        mid += 1
                    else:
                        mid -= 1

                    candidates = []
                    for delta1 in range(-4, 5):
                        for delta2 in range(-4, 5):
                            np1 = p1 + delta1
                            np2 = p2 + delta2
                            if 0 <= np1 <= 255 and 0 <= np2 <= 255 and (np1 + np2) // 2 == mid:
                                diff = abs(delta1) + abs(delta2)
                                candidates.append((diff, np1, np2))

                    if candidates:
                        _, new_p1, new_p2 = min(candidates)
                        stego_array[i, j] = new_p1
                        stego_array[i, j + 1] = new_p2

                idx += 1

        return stego_array

    def embed_message_standard(self):
        if self.stego_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return
        message = self.text_input
        if not message:
            messagebox.showerror("Error", "Please enter a message.")
            return
        
        message_bits = self.str_to_bits(message)

        full_bits = self.get_full_bits(message_bits)

        self.stego_image = self.interpolation_method(self.container_image, full_bits) 
        # --- save and notify
        self.save_image(self.stego_image, "standard_embed")

    def embed_with_hash(self):
        if self.stego_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return
        message = self.text_input
        if not message:
            messagebox.showerror("Error", "Please enter a message.")
            return
        
        message_bits = self.str_to_bits(message)
        encrypted_bits = self.xor_bits(message_bits, self.key)
        hashed_bits = self.add_matrix_hash_blocks(encrypted_bits, 8, self.A)
        full_bits_hashed = self.get_full_bits(hashed_bits)
        self.stego_image = self.interpolation_method(self.container_image, full_bits_hashed)
        # --- save and notify
        self.save_image(self.stego_image, "with_hash_embed")

    # --- Извлечение сообщения   
    def extract_message(self):
        if self.stego_image is None:
            messagebox.showerror("Error", "No stego image available.")
            return
        use_standard = self.extract_mode_standard.get()
        use_hash = self.extract_mode_hash.get()

        if not (use_standard or use_hash):
            messagebox.showerror("Error", "Please select at least one extraction mode.")
            return
        extracted_bits = self.extract_bits_form_stego(self.stego_image)

        if use_standard:
            self.extract_standard(extracted_bits)
        else:
            self.extract_with_hash(extracted_bits, self.key)

    
    def extract_bits_form_stego(self, stego_array):
        height, width = stego_array.shape
        bits = []
        for i in range(height):
            for j in range(0, width - 1, 2):
                p1 = int(stego_array[i, j])
                p2 = int(stego_array[i, j + 1])
                interp = (p1 + p2) // 2
                bits.append(interp % 2)
        
        return bits
    
    
    def extract_standard(self, extracted_bits):
        extrcted_bit = self.extracted_bits_message(extracted_bits)
        self.output_text.insert(tk.END, '\n📊 Максимально получилось встроить: '+ str(len(extrcted_bit))+'\n')
        extracted_msg = self.bits_to_str(extrcted_bit)
        print("len extract message: ", len(extracted_msg))
        self.output_text.insert(tk.END, '\nExtrcted message: '+extracted_msg+'\n')
    
    def extract_with_hash(self, extracted_bits, key):
        raw_encrypted = self.extracted_bits_message(extracted_bits)
        recovered_encrypted = self.check_and_extract_matrix_hash_blocks(raw_encrypted, 8, self.A)
        decrypted = self.xor_bits(recovered_encrypted, key)
        self.output_text.insert(tk.END, '\n📊 Максимально получилось встроить: '+ str(len(decrypted))+'\n')

        extracted_msg = self.bits_to_str(decrypted)
        print("len extract message: ", len(extracted_msg))
        self.output_text.insert(tk.END, 'Extrcted message: '+extracted_msg+'\n')


if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
