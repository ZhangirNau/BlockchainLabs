import time
import json
from typing import List, Optional
import tkinter as tk
from tkinter import messagebox, ttk
import random

# Қарапайым қолмен хэштеу функциясы
def simple_hash(data: str) -> str:
    hash_value = 0
    for char in data:
        hash_value = (hash_value * 31 + ord(char)) % (10**8)  # Қарапайым полиномдық хэш
    return f"{hash_value:08d}"  # Шектелген ұзындық үшін нөлдермен толтыру

class AsymmetricEncryption:
    # Ассимметриялық шифрлау арқылы жұп кілттерді құру
    @staticmethod
    def generate_key_pair():
        private_key = random.randint(10**5, 10**6)
        public_key = private_key * 2  # Жай мысал үшін қарапайым ереже
        return private_key, public_key

    @staticmethod
    def sign_message(private_key, message: str) -> int:
        # Хабарламаны жеке кілтпен қол қою
        return simple_hash(message + str(private_key))

    @staticmethod
    def verify_signature(public_key, message: str, signature: str) -> bool:
        # Қолтаңбаны тексеру
        return simple_hash(message + str(public_key // 2)) == signature

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: float, signature: Optional[str] = None):
        # Транзакция құрылымы (Жіберуші, Қабылдаушы, Сома, Қолтаңба)
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()
        # Транзакция адресін хэштеу
        self.transaction_id = simple_hash(f"{self.sender}{self.receiver}{self.amount}{self.timestamp}")
        self.signature = signature

class MerkleTree:
    def __init__(self, transactions: List[str]):
        # Меркле ағашының түбірін құру
        self.transactions = transactions
        self.root = self.build_merkle_root(transactions)

    def build_merkle_root(self, transactions: List[str]) -> str:
        if not transactions:
            return "0" * 8
        if len(transactions) == 1:
            return simple_hash(transactions[0])

        new_level = []
        for i in range(0, len(transactions), 2):
            left = transactions[i]
            right = transactions[i + 1] if i + 1 < len(transactions) else left
            new_level.append(simple_hash(left + right))
        return self.build_merkle_root(new_level)

class Block:
    def __init__(self, index: int, previous_hash: str, transactions: List[Transaction], timestamp: Optional[float] = None):
        # Блок құрылымы (Индекс, Алдыңғы блоктың хэші, Транзакциялар, Меркле түбірі)
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.merkle_root = MerkleTree([t.transaction_id for t in transactions]).root
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        # Блоктың хэш адресін есептеу
        block_data = f"{self.index}{self.previous_hash}{self.timestamp}{self.merkle_root}"
        return simple_hash(block_data)

class Blockchain:
    def __init__(self):
        # Блокчейн құрылымы (Genesis блок және UTXO)
        self.chain: List[Block] = [self.create_genesis_block()]
        self.utxo = {}  # Шығарылмаған транзакция балансын сақтау

    def create_genesis_block(self) -> Block:
        # Генезис блогын құру
        return Block(0, "0", [])

    def initialize_balance(self, address: str):
        # Әрбір қолданушы үшін бастапқы баланс 100 монета
        if address not in self.utxo:
            self.utxo[address] = 100

    def add_block(self, transactions: List[Transaction]):
        # Жаңа блокты қосу
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), previous_block.hash, transactions)
        if self.validate_block(new_block):
            self.chain.append(new_block)
            self.update_utxo(transactions)

    def validate_block(self, block: Block) -> bool:
        # Блоктың дұрыстығын тексеру (Алдыңғы хэш және хэш дұрыстығы)
        if block.previous_hash != self.chain[-1].hash:
            print("Алдыңғы хэш дұрыс емес")
            return False

        if block.hash != block.calculate_hash():
            print("Блок хэші дұрыс емес")
            return False

        return True

    def update_utxo(self, transactions: List[Transaction]):
        # UTXO моделін жаңарту
        for tx in transactions:
            if tx.sender != "GENESIS":
                if tx.sender not in self.utxo or self.utxo[tx.sender] < tx.amount:
                    print("Қате транзакция: жеткіліксіз қаражат")
                    continue
                self.utxo[tx.sender] -= tx.amount
            self.utxo[tx.receiver] = self.utxo.get(tx.receiver, 0) + tx.amount

    def is_chain_valid(self) -> bool:
        # Тізбектің дұрыстығын тексеру
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Блок хэшін тексеру
            if current_block.hash != current_block.calculate_hash():
                print(f"{i} блоктың хэші дұрыс емес.")
                return False

            # Алдыңғы блок хэшін тексеру
            if current_block.previous_hash != previous_block.hash:
                print(f"{i} блоктың алдыңғы хэші дұрыс емес.")
                return False

        return True

