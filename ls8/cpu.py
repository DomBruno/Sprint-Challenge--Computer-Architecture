"""CPU functionality."""

import sys
import time

class CPU:
    """Main CPU class."""
    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.__instruction_register__ = 0
        self.running = False
        self.im = 5 # iterrupt mask register
        self.isr = 6 # interrupt status register
        self.sp = 7 #our stack pointer starts at the top of a 0-7 index
        self.fl = 0b00000000 # all flags set to false on initialization
        self.reg[7] = 0xf4 # initialize stack pointer to RAM address f4
        self.__init_non_alu_opcodes__()  # initialize opcode map
        
    def __init_non_alu_opcodes__(self):
        self.branch_table = {
            0b01010000: self.CALL,
            0b00000001: self.HLT,
            0b01010010: self.INT,
            0b00010011: self.IRET,
            0b01010101: self.JEQ,
            0b01011010: self.JGE,
            0b01010111: self.JGT,
            0b01011001: self.JLE,
            0b01011000: self.JLT,
            0b01010100: self.JMP,
            0b01010110: self.JNE,
            0b10000011: self.LD,
            0b10000010: self.LDI,
            0b00000000: self.NOP,
            0b01000110: self.POP,
            0b01001000: self.PRA,
            0b01000111: self.PRN,
            0b01000101: self.PUSH,
            0b00010001: self.RET,
            0b10000100: self.ST,
        }

#### ALU Mappings 

     # map the ALU opcodes to their commands
    ALU = {  
        0b10100000: 'ADD',
        0b10101000: 'AND',
        0b10100111: 'CMP',
        0b01100110: 'DEC',
        0b10100011: 'DIV',
        0b01100101: 'INC',
        0b10100100: 'MOD',
        0b10100010: 'MUL',
        0b01101001: 'NOT',
        0b10101010: 'OR',
        0b10101100: 'SHL',
        0b10101101: 'SHR',
        0b10100001: 'SUB',
        0b10101011: 'XOR',
    }        

        # map the ALU commands to their operations
    ALU_OP = {  
        'ADD': lambda x, y: x + y,
        'AND': lambda x, y: x & y,
        'CMP': lambda x, y: 1 if x == y else 2 if x > y else 4,
        'DEC': lambda x, y: x - 1,
        'DIV': lambda x, y: x // y,
        'INC': lambda x, y: x + 1,
        'MOD': lambda x, y: x % y,
        'MUL': lambda x, y: x * y,
        'NOT': lambda x, y: ~x,
        'OR': lambda x, y: x | y,
        'SHL': lambda x, y: x << y,
        'SHR': lambda x, y: x >> y,
        'SUB': lambda x, y: x - y,
        'XOR': lambda x, y: x ^ y,
    }

    ## ^^ Thanks Richany for hinting to look in this direction last friday ^^

     # add the ability to load a file as a second argument from the command line
    def load(self, filename):
        """Load a program into memory."""
        file_path = sys.argv[1]
        program = open(f"{file_path}", "r")
        address = 0
        for line in program:
            if line[0] == "0" or line[0] == "1":
                command = line.split("#", 1)[0]
                self.ram[address] = int(command, 2)
                address += 1

    def ram_read(self, mar):
        """Returns a byte from ram."""
        self.mar = mar
        self.mdr = self.ram[self.mar]
        return self.mdr

    def ram_write(self, mar, mdr):
        """Writes a byte to ram."""
        self.mar = mar
        self.mdr = mdr
        self.ram[self.mar] = self.mdr

    # add the ability to load a file as a second argument from the command line
    def load(self, filename):
        """Load a program into memory."""
        file_path = sys.argv[1]
        program = open(f"{file_path}", "r")
        address = 0
        for line in program:
            if line[0] == "0" or line[0] == "1":
                command = line.split("#", 1)[0]
                self.ram[address] = int(command, 2)
                address += 1

    def ram_read(self, mar):
        """Returns a byte from ram."""
        self.mar = mar
        self.mdr = self.ram[self.mar]
        return self.mdr

    def ram_write(self, mar, mdr):
        """Writes a byte to ram."""
        self.mar = mar
        self.mdr = mdr
        self.ram[self.mar] = self.mdr

    def alu(self, op, reg_a, reg_b):
        try:
            x = self.reg[reg_a]
            y = self.reg[reg_b] if reg_b is not None else None
            result = self.ALU_OP[op](x,y)
                        
            if op == 'CMP':
                self.fl = result
            else:
                self.reg[reg_a] = result
                self.reg[reg_b] &= 0xFF
        except Exception:
            raise SystemError("Unsupported ALU operation")

    def run(self):
        """Run the CPU."""
        self.running = True
        old_time = new_time = time.time()

        while self.running:
            if self.reg[self.im]:
                self.check_inter()

            new_time = time.time()
            if new_time - old_time > 1:
                self.reg[self.isr] |= 0b00000001
                old_time = new_time

            # initialize intruction register and operands (if there are any)
            self.ir = self.ram_read(self.pc)
            if self.ir & 0b100000 > 0:
                # ALU operation
                self.alu(self.ALU[self.ir], self.operand_a, self.operand_b)
            else:
                # non-ALU opcode
                self.branch_table[self.ir]()
        
            # if instruction does not modify program counter
            if self.ir & 0b10000 == 0:
                # move to next instruction
                self.pc += 1             

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

########

def check_inter(self):
        interrupts = self.reg[self.im] & self.reg[self.isr]
        for interrupt in range(8):
            bit = 1 << interrupt
            #if an interrupt is triggered
            if interrupts & bit:
                # save the old interrupt state
                self.old_im = self.reg[self.im]
                # disable interrupts
                self.reg[self.im] = 0
                # clear the interrupt
                self.reg[self.isr] &= (255 ^ bit)
                # decrement the stack pointer
                self.reg[self.sp] -= 1
                # push the pc to the stack
                self.ram_write(self.reg[self.sp], self.pc)
                #decrement the stack pointer
                self.reg[self.sp] -= 1
                # push the flags to the stack
                self.ram_write(self.reg[self.sp], self.fl)
                # push the registers to the stack R0-R6
                for i in range(7):
                    self.reg[self.sp] -= 1
                    self.ram_write(self.reg[self.sp], self.reg[i])
                self.pc = self.ram[0xF8 + interrupt]
                # break out and stop checking interrupts
                break 