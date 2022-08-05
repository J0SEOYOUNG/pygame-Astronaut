import pygame
from pygame.locals import *
from pygame.sprite import Sprite, Group
from pygame.math import Vector2

from itertools import cycle
from enum import Enum, auto
from random import choice, random

  

sounds = pygame.mixer
sounds.pre_init(44100, -16, 2, 512)
sounds.init()
sounds.Sound("C:/Users/psych/Desktop/final/pg/MainBgm.wav").play(-1)


# 전체 게임 상태
class GameState:

  def __init__(self):
    self.scene = MainScene() # 처음 화면 = 메인 메뉴


# 전체 게임 프로그램
class Game:

  # width, height: 창 크기, fps: FPS, caption: 창 타이틀
  def __init__(self, width, height, fps, caption):
    pygame.init()
    pygame.display.set_caption("CRASH LANDING")
    self.fps = fps
    self.screen = pygame.display.set_mode((width, height))
    self.clock = pygame.time.Clock()
    self.state = GameState()

  # 메인 루프
  def loop(self):
    while not self.isexit():
      self.state.scene.update(self.state)
      self.state.scene.draw(self.screen)
      pygame.display.flip()
      self.clock.tick(self.fps)
    pygame.quit()

  def isexit(self):
    events = pygame.event.get()
    self.state.scene.poll(events) # 이벤트 처리
    return any(e.type == QUIT for e in events)


# 기존 Sprite에 속도 가속도 기능 추가
class Entity(Sprite):

  # path: 이미지 위치, x: 초기위치, v: 초기속도, a: 초기 가속도
  def __init__(self, path, x=Vector2(0, 0), v=Vector2(0, 0), a=Vector2(0, 0)):
    super().__init__()
    self.image, self.rect = self.load(path)
    self.rect.topleft = x
    self.v = v
    self.a = a

  def update(self):
    self.v += self.a
    self.rect.move_ip(*self.v)

  # 이벤트 처리
  def poll(self, events):
    pass

  @staticmethod
  def load(path):
    image = pygame.image.load(path)
    image = image.convert_alpha()
    return image, image.get_rect()


# 게임 화면의 배경 화면
class Background(Entity):

  path = 'bb.png'

  # n: n번째 배경화면 (infinite scroll을 위한), vx: x축 방향 속도
  def __init__(self, n, vx, *args, **kwargs):
    super().__init__(self.path, v=Vector2(vx, 0), *args, **kwargs)
    self.n = n
    self.reset()

  def update(self):
    super().update()
    vx, vy = self.v
    self.dx += vx
    if abs(self.dx) >= self.rect.w:
      self.reset()

  def reset(self):
    self.rect.topleft = (self.rect.w * self.n, 0)
    self.dx = 0

  # infinite scroll을 위해 필요한 배경화면들 생성
  @staticmethod
  def infinify(*args, **kwargs):
    sw, sh = pygame.display.get_surface().get_size()
    _, rect = Entity.load(Background.path)
    numbg = sw // rect.w + 2
    return [Background(n, *args, **kwargs) for n in range(numbg)]


# 점프 상태
class JumpState(Enum):

  PENDING = auto() # 점프 준비
  JUMPING = auto() # 점프 중
  STOPPED = auto() # 점프 안하고 있음


# 플레이어
class Player(Entity):

  paths = [
    '1.png',
    '2.png',
    '3.png'
  ]

  # pos: 초기 위치, jv: 점프시 속도, ja: 점프시 가속도, slow: 이미지 반복 속도 조절
  def __init__(self, pos, jv, ja, slow, *args, **kwargs):
    super().__init__(self.paths[0], *args, **kwargs)
    self.rect.bottomleft = self.initpos = pos
    self.images = cycle(self.load(p)[0] for p in self.paths for i in range(slow))
    self.jv = jv
    self.ja = ja
    self.jump = JumpState.STOPPED

  def poll(self, events):
    super().poll(events)
    for e in events:
      if e.type == MOUSEBUTTONDOWN and self.jump == JumpState.STOPPED:
        self.jump = JumpState.PENDING

  def update(self):
    super().update()
    self.image = next(self.images)
    if self.jump == JumpState.PENDING:
      self.jstart()
    elif self.jump == JumpState.JUMPING and self.rect.bottom > self.initpos[1]:
      self.jstop()

  # 점프 시작
  def jstart(self):
    self.v = Vector2(0, self.jv)
    self.a = Vector2(0, self.ja)
    self.jump = JumpState.JUMPING

  # 점프 중단
  def jstop(self):
    self.v = Vector2(0, 0)
    self.a = Vector2(0, 0)
    self.rect.bottomleft = self.initpos
    self.jump = JumpState.STOPPED


