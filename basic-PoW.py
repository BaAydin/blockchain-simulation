import hashlib
import time
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

# Funktion für den SHA256-Hash
def hash256(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

# Block- und Blockheader-Klassen
class Block:
    def __init__(self, height, header, block_size):
        self.height = height
        self.header = header
        self.block_size = block_size  # Blockgröße in Bytes

class BlockHeader:
    def __init__(self, prev_hash, merkle_root, timestamp, difficulty):
        self.prev_hash = prev_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.nonce = 0
        self.block_hash = ''
        self.difficulty = difficulty

    def mine(self):
        target_prefix = '0' * self.difficulty
        while not self.block_hash.startswith(target_prefix):
            self.block_hash = hash256((self.prev_hash + self.merkle_root + str(self.timestamp) + str(self.nonce)).encode()).hex()
            self.nonce += 1
            print(f"Mining in progress... Nonce: {self.nonce}", end="\r")

# Blockchain-Klasse
class Blockchain:
    def __init__(self, difficulty=1):
        self.chain = []
        self.block_times = []
        self.difficulty = difficulty

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def create_genesis_block(self, block_size):
        self.add_block(prev_hash='0' * 64, block_size=block_size)

    def add_block(self, prev_hash, block_size):
        start_time = time.time()
        timestamp = int(time.time())
        # Simuliere Blockdaten mit fixer Größe
        block_data = '0' * block_size
        merkle_root = hash256(block_data.encode()).hex()

        block_header = BlockHeader(prev_hash, merkle_root, timestamp, self.difficulty)
        block_header.mine()

        new_block = Block(len(self.chain), block_header, block_size)
        self.chain.append(new_block)

        mining_time = time.time() - start_time
        self.block_times.append(mining_time)

        print(f"Block {len(self.chain)-1} mined in {mining_time:.2f} seconds with block size {block_size} bytes")
        return mining_time

    def calculate_average_mining_time(self):
        """Calculates the average mining time for all blocks."""
        return sum(self.block_times) / len(self.block_times) if self.block_times else 0

# GUI-Klasse
class BlockchainApp(tk.Tk):
    def __init__(self, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.title("Blockchain Simulation")
        self.geometry("900x700")
        self.create_widgets()

    def create_widgets(self):
        # Eingabe für Mining-Schwierigkeit
        ttk.Label(self, text="Mining Difficulty:").pack()
        self.difficulty_entry = ttk.Entry(self)
        self.difficulty_entry.pack()
        self.difficulty_entry.insert(0, "1")

        # Eingabe für Blockgröße
        ttk.Label(self, text="Block Size (Bytes):").pack()
        self.block_size_entry = ttk.Entry(self)
        self.block_size_entry.pack()
        self.block_size_entry.insert(0, "1024")  # Standardgröße 1 KB

        # Start-Mining-Button
        ttk.Button(self, text="Start Mining", command=self.start_mining).pack()

        # Tabelle zur Anzeige der Blöcke
        self.tree = ttk.Treeview(self, columns=('Height', 'Mining Time', 'Block Size'), show='headings')
        self.tree.heading('Height', text='Block Height')
        self.tree.heading('Mining Time', text='Mining Time (s)')
        self.tree.heading('Block Size', text='Block Size (Bytes)')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Plot für Mining-Zeiten
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()

        # Label für durchschnittliche Mining-Zeit
        self.avg_mining_time_label = ttk.Label(self, text="Average Mining Time: 0.00 s")
        self.avg_mining_time_label.pack()

    def start_mining(self):
        difficulty = int(self.difficulty_entry.get())
        block_size = int(self.block_size_entry.get())
        self.blockchain.set_difficulty(difficulty)

        threading.Thread(target=self.mine_blocks, args=(block_size,), daemon=True).start()

    def mine_blocks(self, block_size):
        self.blockchain.create_genesis_block(block_size=block_size)
        for _ in range(10):  # Anzahl der Blöcke
            last_block = self.blockchain.chain[-1]
            prev_hash = last_block.header.block_hash
            mining_time = self.blockchain.add_block(prev_hash, block_size)
            self.tree.insert('', 'end', values=(len(self.blockchain.chain) - 1, f"{mining_time:.2f}", block_size))
            self.update_plot()
            self.update_average_mining_time()

    def update_plot(self):
        heights = [block.height for block in self.blockchain.chain]
        times = self.blockchain.block_times

        self.ax.clear()
        self.ax.plot(heights, times, marker='o', linestyle='-', color='b')
        self.ax.set_xlabel('Block Height')
        self.ax.set_ylabel('Mining Time (s)')
        self.ax.set_title('Mining Time per Block')
        self.canvas.draw()

    def update_average_mining_time(self):
        avg_time = self.blockchain.calculate_average_mining_time()
        self.avg_mining_time_label.config(text=f"Average Mining Time: {avg_time:.2f} s")

if __name__ == "__main__":
    blockchain = Blockchain(difficulty=1)
    app = BlockchainApp(blockchain)
    app.mainloop()