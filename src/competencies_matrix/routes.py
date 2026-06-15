from src.exceptions import DirectionNotFoundException
from src.directions.model import Direction
from src.direction_map_cors.model import DirectionMapCore
from src.map_cors.model import MapCore
from src.departments.model import Department
from src.disciplines.model import Discipline
from src.discipline_blocks.model import DisciplineBlock
from src.discipline_block_competencies.model import DisciplineBlockCompetency
from src.competencies.model import Competency
from src.competency_groups.model import CompetencyGroup
from src.indicators.model import Indicator
from src.educational_levels.model import EducationalLevel
from src.dependencies import SessionDep

from sqlalchemy import select
from fastapi import APIRouter, status, Path, Response
from typing import Annotated
from fastapi.responses import StreamingResponse
from io import StringIO, BytesIO
import csv
from math import floor, ceil
from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.cell_range import CellRange
try:
    from openpyxl.cell import get_column_letter
except ImportError:
    from openpyxl.utils import get_column_letter
    from openpyxl.utils import column_index_from_string
from openpyxl.styles import PatternFill, Font, Alignment, DEFAULT_FONT
from openpyxl.styles.borders import Border, Side
import urllib.parse
import base64


router = APIRouter(
    tags=['maps']
)

def map_all_objects(objects_list, key_getter):    
    key_to_object = dict()

    for obj in objects_list:
        key = key_getter(obj)
        if key_to_object.get(key, None) == None:
            key_to_object[key] = []
        key_to_object[key].append(obj)
    
    return key_to_object

def get_unique_items_ordered(objects_list, getter_unique_property=None):
    if getter_unique_property == None:
        getter_unique_property = lambda x: x

    set_objects = set()
    unique_items = []
    for item in objects_list:
        old_length = len(set_objects)
        set_objects.add(getter_unique_property(item))
        if len(set_objects) != old_length:
            unique_items.append(item)
    return unique_items
    
def set_outer_border_of_cell_range(rows, cell_range, border):
    i1 = cell_range.min_row - 1
    j1 = cell_range.min_col - 1
    i2 = cell_range.max_row - 1
    j2 = cell_range.max_col - 1

    # Corners
    # |"
    style = rows[i1][j1].border
    new_style = Border(
        left=border.left,
        top=border.top,
        right=style.right,
        bottom=style.bottom
    )
    rows[i1][j1].border = new_style
    # "|
    style = rows[i1][j2].border
    new_style = Border(
        left=style.left,
        top=border.top,
        right=border.right,
        bottom=style.bottom
    )
    rows[i1][j2].border = new_style
    # _|
    style = rows[i2][j2].border
    new_style = Border(
        left=style.left,
        top=style.top,
        right=border.right,
        bottom=border.bottom
    )
    rows[i2][j2].border = new_style
    # |_
    style = rows[i2][j1].border
    new_style = Border(
        left=border.left,
        top=style.top,
        right=style.right,
        bottom=border.bottom
    )
    rows[i2][j1].border = new_style

    # Sides
    # Top
    for j in range(j1 + 1, j2):
        style = rows[i1][j].border
        new_style = Border(
            left=style.left,
            top=border.top,
            right=style.right,
            bottom=style.bottom
        )
        rows[i1][j].border = new_style
    # Right
    for i in range(i1 + 1, i2):
        style = rows[i][j2].border
        new_style = Border(
            left=style.left,
            top=style.top,
            right=border.right,
            bottom=style.bottom
        )
        rows[i][j2].border = new_style
    # Bottom
    for j in range(j1 + 1, j2):
        style = rows[i2][j].border
        new_style = Border(
            left=style.left,
            top=style.top,
            right=style.right,
            bottom=border.bottom
        )
        rows[i2][j].border = new_style
    # Left
    for i in range(i1 + 1, i2):
        style = rows[i][j1].border
        new_style = Border(
            left=border.left,
            top=style.top,
            right=style.right,
            bottom=style.bottom
        )
        rows[i][j1].border = new_style

def column_width_from_pixels(pixels):
    WIDTH_FUDGE = 1 / 7
    return pixels * WIDTH_FUDGE

def row_height_from_pixels(pixels):
    HEIGHT_FUDGE = 3 / 4
    return pixels * HEIGHT_FUDGE

