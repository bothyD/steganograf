import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Watermark Application")
        self.original_image = None
        self.watermarked_image = None
        self.extracted_image = None
        load_button = tk.Button(root, text="Загрузить изображение", command=self.load_image)
        load_button.pack(pady=10)
        embed_button = tk.Button(root, text="Внедрить ЦВЗ", command=self.embed_watermark)
        embed_button.pack(pady=10)
        extract_button = tk.Button(root, text="Извлечь ЦВЗ", command=self.extract_watermark)
        extract_button.pack(pady=10)
        image_frame = tk.Frame(root)
        image_frame.pack(pady=10)
        self.original_canvas = tk.Canvas(image_frame, bg='lightgray', width=200, height=150)
        self.original_canvas.grid(row=0, column=0, padx=10)
        self.watermarked_canvas = tk.Canvas(image_frame, bg='lightgray', width=200, height=150)
        self.watermarked_canvas.grid(row=0, column=1, padx=10)
        self.extracted_canvas = tk.Canvas(image_frame, bg='lightgray', width=200, height=150)
        self.extracted_canvas.grid(row=0, column=2, padx=10)

    def load_image(self):
        file_path = filedialog.askopenfilename(title="Выберите изображение", filetypes=[("Images", "*.bmp *.png *.jpg *.pgm")])
        if file_path:
            self.original_image = Image.open(file_path)
            self.update_view(self.original_image, self.original_canvas)
    

    def embed_watermark(self):
        if self.original_image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение.")
            return

        watermark_path = filedialog.askopenfilename(title="Выберите ЦВЗ", filetypes=[("Images", "*.bmp *.png *.jpg *.pgm")])
        if not watermark_path:
            return

        watermark = Image.open(watermark_path).convert("RGB")  
        watermarked = self.original_image.copy()
        v = 0.15

        original_array = np.array(watermarked)
        watermark_array = np.array(watermark)

        # Проверяем размеры изображений
        if watermark_array.shape[2] != 3:
            messagebox.showerror("Ошибка", "Водяной знак должен быть цветным изображением (RGB).")
            return

        for y in range(min(watermark_array.shape[0], original_array.shape[0])):
            for x in range(min(watermark_array.shape[1], original_array.shape[1])):
                # Убедимся, что мы получаем RGB значения
                if original_array.ndim == 3 and original_array.shape[2] == 3:
                    R, G, B = original_array[y, x][:3]
                else:
                    messagebox.showerror("Ошибка", "Изображение должно быть цветным (RGB).")
                    return

                lambda_ = 0.2989 * R + 0.5866 * G + 0.1145 * B

                # Извлекаем значение серого из водяного знака
                bit = 1 if np.mean(watermark_array[y, x]) > 128 else 0
                newB = B + (2 * bit - 1) * v * lambda_
                newB = max(0, min(255, int(newB)))  
                original_array[y, x][2] = newB  

        self.watermarked_image = Image.fromarray(original_array)
        self.update_view(self.watermarked_image, self.watermarked_canvas)

    def extract_watermark(self):
        if self.original_image is None or self.watermarked_image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение и внедрите ЦВЗ.")
            return
        extracted = Image.new("L", self.original_image.size)
        extracted_array = np.zeros((self.original_image.height, self.original_image.width), dtype=np.uint8)  # Создаем массив для извлеченного изображения

        original_array = np.array(self.original_image)
        watermarked_array = np.array(self.watermarked_image)

        for y in range(3, extracted.height - 3):
            for x in range(3, extracted.width - 3):
                B_orig = original_array[y, x][2]
                B_water = watermarked_array[y, x][2]

                # Приводим к типу int32 для избежания переполнения
                delta = np.int32(B_water) - np.int32(B_orig)

                # Устанавливаем значение в 255 или 0 в зависимости от delta
                bit = 255 if delta >= 0 else 0
                extracted_array[y, x] = bit

        self.extracted_image = Image.fromarray(extracted_array)
        self.update_view(self.extracted_image, self.extracted_canvas)  
    def update_view(self, img, canvas):
        img_resized = resize_image(img)  
        img_tk = ImageTk.PhotoImage(img_resized)
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk 

def resize_image(image, max_size=(200, 200)):
    image.thumbnail(max_size, Image.LANCZOS)  
    return image

if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()
