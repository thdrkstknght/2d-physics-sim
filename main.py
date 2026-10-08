import pygame

pygame.init()
scr = pygame.display.set_mode((720, 480))
clck = pygame.time.Clock()
r = True
rect = (scr.get_width()/2, scr.get_height()/2, 50, 50)
print(rect)
while r:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    scr.fill('white')
    pygame.draw.rect(scr, "black", rect)
    
    
    pygame.display.flip()
    clck.tick(144)
