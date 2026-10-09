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
gameobjects = []
class create_rect():
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.px = float(self.rect.x)
        self.py = float(self.rect.y)
        self.vx = 0
        self.vy = 0
        self.drag = False
        self.grabbed_x = 0
        self.grabbed_y = 0
        self.w = w
        self.h = h
        gameobjects.append(self)

    
    def mouse_handler(self, mx, my, left_press, prevleft_press):
        if self.rect.collidepoint(mx, my) and not prevleft_press and left_press:
            self.drag = True
            self.grabbed_x = self.px - mx
            self.grabbed_y = self.py - my
        elif left_press == False:
            self.drag = False
    
    def phys_update(self, mx, my, bounce):
        if self.drag:
                new_x = min(max(mx + self.grabbed_x, 0), scr.get_width() - self.w)
                new_y = min(max(my + self.grabbed_y, 0), scr.get_height() - self.h)
                self.vx = new_x - self.px
                self.vy = new_y - self.py
                self.px, self.py = new_x, new_y
            
        else:
            self.vy += g
            self.px += self.vx
            self.py += self.vy
        
            if self.py + self.h >= scr.get_height():
                self.py = scr.get_height() - self.h
                self.vy = -self.vy * bounce
                if abs(self.vy) <= 2:
                    self.vy = 0
                self.vx *= 0.95
            if self.px < 0:
                self.px = 0
                self.vx = -self.vx * 0.7
            elif self.px + self.w > scr.get_width():
                self.px = scr.get_width() - self.w
                self.vx = -self.vx * 0.7
                        
        self.sync()
        
    def sync(self):
        self.rect.x = round(self.px)
        self.rect.y = round(self.py)
        
    def draw_rect(self, surface, colour):
        pygame.draw.rect(surface, colour, self.rect)
        

pygame.display.set_caption('sim')
font = pygame.font.Font('freesansbold.ttf', 16)

box = create_rect(480, 0, 50, 50)
box1 = create_rect(380, 0, 50, 50)

while r:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            r = False
            
    m_x, m_y = pygame.mouse.get_pos()
    rleft = pygame.mouse.get_pressed()[0]

    for o in gameobjects:
        o.mouse_handler(m_x, m_y, rleft, prev_left)
    prev_left = rleft
    
    for o in gameobjects:
        o.phys_update(m_x, m_y, 0.7)
    
    scr.fill('white')
    
    for o in gameobjects:
        o.draw_rect(scr, "black")


   
   
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
    
    
    pygame.display.flip()
    clck.tick(60)
