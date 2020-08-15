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

    