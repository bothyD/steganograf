import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import random
import hashlib
import os
from bitarray import bitarray

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography Tool")
        self.container_image = None
        self.message_bits = []
        self.stego_image = None
        self.key = 12345  
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

        # Для хранения максимального объема встроенной информации
        self.max_bits_before = 0
        self.max_bits_after = 0

    def configure_style(self):
        self.style.configure('TButton', 
                            background=self.colors["primary"],
                            foreground='white',
                            font=('Segoe UI', 10),
                            padding=6)
        self.style.map('TButton',
                     background=[('active', self.colors["primary_dark"])])
        
        self.style.configure('TLabel', 
                            background=self.colors["bg"],
                            foreground=self.colors["text"],
                            font=('Segoe UI', 10))
        
        self.style.configure('TEntry', 
                            fieldbackground=self.colors["light_accent"],
                            font=('Segoe UI', 10))
                            
        self.style.configure('TFrame', background=self.colors["bg"])
        
        self.style.configure('Primary.TButton', 
                            background=self.colors["primary"],
                            foreground='white')
        
        self.style.configure('Success.TButton', 
                            background=self.colors["success"],
                            foreground='white')
        self.style.map('Success.TButton',
                     background=[('active', '#218838')])
                     
        self.style.configure('Secondary.TButton', 
                            background=self.colors["secondary"],
                            foreground='white')
        self.style.map('Secondary.TButton',
                     background=[('active', '#5a6268')])

    def setup_ui(self):
        self.root.geometry("800x600")
        self.root.configure(bg=self.colors["bg"])
        
        main_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, 
                              text="Steganography Tool", 
                              font=('Segoe UI', 16, 'bold'),
                              bg=self.colors["bg"],
                              fg=self.colors["primary"])
        title_label.pack(side=tk.LEFT)
        
        # Секция загрузки файла
        file_frame = ttk.LabelFrame(main_frame, text="Image", padding="10 10 10 10")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.file_status = tk.StringVar(value="Image not loaded")
        file_status_label = ttk.Label(file_frame, textvariable=self.file_status)
        file_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        load_btn = ttk.Button(file_frame, text="Load Image", command=self.load_image, style='TButton')
        load_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Секция сообщения
        message_frame = ttk.LabelFrame(main_frame, text="Message", padding="10 10 10 10")
        message_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(message_frame, text="Enter text to embed:").pack(anchor=tk.W, pady=(0, 5))
        
        self.message_entry = ttk.Entry(message_frame, width=80, font=('Segoe UI', 10))
        self.message_entry.pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = ttk.Frame(message_frame, style='TFrame')
        btn_frame.pack(fill=tk.X)
        
        embed_standard_btn = ttk.Button
        embed_standard_btn = ttk.Button(btn_frame, text="Embed Message (Standard)", 
                             command=self.embed_standard, 
                             style='Success.TButton')
        embed_standard_btn.pack(side=tk.LEFT)
        
        embed_hash_btn = ttk.Button(btn_frame, text="Embed Message (with Hash)", 
                               command=self.embed_with_hash, 
                               style='Primary.TButton')
        embed_hash_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        extract_btn = ttk.Button(btn_frame, text="Extract Message", 
                               command=self.extract_message, 
                               style='Secondary.TButton')
        extract_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Секция результата
        result_frame = ttk.LabelFrame(main_frame, text="Result", padding="10 10 10 10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(result_frame, 
                                 wrap=tk.WORD, 
                                 bg=self.colors["light_accent"],
                                 relief=tk.FLAT,
                                 font=('Segoe UI', 10),
                                 height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.bmp")])
        if path:
            image = Image.open(path).convert('L')  
            self.container_image = np.array(image)
            self.file_status.set("Image loaded successfully.")
            messagebox.showinfo("Image", "Image loaded successfully.")

    def read_text_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def text_to_bits(self, text):
        result = bitarray()
        result.frombytes(text.encode('utf-8'))
        return list(result)

    def bits_to_text(self, bits):
        bit_str = bitarray(bits)
        try:
            return bit_str.tobytes().decode('utf-8', errors='ignore')
        except Exception as e:
            return f"Decoding error: {e}"

    def encrypt_bits(self, bits):
        random.seed(self.key)
        return [bit ^ random.randint(0, 1) for bit in bits]

    def decrypt_bits(self, bits):
        return self.encrypt_bits(bits)  

    def interpolation_method(self, img_array, message_bits):
        height, width = img_array.shape
        stego_array = img_array.copy()

        message_length = len(message_bits)
        length_bits = format(message_length, '032b')
        full_message = [int(bit) for bit in length_bits] + message_bits

        idx = 0
        for i in range(height):
            for j in range(width):
                if idx < len(full_message):
                    pixel_value = stego_array[i, j]
                    if j < width - 1:
                        next_pixel_value = stego_array[i, j + 1]
                        interpolated_value = (pixel_value + next_pixel_value) // 2

                        if full_message[idx] == 1:
                            if interpolated_value % 2 == 0:
                                stego_array[i, j] += 1
                        else:
                            if interpolated_value % 2 == 1:
                                stego_array[i, j] -= 1
                        idx += 1
                else:
                    break
        return stego_array

    def linear_hash_function(self, bit_segment):
        return sum(bit_segment) % 2  # Простая линейная хэш-функция

    def embed_with_hash(self):
        if self.container_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return

        message = self.message_entry.get()
        if not message:
            messagebox.showerror("Error", "Please enter a message.")
            return

        self.message_bits = self.text_to_bits(message)
        self.message_bits = self.encrypt_bits(self.message_bits)

        block_size = 8
        hash_bits = []

        for i in range(0, len(self.message_bits), block_size):
            segment = self.message_bits[i:i + block_size]
            h = self.linear_hash_function(segment)
            hash_bits += segment + [h]

        stego_array = self.interpolation_method(self.container_image, hash_bits)
        self.stego_image = stego_array
        self.save_and_show(stego_array, "src/img_out/stego_hash.png")
        messagebox.showinfo("Success", "Message embedded with hash.")

    def embed_standard(self):
        if self.container_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return

        message = self.message_entry.get()
        if not message:
            messagebox.showerror("Error", "Please enter a message.")
            return

        self.message_bits = self.text_to_bits(message)
        self.message_bits = self.encrypt_bits(self.message_bits)

        stego_array = self.interpolation_method(self.container_image, self.message_bits)
        self.stego_image = stego_array
        self.save_and_show(stego_array, "src/img_out/stego_standard.png")
        messagebox.showinfo("Success", "Message embedded.")

    def extract_message(self):
        if self.stego_image is None:
            messagebox.showerror("Error", "No stego image available.")
            return

        img = self.stego_image
        height, width = img.shape
        extracted_bits = []

        idx = 0
        length_bits = ""
        message_length = None

        for i in range(height):
            for j in range(width):
                if j < width - 1:
                    pixel = img[i, j]
                    next_pixel = img[i, j + 1]
                    interpolated = (pixel + next_pixel) // 2
                    bit = 1 if interpolated % 2 else 0

                    if message_length is None:
                        length_bits += str(bit)
                        if len(length_bits) == 32:
                            message_length = int(length_bits, 2)
                    else:
                        extracted_bits.append(bit)
                        if len(extracted_bits) >= message_length:
                            break
            if message_length and len(extracted_bits) >= message_length:
                break

        decrypted = self.decrypt_bits(extracted_bits)
        text = self.bits_to_text(decrypted)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)

    def save_and_show(self, array, filename):
        img = Image.fromarray(array.astype(np.uint8))
        img.save(filename)
        plt.imshow(array, cmap='gray')
        plt.title(f"Image: {filename}")
        plt.show()

    def evaluate_bit_distribution(self):
        if self.container_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return

        height, width = self.container_image.shape
        bit_counts = np.zeros((8, 8), dtype=int)

        for i in range(0, height, 8):
            for j in range(0, width, 8):
                block = self.container_image[i:i+8, j:j+8]
                if block.shape[0] < 8 or block.shape[1] < 8:
                    continue
                # Подсчет битов в блоке
                for x in range(8):
                    for y in range(8):
                        if block[x, y] % 2 == 1:  # Проверка на нечетность
                            bit_counts[x, y] += 1

        # Вывод распределения битов
        plt.imshow(bit_counts, cmap='hot', interpolation='nearest')
        plt.title("Bit Distribution in 8x8 Blocks")
        plt.colorbar(label='Count of 1s')
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
