import hashlib
import time
import random
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import psutil

def hash256(s):
    """Two rounds of SHA256"""
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def create_transaction_of_size(byte_size):
    """Simulates a transaction with a predefined size in bytes."""
    return ''.join(random.choices('01', k=byte_size * 8))  # Simulate byte_size in bits as a binary string.

class Block:
    def __init__(self, Height, Blocksize, BlockHeader, TxCount, Txs):
        self.Height = Height
        self.Blocksize = Blocksize
        self.BlockHeader = BlockHeader
        self.Txcount = TxCount
        self.Txs = Txs

class BlockHeader:
    def __init__(self, version, prevBlockHash, merkleRoot, timestamp, bits):
        self.version = version
        self.prevBlockHash = prevBlockHash
        self.merkleRoot = merkleRoot
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0
        self.blockHash = self.generate_block_hash()  # Generate hash immediately

    def generate_block_hash(self):
        """Simulate instant block hash generation for PoA"""
        return hash256((str(self.version) + self.prevBlockHash + self.merkleRoot + str(self.timestamp)
                        + self.bits).encode()).hex()

class Blockchain:
    def __init__(self, validation_delay=0):
        self.blockchain = []
        self.block_times = []
        self.validation_delay = validation_delay  # Delay in seconds

    def set_validation_delay(self, delay):
        """Allows setting the validation delay dynamically."""
        self.validation_delay = delay

    def create_genesis_block(self):
        BlockHeight = 0
        prevBlockHash = '0' * 64
        self.addBlock(BlockHeight, prevBlockHash, 1)

    def addBlock(self, BlockHeight, prevBlockHash, transaction_size):
        start_time = time.time()
        
        # Apply validation delay before adding the block (for simulating network delay if needed)
        time.sleep(self.validation_delay)
        
        timestamp = int(time.time())
        transactions = [create_transaction_of_size(transaction_size) for _ in range(transaction_size)]
        merkleRoot = self.create_merkle_root(transactions)
        bits = 'ffff001f'
        blockheader = BlockHeader(1, prevBlockHash, merkleRoot, timestamp, bits)  # Hash generated instantly
        
        new_block = Block(BlockHeight, 1, blockheader.__dict__, len(transactions), transactions).__dict__
        self.blockchain.append(new_block)
        
        end_time = time.time()
        block_creation_time = end_time - start_time
        self.block_times.append(block_creation_time)
        
        print(f"Block {BlockHeight} added in {block_creation_time:.5f} seconds with {len(transactions)} transactions")
        return block_creation_time

    def create_merkle_root(self, transactions):
        """Creates a Merkle root from a list of transactions."""
        transaction_hashes = [hash256(tx.encode()).hex() for tx in transactions]
        while len(transaction_hashes) > 1:
            if len(transaction_hashes) % 2 != 0:
                transaction_hashes.append(transaction_hashes[-1])
            transaction_hashes = [hash256((transaction_hashes[i] + transaction_hashes[i + 1]).encode()).hex()
                                  for i in range(0, len(transaction_hashes), 2)]
        return transaction_hashes[0]

    def get_last_block(self):
        return self.blockchain[-1] if self.blockchain else None

    def print_statistics(self):
        if self.block_times:
            average_time = sum(self.block_times) / len(self.block_times)
            print(f"Average block creation time: {average_time:.5f} seconds")
            print(f"CPU Usage: {psutil.cpu_percent()}%")
            print(f"Memory Usage: {psutil.virtual_memory().percent}%")

    def visualize_blockchain(self, ax):
        heights = [block["Height"] for block in self.blockchain]
        creation_times = self.block_times

        ax.clear()
        ax.plot(heights, creation_times, marker='o', linestyle='-', color='b')
        ax.set_xlabel('Block Height')
        ax.set_ylabel('Creation Time (s)')
        ax.set_title('Blockchain Block Creation Time per Block')
        ax.grid(True)