# Hardcoded for Arial 11 pts
ADVANCE_WIDTHS_PIXELS={'0': 9.202, '1': 9.202, '2': 9.202, '3': 9.202, '4': 9.202, '5': 9.202, '6': 9.202, '7': 9.202, '8': 9.202, '9': 9.202, 'a': 9.202, 'b': 9.202, 'c': 8.273, 'd': 9.202, 'e': 9.202, 'f': 4.597, 'g': 9.202, 'h': 9.202, 'i': 3.676, 'j': 3.676, 'k': 8.273, 'l': 3.676, 'm': 13.783, 'n': 9.202, 'o': 9.202, 'p': 9.202, 'q': 9.202, 'r': 5.51, 's': 8.273, 't': 4.597, 'u': 9.202, 'v': 8.273, 'w': 11.949, 'x': 8.273, 'y': 8.273, 'z': 8.273, 'A': 11.036, 'B': 11.036, 'C': 11.949, 'D': 11.949, 'E': 11.036, 'F': 10.107, 'G': 12.87, 'H': 11.949, 'I': 4.597, 'J': 8.273, 'K': 11.036, 'L': 9.202, 'M': 13.783, 'N': 11.949, 'O': 12.87, 'P': 11.036, 'Q': 12.87, 'R': 11.949, 'S': 11.036, 'T': 10.107, 'U': 11.949, 'V': 11.036, 'W': 15.617, 'X': 11.036, 'Y': 11.036, 'Z': 10.107, '!': 4.597, '"': 5.874, '#': 9.202, '$': 9.202, '%': 14.712, '&': 11.036, "'": 3.159, '(': 5.51, ')': 5.51, '*': 6.439, '+': 9.663, ',': 4.597, '-': 5.51, '.': 4.597, '/': 4.597, ':': 4.597, ';': 4.597, '<': 9.663, '=': 9.663, '>': 9.663, '?': 9.202, '@': 16.796, '[': 4.597, '\\': 4.597, ']': 4.597, '^': 7.764, '_': 9.202, '`': 5.51, '{': 5.526, '|': 4.298, '}': 5.526, '~': 9.663, ' ': 4.597, 'а': 9.202, 'б': 9.477, 'в': 8.79, 'г': 6.035, 'д': 9.655, 'е': 9.202, 'ё': 9.202, 'ж': 11.068, 'з': 7.586, 'и': 9.243, 'й': 9.243, 'к': 7.239, 'л': 9.655, 'м': 11.375, 'н': 9.138, 'о': 9.202, 'п': 8.96, 'р': 9.202, 'с': 8.273, 'т': 7.578, 'у': 8.273, 'ф': 13.613, 'х': 8.273, 'ц': 9.477, 'ч': 8.621, 'ш': 13.274, 'щ': 13.613, 'ъ': 10.341, 'ы': 11.892, 'ь': 8.621, 'э': 8.443, 'ю': 12.41, 'я': 8.96, 'А': 11.036, 'Б': 10.858, 'В': 11.036, 'Г': 8.96, 'Д': 11.206, 'Е': 11.036, 'Ё': 11.044, 'Ж': 15.277, 'З': 9.994, 'И': 11.892, 'Й': 11.892, 'К': 9.638, 'Л': 10.858, 'М': 13.783, 'Н': 11.949, 'О': 12.87, 'П': 11.892, 'Р': 11.036, 'С': 11.949, 'Т': 10.107, 'У': 10.511, 'Ф': 12.579, 'Х': 11.036, 'Ц': 12.24, 'Ч': 11.028, 'Ш': 15.164, 'Щ': 15.512, 'Ъ': 13.096, 'Ы': 14.647, 'Ь': 10.858, 'Э': 11.892, 'Ю': 16.716, 'Я': 11.949, '\t': 18.388, 'UNSUPPORTED': 9.202}
KERNING={(' ', 'A'): -1.243, (' ', 'T'): -0.407, (' ', 'Y'): -0.407, ('1', '1'): -1.672, ('A', ' '): -1.243, ('A', 'T'): -1.672, ('A', 'V'): -1.672, ('A', 'W'): -0.836, ('A', 'Y'): -1.672, ('A', 'v'): -0.407, ('A', 'w'): -0.407, ('A', 'y'): -0.407, ('F', ','): -2.497, ('F', '.'): -2.497, ('F', 'A'): -1.243, ('L', ' '): -0.836, ('L', 'T'): -1.672, ('L', 'V'): -1.672, ('L', 'W'): -1.672, ('L', 'Y'): -1.672, ('L', 'y'): -0.836, ('P', ' '): -0.407, ('P', ','): -2.904, ('P', '.'): -2.904, ('P', 'A'): -1.672, ('R', 'T'): -0.407, ('R', 'V'): -0.407, ('R', 'W'): -0.407, ('R', 'Y'): -0.407, ('T', ' '): -0.407, ('T', ','): -2.497, ('T', '-'): -1.243, ('T', '.'): -2.497, ('T', ':'): -2.497, ('T', ';'): -2.497, ('T', 'A'): -1.672, ('T', 'O'): -0.407, ('T', 'a'): -2.497, ('T', 'c'): -2.497, ('T', 'e'): -2.497, ('T', 'i'): -0.836, ('T', 'o'): -2.497, ('T', 'r'): -0.836, ('T', 's'): -2.497, ('T', 'u'): -0.836, ('T', 'w'): -1.243, ('T', 'y'): -1.243, ('V', ','): -2.068, ('V', '-'): -1.243, ('V', '.'): -2.068, ('V', ':'): -0.836, ('V', ';'): -0.836, ('V', 'A'): -1.672, ('V', 'a'): -1.672, ('V', 'e'): -1.243, ('V', 'i'): -0.407, ('V', 'o'): -1.243, ('V', 'r'): -0.836, ('V', 'u'): -0.836, ('V', 'y'): -0.836, ('W', ','): -1.243, ('W', '-'): -0.407, ('W', '.'): -1.243, ('W', ':'): -0.407, ('W', ';'): -0.407, ('W', 'A'): -0.836, ('W', 'a'): -0.836, ('W', 'e'): -0.407, ('W', 'i'): 0.0, ('W', 'o'): -0.407, ('W', 'r'): -0.407, ('W', 'u'): -0.407, ('W', 'y'): -0.198, ('Y', ' '): -0.407, ('Y', ','): -2.904, ('Y', '-'): -2.068, ('Y', '.'): -2.904, ('Y', ':'): -1.243, ('Y', ';'): -1.463, ('Y', 'A'): -1.672, ('Y', 'a'): -1.672, ('Y', 'e'): -2.068, ('Y', 'i'): -0.836, ('Y', 'o'): -2.068, ('Y', 'p'): -1.672, ('Y', 'q'): -2.068, ('Y', 'u'): -1.243, ('Y', 'v'): -1.243, ('f', 'f'): -0.407, ('r', ','): -1.243, ('r', '.'): -1.243, ('v', ','): -1.672, ('v', '.'): -1.672, ('w', ','): -1.243, ('w', '.'): -1.243, ('y', ','): -1.672, ('y', '.'): -1.672, ('А', 'Д'): 0.748, ('А', 'З'): -0.253, ('А', 'Л'): 0.495, ('А', 'О'): -0.495, ('А', 'П'): -0.253, ('А', 'С'): -0.495, ('А', 'Т'): -1.76, ('А', 'У'): -0.99, ('А', 'Ф'): -0.748, ('А', 'Ч'): -1.76, ('А', 'Э'): -0.495, ('А', 'а'): 0.253, ('А', 'т'): -0.495, ('А', 'у'): -0.253, ('А', 'ф'): 0.253, ('А', 'э'): 0.495, ('Б', 'А'): -0.495, ('Б', 'З'): -0.253, ('Б', 'О'): -0.253, ('Б', 'С'): -0.253, ('Б', 'Т'): -1.012, ('Б', 'У'): -0.517, ('Б', 'Ф'): -0.253, ('Б', 'Х'): -0.495, ('Б', 'Ч'): -1.012, ('Б', 'Ъ'): -0.748, ('Б', 'Э'): -0.253, ('Б', 'Я'): -0.253, ('Б', 'л'): -0.253, ('Б', 'у'): -0.495, ('В', 'А'): -0.748, ('В', 'Д'): -0.495, ('В', 'Ж'): -0.495, ('В', 'З'): -0.748, ('В', 'Л'): -0.253, ('В', 'О'): -0.748, ('В', 'С'): -0.748, ('В', 'Т'): -1.507, ('В', 'У'): -0.748, ('В', 'Ф'): -0.748, ('В', 'Х'): -0.99, ('В', 'Ч'): -1.012, ('В', 'Ъ'): -1.265, ('В', 'Я'): -0.748, ('В', 'д'): -0.253, ('В', 'м'): -0.253, ('В', 'т'): -0.748, ('В', 'у'): -0.253, ('В', 'х'): -0.253, ('В', 'ч'): -0.748, ('В', 'я'): -0.253, ('Г', ','): -2.75, ('Г', '.'): -2.75, ('Г', 'А'): -1.507, ('Г', 'Д'): -1.507, ('Г', 'З'): -0.495, ('Г', 'Л'): -1.265, ('Г', 'М'): -0.517, ('Г', 'О'): -1.265, ('Г', 'С'): -1.012, ('Г', 'Я'): -0.748, ('Г', 'а'): -1.265, ('Г', 'в'): -1.265, ('Г', 'д'): -1.507, ('Г', 'е'): -1.507, ('Г', 'и'): -1.265, ('Г', 'л'): -1.265, ('Г', 'м'): -1.265, ('Г', 'н'): -1.265, ('Г', 'о'): -1.507, ('Г', 'р'): -1.265, ('Г', 'у'): -1.507, ('Г', 'ы'): -1.265, ('Г', 'ь'): -1.265, ('Г', 'ю'): -1.265, ('Г', 'я'): -1.507, ('Д', 'У'): 0.253, ('Д', 'Ф'): -0.495, ('Д', 'Ч'): -0.77, ('Д', 'з'): 0.748, ('Д', 'о'): 0.253, ('Д', 'у'): 0.495, ('Е', 'З'): -0.495, ('Е', 'с'): -0.253, ('Ж', 'З'): -0.253, ('Ж', 'О'): -0.495, ('Ж', 'С'): -0.253, ('Ж', 'Т'): 0.253, ('Ж', 'У'): 0.495, ('Ж', 'Ъ'): 0.495, ('Ж', 'а'): 0.253, ('Ж', 'е'): -0.275, ('Ж', 'о'): -0.253, ('Ж', 'у'): -0.253, ('З', 'Л'): -0.253, ('З', 'О'): -0.253, ('З', 'С'): -0.253, ('З', 'Т'): -0.495, ('З', 'У'): -0.253, ('З', 'Ф'): -0.253, ('З', 'Ч'): -0.495, ('З', 'Я'): -0.253, ('К', 'З'): -0.253, ('К', 'О'): -0.253, ('К', 'С'): -0.253, ('К', 'У'): 0.253, ('К', 'Ф'): -0.77, ('Л', 'Ф'): -0.253, ('Л', 'б'): 0.253, ('Л', 'у'): 0.253, ('М', 'Ф'): -0.253, ('М', 'Ч'): -0.253, ('М', 'а'): 0.253, ('М', 'е'): 0.253, ('М', 'о'): 0.253, ('М', 'с'): 0.253, ('М', 'у'): 0.253, ('М', 'ч'): -0.253, ('М', 'э'): 0.253, ('О', 'А'): -0.495, ('О', 'Д'): -0.495, ('О', 'Ж'): -0.495, ('О', 'Л'): -0.253, ('О', 'У'): -0.495, ('О', 'Х'): -1.012, ('О', 'Ч'): -0.495, ('О', 'Я'): -0.495, ('О', 'д'): -0.495, ('О', 'л'): -0.253, ('О', 'х'): -0.253, ('Р', ','): -4.257, ('Р', '.'): -4.257, ('Р', ':'): -0.495, ('Р', ';'): -0.495, ('Р', 'А'): -1.507, ('Р', 'Д'): -1.507, ('Р', 'Ж'): -0.253, ('Р', 'З'): -0.495, ('Р', 'Л'): -1.265, ('Р', 'М'): -0.253, ('Р', 'О'): -0.495, ('Р', 'С'): -0.253, ('Р', 'Т'): -1.012, ('Р', 'У'): -0.495, ('Р', 'Ф'): -0.253, ('Р', 'Х'): -1.012, ('Р', 'Я'): -0.495, ('Р', 'а'): -0.748, ('Р', 'д'): -1.76, ('Р', 'е'): -0.99, ('Р', 'о'): -0.99, ('Р', 'э'): -0.495, ('Р', 'я'): -0.748, ('С', 'А'): -0.495, ('С', 'Д'): -0.495, ('С', 'З'): -0.253, ('С', 'Л'): -0.748, ('С', 'М'): -0.253, ('С', 'О'): -0.495, ('С', 'Т'): -0.748, ('С', 'У'): -0.748, ('С', 'Х'): -1.265, ('С', 'Ч'): -0.748, ('С', 'Ъ'): -0.77, ('С', 'Э'): -0.253, ('С', 'а'): 0.253, ('С', 'ж'): 0.495, ('С', 'ч'): -0.253, ('Т', ','): -2.497, ('Т', '.'): -2.497, ('Т', 'А'): -0.748, ('Т', 'Д'): -0.748, ('Т', 'Ж'): 0.253, ('Т', 'З'): -0.253, ('Т', 'Л'): -0.495, ('Т', 'О'): -1.012, ('Т', 'Ф'): -0.748, ('Т', 'Я'): -0.495, ('Т', 'а'): -1.012, ('Т', 'в'): -0.99, ('Т', 'е'): -1.265, ('Т', 'и'): -0.99, ('Т', 'к'): -0.99, ('Т', 'л'): -1.012, ('Т', 'м'): -0.99, ('Т', 'о'): -1.76, ('Т', 'п'): -0.99, ('Т', 'р'): -1.265, ('Т', 'с'): -1.265, ('Т', 'у'): -1.265, ('Т', 'х'): -0.99, ('Т', 'щ'): -0.99, ('Т', 'ы'): -0.99, ('Т', 'ь'): -0.99, ('Т', 'ю'): -0.99, ('Т', 'я'): -1.265, ('У', ','): -2.992, ('У', '.'): -2.992, ('У', ':'): -0.495, ('У', ';'): -0.495, ('У', 'А'): -1.507, ('У', 'Д'): -1.012, ('У', 'З'): -0.495, ('У', 'Л'): -0.748, ('У', 'О'): -0.748, ('У', 'Ф'): -0.748, ('У', 'Э'): -0.495, ('У', 'Я'): -0.495, ('У', 'б'): -0.495, ('У', 'в'): -1.265, ('У', 'г'): -1.012, ('У', 'д'): -1.76, ('У', 'е'): -1.507, ('У', 'ж'): -0.748, ('У', 'з'): -1.265, ('У', 'и'): -1.012, ('У', 'й'): -0.748, ('У', 'к'): -1.012, ('У', 'л'): -1.507, ('У', 'м'): -1.012, ('У', 'н'): -1.012, ('У', 'о'): -1.507, ('У', 'п'): -1.012, ('У', 'р'): -1.012, ('У', 'с'): -1.507, ('У', 'х'): -1.012, ('У', 'ц'): -1.012, ('У', 'ш'): -1.012, ('У', 'щ'): -1.012, ('У', 'ю'): -1.012, ('У', 'я'): -1.507, ('Ф', 'А'): -0.495, ('Ф', 'Д'): -0.748, ('Ф', 'Л'): -0.748, ('Ф', 'Т'): -1.265, ('Ф', 'У'): -1.012, ('Ф', 'Ч'): -0.495, ('Ф', 'Я'): -0.77, ('Ф', 'л'): -0.748, ('Х', 'З'): -0.495, ('Х', 'О'): -0.748, ('Х', 'С'): -0.748, ('Х', 'Ф'): -0.748, ('Х', 'Э'): -0.77, ('Х', 'о'): -0.253, ('Х', 'у'): -0.495, ('Ц', 'О'): -0.495, ('Ц', 'а'): 0.495, ('Щ', 'а'): 0.253, ('Щ', 'у'): 0.495, ('Ъ', 'Я'): -0.748, ('Ь', 'А'): -0.495, ('Ь', 'Д'): -0.495, ('Ь', 'Ж'): -0.748, ('Ь', 'З'): -0.253, ('Ь', 'Л'): -0.77, ('Ь', 'М'): -0.495, ('Ь', 'О'): -0.495, ('Ь', 'С'): -0.495, ('Ь', 'Т'): -2.255, ('Ь', 'Х'): -1.012, ('Ь', 'Ч'): -1.76, ('Ь', 'Э'): -0.253, ('Ь', 'Я'): -1.012, ('Э', 'Д'): -0.748, ('Э', 'Ж'): -0.275, ('Э', 'З'): -0.253, ('Э', 'Л'): -0.748, ('Э', 'Х'): -0.77, ('Э', 'Я'): -0.495, ('Э', 'д'): -0.748, ('Э', 'ж'): 0.253, ('Э', 'л'): -0.748, ('Э', 'м'): -0.253, ('Э', 'я'): -0.253, ('Ю', 'А'): -0.748, ('Ю', 'Д'): -0.99, ('Ю', 'Ж'): -0.495, ('Ю', 'Л'): -1.012, ('Ю', 'О'): -0.253, ('Ю', 'С'): -0.253, ('Ю', 'Т'): -1.265, ('Ю', 'Х'): -1.012, ('Ю', 'Ч'): -0.748, ('Ю', 'д'): -1.012, ('Ю', 'л'): -1.012, ('Ю', 'м'): -0.253, ('а', 'з'): -0.253, ('а', 'т'): -0.495, ('а', 'у'): -0.253, ('а', 'ч'): -0.495, ('б', 'а'): -0.517, ('б', 'д'): -1.012, ('б', 'е'): -0.253, ('б', 'ж'): -0.253, ('б', 'з'): -0.495, ('б', 'л'): -1.012, ('б', 'м'): -0.495, ('б', 'с'): -0.253, ('б', 'у'): -0.495, ('б', 'ф'): -0.253, ('б', 'х'): -0.748, ('б', 'ч'): -0.748, ('б', 'ъ'): -0.748, ('б', 'э'): -0.253, ('б', 'я'): -0.495, ('в', 'а'): -0.253, ('в', 'б'): -0.253, ('в', 'д'): -0.253, ('в', 'е'): -0.253, ('в', 'ж'): -0.253, ('в', 'з'): -0.253, ('в', 'л'): -0.517, ('в', 'м'): -0.253, ('в', 'о'): -0.253, ('в', 'с'): -0.253, ('в', 'т'): -0.495, ('в', 'у'): -0.495, ('в', 'ф'): -0.253, ('в', 'ч'): -1.012, ('в', 'ъ'): -0.748, ('в', 'я'): -0.253, ('г', ','): -2.75, ('г', '.'): -2.75, ('г', 'а'): -0.495, ('г', 'д'): -1.012, ('г', 'е'): -0.495, ('г', 'з'): -0.253, ('г', 'л'): -0.495, ('г', 'о'): -0.495, ('г', 'с'): -0.495, ('г', 'я'): -0.253, ('д', 'ъ'): -0.495, ('д', 'э'): 0.253, ('е', 'б'): -0.253, ('е', 'д'): -0.495, ('е', 'ж'): -0.253, ('е', 'з'): -0.495, ('е', 'л'): -0.748, ('е', 'т'): -0.748, ('е', 'у'): -0.253, ('е', 'х'): -0.495, ('е', 'ч'): -0.748, ('ж', 'б'): 0.253, ('ж', 'у'): 0.253, ('ж', 'ч'): -0.253, ('ж', 'ъ'): 0.495, ('з', 'б'): -0.253, ('з', 'д'): -0.495, ('з', 'е'): -0.253, ('з', 'з'): -0.253, ('з', 'л'): -0.253, ('з', 'о'): -0.253, ('з', 'с'): -0.253, ('з', 'у'): -0.253, ('з', 'ф'): -0.253, ('з', 'ч'): -0.748, ('з', 'ъ'): -0.495, ('к', 'а'): 0.495, ('к', 'б'): 0.495, ('к', 'е'): 0.253, ('к', 'з'): 0.253, ('к', 'л'): 0.253, ('к', 'о'): 0.253, ('к', 'с'): 0.253, ('к', 'т'): 0.253, ('к', 'у'): 0.253, ('к', 'э'): 0.253, ('л', 'о'): 0.253, ('л', 'ч'): -0.495, ('м', 'б'): -0.253, ('м', 'з'): -0.253, ('м', 'у'): 0.253, ('о', 'д'): -0.495, ('о', 'ж'): -0.253, ('о', 'з'): -0.253, ('о', 'л'): -0.495, ('о', 'т'): -0.495, ('о', 'у'): -0.253, ('о', 'х'): -0.253, ('о', 'ч'): -0.495, ('р', 'д'): -0.517, ('р', 'з'): -0.253, ('р', 'л'): -0.77, ('р', 'т'): -0.495, ('р', 'у'): -0.253, ('р', 'х'): -0.253, ('р', 'ч'): -0.495, ('р', 'я'): -0.253, ('с', 'ж'): 0.253, ('с', 'о'): 0.253, ('с', 'ч'): -0.253, ('с', 'э'): 0.253, ('т', ','): -2.497, ('т', '.'): -2.497, ('т', 'а'): -0.253, ('т', 'д'): -0.748, ('т', 'е'): -0.253, ('т', 'ж'): 0.748, ('т', 'л'): -0.495, ('т', 'о'): -0.253, ('т', 'с'): -0.253, ('т', 'у'): 0.253, ('у', ','): -2.255, ('у', '.'): -2.255, ('у', 'а'): -0.253, ('у', 'б'): 0.253, ('у', 'д'): -0.748, ('у', 'е'): -0.253, ('у', 'ж'): 0.253, ('у', 'л'): -0.495, ('у', 'м'): -0.253, ('у', 'о'): -0.275, ('у', 'р'): -0.253, ('у', 'с'): -0.253, ('у', 'ф'): -0.253, ('у', 'э'): -0.253, ('у', 'я'): -0.253, ('ф', 'б'): -0.253, ('ф', 'д'): -0.495, ('ф', 'л'): -0.495, ('ф', 'т'): -0.495, ('ф', 'у'): -0.253, ('ф', 'ч'): -0.495, ('ф', 'я'): -0.253, ('х', 'а'): -0.253, ('х', 'б'): -0.253, ('х', 'е'): -0.253, ('х', 'з'): -0.253, ('х', 'о'): -0.253, ('х', 'с'): -0.253, ('х', 'т'): -0.253, ('х', 'ф'): -0.253, ('х', 'ч'): -0.495, ('ц', 'е'): -0.253, ('ц', 'з'): -0.253, ('ц', 'о'): -0.253, ('ц', 'с'): -0.253, ('щ', 'е'): -0.253, ('щ', 'о'): -0.253, ('щ', 'у'): 0.253, ('ь', 'т'): -1.76, ('ь', 'ч'): -1.507, ('э', 'д'): -0.495, ('э', 'е'): 0.253, ('э', 'з'): -0.253, ('э', 'л'): -0.495, ('э', 'о'): 0.253, ('э', 'т'): -0.495, ('э', 'х'): -0.253, ('э', 'я'): -0.253, ('ю', 'д'): -0.495, ('ю', 'ж'): -0.253, ('ю', 'л'): -0.495, ('ю', 'м'): -0.253, ('ю', 'т'): -0.495, ('ю', 'х'): -0.253, ('ю', 'ч'): -0.495}

