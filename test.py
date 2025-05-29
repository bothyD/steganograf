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

# --- Линейная хэш-функция: lambda(x) = A * x mod 2 ---
def generate_random_binary_matrix(m, N, seed=None):
    if seed is not None:
        np.random.seed(seed)
    return np.random.randint(0, 2, size=(m, N), dtype=int)

def linear_hash_matrix(block, A):
    x = np.array(block, dtype=int)
    result = (A @ x) % 2
    return result.tolist()

def add_matrix_hash_blocks(bits, block_size=8, A=None):
    assert A is not None, "Матрица A обязательна"
    m = A.shape[0]
    hashed = []

    for i in range(0, len(bits), block_size):
        block = bits[i:i+block_size]
        if len(block) < block_size:
            break
        h = linear_hash_matrix(block, A)
        hashed.extend(block + h)

    return hashed

def check_and_extract_matrix_hash_blocks(bits, block_size=8, A=None):
    assert A is not None, "Матрица A обязательна"
    m = A.shape[0]
    recovered = []

    for i in range(0, len(bits), block_size + m):
        block = bits[i:i+block_size]
        h = bits[i+block_size:i+block_size+m]
        if len(block) < block_size or len(h) < m:
            break
        expected_h = linear_hash_matrix(block, A)
        if h == expected_h:
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
    print("\U0001F4E5 Извлечённая длина:", extracted_len)
    return extracted_bits[32:32 + extracted_len]

def read_text_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == "__main__":
    img = Image.open("lab7/src/img_in/1.bmp").convert("L")
    img_array = np.array(img)

    message = read_text_from_file("lab7/src/texts/example.txt")
    message_bits = str_to_bits(message)
    key = [1, 0, 1, 1, 0, 1, 0, 0]
    encrypted_bits = xor_bits(message_bits, key)

    A = generate_random_binary_matrix(m=4, N=8, seed=42)
    hashed_bits = add_matrix_hash_blocks(encrypted_bits, block_size=8, A=A)
    full_bits_hashed = get_full_bits(hashed_bits)
    full_bits_plain = get_full_bits(encrypted_bits)

    # Встраивание с хэшем
    stego_array_hashed = interpolation_method(img_array.copy(), full_bits_hashed)
    
    # Извлечение  с хэшем
    extracted_bits_hashed = extract_standard(stego_array_hashed)
    print("\U0001F4CA Вместимость с хэшем (бит):", len(extracted_bits_hashed))
    raw_encrypted_hashed = extracted_bits_message(extracted_bits_hashed)
    recovered_encrypted_hashed = check_and_extract_matrix_hash_blocks(raw_encrypted_hashed, block_size=8, A=A)
    decrypted_hashed = xor_bits(recovered_encrypted_hashed, key)
    extracted_msg_hashed = bits_to_str(decrypted_hashed)

    # Встраивание без хэша
    stego_array_plain = interpolation_method(img_array.copy(), full_bits_plain)
    
    # Извлечение  без хэшем
    extracted_bits_plain = extract_standard(stego_array_plain)
    print("\U0001F4CA Вместимость без хэша (бит):", len(extracted_bits_plain))
    raw_encrypted_plain = extracted_bits_message(extracted_bits_plain)
    decrypted_plain = xor_bits(raw_encrypted_plain, key)

    print("\U0001F4E8 Извлечено в битах (с хэшем):", len(decrypted_hashed))
    print("\U0001F4E8 Извлечено в битах (без хэша):", len(decrypted_plain))
    extracted_msg_plain = bits_to_str(decrypted_plain)

    print("\U0001F4CA Анализ распределения битов (энтропия):", analyze_bit_distribution(img_array))
    print("\U0001F4E8 Извлечено (с хэшем):", len(extracted_msg_hashed))
    print("✅ Совпадает (с хэшем)?", extracted_msg_hashed == message)
    print("\U0001F4E8 Извлечено (без хэша):", len(extracted_msg_plain))
    print("✅ Совпадает (без хэша)?", extracted_msg_plain == message)
