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

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.pending_transactions: List[Transaction] = []

    def create_genesis_block(self) -> Block:
        return Block(0, "0", [])

    def add_block(self, transactions):
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), previous_block.hash, transactions)
        self.chain.append(new_block)
        self.broadcast_block(new_block)

    def broadcast_block(self, block):
        # 4 week. Түйіндерге блоктарды тарату (Node Network)
        message = "NEW_BLOCK" + json.dumps(block.__dict__)
        for node in PEER_NODES:
            host, port = node.split(":")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((host, int(port)))
                    s.sendall(message.encode())
                except ConnectionRefusedError:
                    print(f"{node} түйініне қосылу сәтсіз аяқталды")

    def resolve_conflicts(self):
        # 4 week. Қақтығыстарды ең ұзын тізбек арқылы шешу (Node Network)
        longest_chain = self.chain
        for node in PEER_NODES:
            host, port = node.split(":")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((host, int(port)))
                    s.sendall("GET_CHAIN".encode())
                    data = s.recv(1024).decode()
                    other_chain = json.loads(data)
                    if len(other_chain) > len(longest_chain):
                        longest_chain = other_chain
                except ConnectionRefusedError:
                    continue
        self.chain = longest_chain

    def mine_block(self):
        # 4 week. Жаңа блокты өндіру (Block Minting)
        if not self.pending_transactions:
            print("Өңдеуде тұрған транзакциялар жоқ.")
            return
        new_block = Block(len(self.chain), self.chain[-1].hash, self.pending_transactions)
        self.chain.append(new_block)
        self.broadcast_block(new_block)
        self.pending_transactions = []

class Node:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def start(self):
        server_thread = threading.Thread(target=self.run_server, daemon=True)
        server_thread.start()

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", NODE_PORT))
            s.listen()
            print("Түйін іске қосылды және қосылымдарды күтуде...")
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024).decode()
                    if data.startswith("NEW_BLOCK"):
                        # 4 week. Таратылған блоктарды қабылдау (Node Network)
                        block_data = json.loads(data[10:])
                        new_block = Block(block_data['index'], block_data['previous_hash'], block_data['transactions'], block_data['timestamp'])
                        self.blockchain.chain.append(new_block)
                        self.blockchain.resolve_conflicts()
                    elif data.startswith("GET_CHAIN"):
                        conn.sendall(json.dumps([block.__dict__ for block in self.blockchain.chain]).encode())

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

        def update_tree():
            # 4 week. Нақты уақыт режимінде жаңарту (Blockchain Explorer)
            for item in tree.get_children():
                tree.delete(item)
            for block in self.blockchain.chain:
                tree.insert("", "end", values=(
                    block.index,
                    time.ctime(block.timestamp),
                    block.hash,
                    block.previous_hash
                ))
            window.after(5000, update_tree)

        update_tree()
        tree.pack(fill=tk.BOTH, expand=True)

        def mine_block():
            # 4 week. Жаңа блокты өндіру батырмасы (Block Minting)
            self.blockchain.mine_block()
            update_tree()

        mine_button = tk.Button(window, text="Жаңа блок өндіру", command=mine_block)
        mine_button.pack()

        window.mainloop()

if __name__ == "__main__":
    my_blockchain = Blockchain()
    node = Node(my_blockchain)
    node.start()

    explorer = BlockchainExplorer(my_blockchain, node)
    explorer.display_chain_gui()
