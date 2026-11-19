from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


SIZE = 1024
MARGIN = 24
WIDTH = SIZE - MARGIN * 2
PAPER = (246, 241, 229)
INK = (23, 35, 59)
NAVY = (22, 50, 79)
RED = (179, 32, 44)
SLATE = (52, 61, 78)
GOLD = (198, 158, 66)
SEA = (203, 221, 228)
TAN = (226, 210, 175)
WHITE = (255, 255, 255)
GREY = (118, 122, 130)

FONT_PATHS = {
    "serif_cond_bold": [
        "/usr/share/fonts/truetype/noto/NotoSerifDisplay-CondensedBold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-CondensedBold.ttf",
    ],
    "serif_cond_bitalic": [
        "/usr/share/fonts/truetype/noto/NotoSerifDisplay-CondensedBoldItalic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-CondensedBoldItalic.ttf",
    ],
    "serif_bold": ["/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"],
    "sans_bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "sans": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}


def font(kind, size):
    for path in FONT_PATHS[kind]:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    raise FileNotFoundError(f"No configured font for {kind}")


FONTS = {
    "kicker": font("sans_bold", 12),
    "masthead": font("serif_cond_bold", 64),
    "standfirst": font("serif_cond_bitalic", 18),
    "lead_head": font("serif_cond_bold", 30),
    "wide_head": font("serif_cond_bold", 27),
    "deck": font("sans", 16),
    "footer": font("sans", 12),
}

STORIES = [
    (1, "NORTH AMERICA", "GAMES", "Grand Theft Auto VI launches worldwide",
     "After a 13-year wait, Grand Theft Auto VI begins its global rollout; players return to Vice City.", "gta"),
    (2, "THE HAGUE", "WORLD COURT", "World Court rules on Myanmar genocide case",
     "The world court delivers its judgment today on whether Myanmar committed genocide against the Rohingya.", "court"),
    (3, "ASIA", "DIPLOMACY", "Trump, Xi and Putin meet in Shenzhen",
     "Trump, Xi and Putin meet in Shenzhen on the sidelines of the APEC summit; nuclear cuts and the US war with Iran on the agenda.", "summit"),
    (4, "UNITED STATES", "POLITICS", "Democrats nominate Jeffries for Speaker",
     "Democrats nominate Hakeem Jeffries for Speaker of the House; he would be the first African-American Speaker.", "capitol"),
    (5, "SOUTH ASIA", "WEATHER", "Cyclone Akvan bears down on India's east coast",
     "Cyclone Akvan bears down on India's east coast, expected to cross between Machilipatnam and Puri.", "cyclone"),
    (6, "EUROPE", "UKRAINE", "EU proposes a 45 billion euro loan for Ukraine",
     "The EU proposes a 45 billion euro loan for Ukraine, to be repaid after Russia pays reparations.", "eu"),
]

image = Image.new("RGB", (SIZE, SIZE), PAPER)
draw = ImageDraw.Draw(image)


def text_width(text, face):
    return draw.textlength(text, font=face)


def wrap_text(text, face, width):
    lines = []
    line = ""
    for word in text.split():
        candidate = word if not line else f"{line} {word}"
        if text_width(candidate, face) <= width:
            line = candidate
        else:
            if not line:
                raise ValueError(f"Word wider than text box: {word}")
            lines.append(line)
            line = word
            if text_width(line, face) > width:
                raise ValueError(f"Word wider than text box: {word}")
    if line:
        lines.append(line)
    return lines


def draw_block(text, x, y, width, max_height, face, color, line_height):
    lines = wrap_text(text, face, width)
    height = len(lines) * line_height
    if height > max_height:
        raise ValueError(f"Text block is {height}px tall; box allows {max_height}px")
    for line in lines:
        if text_width(line, face) > width:
            raise ValueError(f"Wrapped line wider than box: {line}")
        draw.text((x, y), line, font=face, fill=color)
        y += line_height
    return y


def draw_fitted_line(text, x, y, width, max_height, face, color):
    measured_width = text_width(text, face)
    measured_height = face.getbbox(text)[3] - face.getbbox(text)[1]
    if measured_width > width:
        raise ValueError(f"Text line is {measured_width:.1f}px wide; box allows {width}px")
    if measured_height > max_height:
        raise ValueError(f"Text line is {measured_height}px tall; box allows {max_height}px")
    draw.text((x, y), text, font=face, fill=color)


def draw_star(cx, cy, outer_radius, color):
    points = []
    for point in range(10):
        angle = -math.pi / 2 + point * math.pi / 5
        radius = outer_radius if point % 2 == 0 else outer_radius * 0.42
        points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    draw.polygon(points, fill=color)


def panel_box(box, fill):
    draw.rectangle(box, fill=fill, outline=INK, width=1)


def art_gta(x, y, w, h):
    panel_box((x, y, x + w - 1, y + h - 1), (218, 151, 119))
    draw.rectangle((x + 1, y + 1, x + w - 2, y + 67), fill=(235, 178, 145))
    draw.ellipse((x + w - 100, y + 13, x + w - 54, y + 59), fill=GOLD, outline=INK, width=1)
    skyline = [(8, 81, 38, 132), (42, 98, 74, 132), (79, 75, 109, 132),
               (115, 91, 146, 132), (153, 61, 187, 132), (194, 92, 226, 132),
               (232, 77, 270, 132), (275, 99, 308, 132)]
    for left, top, right, bottom in skyline:
        draw.rectangle((x + left, y + top, x + right, y + bottom), fill=NAVY, outline=INK)
    for palm_x, top in ((x + 56, y + 38), (x + w - 51, y + 47)):
        draw.line((palm_x, y + 130, palm_x, top), fill=INK, width=4)
        for dx, dy in ((-24, 2), (-18, -12), (-4, -17), (11, -13), (23, 1), (5, 6)):
            draw.line((palm_x, top, palm_x + dx, top + dy), fill=INK, width=4)
    draw.rectangle((x + 1, y + 132, x + w - 2, y + h - 2), fill=(42, 48, 62))
    draw.polygon([(x + 125, y + 132), (x + 190, y + 132), (x + 244, y + h - 2), (x + 72, y + h - 2)], fill=(63, 69, 79), outline=INK)
    draw.line((x + 158, y + 135, x + 153, y + h - 5), fill=GOLD, width=3)
    car_x, car_y = x + 98, y + 108
    draw.polygon([(car_x, car_y + 17), (car_x + 17, car_y + 3), (car_x + 58, car_y + 3),
                  (car_x + 76, car_y + 17), (car_x + 83, car_y + 22), (car_x - 3, car_y + 22)],
                 fill=RED, outline=INK)
    draw.polygon([(car_x + 21, car_y + 5), (car_x + 53, car_y + 5),
                  (car_x + 66, car_y + 16), (car_x + 13, car_y + 16)], fill=SEA, outline=INK)
    for wheel in (car_x + 15, car_x + 65):
        draw.ellipse((wheel - 6, car_y + 17, wheel + 6, car_y + 29), fill=INK, outline=WHITE)


def art_court(x, y, w, h):
    panel_box((x, y, x + w - 1, y + h - 1), (233, 225, 205))
    for cx in (x + 68, x + w - 68):
        draw.rectangle((cx - 20, y + 48, cx + 20, y + 147), fill=(245, 238, 221), outline=INK)
        for offset in (-13, 0, 13):
            draw.line((cx + offset, y + 58, cx + offset, y + 137), fill=NAVY, width=4)
        draw.rectangle((cx - 27, y + 43, cx + 27, y + 52), fill=TAN, outline=INK)
        draw.rectangle((cx - 26, y + 144, cx + 26, y + 153), fill=TAN, outline=INK)
    cx = x + w // 2
    draw.line((cx, y + 30, cx, y + 140), fill=INK, width=5)
    draw.line((cx - 85, y + 48, cx + 85, y + 48), fill=GOLD, width=5)
    draw.ellipse((cx - 10, y + 26, cx + 10, y + 46), fill=GOLD, outline=INK)
    for direction in (-1, 1):
        end = cx + direction * 70
        draw.line((end, y + 51, end - direction * 8, y + 80), fill=INK, width=2)
        draw.line((end, y + 51, end + direction * 8, y + 80), fill=INK, width=2)
        draw.arc((end - 33, y + 77, end + 33, y + 106), 0, 180, fill=INK, width=3)
        draw.line((end - 30, y + 92, end + 30, y + 92), fill=GOLD, width=3)
    draw.rectangle((cx - 40, y + 143, cx + 40, y + 152), fill=NAVY, outline=INK)


def art_summit(x, y, w, h):
    panel_box((x, y, x + w - 1, y + h - 1), (220, 192, 166))
    draw.rectangle((x + 1, y + 112, x + w - 2, y + h - 2), fill=SEA)
    for left, top, right, bottom in ((15, 74, 48, 111), (52, 49, 84, 111), (90, 82, 126, 111),
                                     (133, 39, 170, 111), (177, 66, 212, 111), (220, 47, 250, 111),
                                     (257, 76, 301, 111)):
        draw.rectangle((x + left, y + top, x + right, y + bottom), fill=NAVY, outline=INK)
    flag_y = y + 15
    poles = (x + 65, x + 158, x + 251)
    for pole in poles:
        draw.line((pole, flag_y - 4, pole, y + 154), fill=INK, width=2)
    fx = poles[0]
    draw.rectangle((fx + 2, flag_y, fx + 40, flag_y + 25), fill=RED, outline=INK)
    draw_star(fx + 10, flag_y + 8, 4, GOLD)
    for sx, sy in ((19, 5), (22, 11), (18, 17), (10, 20)):
        draw_star(fx + sx, flag_y + sy, 2, GOLD)
    fx = poles[1]
    draw.rectangle((fx + 2, flag_y, fx + 44, flag_y + 25), fill=WHITE, outline=INK)
    for stripe in range(4):
        draw.rectangle((fx + 2, flag_y + stripe * 6, fx + 45, flag_y + stripe * 6 + 2), fill=RED)
    draw.rectangle((fx + 2, flag_y, fx + 20, flag_y + 13), fill=NAVY, outline=INK)
    fx = poles[2]
    draw.rectangle((fx + 2, flag_y, fx + 43, flag_y + 8), fill=WHITE, outline=INK)
    draw.rectangle((fx + 2, flag_y + 8, fx + 43, flag_y + 17), fill=(52, 91, 156), outline=INK)
    draw.rectangle((fx + 2, flag_y + 17, fx + 43, flag_y + 26), fill=RED, outline=INK)
    draw.line((x + 22, y + 131, x + w - 22, y + 131), fill=WHITE, width=2)


def art_capitol(x, y, w, h):
    panel_box((x, y, x + w - 1, y + h - 1), (224, 216, 199))
    cx = x + w // 2
    base = y + 98
    draw.rectangle((x + 77, base, x + w - 78, y + 102), fill=NAVY, outline=INK)
    draw.rectangle((x + 91, base - 10, x + w - 92, base), fill=WHITE, outline=INK)
    draw.polygon([(cx - 76, base - 12), (cx, y + 43), (cx + 76, base - 12)], fill=(238, 231, 214), outline=INK)
    draw.rectangle((cx - 67, y + 37, cx + 67, y + 48), fill=WHITE, outline=INK)
    draw.ellipse((cx - 40, y + 9, cx + 40, y + 61), fill=(238, 231, 214), outline=INK, width=2)
    draw.rectangle((cx - 40, y + 38, cx + 40, y + 62), fill=(238, 231, 214), outline=INK)
    draw.arc((cx - 40, y + 8, cx + 40, y + 82), 180, 360, fill=INK, width=2)
    draw.line((cx, y + 2, cx, y + 9), fill=INK, width=3)
    for col_x in (cx - 55, cx - 19, cx + 17, cx + 53):
        draw.rectangle((col_x, y + 49, col_x + 10, base - 10), fill=WHITE, outline=INK)
    draw.rectangle((x + 69, y + 102, x + w - 70, y + 103), fill=INK)


def art_cyclone(x, y, w, h):
    panel_box((x, y, x + w - 1, y + h - 1), (214, 222, 221))
    draw.rectangle((x + 1, y + 69, x + w - 2, y + h - 2), fill=SEA)
    cx, cy = x + w // 2, y + 52
    for radius in (8, 16, 24, 32):
        draw.arc((cx - radius, cy - radius, cx + radius, cy + radius), 35, 315, fill=NAVY, width=4)
    draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=RED, outline=INK)
    for start_x in range(x + 18, x + w - 20, 35):
        draw.line((start_x, y + 5, start_x - 13, y + 36), fill=SLATE, width=2)
    draw.arc((x + 205, y + 65, x + 294, y + 99), 190, 345, fill=WHITE, width=4)
    draw.arc((x + 220, y + 74, x + 281, y + 101), 190, 345, fill=NAVY, width=2)


