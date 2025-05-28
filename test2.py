import numpy as np

class MixingHashFunction:
    def __init__(self, N, m):
        if N < m or m < 1:
            raise ValueError("Должно выполняться N ≥ m ≥ 1")
        
        self.N = N
        self.m = m
        # Создаем случайную бинарную матрицу преобразования
        self.matrix = np.random.randint(0, 2, (m, N))
    
    def hash(self, word):
        if len(word) != self.N:
            raise ValueError(f"Длина входного слова должна быть {self.N}")
            
        # Преобразуем входное слово в numpy массив
        word_array = np.array([int(bit) for bit in word])
        
        # Выполняем матричное умножение по модулю 2
        result = np.dot(self.matrix, word_array) % 2
        
        # Преобразуем результат обратно в бинарную строку
        return ''.join(map(str, result))
    
    def __call__(self, word):
        return self.hash(word)

# Пример использования:
def test_hash_function():
    N, m = 8, 4  # Пример: N=8, m=4
    hash_func = MixingHashFunction(N, m)
    
    # Тест линейности
    word1 = '10101010'
    word2 = '11001100'
    
    # Вычисляем XOR входных слов
    xor_input = ''.join(str(int(a) ^ int(b)) for a, b in zip(word1, word2))
    
    # Вычисляем хеши
    hash1 = hash_func(word1)
    hash2 = hash_func(word2)
    hash_xor = hash_func(xor_input)
    
    # Вычисляем XOR выходных хешей
    xor_output = ''.join(str(int(a) ^ int(b)) for a, b in zip(hash1, hash2))
    
    print(f"Хеш слова {word1}: {hash1}")
    print(f"Хеш слова {word2}: {hash2}")
    print(f"XOR хешей: {xor_output}")
    print(f"Хеш XOR входов: {hash_xor}")
    print(f"Свойство линейности соблюдается: {xor_output == hash_xor}")

# Запускаем тест
test_hash_function()
