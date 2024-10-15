import tkinter as tk
from tkinter import filedialog, scrolledtext
from cpu import MIC1Processor

class GUI:
    def __init__(self, root):
        
        self.root = root
        self.root.title("MIC-1 Simulator Bárbara Lucas Pedro")
        self.root.geometry("1000x600")
        self.cpu = MIC1Processor()
        self.program_loaded = False
        self.program_running = False

        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(padx=10, pady=10, side=tk.TOP)

        self.data_cache_hits_label = tk.Label(self.status_frame, text="")
        self.data_cache_hits_label.grid(row=4, column=0, sticky="w")

        self.instruction_cache_hits_label = tk.Label(self.status_frame, text="")
        self.instruction_cache_hits_label.grid(row=5, column=0, sticky="w")

        self.create_widgets()

    def create_widgets(self):

        self.load_button = tk.Button(self.root, text="Load Program", command=self.load_program)
        self.load_button.pack(pady=10)

        self.step_button = tk.Button(self.root, text="Step", command=self.step_program, state=tk.NORMAL)
        self.step_button.pack(pady=10)

        self.run_button = tk.Button(self.root, text="Run", command=self.run_program, state=tk.NORMAL)
        self.run_button.pack(pady=10)

        self.speed_label = tk.Label(self.root, text="Execution Speed")
        self.speed_label.pack()
        self.speed_scale = tk.Scale(self.root, from_=1, to=10, orient=tk.HORIZONTAL)
        self.speed_scale.pack()

        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(padx=10, pady=10, side=tk.TOP)

        self.pc_label = tk.Label(self.status_frame, text="PC:")
        self.pc_label.grid(row=0, column=0, sticky="w")
        self.pc_value_label = tk.Label(self.status_frame, text="")
        self.pc_value_label.grid(row=0, column=1, sticky="w")

        self.ac_label = tk.Label(self.status_frame, text="AC:")
        self.ac_label.grid(row=1, column=0, sticky="w")
        self.ac_value_label = tk.Label(self.status_frame, text="")
        self.ac_value_label.grid(row=1, column=1, sticky="w")

        self.sp_label = tk.Label(self.status_frame, text="SP:")
        self.sp_label.grid(row=2, column=0, sticky="w")
        self.sp_value_label = tk.Label(self.status_frame, text="")
        self.sp_value_label.grid(row=2, column=1, sticky="w")

        self.instruction_label = tk.Label(self.status_frame, text="Decoded Instruction:")
        self.instruction_label.grid(row=3, column=0, sticky="w")
        self.instruction_value_label = tk.Label(self.status_frame, text="")
        self.instruction_value_label.grid(row=3, column=1, sticky="w")

        self.memory_frame = tk.Frame(self.root, width=200, height=300, borderwidth=2, relief="groove")
        self.memory_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.memory_label = tk.Label(self.memory_frame, text="Memory")
        self.memory_label.pack()

        self.memory_display = scrolledtext.ScrolledText(self.memory_frame, width=30, height=10)
        self.memory_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.data_cache_frame = tk.Frame(self.root, width=200, height=300, borderwidth=2, relief="groove")
        self.data_cache_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.data_cache_label = tk.Label(self.data_cache_frame, text="Data Cache")
        self.data_cache_label.pack()

        self.data_cache_display = scrolledtext.ScrolledText(self.data_cache_frame, width=30, height=10)
        self.data_cache_display.pack(padx=10, pady=10)

        self.instruction_cache_frame = tk.Frame(self.root, width=200, height=300, borderwidth=2, relief="groove")
        self.instruction_cache_frame.pack(padx=10, pady=10, side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.instruction_cache_label = tk.Label(self.instruction_cache_frame, text="Instruction Cache")
        self.instruction_cache_label.pack()

        self.instruction_cache_display = scrolledtext.ScrolledText(self.instruction_cache_frame, width=30, height=10)
        self.instruction_cache_display.pack(padx=10, pady=10)

    def load_program(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.cpu.load_program_from_file(file_path)
            self.program_loaded = True
            self.program_running = True
            self.update_status_display()
            self.update_step_button_state()

    def step_program(self):
        if self.program_loaded and self.program_running:
            self.cpu.fetch_instruction()

        if self.cpu.is_end_of_program():
            self.program_running = False
            self.update_step_button_state()

        self.cpu.execute_instruction()
        self.update_status_display()

    def run_program(self):
        if not self.program_loaded:
            return
        
        self.program_running = True
        self.run_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.DISABLED)
        self.step_button.config(state=tk.DISABLED)
        self.speed_scale.config(state=tk.DISABLED)
        
        while self.program_running:
            self.cpu.fetch_instruction()
            
            if self.cpu.is_end_of_program():
                self.program_running = False
                break
            
            self.cpu.execute_instruction()
            self.update_status_display()
            self.root.update()
            speed = self.speed_scale.get()
            self.root.after(1000 // speed)

        self.run_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.NORMAL)
        self.step_button.config(state=tk.NORMAL)
        self.speed_scale.config(state=tk.NORMAL)

    def update_status_display(self):
        self.pc_value_label.config(text=f"{format(self.cpu.PC, '016b')} / {self.cpu.PC}")
        self.ac_value_label.config(text=f"{format(int(self.cpu.AC, 2), '016b')} / {int(self.cpu.AC, 2)}")
        self.sp_value_label.config(text=f"{format(self.cpu.SP, '016b')} / {self.cpu.SP}")

        decoded_instruction = self.cpu.opcode_names.get(self.cpu.opcode, "Unknown Operation")
        
        if self.cpu.opcode in self.cpu.instruction_set:
            decoded_instruction += f" {self.cpu.operando}"
        
        self.instruction_value_label.config(text=decoded_instruction)

        self.memory_display.delete("1.0", tk.END)
        for address in sorted(self.cpu.memory):
            binary_value = self.cpu.memory[address]
            if isinstance(binary_value, int):
                binary_value = format(binary_value, '016b')
            elif not isinstance(binary_value, str):
                continue

            try:
                decimal_value = int(binary_value, 2)
            except ValueError:
                decimal_value = binary_value

            self.memory_display.insert(tk.END, f"Address {address}: {binary_value} / {decimal_value}\n")

        if self.cpu.is_end_of_program():
            self.memory_display.insert(tk.END, "Program finished.\n")

        self.data_cache_display.delete("1.0", tk.END)
        for address, value in sorted(self.cpu.data_cache.items()):
            self.data_cache_display.insert(tk.END, f"Address {address}: {value}\n")

        self.instruction_cache_display.delete("1.0", tk.END)
        for address, value in sorted(self.cpu.instruction_cache.items()):
            self.instruction_cache_display.insert(tk.END, f"Address {address}: {value}\n")

        data_cache_hits = self.cpu.get_data_cache_hits()
        data_cache_misses = self.cpu.get_data_cache_misses()
        self.data_cache_hits_label.config(text=f"Data Cache Hits: {data_cache_hits}, Misses: {data_cache_misses}")

        instruction_cache_hits = self.cpu.get_instruction_cache_hits()
        instruction_cache_misses = self.cpu.get_instruction_cache_misses()
        self.instruction_cache_hits_label.config(text=f"Instruction Cache Hits: {instruction_cache_hits}, Misses: {instruction_cache_misses}")

    def update_step_button_state(self):
        if self.program_loaded and self.program_running:
            self.step_button.config(state=tk.NORMAL)
        else:
            self.step_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()