def art_eu(x, y, w, h):
    panel_box((x, y, x + w - 1, y + h - 1), (226, 222, 211))
    cx, cy, radius = x + w // 2 - 65, y + h // 2, 42
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=NAVY, outline=INK, width=2)
    for index in range(12):
        angle = -math.pi / 2 + index * math.pi / 6
        star_x = cx + math.cos(angle) * 29
        star_y = cy + math.sin(angle) * 29
        draw_star(star_x, star_y, 3, GOLD)
    px, py = x + w // 2 + 5, y + 17
    draw.polygon([(px, py), (px + 120, py), (px + 144, py + 23), (px + 144, py + 77),
                  (px, py + 77)], fill=WHITE, outline=INK)
    draw.polygon([(px + 120, py), (px + 120, py + 24), (px + 144, py + 24)], fill=TAN, outline=INK)
    for line_y, line_end in ((py + 39, px + 125), (py + 50, px + 127), (py + 61, px + 113)):
        draw.line((px + 15, line_y, line_end, line_y), fill=SLATE, width=2)


ART = {"gta": art_gta, "court": art_court, "summit": art_summit,
       "capitol": art_capitol, "cyclone": art_cyclone, "eu": art_eu}


def header():
    draw_fitted_line("THE DAY IN WORLD NEWS", MARGIN, 24, 270, 16, FONTS["kicker"], INK)
    right_text = "ONE PAGE · SIX STORIES"
    right_width = 270
    right_x = SIZE - MARGIN - text_width(right_text, FONTS["kicker"])
    draw_fitted_line(right_text, right_x, 24, right_width, 16, FONTS["kicker"], INK)
    masthead = "Thursday 19 November 2026"
    mast_width = text_width(masthead, FONTS["masthead"])
    draw_fitted_line(masthead, (SIZE - mast_width) / 2, 40, WIDTH, 74,
                     FONTS["masthead"], INK)
    draw.line((MARGIN, 119, SIZE - MARGIN, 119), fill=INK, width=3)
    draw.line((MARGIN, 124, SIZE - MARGIN, 124), fill=INK, width=1)
    standfirst = "Every story on this page happened, or was first reported, on this day."
    draw_block(standfirst, MARGIN, 130, WIDTH, 27, FONTS["standfirst"], NAVY, 24)
    return 158


