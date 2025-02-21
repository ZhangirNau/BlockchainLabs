import time
import json
import random
import socket
import threading
from typing import List, Optional, Dict
import tkinter as tk
from tkinter import messagebox, ttk

# Порт және түйіндер
NODE_PORT = 5000
PEER_NODES = ["localhost:5001", "localhost:5002"]

# Хэш функциясы
def simple_hash(data: str) -> str:
    hash_value = 0
    for char in data:
        hash_value = (hash_value * 31 + ord(char)) % (10 ** 8)
    return f"{hash_value:08d}"

class AsymmetricEncryption:
    @staticmethod
    def generate_key_pair():
        private_key = random.randint(10 ** 5, 10 ** 6)
        public_key = private_key * 2
        return private_key, public_key

    @staticmethod
    def sign_message(private_key, message: str) -> int:
        return simple_hash(message + str(private_key))

class Validator:
    def __init__(self):
        self.stakes: Dict[str, float] = {}
        self.delegations: Dict[str, str] = {}
        self.rewards: Dict[str, float] = {}

    # 6 апта. Валидаторлар монеталарды стейкке қою арқылы қатыса алады
    def stake(self, validator: str, amount: float):
        self.stakes[validator] = self.stakes.get(validator, 0) + amount

    # 6 апта. Кіші аккаунттар монеталарды делегациялап, марапат ала алады
    def delegate(self, delegator: str, validator: str, amount: float):
        if validator in self.stakes:
            self.stakes[validator] += amount
            self.delegations[delegator] = validator

    # 6 апта. Валидаторлар стейкке қойылған монеталар бойынша таңдалады
    def select_validator(self) -> str:
        total_stake = sum(self.stakes.values())
        if total_stake == 0:
            return random.choice(list(self.stakes.keys())) if self.stakes else ""
        weighted_choice = random.uniform(0, total_stake)
        cumulative = 0
        for validator, stake in self.stakes.items():
            cumulative += stake
            if weighted_choice <= cumulative:
                return validator
        return ""

    # 6 апта. Валидаторларға марапаттар тағайындалады
    def reward_validator(self, validator: str, reward: float):
        if validator in self.stakes:
            self.rewards[validator] = self.rewards.get(validator, 0) + reward
            for delegator, delegated_validator in self.delegations.items():
                if delegated_validator == validator:
                    self.rewards[delegator] = self.rewards.get(delegator, 0) + reward * 0.1

validator_manager = Validator()

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: float, signature: Optional[str] = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()
        self.transaction_id = simple_hash(f"{sender}{receiver}{amount}{self.timestamp}")
        self.signature = signature

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "transaction_id": self.transaction_id,
            "signature": self.signature
        }

class Block:
    def __init__(self, index: int, previous_hash: str, transactions: List[Transaction], validator: str):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.transactions = transactions
        self.validator = validator
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        return simple_hash(f"{self.index}{self.previous_hash}{self.timestamp}{self.validator}")

    def to_dict(self):
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "validator": self.validator,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.pending_transactions: List[Transaction] = []

    def create_genesis_block(self) -> Block:
        return Block(0, "0", [], "Genesis")

    # 6 апта. PoS жүйесі арқылы блок құру
    def add_block(self):
        if not self.pending_transactions:
            return
        validator = validator_manager.select_validator()
        if validator:
            new_block = Block(len(self.chain), self.chain[-1].hash, self.pending_transactions, validator)
            self.chain.append(new_block)
            validator_manager.reward_validator(validator, 10)  # 6 апта. Валидаторға марапат беру
            self.broadcast_block(new_block)
            self.pending_transactions = []

    def add_transaction(self, transaction: Transaction):
        self.pending_transactions.append(transaction)

    # 6 апта. Блокты желіде тарату
    def broadcast_block(self, block):
        message = "NEW_BLOCK" + json.dumps(block.to_dict())  # Сериализация үшін to_dict() қолданылады
        for node in PEER_NODES:
            host, port = node.split(":")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((host, int(port)))
                    s.sendall(message.encode())
                except ConnectionRefusedError:
                    print(f"{node} қосылу сәтсіз аяқталды")

    def resolve_conflicts(self):
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

class Node:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain

    def start(self):
        threading.Thread(target=self.run_server, daemon=True).start()

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", NODE_PORT))
            s.listen()
            while True:
                conn, _ = s.accept()
                with conn:
                    data = conn.recv(1024).decode()
                    if data.startswith("NEW_BLOCK"):
                        block_data = json.loads(data[10:])
                        transactions = [Transaction(tx['sender'], tx['receiver'], tx['amount'], tx['signature']) for tx in block_data['transactions']]
                        new_block = Block(block_data['index'], block_data['previous_hash'], transactions, block_data['validator'])
                        self.blockchain.chain.append(new_block)
                        self.blockchain.resolve_conflicts()
                    elif data.startswith("GET_CHAIN"):
                        conn.sendall(json.dumps([block.to_dict() for block in self.blockchain.chain]).encode())

