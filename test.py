import matplotlib.pyplot as plt

# Данные
sizes = [
    (600, 401, 80176),
    (250, 250, 20808),
    (215, 234, 16664),
    (600, 600, 119976),
    (1430, 1424, 441169),
    (1680, 1120, 294112),
    (489, 750, 121976),
    (604, 433, 87152),
    (212, 175, 12344),
    (512, 512, 87360)
]

# Вычисление количества пикселей и сортировка данных
sizes_with_pixels = [(width, height, width * height, bits) for width, height, bits in sizes]
sorted_sizes = sorted(sizes_with_pixels, key=lambda x: x[2])  # Сортировка по количеству пикселей

# Извлечение отсортированных данных
pixel_labels = [f"{width}x{height}" for width, height, _, _ in sorted_sizes]
values = [bits for _, _, _, bits in sorted_sizes]

# Создание графика
plt.figure(figsize=(12, 6))
bars = plt.bar(pixel_labels, values, color='blue', alpha=0.7)

# Добавление значений над столбиками
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval, yval, ha='center', va='bottom')

# Настройка графика
plt.title('Количество бит в зависимости от размера изображения')
plt.xlabel('Размер изображения (пиксели)')
plt.ylabel('Количество бит')
plt.xticks(rotation=45)  # Поворот меток по оси X для лучшей читаемости
plt.grid(axis='y')

# Показать график
plt.tight_layout()  # Автоматическая настройка отступов
plt.show()