class Wallet:
    def __init__(self):
        # Әмиян интерфейсі (жеке және ашық кілттер)
        self.private_key, self.public_key = AsymmetricEncryption.generate_key_pair()

    def sign_transaction(self, transaction: Transaction) -> str:
        # Транзакцияға қол қою
        message = f"{transaction.sender}{transaction.receiver}{transaction.amount}{transaction.timestamp}"
        return AsymmetricEncryption.sign_message(self.private_key, message)

class BlockchainExplorer:
    def __init__(self, blockchain: Blockchain):
        # Блокчейн шолушысы құрылымы
        self.blockchain = blockchain

    def display_chain_gui(self):
        # GUI құру
        window = tk.Tk()
        window.title("Blockchain Explorer")
        window.geometry("700x500")

        tree = ttk.Treeview(window, columns=("Index", "Timestamp", "Hash", "Prev Hash", "Merkle Root"), show="headings")
        tree.heading("Index", text="Индекс")
        tree.heading("Timestamp", text="Уақыт белгісі")
        tree.heading("Hash", text="Хэш")
        tree.heading("Prev Hash", text="Алдыңғы Хэш")
        tree.heading("Merkle Root", text="Меркле түбірі")

        def update_tree():
            # Деректерді жаңарту функциясы
            for item in tree.get_children():
                tree.delete(item)
            for block in self.blockchain.chain:
                tree.insert("", "end", values=(
                    block.index,
                    time.ctime(block.timestamp),
                    block.hash,
                    block.previous_hash,
                    block.merkle_root
                ))

        update_tree()
        tree.pack(fill=tk.BOTH, expand=True)

        def show_validation_status():
            status = self.blockchain.is_chain_valid()
            messagebox.showinfo("Тізбек дұрыстығы", "Дұрыс" if status else "Қате")

        def add_transaction_gui():
            # Жаңа транзакция енгізу терезесі
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

            def submit_transaction():
                sender = sender_entry.get()
                receiver = receiver_entry.get()
                amount = float(amount_entry.get())
                self.blockchain.initialize_balance(sender)
                self.blockchain.initialize_balance(receiver)
                tx = Transaction(sender, receiver, amount)
                tx.signature = AsymmetricEncryption.sign_message(random.randint(10**5, 10**6), f"{sender}{receiver}{amount}{tx.timestamp}")
                self.blockchain.add_block([tx])
                messagebox.showinfo("Транзакция", "Транзакция сәтті қосылды!")
                tx_window.destroy()
                update_tree()  # Жаңарту функциясын шақыру

            submit_button = tk.Button(tx_window, text="Қосу", command=submit_transaction)
            submit_button.grid(row=3, columnspan=2)

        transaction_button = tk.Button(window, text="Жаңа транзакция қосу", command=add_transaction_gui)
        transaction_button.pack()

        validation_button = tk.Button(window, text="Тізбек дұрыстығын тексеру", command=show_validation_status)
        validation_button.pack()

        window.mainloop()

if __name__ == "__main__":
    my_blockchain = Blockchain()
    explorer = BlockchainExplorer(my_blockchain)
    explorer.display_chain_gui()
