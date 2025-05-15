import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def get_bit_image(image_path, bit_position):
    image = Image.open(image_path).convert("RGB")
    binary_image = Image.new('1', image.size)
    
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.getpixel((x, y))
            bit_value = ((pixel[0] >> bit_position) & 1) | ((pixel[1] >> bit_position) & 1) | ((pixel[2] >> bit_position) & 1)
            binary_image.putpixel((x, y), bit_value)
    
    return binary_image

def select_image():
    global image_path
    image_path = filedialog.askopenfilename()
    if image_path:
        image_label.config(text=image_path)

def save_image(image):
    save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if save_path:
        image.save(save_path)

def visualize():
    try:
        bit_position = int(bit_number_entry.get())
        if bit_position < 0 or bit_position > 7:
            raise ValueError("Номер бита должен быть от 0 до 7.")
        
        bit_image = get_bit_image(image_path, bit_position)
        bit_image.show()
        
        if save_checkbox_var.get():
            save_image(bit_image)
            
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

root = tk.Tk()
root.title("Визуализация битов изображения")

root.geometry("640x400")

image_label = tk.Label(root, text="Визуализация битов изображения", font=("Arial", 12))
image_label.pack(pady=10)

select_button = tk.Button(root, text="Выбрать изображение", command=select_image, font=("Arial", 12), width=20)
select_button.pack(pady=10)

bit_number_label = tk.Label(root, text="Введите номер бита (0-7):", font=("Arial", 12))
bit_number_label.pack(pady=10)

bit_number_entry = tk.Entry(root, font=("Arial", 12))
bit_number_entry.pack(pady=10)

save_checkbox_var = tk.BooleanVar()
save_checkbox = tk.Checkbutton(root, text="Сохранить изображение", variable=save_checkbox_var, font=("Arial", 12))
save_checkbox.pack(pady=10)

visualize_button = tk.Button(root, text="Визуализировать", command=visualize, font=("Arial", 12), width=20)
visualize_button.pack(pady=10)

root.mainloop()
