import pygame

pygame.init()
scr = pygame.display.set_mode((720, 480))
clck = pygame.time.Clock()
r = True
g = 0.981
pw = 50
ph = 50
rect = pygame.Rect((scr.get_width()/2), 0, pw, ph)
py = float(rect.y)
px = float(rect.x)
pvy = 0
pvx = 0
drag = False
prev_left = False

pygame.display.set_caption('sim')
font = pygame.font.Font('freesansbold.ttf', 16)

while r:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            r = False
    
    mx, my = pygame.mouse.get_pos()
    left, middle, right = pygame.mouse.get_pressed()
    
    if rect.collidepoint(mx, my) and not prev_left and left:
        drag = True
        grabbed_x = px - mx
        grabbed_y = py - my
    elif left == False:
        drag = False
        prev_left = left
    
    if drag:
        new_x = min(max(mx + grabbed_x, 0), scr.get_width() - pw)
        new_y = min(max(my + grabbed_y, 0), scr.get_height() - ph)
        pvx = new_x - px
        pvy = new_y - py
        px, py = new_x, new_y
    
    else:
        pvy += g
        px += pvx
        py += pvy

        if py + ph >= scr.get_height():
            py = scr.get_height() - ph
            pvy = -pvy * 0.7
            if abs(pvy) <= 2:
                pvy = 0
            pvx *= 0.95
        if px < 0:
            px = 0
            pvx = -pvx * 0.7
        elif px + pw > scr.get_width():
            px = scr.get_width() - pw
            pvx = -pvx * 0.7
                
    rect.y = round(py)
    rect.x = round(px)
        
    #if mx >= (rect.x-(pw/2)) and mx <= (rect.x+(pw/2)) and my >= (rect.y-(pw/2)) and my <= (rect.y+(pw/2)) and left == True:
        #rect.x = mx
        #rect.y = my
        
    scr.fill('white')
            
    fpstext_surface = font.render(f"FPS: {round(clck.get_fps())}", True, "black")
    pvytext_surface = font.render(f"Velocity Y: {pvy:.2f}", True, "black") 
    pvxtext_surface = font.render(f"Velocity x: {pvx:.2f}", True, "black") 
    fpstext_rect = fpstext_surface.get_rect()
    pvytext_rect = pvytext_surface.get_rect()
    pvxtext_rect = pvxtext_surface.get_rect()
    fpstext_rect.topleft = (0, 0)
    pvxtext_rect.topleft = (0, 15)
    pvytext_rect.topleft = (0, 30)
    scr.blit(fpstext_surface, fpstext_rect)
    scr.blit(pvxtext_surface, pvxtext_rect)
    scr.blit(pvytext_surface, pvytext_rect)
    
    pygame.draw.rect(scr, "black", rect)
    
    pygame.display.flip()
    clck.tick(60)
