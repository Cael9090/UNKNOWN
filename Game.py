import pygame
from os import listdir
from os.path import isfile, join
import random
import sys

pygame.init()

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

BLACK=(0,0,0)
WHITE=(255,255,255)
RED = (255, 0, 0)
font = pygame.font.Font(None, 36)

window = pygame.display.set_mode((WIDTH, HEIGHT))

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Cover Screen Test")


try:
    font = pygame.font.Font(None, 36)  
except pygame.error as e:
    print(f"Font could not be loaded: {e}")
    sys.exit()



def draw_cover(window):
    window.fill(WHITE)  

    
    cover_text = font.render("A Game That Will Make You Question Your Life Choices", True, BLACK)
    start_text = font.render("Press SPACE to Start", True, BLACK)

    
    cover_text_pos = (
    window.get_width() // 2 - cover_text.get_width() // 2, window.get_height() // 2 - cover_text.get_height())
    start_text_pos = (
    window.get_width() // 2 - start_text.get_width() // 2, window.get_height() // 2 + cover_text.get_height() // 2)

    
    window.blit(cover_text, cover_text_pos)
    window.blit(start_text, start_text_pos)

    
    pygame.display.flip()



def main():
    cover_mode = True
    while cover_mode:
        draw_cover(window)

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    cover_mode = False


main()


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 60

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 65, 16, 32)
    fire.on()
    floor = []
    for i in range(-WIDTH // block_size, (WIDTH * 20) // block_size):

        floor.append(Block(i * block_size, HEIGHT - block_size, block_size))
    objects= [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire,
              Block(block_size * 4, HEIGHT - block_size * 4, block_size),
              Block(block_size * 5, HEIGHT - block_size * 4, block_size),
              Block(block_size * 6, HEIGHT - block_size * 4, block_size),
              Block(block_size * 7, HEIGHT - block_size * 4, block_size),
              Block(block_size * 7, HEIGHT - block_size * 3, block_size),
              Block(block_size * 7, HEIGHT - block_size * 2, block_size),
              Block(block_size * 9, HEIGHT - block_size * 6, block_size),
              Block(block_size * 11, HEIGHT - block_size * 8, block_size),
              Block(block_size * 13, HEIGHT - block_size * 6, block_size),
              Block(block_size * 16, HEIGHT - block_size * 6, block_size),
              Block(block_size * 17, HEIGHT - block_size * 6, block_size),
              Block(block_size * 18, HEIGHT - block_size * 6, block_size),
              Block(block_size * 19, HEIGHT - block_size * 6, block_size),
              Block(block_size * 11, HEIGHT - block_size * 4, block_size),
              Block(block_size * 20, HEIGHT - block_size * 7, block_size),
              Block(block_size * 21, HEIGHT - block_size * 8, block_size),
              Block(block_size * 23, HEIGHT - block_size * 11, block_size),
              Block(block_size * 28, HEIGHT - block_size * 6, block_size),
              Block(block_size * 31, HEIGHT - block_size * 8, block_size),
              Block(block_size * 30, HEIGHT - block_size * 9, block_size),
              Block(block_size * 29, HEIGHT - block_size * 10, block_size),
              Block(block_size * 32, HEIGHT - block_size * 9, block_size),
              Block(block_size * 33, HEIGHT - block_size * 10, block_size),
              Block(block_size * 30, HEIGHT - block_size * 11, block_size),
              Block(block_size * 32, HEIGHT - block_size * 11, block_size),
              Block(block_size * 31, HEIGHT - block_size * 10, block_size),
              Block(block_size * 31, HEIGHT - block_size * 5, block_size),
              Block(block_size * 36, HEIGHT - block_size * 8, block_size),
              Block(block_size * 37, HEIGHT - block_size * 7, block_size),
              Block(block_size * 38, HEIGHT - block_size * 6, block_size),
              Block(block_size * 42, HEIGHT - block_size * 6, block_size),
              Block(block_size * 46, HEIGHT - block_size * 6, block_size),
              Block(block_size * 50, HEIGHT - block_size * 6, block_size),
              Block(block_size * 54, HEIGHT - block_size * 6, block_size),
              Block(block_size * 58, HEIGHT - block_size * 3, block_size),
              Block(block_size * 34, HEIGHT - block_size * 4, block_size),


              Block(block_size * 59, HEIGHT - block_size * 3, block_size),
              Block(block_size * 59, HEIGHT - block_size * 6, block_size),
              Block(block_size * 59, HEIGHT - block_size * 7, block_size),
              Block(block_size * 59, HEIGHT - block_size * 8, block_size),
              Block(block_size * 59, HEIGHT - block_size * 9, block_size),
              Block(block_size * 59, HEIGHT - block_size * 10, block_size),
              Block(block_size * 59, HEIGHT - block_size * 11, block_size),
              Block(block_size * 59, HEIGHT - block_size * 12, block_size),
              Block(block_size * 59, HEIGHT - block_size * 13, block_size),
              Block(block_size * 59, HEIGHT - block_size * 2, block_size),
              Block(block_size * 34, HEIGHT - block_size * 4, block_size),
              Block(block_size * 59, HEIGHT - block_size * 14, block_size),

              Block(block_size * 72, HEIGHT - block_size * 4, block_size),
              Block(block_size * 72, HEIGHT - block_size * 3, block_size),
              Block(block_size * 72, HEIGHT - block_size * 5, block_size),
              Block(block_size * 72, HEIGHT - block_size * 6, block_size),
              Block(block_size * 72, HEIGHT - block_size * 7, block_size),
              Block(block_size * 72, HEIGHT - block_size * 8, block_size),
              Block(block_size * 72, HEIGHT - block_size * 9, block_size),
              Block(block_size * 72, HEIGHT - block_size * 10, block_size),
              Block(block_size * 72, HEIGHT - block_size * 11, block_size),
              Block(block_size * 72, HEIGHT - block_size * 12, block_size),

              Block(block_size * 72, HEIGHT - block_size * 2, block_size),


              Block(block_size * 61, HEIGHT - block_size * 3, block_size),
              Block(block_size * 63, HEIGHT - block_size * 5, block_size),
              Block(block_size * 65, HEIGHT - block_size * 3, block_size),
              Block(block_size * 67, HEIGHT - block_size * 5, block_size),
              Block(block_size * 69, HEIGHT - block_size * 3, block_size),
              Block(block_size * 71, HEIGHT - block_size * 6, block_size),

              Block(block_size * 69, HEIGHT - block_size * 7, block_size),
              Block(block_size * 67, HEIGHT - block_size * 8, block_size),
              Block(block_size * 65, HEIGHT - block_size * 9, block_size),
              Block(block_size * 62, HEIGHT - block_size* 8, block_size),
              Block(block_size * 60, HEIGHT - block_size * 10, block_size),



              Block(block_size * 63, HEIGHT - block_size * 12, block_size),
              Block(block_size * 64, HEIGHT - block_size * 12, block_size),
              Block(block_size * 65, HEIGHT - block_size * 12, block_size),
              Block(block_size * 66, HEIGHT - block_size * 12, block_size),
              Block(block_size * 67, HEIGHT - block_size * 12, block_size),
              Block(block_size * 68, HEIGHT - block_size * 12, block_size),
              Block(block_size * 69, HEIGHT - block_size * 12, block_size),
              Block(block_size * 70, HEIGHT - block_size * 12, block_size),
              Block(block_size * 71, HEIGHT - block_size * 12, block_size),]








    offset_x = 0
    offset_y = 0
    scroll_area_width = 500
    scroll_area_height = 500

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)

        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (
                player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0):
            offset_x += player.x_vel

        if (player.rect.bottom - offset_y >= HEIGHT - scroll_area_height and player.y_vel > 0) or (
                player.rect.top - offset_y <= scroll_area_height and player.y_vel < 0):
            offset_y += player.y_vel

        draw(window, background, bg_image, player, objects, offset_x)

    def main():
        cover_mode = True
        while cover_mode:
            draw_cover(window)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        cover_mode = False

    main()

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)


