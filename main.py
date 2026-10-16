import pygame
import random

pygame.init()
scr = pygame.display.set_mode((720, 480))   # the game window
clck = pygame.time.Clock()                  # used to cap the frame rate and read the FPS
r = True                                    # main loop runs while this is True
g = 0.981                                   # gravity: added to a box's downward speed every frame
prev_left = False                           # was the left mouse button down last frame?
prev_right = False                          # was the right mouse button down last frame?
gameobjects = []                            # every box registers itself in here


# a physics box. each box owns its position, speed and drag state
class create_rect():
    def __init__(self, x, y, w, h, matfriction, mass, isstatic: bool):
        self.rect = pygame.Rect(x, y, w, h)     # whole-number rect, used for drawing and clicks
        self.mass = mass                        # heavier boxes get pushed around less in collisions
        self.matfriction = matfriction          # 1 = slippery, lower = grippier (speed multiplier)
        self.isstatic = isstatic                # static boxes never move on their own
        # the real position is kept as floats, because a Rect can only hold whole numbers
        # and would throw away small movements
        self.px = float(self.rect.x)
        self.py = float(self.rect.y)
        self.vx = 0                             # horizontal speed (pixels per frame)
        self.vy = 0                             # vertical speed (pixels per frame)
        self.drag = False                       # True while the mouse is holding this box
        self.hud = False                        # True while this box's little menu is open
        self.grabbed_x = 0                      # where on the box the mouse grabbed it,
        self.grabbed_y = 0                      # so the box doesn't snap its corner to the cursor
        self.w = w
        self.h = h
        gameobjects.append(self)                # join the list so the main loop updates and draws us
        self.n = len(gameobjects)               # box number, shown in the on-screen readout

    
    # decides if this box was grabbed, released, or right-clicked this frame
    def mouse_handler(self, mx, my, left_press, prevleft_press, right_press, prevright_press):
        # grab only on the frame the click starts (button down now, not down last frame)
        if self.rect.collidepoint(mx, my) and not prevleft_press and left_press:
            self.drag = True
            self.grabbed_x = self.px - mx       # remember the offset between the corner and the mouse
            self.grabbed_y = self.py - my
        elif left_press == False:
            self.drag = False                   # letting go of the button drops the box
        # right-click on the box opens or closes its menu
        if self.rect.collidepoint(mx, my) and not prevright_press and right_press:
            self.hud = not self.hud
    
    # moves the box for one frame
    def phys_update(self, mx, my, bounce):
        if self.drag:
                # follow the mouse, but keep the whole box inside the window
                new_x = min(max(mx + self.grabbed_x, 0), scr.get_width() - self.w)
                new_y = min(max(my + self.grabbed_y, 0), scr.get_height() - self.h)
                # speed = how far the box moved this frame, so letting go throws it
                self.vx = new_x - self.px
                self.vy = new_y - self.py
                self.px, self.py = new_x, new_y
        elif self.isstatic:
            # static boxes stay put and have no speed
            self.vx = 0
            self.vy = 0
        else:
            self.vy += g                        # gravity speeds the fall up
            self.px += self.vx                  # move by the current speed
            self.py += self.vy
        
            # floor: put the box back on top of it and bounce
            if self.py + self.h >= scr.get_height():
                self.py = scr.get_height() - self.h
                self.vy = -self.vy * bounce     # flip direction, losing some energy
                if abs(self.vy) <= 2:
                    self.vy = 0                 # too small to bounce, so it settles
                self.vx *= ((0.95 + self.matfriction)/2)    # sliding on the floor slows it down
            # left and right walls: bounce back with some energy loss
            if self.px < 0:
                self.px = 0
                self.vx = -self.vx * 0.7
            elif self.px + self.w > scr.get_width():
                self.px = scr.get_width() - self.w
                self.vx = -self.vx * 0.7
                        
        self.sync()
    
    # draws the small "static" button above the box (called while its menu is open)
    def hud_system(self):
        colour = "red" if self.isstatic else "black"
        # put the button above the box, or below it if there's no room at the top of the window
        hud_y = self.py - 20 if self.py >= 20 else self.py + self.h + 2
        button(scr, font, "static", self.px + (self.w/2), hud_y, 0, 0, colour, "white", self.staticswitch ,clicked)

    # copies the float position into the rect, rounded to whole pixels
    def sync(self):
            self.rect.x = round(self.px)
            self.rect.y = round(self.py)
            
    def draw_rect(self, surface, colour):
        # static boxes are grey, normal boxes are black (this replaces the colour passed in)
        colour = (169, 169, 169) if self.isstatic else "black"
        pygame.draw.rect(surface, colour, self.rect)
        
    # called by the "static" button: turns static mode on or off
    def staticswitch(self):
        if self.isstatic == False:
            self.isstatic = True
        else:
            self.isstatic = False
        self.vx = 0                             # clear the speed so it doesn't carry over
        self.vy = 0


