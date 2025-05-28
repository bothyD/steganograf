import numpy as np
from PIL import Image
from collections import Counter

# --- Битовые утилиты ---
def str_to_bits(s):
    return [int(b) for c in s for b in format(ord(c), '08b')]

def bits_to_str(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        chars.append(chr(int(''.join(map(str, byte)), 2)))
    return ''.join(chars)

def xor_bits(bits, key):
    return [b ^ key[i % len(key)] for i, b in enumerate(bits)]

# --- Хэш-функция (линейная) ---
def linear_hash(block):
    return sum(block) % 2

def add_hash_blocks(bits, block_size=8):
    hashed = []
    for i in range(0, len(bits), block_size):
        block = bits[i:i+block_size]
        h = linear_hash(block)
        hashed.extend(block + [h])
    return hashed

def check_and_extract_hash_blocks(bits, block_size=8):
    recovered = []
    for i in range(0, len(bits), block_size + 1):
        block = bits[i:i+block_size]
        if len(block) < block_size:
            break
        h = bits[i + block_size]
        if linear_hash(block) == h:
            recovered.extend(block)
    return recovered

# --- Интерполяционное встраивание ---
def interpolation_method(img_array, full_message_bits):
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

# --- Извлечение ---
def extract_standard(stego_array):
    height, width = stego_array.shape
    bits = []
    for i in range(height):
        for j in range(0, width - 1, 2):
            p1 = int(stego_array[i, j])
            p2 = int(stego_array[i, j + 1])
            interp = (p1 + p2) // 2
            bits.append(interp % 2)
    return bits

# --- Анализ распределения битов ---
def analyze_bit_distribution(img_array):
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

def get_full_bits(message_bits):
    length_bits = [int(b) for b in format(len(message_bits), '032b')]
    return length_bits + message_bits

def extracted_bits_message(extracted_bits):
    extracted_len = int("".join(map(str, extracted_bits[:32])), 2)
    print("📥 Извлечённая длина:", extracted_len)
    return extracted_bits[32:32 + extracted_len]

if __name__ == "__main__":
    
    # Вместимость без хэша
    img = Image.open("lab7/src/img_in/1.bmp").convert("L")
    img_array = np.array(img)
    capacity = img_array.size // 2

    print("📊 Вместимость без хэша:", capacity)
    print("📊 Анализ распределения битов (энтропия):", analyze_bit_distribution(img_array))


    message = "I am trying to paste text or URL into text blocks or sticky notes and nothing happens. I don’t receive any error message, its just blank.I tried using keyboard shortcut methods. the right click method to copy/paste URLs or text, restarting Miro and resizing the screen to 100% but not successfully. Seems like a bug because I used to be able to do this. Hope it can be fixed soon and please let me know what I can do to make this happen again.321"
    message_bits = str_to_bits(message)
    # С хэшем
    key = [1, 0, 1, 1, 0, 1, 0, 0]  # Пример ключа XOR
    encrypted_bits = xor_bits(message_bits, key)
    hashed_bits = add_hash_blocks(encrypted_bits, 8)
    full_bits = get_full_bits(hashed_bits)

    print("📊 Вместимость с хэшем:", len(full_bits))
    stego_array = interpolation_method(img_array, full_bits)
    extracted_bits = extract_standard(stego_array)

    stego_array = interpolation_method(img_array, full_bits)
    extracted_bits = extract_standard(stego_array)

    raw_encrypted = extracted_bits_message(extracted_bits)
    recovered_encrypted = check_and_extract_hash_blocks(raw_encrypted, 8)
    decrypted = xor_bits(recovered_encrypted, key)
    extracted_msg = bits_to_str(decrypted)
    print("📨 Оригинальное сообщение:", message[:60])
    print("📨 Извлечено:", extracted_msg[:60])
    print("✅ Совпадает?", extracted_msg == message)


    # без хэшем
    
    full_bits = get_full_bits(message_bits)
    stego_array = interpolation_method(img_array, full_bits)
    extracted_bits = extract_standard(stego_array)
    extrcted_bit = extracted_bits_message(extracted_bits)
    extracted_msg = bits_to_str(extrcted_bit)
    print("📨 Извлечено:", extracted_msg[:60])
    print("✅ Совпадает?", extracted_msg == message)