import pygame
from os import listdir
from os.path import isfile, join
import random
import sys

pygame.init()

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

BLACK=(0,0,0)
WHITE=(255,255,255)
RED = (255, 0, 0)
font = pygame.font.Font(None, 36)

window = pygame.display.set_mode((WIDTH, HEIGHT))

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Cover Screen Test")

# Set up fonts (ensure default font or proper font loading)
try:
    font = pygame.font.Font(None, 36)  # Default font with size 36
except pygame.error as e:
    print(f"Font could not be loaded: {e}")
    sys.exit()


# Draw the cover function
def draw_cover(window):
    window.fill(WHITE)  # Clear the screen with a white background

    # Create text surfaces
    cover_text = font.render("A Game That Will Make You Question Your Life Choices", True, BLACK)
    start_text = font.render("Press SPACE to Start", True, BLACK)

    # Calculate positions to center the text
    cover_text_pos = (
    window.get_width() // 2 - cover_text.get_width() // 2, window.get_height() // 2 - cover_text.get_height())
    start_text_pos = (
    window.get_width() // 2 - start_text.get_width() // 2, window.get_height() // 2 + cover_text.get_height() // 2)

    # Blit the text onto the screen
    window.blit(cover_text, cover_text_pos)
    window.blit(start_text, start_text_pos)

    # Update the display
    pygame.display.flip()


# Main game loop
def main():
    cover_mode = True
    while cover_mode:
        draw_cover(window)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    cover_mode = False


main()


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 60

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 65, 16, 32)
    fire.on()
    floor = []
    for i in range(-WIDTH // block_size, (WIDTH * 20) // block_size):

        floor.append(Block(i * block_size, HEIGHT - block_size, block_size))
    objects= [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire,
              Block(block_size * 4, HEIGHT - block_size * 4, block_size),
              Block(block_size * 5, HEIGHT - block_size * 4, block_size),
              Block(block_size * 6, HEIGHT - block_size * 4, block_size),
              Block(block_size * 7, HEIGHT - block_size * 4, block_size),
              Block(block_size * 7, HEIGHT - block_size * 3, block_size),
              Block(block_size * 7, HEIGHT - block_size * 2, block_size),
              Block(block_size * 9, HEIGHT - block_size * 6, block_size),
              Block(block_size * 11, HEIGHT - block_size * 8, block_size),
              Block(block_size * 13, HEIGHT - block_size * 6, block_size),
              Block(block_size * 16, HEIGHT - block_size * 6, block_size),
              Block(block_size * 17, HEIGHT - block_size * 6, block_size),
              Block(block_size * 18, HEIGHT - block_size * 6, block_size),
              Block(block_size * 19, HEIGHT - block_size * 6, block_size),
              Block(block_size * 11, HEIGHT - block_size * 4, block_size),
              Block(block_size * 20, HEIGHT - block_size * 7, block_size),
              Block(block_size * 21, HEIGHT - block_size * 8, block_size),
              Block(block_size * 23, HEIGHT - block_size * 11, block_size),
              Block(block_size * 28, HEIGHT - block_size * 6, block_size),
              Block(block_size * 31, HEIGHT - block_size * 8, block_size),
              Block(block_size * 30, HEIGHT - block_size * 9, block_size),
              Block(block_size * 29, HEIGHT - block_size * 10, block_size),
              Block(block_size * 32, HEIGHT - block_size * 9, block_size),
              Block(block_size * 33, HEIGHT - block_size * 10, block_size),
              Block(block_size * 30, HEIGHT - block_size * 11, block_size),
              Block(block_size * 32, HEIGHT - block_size * 11, block_size),
              Block(block_size * 31, HEIGHT - block_size * 10, block_size),
              Block(block_size * 31, HEIGHT - block_size * 5, block_size),
              Block(block_size * 36, HEIGHT - block_size * 8, block_size),
              Block(block_size * 37, HEIGHT - block_size * 7, block_size),
              Block(block_size * 38, HEIGHT - block_size * 6, block_size),
              Block(block_size * 42, HEIGHT - block_size * 6, block_size),
              Block(block_size * 46, HEIGHT - block_size * 6, block_size),
              Block(block_size * 50, HEIGHT - block_size * 6, block_size),
              Block(block_size * 54, HEIGHT - block_size * 6, block_size),
              Block(block_size * 58, HEIGHT - block_size * 3, block_size),
              Block(block_size * 34, HEIGHT - block_size * 4, block_size),


              Block(block_size * 59, HEIGHT - block_size * 3, block_size),
              Block(block_size * 59, HEIGHT - block_size * 6, block_size),
              Block(block_size * 59, HEIGHT - block_size * 7, block_size),
              Block(block_size * 59, HEIGHT - block_size * 8, block_size),
              Block(block_size * 59, HEIGHT - block_size * 9, block_size),
              Block(block_size * 59, HEIGHT - block_size * 10, block_size),
              Block(block_size * 59, HEIGHT - block_size * 11, block_size),
              Block(block_size * 59, HEIGHT - block_size * 12, block_size),
              Block(block_size * 59, HEIGHT - block_size * 13, block_size),
              Block(block_size * 59, HEIGHT - block_size * 2, block_size),
              Block(block_size * 34, HEIGHT - block_size * 4, block_size),
              Block(block_size * 59, HEIGHT - block_size * 14, block_size),

              Block(block_size * 72, HEIGHT - block_size * 4, block_size),
              Block(block_size * 72, HEIGHT - block_size * 3, block_size),
              Block(block_size * 72, HEIGHT - block_size * 5, block_size),
              Block(block_size * 72, HEIGHT - block_size * 6, block_size),
              Block(block_size * 72, HEIGHT - block_size * 7, block_size),
              Block(block_size * 72, HEIGHT - block_size * 8, block_size),
              Block(block_size * 72, HEIGHT - block_size * 9, block_size),
              Block(block_size * 72, HEIGHT - block_size * 10, block_size),
              Block(block_size * 72, HEIGHT - block_size * 11, block_size),
              Block(block_size * 72, HEIGHT - block_size * 12, block_size),

              Block(block_size * 72, HEIGHT - block_size * 2, block_size),


              Block(block_size * 61, HEIGHT - block_size * 3, block_size),
              Block(block_size * 63, HEIGHT - block_size * 5, block_size),
              Block(block_size * 65, HEIGHT - block_size * 3, block_size),
              Block(block_size * 67, HEIGHT - block_size * 5, block_size),
              Block(block_size * 69, HEIGHT - block_size * 3, block_size),
              Block(block_size * 71, HEIGHT - block_size * 6, block_size),

              Block(block_size * 69, HEIGHT - block_size * 7, block_size),
              Block(block_size * 67, HEIGHT - block_size * 8, block_size),
              Block(block_size * 65, HEIGHT - block_size * 9, block_size),
              Block(block_size * 62, HEIGHT - block_size* 8, block_size),
              Block(block_size * 60, HEIGHT - block_size * 10, block_size),



              Block(block_size * 63, HEIGHT - block_size * 12, block_size),
              Block(block_size * 64, HEIGHT - block_size * 12, block_size),
              Block(block_size * 65, HEIGHT - block_size * 12, block_size),
              Block(block_size * 66, HEIGHT - block_size * 12, block_size),
              Block(block_size * 67, HEIGHT - block_size * 12, block_size),
              Block(block_size * 68, HEIGHT - block_size * 12, block_size),
              Block(block_size * 69, HEIGHT - block_size * 12, block_size),
              Block(block_size * 70, HEIGHT - block_size * 12, block_size),
              Block(block_size * 71, HEIGHT - block_size * 12, block_size),]








    offset_x = 0
    offset_y = 0
    scroll_area_width = 500
    scroll_area_height = 500

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)

        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (
                player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0):
            offset_x += player.x_vel

        if (player.rect.bottom - offset_y >= HEIGHT - scroll_area_height and player.y_vel > 0) or (
                player.rect.top - offset_y <= scroll_area_height and player.y_vel < 0):
            offset_y += player.y_vel

        draw(window, background, bg_image, player, objects, offset_x)

    def main():
        cover_mode = True
        while cover_mode:
            draw_cover(window)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        cover_mode = False

    main()

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)


