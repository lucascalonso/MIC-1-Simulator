class MIC1Processor:
    def __init__(self):
        self.SP = 4095 
        self.AC = "0000000000000000"
        self.temp = 0
        self.PC = 0

        self.memory = {}
        self.data_cache = {}
        self.instruction_cache = {}

        self.data_cache_hits = 0
        self.data_cache_misses = 0
        self.instruction_cache_hits = 0
        self.instruction_cache_misses = 0

        self.end_of_program = False
        self.instruction = ""
        self.opcode = ""
        self.operando = ""
        self.decoded_instruction = ""

        self.opcode_names = {
            "0000": "LODD",
            "0001": "STOD",
            "0010": "ADDD",
            "0011": "SUBD",
            "0100": "JPOS",
            "0101": "JZER",
            "0110": "JUMP",
            "0111": "LOCO",
            "1000": "LODL",
            "1001": "STOL",
            "1010": "ADDL",
            "1011": "SUBL",
            "1100": "JNEG",
            "1101": "JNZE",
            "1110": "CALL",
            "1111000000000000": "PSHI",
            "1111001000000000": "POPI",
            "1111010000000000": "PUSH",
            "1111011000000000": "POP",
            "1111100000000000": "RETN",
            "1111101000000000": "SWAP",
            "11111100": "INSP",
            "11111110": "DESP"
        }
        self.instruction_set = {
            "0000": self.load_direct,
            "0001": self.store_direct,
            "0010": self.add_direct,
            "0011": self.sub_direct,
            "0100": self.jump_pos,
            "0101": self.jump_zer,
            "0110": self.jump,
            "0111": self.loco,
            "1000": self.lodl,
            "1001": self.stol,
            "1010": self.addl,
            "1011": self.subl,
            "1100": self.jneg,
            "1101": self.jnze,
            "1110": self.call,
            "1111000000000000": self.pshi,
            "1111001000000000": self.popi,
            "1111010000000000": self.push,
            "1111011000000000": self.pop,
            "1111100000000000": self.retn,
            "1111101000000000": self.swap,
            "11111100": self.insp,
            "11111110": self.desp
        }

    def decode_instruction(self):
        if self.opcode in self.opcode_names:
            return self.opcode_names[self.opcode]
        else:
            return "Unknown Operation"

    def update_data_cache(self, address):
        block_address = address // 4 * 4
        if block_address in self.data_cache:
            self.data_cache_hits += 1
        else:
            self.data_cache_misses += 1

        for i in range(4):
            next_address = block_address + i
            if next_address not in self.data_cache:
                self.data_cache[next_address] = self.memory.get(next_address, "0000000000000000")

    def write_through_cache(self, address, value):
        self.memory[address] = value
        self.update_data_cache(address)

    def load_direct(self):
        address = self.operando
        self.update_data_cache(address)
        self.AC = self.memory.get(address, "0000000000000000")

    def store_direct(self):
        address = self.operando
        self.write_through_cache(address, self.AC)

    def add_direct(self):
        address = self.operando
        self.update_data_cache(address)
        self.AC = format(int(self.AC, 2) + int(self.memory.get(address, "0000000000000000"), 2), '016b')

    def sub_direct(self):
        address = self.operando
        self.update_data_cache(address)
        self.AC = format(int(self.AC, 2) - int(self.memory.get(address, "0000000000000000"), 2), '016b')

    def jump_pos(self):
        if int(self.AC, 2) >= 0:
            self.PC = self.operando

    def jump_zer(self):
        if int(self.AC, 2) == 0:
            self.PC = self.operando

    def jump(self):
        self.PC = self.operando

    def loco(self):
        self.AC = format(self.operando, '016b')

    def lodl(self):
        address = self.SP + self.operando
        self.update_data_cache(address)
        self.AC = self.memory.get(address, "0000000000000000")

    def stol(self):
        address = self.SP + self.operando
        self.write_through_cache(address, self.AC)

    def addl(self):
        address = self.SP + self.operando
        self.update_data_cache(address)
        self.AC = format(int(self.AC, 2) + int(self.memory.get(address, "0000000000000000"), 2), '016b')

    def subl(self):
        address = self.SP + self.operando
        self.update_data_cache(address)
        self.AC = format(int(self.AC, 2) - int(self.memory.get(address, "0000000000000000"), 2), '016b')

    def jneg(self):
        if int(self.AC, 2) < 0:
            self.PC = self.operando

    def jnze(self):
        if int(self.AC, 2) != 0:
            self.PC = self.operando

    def call(self):
        self.SP -= 1
        self.write_through_cache(self.SP, format(self.PC, '016b'))
        self.PC = self.operando

    def pshi(self):
        self.SP -= 1
        address = int(self.AC, 2)
        self.write_through_cache(self.SP, self.memory.get(address, "0000000000000000"))

    def popi(self):
        address = int(self.AC, 2)
        if self.SP in self.memory and address in self.memory:
            self.write_through_cache(address, self.memory[self.SP])
            self.SP += 1
        else:
            print(f"Error: Invalid memory access at address {address} or {self.SP}")

    def push(self):
        self.SP -= 1
        self.write_through_cache(self.SP, self.AC)

    def pop(self):
        self.update_data_cache(self.SP)
        self.AC = self.memory.get(self.SP, "0000000000000000")
        self.SP += 1

    def retn(self):
        self.update_data_cache(self.SP)
        self.PC = int(self.memory.get(self.SP, "0000000000000000"), 2)
        self.SP += 1

    def swap(self):
        self.temp = self.AC
        self.AC = format(self.SP, '016b')
        self.SP = int(self.temp, 2)

    def insp(self):
        self.SP += self.operando

    def desp(self):
        self.SP -= self.operando

    def reset(self):
        self.opcode = ""
        self.operando = ""

    def fetch_instruction(self):
        if not self.end_of_program:
            if self.PC < len(self.program):
                self.instruction = self.program[self.PC]
                self.interpreta_instrucao()

                if self.PC in self.instruction_cache:
                    self.instruction_cache_hits += 1
                else:
                    self.instruction_cache_misses += 1

                self.instruction_cache[self.PC] = format(int(self.instruction, 2), '016b')

                self.PC += 1
            else:
                self.instruction = "1111111111111111"
                self.end_of_program = True
        else:
            self.instruction = "1111111111111111"

    def get_instruction_cache_hits(self):
        return self.instruction_cache_hits

    def get_instruction_cache_misses(self):
        return self.instruction_cache_misses

    def get_data_cache_hits(self):
        return self.data_cache_hits

    def get_data_cache_misses(self):
        return self.data_cache_misses

    def is_end_of_program(self):
        return self.end_of_program

    def interpreta_instrucao(self):
        if self.instruction[:4] in self.instruction_set.keys():
            self.opcode = self.instruction[:4]
            self.operando = int(self.instruction[4:], 2)
        elif self.instruction[:8] in self.instruction_set.keys():
            self.opcode = self.instruction[:8]
            self.operando = int(self.instruction[8:], 2)
        else:
            self.opcode = self.instruction

        if self.opcode in self.instruction_set:
            self.decoded_instruction = self.decode_instruction()
        else:
            self.decoded_instruction = "Unknown Operation"

    def execute_instruction(self):
        if self.opcode in self.instruction_set:
            self.instruction_set[self.opcode]()
        else:
            print(f"Unknown Operation: {self.opcode}")

    def set_program(self, program):
        self.program = program
        self.PC = 0
        self.SP = 2047
        self.end_of_program = False
        self.data_cache_hits = 0
        self.data_cache_misses = 0
        self.instruction_cache_hits = 0
        self.instruction_cache_misses = 0

    def memory_load(self, address):
        self.update_data_cache(address)
        return self.memory.get(address, "0000000000000000")

    def memory_store(self, address, value):
        self.write_through_cache(address, value)



    def load_program_from_file(self, file_path):
        with open(file_path, 'r') as file:
            self.program = [line.strip() for line in file if line.strip()]
        self.PC = 0
        self.end_of_program = False