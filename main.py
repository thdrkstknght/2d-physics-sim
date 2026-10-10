import pygame

pygame.init()
scr = pygame.display.set_mode((720, 480))
clck = pygame.time.Clock()
r = True
g = 0.981
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
        self.n = len(gameobjects)

    
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
        
def collision_phys(object_dict, collision_bounce=0.5):
    for i in range(len(object_dict)):
        for j in range(i+1, len(object_dict)):
            obj_a, obj_b = object_dict[i], object_dict[j]
            overlap_x = min(obj_a.px + obj_a.w, obj_b.px + obj_b.w)-max(obj_a.px, obj_b.px)
            overlap_y = min(obj_a.py + obj_a.h, obj_b.py + obj_b.h)-max(obj_a.py, obj_b.py)
                
            if overlap_x<=0 or overlap_y<=0:
                continue
                
            state_a = 0 if obj_a.drag else 1
            state_b = 0 if obj_b.drag else 1
                
            total = state_a + state_b
            if total == 0:
                continue
                    
            if overlap_x < overlap_y:
                n = 1 if obj_a.px < obj_b.px else -1
                obj_a.px -= (overlap_x * n * state_a)/total
                obj_b.px += (overlap_x * n * state_b)/total
                
                reletive_v = (obj_b.vx - obj_a.vx) * n
                
                if reletive_v<0:
                    e = collision_bounce #if reletive_v<-1 else 0
                    col_force = -(1+e) * reletive_v/total
                    obj_a.vx -= col_force * n * state_a
                    obj_b.vx += col_force * n * state_b
            else:
                n = 1 if obj_a.py < obj_b.py else -1
                obj_a.py -= (overlap_y * n * state_a)/total
                obj_b.py += (overlap_y * n * state_b)/total
                
                reletive_v = (obj_b.vy - obj_a.vy) * n
                
                if reletive_v<0:
                    e = collision_bounce #if reletive_v<-1 else 0
                    col_force = -(1+e) * reletive_v/total
                    obj_a.vy -= col_force * n * state_a
                    obj_b.vy += col_force * n * state_b
                    
            obj_a.sync()
            obj_b.sync()
            
def clamp_to_screen(objs):
    w, h = scr.get_width(), scr.get_height()
    for i in range(len(objs)):
        objct = objs[i]
        objct.px = min(max(objct.px, 0), w - objct.w)
        objct.py = min(objct.py, h - objct.h)
        objct.sync()
pygame.display.set_caption('sim')
font = pygame.font.Font('freesansbold.ttf', 16)

def textbox(surface, font, text: str, x, y, colour: str):
    srfc = font.render(text, True, colour)
    rct = srfc.get_rect()
    rct.topleft = (x, y)
    surface.blit(srfc, rct)
    

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
    for _ in range(3):
        collision_phys(gameobjects)
    clamp_to_screen(gameobjects)
    
    scr.fill('white')
    
    for o in gameobjects:
        o.draw_rect(scr, "black")


   
   
    textbox(scr, font, f"FPS: {round(clck.get_fps())}", 0, 0, "black")
    _xIdjanO = 15
    for o in gameobjects:
        textbox(scr, font, f"rectp{o.n}: x{o.rect.x}, y{o.rect.y}", 0, _xIdjanO, "black")
        _xIdjanO += 15
        textbox(scr, font, f"rectv{o.n}: dx{o.vx:.1f}, dy{o.vy:.1f}", 0, _xIdjanO, "black")
        _xIdjanO +=15
    
    
    pygame.display.flip()
    clck.tick(60)
