import time
from tkinter import Tk, Label


# 1. Реализация алгоритма хэширования
def simple_hash(data):
    """Простой алгоритм хэширования."""
    return str(sum(ord(char) for char in data) % 100000)


# 2. Структура блока
class Block:
    def __init__(self, data, prev_hash):
        self.timestamp = time.time()  # Метка времени
        self.data = data              # Данные блока
        self.prev_hash = prev_hash    # Хэш предыдущего блока
        self.hash = self.calculate_hash()  # Хэш текущего блока

    def calculate_hash(self):
        """Рассчитываем хэш блока на основе его данных."""
        return simple_hash(str(self.timestamp) + self.data + self.prev_hash)


# 3. Структура блокчейна
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]  # Список блоков (начинаем с генезис-блока)

    def create_genesis_block(self):
        """Создаем генезис-блок."""
        return Block("Genesis Block", "0")

    def add_block(self, data):
        """Добавляем новый блок в цепочку."""
        last_block = self.chain[-1]
        new_block = Block(data, last_block.hash)
        self.chain.append(new_block)

    def is_valid(self):
        """Проверяем целостность блокчейна."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Проверяем связь между хэшами
            if current.prev_hash != previous.hash:
                return False

        return True


# 4. Простой блок-эксплорер (GUI)
def display_blockchain(blockchain):
    """Интерфейс для отображения блокчейна."""
    root = Tk()
    root.title("Blockchain Explorer")

    for i, block in enumerate(blockchain.chain):
        Label(root, text=f"Block {i}").pack()
        Label(root, text=f"Timestamp: {block.timestamp}").pack()
        Label(root, text=f"Data: {block.data}").pack()
        Label(root, text=f"Hash: {block.hash}").pack()
        Label(root, text=f"Prev Hash: {block.prev_hash}").pack()
        Label(root, text="-" * 40).pack()

    valid_status = "Valid" if blockchain.is_valid() else "Invalid"
    Label(root, text=f"Blockchain Status: {valid_status}").pack()
    root.mainloop()


# Основной код: создаем блокчейн, добавляем блоки, отображаем
if __name__ == "__main__":
    # Создаем блокчейн
    my_blockchain = Blockchain()

    # Добавляем несколько блоков
    my_blockchain.add_block("First block data")
    my_blockchain.add_block("Second block data")
    my_blockchain.add_block("Third block data")

    # Отображаем блокчейн через GUI
    display_blockchain(my_blockchain)