# checks every pair of boxes. if two overlap, it pushes them apart and bounces them
def collision_phys(object_dict, collision_bounce=0.5):
    for i in range(len(object_dict)):
        for j in range(i+1, len(object_dict)):      # starting at i+1 checks each pair only once
            obj_a, obj_b = object_dict[i], object_dict[j]
            # how far the boxes overlap on each axis (zero or negative means a gap)
            overlap_x = min(obj_a.px + obj_a.w, obj_b.px + obj_b.w)-max(obj_a.px, obj_b.px)
            overlap_y = min(obj_a.py + obj_a.h, obj_b.py + obj_b.h)-max(obj_a.py, obj_b.py)
                
            # they only collide if they overlap on both axes
            if overlap_x<=0 or overlap_y<=0:
                continue
                
            # inverse mass: how easily each box gets pushed.
            # a held or static box counts as 0, so it acts like an immovable wall
            state_a = 0 if obj_a.drag or obj_a.isstatic else 1 / obj_a.mass
            state_b = 0 if obj_b.drag or obj_b.isstatic else 1 / obj_b.mass
                
            total = state_a + state_b
            if total == 0:
                continue                        # neither box can move, so nothing to do
                    
            # separate along the axis with the smaller overlap (that's the side that was actually hit)
            if overlap_x < overlap_y:
                n = 1 if obj_a.px < obj_b.px else -1        # n points from a to b
                # push the boxes apart, the lighter one moving more
                obj_a.px -= (overlap_x * n * state_a)/total
                obj_b.px += (overlap_x * n * state_b)/total
                
                # how fast the boxes approach each other (negative means they're moving together)
                reletive_v = (obj_b.vx - obj_a.vx) * n
                
                if reletive_v<0:
                    # very slow hits get no bounce, which stops resting boxes from jittering
                    e = collision_bounce if reletive_v<-1 else 0
                    # the velocity change that makes them separate at e times their approach speed
                    col_force = -(1+e) * reletive_v/total
                    obj_a.vx -= col_force * n * state_a
                    obj_b.vx += col_force * n * state_b
            else:
                # same as above, but for a hit from above or below
                n = 1 if obj_a.py < obj_b.py else -1
                obj_a.py -= (overlap_y * n * state_a)/total
                obj_b.py += (overlap_y * n * state_b)/total
                
                reletive_v = (obj_b.vy - obj_a.vy) * n
                
                if reletive_v<0:
                    e = collision_bounce if reletive_v<-1 else 0
                    col_force = -(1+e) * reletive_v/total
                    obj_a.vy -= col_force * n * state_a
                    obj_b.vy += col_force * n * state_b
                # the box on top slides on the one below, so it uses the lower box's friction.
                # a held box is skipped so friction doesn't weaken a throw
                if n == 1 and not obj_a.drag:
                    obj_a.vx *= obj_b.matfriction
                elif n == -1 and not obj_b.drag:
                    obj_b.vx *= obj_a.matfriction
                
            obj_a.sync()
            obj_b.sync()
            

# keeps every box inside the window after collisions pushed them around.
# there's no top limit, so boxes can fly above the screen and fall back down
def clamp_to_screen(objs):
    w, h = scr.get_width(), scr.get_height()
    for i in range(len(objs)):
        objct = objs[i]
        objct.px = min(max(objct.px, 0), w - objct.w)   # stay between the left and right walls
        objct.py = min(objct.py, h - objct.h)           # stay above the floor
        objct.sync()
pygame.display.set_caption('sim')
font = pygame.font.Font('freesansbold.ttf', 16)


# draws a line of text with its top-left corner at (x, y)
def textbox(surface, font, text: str, x, y, colour: str):
    srfc = font.render(text, True, colour)      # turn the text into an image
    rct = srfc.get_rect()
    rct.topleft = (x, y)
    surface.blit(srfc, rct)
    

# draws a button and runs `function` when it is clicked.
# `clicked` is only True on the frame the mouse button went down, so one click runs it once
def button(surface, font, text: str, x, y, w, h, colour_rect:str, colour_text:str, function, clicked):
    srfc = font.render(text, True, colour_text)
    rct = srfc.get_rect()
    wn = rct.width + w                          # w and h are extra padding around the text
    hn = rct.height + h
    rect = pygame.Rect(x-(w/2), y-(h/2), wn, hn)
    pygame.draw.rect(surface, colour_rect, rect)
    rct.topleft = (x, y)
    surface.blit(srfc, rct)
    m_x, m_y = pygame.mouse.get_pos()
    if rect.collidepoint(m_x, m_y) and clicked:
        function()
        

