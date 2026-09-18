import pygame
import sys
import os

pygame.init()

# --- ПУТЬ К РЕСУРСАМ (для работы внутри .exe) ---
def resource_path(relative_path):
    """Возвращает путь к файлу внутри exe или рядом со скриптом."""
    try:
        base_path = sys._MEIPASS  # PyInstaller распаковывает сюда
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- ОКНО ---
info = pygame.display.Info()
WIDTH, HEIGHT = int(info.current_w * 0.9), int(info.current_h * 0.9)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Тайна Шепчущего Леса")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
DARK_GREEN = (20, 120, 20)
RED = (200, 50, 50)
DARK_RED = (120, 20, 20)
GRAY = (80, 80, 80)
LIGHT_GRAY = (150, 150, 150)
GOLD = (255, 215, 0)
BTN_BORDER = (220, 220, 220)

def get_fonts(w, h):
    try:
        return (
            pygame.font.SysFont("georgia", int(h * 0.055), bold=True),
            pygame.font.SysFont("georgia", int(h * 0.032)),
            pygame.font.SysFont("georgia", int(h * 0.026))
        )
    except:
        return (
            pygame.font.SysFont("arial", int(h * 0.055), bold=True),
            pygame.font.SysFont("arial", int(h * 0.032)),
            pygame.font.SysFont("arial", int(h * 0.026))
        )

font_title, font, font_small = get_fonts(WIDTH, HEIGHT)

# Игровые переменные
game_state = 0
karma = 0
ending_type = ""
has_wolf_fang = False
has_glow_mushroom = False

# --- ОБОДКА ПЕРСОНАЖАМ ---
def add_outline(image, outline_color=BLACK, thickness=4):
    mask = pygame.mask.from_surface(image)
    outline_surf = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx == 0 and dy == 0:
                continue
            outline_surf.blit(
                mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0)),
                (dx, dy)
            )
    outline_surf.blit(image, (0, 0))
    return outline_surf

# --- ЗАГРУЗКА КАРТИНОК ---
def load_image(name, size=None, is_bg=False):
    path = resource_path(os.path.join("images", name))
    try:
        img = pygame.image.load(path).convert_alpha()
        if is_bg:
            img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        elif size:
            new_w = int(size[0] * (HEIGHT / 600))
            new_h = int(size[1] * (HEIGHT / 600))
            img = pygame.transform.scale(img, (new_w, new_h))
            img = add_outline(img, BLACK, 4)
        return img
    except (FileNotFoundError, pygame.error):
        print(f"Ошибка: Файл {name} не найден!")
        surf = pygame.Surface((WIDTH, HEIGHT) if is_bg else size, pygame.SRCALPHA)
        surf.fill(GRAY if not is_bg else (30, 30, 30))
        return surf

# Фоны
bg_forest = load_image("bg_forest.png", is_bg=True)
bg_wolf = load_image("bg_wolf.png", is_bg=True)
bg_glade = load_image("bg_glade.png", is_bg=True)
bg_cave = load_image("bg_cave.png", is_bg=True)
bg_good = load_image("end_good.png", is_bg=True)
bg_neutral = load_image("end_neutral.png", is_bg=True)
bg_bad = load_image("end_bad.png", is_bg=True)

# Персонажи
img_timmy = load_image("timmy.png", (250, 350))
img_timmy_happy = load_image("timmy_happy.png", (250, 350))
img_owl = load_image("owl.png", (200, 200))
img_spirit = load_image("spirit.png", (300, 400))
img_wolf = load_image("wolf_cub.png", (220, 220))
img_mushroom = load_image("mushroom.png", (180, 220))

# --- ПЛАШКА ПОД ТЕКСТ ---
def draw_panel(x, y, w, h, alpha=200):
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, alpha), (0, 0, w, h), border_radius=15)
    pygame.draw.rect(panel, (200, 200, 200, 80), (0, 0, w, h), 2, border_radius=15)
    screen.blit(panel, (x, y))

