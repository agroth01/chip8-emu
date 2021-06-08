from random import randint

FONTSET = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
	0x20, 0x60, 0x20, 0x20, 0x70, # 1
	0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
	0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
	0x90, 0x90, 0xF0, 0x10, 0x10, # 4
	0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
	0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
	0xF0, 0x10, 0x20, 0x40, 0x40, # 7
	0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
	0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
	0xF0, 0x90, 0xF0, 0x90, 0x90, # A
	0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
	0xF0, 0x80, 0x80, 0x80, 0xF0, # C
	0xE0, 0x90, 0x90, 0x90, 0xE0, # D
	0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
	0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]

class CPU:
    def __init__(self, renderer):
        # Store components
        self.renderer = renderer

        # Create register. Operations in CPU must be done within register
        self.v = [0x0] * 16

        # Register for storing memory address
        self.i = 0x0

        # Program counter stores currently executing address
        self.pc = 0x200

        # Create memory for CPU
        self.memory = [0x0] * 4049

        # Stack is an array to store addresses interpreter should return to
        self.stack = []

        # Timers
        self.delay_timer = 0
        self.sound_timer = 0

        # Load the font into memory
        for i in range(len(FONTSET)):
            self.memory[i] = FONTSET[i]

    # Reads the specified file and writes to CPU memory
    def load_rom(self, rom):
        # Create buffer to store file data
        buffer = []

        # Write file data to buffer
        rom_file = open(rom, "rb")
        while (byte := rom_file.read(1)):
            buffer.append(byte)

        # Move data from buffer into memory, starting at 0x200
        for i in range(len(buffer)):
            self.memory[0x200 + i] = int.from_bytes(buffer[i], 'big')

    # Complete one cycle of the CPU
    def cycle(self):
        # Shift byte at PC left 8 and OR byte at pc + 1 to get opcode
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]

        # Run instruction after being decoded previously
        self.execute_intruction(opcode)

        # Update timers
        if (self.delay_timer > 0):
            self.delay_timer -= 1
        if (self.sound_timer > 0):
            self.sound_timer -= 1

        # Draw to screen
        self.renderer.render()

    def execute_intruction(self, opcode):
        # Increment program counter so next cycle will grab next instruction
        self.pc += 2
        #print("opcode:", hex(opcode))

        # Get variables from opcode
        nnn = (opcode & 0x0FFF) # 12-bit value, the lowest 12 bits of the instruction
        n = (opcode & 0x000F) # 4-bit value, the lowest 4 bits of the instruction
        x = (opcode & 0x0F00) # 4-bit value, the lower 4 bits of the high byte of the instruction
        y = (opcode & 0x00F0) # 4-bit value, the upper 4 bits of the low byte of the instruction
        kk = (opcode & 0x00FF) # 8-bit value, the lowest 8 bits of the instruction
        op = (opcode & 0xF000) # 4-bit value, the upper 4 bits of the high byte of the instruction

        # Fucky wucky IF statements
        if (op == 0x0):
            # Clear display
            if (kk == 0xE0):
                self.renderer.clear()

            # Return from subroutine
            elif (kk == 0xEE):
                self.pc = self.stack.pop()

        # Jump to location nnn
        elif (op == 0x1000):
            self.pc = nnn

        # Call subroutine at nnn
        elif (op == 0x2000):
            self.stack.append(self.pc)
            self.pc = nnn

        # Skip next instruction if Vx == kk
        elif (op == 0x3000):
            if (self.v[x] == kk):
                self.pc += 2

        # Skip next instruction if Vx != kk
        elif (op == 0x4000):
            if (self.v[x] != kk):
                self.pc += 2

        # Skip next instruction if Vx == Vy
        elif (op == 0x5000):
            if (self.v[x] == self.v[y]):
                self.pc += 2

        # Set Vx = kk
        elif (op == 0x6000):
            self.v[x] = kk

        # Set Vx = Vx + kk
        elif (op == 0x7000):
            self.v[x] += kk

        elif (op == 0x8000):
            k = (opcode & 0x000F)
            # Set Vx = Vy
            if (k == 0x0):
                self.v[x] = self.v[y]

            # Set Vx = Vx OR Vy
            elif (k == 0x1):
                self.v[x] = self.v[x] | self.v[y]

            # Set Vx = Vx AND Vy
            elif (k == 0x2):
                self.v[x] = self.v[x] & self.v[y]

            # Set Vx = Vx XOR Vy
            elif (k == 0x3):
                self.v[x] = self.v[x] ^ self.v[y]

            # Set Vx = Vx + Vy, set VF = carry
            elif (k == 0x4):
                # Carry byte 0 by default
                self.v[0xF] = 0

                # Set carry byte to one if overflow and handle wrapping
                sum = (self.v[x] + self.v[y])
                if (sum > 255):
                    sum -= 256
                    self.v[0xF] = 1

                # Set Vx to sum
                self.v[x] = sum

            # Set Vx = Vx - Vy, set VF = NOT borrow
            elif (k == 0x5):
                # Borrow byte NOT borrow by default
                self.v[0xF] = 1

                # Set carry byte to 0 if underflow and handle wrapping
                sum = (self.v[x] - self.v[y])
                if (sum < 0):
                    sum += 256
                    self.v[0xF] = 0

                # Set x to wrapped sum of Vx + Vy
                self.v[x] = sum

            # Set Vx = Vx SHR 1
            elif (k == 0x6):
                self.v[0xF] = (self.v[x] & 0x1)
                self.v[x] >> 1

            # Set Vx = Vy - Vx, set VF = NOT borrow.
            elif (k == 0x7):
                # Borrow byte NOT borrow by default
                self.v[0xF] = 1

                # Set carry byte to 0 if underflow and handle wrapping
                sum = (self.v[y] - self.v[x])
                if (sum < 0):
                    sum += 256
                    self.v[0xF] = 0

                # Set x to wrapped sum of Vx + Vy
                self.v[x] = sum

            # Set Vx = Vx SHL 1
            elif (k == 0xE):
                self.v[0xF] = (self.v[x] & 0x80)
                self.v[x] << 1

        # Skip next instruction if Vx != Vy
        elif (op == 0x9000):
            if (self.v[x] != self.v[y]):
                self.pc += 2

        # Set I = nnn
        elif (op == 0xA000):
            self.i = nnn

        # Jump to location nnn + V0
        elif (op == 0xB000):
            self.pc = nnn + self.v[0x0]

        # Set Vx = random byte AND kk
        elif (op == 0xC000):
            rand = randint(0, 255)
            self.v[x] = (rand + kk)

        # Display n-byte sprite starting at memory location I at (Vx, Vy),
        # set VF = collision
        elif (op == 0xD000):
            # Dimensions of sprite
            width = 8 #
            height = n

            # VF should be 1 if any pixels is erased (set from 1 to 0)
            self.v[0xF] = 0

            for row in range(height):
                sprite_byte = self.memory[self.i + row]

                for col in range(width):
                    b = (sprite_byte & 0x80)

                    # If b is not zero
                    if (b):
                        if (self.renderer.set_pixel(self.v[x] + col, self.v[y] + row)):
                            self.v[0xF] = 1

                self.sprite_byte << 1

        elif (op == 0xE000):
            # Skip next instruction if key with the value of Vx is pressed
            if (kk == 0x9E):
                #print("Skip if keyboard press")
                pass

            # Skip next instruction if key with the value of Vx is not pressed
            elif (kk == 0xA1):
                #print("Skip if no keyboard press")
                pass

        elif (op == 0xF000):
            # Set Vx = delay timer value
            if (kk == 0x07):
                self.v[x] = self.delay_timer

            # Wait for a key press, store the value of the key in Vx
            elif (kk == 0x0A):
                #print("Pausing until keypress")
                pass

            # Set delay timer = Vx
            elif (kk == 0x15):
                self.delay_timer = self.v[x]

            # Set sound timer = Vx
            elif (kk == 0x18):
                self.sound_timer = self.v[x]

            # Set I = I + Vx
            elif (kk == 0x1E):
                self.i += self.v[x]

            # Set I = location of sprite for digit Vx
            elif (kk == 0x29):
                self.i = self.v[x] * 5

            # Store BCD representation of Vx in memory locations I, I+1, and I+2
            elif (kk == 0x33):
                self.memory[self.i] = (self.v[x] / 100) # Hundreds
                self.memory[self.i + 1] = ((self.v[x] % 100) / 10) # Tens
                self.memory[self.i + 2] = (self.v[x] % 10) # Ones

            # Store registers V0 through Vx in memory starting at location I
            elif (kk == 0x55):
                for idx in range(x):
                    self.memory[self.i + idx] = self.x[idx]

            # Read registers V0 through Vx from memory starting at location I
            elif (kk == 0x65):
                for idx in range(x):
                    self.x[idx] = self.memory[self.i + idx]


if __name__ == "__main__":
    cpu = CPU()
    #cpu.load_rom("ROMs/test.ch8")
    #cpu.cycle()


# TODOs
# 0xD / draw sprite
# 0xEx9E AND 0xExA1 / keyboard input
# 0xFx0A / pause until keyboard input
