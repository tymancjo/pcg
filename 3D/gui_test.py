import pygame
import sys

import mypygamegui as gui

# action function
def akcja():
    print('Akcja!')

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Navy Blue Window')

# Define colors
NAVY_BLUE = (0, 0, 128)
OTHER_BLUE = (0, 25, 128)

# defining gui

my_gui = gui.gui_box(30,30,100,123,screen)
btn01 = gui.gui_btn(10,10,50,20,'OK',akcja)
my_gui.addElement(btn01)




# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_x, mouse_y = event.pos
            if my_gui.isOver(mouse_x,mouse_y):
                my_gui.action(mouse_x,mouse_y)
            

    screen.fill(NAVY_BLUE)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if my_gui.isOver(mouse_x,mouse_y):
        my_gui.highlight(mouse_x,mouse_y)
    my_gui.draw()


    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
