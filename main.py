import pygame
from camera import *
import time, math


def draw_text(scr, text, pos):
    t = font.render(text, True, (255, 255, 255))
    scr.blit(t, pos)

pygame.init()
font = pygame.font.Font(None, 36)
info = pygame.display.Info()
WORLD_SIZES = (100,100)
SCREEN_SIZES = (info.current_w, info.current_h)
bounded_world = True

def main():
    tick = 0
    screen = pygame.display.set_mode(SCREEN_SIZES)
    clock = pygame.time.Clock()
    running = True
    
    BTN_COL2 = (25, 25, 25)
    world = World(screen, WORLD_SIZES if bounded_world else None)
    cam = Camera(SCREEN_SIZES)
    drawer = Drawer(cam)
    pause_btn = pygame.Rect(cam.size[0]-100, cam.size[1]//2-130, 100, 100)
    next_btn = pygame.Rect(cam.size[0]-100, pause_btn.top-130, 100, 100)
    minus_scale = pygame.Rect(cam.size[0]-100, cam.size[1]//2+30, 100, 100)
    plus_scale = pygame.Rect(cam.size[0]-100, minus_scale.bottom+30, 100, 100)
    draw_btn = pygame.Rect(0, cam.size[1]//2-50, 100, 100)

    world.render(cam)
    paused = True
    while running:
        tick += 1
        mouse_pos = pygame.mouse.get_pos()
        btn_touched = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                break
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if minus_scale.collidepoint(mouse_pos):
                        cam.ch_scale(-3)
                        btn_touched=True
                    if plus_scale.collidepoint(mouse_pos):
                        cam.ch_scale(3)
                        btn_touched=True
                    if pause_btn.collidepoint(mouse_pos):
                        paused = not paused
                        btn_touched=True
                    if next_btn.collidepoint(mouse_pos):
                        world.update()
                        btn_touched=True
                    if draw_btn.collidepoint(mouse_pos):
                        drawer.mode += 1
                        if drawer.mode == 3:
                            drawer.mode = 0
                        btn_touched=True
                    else:
                        drawer.hold_s(mouse_pos)
                        cam.hold_s(mouse_pos)
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    cam.hold_e(mouse_pos)
                    if btn_touched: continue
                    drawer.hold_e(mouse_pos)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif e.key == pygame.K_r:
                    paused = True
                    del world
                    world = World(screen, WORLD_SIZES if bounded_world else None)
                    cam.x = 0
                    cam.y = 0
                    cam.cell_s = 20
                elif e.key == pygame.K_TAB:
                    drawer.mode += 1
                    if drawer.mode == 3:
                        drawer.mode = 0
                elif e.key == pygame.K_SPACE:
                    paused = not paused
        if not running:
            break
        if drawer.mode == 0:
            cam.update(mouse_pos)
        else:
            drawer.update(mouse_pos, world)
        tick_start = time.time()
        if tick % 1 == 0 and not paused:
            world.update()
            tick_end = time.time()
        else:
            tick_end = time.time()
            
        screen.fill((0,0,0))
        world.render(cam)
        pygame.draw.rect(screen, (210, 210, 210), minus_scale)
        pygame.draw.rect(screen, BTN_COL2, [minus_scale.left+20, minus_scale.top+45, 60, 10])
        pygame.draw.rect(screen, (210, 210, 210), plus_scale)
        pygame.draw.rect(screen, BTN_COL2, [plus_scale.left+20, plus_scale.top+45, 60, 10])
        pygame.draw.rect(screen, BTN_COL2, [plus_scale.left+45, plus_scale.top+20, 10, 60])
        pygame.draw.rect(screen, (210, 210, 210), pause_btn)
        if paused:
            pygame.draw.polygon(screen, BTN_COL2, [[pause_btn.left+30, pause_btn.top+20], [pause_btn.left+70, pause_btn.top+50], [pause_btn.left+30, pause_btn.bottom-20]])
        else:
            pygame.draw.rect(screen, BTN_COL2, [pause_btn.left+34, pause_btn.top+20, 10, 60])
            pygame.draw.rect(screen, BTN_COL2, [pause_btn.right-45, pause_btn.top+20, 10, 60])
        pygame.draw.rect(screen, (210, 210, 210), next_btn)
        pygame.draw.polygon(screen, BTN_COL2, [[next_btn.left+30, next_btn.top+20], [next_btn.left+60, next_btn.top+50], [next_btn.left+30, next_btn.bottom-20]])
        pygame.draw.polygon(screen, BTN_COL2, [[next_btn.left+50, next_btn.top+20], [next_btn.left+80, next_btn.top+50], [next_btn.left+50, next_btn.bottom-20]])
        pygame.draw.rect(screen, (210, 210, 210), draw_btn)
        if drawer.mode == 1:
            pygame.draw.rect(screen, BTN_COL2, [draw_btn.x+30, draw_btn.y+30, 40, 40])
        elif drawer.mode == 2:
            pygame.draw.line(screen, BTN_COL2, [draw_btn.x+20, draw_btn.y+20], [draw_btn.right-20, draw_btn.bottom-20], 10)
            pygame.draw.line(screen, BTN_COL2, [draw_btn.right-20, draw_btn.y+20], [draw_btn.x+20, draw_btn.bottom-20], 10)
        tick_delta = tick_end-tick_start
        time_text = str(math.floor(tick_delta*1000))
        draw_text(screen, f"{cam.x}:{cam.y}; {int(clock.get_fps())} FPS; {world.step}; {time_text} MSPS", [10,10])
        pygame.display.flip()
        clock.tick(60)
main()