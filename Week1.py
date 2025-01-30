import time
from tkinter import Tk, Label


# 1. Хэш алгоритмін жүзеге асыру
def simple_hash(data):
    """Қарапайым хэш алгоритмі."""
    return str(sum(ord(char) for char in data) % 100000)


# 2. Блок құрылымы
class Block:
    def __init__(self, data, prev_hash):
        self.timestamp = time.time()
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Блоктың хэшін оның деректері негізінде есептейміз."""
        return simple_hash(str(self.timestamp) + self.data + self.prev_hash)


# 3. Блокчейн құрылымы
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]  # Блоктардың тізімі (генезис-блоктан бастаймыз)

    def create_genesis_block(self):
        """Генезис-блокты құру."""
        return Block("Genesis Block", "0")

    def add_block(self, data):
        """Жаңа блокты тізбекке қосу."""
        last_block = self.chain[-1]
        new_block = Block(data, last_block.hash)
        self.chain.append(new_block)

    def is_valid(self):
        """Блокчейннің бүтіндігін тексеру."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Хэштераралық байланысты тексеру
            if current.prev_hash != previous.hash:
                return False

        return True


# 4. Қарапайым блок-эксплорер (GUI)
def display_blockchain(blockchain):
    """Блокчейнді көрсетуге арналған интерфейс."""
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


# Негізгі код: блокчейн құру, блоктар қосу, көрсету
if __name__ == "__main__":
    # Блокчейнді құру
    my_blockchain = Blockchain()

    # Бірнеше блоктарды қосу
    my_blockchain.add_block("First block data")
    my_blockchain.add_block("Second block data")
    my_blockchain.add_block("Third block data")

    # Блокчейнді GUI арқылы көрсету
    display_blockchain(my_blockchain)
