# this is the small module of mine to make a reusable gui elements like
# buttons and switches - just to make it possible to create some
# user interface for the pygame based simulations
"""
Idea:

gui_box - the gui object that defines the bounding box and keeps all the elements within

gui_btn - just a push button 
gui_switch - 2 state switch
"""

import pygame


class gui_box:
    def __init__(self, x, y, w, h, canvas):
        self.x0, self.y0, self.W, self.H = x, y, w, h  # type: ignore
        self.x1 = x + w
        self.y1 = y + h
        self.box = [x, y, self.x1, self.y1]

        self.canvas = canvas
        self.elements = []

    def isOver(self, ex, ey):
        return (self.x0 < ex < self.x1) and (self.y0 < ey < self.y1)

    def highlight(self, ex, ey):
        for e in self.elements:
            e.isOver(ex, ey)

    def action(self, ex, ey):
        for e in self.elements:
            if e.isOver(ex, ey):
                e.action()

    def addElement(self, element):
        element.setUp(self.canvas, self.x0, self.y0)
        self.elements.append(element)

    def draw(self):
        for e in self.elements:
            e.draw()


class gui_btn:
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        txt: str,
        action: callable,
        border: int = 2,
        color: tuple[int, int, int] = (75, 10, 10),
        bcolor: tuple[int, int, int] = (30, 5, 5),
        acolor: tuple[int, int, int] = (95, 30, 30),
        txtcolor: tuple[int, int, int] = (200, 200, 200),
        txtsize: int = 20,
    ):

        self.action = action
        self.x0, self.y0, self.W, self.H = x, y, w, h  # type: ignore
        self.x1 = x + w
        self.y1 = y + h
        self.txt = txt
        self.canvas = None

        self.border = border
        self.color = color
        self.bcolor = bcolor
        self.acolor = acolor
        self.txtcolor = txtcolor

        self.isHighlighted: bool = False

        font = pygame.font.SysFont(None, txtsize)
        self.text = font.render(self.txt, True, self.txtcolor)

    def setUp(self, canvas: pygame.display, x0: int, y0: int):
        self.canvas = canvas
        self.x0 += x0
        self.y0 += y0
        self.x1 += x0
        self.y1 += y0

        self.text_rect = self.text.get_rect(
            center=(self.x0 + self.W // 2, self.y0 + self.H // 2)
        )

    def isOver(self, ex: int, ey: int):
        self.isHighlighted = (self.x0 < ex < self.x1) and (self.y0 < ey < self.y1)
        return self.isHighlighted

    def draw(self):
        # Draw the border rectangle
        pygame.draw.rect(self.canvas, self.bcolor, (self.x0, self.y0, self.W, self.H))

        # Draw the inner filled rectangle
        if self.isHighlighted:
            clr = self.acolor
        else:
            clr = self.color
        pygame.draw.rect(
            self.canvas,
            clr,
            (
                self.x0 + self.border,
                self.y0 + self.border,
                self.W - self.border,
                self.H - self.border,
            ),
        )
        self.canvas.blit(self.text, self.text_rect)


if __name__ == "__main__":
    pass