# a box you can type into. click it to select it, press Enter to submit the text
class inp_textbox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.usertext = ""                      # what has been typed so far
        self.selected = False                   # only listens to the keyboard while selected
    
    # call this once for every pygame event.
    # it returns the typed text when Enter is pressed, and None for everything else
    def box_handler(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # clicking inside selects the box, clicking anywhere else deselects it
            self.selected = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.selected:
            if event.key == pygame.K_RETURN:
                submited = self.usertext
                self.usertext = ""              # clear the box after submitting
                return submited
            elif event.key == pygame.K_BACKSPACE:
                self.usertext = self.usertext[:-1]          # delete the last character
            elif event.unicode.isprintable():
                self.usertext += event.unicode              # add the typed character
        return None
    
    def draw_box(self, active_colour, deactive_colour, background_colour, text_colour, surface):
        border = active_colour if self.selected else deactive_colour
        pygame.draw.rect(surface, background_colour, self.rect)
        pygame.draw.rect(surface, border, self.rect, 1)
        srfc = font.render(self.usertext, True, text_colour)
        # clip so long text can't draw outside the box
        surface.set_clip(self.rect.inflate(-8, -4))
        surface.blit(srfc, (self.rect.x + 6, self.rect.y + (self.rect.height - srfc.get_height()) // 2))
        surface.set_clip(None)                  # turn clipping off again so everything else draws normally


box = inp_textbox(620, 20, 100, 24)             # the box where you type "width height mass"
box_submitted = ""
gw, gh, m = 50, 50, 1                           # size and mass of the next created box

while r:
    clicked = False                             # reset every frame, so it's True only on the click frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            r = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = True
        # give every event to the textbox. it returns text only when Enter is pressed
        box_submitted = box.box_handler(event)
        if box_submitted is not None:
            try:
                # "80 30 5" becomes three numbers: width, height, mass
                new_w, new_h, new_m = map(int, box_submitted.split())
                # only accept sensible values (mass 0 would divide by zero in collisions)
                if 5 <= new_w <= 400 and 5 <= new_h <= 400 and new_m >= 1:
                    gw, gh, m = new_w, new_h, new_m
            except ValueError:
                pass                            # not three whole numbers, so keep the old values
    
        
    m_x, m_y = pygame.mouse.get_pos()
    rleft = pygame.mouse.get_pressed()[0]       # index 0 is the left button
    rright = pygame.mouse.get_pressed()[2]      # index 2 is the right button (1 is the middle one)

    # 1. mouse input: grabs, releases and right-clicks
    for o in gameobjects:
        o.mouse_handler(m_x, m_y, rleft, prev_left, rright, prev_right)
    prev_left = rleft                           # save for next frame, after every box has used it
    prev_right = rright
    
    # 2. move every box
    for o in gameobjects:
        o.phys_update(m_x, m_y, 0.7)
    # 3. resolve collisions (three passes make stacks steadier), then keep everything on screen
    for _ in range(3):
        collision_phys(gameobjects, 0.5)
    clamp_to_screen(gameobjects)
    
    
    # 4. draw everything, back to front. the background goes first, since it paints over the whole window
    scr.fill('white')
    box.draw_box("red", "black", "white", "black", scr)
    
    for o in gameobjects:
        o.draw_rect(scr, "black")
    
    # the boxes' menus are drawn after the boxes so they show on top
    for o in gameobjects:
        if o.hud:
            o.hud_system()
    
    # clicking this creates a box using the size and mass typed into the textbox
    button(scr, font, "create rect", 630, 0, 0, 0, "black", "white", lambda: create_rect(random.randint(50, 420), 0, gw, gh, 0.9, m, False), clicked)
    textbox(scr, font, f"FPS: {round(clck.get_fps())}", 0, 0, "black")
    # position and speed readout for every box, one line each, 15 pixels apart
    _xIdjanO = 15
    for o in gameobjects:
        textbox(scr, font, f"rectp{o.n}: x{o.rect.x}, y{o.rect.y}", 0, _xIdjanO, "black")
        _xIdjanO += 15
        textbox(scr, font, f"rectv{o.n}: dx{o.vx:.1f}, dy{o.vy:.1f}", 0, _xIdjanO, "black")
        _xIdjanO +=15
        
    pygame.display.flip()                       # show the finished frame
    clck.tick(60)                               # cap at 60 frames per second
