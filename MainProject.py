import time
import datetime
from tkinter import Tk, Label


def simple_hash(data):
    return str(sum(ord(char) for char in data) % 100000)


class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = "2025-01-30T00:00:00"
        self.transaction_address = self.calculate_hash()

    def calculate_hash(self) -> str:
        data = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return simple_hash(data)


class Block:
    def __init__(self, transactions, prev_hash):
        self.timestamp = "2025-01-30T00:00:00"
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()

    def calculate_merkle_root(self):
        if not self.transactions:
            return "0"
        hashes = [tx.transaction_address for tx in self.transactions]
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            hashes = [simple_hash(hashes[i] + hashes[i + 1]) for i in range(0, len(hashes), 2)]
        return hashes[0]

    def calculate_hash(self):
        return simple_hash(str(self.timestamp) + self.merkle_root + self.prev_hash)


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.balances = {}

    def create_genesis_block(self):
        genesis_tx = Transaction("system", "first_user", 100)
        return Block([genesis_tx], "0")

    def add_block(self, transactions):
        if not all(self.process_transaction(tx) for tx in transactions):
            print("Some transactions are invalid and have not been added.")
            return

        last_block = self.chain[-1]
        new_block = Block(transactions, last_block.hash)
        self.chain.append(new_block)

    def process_transaction(self, tx: Transaction) -> bool:
        self.balances.setdefault(tx.sender, 100)
        self.balances.setdefault(tx.receiver, 100)

        if tx.sender != "system" and self.balances[tx.sender] < tx.amount:
            print(f"Error: Insufficient funds {tx.sender}")
            return False

        self.balances[tx.sender] -= tx.amount
        self.balances[tx.receiver] += tx.amount
        return True

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.prev_hash != previous.hash:
                return False
            if current.hash != current.calculate_hash():
                return False

        return True


# GUI: Blockchain Explorer

def display_blockchain(blockchain):
    root = Tk()
    root.title("Blockchain Explorer")

    for i, block in enumerate(blockchain.chain):
        Label(root, text=f"Block {i}").pack()
        Label(root, text=f"Timestamp: {block.timestamp}").pack()
        Label(root, text=f"Merkle Root: {block.merkle_root}").pack()
        Label(root, text=f"Block Hash: {block.hash}").pack()
        Label(root, text=f"Previous Hash: {block.prev_hash}").pack()
        Label(root, text="Transactions:").pack()

        for tx in block.transactions:
            Label(root,
                  text=f"  TX: {tx.sender} -> {tx.receiver}, {tx.amount} coins, Address: {tx.transaction_address}, Time: {tx.timestamp}").pack()
        Label(root, text="-" * 40).pack()

    valid_status = "Valid" if blockchain.is_valid() else "Invalid"
    Label(root, text=f"Blockchain Status: {valid_status}").pack()
    root.mainloop()


if __name__ == "__main__":
    my_blockchain = Blockchain()

    my_blockchain.add_block([Transaction("Alice", "Bob", 10), Transaction("Bob", "Charlie", 20)])
    my_blockchain.add_block([Transaction("Charlie", "Alice", 15)])

    display_blockchain(my_blockchain)
