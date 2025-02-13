import time
import json
from typing import List, Optional
import tkinter as tk
from tkinter import messagebox, ttk
import random
import socket
import threading

# Порт және түйіндер
NODE_PORT = 5000
PEER_NODES = ["localhost:5001", "localhost:5002"]

# Хэш-функциясы
def simple_hash(data: str) -> str:
    hash_value = 0
    for char in data:
        hash_value = (hash_value * 31 + ord(char)) % (10**8)
    return f"{hash_value:08d}"

class AsymmetricEncryption:
    @staticmethod
    def generate_key_pair():
        private_key = random.randint(10**5, 10**6)
        public_key = private_key * 2
        return private_key, public_key

    @staticmethod
    def sign_message(private_key, message: str) -> int:
        return simple_hash(message + str(private_key))

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: float, signature: Optional[str] = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()
        self.transaction_id = simple_hash(f"{self.sender}{self.receiver}{self.amount}{self.timestamp}")
        self.signature = signature

class Block:
    def __init__(self, index: int, previous_hash: str, transactions: List[Transaction], timestamp: Optional[float] = None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_data = f"{self.index}{self.previous_hash}{self.timestamp}"
        return simple_hash(block_data)

// 4-апта: Түйіндер желісі - Өзара әрекеттесу және синхрондау үшін жаңартылды
class Node:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def start(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", NODE_PORT))
            s.listen()
            print("Узел запущен и ожидает соединений...")
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024).decode()
                    if data.startswith("NEW_BLOCK"):
                        block_data = json.loads(data[10:])
                        self.blockchain.add_block(block_data)

    // 4-апта: Түйіндер желісі - Басқа түйіндерге деректерді жіберу әдісі қосылды
def broadcast(self, message):
        for node in PEER_NODES:
            host, port = node.split(":")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, int(port)))
                s.sendall(message.encode())

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]

    def create_genesis_block(self) -> Block:
        return Block(0, "0", [])

    // 4-апта: Блок жасау - Жаңа блокты қосу және оны тарату
def add_block(self, block_data):
        new_block = Block(block_data['index'], block_data['previous_hash'], block_data['transactions'], block_data['timestamp'])
        if self.validate_block(new_block):
            self.chain.append(new_block)
            self.broadcast_block(new_block)

    // 4-апта: Түйіндер желісі - Жаңа блоктарды басқа түйіндерге тарату
def broadcast_block(self, block):
        message = "NEW_BLOCK" + json.dumps(block.__dict__)
        node.broadcast(message)

class BlockchainExplorer:
    def __init__(self, blockchain: Blockchain, node: Node):
        self.blockchain = blockchain
        self.node = node

    def display_chain_gui(self):
        window = tk.Tk()
        window.title("Decentralized Blockchain Explorer")
        window.geometry("800x600")

        tree = ttk.Treeview(window, columns=("Index", "Timestamp", "Hash", "Prev Hash"), show="headings")
        tree.heading("Index", text="Индекс")
        tree.heading("Timestamp", text="Уақыт белгісі")
        tree.heading("Hash", text="Хэш")
        tree.heading("Prev Hash", text="Алдыңғы Хэш")

        // 4-апта: Blockchain Explorer - Интерфейсті нақты уақытта жаңарту
def update_tree():
            for item in tree.get_children():
                tree.delete(item)
            for block in self.blockchain.chain:
                tree.insert("", "end", values=(
                    block.index,
                    time.ctime(block.timestamp),
                    block.hash,
                    block.previous_hash
                ))

        update_tree()
        tree.pack(fill=tk.BOTH, expand=True)

        // 4-апта: Әмиянды біріктіру - Транзакцияларды жасау үшін GUI қосу
def add_transaction_gui():
            tx_window = tk.Toplevel(window)
            tx_window.title("Жаңа транзакция қосу")

            tk.Label(tx_window, text="Жіберуші").grid(row=0, column=0)
            sender_entry = tk.Entry(tx_window)
            sender_entry.grid(row=0, column=1)

            tk.Label(tx_window, text="Қабылдаушы").grid(row=1, column=0)
            receiver_entry = tk.Entry(tx_window)
            receiver_entry.grid(row=1, column=1)

            tk.Label(tx_window, text="Сомасы").grid(row=2, column=0)
            amount_entry = tk.Entry(tx_window)
            amount_entry.grid(row=2, column=1)

            // 4-апта: Әмиянды біріктіру - Транзакцияларды басқа түйіндерге жіберу
def submit_transaction():
                sender = sender_entry.get()
                receiver = receiver_entry.get()
                amount = float(amount_entry.get())
                tx = Transaction(sender, receiver, amount)
                self.blockchain.add_block([tx.__dict__])
                self.node.broadcast(json.dumps(tx.__dict__))
                messagebox.showinfo("Транзакция", "Транзакция сәтті қосылды!")
                tx_window.destroy()
                update_tree()

            submit_button = tk.Button(tx_window, text="Қосу", command=submit_transaction)
            submit_button.grid(row=3, columnspan=2)

        transaction_button = tk.Button(window, text="Жаңа транзакция қосу", command=add_transaction_gui)
        transaction_button.pack()

        window.mainloop()

if __name__ == "__main__":
    my_blockchain = Blockchain()
    node = Node(my_blockchain)
    node.start()
