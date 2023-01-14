import pygame
import os
import random

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
FLOOR_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))

pygame.font.init()
SCORE_FONT = pygame.font.SysFont('arial', 50)


class Bird:
    BIRD_IMGS = [
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
    ]
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.bird_img_counter = 0
        self.bird_img = self.BIRD_IMGS[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        shift = 1.5 * (self.time**2) + self.speed * self.time

        if shift > 16:
            shift = 16
        elif shift < 0:
            shift -= 2

        self.y += shift

        if shift < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPEED

    def draw(self, surface):
        self.bird_img_counter += 1

        if self.bird_img_counter < self.ANIMATION_TIME:
            self.bird_img = self.BIRD_IMGS[0]
        elif self.bird_img_counter < self.ANIMATION_TIME*2:
            self.bird_img = self.BIRD_IMGS[1]
        elif self.bird_img_counter < self.ANIMATION_TIME*3:
            self.bird_img = self.BIRD_IMGS[2]
        elif self.bird_img_counter < self.ANIMATION_TIME*4:
            self.bird_img = self.BIRD_IMGS[1]
        elif self.bird_img_counter >= self.ANIMATION_TIME*4 + 1:
            self.bird_img = self.BIRD_IMGS[0]
            self.bird_img_counter = 0

        if self.angle <= -80:
            self.bird_img = self.BIRD_IMGS[1]
            self.bird_img_counter = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.bird_img, self.angle)
        img_center = self.bird_img.get_rect(topleft=(self.x, self.y)).center
        rect = rotated_image.get_rect(center=img_center)
        surface.blit(rotated_image, rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.bird_img)


class Pipe:
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.UP_PIPE = pygame.transform.flip(PIPE_IMG, False, True)
        self.DOWN_PIPE = PIPE_IMG
        self.passed = False
        self.setting_height()

    def setting_height(self):
        self.height = random.randrange(50, 450)
        self.pos_topo = self.height - self.UP_PIPE.get_height()
        self.pos_base = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def draw(self, surface):
        surface.blit(self.UP_PIPE, (self.x, self.pos_topo))
        surface.blit(self.DOWN_PIPE, (self.x, self.pos_base))

    def crash(self, bird):
        bird_mask = bird.get_mask()
        up_mask = pygame.mask.from_surface(self.UP_PIPE)
        down_mask = pygame.mask.from_surface(self.DOWN_PIPE)

        up_distance = (self.x - bird.x, self.pos_topo - round(bird.y))
        down_distance = (self.x - bird.x, self.pos_base - round(bird.y))

        topo_ponto = bird_mask.overlap(up_mask, up_distance)
        base_ponto = bird_mask.overlap(down_mask, down_distance)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Floor:
    SPEED = 5
    WIDTH = FLOOR_IMG.get_width()
    IMAGE = FLOOR_IMG

    def __init__(self, y):
        self.y = y
        self.x_1 = 0
        self.x_2 = self.WIDTH

    def move(self):
        self.x_1 -= self.SPEED
        self.x_2 -= self.SPEED

        if self.x_1 + self.WIDTH < 0:
            self.x_1 = self.x_2 + self.WIDTH
        if self.x_2 + self.WIDTH < 0:
            self.x_2 = self.x_1 + self.WIDTH

    def draw(self, surface):
        surface.blit(self.IMAGE, (self.x_1, self.y))
        surface.blit(self.IMAGE, (self.x_2, self.y))


def draw_screen(surface, birds, pipes, floor, pontos):
    surface.blit(BACKGROUND_IMG, (0, 0))
    for bird in birds:
        bird.draw(surface)
    for pipe in pipes:
        pipe.draw(surface)

    text = SCORE_FONT.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    surface.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
    floor.draw(surface)
    pygame.display.update()


def main():
    birds = [Bird(100, 350)]
    floor = Floor(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    score = 0
    clock = pygame.time.Clock()

    while True:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()

        for bird in birds:
            bird.move()
        floor.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.crash(bird):
                    birds.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.UP_PIPE.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.bird_img.get_height()) > floor.y or bird.y < 0:
                birds.pop(i)

        draw_screen(screen, birds, pipes, floor, score)


if __name__ == '__main__':
    main()


