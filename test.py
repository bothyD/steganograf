import numpy as np
from PIL import Image

# --- Битовые утилиты ---
def str_to_bits(s):
    return [int(b) for c in s for b in format(ord(c), '08b')]

def bits_to_str(bits):
    return ''.join(chr(int(''.join(map(str, bits[i:i+8])), 2)) for i in range(0, len(bits), 8))

def encode_message_with_length(message):
    message_bits = str_to_bits(message)
    length_bits = format(len(message_bits), '032b')
    print("📏 Сообщение длиной (в битах):", len(message_bits))
    print("🧠 Биты длины:", length_bits)
    return [int(b) for b in length_bits] + message_bits

# --- Встраивание с учётом интерполяции ---
def interpolation_method(img_array, full_message_bits):
    height, width = img_array.shape
    stego_array = img_array.copy()
    idx = 0
    total_bits = len(full_message_bits)
    bitlog = []

    for i in range(height):
        for j in range(width - 1):
            if idx >= total_bits:
                return stego_array

            p1 = int(stego_array[i, j])
            p2 = int(stego_array[i, j + 1])
            desired_bit = full_message_bits[idx]
            interpolated = (p1 + p2) // 2
            current_bit = interpolated % 2

            bitlog.append(current_bit)

            if current_bit != desired_bit:
                changed = False
                for dp1 in [-1, 1]:
                    np1 = p1 + dp1
                    if 0 <= np1 <= 255:
                        new_bit = ((np1 + p2) // 2) % 2
                        if new_bit == desired_bit:
                            stego_array[i, j] = np1
                            changed = True
                            break

                if not changed:
                    for dp2 in [-1, 1]:
                        np2 = p2 + dp2
                        if 0 <= np2 <= 255:
                            new_bit = ((p1 + np2) // 2) % 2
                            if new_bit == desired_bit:
                                stego_array[i, j + 1] = np2
                                break

            idx += 1

            if idx == 32:
                print("🧪 Первые 32 встроенных бита:", bitlog)
                print("🧪 Ожидалось:", full_message_bits[:32])

    return stego_array

# --- Извлечение ---
def extract_standard(stego_array):
    height, width = stego_array.shape
    flat_pairs = [(int(stego_array[i, j]), int(stego_array[i, j + 1]))
                  for i in range(height) for j in range(width - 1)]

    length_bits = [(p1 + p2) // 2 % 2 for p1, p2 in flat_pairs[:32]]
    message_length = int(''.join(map(str, length_bits)), 2)
    print("📥 Извлечённая длина сообщения:", message_length)

    if message_length > len(flat_pairs) - 32:
        print("❌ Ошибка: длина сообщения превышает доступные пары пикселей.")
        return ""

    message_bits = [(p1 + p2) // 2 % 2 for p1, p2 in flat_pairs[32:32 + message_length]]
    print("🧾 Первые биты:", message_bits[:16], "...")
    return bits_to_str(message_bits)

# --- Тест с загрузкой изображения ---
if __name__ == "__main__":
    message = "Hello, GPT!213"
    encoded_bits = encode_message_with_length(message)

    # Загрузка изображения из файла (конвертация в grayscale)
    image_path = "lab7/src/img_in/1.bmp"
    img = Image.open(image_path).convert("L")
    img_array = np.array(img)

    print(f"🖼 Исходное изображение: {img_array.shape}, dtype={img_array.dtype}")

    stego_img = interpolation_method(img_array, encoded_bits)
    extracted = extract_standard(stego_img)

    print("📨 Извлечённое сообщение:", extracted)
    print("✅ Совпадает?", message == extracted)