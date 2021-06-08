from math import floor
from os import system

# constants
WIDTH = 64
HEIGHT = 32

class Renderer:
    def __init__(self):
        self.display = [0] * (WIDTH * HEIGHT)

    def set_pixel(self, x, y):
        # wrap if pixel out of bounds
        if (x > WIDTH):
            x -= WIDTH
        elif (x < 0):
            x += WIDTH

        if (y > HEIGHT):
            y = HEIGHT
        elif (y < 0):
            y += HEIGHT

        # calculate index in array based on position, toggle pixel
        di = x + (y * HEIGHT)
        self.display[di] = 1 if self.display[di] == 0 else 0

        # return true if pixel was erased
        return not self.display[di]

    def clear(self):
        self.display = [0] * (WIDTH * HEIGHT)

    def render(self):
        system('cls')
        lines = [""] * HEIGHT

        # loop through each pixel in array
        for i in range(WIDTH * HEIGHT):
            x = i % WIDTH
            y = floor(i / WIDTH)

            # if value at display[i] == 1, draw pixel
            if (self.display[i]):
                lines[y] += "#"
            else:
                lines[y] += " "

        for line in lines:
            print(line)

if __name__ == "__main__":
    try:
        r = Renderer()
        print("Renderer initialized")
    except:
        print("Error initializing")
