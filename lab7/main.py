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
        self.message_bits = []
        self.stego_image = None
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

        embed_standard_btn = ttk.Button(btn_frame, text="Embed Message (Standard)", command=self.embed_standard, style='Success.TButton')
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
            image = Image.open(path).convert('L')
            self.container_image = np.array(image)
            self.file_status.set("Image loaded successfully.")
            messagebox.showinfo("Image", "Image loaded successfully.")
            

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
                        interpolated_value = (int(pixel_value) + int(next_pixel_value)) // 2

                        if full_message[idx] == 1:
                            if interpolated_value % 2 == 0:
                                stego_array[i, j] = min(pixel_value + 1, 255)
                            else:
                                stego_array[i, j] = max(pixel_value - 1, 0)
                        else:
                            if interpolated_value % 2 == 1:
                                stego_array[i, j] = max(pixel_value - 1, 0)
                            else:
                                stego_array[i, j] = min(pixel_value + 1, 255)

                        idx += 1
                else:
                    break
        return stego_array


    def linear_hash_function(self, bit_segment):
        return sum(bit_segment) % 2

    def embed_with_hash(self):
        if self.container_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return

        message = self.message_entry.get()
        if not message:
            messagebox.showerror("Error", "Please enter a message.")
            return

        raw_bits = self.text_to_bits(message)
        encrypted_bits = self.encrypt_bits(raw_bits)

        block_size = 8
        block_with_hash = []

        for i in range(0, len(encrypted_bits), block_size):
            segment = encrypted_bits[i:i + block_size]
            if len(segment) < block_size:
                segment += [0] * (block_size - len(segment))  # padding
            h = self.linear_hash_function(segment)
            block_with_hash.extend(segment + [h])

        print(f"[With Hash] Original bits: {len(raw_bits)} Encrypted: {len(encrypted_bits)} With hash: {len(block_with_hash)}")

        length_bits = self.encrypt_bits([int(b) for b in format(len(block_with_hash), '032b')])

        full_bits = length_bits + block_with_hash

        stego_array = self.interpolation_method(self.container_image, full_bits)
        self.stego_image = stego_array
        output_dir = "lab7/src/img_out"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.save_and_show(stego_array, "lab7/src/img_out/stego_hash.png")
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
        output_dir = "lab7/src/img_out"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.save_and_show(stego_array, "lab7/src/img_out/stego_standard.png")
        messagebox.showinfo("Success", "Message embedded.")

    def extract_message(self):
        if self.stego_image is None:
            messagebox.showerror("Error", "No stego image available.")
            return

        use_standard = self.extract_mode_standard.get()
        use_hash = self.extract_mode_hash.get()

        if not (use_standard or use_hash):
            messagebox.showerror("Error", "Please select at least one extraction mode.")
            return

        img = self.stego_image
        height, width = img.shape
        extracted_bits = []

        length_bits = ""
        message_length = None
        idx = 0

        for i in range(height):
            for j in range(width):
                if j < width - 1:
                    pixel = img[i, j]
                    next_pixel = img[i, j + 1]
                    interpolated = (int(pixel) + int(next_pixel)) // 2
                    bit = 1 if interpolated % 2 else 0

                    if message_length is None:
                        length_bits += str(bit)
                        if len(length_bits) == 32:
                            # Сброс генератора перед расшифровкой длины
                            random.seed(self.key)

                            decrypted_length_bits = [int(b) ^ random.randint(0, 1) for b in map(int, length_bits)]
                            length_str = ''.join(str(b) for b in decrypted_length_bits)
                            message_length = int(length_str, 2)
                            print(f"[Extract] Decrypted length bits: {length_str} → {message_length}")
                        continue


                    extracted_bits.append(bit)
                    if len(extracted_bits) >= message_length:
                        break
            if message_length and len(extracted_bits) >= message_length:
                break
        

        results = []
        if use_standard:
            try:
                decrypted = self.decrypt_bits(extracted_bits)
                text = self.bits_to_text(decrypted)
                results.append("Standard:\n" + text)
            except Exception as e:
                results.append(f"Standard: error — {e}")

        if use_hash:
            try:
                decrypted = self.decrypt_bits(extracted_bits)
                text = self.validate_and_extract_from_hash(decrypted)
                results.append("With Hash:\n" + text)
            except Exception as e:
                results.append(f"With Hash: error — {e}")

        final_output = "\n\n---\n\n".join(results)

        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, final_output)
        print(f"[Extract] Raw bits: {len(extracted_bits)} (Expected: {message_length})")

    def validate_and_extract_from_hash(self, bits):
        block_size = 8
        valid_bits = []
        errors = 0
        total_blocks = 0

        for i in range(0, len(bits), block_size + 1):
            block = bits[i:i + block_size + 1]
            if len(block) < block_size + 1:
                print(f"[With Hash] Skipped incomplete block at end.")
                break
            segment = block[:block_size]
            h = block[-1]
            h_check = self.linear_hash_function(segment)

            if h == h_check:
                valid_bits.extend(segment)
            else:
                errors += 1
            total_blocks += 1

        print(f"[With Hash] Extracted blocks: {total_blocks}, Errors: {errors}, Valid: {total_blocks - errors}")
        return valid_bits


    def save_and_show(self, array, filename):
        img = Image.fromarray(array.astype(np.uint8))
        img.save(filename)
        plt.imshow(array, cmap='gray')
        plt.title(f"Image: {filename}")
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