class BlockchainExplorer:
    def __init__(self, blockchain: Blockchain, node: Node):
        self.blockchain = blockchain
        self.node = node

    def display_chain_gui(self):
        window = tk.Tk()
        window.title("Орталықсыз Blockchain Explorer")
        window.geometry("1000x800")

        # Блоктарды көрсету үшін Treeview
        tree = ttk.Treeview(window, columns=("Index", "Timestamp", "Hash", "Prev Hash", "Validator"), show="headings")
        tree.heading("Index", text="Индекс")
        tree.heading("Timestamp", text="Уақыт белгісі")
        tree.heading("Hash", text="Хэш")
        tree.heading("Prev Hash", text="Алдыңғы Хэш")
        tree.heading("Validator", text="Валидатор")
        tree.pack(fill=tk.BOTH, expand=True)

        # 6 апта. Стейкинг және марапаттарды көрсету үшін Treeview
        stake_tree = ttk.Treeview(window, columns=("Validator", "Stake", "Rewards"), show="headings")
        stake_tree.heading("Validator", text="Валидатор")
        stake_tree.heading("Stake", text="Стейк")
        stake_tree.heading("Rewards", text="Марапаттар")
        stake_tree.pack(fill=tk.BOTH, expand=True)

        def update_trees():
            # Блоктардың Treeview-ын жаңарту
            for item in tree.get_children():
                tree.delete(item)
            for block in self.blockchain.chain:
                tree.insert("", "end", values=(
                    block.index,
                    time.ctime(block.timestamp),
                    block.hash,
                    block.previous_hash,
                    block.validator
                ))

            # 6 апта. Стейкинг және марапаттардың Treeview-ын жаңарту
            for item in stake_tree.get_children():
                stake_tree.delete(item)
            for validator, stake in validator_manager.stakes.items():
                reward = validator_manager.rewards.get(validator, 0)
                stake_tree.insert("", "end", values=(validator, stake, reward))

            window.after(5000, update_trees)

        update_trees()

        # 6 апта. Стейкинг және делегация үшін фрейм
        staking_frame = tk.Frame(window)
        staking_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(staking_frame, text="Валидатор:").grid(row=0, column=0)
        validator_entry = tk.Entry(staking_frame)
        validator_entry.grid(row=0, column=1)

        tk.Label(staking_frame, text="Стейк:").grid(row=1, column=0)
        stake_entry = tk.Entry(staking_frame)
        stake_entry.grid(row=1, column=1)

        def stake():
            validator = validator_entry.get()
            amount = float(stake_entry.get())
            validator_manager.stake(validator, amount)
            update_trees()

        tk.Button(staking_frame, text="Стейк", command=stake).grid(row=2, column=0, columnspan=2)

        tk.Label(staking_frame, text="Делегатор:").grid(row=3, column=0)
        delegator_entry = tk.Entry(staking_frame)
        delegator_entry.grid(row=3, column=1)

        def delegate():
            delegator = delegator_entry.get()
            validator = validator_entry.get()
            amount = float(stake_entry.get())
            validator_manager.delegate(delegator, validator, amount)
            update_trees()

        tk.Button(staking_frame, text="Делегациялау", command=delegate).grid(row=4, column=0, columnspan=2)

        # 6 апта. Транзакцияларды қосу және майнинг үшін фрейм
        transaction_frame = tk.Frame(window)
        transaction_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(transaction_frame, text="Жіберуші:").grid(row=0, column=0)
        sender_entry = tk.Entry(transaction_frame)
        sender_entry.grid(row=0, column=1)

        tk.Label(transaction_frame, text="Қабылдауші:").grid(row=1, column=0)
        receiver_entry = tk.Entry(transaction_frame)
        receiver_entry.grid(row=1, column=1)

        tk.Label(transaction_frame, text="Сома:").grid(row=2, column=0)
        amount_entry = tk.Entry(transaction_frame)
        amount_entry.grid(row=2, column=1)

        def add_transaction():
            sender = sender_entry.get()
            receiver = receiver_entry.get()
            amount = float(amount_entry.get())
            transaction = Transaction(sender, receiver, amount)
            self.blockchain.add_transaction(transaction)
            messagebox.showinfo("Сәтті", "Транзакция қосылды!")

        tk.Button(transaction_frame, text="Транзакция қосу", command=add_transaction).grid(row=3, column=0, columnspan=2)

        # 6 апта. Блок құру батырмасы
        def mine_block():
            self.blockchain.add_block()
            update_trees()
            messagebox.showinfo("Сәтті", "Жаңа блок құрылды!")

        tk.Button(transaction_frame, text="Блок құру", command=mine_block).grid(row=4, column=0, columnspan=2)

        window.mainloop()

if __name__ == "__main__":
    my_blockchain = Blockchain()
    node = Node(my_blockchain)
    node.start()

    explorer = BlockchainExplorer(my_blockchain, node)
    explorer.display_chain_gui()