# --- ТЕКСТ НА ПЛАШКЕ ---
def draw_text_with_panel(text, font_obj, color, y_top, padding=25):
    words = text.split(' ')
    max_width = int(WIDTH * 0.75)
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font_obj.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    
    line_height = font_obj.get_height() + 6
    panel_h = len(lines) * line_height + padding * 2
    panel_w = max_width + padding * 2
    panel_x = (WIDTH - panel_w) // 2
    panel_y = y_top
    
    draw_panel(panel_x, panel_y, panel_w, panel_h, alpha=200)
    
    for i, line in enumerate(lines):
        shadow = font_obj.render(line, True, BLACK)
        surface = font_obj.render(line, True, color)
        rect = surface.get_rect(center=(WIDTH // 2, panel_y + padding + i * line_height + line_height // 2))
        screen.blit(shadow, (rect.x + 2, rect.y + 2))
        screen.blit(surface, rect)

# --- КНОПКИ ---
buttons = []

def create_button(text, x, y, w, h, color, hover_color, action):
    buttons.append({
        "rect": pygame.Rect(x, y, w, h),
        "text": text,
        "color": color,
        "hover": hover_color,
        "action": action
    })

def draw_buttons():
    mouse_pos = pygame.mouse.get_pos()
    for btn in buttons:
        rect = btn["rect"]
        is_hover = rect.collidepoint(mouse_pos)
        color = btn["hover"] if is_hover else btn["color"]
        
        shadow_rect = rect.move(3, 3)
        pygame.draw.rect(screen, (0, 0, 0, 150), shadow_rect, border_radius=10)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, BTN_BORDER, rect, 2, border_radius=10)
        
        text_surf = font_small.render(btn["text"], True, WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

# --- ИГРОВОЙ ЦИКЛ ---
running = True
clock = pygame.time.Clock()

while running:
    # 1. СОБЫТИЯ
    mouse_clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

    # 2. АДАПТАЦИЯ
    WIDTH, HEIGHT = screen.get_size()
    font_title, font, font_small = get_fonts(WIDTH, HEIGHT)
    bg_forest = pygame.transform.scale(bg_forest, (WIDTH, HEIGHT))
    bg_wolf = pygame.transform.scale(bg_wolf, (WIDTH, HEIGHT))
    bg_glade = pygame.transform.scale(bg_glade, (WIDTH, HEIGHT))
    bg_cave = pygame.transform.scale(bg_cave, (WIDTH, HEIGHT))
    bg_good = pygame.transform.scale(bg_good, (WIDTH, HEIGHT))
    bg_neutral = pygame.transform.scale(bg_neutral, (WIDTH, HEIGHT))
    bg_bad = pygame.transform.scale(bg_bad, (WIDTH, HEIGHT))

    # 3. КНОПКИ ТЕКУЩЕЙ СЦЕНЫ
    buttons = []
    btn_w = int(WIDTH * 0.32)
    btn_h = int(HEIGHT * 0.08)
    btn_y = HEIGHT - btn_h - 40

    # --- СЦЕНА 0: НАЧАЛО ---
    if game_state == 0:
        def go_forest():
            global game_state
            game_state = 1
        create_button("Отправиться в путь", WIDTH // 2 - btn_w // 2, btn_y, btn_w, btn_h, DARK_GREEN, GREEN, go_forest)

    # --- СЦЕНА 1: ФИЛИН ---
    elif game_state == 1:
        def go_left():
            global game_state, karma
            karma -= 1
            game_state = 2
        def go_right():
            global game_state, karma
            karma += 1
            game_state = 3
        create_button("Налево (тропа теней)", WIDTH // 2 - btn_w - 20, btn_y, btn_w, btn_h, DARK_RED, RED, go_left)
        create_button("Направо (тропа света)", WIDTH // 2 + 20, btn_y, btn_w, btn_h, DARK_GREEN, GREEN, go_right)

    # --- СЦЕНА 2: ВОЛЧОНОК ---
    elif game_state == 2:
        def help_wolf():
            global game_state, karma, has_wolf_fang
            karma += 2
            has_wolf_fang = True
            game_state = 4
        def ignore_wolf():
            global game_state
            game_state = 4
        create_button("Помочь волчонку", WIDTH // 2 - btn_w - 20, btn_y, btn_w, btn_h, DARK_GREEN, GREEN, help_wolf)
        create_button("Пройти мимо", WIDTH // 2 + 20, btn_y, btn_w, btn_h, GRAY, LIGHT_GRAY, ignore_wolf)

    # --- СЦЕНА 3: ГРИБЫ ---
    elif game_state == 3:
        def feed_mushroom():
            global game_state, karma, has_glow_mushroom
            karma += 2
            has_glow_mushroom = True
            game_state = 4
        def eat_mushroom():
            global game_state, karma
            karma -= 1
            game_state = 4
        create_button("Поделиться едой", WIDTH // 2 - btn_w - 20, btn_y, btn_w, btn_h, DARK_GREEN, GREEN, feed_mushroom)
        create_button("Съесть самому", WIDTH // 2 + 20, btn_y, btn_w, btn_h, DARK_RED, RED, eat_mushroom)

    # --- СЦЕНА 4: ПЕЩЕРА (ДУХ) ---
    elif game_state == 4:
        def make_deal():
            global game_state, ending_type
            ending_type = "neutral"
            game_state = 5
        def chase_spirit():
            global game_state, ending_type, karma
            if karma > 0 or has_wolf_fang or has_glow_mushroom:
                ending_type = "good"
            else:
                ending_type = "bad"
            game_state = 5
        create_button("Договориться с Духом", WIDTH // 2 - btn_w - 20, btn_y, btn_w, btn_h, GRAY, LIGHT_GRAY, make_deal)
        create_button("Прогнать Духа", WIDTH // 2 + 20, btn_y, btn_w, btn_h, DARK_GREEN, GREEN, chase_spirit)

    # --- СЦЕНА 5: ФИНАЛЫ ---
    elif game_state == 5:
        def restart():
            global game_state, karma, ending_type, has_wolf_fang, has_glow_mushroom
            game_state = 0
            karma = 0
            ending_type = ""
            has_wolf_fang = False
            has_glow_mushroom = False
        create_button("Играть снова", WIDTH // 2 - btn_w // 2, btn_y, btn_w, btn_h, GRAY, LIGHT_GRAY, restart)

    # 4. ПРОВЕРКА КЛИКА
    if mouse_clicked:
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            if btn["rect"].collidepoint(mouse_pos):
                btn["action"]()
                break

    # 5. ОТРИСОВКА СЦЕНЫ
    if game_state == 0:
        screen.blit(bg_forest, (0, 0))
        screen.blit(img_timmy, (int(WIDTH * 0.05), HEIGHT - img_timmy.get_height() - 20))
        draw_text_with_panel(
            "Гномик Тимми узнал, что его бабушка тяжело заболела. "
            "Старый лесной дух сказал: спасти её сможет только Слеза Древа Жизни, "
            "что растёт в самом сердце Шепчущего Леса. Тимми взял свою котомку и отправился в путь.",
            font, WHITE, y_top=int(HEIGHT * 0.08)
        )

    elif game_state == 1:
        screen.blit(bg_forest, (0, 0))
        screen.blit(img_owl, (WIDTH - img_owl.get_width() - 50, HEIGHT // 2 - 100))
        screen.blit(img_timmy, (int(WIDTH * 0.05), HEIGHT - img_timmy.get_height() - 20))
        draw_text_with_panel(
            "На опушке Тимми встретил Мудрого Филина. "
            "«Куда пойдёшь, малыш? Налево — тропа теней, там водятся волки. "
            "Направо — тропа света, но она длинная и петляет».",
            font, WHITE, y_top=int(HEIGHT * 0.08)
        )

    elif game_state == 2:
        screen.blit(bg_wolf, (0, 0))
        screen.blit(img_wolf, (WIDTH - img_wolf.get_width() - 80, HEIGHT // 2 - 100))
        screen.blit(img_timmy, (int(WIDTH * 0.05), HEIGHT - img_timmy.get_height() - 20))
        draw_text_with_panel(
            "На тёмной тропе Тимми услышал жалобный писк. "
            "В кустах лежал раненый волчонок. Его лапка застряла в коряге. "
            "Что же делать?",
            font, WHITE, y_top=int(HEIGHT * 0.08)
        )

    elif game_state == 3:
        screen.blit(bg_glade, (0, 0))
        screen.blit(img_mushroom, (WIDTH - img_mushroom.get_width() - 100, HEIGHT // 2 - 80))
        screen.blit(img_timmy, (int(WIDTH * 0.05), HEIGHT - img_timmy.get_height() - 20))
        draw_text_with_panel(
            "Тропа света вывела Тимми на поляну. "
            "Здесь росли говорящие грибы. Они грустно попросили: "
            "«Гномик, поделись едой, мы голодны уже три дня».",
            font, WHITE, y_top=int(HEIGHT * 0.08)
        )

    elif game_state == 4:
        screen.blit(bg_cave, (0, 0))
        screen.blit(img_spirit, (WIDTH - img_spirit.get_width() - 50, HEIGHT // 2 - 150))
        screen.blit(img_timmy, (int(WIDTH * 0.05), HEIGHT - img_timmy.get_height() - 20))
        draw_text_with_panel(
            "Наконец Тимми достиг сердца леса. У Древа Жизни его ждал Темный Дух. "
            "«Отдай мне свою смелость — и я отдам тебе Слезу. Или попробуй прогнать меня!»",
            font, WHITE, y_top=int(HEIGHT * 0.08)
        )

    elif game_state == 5:
        if ending_type == "good":
            screen.blit(bg_good, (0, 0))
            screen.blit(img_timmy_happy, (int(WIDTH * 0.05), HEIGHT - img_timmy_happy.get_height() - 20))
            draw_text_with_panel(
                "ХОРОШИЙ ФИНАЛ\n\nТимми принёс Слезу домой. Бабушка проснулась и обняла его! "
                "Лес расцвёл, а Темный Дух исчез навсегда. "
                "Тимми стал Хранителем Шепчущего Леса.",
                font, GREEN, y_top=int(HEIGHT * 0.08)
            )
        elif ending_type == "neutral":
            screen.blit(bg_neutral, (0, 0))
            screen.blit(img_timmy, (int(WIDTH * 0.05), HEIGHT - img_timmy.get_height() - 20))
            draw_text_with_panel(
                "НЕЙТРАЛЬНЫЙ ФИНАЛ\n\nТимми заключил сделку с Духом. "
                "Бабушка спасена, но часть магии Тимми навсегда осталась в пещере. "
                "Лес тих, но больше не шепчет ему по ночам.",
                font, WHITE, y_top=int(HEIGHT * 0.08)
            )
        elif ending_type == "bad":
            screen.blit(bg_bad, (0, 0))
            screen.blit(img_timmy, (int(WIDTH * 0.05), HEIGHT - img_timmy.get_height() - 20))
            draw_text_with_panel(
                "ПЛОХОЙ ФИНАЛ\n\nТимми вернулся домой ни с чем. "
                "Бабушка не проснулась. Лес засох, а Темный Дух забрал его силу. "
                "Тимми остался совсем один.",
                font, RED, y_top=int(HEIGHT * 0.08)
            )

    # 6. КНОПКИ
    draw_buttons()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