class BlockchainApp(tk.Tk):
    def __init__(self, blockchain):
        super().__init__()
        self.title("Blockchain PoA")
        self.geometry("900x600")
        self.blockchain = blockchain

        self.stop_mining = False
        self.blocks_mined = 0
        self.blocks_to_mine = 0

        self.create_widgets()

    def create_widgets(self):
        self.add_transaction_button = ttk.Button(self, text="Add Transaction", command=self.add_transaction)
        self.add_transaction_button.pack()

        # Input for validation delay
        self.delay_label = ttk.Label(self, text="Validation Delay (in seconds):")
        self.delay_label.pack()
        self.delay_entry = ttk.Entry(self)
        self.delay_entry.pack()
        self.delay_entry.insert(0, "0")  # Default to 0 seconds
        self.set_delay_button = ttk.Button(self, text="Set Delay", command=self.set_delay)
        self.set_delay_button.pack()

        # Input to define how many blocks to mine
        self.num_blocks_label = ttk.Label(self, text="Number of Blocks to Mine:")
        self.num_blocks_label.pack()
        self.num_blocks_entry = ttk.Entry(self)
        self.num_blocks_entry.pack()
        self.num_blocks_entry.insert(0, "10")  # Default to 10 blocks

        self.start_mining_button = ttk.Button(self, text="Start Adding Blocks", command=self.start_mining)
        self.start_mining_button.pack()

        self.stop_mining_button = ttk.Button(self, text="Stop Adding Blocks", command=self.stop_mining_process)
        self.stop_mining_button.pack()

        # Treeview (table) to display Creation Time and TPS
        self.columns = ('Block Height', 'Creation Time', 'TPS')
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings')
        self.tree.heading('Block Height', text='Block Height')
        self.tree.heading('Creation Time', text='Creation Time (s)')
        self.tree.heading('TPS', text='TPS')
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind('<Double-1>', self.show_block_details)

        self.tps_label = ttk.Label(self, text="TPS: 0.0")
        self.tps_label.pack()

        self.avg_creation_time_label = ttk.Label(self, text="Avg Creation Time: 0.00 ms")
        self.avg_creation_time_label.pack()

        self.num_transactions_label = ttk.Label(self, text="Transaction Size (in Bytes):")
        self.num_transactions_label.pack()
        self.num_transactions_entry = ttk.Entry(self)
        self.num_transactions_entry.pack()
        self.num_transactions_entry.insert(0, "100")  # Default byte size

        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()

    def set_delay(self):
        """Sets the validation delay in the blockchain instance."""
        try:
            delay = float(self.delay_entry.get())
            self.blockchain.set_validation_delay(delay)
            print(f"Validation delay set to {delay} seconds")
        except ValueError:
            print("Invalid delay value")

    def add_transaction(self):
        transaction_size = int(self.num_transactions_entry.get()) if self.num_transactions_entry.get() else 100
        lastBlock = self.blockchain.get_last_block()
        BlockHeight = lastBlock["Height"] + 1 if lastBlock else 0
        prevBlockHash = lastBlock['BlockHeader']['blockHash'] if lastBlock else '0' * 64

        creation_time = self.blockchain.addBlock(BlockHeight, prevBlockHash, transaction_size)
        tps = transaction_size / creation_time if creation_time > 0 else 0

        # Insert row into the treeview table
        self.tree.insert('', 'end', values=(BlockHeight, f"{creation_time:.5f}", f"{tps:.2f}"))

        self.update_performance_metrics()
        self.visualize_blockchain()

        self.blocks_mined += 1
        if self.blocks_mined >= self.blocks_to_mine:
            self.stop_mining_process()

    def start_mining(self):
        self.stop_mining = False
        self.blocks_mined = 0
        self.blocks_to_mine = int(self.num_blocks_entry.get())  
        mining_thread = threading.Thread(target=self.mine_blocks_continuously)
        mining_thread.start()

    def mine_blocks_continuously(self):
        while not self.stop_mining and self.blocks_mined < self.blocks_to_mine:
            self.add_transaction()
            time.sleep(0.1)

    def stop_mining_process(self):
        self.stop_mining = True

    def show_block_details(self, event):
        item = self.tree.selection()[0]
        block_height = self.tree.item(item, 'values')[0]
        
        for block in self.blockchain.blockchain:
            if block["Height"] == int(block_height):
                detail_window = tk.Toplevel(self)
                detail_window.title(f"Block {block_height} Details")

                tx_label = ttk.Label(detail_window, text=f"Transactions in Block {block_height}:")
                tx_label.pack()

                for tx in block["Txs"]:
                    tx_info = ttk.Label(detail_window, text=tx)
                    tx_info.pack()

    def update_performance_metrics(self):
        if self.blockchain.block_times:
            total_transactions = sum(block["Txcount"] for block in self.blockchain.blockchain)
            total_time = sum(self.blockchain.block_times)
            average_time = total_time / len(self.blockchain.block_times) if len(self.blockchain.block_times) > 0 else 0

            self.avg_creation_time_label.config(text=f"Avg Creation Time: {average_time:.5f} ms")
            
            if total_time > 0:
                self.tps_label.config(text=f"TPS: {total_transactions / total_time:.2f}")
            else:
                self.tps_label.config(text="TPS: N/A")

    def visualize_blockchain(self):
        self.blockchain.visualize_blockchain(self.ax)
        self.canvas.draw()


if __name__ == "__main__":
    blockchain = Blockchain()
    blockchain.create_genesis_block()
    app = BlockchainApp(blockchain)
    app.mainloop()
