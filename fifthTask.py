import os
import sys

import pygame
import requests

pygame.init()

COLOR_INACTIVE = (50, 50, 50)
COLOR_ACTIVE = (255, 204, 0)
FONT = pygame.font.Font(None, 32)


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.min_w = w
        self.rect = pygame.Rect(x, y, w, h)
        self.rect2 = pygame.Rect(x + 2, y + 2, w - 2, h - 3)
        self.searchImg = pygame.image.load('data/searchButton.png')
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def txt(self):
        txt = self.text
        self.text = ''
        return txt

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode if (
                                                          event.unicode != '\r' and event.unicode != '\x1b') and len(
                        self.text) + 1 <= 35 else ''
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        width = max(self.min_w, self.txt_surface.get_width() + 10)
        self.rect.w = width
        self.rect2.w = width - 2

    def draw(self, screen):
        self.update()
        pygame.draw.rect(screen, (150, 150, 150), self.rect2)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 10))
        screen.blit(self.searchImg, (self.rect.x + self.rect.w + 5, self.rect.y - 4))

    def hover_on_search(self, m_pos):
        if self.searchImg.get_rect(x=self.rect.x + self.rect.w + 5, y=self.rect.y).collidepoint(
                m_pos):
            return True


def get_pic(coords='39 52', spn='0.005 0.005', l='map', pt=''):
    picserver = 'https://static-maps.yandex.ru/1.x/'
    picparams = {
        'l': l,
        'll': ','.join(coords.split()),
        'spn': ','.join(spn.split()),
    }
    if pt != '':
        picparams['pt'] = pt
    response = requests.get(picserver, params=picparams).content
    return response


def draw_buttons():
    for i in range(3):
        if Buttons[i]:
            screen.blit(clickedButton, (500 + 25 * i, 20))
        else:
            screen.blit(normalButton, (500 + 25 * i, 20))


map_file = "map.png"

try:
    with open(map_file, "wb") as file:
        file.write(get_pic())
except IOError as ex:
    print("Ошибка записи временного файла:", ex)
    sys.exit(2)

spm = ['0.001 0.001', '0.003 0.003', '0.005 0.005', '0.01 0.01', '0.05 0.05', '0.1 0.1',
       '0.25 0.25', '0.5 0.5', '1 1', '2 2',
       '5 5', '10 10', '20 20', '30 30', '50 50']
k = 0
screen = pygame.display.set_mode((600, 450))
pygame.display.flip()
FPS = 40
running = True
clock = pygame.time.Clock()
img = pygame.image.load(map_file)
first_c, sec_c = 39, 52
find = InputBox(10, 400, 300, 40)

Buttons = [True, False, False]
normalButton = pygame.transform.scale(pygame.image.load('data/normalButton.png'), (25, 25))
clickedButton = pygame.transform.scale(pygame.image.load('data/clickedButton.png'), (25, 25))

l = ['map', 'sat', 'sat,skl']
eventy_pos = []
pt = ''
while running:
    try:
        with open(map_file, "wb") as file:
            try:
                file.write(get_pic(spn=spm[k], l=l[Buttons.index(True)],
                                   coords=' '.join([str(i) for i in [first_c, sec_c]]), pt=pt))
            except ValueError:
                file.write(get_pic(spn=spm[k],
                                   coords=' '.join([str(i) for i in [first_c, sec_c]])))
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    screen.blit(pygame.image.load(map_file), (0, 0))

    for event in pygame.event.get():
        find.handle_event(event)
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            pt = ''
            if event.key == 281:
                if k < len(spm) - 1:
                    k += 1
            elif event.key == 280:
                if k > 0:
                    k -= 1
            elif event.key == pygame.K_UP:
                sec_c += (float(spm[k].split()[1]))
            elif event.key == pygame.K_DOWN:
                sec_c -= (float(spm[k].split()[1]))
            elif event.key == pygame.K_RIGHT:
                first_c += (float(spm[k].split()[0]))
            elif event.key == pygame.K_LEFT:
                first_c -= (float(spm[k].split()[0]))
            if first_c >= 180:
                first_c -= 359
            elif first_c <= - 180:
                first_c += 359
            if sec_c >= 86:
                sec_c -= 171
            elif sec_c <= -86:
                sec_c += 171

        if event.type == pygame.MOUSEBUTTONDOWN:
            if clickedButton.get_rect(x=500, y=20).collidepoint(event.pos):
                Buttons = [True, False, False]
            elif clickedButton.get_rect(x=525, y=20).collidepoint(event.pos):
                Buttons = [False, True, False]
            elif clickedButton.get_rect(x=550, y=20).collidepoint(event.pos):
                Buttons = [False, False, True]
            elif find.hover_on_search(event.pos):
                server = 'https://geocode-maps.yandex.ru/1.x'
                params = {
                    'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                    'geocode': find.text,
                    'format': 'json'
                }
                response = requests.get(server, params=params)

                if response:
                    first_c, sec_c = response.json()["response"]["GeoObjectCollectio"
                                                                 "n"]["featureMember"][0][
                        "GeoObject"][
                        'Point']['po'
                                 's'].split()
                    first_c, sec_c = float(first_c), float(sec_c)
                    pt = ','.join([str(i) for i in [first_c, sec_c]])
                else:
                    find.text = ''

        if event.type == pygame.MOUSEMOTION:
            eventy_pos = list(event.pos)
    if find.hover_on_search(eventy_pos):
        pygame.draw.rect(screen, (200, 200, 200),
                         find.searchImg.get_rect(x=find.rect.x + find.rect.w + 5,
                                                 y=find.rect.y - 7))

    find.draw(screen)
    draw_buttons()
    find.update()
    pygame.display.flip()
    clock.tick(FPS)

os.remove(map_file)
pygame.quit()
