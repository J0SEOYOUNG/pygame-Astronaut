import pygame, time, timeit, threading, copy, os

FPS = 70
BGA_FPS = 27.98
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 500
S_HEIGHT = WINDOW_HEIGHT - 50

SHOWN_TIME = 1500
WHITE = [255, 255, 255]

#Game Init
sounds = pygame.mixer
sounds.pre_init(44100, -16, 2, 512)
sounds.init()

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Intro")

#LoadBGA
bga_files = []
for file in os.listdir("opening"):
    bga_files.append(file)

def getRuntime():
    end = timeit.default_timer()
    runtime = int((end - start) * 1000)
    return runtime

bgmImage = 0
prevNum = 0

def draw():
    global bgmImage, prevNum

    try:
        #Clear Sreen
        screen.fill((0, 0, 0))

        bgaNum = int((getRuntime() / 1000) * BGA_FPS)
        if ("오프닝 30프레임" + str(bgaNum).zfill(4) + ".jpg") in bga_files:
            if prevNum == bgaNum:
                screen.blit(bgmImage, bgmImage.get_rect())
            else:
                bgmImage = pygame.image.load("opening\\" + "오프닝 30프레임" + str(bgaNum).zfill(4) + ".jpg")
                bgmImage = pygame.transform.scale(bgmImage, (WINDOW_WIDTH, WINDOW_HEIGHT))
                screen.blit(bgmImage, bgmImage.get_rect())
                prevNum = bgaNum
        pygame.display.flip()
    except:
        pass


running = True
sounds.Sound("C:/Users/psych/Desktop/Intro/OpeningBgm.wav").play()
clock = pygame.time.Clock()
start = timeit.default_timer()

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            quit()

    draw()
exit()