# 오브젝트: 장애물과 아이템의 공통요소
class Object(Entity):

  # gnd: 바닥 위치, vx: x축 방향 속도
  def __init__(self, path, gnd, vx, *args, **kwargs):
    super().__init__(path, v=Vector2(vx, 0), *args, **kwargs)
    sw, _ = pygame.display.get_surface().get_size()
    self.rect.bottomleft = (sw, gnd)

  def update(self):
    super().update()
    srect = pygame.display.get_surface().get_rect()
    # 화면 밖으로 나가면 없앰
    if not srect.colliderect(self.rect):
      self.kill()


# 장애물
class Obstacle(Object):

  paths = [
    'Obstacle 1.png',
    'Obstacle 2.png',
    'Obstacle 3.png',
    'Obstacle 4.png'
  ]

  def __init__(self, *args, **kwargs):
    super().__init__(choice(self.paths), *args, **kwargs)


# 아이템 타입
class ItemType(Enum):

  HAMMER = auto()
  SPANNER = auto()
  GAS = auto()


# 아이템
class Item(Object):

  paths = {
    ItemType.HAMMER: '망치.png',
    ItemType.SPANNER: '스패너.png',
    ItemType.GAS: '연료통.png'
  }

  # itemtype: 아이템 타입, maxh: 아이템 최대 높이
  def __init__(self, itemtype, maxh, *args, **kwargs):
    super().__init__(self.paths[itemtype], *args, **kwargs)
    self.rect.bottom -= choice(range(maxh)) # 아이템 높이 범위 내에서 랜덤
    self.type = itemtype


# 화면
class Scene:

  def __init__(self, *sprites):
    self.group = Group(*sprites)

  # 각 sprite마다 이벤트 처리
  def poll(self, events):
    for sprite in self.group:
      if isinstance(sprite, Entity):
        sprite.poll(events)

  def draw(self, screen):
    self.group.draw(screen)

  def update(self, state):
    self.group.update()


# 게임 화면
class GameScene(Scene):

  def __init__(self):
    self.ground = 415 # 바닥 위치
    self.bgspeed = -5 # 배경 이동 속도
    self.bgs = Background.infinify(self.bgspeed)
    self.player = Player((250, self.ground + 14), -20, 1, 10)
    self.ointv = cycle(range(50)) # 장애물 간격
    self.oprob = 0.5 # 장애물 등장 확률
    self.iprob = 0.007 # 아이템 등장 확률
    self.imaxh = 100 # 아이템이 나타날 수 있는 높이 한계
    self.hitrd = (-50, -50) # 판정: hitbox를 얼마나 줄일 것인가
    self.collected = {itype: False for itype in ItemType} # 아이템 수집 현황
    super().__init__(*self.bgs, self.player)

  def update(self, state):
    super().update(state)
    self.update_obstacles(state)
    self.update_items(state)

  def update_obstacles(self, state):
    # 장애물 생성
    if next(self.ointv) == 0 and random() < self.oprob:
      self.group.add(Obstacle(self.ground, self.bgspeed))
    # 장애물 충돌 감지
    obstacles = [s.rect for s in self.group if isinstance(s, Obstacle)]
    if self.hitbox().collidelist(obstacles) != -1:
      state.scene = EndScene()

  def update_items(self, state):
    # 아이템 생성
    if random() < self.iprob:
      self.group.add(Item(choice(list(ItemType)), self.imaxh, self.ground, self.bgspeed))
    # 아이템 충돌 감지
    items = [s for s in self.group if isinstance(s, Item)]
    idx = self.hitbox().collidelist([i.rect for i in items])
    if idx != -1:
      item = items[idx]
      self.collected[item.type] = True
      item.kill()
    # 모두 모았으면 clear
    if all(v for v in self.collected.values()):
      state.scene = EndScene(clear=True)

  def hitbox(self):
    return self.player.rect.inflate(*self.hitrd)


# 메인 메뉴 화면
class MainScene(Scene):

  bgpath = 'Menu1.png'
  btnpath = 'Menu3.png'

  def __init__(self):
    self.bg = Entity(self.bgpath)
    self.button = Entity(self.btnpath, x=Vector2(10, 140))
    self.clicked = False
    super().__init__(self.bg, self.button)

  def poll(self, events):
    super().poll(events)
    for e in events:
      if e.type == MOUSEBUTTONDOWN:
        self.clicked = True

  def update(self, state):
    super().update(state)
    if self.clicked:
      state.scene = GameScene()


# 게임 종료 화면
class EndScene(Scene):

  overpath = 'over.png'
  clrpath = 'clear.png'

  def __init__(self, clear=False):
    self.bg = Entity(self.clrpath if clear else self.overpath)
    self.clicked = False
    super().__init__(self.bg)

  def poll(self, events):
    super().poll(events)
    for e in events:
      if e.type == MOUSEBUTTONDOWN:
        self.clicked = True

  def update(self, state):
    super().update(state)
    if self.clicked:
      state.scene = MainScene()


if __name__ == '__main__':
  game = Game(900, 500, 60, 'Crash Landing')
  game.loop()