# Hardcoded for Arial 11 pts
def get_width_text(text):
    global ADVANCE_WIDTHS_PIXELS, KERNING
    UNSUPPORTED_CHARACTER_WIDTH = ADVANCE_WIDTHS_PIXELS["UNSUPPORTED"]
    return sum([ADVANCE_WIDTHS_PIXELS.get(c, UNSUPPORTED_CHARACTER_WIDTH) for c in text]) + \
           sum([KERNING.get((text[i], text[i + 1]), 0) for i in range(len(text) - 1)])

def determine_number_of_rows_after_wrapping_text(text, width_pixels):
    if len(text) == 0:
        return 1

    words = [word + " " for word in text.split(" ")]
    words[-1] = words[-1][:-1]
    widths = [get_width_text(word) for word in words]
    rows = 0
    sum_width = 0
    i = 0
    while i < len(widths):
        if sum_width + widths[i] < width_pixels:
            sum_width += widths[i]
            i += 1
        elif sum_width == 0:
            rows += ceil(widths[i] / width_pixels)
            sum_width = 0
            i += 1
        else:
            rows += 1
            sum_width = 0
    
    if sum_width != 0:
        rows += 1

    return rows

# Hardcoded for Arial 11 pts
def get_height_cell(rows_count):
    FONT_SIZE_POINTS = 11
    if rows_count == 1:
        return 22
    return 19 * rows_count


