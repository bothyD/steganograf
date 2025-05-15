import PIL.Image
from bitarray import bitarray


class LSBMessage:
    @staticmethod
    def inject_message(
        img_in: PIL.Image.Image, message_bits: bitarray
    ) -> PIL.Image.Image:
        img = img_in.copy()
        pixels_in = img_in.load()
        pixels = img.load()
        if pixels_in is None or pixels is None:
            raise BaseException("pixels_in is None")

        msg_index = 0

        def index_in():
            return msg_index < len(message_bits) - 1

        def mi():
            try:
                return (message_bits[msg_index] << 1) | message_bits[msg_index + 1]
            except BaseException:
                return 0b100

        for x in range(img.size[0]):
            for y in range(img.size[1]):
                if not index_in():
                    break

                byte = pixels_in[x, y]
                clp = (byte & 0b11000000) >> 6
                cmp = (byte & 0b01100000) >> 5
                crp = (byte & 0b00110000) >> 4

                if mi() == clp:
                    byte |= 1 << 2
                    msg_index += 2
                else:
                    byte &= ~(1 << 2)
                if mi() == cmp:
                    byte |= 1 << 1
                    msg_index += 2
                else:
                    byte &= ~(1 << 1)
                if mi() == crp:
                    byte |= 1
                    msg_index += 2
                else:
                    byte &= ~(1)

                pixels[x, y] = byte
            else:
                continue
            break

        return img

    @staticmethod
    def extract_message(img_in: PIL.Image.Image, message_bit_len: int) -> bitarray:
        pixels_in = img_in.load()
        msg_index = 0
        message_bits = []
        if pixels_in is None:
            raise BaseException("pixels_in is None")

        for x in range(img_in.size[0]):
            for y in range(img_in.size[1]):
                if msg_index >= message_bit_len:
                    break

                byte = pixels_in[x, y]

                # Извлекаем старшие биты (по 2 бита каждый)
                clp = (byte & 0b11000000) >> 6
                cmp = (byte & 0b01100000) >> 5
                crp = (byte & 0b00110000) >> 4

                # Извлекаем флаги (младшие 3 бита)
                clp_flag = (byte >> 2) & 1
                cmp_flag = (byte >> 1) & 1
                crp_flag = byte & 1

                # Если флаг установлен — значит соответствующий старший блок был частью сообщения
                if clp_flag and msg_index + 2 <= message_bit_len:
                    message_bits.extend([(clp >> 1) & 1, clp & 1])
                    msg_index += 2
                if cmp_flag and msg_index + 2 <= message_bit_len:
                    message_bits.extend([(cmp >> 1) & 1, cmp & 1])
                    msg_index += 2
                if crp_flag and msg_index + 2 <= message_bit_len:
                    message_bits.extend([(crp >> 1) & 1, crp & 1])
                    msg_index += 2

                if msg_index >= message_bit_len:
                    break
            else:
                continue
            break

        return bitarray(message_bits)

    @staticmethod
    def get_max_capacity(img_in: PIL.Image.Image, message_bits: bitarray):
        img = img_in.copy()
        pixels_in = img_in.load()
        pixels = img.load()
        if pixels_in is None or pixels is None:
            raise BaseException("pixels_in is None")

        msg_index = 0

        def index_in():
            return msg_index < len(message_bits) - 1

        def mi():
            try:
                return (message_bits[msg_index] << 1) | message_bits[msg_index + 1]
            except BaseException:
                return 0b100

        for x in range(img.size[0]):
            for y in range(img.size[1]):
                if not index_in():
                    break

                byte = pixels_in[x, y]
                clp = (byte & 0b11000000) >> 6
                cmp = (byte & 0b01100000) >> 5
                crp = (byte & 0b00110000) >> 4

                if mi() == clp:
                    byte |= 1 << 2
                    msg_index += 2
                else:
                    byte &= ~(1 << 2)
                if mi() == cmp:
                    byte |= 1 << 1
                    msg_index += 2
                else:
                    byte &= ~(1 << 1)
                if mi() == crp:
                    byte |= 1
                    msg_index += 2
                else:
                    byte &= ~(1)

                pixels[x, y] = byte
            else:
                continue
            break

        return msg_index
