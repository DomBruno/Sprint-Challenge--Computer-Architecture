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

        