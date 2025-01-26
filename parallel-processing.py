import hashlib
import time
import random
import tkinter as tk
from tkinter import ttk
import threading

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
        self.blockHash = self.create_hash()  # Directly generate the block hash for PoA

    def create_hash(self):
        return hashlib.sha256(
            (str(self.version) + self.prevBlockHash + self.merkleRoot + str(self.timestamp) + self.bits).encode()
        ).hexdigest()

class Chain:
    def __init__(self, chain_type, chain_id, validation_delay=0.1):
        self.chain_type = chain_type
        self.chain_id = chain_id
        self.validation_delay = validation_delay
        self.blockchain = []
        self.block_times = []
        self.GenesisBlock()

    def GenesisBlock(self):
        BlockHeight = 0
        prevBlockHash = '0' * 64
        self.addBlock(BlockHeight, prevBlockHash, 1)

    def addBlock(self, BlockHeight, prevBlockHash, transaction_size):
        """Adds a block instantly with PoA consensus."""
        start_time = time.time()
        time.sleep(self.validation_delay)  # Simulate validation delay
        
        timestamp = int(time.time())
        transactions = [create_transaction_of_size(transaction_size) for _ in range(transaction_size)]
        merkleRoot = self.create_merkle_root(transactions)
        bits = 'ffff001f'
        blockheader = BlockHeader(1, prevBlockHash, merkleRoot, timestamp, bits)  # No mining needed
        
        new_block = Block(BlockHeight, 1, blockheader.__dict__, len(transactions), transactions).__dict__
        self.blockchain.append(new_block)
        
        end_time = time.time()
        creation_time = end_time - start_time
        self.block_times.append(creation_time)
        
        print(f"{self.chain_type} {self.chain_id} - Block {BlockHeight} created in {creation_time:.2f} seconds with PoA.")
        return creation_time

    def create_merkle_root(self, transactions):
        """Creates a Merkle root from a list of transactions."""
        transaction_hashes = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
        while len(transaction_hashes) > 1:
            if len(transaction_hashes) % 2 != 0:
                transaction_hashes.append(transaction_hashes[-1])
            transaction_hashes = [hashlib.sha256((transaction_hashes[i] + transaction_hashes[i + 1]).encode()).hexdigest()
                                  for i in range(0, len(transaction_hashes), 2)]
        return transaction_hashes[0]

    def get_last_block(self):
        return self.blockchain[-1] if self.blockchain else None

class BlockchainApp(tk.Tk):
    def __init__(self, chains):
        super().__init__()
        self.title("Generalized Blockchain PoA Simulation")
        self.geometry("1000x600")
        self.chains = chains
        self.create_widgets()

    def create_widgets(self):
        chain_frames = []

        # Dynamically create UI elements for each chain
        for chain in self.chains:
            frame = ttk.LabelFrame(self, text=f"{chain.chain_type} {chain.chain_id} Parameters")
            frame.pack(side="left", padx=10, pady=10)

            # Number of Blocks to Mine
            label = ttk.Label(frame, text="Number of Blocks to Mine:")
            label.pack()
            entry = ttk.Entry(frame)
            entry.pack()
            entry.insert(0, "5")
            setattr(chain, 'num_blocks_entry', entry)  # Store entry reference in the chain object

            # Transaction Size
            label = ttk.Label(frame, text="Transaction Size (Bytes):")
            label.pack()
            entry = ttk.Entry(frame)
            entry.pack()
            entry.insert(0, "100")
            setattr(chain, 'num_transactions_entry', entry)

            # Validation Delay
            label = ttk.Label(frame, text="Validation Delay (s):")
            label.pack()
            entry = ttk.Entry(frame)
            entry.pack()
            entry.insert(0, str(chain.validation_delay))
            setattr(chain, 'validation_delay_entry', entry)

            chain_frames.append(frame)

        # Start Mining Button
        self.start_mining_button = ttk.Button(self, text="Start Mining", command=self.start_mining)
        self.start_mining_button.pack(pady=10)

        # Treeview table for showing results
        self.tree = ttk.Treeview(self, columns=('Chain', 'Block Height', 'Creation Time', 'TPS', 'Bytes'), show='headings')
        self.tree.heading('Chain', text='Chain')
        self.tree.heading('Block Height', text='Block Height')
        self.tree.heading('Creation Time', text='Creation Time (s)')
        self.tree.heading('TPS', text='TPS')
        self.tree.heading('Bytes', text='Bytes per Block')
        self.tree.pack(fill=tk.BOTH, expand=True)

    def start_mining(self):
        # Start PoA "mining" for each chain with specified parameters
        for chain in self.chains:
            num_blocks = int(chain.num_blocks_entry.get())
            transaction_size = int(chain.num_transactions_entry.get())
            validation_delay = float(chain.validation_delay_entry.get())
            chain.validation_delay = validation_delay  # Update chain validation delay

            # Start a separate thread for each chain
            threading.Thread(target=self.mine_blocks_poa, args=(chain, num_blocks, transaction_size)).start()

    def mine_blocks_poa(self, chain, num_blocks, transactions_per_block):
        """Creates blocks with PoA for the given chain."""
        for i in range(num_blocks):
            lastBlock = chain.get_last_block()
            BlockHeight = lastBlock["Height"] + 1 if lastBlock else 0
            prevBlockHash = lastBlock['BlockHeader']['blockHash'] if lastBlock else '0' * 64
            creation_time = chain.addBlock(BlockHeight, prevBlockHash, transactions_per_block)
            tps = transactions_per_block / creation_time if creation_time > 0 else 0
            self.tree.insert('', 'end', values=(f"{chain.chain_type} {chain.chain_id}", BlockHeight, f"{creation_time:.2f}", f"{tps:.2f}", transactions_per_block))

if __name__ == "__main__":
    # Initialize multiple chains with PoA consensus
    chain1 = Chain("Chain", 1, validation_delay=0.1)
    chain2 = Chain("Chain", 2, validation_delay=0.1)

    chains = [chain1, chain2]  # This can represent sharding, sidechains, or multichain architectures
    app = BlockchainApp(chains)
    app.mainloop()