@router.get(
    '/directions/{direction_id}/competencies_matrix/export/excel',
    responses={
        200: {'description': 'Competencies matrix successfully exported (Excel file)'},
        404: {'description': 'Direction not found'}
    },
    summary='Export the competencies matrix as Excel file'
)
def export_map_excel(direction_id: Annotated[int, Path(gt=0)], session: SessionDep) -> StreamingResponse:
    # V  1. Получить список ядер в направлении подготовки
    # V  2. Получить списки дисциплин, сгрупированные по ядрам
    # V  3. Получить список дисциплин в направлении подготовки
    # V  4. Получить список кафедр по каждой дисциплине
    # V  5. Получить список связей в матрице компетенции
    # V  6. Получить список компетенций в направлении подготовки
    # V  7. Сгруппировать список компетенций по группам компетенций
    # V  8. Отметить плюсиком связи, остальное - пусто
    # X  9. Посчитать итоговое количество плюсиков по дисциплинам
    # X  10. Макет таблицы
    # X  11. Оформление таблицы

    # 1. Получить список дисциплин в направлении подготовки:
    #   1.1. Получить ядра
    #   1.2. Получить дисциплины, добавленные в ядра
    #   1.3. Получить список дисциплин из справочника "Дисциплины"

    direction = session.get(Direction, direction_id)
    if not direction:
        raise DirectionNotFoundException()

    educational_level = session.get(EducationalLevel, direction.educational_level_id)

    # 1. Получить список ядер в направлении подготовки

    direction_map_cores = session.execute(
        select(DirectionMapCore).where(DirectionMapCore.direction_id == direction_id)
    ).scalars().all()

    map_core_ids = [direction_map_core.map_core_id for direction_map_core in direction_map_cores]
    map_cores = session.execute(
        select(MapCore).where(MapCore.id.in_(map_core_ids))
    ).scalars().all()
    map_core_id_to_map_core = {
        map_core.id: map_core
        for map_core in map_cores
    }

    # 2. Получить списки дисциплин, сгруппированные по ядрам
    # 3. Получить список дисциплин в направлении подготовки

    discipline_blocks = session.execute(
        select(DisciplineBlock).where(DisciplineBlock.map_core_id.in_(map_core_ids))
    ).scalars().all()
    
    discipline_blocks_unique_discipline = get_unique_items_ordered(
        discipline_blocks,
        getter_unique_property=lambda x: x.discipline_id
    )

    map_core_ids_of_discipline_blocks = [
        discipline_block.map_core_id
        for discipline_block in discipline_blocks_unique_discipline
    ]

    discipline_ids = [
        discipline_block.discipline_id
        for discipline_block in discipline_blocks_unique_discipline
    ]

    disciplines = session.execute(
        select(Discipline).where(Discipline.id.in_(discipline_ids))
    ).scalars().all()

    disciplines_by_map_core_id = dict()
    for i in range(len(disciplines)):
        map_core_id = map_core_ids_of_discipline_blocks[i]
        if disciplines_by_map_core_id.get(map_core_id, None) == None:
            disciplines_by_map_core_id[map_core_id] = []
        disciplines_by_map_core_id[map_core_id].append(disciplines[i])

    # 4. Получить список кафедр по каждой дисциплине

    department_ids = [discipline.department_id for discipline in disciplines]
    all_departments = session.execute(select(Department)).scalars().all()
    department_id_to_department = {
        department.id: department
        for department in all_departments
    }
    departments = [
        department_id_to_department[department_id]
        for department_id in department_ids
    ]
    
    # 5. Получить список связей в матрице компетенции

    discipline_block_ids = [discipline_block.id for discipline_block in discipline_blocks]
    discipline_block_competencies = session.execute(
        select(DisciplineBlockCompetency)\
        .where(DisciplineBlockCompetency.discipline_block_id.in_(discipline_block_ids))
    ).scalars().all()

    # 6. Получить список компетенций в направлении подготовки

    competency_ids = [
        discipline_block_competency.competency_id
        for discipline_block_competency in get_unique_items_ordered(
            discipline_block_competencies,
            getter_unique_property=lambda x: x.competency_id
        )
    ]
    competencies = session.execute(
        select(Competency).where(Competency.id.in_(competency_ids))
    ).scalars().all()
    competency_id_to_competencies = {
        competency_ids[i]: competencies[i]
        for i in range(len(competency_ids))
    }

    # 7. Сгруппировать компетенции по группам компетенций

    competencies_by_competency_group_id = map_all_objects(
        competencies,
        key_getter=lambda x: x.competency_group_id
    )
    competency_group_ids = [
        key for key in competencies_by_competency_group_id.keys()
    ]
    competency_groups = session.execute(
        select(CompetencyGroup).where(CompetencyGroup.id.in_(competency_group_ids))
    ).scalars().all()
    competency_group_id_to_competency_group = {
        competency_group_ids[i]: competency_groups[i]
        for i in range(len(competency_group_ids))
    }

    # 8. Отметить плюсиком связи, остальное пусто
    
    # 8.1. Преобразовать связи из "Дисциплина ядра" - "Компетенция" в "Дисциплина" - "Компетенция"
    
    discipline_block_id_to_discipline_id = {
        discipline_block.id: discipline_block.discipline_id
        for discipline_block in discipline_blocks
    }

    discipline_competencies = [
        {
            "discipline_id": discipline_block_id_to_discipline_id[discipline_block_competency.discipline_block_id],
            "competency_id": discipline_block_competency.competency_id
        }
        for discipline_block_competency in discipline_block_competencies
    ]

    discipline_ids_by_competency_id = dict()
    for discipline_competency in discipline_competencies:
        key = discipline_competency["competency_id"]
        if discipline_ids_by_competency_id.get(key, None) == None:
            discipline_ids_by_competency_id[key] = set()
        discipline_ids_by_competency_id[key].add(discipline_competency["discipline_id"])

    # 8.2. Проставляем плюсики там, где есть связь

    row_by_competency_id = dict()
    row_by_competency_id = {
        competency.id: [
            "+" if discipline_id in discipline_ids_by_competency_id[competency.id]
            else ""
            for discipline_id in discipline_ids
        ]
        for competency in competencies
    }

    # 9. Посчитать количество плюсиков по дисциплинам
    # 10. Макет таблицы

    wb = Workbook()
    ws = wb.active
    ws.title = direction.name

    # To automatically determine sizes of rows and columns in exported excel file
    # sizes of each character are hardcoded for Arial font in get_text_width function.
    # After changing font family and size of default font you should precompute
    # widths for each character of new font and change hardcoded values
    default_font = Font(name="Arial", sz=11)
    for key, value in default_font.__dict__.items():
        setattr(DEFAULT_FONT, key, value)
    title_font = Font(name="Arial", sz=14, b=True)
    header1_font = Font(name="Arial", sz=14)
    map_core_font = Font(name="Arial", sz=14, b=True)
    header2_font = Font(name="Arial", sz=12)

    thin_border = Border(left=Side(style="thin"),
                         top=Side(style="thin"),
                         right=Side(style="thin"),
                         bottom=Side(style="thin"))
    medium_border = Border(left=Side(style="medium"),
                           top=Side(style="medium"),
                           right=Side(style="medium"),
                           bottom=Side(style="medium"))

    color_disciplines = "99cc00"
    color_header_competency_group = "fffd40"
    colors_competency_groups = [
        "fbe5d7",
        "ffe59f",
        "b5cad2"
    ]

    table_width = 3 + len(disciplines)
    table_height = \
        4 + \
        sum([1 + len(c_list) for c_list in competencies_by_competency_group_id.values()]) + \
        1

    rows = [
        [Cell(ws, row=1, column="A", value="") for j in range(table_width)] for i in range(1 + table_height)
    ]

    i_row = 0
    row = rows[i_row]
    row[0].value = f"Матрица соответствия компетенций и дисциплин по направлению подготовки {direction.name} " + \
                   f"(уровень {educational_level.name.lower()})"
    row[0].font = title_font
    row[0].alignment = Alignment(horizontal="left", wrap_text=True)
    row[3].value = f"Направленность (профиль) {direction.name}"
    row[3].font = title_font
    row[3].alignment = Alignment(horizontal="left", wrap_text=True)
    ws.row_dimensions[i_row + 1].height = row_height_from_pixels(71)

    i_row += 1
    row = rows[i_row]
    row[0].value = "№ п/п"
    row[0].font = header1_font
    row[0].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    row[1].value = "Компетенции"
    row[1].font = header1_font
    row[1].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    row[2].value = "Формулировка компетенции"
    row[2].font = header1_font
    row[2].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    i = 3
    for map_core in map_cores:
        count_disciplines_of_map_core = len(disciplines_by_map_core_id[map_core.id])
        row[i].value = map_core.name
        row[i].font = map_core_font
        row[i].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        i += count_disciplines_of_map_core
    ws.row_dimensions[i_row + 1].height = row_height_from_pixels(60)

    i_row += 1
    row = rows[i_row]
    i = 3
    for map_core in map_cores:
        count_disciplines_of_map_core = len(disciplines_by_map_core_id[map_core.id])
        for discipline in disciplines_by_map_core_id[map_core.id]:
            row[i].value = discipline.name
            row[i].alignment = Alignment(horizontal="center", vertical="center", textRotation=90, wrap_text=True)
            row[i].fill = PatternFill(
                start_color=color_disciplines,
                end_color=color_disciplines,
                fill_type="solid"
            )
            i += 1

    disciplines_row_height_pixels = 205
    ws.row_dimensions[i_row + 1].height = row_height_from_pixels(disciplines_row_height_pixels)
    n = 4
    for map_core in map_cores:
        count_disciplines_of_map_core = len(disciplines_by_map_core_id[map_core.id])
        for discipline in disciplines_by_map_core_id[map_core.id]:
            n_rows_discipline = determine_number_of_rows_after_wrapping_text(
                discipline.name,
                disciplines_row_height_pixels
            )
            row_disciplines_width = get_height_cell(n_rows_discipline) + 4
            ws.column_dimensions[get_column_letter(n)].width = column_width_from_pixels(row_disciplines_width)
            n += 1
    
    i_row += 1
    row = rows[i_row]
    for i in range(table_width):
        row[i].fill = PatternFill(
            start_color=color_header_competency_group,
            end_color=color_header_competency_group,
            fill_type="solid"
        )
    row[2].value = "Обеспечивающая кафедра \u2192"
    row[2].alignment = Alignment(horizontal="right", vertical="center")
    i = 3
    for department in departments:
        row[i].value = department.short_name
        row[i].alignment = Alignment(horizontal="center", vertical="center", textRotation=90)
        i += 1
    ws.row_dimensions[i_row + 1].height = row_height_from_pixels(60)

    i_row += 1
    row = rows[i_row]
    for i in range(table_width):
        row[i].fill = PatternFill(
            start_color=color_header_competency_group,
            end_color=color_header_competency_group,
            fill_type="solid"
        )
    for i in range(table_width):
        row[i].alignment = Alignment(horizontal="center", vertical="center")
    row[0].value = "1"
    for i in range(2, table_width):
        row[i].value = str(i)
    
    column_code_size_pixels = 51
    column_name_size_pixels = 181
    column_description_size_pixels = 285
    ws.column_dimensions[get_column_letter(1)].width = column_width_from_pixels(column_code_size_pixels)
    ws.column_dimensions[get_column_letter(2)].width = column_width_from_pixels(column_name_size_pixels)
    ws.column_dimensions[get_column_letter(3)].width = column_width_from_pixels(column_description_size_pixels)

    count_plus = [0] * (table_width - 3)
    competency_group_color_i = 0
    for competency_group_id, competencies_of_competency_group in competencies_by_competency_group_id.items():
        competency_group = competency_group_id_to_competency_group[competency_group_id]

        i_row += 1
        row = rows[i_row]
        row[0].value = f"[НАЗВАНИЕ ГРУППЫ КОМПЕТЕНЦИЙ] ({competency_group.name})"
        row[0].alignment = Alignment(horizontal="center", vertical="center")
        for i in range(table_width):
            row[i].fill = PatternFill(
                start_color=color_header_competency_group,
                end_color=color_header_competency_group,
                fill_type="solid"
            )
        
        for competency in competencies_of_competency_group:
            i_row += 1
            row = rows[i_row]
            pattern_fill = PatternFill(
                start_color=colors_competency_groups[competency_group_color_i],
                end_color=colors_competency_groups[competency_group_color_i],
                fill_type="solid"
            )
            row[0].value = competency.code
            row[0].alignment = Alignment(horizontal="center", vertical="center")
            row[0].fill = pattern_fill
            row[1].value = competency.name
            row[1].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            row[1].fill = pattern_fill
            row[2].value = competency.description
            row[2].alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            row[2].fill = pattern_fill
            row_plus_or_none = row_by_competency_id[competency.id]
            for i in range(3, table_width):
                row[i].value = row_plus_or_none[i - 3]
                row[i].alignment = Alignment(horizontal="center", vertical="center")
                if row_plus_or_none[i - 3] == "+":
                    count_plus[i - 3] += 1

            n_rows_competency_name = determine_number_of_rows_after_wrapping_text(
                competency.name,
                column_name_size_pixels
            )
            n_rows_competency_description = determine_number_of_rows_after_wrapping_text(
                competency.description,
                column_description_size_pixels
            )
            height_competency_name = get_height_cell(n_rows_competency_name)
            height_competency_description = get_height_cell(n_rows_competency_description)
            row_height = max(height_competency_name, height_competency_description)
            ws.row_dimensions[i_row + 1].height = row_height_from_pixels(row_height)

        competency_group_color_i = (competency_group_color_i + 1) % len(colors_competency_groups)

    i_row += 1
    row = rows[i_row]
    row[0].value = "Итого:"
    row[0].alignment = Alignment(horizontal="right")
    for i in range(3, table_width):
        row[i].value = count_plus[i - 3]
        row[i].alignment = Alignment(horizontal="center")

    # Borders

    for i in range(1, len(rows)):
        for j in range(len(rows[0])):
            rows[i][j].border = thin_border

    for i in range(1, 5):
        for j in range(len(rows[0])):
            rows[i][j].border = medium_border

    set_outer_border_of_cell_range(
        rows,
        CellRange(
            min_row=2, min_col=1,
            max_row=1 + table_height, max_col=table_width
        ),
        medium_border
    )

    i_row = table_height
    row = rows[i_row]
    row[0].border = medium_border
    set_outer_border_of_cell_range(
        rows,
        CellRange(
            min_row=i_row + 1, min_col=1,
            max_row=i_row + 1, max_col=table_width
        ),
        medium_border
    )
    
    n = 6
    for competency_group_id, competencies_of_competency_group in competencies_by_competency_group_id.items():
        count_competencies = len(competencies_of_competency_group)
        rows[n - 1][0].border = medium_border
        set_outer_border_of_cell_range(
            rows,
            CellRange(
                min_row=n, min_col=1,
                max_row=n, max_col=table_width
            ),
            medium_border
        )
        n += 1
        for m in range(1, 4):
            set_outer_border_of_cell_range(
                rows,
                CellRange(
                    min_row=n, min_col=m,
                    max_row=n + count_competencies - 1, max_col=m
                ),
                medium_border
            )
        n += count_competencies
        
    # Add rows to worksheet

    for i in range(len(rows)):
        ws.append(rows[i])

    # Merge cells

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=3)
    ws.merge_cells(start_row=1, start_column=4, end_row=1, end_column=table_width)

    ws.merge_cells(start_row=2, start_column=1, end_row=3, end_column=1)
    ws.merge_cells(start_row=2, start_column=2, end_row=3, end_column=2)
    ws.merge_cells(start_row=2, start_column=3, end_row=3, end_column=3)

    i = 4
    for map_core in map_cores:
        count_disciplines_of_map_core = len(disciplines_by_map_core_id[map_core.id])
        ws.merge_cells(
            start_row=2, start_column=i,
            end_row=2, end_column=i + count_disciplines_of_map_core - 1
        )
        i += count_disciplines_of_map_core
    
    i = 6
    for competency_group_id, competencies_of_competency_group in competencies_by_competency_group_id.items():
        ws.merge_cells(
            start_row=i, start_column=1,
            end_row=i, end_column=3
        )
        i += len(competencies_of_competency_group) + 1

    ws.merge_cells(
        start_row=1 + table_height, start_column=1,
        end_row=1 + table_height, end_column=3
    )

    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Матрица компетенций {direction.name}.xlsx"
    encoded_filename = urllib.parse.quote(filename.encode("utf-8"))

    headers = {
        "Content-Disposition": f'attachment; filename=\"competencies_matrix.xlsx\"; filename*=UTF-8\'\'{encoded_filename};',
        "Access-Control-Expose-Headers": "Content-Disposition",
    }

    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers=headers,
    )
