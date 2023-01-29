import pygame as pg
import numpy as np
from PIL import ImageColor
import sqlite3
from field import Field


pg.init()
con = sqlite3.connect('color_schemes.db')
cur = con.cursor()


def make_images():  # создаёт и сохраняет изображение каждой цветовой гаммы из базы данных,
    query = """SELECT levels.id, levels.left_top, levels.right_top, levels.left_bottom,
    levels.right_bottom, levels.size, levels.cell_size, templates.type, difficulties.difficulty
    FROM levels INNER JOIN templates ON templates.id = levels.template
    INNER JOIN difficulties ON difficulties.id = levels.difficulty
    """
    result = cur.execute(query).fetchall()  # создаёт и сохраняет изображение каждой цветовой гаммы из базы данных,
    for level in result:  # для  использования в интерфейсе
        size = list(map(int, level[5].split('*')))
        cell_size = list(map(int, level[6].split('*')))
        screen = pg.Surface((size[0] * cell_size[0], size[1] * cell_size[1]))
        left_top = np.array(ImageColor.getcolor(level[1], "RGB"))
        right_top = np.array(ImageColor.getcolor(level[2], "RGB"))
        left_bottom = np.array(ImageColor.getcolor(level[3], "RGB"))
        right_bottom = np.array(ImageColor.getcolor(level[4], "RGB"))
        scheme = Field(size[0], size[1], left_top, right_top, left_bottom, right_bottom, level[7])
        scheme.set_view(0, 0, cell_size)
        scheme.render()
        scheme.sprite_group1.draw(screen)
        image = pg.transform.scale(screen, (300, 450))
        pg.image.save(image, 'data/' + level[-1] + '_' + str(level[0]) + '.jpg')  # название файла - id уровня
        # и сложность из бд


make_images()