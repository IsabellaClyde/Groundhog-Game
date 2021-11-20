import random
import pygame
from pygame.locals import *
from pygame_functions import *
import noise

# Colour palette
black = (0, 0, 0)
white = (244, 244, 244)
baby_blue = (24, 237, 255)  # Not actually baby blue
grey = (179, 179, 179)

# Window Setup
boarder = 400
clock = pygame.time.Clock()
check_timer = clock.get_time()
pygame.init()  # initiates pygame
pygame.display.set_caption("Title Undecided")  # Adds title to window
window_size = (1200, 800)

# Define variables to be used for background later
game_map = {}
true_scroll = [0, (-1000)]
true_true_scroll = [0, 0]
screen = pygame.display.set_mode(window_size, 0, 32)
tile_size = 60
tile_detail = 60

# Background images defined
grass = pygame.image.load("Grass.png")
grass = pygame.transform.scale(grass, (tile_size, tile_size))
dirt = pygame.image.load("Dirt.png")
dirt = pygame.transform.scale(dirt, (tile_size, tile_size))
plant = pygame.image.load("plant.png").convert()
plant = pygame.transform.scale(plant, (tile_size, tile_size))
plant.set_colorkey(black)
tile_index = {1: grass, 2: dirt, 3: plant}
chunk_size = 8


# Use to render text
def text_objects(text, font):
    text_surface = font.render(text, True, white)
    return text_surface, text_surface.get_rect()


# The game intro
def game_intro():
    intro = True
    health_bar.death = False  # Character isn't dead

    while intro:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Exits game if "x" is pressed
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:  # Game starts if space key is pressed
                if event.key == K_SPACE:
                    intro = False
        screen.fill(baby_blue)  # Makes background blue

        # Renders text
        title = pygame.font.Font("freesansbold.ttf", 115)
        text_surf, text_rect = text_objects("GROUNDHOG", title)
        text_rect.center = ((window_size[0] / 2), (window_size[1] / 2))
        screen.blit(text_surf, text_rect)

        pygame.display.update()
        clock.tick(30)


def get_em_chunks(x, y):  # Renders background in "chunks" similar to minecraft but each "chunk" contains multiple
    # blocks which helps prevent lagging
    chunk_data = []

    # Goes through all the blocks in the chunks and makes a map of wear the blocks will be
    for y_pos in range(chunk_size):
        for x_pos in range(chunk_size):
            target_x = x * chunk_size + x_pos
            target_y = y * chunk_size + y_pos
            tile_type = 0  # nothing
            height = int(noise.pnoise1(target_x * 0.1, repeat=9999999) * 5)
            if target_y > 8 - height:
                tile_type = 2  # dirt
            elif target_y == 8 - height:
                tile_type = 1  # grass
            elif target_y == 8 - height - 1:
                if random.randint(1, 5) == 1:
                    tile_type = 3  # plant
            if tile_type != 0:
                chunk_data.append([[target_x, target_y], tile_type])  # Makes map
    return chunk_data


#  Health bar for character
class Health:

    def __init__(self):
        health_bar_image = pygame.image.load("health_bar.jpeg")
        white1 = (255, 255, 255)
        health_bar_image.set_colorkey(white1)
        self.size_percent = 3
        self.size = (int(150 * self.size_percent), int((30 * self.size_percent) / 1.5))
        health_bar_image = pygame.transform.scale(health_bar_image, self.size)
        self.image = health_bar_image
        self.width = int(860 * self.size_percent)
        self.rect = self.image.get_rect(size=self.size)
        self.rect.y = window_size[1] - 90
        self.rect.x = int((window_size[0] / 2) - (self.size[0] / 2))
        self.health = self.size[0] - 100
        self.death = False

    def update(self, pain):  # Updates health bar on screen
        if pain[0] <= 0:  # If character has no health
            self.death = True
            death()
            game_intro()
        screen.blit(self.image, (self.rect.x, self.rect.y))
        hurt = self.health - pain[0]
        pygame.draw.rect(screen, white, pygame.Rect(pain[1] + 89, self.rect.y + 15, hurt, self.size[1] - 28))


