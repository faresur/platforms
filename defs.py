import pygame
import pickle


class World():
    def __init__(self, data, b_dim):
        brick = pygame.image.load("src/img/brick.png")
        floor_brick = pygame.image.load("src/img/floor_brick.png")
        self.block_data = []
        self.object_data = {
            "dwarves": pygame.sprite.Group(),
            "spikes": pygame.sprite.Group(),
            "portals": pygame.sprite.Group(),
            "platforms": pygame.sprite.Group(),
        }

        level_count = 0
        for level in data:
            block_count = 0
            for block in level:
                if block == 1:
                    block_img = pygame.transform.scale(brick, (b_dim, b_dim))
                    block_rect = block_img.get_rect()
                    block_rect.x = block_count * b_dim
                    block_rect.y = level_count * b_dim
                    block = (block_img, block_rect)
                    self.block_data.append(block)
                if block == 2:
                    block_img = pygame.transform.scale(floor_brick, (b_dim, b_dim))
                    block_rect = block_img.get_rect()
                    block_rect.x = block_count * b_dim
                    block_rect.y = level_count * b_dim
                    block = (block_img, block_rect)
                    self.block_data.append(block)
                if block == 3:
                    self.object_data["dwarves"].add(Dwarf(block_count * b_dim, level_count * b_dim, b_dim))
                if block == 4:
                    self.object_data["spikes"].add(Spikes(block_count * b_dim, level_count * b_dim + (b_dim // 2), b_dim))
                if block == 5:
                    self.object_data["portals"].add(Portal(block_count * b_dim, level_count * b_dim - b_dim, b_dim))
                if block == 6:
                    self.object_data["platforms"].add(Platform(block_count * b_dim, level_count * b_dim, b_dim, "hor"))
                if block == 7:
                    self.object_data["platforms"].add(Platform(block_count * b_dim, level_count * b_dim, b_dim, "ver"))
                block_count += 1
            level_count += 1

    def draw(self, screen):
        for block in self.block_data:
            screen.blit(block[0], block[1])


class Character():
    def __init__(self, x, y):
        self.start(x, y)

    def physics(self, screen, world, gameover, victory):
        screen.blit(self.image, self.rect)
        colth = 10

        cooldown = 20
        Dx = Dy = 0

        if not gameover:
            # Controls
            press = pygame.key.get_pressed()

            if press[pygame.K_RIGHT]:
                Dx += 5
                self.counter += 10
                self.dir = 1
            if press[pygame.K_LEFT]:
                Dx -= 5
                self.counter += 10
                self.dir = -1
            if press[pygame.K_UP] and not self.jump and not self.airborne:
                self.accy = -16
                self.jump = True
            if not press[pygame.K_UP]:
                self.jump = False
            if not press[pygame.K_RIGHT] and not press[pygame.K_LEFT]:
                self.counter = 0
                self.index = 0
                if self.dir == 1:
                    self.image = self.imgs_right[self.index]
                elif self.dir == -1:
                    self.image = self.imgs_left[self.index]

            # Gravity
            self.accy += 1
            if self.accy > 30:
                self.accy = 10
            Dy += self.accy

            # Animation
            if self.counter > cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.imgs_right):
                    self.index = 0
                if self.dir == 1:
                    self.image = self.imgs_right[self.index]
                if self.dir == -1:
                    self.image = self.imgs_left[self.index]

            # Collision
            self.airborne = True
            for block in world.block_data:
                if block[1].colliderect(self.rect.x, self.rect.y + Dy, self.width, self.height):
                    if self.accy < 0:
                        Dy = block[1].bottom - self.rect.top
                        self.accy = 0
                    elif self.accy >= 0:
                        Dy = block[1].top - self.rect.bottom
                        self.accy = 0
                        self.airborne = False
                if block[1].colliderect(self.rect.x + Dx, self.rect.y, self.width, self.height):
                    Dx = 0

            if pygame.sprite.spritecollide(self, world.object_data["spikes"], False) or pygame.sprite.spritecollide(self, world.object_data["dwarves"], False):
                return -1
            if pygame.sprite.spritecollide(self, world.object_data["portals"], False):
                return 1

            for platform in world.object_data["platforms"]:
                if platform.rect.colliderect(self.rect.x + Dx, self.rect.y, self.width, self.height):
                    Dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + Dy, self.width, self.height):
                    if abs((self.rect.top + Dy) - platform.rect.bottom) < colth:
                        self.accy = 0
                        Dy = platform.rect.bottom - self.rect.top + 1
                    elif self.accy >= 0:
                        self.rect.bottom = platform.rect.top - 1
                        Dy = 0
                        self.airborne = False
                    if platform.mov == "hor":
                        self.rect.x += platform.dir
                        
                    
            # Updating
            self.rect.x += Dx
            self.rect.y += Dy

            return 0

        elif gameover:
            self.image = self.dead

    def start(self, x, y):
        self.imgs_right = [pygame.transform.scale(pygame.image.load(f"src/img/char_mov{i}.png"), (35, 70)) for i in range(3)]
        self.imgs_left = [pygame.transform.flip(img, True, False) for img in self.imgs_right]
        self.index = self.counter = self.dir = self.accy = 0
        self.image = self.imgs_right[self.index]
        self.dead = pygame.transform.scale(pygame.image.load("src/img/char_dead.png"), (35, 70))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.width, self.height = self.image.get_width(), self.image.get_height()
        self.jump, self.airborne = False, True


class Dwarf(pygame.sprite.Sprite):
    def __init__(self, x, y, b_dim):
        pygame.sprite.Sprite.__init__(self)
        dwarf = pygame.image.load("src/img/dwarf.png")
        self.image = pygame.transform.scale(dwarf, (b_dim, b_dim))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.dir = 1
        self.flip_cond = 0
    def update(self):
        self.rect.x += self.dir
        self.flip_cond += 1
        if self.flip_cond >= 50:
            self.dir *= -1
            self.flip_cond *= -1


class Spikes(pygame.sprite.Sprite):
    def __init__(self, x, y, b_dim):
        pygame.sprite.Sprite.__init__(self)
        spikes = pygame.image.load("src/img/spikes.png")
        self.image = pygame.transform.scale(spikes, (b_dim, b_dim // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y, b_dim):
        pygame.sprite.Sprite.__init__(self)
        portal = pygame.image.load("src/img/portal.png")
        self.image = pygame.transform.scale(portal, (b_dim, b_dim * 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, b_dim, card):
        pygame.sprite.Sprite.__init__(self)
        spikes = pygame.image.load("src/img/platform.png")
        self.image = pygame.transform.scale(spikes, (b_dim, b_dim // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dir = 1
        self.flip_cond = 0
        self.mov = card

    def update(self):  
        if self.mov == "hor":
            self.rect.x += self.dir
        elif self.mov == "ver":
            self.rect.y += self.dir
            
        self.flip_cond += 1
        if self.flip_cond >= 50:
            self.dir *= -1
            self.flip_cond *= -1


class Button():
    def __init__(self, x, y, img):
        resetbtn_img = pygame.image.load(img)
        self.image = pygame.transform.scale(resetbtn_img, (200, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.click = False
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        reset = False

        mouse_click = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and mouse_click == 1 and self.click == False:
            self.click = True
            reset = True
        if mouse_click == 0:
            self.click = False
        return reset


def resetlvl(old_world, character, level, height, b_dim):
    character.start(100, height - 200)

    for obj in old_world.object_data:
        old_world.object_data[obj].empty()

    return World(pickle.load(open(f"src/lvl/level{level}", "rb")), b_dim)