def story_text(story, x, y, width, heading_face, max_text_height):
    num, region, beat, headline, deck, _ = story
    number = f"{num:02d}"
    label = f"{region} · {beat}"
    number_width = text_width(number, FONTS["kicker"])
    label_width = text_width(label, FONTS["kicker"])
    if number_width + 7 + label_width > width:
        raise ValueError(f"Story {num} kicker is wider than its {width}px box")
    draw_fitted_line(number, x, y, number_width, 16, FONTS["kicker"], RED)
    label_x = x + number_width + 7
    draw_fitted_line(label, label_x, y, width - number_width - 7, 16,
                     FONTS["kicker"], INK)
    y += 17
    y = draw_block(headline, x, y + 2, width, max_text_height, heading_face, INK,
                   heading_face.size + 3)
    y = draw_block(deck, x, y + 4, width, max_text_height, FONTS["deck"], SLATE, 20)
    return y


def lead_card(story, x, y, width):
    ART[story[5]](x, y, width, 160)
    return story_text(story, x, y + 168, width, FONTS["lead_head"], 112)


def wide_card(story, x, y, width):
    ART[story[5]](x, y, width, 104)
    return story_text(story, x, y + 111, width, FONTS["wide_head"], 78)


def render():
    header_bottom = header()
    lead_y = header_bottom + 10
    lead_width = (WIDTH - 24) // 3
    lead_bottoms = [lead_card(STORIES[index], MARGIN + index * (lead_width + 12), lead_y, lead_width)
                    for index in range(3)]
    leads_bottom = max(lead_bottoms)
    divider_one = leads_bottom + 10
    draw.line((MARGIN, divider_one, SIZE - MARGIN, divider_one), fill=INK, width=1)
    wide_y = divider_one + 11
    wide_width = (WIDTH - 12) // 2
    wide_bottoms = [wide_card(STORIES[story_index], MARGIN + column * (wide_width + 12), wide_y, wide_width)
                    for column, story_index in enumerate((3, 4))]
    wides_bottom = max(wide_bottoms)
    divider_two = wides_bottom + 10
    draw.line((MARGIN, divider_two, SIZE - MARGIN, divider_two), fill=INK, width=1)
    final_y = divider_two + 11
    ART[STORIES[5][5]](MARGIN, final_y, WIDTH, 104)
    final_bottom = story_text(STORIES[5], MARGIN, final_y + 111, WIDTH,
                              FONTS["wide_head"], 60)
    footer_rule = final_bottom + 8
    draw.line((MARGIN, footer_rule, SIZE - MARGIN, footer_rule), fill=INK, width=1)
    footer = "Six stories that defined Thursday 19 November 2026, as reported that day."
    footer_bottom = draw_block(footer, MARGIN, footer_rule + 7, WIDTH, 18,
                               FONTS["footer"], GREY, 15)
    measurements = {
        "header bottom": header_bottom,
        "lead bottoms": lead_bottoms,
        "wide bottoms": wide_bottoms,
        "final bottom": footer_bottom,
    }
    if footer_bottom > 1000:
        raise ValueError(f"Final content bottom {footer_bottom} exceeds y=1000")
    image.save(Path(__file__).with_name("entry.png"), format="PNG", optimize=False)
    for label, value in measurements.items():
        print(f"{label}: {value}")


if __name__ == "__main__":
    render()
