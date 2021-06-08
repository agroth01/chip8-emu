from time import time, sleep

from render import Renderer
from cpu import CPU

FPS_INTERVAL = 1 / 60

def run(rom):
    # Create cpu
    cpu = CPU(Renderer())
    cpu.load_rom(rom)

    renderer = Renderer()

    while True:
        # Used for tracking time in cycle
        start_time = time()

        # Do one cycle
        try:
            cpu.cycle()
            #print(cpu.pc)
        except:
            pass

        # Keep program running at 60 FPS
        elapsed_time = time() - start_time
        if (elapsed_time < FPS_INTERVAL):
            sleep(FPS_INTERVAL - elapsed_time)

if __name__ == "__main__":
    run("ROMs/test.ch8")
