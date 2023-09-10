from defs import *
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()

# Constants

MAINMENU = True
GAMEOVER = VICTORY = DEAD = False
LIVES = 2
CRTLVL = MINLVL = 6
MAXLVL = 7
FPS = 60
b_dim = 50
dimension = width, height = 1000, 700


# Game screen
screen = pygame.display.set_mode(dimension)
pygame.display.set_caption("Platforms")

# Imgs
BG = pygame.image.load("src/img/bground.png")
VICSCREEN = pygame.image.load("src/img/victory_screen.png")
DEATHSCREEN = pygame.image.load("src/img/death_screen.png")
HEART = pygame.transform.scale(pygame.image.load("src/img/heart.png"), (50, 50))


# Object inits

character = Character(100, height - 200)

world = World(pickle.load(open(f"src/lvl/level{CRTLVL}", "rb")), b_dim)

restartbtn = Button(width // 2 - 100, height // 2 - 40, "src/img/restart_button.png")
exitbtn = Button(width // 2 + 100, height // 2 - 40, "src/img/exit_button.png")
startbtn = Button(width // 2 - 250, height // 2 - 40, "src/img/start_button.png")
nxtlvlbtn = Button(width // 2 - 100, height // 2 - 40, "src/img/nextlevel_button.png")


# Game loop

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        MAINMENU = True

    if MAINMENU:
        screen.blit(BG, (0, 0))
        if startbtn.draw(screen):
            MAINMENU = False
        if exitbtn.draw(screen):
            running = False
    elif VICTORY:
        CRTLVL += 1
        if CRTLVL <= MAXLVL:
            b_data = []
            world = resetlvl(world, character, CRTLVL, height, b_dim)
            VICTORY = False
        else:
            screen.blit(VICSCREEN, (0, 0))
            if restartbtn.draw(screen):
                CRTLVL = MINLVL
                world = resetlvl(world, character, CRTLVL, height, b_dim)
                VICTORY = False
    elif DEAD:
        screen.blit(DEATHSCREEN, (0, 0))
        if restartbtn.draw(screen):
            CRTLVL = MINLVL
            world = resetlvl(world, character, CRTLVL, height, b_dim)
            LIVES = 2
            DEAD = False         
    else:
        # Setting FPS
        clock.tick(FPS)

        screen.blit(BG, (0, 0))
        world.draw(screen)
        
        char_cond = character.physics(screen, world, GAMEOVER, VICTORY)

        if char_cond == 1:
            VICTORY = True
        if char_cond == -1:
            GAMEOVER = True

        if not GAMEOVER:
            world.object_data["dwarves"].update()
            world.object_data["platforms"].update()

        for obj in world.object_data:
            world.object_data[obj].draw(screen)
        
        for i in range(LIVES+1):
            screen.blit(HEART, (width//2 + i*50 - 86, 0))

        if GAMEOVER and restartbtn.draw(screen) and LIVES:
                b_data = []
                world = resetlvl(world, character, CRTLVL, height, b_dim)
                GAMEOVER = False
                LIVES -= 1
        elif GAMEOVER and not LIVES:
            GAMEOVER = False
            DEAD = True

    pygame.display.update()

pygame.quit()