# Enemy character
class Slime(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        slime_image = pygame.image.load("Slime_Idle/1slimestill.png").convert()
        slime_image.set_colorkey(black)
        size_percent = 4
        self.image = slime_image
        self.size = (int(40 * size_percent), int(36 * size_percent))
        self.width = int(40 * size_percent)
        self.height = int(36 * size_percent)
        self.rect = self.image.get_rect(size=(self.width, self.height))
        self.rect.x = random.randint(50, 100)
        self.rect.y = 50
        self.health = 100
        self.death = False

    def update(self):  # Updates slime on the screen
        if not self.death:
            screen.blit(self.image, (self.rect.x, self.rect.y))
            clock.tick(30)

    def bounce(self, x):  # Makes slime bounce
        set_bounce = str("Slime_Idle/" + str(x) + "slimestill.png")
        self.image = pygame.image.load(set_bounce).convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image.set_colorkey(black)

    def attack(self, x):  # Animation for slime attacking
        set_attack = str("slime_attack/" + str(x) + "slimeattack.png")
        self.image = pygame.image.load(set_attack).convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image.set_colorkey(black)

    def hurt(self, x):  # Animation for slime hurt
        set_hurt = str("slime_hurt/" + str(x) + "slimehurt.png")
        self.image = pygame.image.load(set_hurt).convert()
        self.image = pygame.transform.scale(self.image, self.size)
        self.image.set_colorkey(black)

    def die(self, x):  # When slime dies
        set_death = str("slime_hurt/" + str(x) + "slimehurt.png")
        self.image = pygame.image.load(set_death).convert()
        self.image = pygame.transform.scale(self.image, self.size)
        self.image.set_colorkey(black)


# Main character
class Character(pygame.sprite.Sprite):

    def __init__(self):
        character_image = pygame.image.load("pink_monster.png").convert()
        character_image.set_colorkey(black)
        size_percent = 4  # Percent size of character from original image
        super().__init__()
        self.image = character_image
        self.size = (int(17 * size_percent), int(28 * size_percent))
        self.width = int(17 * size_percent)
        self.height = int(28 * size_percent)
        self.rect = self.image.get_rect(size=(self.width, self.height))
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image_right = self.image
        self.image_left = pygame.transform.flip(self.image, True, False)
        self.rect.x = 100
        self.imagine_x = 100
        self.rect.y = 500
        self.is_jumping = False
        self.points = 0
        self.facing = "left"

    def update(self):  # Renders character on the screen
        screen.blit(self.image, (self.rect.x, self.rect.y))
        if self.facing == "left":
            self.image = self.image_left
        else:
            self.image = self.image_right
        clock.tick(30)

    def walking(self, x):
        set_walk = str("Walk/" + str(x) + "walk.png")
        self.image = pygame.image.load(set_walk).convert()
        if self.facing == "left":
            self.image = pygame.transform.flip(self.image, True, False)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image.set_colorkey(black)
        self.facing = "right"

    # To jump up
    def jumping_up(self, x):
        self.is_jumping = True
        set_jump = str("jump/" + str(x) + "jump.png")
        self.image = pygame.image.load(set_jump).convert()
        if self.facing == "left":
            self.image = pygame.transform.flip(self.image, True, False)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image.set_colorkey(black)

    # To jump down
    def jumping_down(self, x):
        self.is_jumping = True
        set_jump = str("jump/" + str(x) + "jump.png")
        self.image = pygame.image.load(set_jump).convert()
        if self.facing == "left":
            self.image = pygame.transform.flip(self.image, True, False)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image.set_colorkey(black)

    # If being attacked animation
    def hurt(self, x):
        set_hurt = str("main_hurt/" + str(x) + "pinkhurt.png")
        self.image = pygame.image.load(set_hurt).convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image = pygame.transform.flip(self.image, True, False)
        self.image.set_colorkey(black)

    # If attacking animation
    def attack(self, x):
        set_attack = str("main_attack/" + str(x) + "pinkattack.png")
        self.image = pygame.image.load(set_attack).convert()
        if self.facing == "left":
            self.image = pygame.transform.flip(self.image, True, False)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image.set_colorkey(black)


# Defines classes variables and makes sprites
shape_group = pygame.sprite.Group()
main_character = Character()
shape_group.add(main_character)
main_character.image = pygame.transform.scale(main_character.image, main_character.size)
slime_character = Slime()
shape_group.add(slime_character)
health_bar = Health()


# If character dies
def death():
    dead = True

    while dead:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Game ends if player presses "x"
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:  # If player presses space game restarts
                if event.key == K_SPACE:
                    dead = False

        # Renders text
        title = pygame.font.Font("freesansbold.ttf", 115)
        text_surf, text_rect = text_objects("YOU DIED", title)
        score_text, score_rect = text_objects(("Score: " + str(main_character.points)), title)
        text_rect.center = ((window_size[0] / 2), (window_size[1] / 2) - 75)
        score_rect.center = ((window_size[0] / 2), (window_size[1] / 2) + 75)
        screen.blit(text_surf, text_rect)
        screen.blit(score_text, score_rect)

        # Respawns character
        main_character.rect.x = 300
        main_character.rect.y = 100
        slime_character.health = 100
        pain[0] = int(225 * health_bar.size_percent) - 100
        pain[1] = health_bar.rect.x + 350

        pygame.display.update()
        clock.tick(60)


# Checks for collisions to see if character is touching blocks
def check_collisions(character):

    # Goes through and finds what coordinates are touching what side
    collisions = []
    touched = [coordinate for coordinate in tile_rects if character.rect.colliderect(coordinate)]
    bottom = [coordinate for coordinate in touched if coordinate[1] < character.rect.y + character.height]
    right = [coordinate for coordinate in touched if
             coordinate[0] - x_scroll[0] < character.rect.x + character.width and coordinate[1] - scroll[
                 1] < character.rect.y + character.height - 100]
    left = [coordinate for coordinate in touched if
            coordinate[0] - x_scroll[0] - tile_rects[0][2] > character.rect.x and coordinate[1] - scroll[
                1] < character.rect.y + character.height - 100]

    # Changes location of bottom to make it more accurate
    try:
        collisions.append(bottom[0][1] - character.height)
    except IndexError:
        pass

    # Returns information
    if len(bottom) > 0:
        collisions.append("bottom")
    if len(right) > 0:
        collisions.append("right")
    if len(left) > 0:
        collisions.append("left")
    return collisions

# Checks for collisions between two characters
def check_character_collision(character1, character2):

    types = []

    # Finds if they are touching from left of rifht
    if character2.rect.x + 5 >= character1.rect.x + character1.width >= character2.rect.x - 5 and (
            character2.rect.y <= character1.rect.y <= character2.rect.y + character1.height or character2.rect.y <=
            character1.rect.y <= character2.rect.y + character2.height):
        types.append("1right to 2left")
    if character2.rect.x + character2.width + 5 >= character1.rect.x >= character2.rect.x - 5 and (
            character2.rect.y <= character1.rect.y <= character2.rect.y + character1.height or character2.rect.y <=
            character1.rect.y <= character2.rect.y + character2.height):
        types.append("2right to 1left")

    # Returns information
    return types


# Updates background with everything in order
def update_background():
    screen.fill(baby_blue)
    shape_group.update()
    draw_em_chunks()
    health_bar.update(pain)
    pygame.display.update()
    clock.tick(120)


# Makes the character jump
def jump():

    main_character.is_jumping = True
    count = 1
    x = 80

    # Jump up
    for moment in range(4):
        main_character.jumping_up(count)
        main_character.rect.y -= x
        check_action(six)
        update_background()
        slime_character.rect.y += 10
        x -= 10
        count += 1
    x = 0

    # Jump down
    for moment in range(4):
        main_character.jumping_down(count)
        count += 1
        if "bottom" not in check_collisions(main_character):
            main_character.rect.y += x
            check_action(six)
            update_background()
            x += 30

    if "bottom" not in check_collisions(main_character):  # If character hasn't touched the ground yet move it down
        main_character.rect.y += 20
    clock.tick()
    if "bottom" in check_collisions(main_character):  # If character has touched the ground it's no longer jumping
        main_character.is_jumping = False


# Checks for all actions
def check_action(six):

    actions = []
    for event in pygame.event.get():  # loops through events and if event = quit (if the "x" is pressed) the game ends
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == K_UP and not main_character.is_jumping:  # If up and character isn't jumping
                actions.append("is_jumping")
                jump()  # Character jumps

    keys = pygame.key.get_pressed()  # Checks when key is let go and continues action until it is

    # If right and nothing's in the way
    if keys[K_RIGHT] and "right" not in check_collisions(main_character) and "1right to 2left" not in \
            check_character_collision(main_character, slime_character) and not slime_character.death:

        actions.append("right walk")
        main_character.facing = "right"

        # If within boarder move
        if main_character.rect.x < window_size[0] - boarder:
            main_character.rect.x += 5
            main_character.imagine_x += 5

        # If not within boarder just move perspective
        else:
            main_character.imagine_x += 8
            if not slime_character.death:
                slime_character.rect.x -= 4

        # If character is jumping and at edge just move perspective
        if main_character.is_jumping and main_character.rect.x < boarder - main_character.width:
            main_character.imagine_x += 5

    # If right and slime is dead
    elif keys[K_RIGHT] and "right" not in check_collisions(main_character) and slime_character.death:

        actions.append("right walk")
        main_character.facing = "right"

        # If within boarder
        if main_character.rect.x < window_size[0] - boarder:
            main_character.rect.x += 5
            main_character.imagine_x += 5

        # If not within boarder jump move perspective
        else:
            main_character.imagine_x += 8

    # If left and no collisions
    elif keys[K_LEFT] and "left" not in check_collisions(main_character) and "2right to 1left" not in \
            check_character_collision(main_character, slime_character) and not slime_character.death:

        actions.append("left walk")
        main_character.facing = "left"

        # If character within boarder
        if main_character.rect.x > boarder - main_character.width:
            main_character.rect.x -= 5
            main_character.imagine_x -= 5

        # If character at edge just move perspective
        else:
            main_character.imagine_x -= 8
            if not slime_character.death:
                slime_character.rect.x += 4

        # If character jumping at edge just move perspective
        if main_character.is_jumping and main_character.rect.x < boarder - main_character.width:
            main_character.imagine_x -= 5

    # If left and slime dead
    elif keys[K_LEFT] and "left" not in check_collisions(main_character) and slime_character.death:

        actions.append("left walk")
        main_character.facing = "left"

        # If character within boarder
        if main_character.rect.x > boarder - main_character.width:
            main_character.rect.x -= 5
            main_character.imagine_x -= 5

        # If not just move perspective
        else:
            main_character.imagine_x -= 8
            if not slime_character.death:
                slime_character.rect.x += 4

    # Attack if player presses space
    elif keys[K_SPACE]:
        if six > 6:
            six = 1
        main_character.attack(six)
        actions.append("attack")

    return actions


game_intro()

game_exit = False
while True:


    # Animation variables
    y = 1
    x = 1
    z = 1
    q = 1
    six = 1
    four = 1

    # Defines direction and health bar health
    direction = random.randint(1, 2)
    x_value = health_bar.rect.x + 350
    pain = [health_bar.health, x_value]


    # Renders blocks
    def draw_em_chunks():

        # Refreshes perspective
        true_true_scroll[0] = (main_character.rect.x - true_true_scroll[0] - 152) / 20
        true_scroll[0] += (main_character.imagine_x - true_scroll[0] - 152) / 20
        true_scroll[1] += (main_character.rect.y - true_scroll[1] - 600) / 20
        scroll = true_scroll.copy()
        x_scroll = true_true_scroll.copy()
        x_scroll[0] = int(x_scroll[0])
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        tile_rects = []
        for y in range(4):
            for x in range(4):

                # Makes block map
                target_x = x - 1 + int(round(scroll[0] / (chunk_size * tile_detail)))
                target_y = y - 1 + int(round(scroll[1] / (chunk_size * tile_detail)))
                target_chunk = str(target_x) + ';' + str(target_y)
                if target_chunk not in game_map:
                    game_map[target_chunk] = get_em_chunks(target_x, target_y)

                # Renders them
                for tile in game_map[target_chunk]:
                    screen.blit(tile_index[tile[1]],
                                (tile[0][0] * tile_detail - scroll[0], tile[0][1] * tile_detail - scroll[1]))

                    # Makes list of locations
                    if tile[1] in [1, 2]:
                        tile_rects.append(
                            pygame.Rect(tile[0][0] * tile_detail - scroll[0], tile[0][1] * tile_detail - scroll[1],
                                        tile_detail, tile_detail))
        return tile_rects


    update_background()

    # While character is alive
    while not health_bar.death:

        # If character is alive slowly regain health
        if health_bar.health > 0:
            pain[0] += 0.5
            pain[1] += 0.5

        # Refreshes sperspective scroll
        true_true_scroll[0] = (main_character.rect.x - true_true_scroll[0] - 152) / 20
        true_scroll[0] += (main_character.imagine_x - true_scroll[0] - 152) / 20
        true_scroll[1] += (main_character.rect.y - true_scroll[1] - 600) / 20
        scroll = true_scroll.copy()
        x_scroll = true_true_scroll.copy()
        x_scroll[0] = int(x_scroll[0])
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        # Checks list from actions and does appropriate animation
        if "right walk" in check_action(six) and "is_jumping" not in check_action(
                six) and not main_character.is_jumping:
            if x == 7:
                x = 1
            main_character.facing = "right"
            main_character.walking(x)
            x += 1
        elif "left walk" in check_action(six) and "is_jumping" not in check_action(
                six) and not main_character.is_jumping:
            if x == 7:
                x = 1
            main_character.facing = "left"
            main_character.walking(x)
            x += 1
        elif "attack" in check_action(six):
            six += 1
        if "attack" in check_action(six) and len(check_character_collision(main_character, slime_character)) != 0:
            if four > 4:
                four = 1
            slime_character.hurt(four)
            update_background()
            slime_character.health -= 5

            # If slime has no more health it dies
            if slime_character.health <= 0:
                slime_character.death = True

                # Refreshes slime and sets a timer
                slime_character.health = 100
                the_timer = random.randint(50, 100)
            four += 1

        # If slime is dead
        if slime_character.death:
            the_timer -= 1
            if the_timer < 0:  # If the timers done respawn slime
                slime_character.rect.y = 100
                slime_character.rect.x = random.randint(1000, 1500)
                slime_character.death = False

        tile_rects = draw_em_chunks()
        check_collisions(main_character)  # Checks to make sure character isn't walking through blocks

        # Looks for what collisions between character and block are occuring and does appropriate actions
        if "bottom" not in check_collisions(main_character):  # Gravity
            main_character.rect.y += 25

        if "bottom" in check_collisions(main_character):  # If touching blocks move just above blocks
            main_character.is_jumping = False
            main_character.rect.y = int(check_collisions(main_character)[0] + 20)

        if "bottom" not in check_collisions(slime_character) and not slime_character.death:  # Slime gravity
            slime_character.rect.y += 15

        if "bottom" in check_collisions(slime_character) and not slime_character.death:  # If slime touching blocks
            # move just above
            slime_character.rect.y = int(check_collisions(slime_character)[0] + 10)


        # Slime bounching and random movement rendering
        if not slime_character.death:
            stride = random.randint(20, 75)
            if stride == 20:
                direction = direction * (-1)
            if stride != 20:
                # If no collisions
                if direction > 0 and "2right to 1left" not in check_character_collision(main_character, slime_character)\
                        or direction < 0 and "1right to 2left" not in check_character_collision(
                        main_character, slime_character):
                    slime_character.rect.x += 5 * direction

        # If slime is too far away respawns slime in front
        if abs(slime_character.rect.x - main_character.rect.x) > random.randint(1000, 5000):
            if slime_character.rect.x - main_character.rect.x > 0:
                slime_character.rect.x = random.randint(300, 1500) * (-1)
            else:
                slime_character.rect.x = random.randint(1800, 3000)
        if six > 6:
            six = 1
        check_action(six)

        if y > 9:
            y = 1

        # Slime bounce animation
        if not slime_character.death:
            slime_character.bounce(y)

        # Slime attack animation
        if len(check_character_collision(main_character, slime_character)) > 0 and not slime_character.death:
            if z > 2:
                z = 1
            if q > 4:
                q = 1
            slime_character.rect.y -= 10
            slime_character.attack(z)
            main_character.hurt(q)
            pain[0] -= 5
            pain[1] -= 5
            z += 1
            q += 1

        y += 1

        main_character.points += 1  # length alive
        update_background()  # updates screen
        clock.tick(60)  # Makes the game only run at 60 fps
