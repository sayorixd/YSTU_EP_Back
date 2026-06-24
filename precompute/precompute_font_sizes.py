#
# What does this script do?
#
# The openpyxl package, which is used in competencies matrix and indicators table exports,
# lacks a function that automatically adjusts width/height of a column or a row with a set
# height/width. As of time of writing this comment, this function is manually implemented in
# src/common/excel.py file and named get_height_cell_pixels_after_wrapping_text, although it
# is not completely accurate and can allocate some extra space. The calculation inside this
# function accounts for advance widths of characters and kerning offset adjustments, which
# are retrieved from the FONT_DATA dictionary inside the same file. This script generates
# the necessary advance widths and kerning data for a set font with a set font size
#
# How to use this script?
#
# 1) (Optional) Create a virtual environment
# 2) Install dependecies listed in the requirements.txt file
# 3) Find config parameters section
# 4) Set font_file_path_string to the relative path to the desired font file
# 5) Set font_size to the desired font size in points
# 6) Run this script
# 7) Copy ADVANCE_WIDTHS and KERNING dictionaries and paste them in the FONT_DATA dictionary
#

import string
from math import floor, ceil
from pathlib import Path
from PIL import ImageFont
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode
from itertools import chain


#
# Config parameters
#

font_file_path_string = "fonts/Arial.ttf"
font_size = 11

# Coefficient to multiply the resulting advance_widths and kerning offsets by to match
# the sizes of characters and kerning in Excel and Google Docs
coefficient_advance_widths_and_kerning = 8.925 / 13.668

#
# End of config parameters
#


font_file_path = str(Path(font_file_path_string).expanduser())
font = ImageFont.truetype(font_file_path, font_size)

ttf = TTFont(font_file_path)

chars = list(chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables))
map_class_to_unicode = {
    c[1]: chr(c[0]) for c in chars
}
equivalent_pairs = [
    (chr(32), chr(160)),  # space
    (chr(45), chr(173)),  # -
    (chr(59), chr(894))
]
equivalent = dict()
equivalent.update({ c1: c2 for (c1, c2) in equivalent_pairs })
equivalent.update({ c2: c1 for (c1, c2) in equivalent_pairs })

#upm = ttf["head"].unitsPerEm
upm = 1000

def get_kern_table_data():
    global ttf
    kerning_pairs = {}
    
    # Check if the traditional 'kern' table exists
    if 'kern' in ttf:
        for table in ttf['kern'].kernTables:
            for (left_glyph, right_glyph), value in table.kernTable.items():
                kerning_pairs[(left_glyph, right_glyph)] = value
                
    return kerning_pairs

def get_gpos_kerning():
    global ttf
    kerning_pairs = {}
    
    if 'GPOS' not in ttf:
        return kerning_pairs

    gpos = ttf['GPOS'].table
    for lookup in gpos.LookupList.Lookup:
        # LookupType 2 is Pair Positioning
        if lookup.LookupType == 2:
            for pair_pos in lookup.SubTable:
                # Format 1: Adjustments for specific glyph pairs
                if pair_pos.Format == 1:
                    for left_glyph, pair_set in zip(pair_pos.Coverage.glyphs, pair_pos.PairSet):
                        for pair_value_record in pair_set.PairValueRecord:
                            right_glyph = pair_value_record.SecondGlyph
                            value = pair_value_record.Value1.XAdvance if pair_value_record.Value1 else 0
                            if value != 0:
                                kerning_pairs[(left_glyph, right_glyph)] = value
                                
                # Format 2: Class-based adjustments
                elif pair_pos.Format == 2:
                    left_classes = pair_pos.ClassDef1.classDefs
                    right_classes = pair_pos.ClassDef2.classDefs
                    
                    # Invert class definitions to map class ID -> list of glyphs
                    left_class_map = {}
                    for glyph, class_id in left_classes.items():
                        left_class_map.setdefault(class_id, []).append(glyph)
                        
                    right_class_map = {}
                    for glyph, class_id in right_classes.items():
                        right_class_map.setdefault(class_id, []).append(glyph)

                    for i, class1_record in enumerate(pair_pos.Class1Record):
                        for j, class2_record in enumerate(class1_record.Class2Record):
                            value = class2_record.Value1.XAdvance if class2_record.Value1 else 0
                            if value != 0:
                                left_glyphs = left_class_map.get(i, [])
                                right_glyphs = right_class_map.get(j, [])
                                for lg in left_glyphs:
                                    for rg in right_glyphs:
                                        kerning_pairs[(lg, rg)] = value
    return kerning_pairs

def get_all_kerning():
    all_kerns = get_kern_table_data()
    all_kerns.update(get_gpos_kerning())
    return all_kerns

supported_chars = \
    [c for c in string.printable] + \
    [c for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"]
for c in "\t\n\r\x0b\x0c":
    supported_chars.remove(c)
set_supported_chars = set([c for c in supported_chars])


advance_widths = { map_class_to_unicode[c[1]]: ttf["hmtx"][c[1]][0] for c in chars }

advance_widths_supported_characters = dict()
for c in supported_chars:
    #print(c, ord(c), f"width={advance_widths.get(c, None)}")
    advanced_width = advance_widths.get(c, None)
    if advanced_width == None:
        advanced_width = advance_widths[equivalent[c]]
    advance_widths_supported_characters[c] = advanced_width
ADVANCE_WIDTHS_PIXELS = {
    key: advance_width * font_size / upm * coefficient_advance_widths_and_kerning
    for key, advance_width in advance_widths_supported_characters.items()
}
ADVANCE_WIDTHS_PIXELS["\t"] = 4 * ADVANCE_WIDTHS_PIXELS[" "]
for key, value in ADVANCE_WIDTHS_PIXELS.items():
    ADVANCE_WIDTHS_PIXELS[key] = round(ceil(ADVANCE_WIDTHS_PIXELS[key] * 1000), 3) / 1000
ADVANCE_WIDTHS_PIXELS["UNSUPPORTED"] = ADVANCE_WIDTHS_PIXELS["0"]


kerning_raw = get_all_kerning()

kerning_by_pair_of_characters = {
    (map_class_to_unicode[key[0]], map_class_to_unicode[key[1]]): kerning_value
    for key, kerning_value in kerning_raw.items()
}
KERNING = dict()
for key, kerning_value in kerning_by_pair_of_characters.items():
    c1, c2 = key
    equivalent_c1 = equivalent.get(c1, None)
    if equivalent_c1 != None:
        c1 = equivalent_c1
    equivalent_c2 = equivalent.get(c2, None)
    if equivalent_c2 != None:
        c2 = equivalent_c2
    if c1 not in set_supported_chars or c2 not in set_supported_chars:
        continue
    KERNING[(c1, c2)] = kerning_value * font_size / upm * coefficient_advance_widths_and_kerning

for key, value in KERNING.items():
    KERNING[key] = round(ceil(KERNING[key] * 1000), 3) / 1000


print(f'{ADVANCE_WIDTHS_PIXELS=}')
print(f'{KERNING=}')
