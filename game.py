"""
MoonieQuest – Pokémon-style learning game with AP2 flashcards
Run with:  python game.py
Assets expected in:  assets/moonie/*.png  assets/ppl/  assets/*.png
"""

import pygame
import sys
import os
import csv
import random
import json
import time
import math

# ── Bootstrap ──────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

SW, SH = 1200, 800
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("MoonieQuest – AP2 Edition")
clock = pygame.time.Clock()
FPS   = 60

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Fonts ──────────────────────────────────────────────────────────────────────
def font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)

F_HUGE  = font(52, True)
F_BIG   = font(34, True)
F_MED   = font(22)
F_SMALL = font(17)
F_TINY  = font(13)

# ── Colors ─────────────────────────────────────────────────────────────────────
C_BG     = (30, 34, 42)
C_PANEL  = (45, 50, 62)
C_PANEL2 = (55, 62, 78)
C_WHITE  = (240, 245, 255)
C_YELLOW = (255, 220, 50)
C_GREEN  = (80, 200, 100)
C_RED    = (220, 60, 60)
C_BLUE   = (80, 140, 220)
C_PURPLE = (150, 80, 220)
C_ORANGE = (240, 140, 50)
C_GRAY   = (120, 130, 150)
C_DARK   = (20, 22, 28)
C_ROCKET = (180, 20, 20)
C_STEIN  = (120, 200, 255)   # Entwicklungsstein highlight color

TYPE_COLORS = {
    "Normal":  (168,168,120), "Feuer":   (240,128,48),  "Wasser":  (104,144,240),
    "Pflanze": (120,200,80),  "Elektro": (248,208,48),  "Eis":     (152,216,216),
    "Kampf":   (192,48,40),   "Gift":    (160,64,160),  "Boden":   (224,192,104),
    "Flug":    (168,144,240), "Psycho":  (248,88,136),  "Käfer":   (168,184,32),
    "Gestein": (184,160,56),  "Geist":   (112,88,152),  "Drache":  (112,56,248),
    "Unlicht": (112,88,72),   "Stahl":   (184,184,208), "Fee":     (238,153,172),
}

# ── Image loader ───────────────────────────────────────────────────────────────
_img_cache = {}
def load_img(path, size=None):
    key = (path, size)
    if key in _img_cache:
        return _img_cache[key]
    full = os.path.join(BASE, path)
    try:
        img = pygame.image.load(full).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
    except Exception:
        img = pygame.Surface(size or (64, 64), pygame.SRCALPHA)
        img.fill((100, 100, 100, 180))
        if size:
            s = min(size) // 2
            pygame.draw.rect(img, (200,80,80), (size[0]//2-s//2, size[1]//2-s//2, s, s))
    _img_cache[key] = img
    return img

_fit_cache = {}
def fit_img(path, max_w, max_h):
    """Load image and scale proportionally to fit within max_w x max_h. Returns (surface, actual_w, actual_h)."""
    key = (path, max_w, max_h)
    if key in _fit_cache:
        s = _fit_cache[key]; return s, s.get_width(), s.get_height()
    full = os.path.join(BASE, path)
    try:
        img = pygame.image.load(full).convert_alpha()
        iw, ih = img.get_size()
        scale = min(max_w / iw, max_h / ih, 1.0)
        nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
        # upscale if image is smaller than half the box
        if iw < max_w * 0.5 and ih < max_h * 0.5:
            scale2 = min(max_w / iw, max_h / ih)
            nw, nh = max(1, int(iw * scale2)), max(1, int(ih * scale2))
        img = pygame.transform.smoothscale(img, (nw, nh))
    except Exception:
        img = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
        img.fill((100, 100, 100, 120))
        nw, nh = max_w, max_h
    _fit_cache[key] = img
    return img, img.get_width(), img.get_height()

# Item image paths — used everywhere items are displayed
ITEM_IMAGES = {
    "balls":                "assets/pokeball.png",
    "master_balls":         "assets/meisterball.png",
    "potions":              "assets/trank.png",
    "super_potions":        "assets/supertrank.png",
    "hyper_potions":        "assets/hypertrank.png",
    "sonderbonbons":        "assets/sonderbonbon.png",
    "beleber":              "assets/beleber.png",
    "top_beleber":          "assets/topBeleber.png",
    "raid_passes":          "assets/raidpass.png",
    "premium_raid_passes":  "assets/premiumRaidPass.png",
    "redbull":              "assets/redbull.png",
    "entwicklungsstein":    "assets/stein.png",   # ← NEU
}

def item_icon(key, size=24):
    path = ITEM_IMAGES.get(key)
    if not path:
        return None
    return load_img(path, (size, size))

def load_flashcards(path):
    cards = []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    q = row[0].replace('$', '').strip()
                    a = row[1].replace('$', '').strip()
                    cards.append({
                        "q": q, "a": a, "known": False, "shown": 0,
                        "ease": 2.5,   # SM-2 ease factor
                        "interval": 0, # days until next review (0 = today)
                        "due": "",     # ISO date string
                        "reps": 0,     # total correct reps
                        "streak": 0,   # consecutive correct
                    })
    except Exception as e:
        print(f"Flashcard load error: {e}")
    return cards

# ── Save / Load ────────────────────────────────────────────────────────────────
SAVE_FILE = os.path.join(BASE, "savegame.json")

def default_save():
    return {
        "trainer": 0, "name": "Spieler",
        "team": [], "pc_box": [],
        "balls": 10, "master_balls": 0, "coins": 0,
        "potions": 3, "super_potions": 0, "hyper_potions": 0,
        "sonderbonbons": 0, "beleber": 0, "top_beleber": 0,
        "raid_passes": 0, "premium_raid_passes": 0, "redbull": 0,
        "entwicklungsstein": 0,          # ← NEU
        "badges": 0, "battles_won": 0,
        "cards_known": 0, "total_catches": 0,
        "step_count": 0,
        "trainer_battles_won":  0,
        "rocket_battles_won":   0,
        "evolution_count":      0,
        "cards_correct_total":  0,
        "cards_best_streak":    0,
        "cards_current_streak": 0,
        "stein_used_count":     0,       # ← NEU
        "evoli_evos_no_stone":  [],      # ← NEU  list of evo names triggered without stone
        "achievements": {},
        "card_album":   {},
        "blackmarket":  {"stock": [], "refresh_at": 0},
        "daily_event_date":   "",
        "daily_event_streak": 0,
        "current_map":        "Normal",
        "map_weather":        {},
        "friendship":         {},   # {moonie_name: 0-255}
        # Rang-System
        "rank":               0,          # 0=Bronze 1=Silber 2=Gold 3=Platin 4=Meister
        "rank_points":        0,
        # Wetter (täglich, via Datum-Seed gesetzt)
        "weather_date":       "",
        "weather":            "Klar",
        # Gilden-Challenges
        "guild_date":         "",
        "guild_challenges":   [],         # [{id, desc, goal, progress, reward_coins, done}]
        # Prüfungsmodus
        "exam_best_score":    0,
        "exam_attempts":      0,
        # Einstellungen
        "settings": {
            "sfx_vol":        5,
            "music_vol":      5,
            "game_speed":     1,          # 1=Normal 2=Schnell
            "show_hints":     True,
        },
    }

def save_game(data):
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass

def load_game():
    try:
        with open(SAVE_FILE) as f:
            d = json.load(f)
            dd = default_save()
            dd.update(d)
            return dd
    except:
        return None

# ── Moonie data ────────────────────────────────────────────────────────────────
import addPokemon
ALL_MOONIES_DICT = addPokemon.ALL_MOONIES
from moonie import effectiveness_label, get_type_multiplier
import achievements as ach_module

# Evoli-Entwicklungen (gespiegelt aus achievements.py)
EVOLI_EVOLUTIONS = ach_module.EVOLI_EVOLUTIONS

def get_moonie(name):
    m = ALL_MOONIES_DICT.get(name)
    if m:
        return m.clone_for_battle()
    import moonie as mmod
    return mmod.Moonie(name,"common",False,["Normal"],0,1,"assets/moonie/ditto.png")

def moonie_to_dict(m):
    """Serialisiert ein Moonie-Objekt in ein JSON-fähiges Dict."""
    return {
        "name":        m.name,
        "level":       m.level,
        "xp":          getattr(m, "xp", 0),
        "current_hp":  m.current_hp,
        "max_hp":      m.max_hp,
        "attack":      m.attack,
    }

def moonie_from_dict(d):
    """Stellt ein Moonie-Objekt aus einem gespeicherten Dict wieder her."""
    name = d.get("name", "Bisasam")
    m = ALL_MOONIES_DICT.get(name)
    if m:
        m = m.clone_for_battle()
    else:
        import moonie as mmod
        m = mmod.Moonie(name,"common",False,["Normal"],0,1,"assets/moonie/ditto.png")
    m.level      = d.get("level",      m.level)
    m.xp         = d.get("xp",         0)
    m.max_hp     = d.get("max_hp",     m.max_hp)
    m.current_hp = d.get("current_hp", m.max_hp)
    m.attack     = d.get("attack",     m.attack)
    return m

def get_wild_pool(rarity_filter=None):
    pool = list(ALL_MOONIES_DICT.values())
    if rarity_filter:
        pool = [m for m in pool if m.rarity in rarity_filter]
    return pool or list(ALL_MOONIES_DICT.values())

# ── UI helpers ─────────────────────────────────────────────────────────────────
def draw_rounded_rect(surf, color, rect, r=12, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=r)

def draw_text(surf, txt, font, color, x, y, center=False, shadow=False):
    if shadow:
        s = font.render(txt, True, (0,0,0))
        surf.blit(s, (x+2 if not center else x - s.get_width()//2 + 2, y+2))
    rendered = font.render(txt, True, color)
    if center:
        surf.blit(rendered, (x - rendered.get_width()//2, y))
    else:
        surf.blit(rendered, (x, y))
    return rendered.get_height()

def draw_hp_bar(surf, x, y, w, h, hp, max_hp, label=True):
    pct = max(0, hp / max_hp) if max_hp > 0 else 0
    color = C_GREEN if pct > 0.5 else C_YELLOW if pct > 0.25 else C_RED
    pygame.draw.rect(surf, (60,60,60), (x, y, w, h), border_radius=4)
    if pct > 0:
        pygame.draw.rect(surf, color, (x, y, int(w*pct), h), border_radius=4)
    pygame.draw.rect(surf, C_WHITE, (x, y, w, h), 1, border_radius=4)
    if label:
        draw_text(surf, f"{hp}/{max_hp}", F_TINY, C_WHITE, x + w + 6, y - 1)

def wrap_text(text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_type_badge(surf, type_name, x, y):
    color = TYPE_COLORS.get(type_name, (150,150,150))
    r = pygame.Rect(x, y, 64, 18)
    pygame.draw.rect(surf, color, r, border_radius=9)
    draw_text(surf, type_name, F_TINY, C_WHITE, x + 32, y + 2, center=True, shadow=True)

# ── Moonie card renderer ───────────────────────────────────────────────────────
def draw_moonie_card(surf, moonie_obj, x, y, w=200, h=240, selected=False, flip=False):
    r_color = moonie_obj.get_rarity_color()
    border = 3 if selected else 1
    border_col = C_YELLOW if selected else (80, 80, 100)
    draw_rounded_rect(surf, C_PANEL, (x, y, w, h), 14, border, border_col)
    if selected:
        glow = pygame.Surface((w+8, h+8), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*C_YELLOW, 60), (0,0,w+8,h+8), border_radius=16)
        surf.blit(glow, (x-4, y-4))
    pygame.draw.rect(surf, r_color, (x, y, w, 8), border_radius=14)
    img = load_img(moonie_obj.image, (w-20, h-100))
    if flip:
        img = pygame.transform.flip(img, True, False)
    surf.blit(img, (x+10, y+14))
    draw_text(surf, moonie_obj.name, F_SMALL, C_WHITE, x + w//2, y + h - 78, center=True, shadow=True)
    types = moonie_obj.types
    tx = x + w//2 - (len(types)*34)
    for t in types:
        draw_type_badge(surf, t, tx, y + h - 58)
        tx += 68
    draw_text(surf, f"Lv {moonie_obj.level}", F_TINY, C_GRAY, x + 6, y + h - 32)
    draw_hp_bar(surf, x + 6, y + h - 18, w - 12, 8, moonie_obj.current_hp, moonie_obj.max_hp, label=False)

# ── Particle system ────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, vx=None, vy=None, life=40, size=6):
        self.x, self.y = x, y
        self.color = color
        self.vx = vx if vx is not None else random.uniform(-3, 3)
        self.vy = vy if vy is not None else random.uniform(-4, 1)
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surf):
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surf.blit(s, (int(self.x)-self.size, int(self.y)-self.size))

particles = []

def add_particles(x, y, color, n=20, **kw):
    for _ in range(n):
        particles.append(Particle(x, y, color, **kw))

def update_particles(surf):
    for p in particles[:]:
        p.update()
        p.draw(surf)
        if p.life <= 0:
            particles.remove(p)

# ── Shake effect ───────────────────────────────────────────────────────────────
shake_timer = 0
def shake():
    global shake_timer
    shake_timer = 10

def get_shake_offset():
    if shake_timer > 0:
        return (random.randint(-4,4), random.randint(-4,4))
    return (0, 0)

# ── Notification system ────────────────────────────────────────────────────────
notifications = []

def notify(text, color=C_WHITE, duration=120):
    notifications.append({"text": text, "color": color, "t": duration, "max": duration})

def draw_notifications(surf):
    y = 20
    for n in notifications[:]:
        alpha = int(255 * n["t"] / n["max"])
        s = F_MED.render(n["text"], True, n["color"])
        bg = pygame.Surface((s.get_width()+20, s.get_height()+8), pygame.SRCALPHA)
        bg.fill((0,0,0,min(200, alpha)))
        surf.blit(bg, (SW//2 - bg.get_width()//2, y))
        surf.blit(s, (SW//2 - s.get_width()//2, y + 4))
        n["t"] -= 1
        if n["t"] <= 0:
            notifications.remove(n)
        y += s.get_height() + 12

# ── Entwicklungsstein-Auswahl-Screen ──────────────────────────────────────────
class SteinEvoSelectScreen:
    """
    Shown when the player uses an Entwicklungsstein on a Pokémon.
    Lets them pick WHICH evolution to trigger (if multiple) and confirms.
    """
    def __init__(self, moonie_obj, save_data, team):
        self.mon        = moonie_obj
        self.save       = save_data
        self.team       = team
        self.sel        = 0
        self.anim_t     = 0
        self.result     = None   # None | evo_name (string to evolve into)
        # Build list of possible evolutions
        nxt = moonie_obj.nextEvolution
        if isinstance(nxt, list):
            self.options = [n for n in nxt if n in ALL_MOONIES_DICT]
        elif isinstance(nxt, str) and nxt in ALL_MOONIES_DICT:
            self.options = [nxt]
        else:
            self.options = []

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key
        n = max(1, len(self.options))
        if k in (pygame.K_ESCAPE, pygame.K_x):
            return "cancel"
        elif k in (pygame.K_LEFT, pygame.K_a):
            self.sel = (self.sel - 1) % n
        elif k in (pygame.K_RIGHT, pygame.K_d):
            self.sel = (self.sel + 1) % n
        elif k in (pygame.K_UP, pygame.K_w):
            # Jump back one full page
            self.sel = max(0, self.sel - self.PER_PAGE)
        elif k in (pygame.K_DOWN, pygame.K_s):
            # Jump forward one full page
            self.sel = min(n - 1, self.sel + self.PER_PAGE)
        elif k in (pygame.K_RETURN, pygame.K_z):
            if self.options:
                self.result = self.options[self.sel]
                return "confirm"
        return None

    # Cards shown per page — fixed width of 120px each, 8 fit comfortably on 1200px wide screen
    PER_PAGE = 8
    CARD_W   = 120
    CARD_H   = 180

    def draw(self, surf):
        self.anim_t += 1
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surf.blit(overlay, (0, 0))

        pw, ph = SW - 40, 460
        px, py = 20, SH//2 - ph//2

        pulse = abs(math.sin(self.anim_t * 0.06))
        bc = (int(100+120*pulse), int(180+75*pulse), 255)
        draw_rounded_rect(surf, (14, 18, 40), (px, py, pw, ph), 16, 3, bc)

        # Header
        stein_icon = item_icon("entwicklungsstein", 36)
        if stein_icon:
            surf.blit(stein_icon, (px + 14, py + 12))
        draw_text(surf, "💎 Entwicklungsstein einsetzen", F_BIG, C_STEIN, SW//2, py + 14, center=True, shadow=True)
        draw_text(surf, f"Wähle die Entwicklung für {self.mon.name}:", F_MED, C_WHITE, SW//2, py + 52, center=True)

        if not self.options:
            draw_text(surf, "Dieses Pokémon kann sich nicht entwickeln!", F_MED, C_RED, SW//2, py + 180, center=True)
            draw_text(surf, "[ ESC ] Abbrechen", F_SMALL, C_GRAY, SW//2, py + ph - 30, center=True)
            return

        # Pagination
        total    = len(self.options)
        per_page = self.PER_PAGE
        page     = self.sel // per_page
        pages    = max(1, (total + per_page - 1) // per_page)
        start    = page * per_page
        end      = min(start + per_page, total)
        visible  = self.options[start:end]

        cw = self.CARD_W
        ch = self.CARD_H
        gap = (pw - 32) // per_page  # distribute evenly
        cards_x = px + 16

        for i, evo_name in enumerate(visible):
            global_idx = start + i
            sel = (global_idx == self.sel)
            m   = ALL_MOONIES_DICT.get(evo_name)
            cx  = cards_x + i * gap
            cy  = py + 82

            bg  = (30, 60, 100) if sel else (22, 28, 50)
            bdr = C_STEIN if sel else (50, 60, 90)
            draw_rounded_rect(surf, bg, (cx, cy, cw, ch), 10, 3 if sel else 1, bdr)

            if sel:
                glow = pygame.Surface((cw+10, ch+10), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*C_STEIN, int(40+40*pulse)), (0,0,cw+10,ch+10), border_radius=13)
                surf.blit(glow, (cx-5, cy-5))

            img_size = max(1, cw - 16)   # never below 1
            if m:
                img = load_img(m.image, (img_size, img_size))
                surf.blit(img, (cx + 8, cy + 6))
            # Name
            short = evo_name if len(evo_name) <= 10 else evo_name[:9] + "."
            draw_text(surf, short, F_TINY, C_YELLOW if sel else C_WHITE,
                      cx + cw//2, cy + img_size + 10, center=True, shadow=True)
            # Type badges (tiny)
            if m:
                tbx = cx + cw//2 - len(m.types) * 20
                for t in m.types:
                    tc = TYPE_COLORS.get(t, (150,150,150))
                    pygame.draw.rect(surf, tc, (tbx, cy + img_size + 26, 38, 11), border_radius=5)
                    draw_text(surf, t[:4], F_TINY, C_WHITE, tbx+19, cy + img_size + 27, center=True)
                    tbx += 42
                draw_text(surf, f"Ang:{m.attack}", F_TINY, C_GRAY,
                          cx + cw//2, cy + img_size + 42, center=True)

        # Page indicator + nav hint
        hint = f"◄ ►  wählen   Seite {page+1}/{pages}   ENTER bestätigen   ESC abbrechen"
        draw_text(surf, hint, F_TINY, C_GRAY, SW//2, py + ph - 22, center=True)

        draw_notifications(surf)


# ── Stein-Anwenden-Picker: Welches Pokémon soll den Stein bekommen? ───────────
class SteinMonPickScreen:
    """Let the player pick which team member to apply the Entwicklungsstein to."""

    def __init__(self, team, save_data):
        self.team  = team
        self.save  = save_data
        self.sel   = 0
        self.anim_t = 0

    def _can_evolve(self, m):
        """True if this mon has a valid next evolution."""
        nxt = m.nextEvolution if hasattr(m, 'nextEvolution') else None
        if not nxt:
            return False
        if isinstance(nxt, list):
            return any(n in ALL_MOONIES_DICT for n in nxt)
        return nxt in ALL_MOONIES_DICT

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key
        if k in (pygame.K_ESCAPE, pygame.K_x):
            return "cancel"
        if k in (pygame.K_UP, pygame.K_w):
            self.sel = max(0, self.sel - 1)
        elif k in (pygame.K_DOWN, pygame.K_s):
            self.sel = min(len(self.team) - 1, self.sel + 1)
        elif k in (pygame.K_RETURN, pygame.K_z):
            if self.sel < len(self.team):
                m = self.team[self.sel]
                if self._can_evolve(m):
                    return ("picked", self.sel)
                else:
                    notify(f"{m.name} kann sich nicht (weiter) entwickeln!", C_RED, 120)
        return None

    def draw(self, surf):
        self.anim_t += 1
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surf.blit(overlay, (0, 0))

        pw, ph = 560, min(120 + len(self.team) * 72 + 40, 560)
        px, py = SW//2 - pw//2, SH//2 - ph//2
        draw_rounded_rect(surf, (14, 18, 40), (px, py, pw, ph), 16, 3, C_STEIN)

        stein_icon = item_icon("entwicklungsstein", 36)
        if stein_icon:
            surf.blit(stein_icon, (px + 20, py + 14))
        draw_text(surf, "Wen soll der Stein treffen?", F_BIG, C_STEIN,
                  px + pw//2 + 10, py + 16, center=True, shadow=True)

        for i, m in enumerate(self.team):
            sel = (i == self.sel)
            can = self._can_evolve(m)
            iy  = py + 66 + i * 68
            bg  = (40, 65, 110) if sel else (22, 28, 46)
            bdr = C_STEIN if sel else ((60, 100, 60) if can else (80, 50, 50))
            draw_rounded_rect(surf, bg, (px+14, iy, pw-28, 60), 10, 2 if sel else 1, bdr)

            img = load_img(m.image, (44, 44))
            surf.blit(img, (px + 22, iy + 8))
            draw_text(surf, m.name, F_MED, C_WHITE, px + 76, iy + 8)
            draw_text(surf, f"Lv {m.level}", F_TINY, C_GRAY, px + 76, iy + 32)

            if can:
                nxt = m.nextEvolution
                if isinstance(nxt, list):
                    nxt_str = " / ".join(nxt)
                else:
                    nxt_str = str(nxt)
                draw_text(surf, f"→ {nxt_str}", F_TINY, C_STEIN, px + 180, iy + 32)
            else:
                draw_text(surf, "Keine Entwicklung", F_TINY, C_GRAY, px + 180, iy + 32)

            draw_hp_bar(surf, px + pw - 160, iy + 24, 130, 8, m.current_hp, m.max_hp, label=False)

        draw_text(surf, "↑↓ wählen   ENTER auswählen   ESC abbrechen",
                  F_TINY, C_GRAY, px + pw//2, py + ph - 20, center=True)
        draw_notifications(surf)


# ── Flashcard mini-game ────────────────────────────────────────────────────────
class FlashcardGame:
    _save_ref = None

    def __init__(self, cards, reward_callback, n=3):
        self.cards = cards
        self.reward_cb = reward_callback
        self.n_required = n
        self.answered = 0
        self.correct = 0
        self.card = None
        self.state = "question"
        self.input_text = ""
        self.feedback = ""
        self.feedback_color = C_WHITE
        self.done = False
        self.pick_card()
        self.cursor_blink = 0

    def pick_card(self):
        today = _today_str()
        # Priority: overdue/new > known but due > known not due
        overdue = [c for c in self.cards
                   if not c.get("known") or c.get("due","") <= today]
        pool = overdue if overdue else self.cards
        # Weight by ease: lower ease = picked more often
        weights = [max(0.5, 3.5 - c.get("ease", 2.5)) for c in pool]
        total_w = sum(weights)
        r = random.uniform(0, total_w)
        cumul = 0
        self.card = pool[0]
        for c, w in zip(pool, weights):
            cumul += w
            if r <= cumul:
                self.card = c
                break
        self.state = "question"
        self.input_text = ""
        self.feedback = ""

    def handle_event(self, event):
        if self.state == "question":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state = "answer"
        elif self.state == "answer":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.check_answer()
                elif event.key == pygame.K_ESCAPE:
                    self.feedback = "Übersprungen!"
                    self.feedback_color = C_GRAY
                    self.state = "result"
                elif len(self.input_text) < 200:
                    self.input_text += event.unicode
        elif self.state == "result":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.answered += 1
                if self.answered >= self.n_required:
                    self.done = True
                    self.reward_cb(self.correct, self.n_required)
                else:
                    self.pick_card()

    def check_answer(self):
        if not self.card:
            return
        user = self.input_text.strip().lower()
        answer = self.card["a"].lower()
        key_words = [w for w in answer.split() if len(w) > 3]
        matches = sum(1 for w in key_words if w in user)
        threshold = max(1, len(key_words) // 2)
        correct = (matches >= threshold or user in answer or answer in user)
        today = _today_str()
        c = self.card
        if correct:
            # SM-2 algorithm
            q = 4  # quality: 4=correct, 5=easy
            ease = max(1.3, c.get("ease", 2.5) + 0.1 - (5-q)*(0.08+(5-q)*0.02))
            reps = c.get("reps", 0) + 1
            interval = 1 if reps == 1 else (6 if reps == 2 else
                       max(1, round(c.get("interval",1) * ease)))
            interval = min(interval, 30)  # cap at 30 days
            due_date = (_dt.date.today() + _dt.timedelta(days=interval)).isoformat()
            c["ease"] = ease; c["reps"] = reps; c["interval"] = interval
            c["due"] = due_date; c["known"] = True
            c["streak"] = c.get("streak", 0) + 1
            interval_txt = f"  (nächste Review: {interval}d)" if interval > 1 else "  (morgen wieder)"
            self.feedback = "✓ Richtig! " + c["a"] + interval_txt
            self.feedback_color = C_GREEN
            self.correct += 1
            add_particles(SW//2, 300, (80,220,100), n=30)
            if FlashcardGame._save_ref is not None:
                s = FlashcardGame._save_ref
                s["cards_correct_total"] = s.get("cards_correct_total", 0) + 1
                s["cards_current_streak"] = s.get("cards_current_streak", 0) + 1
                if s["cards_current_streak"] > s.get("cards_best_streak", 0):
                    s["cards_best_streak"] = s["cards_current_streak"]
        else:
            # Wrong: reset interval, lower ease
            c["ease"] = max(1.3, c.get("ease", 2.5) - 0.3)
            c["interval"] = 0; c["due"] = today; c["reps"] = 0
            c["streak"] = 0; c["known"] = False
            self.feedback = "✗ Falsch. Antwort: " + c["a"]
            self.feedback_color = C_RED
            if FlashcardGame._save_ref is not None:
                FlashcardGame._save_ref["cards_current_streak"] = 0
        self.state = "result"

    def draw(self, surf):
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((10, 12, 20, 230))
        surf.blit(overlay, (0, 0))
        pw, ph = 780, 440
        px, py = SW//2 - pw//2, SH//2 - ph//2
        draw_rounded_rect(surf, C_PANEL, (px, py, pw, ph), 18, 2, C_BLUE)
        hdr = "📚 Lernkarte – Frage" if self.state == "question" else \
              "📝 Deine Antwort" if self.state == "answer" else "✅ Ergebnis"
        draw_text(surf, hdr, F_BIG, C_YELLOW, SW//2, py+18, center=True, shadow=True)
        prog = f"Frage {self.answered+1} / {self.n_required}   Richtig: {self.correct}"
        draw_text(surf, prog, F_SMALL, C_GRAY, SW//2, py+60, center=True)
        if self.card:
            q_lines = wrap_text(self.card["q"], F_MED, pw-60)
            qy = py + 95
            for line in q_lines:
                draw_text(surf, line, F_MED, C_WHITE, SW//2, qy, center=True)
                qy += 30
            if self.state == "question":
                draw_text(surf, "[ ENTER ] um Antwort einzugeben", F_SMALL, C_GRAY, SW//2, py+ph-60, center=True)
            elif self.state == "answer":
                ify = qy + 20
                draw_rounded_rect(surf, C_DARK, (px+30, ify, pw-60, 44), 8, 2, C_BLUE)
                self.cursor_blink = (self.cursor_blink+1) % 60
                cursor = "|" if self.cursor_blink < 30 else " "
                inp_lines = wrap_text(self.input_text + cursor, F_MED, pw-80)
                iy = ify + 8
                for ln in inp_lines[:2]:
                    draw_text(surf, ln, F_MED, C_WHITE, px+40, iy)
                    iy += 26
                draw_text(surf, "[ ENTER ] Bestätigen  [ ESC ] Überspringen", F_TINY, C_GRAY, SW//2, py+ph-35, center=True)
            elif self.state == "result":
                fb_lines = wrap_text(self.feedback, F_MED, pw-60)
                fy = qy + 25
                for line in fb_lines:
                    draw_text(surf, line, F_MED, self.feedback_color, SW//2, fy, center=True)
                    fy += 30
                draw_text(surf, "[ ENTER ] Weiter", F_SMALL, C_GRAY, SW//2, py+ph-35, center=True)
        update_particles(surf)

# ── Battle system ──────────────────────────────────────────────────────────────
class Battle:
    STATES = ["intro","player_turn","enemy_turn","catch_anim","flashcard","result","run","switch_pick"]

    def __init__(self, player_team, enemy_data, wild_moonie=None, flashcards=None, is_wild=False):
        self.player_team  = player_team
        self.enemy_data   = enemy_data
        self.wild_moonie  = wild_moonie
        self.flashcards   = flashcards or []
        self.is_wild      = is_wild
        self.state        = "intro"
        self.log          = []
        self.log_timer    = 0
        self.result       = None
        self.player_idx   = 0
        self.enemy_moonies= []
        self.enemy_idx    = 0
        self.catch_result = None
        self.catch_anim_t = 0
        self.flash_game   = None
        self.flash_pending= False
        self.shake_enemy  = 0
        self.shake_player = 0
        self.anim_t       = 0
        self.turn_cooldown= 0
        self.selected_btn = 0
        self.balls_used    = 0
        self.xp_gained     = 0
        self.coins_reward  = 0
        self.andreas_anim_t = 0
        self.andreas_audio_done = False
        self.save_data_ref = {}
        self.last_effectiveness = (1.0, "", C_WHITE)
        self.pending_evolutions = []
        self.item_pick_sel  = 0
        self.switch_pick_sel= 0
        self.switch_forced  = False  # True = forced switch after faint
        self.raid_cards_needed = 0
        self.raid_cards_answered = 0
        self.overworld_ref = None
        self.energy_drink_used    = False
        self.energy_boost_rounds  = 0
        self.energy_boost_actions = 0
        self.energy_down_phase    = False
        self._hit_flash           = 0
        self._hit_flash_col       = (255,80,80)
        self._player_hit_flash    = 0
        # Attack jump animation
        self._player_jump         = 0   # frames remaining for forward lunge
        self._enemy_jump          = 0
        self._atk_particles_t     = 0
        # Status cure
        self._status_msg_t        = 0
        self._status_msg          = ""
        self._status_msg_col      = C_WHITE
        self._setup_enemies()
        self.push_log(f"Ein wildes {self.enemy_moonies[0].name} erscheint!" if is_wild
                      else f"Trainer {enemy_data.name} möchte kämpfen!")

    def _setup_enemies(self):
        if self.is_wild and self.wild_moonie:
            self.enemy_moonies = [self.wild_moonie.clone_for_battle()]
            return
        if not self.enemy_data:
            self.enemy_moonies = [get_moonie("Taubsi")]
            return
        en = self.enemy_data
        strength = getattr(en, 'strenght', 2)
        for name in en.moonies:
            m = get_moonie(name)
            m.level = max(1, strength * 8 + random.randint(-3, 3))
            m.max_hp = m.max_hp + m.level * 2
            m.attack = m.attack + m.level
            m.current_hp = m.max_hp
            m.status = None; m.status_turns = 0
            self.enemy_moonies.append(m)
        max_extra = 6 - len(self.enemy_moonies)
        if max_extra > 0:
            n_extra = random.randint(0, max_extra)
            trainer_types = set(en.pokemonTypes)
            pool = [m for m in ALL_MOONIES_DICT.values()
                    if any(t in trainer_types for t in m.types)
                    and m.name not in en.moonies]
            if not pool:
                pool = list(ALL_MOONIES_DICT.values())
            for _ in range(n_extra):
                pick = random.choice(pool).clone_for_battle()
                pick.level = max(1, strength * 8 + random.randint(-4, 4))
                pick.max_hp = pick.max_hp + pick.level * 2
                pick.attack = pick.attack + pick.level
                pick.current_hp = pick.max_hp
                pick.status = None; pick.status_turns = 0
                self.enemy_moonies.append(pick)
        if not self.enemy_moonies:
            self.enemy_moonies = [get_moonie("Taubsi")]

    @property
    def player_moonie(self):
        for m in self.player_team[self.player_idx:]:
            if m.is_alive():
                return m
        return self.player_team[0]

    @property
    def enemy_moonie(self):
        return self.enemy_moonies[self.enemy_idx] if self.enemy_idx < len(self.enemy_moonies) else None

    def push_log(self, txt):
        self.log.append(txt)
        if len(self.log) > 5:
            self.log.pop(0)
        self.log_timer = 90

    def handle_event(self, event, save_data):
        self.save_data_ref = save_data
        if self.flash_game and not self.flash_game.done:
            self.flash_game.handle_event(event)
            if self.flash_game.done:
                self.flash_game = None
                self.state = "player_turn"
                notify("Lernkarte beantwortet! +XP Bonus", C_GREEN)
            return
        if event.type != pygame.KEYDOWN or self.turn_cooldown > 0:
            return
        if self.state in ("done", "andreas_steal"):
            return
        self.save_data_ref = save_data
        if self.state == "intro":
            self.state = "player_turn"
        elif self.state == "item_pick":
            items = self._get_usable_items(save_data)
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                self.state = "player_turn"
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.item_pick_sel = max(0, self.item_pick_sel - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.item_pick_sel = min(len(items)-1, self.item_pick_sel + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                if items:
                    self._use_item(items[self.item_pick_sel], save_data)
        elif self.state == "switch_pick":
            if event.type == pygame.KEYDOWN:
                alive_idx = [i for i,m in enumerate(self.player_team) if m.is_alive() and i != self.player_idx]
                if not alive_idx:
                    self.state = "player_turn"; return None
                k = event.key
                if k == pygame.K_UP:
                    pos = alive_idx.index(self.switch_pick_sel) if self.switch_pick_sel in alive_idx else 0
                    self.switch_pick_sel = alive_idx[(pos - 1) % len(alive_idx)]
                elif k == pygame.K_DOWN:
                    pos = alive_idx.index(self.switch_pick_sel) if self.switch_pick_sel in alive_idx else 0
                    self.switch_pick_sel = alive_idx[(pos + 1) % len(alive_idx)]
                elif k in (pygame.K_RETURN, pygame.K_z):
                    new_idx = self.switch_pick_sel
                    old_name = self.player_moonie.name
                    self.player_idx = new_idx
                    new_m = self.player_team[new_idx]
                    self.push_log(f"Zurück, {old_name}! Komm raus, {new_m.name}!")
                    if not self.switch_forced:
                        self._enemy_turn()
                    self.state = "player_turn"
                    self.switch_forced = False
                elif k == pygame.K_ESCAPE and not self.switch_forced:
                    self.state = "player_turn"
            return None
        elif self.state == "ball_pick":
            balls = self._get_available_balls(save_data)
            if event.key in (pygame.K_ESCAPE, pygame.K_x):
                self.state = "player_turn"
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.ball_pick_sel = max(0, self.ball_pick_sel - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.ball_pick_sel = min(len(balls)-1, self.ball_pick_sel + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                if balls:
                    self._throw_ball(balls[self.ball_pick_sel], save_data)
        elif self.state == "player_turn":
            # 5-button layout: top row [0,1,2], bottom row [3,4]
            NAV = {
                0: {"left":2,"right":1,"down":3},
                1: {"left":0,"right":2,"down":4},
                2: {"left":1,"right":0,"down":4},
                3: {"left":4,"right":4,"up":0,"down":3},
                4: {"left":3,"right":3,"up":1,"down":4},
            }
            nav = NAV.get(self.selected_btn, {})
            if event.key == pygame.K_LEFT:
                self.selected_btn = nav.get("left", self.selected_btn)
            elif event.key == pygame.K_RIGHT:
                self.selected_btn = nav.get("right", self.selected_btn)
            elif event.key == pygame.K_UP:
                self.selected_btn = nav.get("up", self.selected_btn)
            elif event.key == pygame.K_DOWN:
                self.selected_btn = nav.get("down", self.selected_btn)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_z:
                self._player_action(self.selected_btn, save_data)
        elif self.state == "result":
            if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_ESCAPE, pygame.K_SPACE):
                self.state = "done"

    def _player_action(self, btn, save_data):
        pm = self.player_moonie
        em = self.enemy_moonie
        if not em:
            self.state = "result"; self.result = "win"; return

        if btn == 0:  # Attack
            pm_status = getattr(pm, "status", None)
            if pm_status == "sleep":
                self.push_log(f"💤 {pm.name} schläft und kann nicht kämpfen!")
                self._enemy_turn(); return
            if pm_status == "paralyze" and random.random() < 0.30:
                self.push_log(f"⚡ {pm.name} ist gelähmt und kann sich nicht bewegen!")
                self._enemy_turn(); return
            if pm_status == "freeze":
                self.push_log(f"❄ {pm.name} ist eingefroren und kann sich nicht bewegen!")
                if random.random() < 0.20: pm.status = None; self.push_log(f"❄ ...aber taut auf!")
                else: self._enemy_turn(); return
            if self.energy_down_phase:
                self.push_log(f"⚠ {pm.name} ist erschöpft! Keine Aktion möglich.")
                self.energy_down_phase = False
                self.turn_cooldown = 30
                self._enemy_turn()
                return
            is_raid = getattr(self, '_is_raid', False)
            if is_raid:
                self._raid_attack_count = getattr(self, '_raid_attack_count', 0) + 1
                show_card = (self._raid_attack_count % 2 == 1) and bool(self.flashcards)
            else:
                show_card = bool(self.flashcards) and random.random() < 0.4
            if show_card:
                def reward(correct, total):
                    bonus = correct * 5
                    leveled, evos = pm.gain_xp(bonus)
                    if leveled: notify(f"{pm.name} Level {pm.level}! +{bonus} Bonus-XP", C_YELLOW)
                    else: notify(f"+{bonus} Bonus-XP für {correct}/{total} richtige!", C_YELLOW)
                    if is_raid and correct > 0:
                        self.raid_cards_answered = getattr(self, 'raid_cards_answered', 0) + correct
                        if self.overworld_ref:
                            self.overworld_ref.raid["cards_answered"] = self.raid_cards_answered
                self.flash_game = FlashcardGame(self.flashcards, reward, n=1)
                self.push_log("Lernfrage!" if not is_raid else f"📚 Raid-Lernkarte!")
                return
            dmg, mult = pm.calculate_damage(em)
            # Friendship damage bonus
            fs_mult = friendship_dmg_bonus(self.save_data_ref, pm.name) if self.save_data_ref else 1.0
            dmg = max(1, int(dmg * fs_mult))
            em.take_damage(dmg)
            self.shake_enemy = 14
            self._player_jump = 12  # lunge forward animation
            # Attack particles based on player type
            pm_types = getattr(pm, "types", ["Normal"])
            type_cols = {
                "Feuer":(255,120,30),"Wasser":(60,150,255),"Elektro":(255,230,40),
                "Pflanze":(80,220,80),"Eis":(150,230,255),"Psycho":(255,80,200),
                "Geist":(140,60,200),"Kampf":(220,80,40),"Dunkel":(80,60,120),
                "Drache":(100,60,255),"Fee":(255,160,220),"Gift":(180,60,220),
            }
            p_col = type_cols.get(pm_types[0], (220,60,60))
            # Big burst at enemy position + trailing particles
            add_particles(700, 200, p_col, n=40)
            add_particles(680, 230, (255,255,255), n=12)
            # Hit flash on enemy sprite area
            self._hit_flash = 14
            self._hit_flash_col = p_col
            eff_lbl, eff_col = effectiveness_label(mult) if mult != 1.0 else ("", None)
            log_msg = f"{pm.name} greift an! -{dmg} HP"
            if eff_lbl: log_msg += f"  {eff_lbl}"
            self.push_log(log_msg)
            self.last_effectiveness = (mult, eff_lbl, eff_col or C_WHITE)
            # Player attack can inflict status based on type
            if not getattr(em, "status", None):
                if "Feuer"   in pm_types: try_inflict_status(em, "burn",     self.push_log, 0.18)
                elif "Gift"  in pm_types: try_inflict_status(em, "poison",   self.push_log, 0.22)
                elif "Psycho" in pm_types: try_inflict_status(em, "sleep",   self.push_log, 0.10)
                elif "Elektro" in pm_types: try_inflict_status(em, "paralyze", self.push_log, 0.18)
                elif "Eis"   in pm_types: try_inflict_status(em, "freeze",   self.push_log, 0.10)
            if not em.is_alive():
                self._enemy_faint()
                return
            if self.energy_boost_rounds > 0 and self.energy_boost_actions > 0:
                self.energy_boost_actions -= 1
                self.energy_boost_rounds  -= 1
                remaining = self.energy_boost_rounds
                if remaining > 0:
                    self.push_log(f"⚡ Bonus-Angriff! Noch {remaining} Boost-Runde(n)!")
                else:
                    self.push_log("⚡ Letzter Boost-Angriff! Nächste Runde: Downphase!")
                    self.energy_down_phase = True
                self.turn_cooldown = 25
                self.energy_boost_actions = 1
                return
            self.turn_cooldown = 40
            self._enemy_turn()

        elif btn == 1:  # Ball picker
            has_balls  = save_data.get("balls", 0) > 0
            has_master = save_data.get("master_balls", 0) > 0
            if not has_balls and not has_master:
                self.push_log("Keine Pokébälle mehr!")
                return
            if not self.is_wild:
                self.push_log("Du kannst keine Trainer-Moonies fangen!")
                return
            self.state = "ball_pick"
            self.ball_pick_sel = 0

        elif btn == 2:  # Item bag
            self.state = "item_pick"
            self.item_pick_sel = 0

        elif btn == 3:  # Switch team
            alive_team = [m for m in self.player_team if m.is_alive()]
            if len(alive_team) > 1:
                self.state = "switch_pick"
                self.switch_pick_sel = next(
                    (i for i,m in enumerate(self.player_team) if m.is_alive() and m != pm), 0)
                self.switch_forced = False
            else:
                self.push_log("Kein anderes Pokémon verfügbar!")

        elif btn == 4:  # Flee
            if self.is_wild:
                if random.random() < 0.6:
                    self.state = "result"; self.result = "run"
                    self.push_log("Du bist geflohen!")
                else:
                    self.push_log("Flucht fehlgeschlagen!")
                    self._enemy_turn()
            else:
                self.push_log("Aus Trainer-Kämpfen kann man nicht fliehen!")

    def _get_available_balls(self, save_data):
        balls = []
        if save_data.get("master_balls", 0) > 0:
            balls.append(("Meisterball", "100% Fangchance!", "master_balls", 1.0))
        if save_data.get("balls", 0) > 0:
            balls.append(("Pokéball", "Normaler Ball", "balls", None))
        return balls

    def _throw_ball(self, ball_entry, save_data):
        name, desc, key, catch_override = ball_entry
        em = self.enemy_moonie
        if not em or not em.is_alive():
            return
        self.state = "player_turn"
        save_data[key] -= 1
        self.balls_used += 1
        if key == "balls" and random.random() < 0.08:
            self.state = "andreas_steal"
            self.andreas_anim_t = 0
            self.push_log("Psycho Andreas taucht auf!!!")
            return
        if catch_override is not None:
            chance = catch_override
        else:
            hp_factor = 0.3 + 0.7 * (1 - em.current_hp / max(1, em.max_hp))
            base = max(0.35, getattr(em, "catch_rate", 0.35))
            chance = min(0.95, base * hp_factor * 1.6)
        self.state = "catch_anim"
        self.catch_anim_t = 0
        self.catch_result = (random.random() < chance)
        self._catch_ball_key = "master_balls" if key == "master_balls" else "balls"
        self.push_log(f"{name} geworfen! ({save_data.get(key,0)} übrig)")

    def _enemy_faint(self):
        em = self.enemy_moonie
        add_particles(650, 250, (255,200,50), n=40, size=8)
        self.xp_gained += em.level * 8
        self.coins_reward += em.level * (8 if not self.is_wild else 3)
        self.push_log(f"{em.name} wurde besiegt!")
        self.enemy_idx += 1
        if self.enemy_idx >= len(self.enemy_moonies):
            self.state = "result"; self.result = "win"
            pm = self.player_moonie
            boosted_xp, streak_pct = apply_streak_xp_bonus(self.save_data_ref, self.xp_gained)
            if streak_pct > 0: notify(f"🔥 Streak-Bonus: +{streak_pct}% XP!", C_ORANGE, 120)
            self.xp_gained = boosted_xp
            leveled, evos = pm.gain_xp(self.xp_gained)
            if leveled:
                notify(f"{pm.name} ist auf Lv {pm.level} aufgestiegen!", C_YELLOW)
            self.pending_evolutions = evos
        else:
            self.push_log(f"Nächstes Moonie: {self.enemy_moonies[self.enemy_idx].name}!")

    def _enemy_turn(self):
        em = self.enemy_moonie
        pm = self.player_moonie
        if not em or not pm: return
        # Enemy sleep/paralyze/freeze check
        em_st = getattr(em, "status", None)
        if em_st == "sleep":
            self.push_log(f"💤 {em.name} schläft — kein Angriff!")
            apply_status_end_of_turn(em, self.push_log)
            apply_status_end_of_turn(pm, self.push_log)
            return
        if em_st == "paralyze" and random.random() < 0.30:
            self.push_log(f"⚡ {em.name} ist gelähmt!")
            apply_status_end_of_turn(em, self.push_log)
            apply_status_end_of_turn(pm, self.push_log)
            return
        if em_st == "freeze":
            if random.random() < 0.20:
                em.status = None
                self.push_log(f"❄ {em.name} taut auf!")
            else:
                self.push_log(f"❄ {em.name} ist eingefroren!")
                apply_status_end_of_turn(pm, self.push_log)
                return
        dmg, mult = em.calculate_damage(pm)
        # Burn reduces attacker dmg
        if em_st == "burn":
            dmg = max(1, int(dmg * 0.75))
        pm.take_damage(dmg)
        self.shake_player = 14
        self._enemy_jump = 12  # enemy lunge animation
        em_types = getattr(em, "types", ["Normal"])
        from_type_cols = {
            "Feuer":(255,120,30),"Wasser":(60,150,255),"Elektro":(255,230,40),
            "Pflanze":(80,220,80),"Eis":(150,230,255),"Psycho":(255,80,200),
        }
        ep_col = from_type_cols.get(em_types[0] if em_types else "Normal", (220,60,60))
        add_particles(240, 350, ep_col, n=28)
        add_particles(260, 380, (255,255,255), n=8)
        self._player_hit_flash = 10
        self.push_log(f"{em.name} greift an! -{dmg} HP")
        if self.save_data_ref: add_friendship(self.save_data_ref, pm.name, 1)
        # Chance to inflict status based on enemy type
        em_types = getattr(em, "types", [])
        if "Feuer" in em_types:   try_inflict_status(pm, "burn",     self.push_log, 0.20)
        if "Gift"  in em_types:   try_inflict_status(pm, "poison",   self.push_log, 0.25)
        if "Psycho" in em_types:  try_inflict_status(pm, "sleep",    self.push_log, 0.12)
        if "Elektro" in em_types: try_inflict_status(pm, "paralyze", self.push_log, 0.20)
        if "Eis"  in em_types:    try_inflict_status(pm, "freeze",   self.push_log, 0.12)
        # Status DoT on enemy
        if getattr(em, "status", None):
            apply_status_end_of_turn(em, self.push_log)
        # Status DoT on player
        if getattr(pm, "status", None):
            apply_status_end_of_turn(pm, self.push_log)
        if not pm.is_alive():
            self.energy_boost_rounds  = 0
            self.energy_boost_actions = 0
            self.energy_down_phase    = False
            alive = [m for m in self.player_team if m.is_alive()]
            if not alive:
                self.state = "result"; self.result = "lose"
                self.push_log("Alle deine Moonies sind besiegt!")
            else:
                if len(alive) > 1:
                    self.state = "switch_pick"
                    self.switch_pick_sel = self.player_team.index(alive[0])
                    self.switch_forced = True
                    self.push_log("Wähle dein nächstes Pokémon!")
                else:
                    self.player_idx = self.player_team.index(alive[0])
                    self.push_log(f"{alive[0].name} kämpft weiter!")

    def _get_usable_items(self, save_data):
        items = []
        if save_data.get("potions", 0) > 0:
            items.append(("Trank",        "+30 HP",    "potions",       30))
        if save_data.get("super_potions", 0) > 0:
            items.append(("Super Trank",  "+80 HP",    "super_potions", 80))
        if save_data.get("hyper_potions", 0) > 0:
            items.append(("Hyper Trank",  "+150 HP",   "hyper_potions", 150))
        if save_data.get("sonderbonbons", 0) > 0:
            items.append(("Sonderbonbon", "+1 Level",  "sonderbonbons", 0))
        if save_data.get("beleber", 0) > 0:
            items.append(("Beleber",      "½ HP beleben", "beleber",    -1))
        if save_data.get("redbull", 0) > 0 and not self.energy_drink_used:
            items.append(("Energy Drink", "3 Runden 2× Angriff", "redbull", -3))
        # Status cure: only show if player mon has a status
        pm = self.player_moonie
        pm_st = getattr(pm, "status", None) if pm else None
        if pm_st and save_data.get("antidot", 0) > 0 and pm_st == "poison":
            items.append(("Antidot",    "Heilt Vergiftung", "antidot",    "cure_poison"))
        if pm_st and save_data.get("awakener", 0) > 0 and pm_st == "sleep":
            items.append(("Wecker",     "Heilt Schlaf",     "awakener",   "cure_sleep"))
        if pm_st and save_data.get("burnheal", 0) > 0 and pm_st == "burn":
            items.append(("Brandheiler","Heilt Verbrennung","burnheal",   "cure_burn"))
        if pm_st and save_data.get("paralyzeheal", 0) > 0 and pm_st == "paralyze":
            items.append(("Paralyheiler","Heilt Lähmung",   "paralyzeheal","cure_paralyze"))
        if pm_st and save_data.get("iceheal", 0) > 0 and pm_st == "freeze":
            items.append(("Eisheilmittel","Heilt Einfrieren","iceheal",   "cure_freeze"))
        if pm_st and save_data.get("fullheal", 0) > 0:
            items.append(("Volltreffer", "Heilt alle Status", "fullheal",  "cure_all"))
        return items

    def _use_item(self, item, save_data):
        name, desc, key, heal = item
        pm = self.player_moonie
        save_data[key] -= 1
        if key == "redbull":
            if self.energy_drink_used:
                save_data[key] += 1
                self.push_log("Energy Drink bereits benutzt!")
                return
            self.energy_drink_used   = True
            self.energy_boost_rounds = 3
            self.energy_boost_actions = 1
            self.energy_down_phase   = False
            self.push_log("⚡ ENERGY BOOST! 3 Runden Doppel-Angriff!")
            notify("⚡ Energy Drink! 3 Runden × 2 Aktionen!", (255, 80, 0), 200)
            self.state = "player_turn"
            return
        elif key == "sonderbonbons":
            pm.level += 1
            pm.max_hp  = int(pm.max_hp  * 1.05) + 2
            pm.attack  = int(pm.attack  * 1.05) + 1
            pm.current_hp = min(pm.current_hp + 10, pm.max_hp)
            self.push_log(f"Sonderbonbon! {pm.name} ist jetzt Level {pm.level}!")
        elif key == "beleber":
            if pm.current_hp > 0:
                save_data[key] += 1
                self.push_log("Nur für bewusstlose Pokémon!")
                return
            pm.current_hp = max(1, pm.max_hp // 2)
            self.push_log(f"Beleber! {pm.name} mit {pm.current_hp} HP wiederbelebt!")
        elif key == "top_beleber":
            if pm.current_hp > 0:
                save_data[key] += 1
                self.push_log("Nur für bewusstlose Pokémon!")
                return
            pm.current_hp = pm.max_hp
            self.push_log(f"Top-Beleber! {pm.name} vollständig wiederbelebt!")
        elif isinstance(heal, str) and heal.startswith("cure_"):
            st_to_cure = heal.replace("cure_", "")
            if st_to_cure == "all":
                pm.status = None
                pm.status_turns = 0
                self.push_log(f"✨ {name}! {pm.name} ist wieder fit!")
            elif getattr(pm, "status", None) == st_to_cure or st_to_cure == "all":
                pm.status = None
                pm.status_turns = 0
                data = STATUS_DATA.get(st_to_cure, {})
                self.push_log(f"{data.get('icon','✨')} {name}! {pm.name} geheilt!")
            else:
                save_data[key] += 1
                self.push_log(f"{pm.name} hat keinen passenden Status!")
                return
        else:
            pm.heal(heal)
            self.push_log(f"{name} eingesetzt! +{heal} HP")
        self.state = "player_turn"
        self._enemy_turn()

    def update(self):
        global shake_timer
        if self.turn_cooldown > 0:
            self.turn_cooldown -= 1
        if self.log_timer > 0:
            self.log_timer -= 1
        if self.shake_enemy > 0:
            self.shake_enemy -= 1
        if self.shake_player > 0:
            self.shake_player -= 1
        if self._player_jump > 0:
            self._player_jump -= 1
        if self._enemy_jump > 0:
            self._enemy_jump -= 1
        if self._status_msg_t > 0:
            self._status_msg_t -= 1
        self.anim_t += 1

        if self.state == "andreas_steal":
            self.andreas_anim_t += 1
            if self.andreas_anim_t == 1:
                try:
                    snd = pygame.mixer.Sound(os.path.join(BASE, "assets/audio/haltStop.mp3"))
                    snd.play()
                    self._andreas_audio_len = int(snd.get_length() * 60) + 30
                except Exception:
                    self._andreas_audio_len = 150
            if self.andreas_anim_t >= getattr(self, '_andreas_audio_len', 150):
                em = self.enemy_moonie
                self.push_log(f"Psycho Andreas hat {em.name} weggeschnappt!")
                add_particles(SW//2, SH//2, (180,20,180), n=40)
                self.state = "result"; self.result = "andreas"

        elif self.state == "catch_anim":
            self.catch_anim_t += 1
            if self.catch_anim_t > 90:
                if self.catch_result:
                    em = self.enemy_moonie
                    self.push_log(f"{em.name} wurde gefangen!")
                    add_particles(SW//2, SH//2, (80,220,255), n=50)
                    self.state = "result"; self.result = "catch"
                else:
                    em = self.enemy_moonie
                    self.push_log(f"{em.name} ist ausgebrochen!")
                    self.state = "player_turn"
                    self._enemy_turn()

    def draw(self, surf):
        if self.flash_game and not self.flash_game.done:
            self.flash_game.draw(surf)
            return

        draw_rounded_rect(surf, (15, 18, 28), (0, 0, SW, 32), 0, 1, (50, 55, 70))
        hud_items = [
            ("↑↓←→ wählen", C_GRAY),
            ("ENTER/Z Aktion", C_GRAY),
            (f"🎯 {self.save_data_ref.get('balls',0) if hasattr(self,'save_data_ref') else '?'} Bälle", C_GREEN),
            (f"💊 {self.save_data_ref.get('potions',0) if hasattr(self,'save_data_ref') else '?'} / {self.save_data_ref.get('super_potions',0) if hasattr(self,'save_data_ref') else '?'} Tränke", (180,230,180)),
            (f"💰 {self.save_data_ref.get('coins',0) if hasattr(self,'save_data_ref') else '?'}", C_YELLOW),
        ]
        hx = 10
        for txt, col in hud_items:
            draw_text(surf, txt, F_TINY, col, hx, 9)
            hx += 175

        if getattr(self, '_is_raid', False):
            needed = getattr(self, 'raid_cards_needed', 0)
            answered = getattr(self, 'raid_cards_answered', 0)
            ok = answered >= needed
            rc = C_GREEN if ok else C_YELLOW
            draw_text(surf, f"📚 RAID: {answered}/{needed} Lernkarten", F_SMALL, rc, SW//2, 10, center=True, shadow=True)

        is_rocket  = not self.is_wild and getattr(self.enemy_data, 'isRocket', False)
        bg_color   = (18, 8, 12) if is_rocket else ((20, 18, 35) if not self.is_wild else (15, 30, 18))
        surf.fill(bg_color)
        # Ground strip
        ground_col = (60, 15, 20) if is_rocket else ((50, 60, 40) if self.is_wild else (40, 45, 65))
        pygame.draw.rect(surf, ground_col, (0, SH-160, SW, 160))
        pygame.draw.line(surf, (100, 40, 50) if is_rocket else (80,100,60), (0, SH-160), (SW, SH-160), 2)

        # ── Trainer sprite (right side, next to enemy pokemon) ──
        if not self.is_wild and self.enemy_data:
            is_r = getattr(self.enemy_data, 'isRocket', False)
            tr_img, tr_w, tr_h = fit_img(self.enemy_data.image, 110, 200)
            # Place trainer to the right of enemy pokemon area
            tr_x = SW - tr_w - 20
            tr_y = SH - 160 - tr_h + 5
            bob_tr = math.sin(self.anim_t * 0.04) * 2
            surf.blit(tr_img, (tr_x, int(tr_y + bob_tr)))
            name_col = (220, 50, 50) if is_r else C_ORANGE
            badge_bg  = (50, 10, 10) if is_r else (30, 30, 50)
            draw_rounded_rect(surf, badge_bg, (tr_x - 4, tr_y + tr_h + 4, tr_w + 8, 20), 6, 1, name_col)
            draw_text(surf, ("🚀 " if is_r else "👤 ") + self.enemy_data.name[:12],
                      F_TINY, name_col, tr_x + tr_w//2, tr_y + tr_h + 7, center=True)

        # ── Enemy Pokémon (right side) ──
        em = self.enemy_moonie
        if em:
            ex_base = 680
            jump_x = -int(self._enemy_jump * 3.5)
            jump_y = -int(math.sin(self._enemy_jump / 12.0 * math.pi) * 18) if self._enemy_jump > 0 else 0
            ex = ex_base + (random.randint(-3,3) if self.shake_enemy > 0 else 0) + jump_x
            ey_base = 95
            em_img, em_w, em_h = fit_img(em.image, 200, 200)
            bob = math.sin(self.anim_t * 0.05) * 4
            draw_y = int(ey_base + bob + jump_y)
            surf.blit(em_img, (ex - em_w//2, draw_y))
            shad_alpha = max(20, 60 - self._enemy_jump * 4)
            shad_s = pygame.Surface((em_w, 14), pygame.SRCALPHA)
            pygame.draw.ellipse(shad_s, (0,0,0,shad_alpha), (0,0,em_w,14))
            surf.blit(shad_s, (ex - em_w//2, SH - 168))
            # Info panel top-right
            em_st = getattr(em, "status", None)
            px_info = SW - 310
            panel_border = STATUS_DATA[em_st]["col"] if em_st else (60,65,85)
            draw_rounded_rect(surf, C_PANEL, (px_info, 42, 290, 64), 8, 2, panel_border)
            em_name_col = STATUS_DATA[em_st]["col"] if em_st else C_WHITE
            em_name_txt = em.name + (f"  {STATUS_DATA[em_st]['icon']} {STATUS_DATA[em_st]['label']}" if em_st else "")
            draw_text(surf, em_name_txt, F_SMALL, em_name_col, px_info + 8, 46, shadow=True)
            draw_text(surf, f"Lv {em.level}", F_TINY, C_GRAY, px_info + 240, 46)
            draw_hp_bar(surf, px_info + 8, 70, 270, 10, em.current_hp, em.max_hp, label=True)
            for i, t in enumerate(em.types):
                draw_type_badge(surf, t, px_info + 8 + i*70, 84)
            # Floating status badge above sprite
            if em_st:
                sd = STATUS_DATA[em_st]
                pulse_a = int(160 + 80 * math.sin(self.anim_t * 0.1))
                bs = pygame.Surface((90, 20), pygame.SRCALPHA)
                bs.fill((*sd["col"], pulse_a))
                surf.blit(bs, (ex - 45, draw_y - 26))
                draw_text(surf, f"{sd['icon']} {sd['label']}", F_TINY, (255,255,255), ex, draw_y - 23, center=True)

        # ── Player Pokémon (left-center) ──
        pm = self.player_moonie
        if pm:
            px_base = 240
            py_base = 250
            jump_x_p = int(self._player_jump * 4.0)
            jump_y_p = -int(math.sin(self._player_jump / 12.0 * math.pi) * 20) if self._player_jump > 0 else 0
            px = px_base + (random.randint(-3,3) if self.shake_player > 0 else 0) + jump_x_p
            py = py_base
            pm_img, pm_w, pm_h = fit_img(pm.image, 180, 180)
            pm_img = pygame.transform.flip(pm_img, True, False)
            bob = math.sin(self.anim_t * 0.05 + 1) * 4
            draw_y_p = int(py + bob + jump_y_p)
            surf.blit(pm_img, (px - pm_w//2, draw_y_p))
            # Info panel bottom-left
            pm_st = getattr(pm, "status", None)
            panel_border_p = STATUS_DATA[pm_st]["col"] if pm_st else (60,65,85)
            draw_rounded_rect(surf, C_PANEL, (20, py + pm_h + 14, 250, 68), 8, 2, panel_border_p)
            pm_name_col = STATUS_DATA[pm_st]["col"] if pm_st else C_WHITE
            pm_name_txt = pm.name + (f"  {STATUS_DATA[pm_st]['icon']} {STATUS_DATA[pm_st]['label']}" if pm_st else "")
            draw_text(surf, pm_name_txt, F_SMALL, pm_name_col, 28, py + pm_h + 18, shadow=True)
            draw_text(surf, f"Lv {pm.level}", F_TINY, C_GRAY, 220, py + pm_h + 18)
            draw_hp_bar(surf, 28, py + pm_h + 42, 230, 10, pm.current_hp, pm.max_hp, label=True)
            xp_pct = pm.xp / pm.xp_to_next if pm.xp_to_next else 0
            pygame.draw.rect(surf, (60,60,80), (28, py + pm_h + 60, 230, 5), border_radius=3)
            if xp_pct > 0:
                pygame.draw.rect(surf, C_BLUE, (28, py + pm_h + 60, int(230*xp_pct), 5), border_radius=3)
            # Floating status badge above player sprite
            if pm_st:
                sd = STATUS_DATA[pm_st]
                pulse_a = int(160 + 80 * math.sin(self.anim_t * 0.1 + 1.5))
                bs = pygame.Surface((90, 20), pygame.SRCALPHA)
                bs.fill((*sd["col"], pulse_a))
                surf.blit(bs, (px - 45, draw_y_p - 26))
                draw_text(surf, f"{sd['icon']} {sd['label']}", F_TINY, (255,255,255), px, draw_y_p - 23, center=True)

        # Hit flash overlays
        if self._hit_flash > 0:
            hf = pygame.Surface((280, 240), pygame.SRCALPHA)
            r,g,b = self._hit_flash_col
            hf.fill((r,g,b, int(120 * self._hit_flash / 10)))
            surf.blit(hf, (560, 80))
            self._hit_flash -= 1
        if self._player_hit_flash > 0:
            hf2 = pygame.Surface((220, 220), pygame.SRCALPHA)
            hf2.fill((255,80,80, int(100 * self._player_hit_flash / 8)))
            surf.blit(hf2, (130, 240))
            self._player_hit_flash -= 1

        log_rect = (20, SH - 148, SW - 260, 130)
        draw_rounded_rect(surf, C_DARK, log_rect, 10, 1, (80,80,100))
        for i, txt in enumerate(self.log[-4:]):
            color = C_WHITE if i == len(self.log[-4:])-1 else C_GRAY
            draw_text(surf, txt, F_SMALL, color, log_rect[0]+10, log_rect[1]+10+i*28)

        mult, lbl, ecol = self.last_effectiveness
        if lbl and self.state == "player_turn":
            draw_text(surf, lbl, F_SMALL, ecol, log_rect[0]+10, log_rect[1]+120, shadow=True)

        if self.state == "switch_pick":
            alive_idx = [i for i,m in enumerate(self.player_team) if m.is_alive() and i != self.player_idx]
            pw, ph = 420, min(80 + max(1,len(alive_idx))*70 + 36, 420)
            px2, py2 = SW//2 - pw//2, SH//2 - ph//2
            draw_rounded_rect(surf, C_PANEL, (px2, py2, pw, ph), 14, 2, C_BLUE)
            hdr = "⚠ Wähle dein nächstes!" if self.switch_forced else "🔄 Team wechseln"
            draw_text(surf, hdr, F_MED, C_YELLOW, px2+pw//2, py2+10, center=True, shadow=True)
            for row_i, tidx in enumerate(alive_idx):
                m = self.player_team[tidx]
                sel = (tidx == self.switch_pick_sel)
                ibg = (40,70,120) if sel else (28,34,52)
                ibc = C_YELLOW if sel else (50,55,75)
                ry = py2 + 48 + row_i * 68
                draw_rounded_rect(surf, ibg, (px2+12, ry, pw-24, 60), 10, 2 if sel else 1, ibc)
                mimg, mw, mh = fit_img(m.image, 48, 48)
                surf.blit(mimg, (px2+18, ry+6))
                fs_val = get_friendship(self.save_data_ref, m.name)
                fs_icon = next((icon for thresh,_,_,icon in FRIENDSHIP_LEVELS if fs_val>=thresh and icon),"")
                draw_text(surf, f"{m.name} {fs_icon}", F_SMALL, C_WHITE, px2+76, ry+6, shadow=True)
                draw_text(surf, f"Lv {m.level}", F_TINY, C_GRAY, px2+76, ry+26)
                draw_hp_bar(surf, px2+76, ry+42, pw-100, 8, m.current_hp, m.max_hp, label=True)
                st = getattr(m, "status", None)
                if st:
                    draw_text(surf, STATUS_DATA[st]["icon"], F_SMALL, STATUS_DATA[st]["col"], px2+pw-36, ry+18)
            esc_hint = "" if self.switch_forced else "  ESC=Abbruch"
            draw_text(surf, f"↑↓ wählen   ENTER bestätigen{esc_hint}", F_TINY, C_GRAY, px2+pw//2, py2+ph-18, center=True)

        elif self.state == "item_pick":
            items = self._get_usable_items(self.save_data_ref)
            pw, ph = 340, min(60 + max(1,len(items))*52 + 40, 340)
            px2, py2 = SW//2 - pw//2, SH//2 - ph//2
            draw_rounded_rect(surf, C_PANEL, (px2, py2, pw, ph), 14, 2, C_YELLOW)
            draw_text(surf, "💊 Items benutzen", F_MED, C_YELLOW, px2+pw//2, py2+10, center=True, shadow=True)
            if not items:
                draw_text(surf, "Keine Items vorhanden!", F_SMALL, C_GRAY, px2+pw//2, py2+80, center=True)
            else:
                for i, (name, desc, key, heal) in enumerate(items):
                    sel = (i == self.item_pick_sel)
                    ibg = (50,80,130) if sel else (30,36,55)
                    ibc = C_YELLOW if sel else (50,55,75)
                    cnt = self.save_data_ref.get(key, 0)
                    row_y = py2 + 44 + i * 50
                    draw_rounded_rect(surf, ibg, (px2+14, row_y, pw-28, 42), 8, 2 if sel else 1, ibc)
                    icon = item_icon(key, 32)
                    if icon:
                        surf.blit(icon, (px2+20, row_y+5))
                    draw_text(surf, f"{name}", F_SMALL, C_WHITE, px2+60, row_y+4)
                    draw_text(surf, f"{desc}  ({cnt}x)", F_TINY, C_GRAY, px2+60, row_y+22)
            draw_text(surf, "↑↓ wählen   ENTER nutzen   ESC zurück", F_TINY, C_GRAY, px2+pw//2, py2+ph-18, center=True)

        elif self.state == "ball_pick":
            balls = self._get_available_balls(self.save_data_ref)
            pw, ph = 340, min(60 + max(1,len(balls))*52 + 40, 260)
            px2, py2 = SW//2 - pw//2, SH//2 - ph//2
            draw_rounded_rect(surf, C_PANEL, (px2, py2, pw, ph), 14, 2, C_YELLOW)
            draw_text(surf, "🎯 Ball wählen", F_MED, C_YELLOW, px2+pw//2, py2+10, center=True, shadow=True)
            if not balls:
                draw_text(surf, "Keine Bälle!", F_SMALL, C_GRAY, px2+pw//2, py2+80, center=True)
            else:
                for i, (name, desc, key, _) in enumerate(balls):
                    sel = (i == self.ball_pick_sel)
                    ibg = (50,80,130) if sel else (30,36,55)
                    ibc = (255,215,0) if (sel and key=="master_balls") else (C_YELLOW if sel else (50,55,75))
                    cnt = self.save_data_ref.get(key, 0)
                    row_y = py2 + 44 + i * 50
                    draw_rounded_rect(surf, ibg, (px2+14, row_y, pw-28, 42), 8, 2 if sel else 1, ibc)
                    icon = item_icon(key, 32)
                    if icon:
                        surf.blit(icon, (px2+20, row_y+5))
                    nc = (255,215,0) if key=="master_balls" else C_WHITE
                    draw_text(surf, f"{name}", F_SMALL, nc, px2+60, row_y+4)
                    draw_text(surf, f"{desc}  ({cnt}x)", F_TINY, C_GRAY, px2+60, row_y+22)
            draw_text(surf, "↑↓ wählen   ENTER werfen   ESC zurück", F_TINY, C_GRAY, px2+pw//2, py2+ph-18, center=True)

        elif self.state == "player_turn":
            if self.energy_boost_rounds > 0 or self.energy_down_phase:
                pulse = abs(math.sin(self.anim_t * 0.12))
                if self.energy_down_phase:
                    banner_col = (180, 60, 60)
                    banner_txt = "⚠ DOWNPHASE — kein Angriff möglich!"
                    bg_col     = (60, 10, 10)
                else:
                    banner_col = (255, int(120 + 135*pulse), 0)
                    banner_txt = f"⚡ ENERGY BOOST aktiv! Noch {self.energy_boost_rounds} Runde(n) — 2. Angriff verfügbar!"
                    bg_col     = (40, 20, 0)
                bw2 = 600; bh2 = 28
                bx2 = SW//2 - bw2//2; by2 = SH - 185
                draw_rounded_rect(surf, bg_col, (bx2, by2, bw2, bh2), 8, 2, banner_col)
                rb_icon = item_icon("redbull", 22)
                if rb_icon:
                    surf.blit(rb_icon, (bx2+6, by2+3))
                draw_text(surf, banner_txt, F_SMALL, banner_col, bx2+bw2//2+10, by2+4, center=True, shadow=True)

            # 5-button layout: top row [0,1,2], bottom row [3,4]
            can_switch = sum(1 for m in self.player_team if m.is_alive()) > 1
            btn_labels = ["⚔ Angriff", "🎯 Ball", "💊 Tasche", "🔄 Wechsel", "🏃 Fliehen"]
            btn_colors = [
                (60,90,150),(90,150,60),(80,130,80),
                (60,100,150) if can_switch else (45,45,65),
                (150,60,60)
            ]
            if not can_switch:
                btn_labels[3] = "🔄 Kein Team"
            if self.energy_boost_rounds > 0 and not self.energy_down_phase:
                pulse2 = abs(math.sin(self.anim_t * 0.15))
                btn_colors[0] = (int(160+60*pulse2), int(60+40*pulse2), 0)
                btn_labels[0] = "⚡×2 Angriff"
            elif self.energy_down_phase:
                btn_colors[0] = (60, 30, 30)
                btn_labels[0] = "💤 Erschöpft"

            # Top row: 3 buttons; bottom row: 2 buttons centered
            bw, bh = 110, 50
            gap = 6
            total_top = 3*bw + 2*gap
            bx_top = SW - total_top - 12
            by_top = SH - 148
            total_bot = 2*bw + gap
            bx_bot = SW - total_bot - 12
            by_bot = by_top + bh + gap

            btn_positions = [
                (bx_top + 0*(bw+gap), by_top),
                (bx_top + 1*(bw+gap), by_top),
                (bx_top + 2*(bw+gap), by_top),
                (bx_bot + 0*(bw+gap), by_bot),
                (bx_bot + 1*(bw+gap), by_bot),
            ]
            for i, (lbl, col) in enumerate(zip(btn_labels, btn_colors)):
                bxi, byi = btn_positions[i]
                sel = (i == self.selected_btn)
                bc = C_YELLOW if sel else col
                draw_rounded_rect(surf, col, (bxi, byi, bw, bh), 10, 3 if sel else 1, bc)
                if sel:
                    glow = pygame.Surface((bw+6,bh+6), pygame.SRCALPHA)
                    pygame.draw.rect(glow,(255,220,50,80),(0,0,bw+6,bh+6),border_radius=12)
                    surf.blit(glow,(bxi-3,byi-3))
                draw_text(surf, lbl, F_SMALL, C_WHITE, bxi+bw//2, byi+14, center=True, shadow=True)
                if i == 1 and hasattr(self,"save_data_ref"):
                    b  = self.save_data_ref.get("balls",0)
                    mb = self.save_data_ref.get("master_balls",0)
                    ball_str = f"×{b}" + (f"  ✦×{mb}" if mb else "")
                    draw_text(surf, ball_str, F_TINY, C_GRAY, bxi+bw//2, byi+30, center=True)
                if i == 2 and hasattr(self,"save_data_ref"):
                    pot = self.save_data_ref.get("potions",0)
                    sp  = self.save_data_ref.get("super_potions",0)
                    hp  = self.save_data_ref.get("hyper_potions",0)
                    draw_text(surf, f"T:{pot}  ST:{sp}  HT:{hp}", F_TINY, C_GRAY, bxi+bw//2, byi+30, center=True)
                if i == 3 and can_switch:
                    alive_c = sum(1 for m in self.player_team if m.is_alive())
                    draw_text(surf, f"Team: {alive_c} fit", F_TINY, C_GRAY, bxi+bw//2, byi+30, center=True)

        elif self.state == "andreas_steal":
            overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
            pulse = abs(math.sin(self.andreas_anim_t * 0.1))
            overlay.fill((80, 0, 80, int(60 + pulse * 80)))
            surf.blit(overlay, (0, 0))
            andreas_img = load_img("assets/moonie/psychoAndreas.png", (200, 200))
            ax = SW//2 - 100
            ay = SH//2 - 140 + int(math.sin(self.andreas_anim_t * 0.15) * 10)
            surf.blit(andreas_img, (ax, ay))
            draw_text(surf, "PSYCHO ANDREAS!", F_BIG, (255, 80, 255), SW//2, ay - 45, center=True, shadow=True)
            em = self.enemy_moonie
            if em:
                draw_text(surf, f"Er schnappt sich {em.name}...", F_MED, C_WHITE, SW//2, ay + 215, center=True, shadow=True)
            total = getattr(self, '_andreas_audio_len', 150)
            pct = min(1.0, self.andreas_anim_t / total)
            pygame.draw.rect(surf, (60,20,60), (SW//2-150, SH-50, 300, 14), border_radius=7)
            pygame.draw.rect(surf, (220,60,220), (SW//2-150, SH-50, int(300*pct), 14), border_radius=7)
            draw_text(surf, "Warte auf Andreas...", F_TINY, C_GRAY, SW//2, SH-70, center=True)

        elif self.state == "catch_anim":
            t = self.catch_anim_t
            ball_x = SW//2 + math.sin(t*0.2)*100
            ball_y = SH//2 - abs(math.cos(t*0.08))*120
            ball_key = getattr(self, "_catch_ball_key", "balls")
            ball_path = ITEM_IMAGES.get(ball_key, "assets/pokeball.png")
            ball_img = load_img(ball_path, (48,48))
            surf.blit(ball_img, (int(ball_x)-24, int(ball_y)-24))
            if t > 60:
                msg = "Gefangen!" if self.catch_result else "Ausgebrochen!"
                col = C_GREEN if self.catch_result else C_RED
                draw_text(surf, msg, F_BIG, col, SW//2, SH//2, center=True, shadow=True)

        elif self.state in ("result", "done"):
            overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            surf.blit(overlay, (0,0))
            msgs = {"win":"Sieg! 🎉","lose":"Niederlage...","catch":"Gefangen! 🎊",
                    "run":"Geflohen!","andreas":"Psycho Andreas war schneller!","end":"Ende"}
            cols = {"win":C_YELLOW,"lose":C_RED,"catch":C_GREEN,"run":C_GRAY,
                    "andreas":(255,80,255),"end":C_WHITE}
            r = self.result or "end"
            draw_text(surf, msgs.get(r,"Ende"), F_HUGE, cols.get(r,C_WHITE), SW//2, SH//2-60, center=True, shadow=True)
            if r == "win":
                draw_text(surf, f"+{self.xp_gained} XP  +{self.coins_reward} Coins", F_MED, C_YELLOW, SW//2, SH//2+10, center=True)
            elif r == "lose":
                draw_text(surf, "Dein Team wurde besiegt. Du wachst im Pokécenter auf.", F_SMALL, C_GRAY, SW//2, SH//2+10, center=True)
            elif r == "andreas":
                draw_text(surf, "Das Moonie ist für immer weg. Danke Andreas.", F_SMALL, (200,100,200), SW//2, SH//2+10, center=True)
            draw_text(surf, "[ ENTER / SPACE ] Weiter", F_SMALL, C_GRAY, SW//2, SH//2+60, center=True)
        elif self.state == "intro":
            draw_text(surf, "[ ENTER ] Kampf beginnen", F_MED, C_WHITE, SW//2, SH-50, center=True)

        update_particles(surf)
        draw_notifications(surf)

# ── Pokedex screen ─────────────────────────────────────────────────────────────
class PokedexScreen:
    COLS = 5
    ROWS = 4
    PER_PAGE = COLS * ROWS

    def __init__(self, caught_list, save_ref=None):
        self.caught_set  = set(caught_list)
        self._save_ref   = save_ref
        self.seen_set    = set(save_ref.get("dex_seen", [])) if save_ref else set()
        # merge: caught are also seen
        self.seen_set.update(self.caught_set)
        self.all_names   = sorted(ALL_MOONIES_DICT.keys())
        self.filter_mode = "caught"  # "caught" | "seen" | "all"
        self.search      = ""
        self.searching   = False
        self.sel         = 0
        self.detail_name = None
        self._sil_cache  = {}

    def _visible(self):
        pool = [n for n in self.all_names
                if (self.filter_mode == "all"
                    or (self.filter_mode == "caught" and n in self.caught_set)
                    or (self.filter_mode == "seen"   and n in self.seen_set))
                and (not self.search or self.search.lower() in n.lower())]
        return pool

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key
        if self.detail_name:
            self.detail_name = None
            return None
        if self.searching:
            if k == pygame.K_ESCAPE or k == pygame.K_RETURN:
                self.searching = False
                self.sel = 0
            elif k == pygame.K_BACKSPACE:
                self.search = self.search[:-1]
            else:
                ch = event.unicode
                if ch.isprintable():
                    self.search += ch
            return None
        vis = self._visible()
        total = len(vis)
        if k == pygame.K_LEFT:
            self.sel = max(0, self.sel - 1)
        elif k == pygame.K_RIGHT:
            self.sel = min(total - 1, self.sel + 1)
        elif k == pygame.K_UP:
            self.sel = max(0, self.sel - self.COLS)
        elif k == pygame.K_DOWN:
            self.sel = min(total - 1, self.sel + self.COLS)
        elif k == pygame.K_RETURN or k == pygame.K_z:
            if 0 <= self.sel < total and vis[self.sel] in self.seen_set:
                self.detail_name = vis[self.sel]
        elif k == pygame.K_f:
            modes = ["caught","seen","all"]
            self.filter_mode = modes[(modes.index(self.filter_mode)+1) % len(modes)]
            self.sel = 0
        elif k == pygame.K_s:
            self.searching = True
            self.search = ""
        elif k == pygame.K_ESCAPE or k == pygame.K_x:
            return "close"
        return None

    def _make_silhouette(self, img):
        sil = img.copy()
        dark = pygame.Surface(sil.get_size(), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 255))
        sil.blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        return sil

    def draw(self, surf):
        surf.fill((12, 14, 22))
        vis = self._visible()
        total = len(vis)
        draw_rounded_rect(surf, C_PANEL, (0, 0, SW, 54), 0)
        draw_text(surf, "📖 Pokédex", F_BIG, C_YELLOW, SW//2, 4, center=True, shadow=True)
        caught_count = len(self.caught_set)
        seen_count   = len(self.seen_set)
        total_count  = len(self.all_names)
        filter_lbl   = {"caught":"Nur Gefangene","seen":"Gesehen","all":"Alle"}[self.filter_mode]
        draw_text(surf, f"👁 {seen_count} gesehen  •  ✅ {caught_count}/{total_count} gefangen  |  [F] Filter: {filter_lbl}  [S] Suche  [ENTER] Detail  [ESC] zurück", F_TINY, C_GRAY, SW//2, 38, center=True)
        if self.searching or self.search:
            bar_col = C_BLUE if self.searching else (60, 60, 80)
            draw_rounded_rect(surf, bar_col, (SW//2-200, 56, 400, 28), 8, 2, C_YELLOW if self.searching else C_GRAY)
            cursor = "|" if self.searching and int(time.time()*2)%2 == 0 else ""
            draw_text(surf, f"Suche: {self.search}{cursor}", F_SMALL, C_WHITE, SW//2, 62, center=True)
        cw, ch = 148, 120
        pad_y = 88 if (self.searching or self.search) else 58
        pad_x = (SW - self.COLS * cw) // 2
        page  = self.sel // self.PER_PAGE if total > 0 else 0
        start = page * self.PER_PAGE
        end   = min(start + self.PER_PAGE, total)
        for i, idx in enumerate(range(start, end)):
            name   = vis[idx]
            caught = name in self.caught_set
            row, col = divmod(i, self.COLS)
            x = pad_x + col * cw
            y = pad_y + row * ch
            sel = (idx == self.sel)
            seen   = name in self.seen_set
            caught = name in self.caught_set
            bg  = (40, 55, 40) if caught else ((30, 35, 50) if seen else (20, 20, 30))
            bdr = C_YELLOW if sel else ((80,160,80) if caught else ((80,80,120) if seen else (40,40,55)))
            draw_rounded_rect(surf, bg, (x+2, y+2, cw-4, ch-4), 8, 2 if sel else 1, bdr)
            m = ALL_MOONIES_DICT.get(name)
            if m:
                img = load_img(m.image, (68, 68))
                if caught:
                    pass  # full color
                elif seen:
                    # dimmed but visible
                    dim = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                    dim.fill((0,0,0,100))
                    img = img.copy(); img.blit(dim,(0,0))
                else:
                    if name not in self._sil_cache:
                        self._sil_cache[name] = self._make_silhouette(img)
                    img = self._sil_cache[name]
                surf.blit(img, (x + (cw-68)//2, y + 4))
            if caught:
                draw_text(surf, name, F_TINY, C_WHITE, x + cw//2, y + ch - 26, center=True)
                if m:
                    tw = len(m.types) * 38
                    tx = x + cw//2 - tw//2
                    for t in m.types:
                        tc = TYPE_COLORS.get(t, (150,150,150))
                        pygame.draw.rect(surf, tc, (tx, y+ch-14, 34, 12), border_radius=6)
                        draw_text(surf, t[:4], F_TINY, C_WHITE, tx+17, y+ch-13, center=True)
                        tx += 38
            elif seen:
                draw_text(surf, name, F_TINY, (160,160,200), x + cw//2, y + ch - 26, center=True)
                draw_text(surf, "👁 Gesehen", F_TINY, (120,120,160), x+cw//2, y+ch-14, center=True)
            else:
                draw_text(surf, "???", F_SMALL, C_GRAY, x + cw//2, y + ch - 24, center=True)
            global_idx = self.all_names.index(name)
            draw_text(surf, f"#{global_idx+1:03d}", F_TINY, C_GRAY, x+4, y+5)
        if total == 0:
            draw_text(surf, "Keine Pokémon gefunden." if self.search else "Noch keine gefangen!", F_MED, C_GRAY, SW//2, 300, center=True)
        total_pages = max(1, (total + self.PER_PAGE - 1) // self.PER_PAGE)
        draw_text(surf, f"Seite {page+1}/{total_pages}", F_TINY, C_GRAY, SW//2, SH-18, center=True)
        fm = self.filter_mode
        fc = C_GREEN if fm=="caught" else (C_BLUE if fm=="seen" else C_GRAY)
        next_lbl = {"caught":"Gesehen","seen":"Alle","all":"Gefangene"}[fm]
        draw_rounded_rect(surf, (25,40,25) if fm=="caught" else (25,25,45), (SW-190, SH-36, 182, 28), 8, 2, fc)
        draw_text(surf, f"[F] → {next_lbl} zeigen", F_TINY, fc, SW-99, SH-24, center=True)
        if self.detail_name and self.detail_name in self.seen_set:
            m = ALL_MOONIES_DICT.get(self.detail_name)
            if m:
                self._draw_detail(surf, m)
        draw_notifications(surf)

    def _draw_detail(self, surf, m):
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surf.blit(overlay, (0, 0))
        pw, ph = 860, 540
        px, py = SW//2 - pw//2, SH//2 - ph//2
        draw_rounded_rect(surf, (18, 20, 32), (px, py, pw, ph), 18, 2, C_YELLOW)
        r_col = m.get_rarity_color()
        pygame.draw.rect(surf, r_col, (px, py, pw, 7), border_radius=18)

        is_caught = m.name in self.caught_set
        is_seen   = m.name in self.seen_set

        # ── Left panel: image + size/weight ──
        lx = px + 16
        img, iw, ih = fit_img(m.image, 200, 200)
        if not is_caught:
            # Silhouette for seen-only
            sil = img.copy()
            dark = pygame.Surface(sil.get_size(), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 255))
            sil.blit(dark, (0,0), special_flags=pygame.BLEND_RGB_MULT)
            img = sil
        surf.blit(img, (lx + (200 - iw)//2, py + 14))
        # Size / weight
        size_str, weight_str = get_moonie_size_weight(m.name)
        draw_rounded_rect(surf, (30,36,55), (lx, py+222, 200, 48), 8)
        draw_text(surf, f"📏 {size_str}", F_SMALL, C_GRAY, lx+100, py+228, center=True)
        draw_text(surf, f"⚖ {weight_str}", F_SMALL, C_GRAY, lx+100, py+248, center=True)
        # Caught/Seen badge
        if is_caught:
            draw_rounded_rect(surf, (20,60,30), (lx, py+278, 200, 26), 8, 1, C_GREEN)
            draw_text(surf, "✅ Gefangen", F_SMALL, C_GREEN, lx+100, py+283, center=True)
        else:
            draw_rounded_rect(surf, (30,30,60), (lx, py+278, 200, 26), 8, 1, C_BLUE)
            draw_text(surf, "👁 Gesehen", F_SMALL, C_BLUE, lx+100, py+283, center=True)

        # ── Right panel ──
        rx = px + 230
        global_idx = self.all_names.index(m.name) if m.name in self.all_names else 0
        name_display = m.name if is_caught else f"??? (#{global_idx+1:03d})"
        draw_text(surf, f"#{global_idx+1:03d}  {name_display}", F_BIG, C_WHITE, rx, py + 14, shadow=True)
        draw_text(surf, m.rarity.capitalize(), F_SMALL, r_col, rx, py + 50)

        # Types
        tx2 = rx
        for t in m.types:
            draw_type_badge(surf, t, tx2, py + 68)
            tx2 += 74

        # Stats (only if caught)
        if is_caught:
            stats = [("Max HP", m.max_hp), ("Angriff", m.attack), ("Level", m.level)]
            for si,(slbl,sval) in enumerate(stats):
                sx = rx + si * 180
                draw_rounded_rect(surf, (30,36,55), (sx, py+98, 165, 44), 8)
                draw_text(surf, slbl, F_TINY, C_GRAY, sx+82, py+102, center=True)
                draw_text(surf, str(sval), F_MED, C_WHITE, sx+82, py+116, center=True)

            if m.nextEvolution and isinstance(m.nextEvolution, str):
                draw_text(surf, f"→ Entwickelt sich zu: {m.nextEvolution}", F_SMALL, C_BLUE, rx, py+150)

            # Friendship
            if self._save_ref:
                fs_val, fs_lbl, fs_col, fs_icon = get_friendship_label(self._save_ref, m.name)
                draw_text(surf, f"{fs_icon} {fs_lbl} ({fs_val}/255)", F_SMALL, fs_col, rx, py+174)
                pygame.draw.rect(surf, (40,40,60), (rx, py+194, 360, 8), border_radius=4)
                if fs_val > 0:
                    pygame.draw.rect(surf, fs_col, (rx, py+194, int(360*fs_val/255), 8), border_radius=4)

        # ── Pokédex entry ──
        pygame.draw.line(surf, (55,60,85), (rx, py+210), (px+pw-16, py+210), 1)
        desc = get_pokedex_entry(m.name) if is_caught else "Dieses Pokémon wurde gesehen, aber noch nicht gefangen. Details unbekannt."
        desc_lines = wrap_text(desc, F_SMALL, pw - 250)
        draw_text(surf, "📖 Pokédex-Eintrag", F_SMALL, C_YELLOW, rx, py+216)
        for li, line in enumerate(desc_lines[:3]):
            draw_text(surf, line, F_SMALL, (195,205,220), rx, py+238+li*24)

        # ── Type matchup chart ──
        pygame.draw.line(surf, (55,60,85), (px+16, py+310), (px+pw-16, py+310), 1)
        draw_text(surf, "⚔ Typ-Matchups", F_SMALL, C_YELLOW, px+pw//2, py+316, center=True)
        matchups = get_type_matchups(m.types)
        weak2   = sorted([t for t,v in matchups.items() if v >= 2.0])
        weak4   = sorted([t for t,v in matchups.items() if v >= 4.0])
        resist  = sorted([t for t,v in matchups.items() if 0 < v < 1.0])
        immune  = sorted([t for t,v in matchups.items() if v == 0])

        row_y = py + 334
        for label, types_list, col in [
            ("🔴 Schwach ×2", [t for t in weak2 if t not in weak4], (220,80,80)),
            ("🔥 Schwach ×4", weak4,                                  (255,60,60)),
            ("🔵 Resistenz",  resist,                                  (80,140,220)),
            ("⬛ Immun",      immune,                                   (100,100,120)),
        ]:
            if not types_list: continue
            draw_text(surf, label, F_TINY, col, px+20, row_y)
            tx3 = px+145
            for t in types_list[:8]:
                tc = TYPE_COLORS.get(t, (120,120,120))
                pygame.draw.rect(surf, tc, (tx3, row_y-1, 52, 16), border_radius=6)
                draw_text(surf, t[:5], F_TINY, C_WHITE, tx3+26, row_y+1, center=True)
                tx3 += 56
            row_y += 22

        pygame.draw.line(surf, (55,60,85), (px+16, py+ph-32), (px+pw-16, py+ph-32), 1)
        draw_text(surf, "[ beliebige Taste ] schließen", F_TINY, C_GRAY, px+pw//2, py+ph-20, center=True)


# ── PC Box screen ──────────────────────────────────────────────────────────────
class PCBoxScreen:
    # Available type filters (None = alle)
    TYPE_FILTERS = [None, "Feuer","Wasser","Pflanze","Elektro","Normal","Geist",
                    "Drache","Eis","Käfer","Boden","Gestein","Fee","Psycho",
                    "Kampf","Gift","Flug","Stahl","Dunkel"]

    def __init__(self, save_data, team):
        self.save        = save_data
        self.team        = team
        self.search      = ""
        self.searching   = False
        self.panel       = 0
        self.sel         = [0, 0]
        self.msg         = ""
        self.type_filter = 0      # index into TYPE_FILTERS (0 = alle)
        self.rarity_filter = None # None | "common" | "uncommon" | "rare" | "legendary"

    def _passes_filter(self, name):
        m = ALL_MOONIES_DICT.get(name)
        if not m: return True
        if self.search and self.search.lower() not in name.lower(): return False
        tf = self.TYPE_FILTERS[self.type_filter]
        if tf and tf not in m.types: return False
        if self.rarity_filter and m.rarity != self.rarity_filter: return False
        return True

    def _box_names(self):
        team_names = {m.name for m in self.team}
        raw = self.save.get("pc_box", [])
        seen = set()
        pool = []
        for n in raw:
            if n not in team_names and n not in seen:
                seen.add(n)
                if self._passes_filter(n):
                    pool.append(n)
        return pool

    def _team_list(self):
        return [m for m in self.team if self._passes_filter(m.name)]

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key
        if self.searching:
            if k in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.searching = False
                self.sel = [0, 0]
            elif k == pygame.K_BACKSPACE:
                self.search = self.search[:-1]
            else:
                ch = event.unicode
                if ch.isprintable():
                    self.search += ch
            return None
        if k == pygame.K_ESCAPE or k == pygame.K_x:
            return "close"
        if k == pygame.K_s:
            self.searching = True
            self.search = ""
            return None
        # Filter cycling
        if k == pygame.K_f:
            self.type_filter = (self.type_filter + 1) % len(self.TYPE_FILTERS)
            self.sel = [0,0]
            return None
        if k == pygame.K_r:
            rarities = [None,"common","uncommon","rare","legendary"]
            cur_idx = rarities.index(self.rarity_filter) if self.rarity_filter in rarities else 0
            self.rarity_filter = rarities[(cur_idx+1)%len(rarities)]
            self.sel = [0,0]
            return None
        if k == pygame.K_TAB or k == pygame.K_LEFT or k == pygame.K_RIGHT:
            self.panel = 1 - self.panel
            return None
        cur = self.panel
        if k == pygame.K_UP or k == pygame.K_w:
            self.sel[cur] = max(0, self.sel[cur] - 1)
        elif k == pygame.K_DOWN or k == pygame.K_s:
            lim = (len(self._team_list()) if cur == 0 else len(self._box_names())) - 1
            self.sel[cur] = min(max(0, lim), self.sel[cur] + 1)
        elif k == pygame.K_RETURN or k == pygame.K_z:
            self._transfer()
        return None

    def _transfer(self):
        box_names = self._box_names()
        team_list = self._team_list()
        if self.panel == 0:
            if not team_list:
                return
            idx = min(self.sel[0], len(team_list)-1)
            mon = team_list[idx]
            if len(self.team) <= 1:
                self.msg = "Du kannst nicht dein letztes Pokémon in die Box!"
                return
            self.team.remove(mon)
            pc = self.save.get("pc_box", [])
            if mon.name not in pc:
                pc.append(mon.name)
            self.save["pc_box"] = pc
            self.save["team"] = [moonie_to_dict(m) for m in self.team]
            self.msg = f"{mon.name} in die Box gelegt."
            self.sel[0] = min(self.sel[0], max(0, len(self.team)-1))
        else:
            if not box_names:
                return
            idx = min(self.sel[1], len(box_names)-1)
            name = box_names[idx]
            if len(self.team) >= 6:
                self.msg = "Team ist voll! (max 6)"
                return
            m = get_moonie(name)
            self.team.append(m)
            self.save["team"] = [moonie_to_dict(m) for m in self.team]
            self.msg = f"{name} ins Team geholt."
            self.sel[1] = min(self.sel[1], max(0, len(self._box_names())-1))

    def draw(self, surf):
        surf.fill((10, 14, 26))
        draw_rounded_rect(surf, C_PANEL, (0, 0, SW, 50), 0)
        draw_text(surf, "PC Box", F_BIG, C_YELLOW, SW//2, 4, center=True, shadow=True)
        draw_text(surf, "TAB/←→ Panel  ↑↓ Nav  ENTER Transfer  S Suche  F Typ-Filter  R Seltenheit  ESC zurück", F_TINY, C_GRAY, SW//2, 36, center=True)
        sy = 52
        # Filter bar
        tf = self.TYPE_FILTERS[self.type_filter]
        rf = self.rarity_filter
        if tf or rf or self.search or self.searching:
            chips = []
            if self.searching or self.search:
                chips.append((f"Suche: {self.search}{'|' if self.searching and int(time.time()*2)%2==0 else ''}", C_BLUE))
            if tf:
                tc = TYPE_COLORS.get(tf, C_GRAY)
                chips.append((f"Typ: {tf}", tc))
            if rf:
                rc = {"common":(150,150,150),"uncommon":(80,200,100),"rare":(80,140,220),"legendary":(220,180,50)}.get(rf, C_GRAY)
                chips.append((f"Seltenheit: {rf}", rc))
            cx = 20
            for label, col in chips:
                chip_w = len(label)*8+16
                draw_rounded_rect(surf, (*col,50), (cx, sy, chip_w, 22), 11, 1, col)
                draw_text(surf, label, F_TINY, C_WHITE, cx+chip_w//2, sy+5, center=True)
                cx += chip_w + 8
            sy += 26
        team_list = self._team_list()
        box_names = self._box_names()
        half = SW//2 - 8
        panels = [
            (10, sy, half, "Team", team_list, 0),
            (SW//2 + 8, sy, half, "PC Box", box_names, 1),
        ]
        for px, py, pw, title, items, pid in panels:
            active = (self.panel == pid)
            bdr = C_YELLOW if active else C_GRAY
            draw_rounded_rect(surf, (22, 28, 42), (px, py, pw, SH-py-40), 12, 2, bdr)
            title_col = C_YELLOW if active else C_GRAY
            draw_text(surf, f"{title} ({len(items)})", F_MED, title_col, px+pw//2, py+8, center=True, shadow=True)
            list_y = py + 38
            for i, item in enumerate(items[:14]):
                name = item.name if hasattr(item, 'name') else item
                is_sel = active and (i == self.sel[pid])
                bg  = (50, 80, 130) if is_sel else (30, 36, 55)
                bdc = C_YELLOW if is_sel else (50, 55, 75)
                draw_rounded_rect(surf, bg, (px+8, list_y, pw-16, 34), 7, 1, bdc)
                m_data = ALL_MOONIES_DICT.get(name)
                img = load_img(m_data.image if m_data else "assets/moonie/default.png", (28, 28))
                surf.blit(img, (px+12, list_y+3))
                draw_text(surf, name, F_SMALL, C_WHITE, px+46, list_y+9)
                if hasattr(item, 'level'):
                    draw_text(surf, f"Lv{item.level}", F_TINY, C_GRAY, px+pw-28, list_y+12)
                elif m_data:
                    draw_text(surf, f"Lv{m_data.level}", F_TINY, C_GRAY, px+pw-28, list_y+12)
                if is_sel and pid == 0:
                    draw_text(surf, "→ Box", F_TINY, (180,220,180), px+pw-80, list_y+12)
                elif is_sel and pid == 1:
                    draw_text(surf, "→ Team", F_TINY, (180,220,255), px+pw-86, list_y+12)
                list_y += 37
            if not items:
                draw_text(surf, "Leer" if not self.search else "Keine Treffer", F_SMALL, C_GRAY, px+pw//2, py+100, center=True)
        if self.msg:
            draw_rounded_rect(surf, (30,50,30), (SW//2-250, SH-36, 500, 28), 8, 1, C_GREEN)
            draw_text(surf, self.msg, F_SMALL, C_GREEN, SW//2, SH-24, center=True)
        draw_notifications(surf)


# ── Team screen ────────────────────────────────────────────────────────────────
class TeamScreen:
    def __init__(self, team, save_data):
        self.team = team
        self.save = save_data
        self.sel = 0
        self.anim_t = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.sel = max(0, self.sel - 1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.sel = min(len(self.team)-1, self.sel + 1)
            elif event.key in (pygame.K_ESCAPE, pygame.K_x, pygame.K_t):
                return "close"
        return None

    def draw(self, surf):
        self.anim_t += 1
        surf.fill((12, 16, 28))
        draw_rounded_rect(surf, C_PANEL, (0, 0, SW, 44), 0)
        draw_text(surf, "Dein Team", F_BIG, C_YELLOW, SW//2, 6, center=True, shadow=True)
        draw_text(surf, "[ T / ESC ] zurück   ↑↓ navigieren", F_TINY, C_GRAY, SW//2, 32, center=True)
        if not self.team:
            draw_text(surf, "Kein Team!", F_MED, C_GRAY, SW//2, SH//2, center=True)
            return
        for i, m in enumerate(self.team):
            y = 54 + i * 90
            sel = (i == self.sel)
            bg = (40,60,100) if sel else C_PANEL
            border = C_YELLOW if sel else (60,65,80)
            draw_rounded_rect(surf, bg, (12, y, 280, 82), 10, 2, border)
            img = load_img(m.image, (56, 56))
            surf.blit(img, (18, y + 13))
            draw_text(surf, m.name, F_MED, C_WHITE, 82, y + 10, shadow=True)
            draw_text(surf, f"Lv {m.level}", F_TINY, C_GRAY, 82, y + 33)
            draw_hp_bar(surf, 82, y + 52, 190, 10, m.current_hp, m.max_hp)
            tx = 82
            for t in m.types[:2]:
                tc = TYPE_COLORS.get(t, (150,150,150))
                pygame.draw.rect(surf, tc, (tx, y + 68, 52, 12), border_radius=6)
                draw_text(surf, t[:5], F_TINY, C_WHITE, tx+26, y+69, center=True)
                tx += 56
        if self.sel < len(self.team):
            m = self.team[self.sel]
            px, py_d, pw, ph = 308, 54, SW - 320, SH - 66
            draw_rounded_rect(surf, C_PANEL, (px, py_d, pw, ph), 14, 2, C_BLUE)
            img = load_img(m.image, (140, 140))
            bob = int(math.sin(self.anim_t * 0.06) * 5)
            surf.blit(img, (px + pw//2 - 70, py_d + 10 + bob))
            cy = py_d + 158
            draw_text(surf, m.name, F_BIG, C_WHITE, px + pw//2, cy, center=True, shadow=True)
            cy += 36
            rc = m.get_rarity_color()
            draw_text(surf, m.rarity.capitalize(), F_SMALL, rc, px + pw//2, cy, center=True)
            cy += 24
            tw = len(m.types) * 72
            tx = px + pw//2 - tw//2
            for t in m.types:
                draw_type_badge(surf, t, tx, cy)
                tx += 72
            cy += 26
            stats = [
                ("HP", m.current_hp, m.max_hp, C_GREEN),
                ("Ang", m.attack, 150, C_RED),
                ("XP", m.xp, m.xp_to_next, C_BLUE),
            ]
            for label, val, max_v, col in stats:
                cy += 6
                draw_text(surf, f"{label}: {val}/{max_v}", F_TINY, C_GRAY, px+16, cy)
                cy += 16
                bar_w = pw - 32
                pygame.draw.rect(surf, (50,50,60), (px+16, cy, bar_w, 10), border_radius=5)
                fill = int(bar_w * min(1.0, val/max_v)) if max_v > 0 else 0
                if fill > 0:
                    pygame.draw.rect(surf, col, (px+16, cy, fill, 10), border_radius=5)
                cy += 14
            if m.nextEvolution and m.evolve:
                cy += 8
                evo_name = m.nextEvolution if isinstance(m.nextEvolution, str) else str(m.nextEvolution)
                draw_text(surf, f"Entwicklung: {evo_name} (Lv {m.evolutionLevel})", F_SMALL, C_BLUE, px + pw//2, cy, center=True)
                if m.level >= m.evolutionLevel:
                    cy += 22
                    draw_text(surf, "Bereit zur Entwicklung!", F_SMALL, C_GREEN, px + pw//2, cy, center=True)
        draw_notifications(surf)

# ── Item bag screen ────────────────────────────────────────────────────────────
class ItemBagScreen:
    def __init__(self, save_data, team):
        self.save = save_data
        self.team = team
        self.sel_item = 0
        self.sel_mon  = 0
        self.mode = "items"

    def _all_items(self):
        return [
            {"name": "Trank",             "key": "potions",              "heal": 30,   "col": (100,200,130), "action": "heal"},
            {"name": "Super Trank",       "key": "super_potions",        "heal": 80,   "col": (80,160,255),  "action": "heal"},
            {"name": "Hyper Trank",       "key": "hyper_potions",        "heal": 150,  "col": (200,100,255), "action": "heal"},
            {"name": "Sonderbonbon",      "key": "sonderbonbons",        "heal": 0,    "col": (255,180,230), "action": "level"},
            {"name": "Beleber",           "key": "beleber",              "heal": 0,    "col": (180,255,180), "action": "revive_half"},
            {"name": "Top-Beleber",       "key": "top_beleber",          "heal": 0,    "col": (100,255,200), "action": "revive_full"},
            {"name": "💎 Entwicklungsstein", "key": "entwicklungsstein", "heal": 0,    "col": C_STEIN,       "action": "stein"},
            {"name": "Meisterball",       "key": "master_balls",         "heal": 0,    "col": (255,215,0),   "action": "info"},
            {"name": "Pokéball",          "key": "balls",                "heal": 0,    "col": (220,80,80),   "action": "info"},
            {"name": "Raid-Pass",         "key": "raid_passes",          "heal": 0,    "col": (80,180,255),  "action": "info"},
            {"name": "Premium Raid-Pass", "key": "premium_raid_passes",  "heal": 0,    "col": (255,160,80),  "action": "info"},
        ]

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        items = self._all_items()
        if self.mode == "items":
            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel_item = max(0, self.sel_item - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel_item = min(len(items)-1, self.sel_item + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                item = items[self.sel_item]
                if self.save.get(item["key"], 0) <= 0:
                    notify(f"Kein {item['name']} mehr!", C_RED)
                    return None
                if item["action"] in ("heal", "level"):
                    self.mode = "pick_target"
                    self.sel_mon = 0
                elif item["action"] == "stein":
                    # Signal to Game that Stein should be applied
                    return ("use_stein",)
                elif item["action"] in ("revive_half", "revive_full"):
                    if any(m.current_hp <= 0 for m in self.team):
                        self.mode = "pick_target"
                        self.sel_mon = 0
                    else:
                        notify("Kein besiegtes Pokémon im Team!", C_RED)
                else:
                    notify(f"{item['name']}: Nur im Kampf einsetzbar!", C_GRAY)
            elif event.key in (pygame.K_ESCAPE, pygame.K_x, pygame.K_i):
                return "close"
        elif self.mode == "pick_target":
            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel_mon = max(0, self.sel_mon - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel_mon = min(len(self.team)-1, self.sel_mon + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                self._use_item()
            elif event.key in (pygame.K_ESCAPE, pygame.K_x):
                self.mode = "items"
        return None

    def _use_item(self):
        m = self.team[self.sel_mon] if self.sel_mon < len(self.team) else None
        if not m: return
        items = self._all_items()
        item  = items[self.sel_item]
        key   = item["key"]
        if self.save.get(key, 0) <= 0:
            return
        self.save[key] -= 1
        if item["action"] == "heal":
            if m.current_hp <= 0:
                notify(f"{m.name} ist bewusstlos! Nutze einen Beleber.", C_RED)
                self.save[key] += 1
                return
            m.heal(item["heal"])
            notify(f"{m.name} +{item['heal']} HP! ({self.save[key]} übrig)", C_GREEN)
        elif item["action"] == "level":
            m.level += 1
            m.max_hp  = int(m.max_hp * 1.05) + 2
            m.attack  = int(m.attack * 1.05) + 1
            m.current_hp = min(m.current_hp + 10, m.max_hp)
            notify(f"🍬 {m.name} ist jetzt Level {m.level}!", (255,180,230))
        elif item["action"] == "revive_half":
            if m.current_hp > 0:
                notify(f"{m.name} ist nicht bewusstlos!", C_RED)
                self.save[key] += 1
                return
            m.current_hp = max(1, m.max_hp // 2)
            notify(f"💚 {m.name} wurde wiederbelebt! ({m.current_hp}/{m.max_hp} HP)", C_GREEN)
        elif item["action"] == "revive_full":
            if m.current_hp > 0:
                notify(f"{m.name} ist nicht bewusstlos!", C_RED)
                self.save[key] += 1
                return
            m.current_hp = m.max_hp
            notify(f"💚 {m.name} vollständig wiederbelebt! ({m.max_hp}/{m.max_hp} HP)", (100,255,200))
        self.mode = "items"

    def draw(self, surf):
        surf.fill((12, 16, 28))
        draw_rounded_rect(surf, C_PANEL, (0, 0, SW, 44), 0)
        draw_text(surf, "Item-Beutel", F_BIG, C_YELLOW, SW//2, 6, center=True, shadow=True)
        draw_text(surf, "[ I / ESC ] zurück", F_TINY, C_GRAY, SW//2, 32, center=True)
        items  = self._all_items()
        col_w  = (SW - 100) // 2
        for i, item in enumerate(items):
            count = self.save.get(item["key"], 0)
            col_i = i % 2
            row_i = i // 2
            ix = 40 + col_i * (col_w + 20)
            iy = 60 + row_i * 76
            sel = (i == self.sel_item) and self.mode == "items"
            bg = (40,60,100) if sel else C_PANEL
            draw_rounded_rect(surf, bg, (ix, iy, col_w, 68), 12, 2 if sel else 1,
                              C_YELLOW if sel else C_GRAY)
            icon = item_icon(item.get("key", ""), 40)
            if icon:
                surf.blit(icon, (ix+10, iy+14))
            draw_text(surf, item["name"], F_MED, item["col"], ix+58, iy+10, shadow=True)
            action_desc = (f"+{item['heal']} HP" if item["action"]=="heal"
                          else ("+1 Level" if item["action"]=="level"
                          else ("Sofort entwickeln!" if item["action"]=="stein"
                          else "Im Kampf")))
            draw_text(surf, action_desc, F_SMALL, C_GRAY, ix+58, iy+34)
            count_col = C_WHITE if count > 0 else C_RED
            draw_text(surf, f"×{count}", F_BIG, count_col, ix+col_w-30, iy+22, center=True)
        list_bottom = 60 + ((len(items)+1)//2) * 76 + 10
        if self.mode == "items":
            draw_text(surf, "↑↓← → wählen   ENTER benutzen", F_SMALL, C_GRAY, SW//2, list_bottom, center=True)
        else:
            draw_text(surf, "Welches Pokémon?", F_MED, C_YELLOW, SW//2, list_bottom, center=True)
            for i, m in enumerate(self.team):
                y = list_bottom + 30 + i * 78
                sel = (i == self.sel_mon) and self.mode == "pick_target"
                bg2 = (40,80,50) if sel else (28,32,45)
                draw_rounded_rect(surf, bg2, (40, y, SW-80, 70), 10, 2 if sel else 1, C_GREEN if sel else (55,60,75))
                img = load_img(m.image, (48, 48))
                surf.blit(img, (52, y+11))
                draw_text(surf, m.name, F_MED, C_WHITE, 112, y+12)
                draw_text(surf, f"Lv {m.level}", F_TINY, C_GRAY, 112, y+34)
                draw_hp_bar(surf, 220, y+26, 500, 12, m.current_hp, m.max_hp)
                hp_col = C_RED if m.current_hp < m.max_hp * 0.3 else C_WHITE
                draw_text(surf, f"{m.current_hp}/{m.max_hp}", F_TINY, hp_col, 740, y+26)
        draw_notifications(surf)


# ── Evolution screen ───────────────────────────────────────────────────────────
class EvolutionScreen:
    def __init__(self, old_name, new_name, team):
        self.old_name = old_name
        self.new_name = new_name
        self.team = team
        self.anim_t = 0
        self.phase = "flash"

    def update(self):
        self.anim_t += 1
        if self.anim_t < 80:
            self.phase = "flash"
        elif self.anim_t < 200:
            self.phase = "show"
        else:
            self.phase = "done"

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.phase == "show":
            self.phase = "done"
        return "done" if self.phase == "done" else None

    def draw(self, surf):
        surf.fill(C_BG)
        t = self.anim_t
        if self.phase == "flash":
            flash = pygame.Surface((SW, SH), pygame.SRCALPHA)
            alpha = int(200 * abs(math.sin(t * 0.15)))
            flash.fill((255, 255, 255, alpha))
            surf.blit(flash, (0,0))
            draw_text(surf, f"{self.old_name} entwickelt sich!", F_BIG, C_WHITE, SW//2, SH//2, center=True, shadow=True)
        elif self.phase in ("show", "done"):
            m = get_moonie(self.new_name)
            img = load_img(m.image, (200, 200))
            bob = int(math.sin(t * 0.08) * 8)
            surf.blit(img, (SW//2-100, 140 + bob))
            glow = pygame.Surface((220, 220), pygame.SRCALPHA)
            pulse = abs(math.sin(t * 0.05))
            pygame.draw.circle(glow, (255,220,50, int(80*pulse)), (110,110), 110)
            surf.blit(glow, (SW//2-110, 130))
            draw_text(surf, f"{self.old_name} wurde zu", F_MED, C_GRAY, SW//2, 360, center=True)
            draw_text(surf, self.new_name + "!", F_HUGE, C_YELLOW, SW//2, 390, center=True, shadow=True)
            draw_text(surf, "[ beliebige Taste ]", F_SMALL, C_GRAY, SW//2, 460, center=True)
        add_particles(SW//2, 300, (255,220,80), n=2, size=5)
        update_particles(surf)


# ── Achievement screen ─────────────────────────────────────────────────────────
class AchievementScreen:
    CATEGORIES = ["Alle", "Fangen", "Typen", "Kämpfe", "Lernen", "Abenteuer", "Pokédex"]

    def __init__(self, save, flashcards, all_moonies):
        self.save       = save
        self.flashcards = flashcards
        self.all_moonies= all_moonies
        self.cat_sel    = 0
        self.scroll     = 0
        self.anim_t     = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key
        if k in (pygame.K_ESCAPE, pygame.K_x, pygame.K_a):
            return "close"
        if k in (pygame.K_LEFT, pygame.K_a):
            self.cat_sel = (self.cat_sel - 1) % len(self.CATEGORIES)
            self.scroll = 0
        elif k == pygame.K_RIGHT:
            self.cat_sel = (self.cat_sel + 1) % len(self.CATEGORIES)
            self.scroll = 0
        elif k == pygame.K_UP or k == pygame.K_w:
            self.scroll = max(0, self.scroll - 1)
        elif k == pygame.K_DOWN or k == pygame.K_s:
            self.scroll += 1
        return None

    def draw(self, surf):
        self.anim_t += 1
        surf.fill((8, 10, 20))
        draw_rounded_rect(surf, C_PANEL, (0, 0, SW, 48), 0)
        draw_text(surf, "Achievements", F_BIG, C_YELLOW, SW//2, 5, center=True, shadow=True)
        all_status = ach_module.get_all_status(self.save, self.flashcards, self.all_moonies)
        total_tiers  = sum(len(a["milestones"]) for a,_,_ in all_status)
        unlocked_cnt = sum(t+1 for _,_,t in all_status if t >= 0)
        draw_text(surf, f"{unlocked_cnt}/{total_tiers} freigeschaltet   ESC zurück   ◄► Kategorie   ↑↓ scrollen",
                  F_TINY, C_GRAY, SW//2, 33, center=True)
        tab_w = SW // len(self.CATEGORIES)
        for i, cat in enumerate(self.CATEGORIES):
            sel = (i == self.cat_sel)
            bg  = (40, 60, 120) if sel else (25, 28, 45)
            bdr = C_YELLOW if sel else (50, 55, 75)
            draw_rounded_rect(surf, bg, (i*tab_w+2, 50, tab_w-4, 24), 6, 2 if sel else 1, bdr)
            draw_text(surf, cat, F_TINY, C_YELLOW if sel else C_GRAY, i*tab_w + tab_w//2, 56, center=True)
        cat_filter = self.CATEGORIES[self.cat_sel]
        if cat_filter == "Alle":
            visible = all_status
        else:
            visible = [(a,p,t) for a,p,t in all_status if a["category"] == cat_filter]
        cy = 78 - self.scroll * 80
        card_h = 74
        for a, progress, tier in visible:
            if cy + card_h < 78 or cy > SH:
                cy += card_h + 6
                continue
            milestones = a["milestones"]
            next_tier  = tier + 1
            completed  = (tier >= len(milestones) - 1)
            has_any    = (tier >= 0)
            if completed:
                bg = (30, 55, 30); bdr = C_GREEN
            elif has_any:
                bg = (35, 40, 60); bdr = C_BLUE
            else:
                bg = (20, 22, 35); bdr = (45, 48, 65)
            draw_rounded_rect(surf, bg, (10, cy, SW-20, card_h), 10, 2, bdr)
            draw_text(surf, a["icon"], F_BIG, C_WHITE, 28, cy+8)
            title_col = C_YELLOW if completed else (C_WHITE if has_any else C_GRAY)
            draw_text(surf, a["title"], F_MED, title_col, 60, cy+8, shadow=completed)
            draw_text(surf, a["desc"], F_TINY, C_GRAY, 60, cy+30)
            bx = 60
            for mi, (thresh, label, reward) in enumerate(milestones):
                done = (tier >= mi)
                bc   = C_GREEN if done else (45, 48, 65)
                tc   = C_WHITE if done else (80, 80, 100)
                draw_rounded_rect(surf, bc if done else (25,28,40), (bx, cy+46, 70, 20), 5, 1, bc)
                draw_text(surf, label, F_TINY, tc, bx+35, cy+50, center=True)
                if done:
                    draw_text(surf, "✓", F_TINY, C_GREEN, bx+60, cy+50)
                bx += 75
            if not completed and next_tier < len(milestones):
                nth, nlabel, _ = milestones[next_tier]
                prev_thresh = milestones[next_tier-1][0] if next_tier > 0 else 0
                span = nth - prev_thresh
                val  = max(0, progress - prev_thresh)
                pct  = min(1.0, val / span) if span > 0 else 1.0
                bar_x, bar_w = SW - 230, 200
                pygame.draw.rect(surf, (40,42,60), (bar_x, cy+10, bar_w, 10), border_radius=5)
                if pct > 0:
                    col = C_BLUE if pct < 0.5 else C_YELLOW if pct < 0.9 else C_GREEN
                    pygame.draw.rect(surf, col, (bar_x, cy+10, int(bar_w*pct), 10), border_radius=5)
                draw_text(surf, f"{progress}/{nth}", F_TINY, C_GRAY, bar_x + bar_w//2, cy+23, center=True)
                draw_text(surf, f"→ {nlabel}", F_TINY, C_BLUE, bar_x + bar_w//2, cy+36, center=True)
            elif completed:
                pulse = abs(math.sin(self.anim_t * 0.05))
                star_col = (int(200+55*pulse), int(180+70*pulse), 50)
                draw_text(surf, "★ ABGESCHLOSSEN ★", F_SMALL, star_col, SW-130, cy+22, center=True, shadow=True)
            cy += card_h + 6
        self.scroll = min(self.scroll, max(0, len(visible) - 7))
        draw_notifications(surf)


# ── Card Album screen ─────────────────────────────────────────────────────────
CARD_DROP_CHANCES = {
    "common":    0.08,
    "uncommon":  0.12,
    "rare":      0.18,
    "epic":      0.25,
    "legendary": 0.35,
}
CARD_SHINY_DIVISOR = 20

def try_card_drop(pokemon_name, save):
    m = ALL_MOONIES_DICT.get(pokemon_name)
    if not m:
        return None
    base = CARD_DROP_CHANCES.get(m.rarity, 0.08)
    roll = random.random()
    result = None
    if roll < base / CARD_SHINY_DIVISOR:
        result = "shiny"
    elif roll < base:
        result = "normal"
    if result:
        album = save.setdefault("card_album", {})
        entry = album.setdefault(pokemon_name, {"count": 0, "shiny": 0})
        if result == "shiny":
            entry["shiny"] += 1
        else:
            entry["count"] += 1
        col   = (255, 220, 50) if result == "shiny" else (180, 230, 255)
        label = "✨ GLITZERKARTE" if result == "shiny" else "🃏 Pokémon-Karte"
        notify(f"{label} erhalten: {pokemon_name}!", col, 220)
    return result

def _rarity_card_palette(rarity):
    return {
        "common":    ((200,200,190),(150,152,148),(180,180,170),(100,100,100)),
        "uncommon":  ((160,210,170),(80,150,100),(100,180,120),(60,200,100)),
        "rare":      ((140,190,240),(60,110,200),(80,150,230),(80,160,255)),
        "epic":      ((190,140,240),(110,50,200),(160,80,230),(200,100,255)),
        "legendary": ((255,220,80),(220,140,20),(255,200,40),(255,160,0)),
    }.get(rarity, ((200,200,200),(150,150,150),(170,170,170),(120,120,120)))

def draw_tcg_card(surf, x, y, cw, ch, name, m, is_shiny, anim_t, idx, selected=False, scale=1.0):
    r = m.rarity if m else "common"
    bg_top, bg_bot, border_col, accent = _rarity_card_palette(r)
    if is_shiny:
        bg_top = (255,245,160); bg_bot = (230,185,40); border_col = (255,215,0); accent = (255,200,0)
    outer_col = (255,215,0) if is_shiny else (border_col if not selected else C_YELLOW)
    pygame.draw.rect(surf, outer_col, (x, y, cw, ch), border_radius=10)
    b = 4
    body_x, body_y = x+b, y+b
    body_w, body_h = cw-b*2, ch-b*2
    half = body_h * 6 // 10
    pygame.draw.rect(surf, bg_top, (body_x, body_y, body_w, half), border_radius=8)
    pygame.draw.rect(surf, bg_bot, (body_x, body_y+half, body_w, body_h-half))
    pygame.draw.rect(surf, bg_bot, (body_x, body_y+body_h-10, body_w, 10), border_radius=6)
    inner_s = pygame.Surface((body_w, body_h), pygame.SRCALPHA)
    pygame.draw.rect(inner_s, (255,255,255,80), (0,0,body_w,body_h), 2, border_radius=8)
    surf.blit(inner_s, (body_x, body_y))
    if is_shiny:
        pulse = abs(math.sin(anim_t*0.05 + idx*0.5))
        shim = pygame.Surface((cw, ch), pygame.SRCALPHA)
        for si in range(0, cw, 12):
            h = ((si/cw) + anim_t*0.008) % 1.0
            hi = int(h*6)
            f2 = h*6 - hi
            rc = [(255,int(255*f2),0),(int(255*(1-f2)),255,0),(0,255,int(255*f2)),
                  (0,int(255*(1-f2)),255),(int(255*f2),0,255),(255,0,int(255*(1-f2)))][hi%6]
            shim.fill((*rc, int(22+18*pulse)), rect=(si,0,10,ch))
        surf.blit(shim, (x, y))
    px = body_x + 5; pw2 = body_w - 10; cy2 = body_y + 4
    hdr_h = max(16, int(ch*0.10))
    if m and m.types:
        ec = TYPE_COLORS.get(m.types[0], (150,150,150))
        pygame.draw.circle(surf, ec, (px+8, cy2+hdr_h//2), 8)
        pygame.draw.circle(surf, (255,255,255), (px+8, cy2+hdr_h//2), 8, 1)
        name_x = px + 20
    else:
        name_x = px
    short = name if len(name) <= 11 else name[:10]+"."
    surf.blit(F_TINY.render(short, True, (200,200,200)), (name_x+1, cy2+2))
    surf.blit(F_TINY.render(short, True, (20,20,20)), (name_x, cy2+1))
    if m:
        hp_s = F_TINY.render(f"HP {m.max_hp}", True, (200,30,30))
        surf.blit(hp_s, (body_x+body_w-hp_s.get_width()-4, cy2+2))
    cy2 += hdr_h
    stage_map = {"common":"Basic","uncommon":"Basic","rare":"Stage 1","epic":"Stage 2","legendary":"MEGA"}
    stage = stage_map.get(r, "Basic")
    surf.blit(F_TINY.render(stage, True, (60,60,60)), (px, cy2))
    if m:
        r_col = m.get_rarity_color()
        ri_s = F_TINY.render(r.capitalize(), True, r_col)
        surf.blit(ri_s, (body_x+body_w-ri_s.get_width()-4, cy2))
    cy2 += 13
    img_h = int(ch*0.38); img_pad = 3
    img_bx = px-1; img_bw = pw2+2
    img_bg = (245,240,225) if not is_shiny else (255,252,210)
    pygame.draw.rect(surf, img_bg, (img_bx, cy2, img_bw, img_h), border_radius=4)
    pygame.draw.rect(surf, (160,140,80), (img_bx, cy2, img_bw, img_h), 2, border_radius=4)
    pygame.draw.rect(surf, (220,200,130), (img_bx+2, cy2+2, img_bw-4, img_h-4), 1, border_radius=3)
    if m:
        isz = min(img_bw-img_pad*2-4, img_h-img_pad*2-2)
        img = load_img(m.image, (isz, isz))
        surf.blit(img, (img_bx+(img_bw-isz)//2, cy2+(img_h-isz)//2))
    if is_shiny:
        pulse2 = abs(math.sin(anim_t*0.07+idx*0.3))
        shim2 = pygame.Surface((img_bw, img_h), pygame.SRCALPHA)
        for si in range(0, img_bw, 10):
            shim2.fill((255,255,180,int(30*pulse2)), rect=(si,0,5,img_h))
        surf.blit(shim2, (img_bx, cy2))
    cy2 += img_h + 3
    if m:
        tbw = min(34, pw2//max(len(m.types),1)-3); tx2 = px
        for t in m.types:
            tc = TYPE_COLORS.get(t, (150,150,150))
            pygame.draw.rect(surf, tc, (tx2, cy2, tbw, 11), border_radius=5)
            pygame.draw.rect(surf, (255,255,255), (tx2, cy2, tbw, 11), 1, border_radius=5)
            lb = F_TINY.render(t[:4], True, C_WHITE)
            surf.blit(lb, (tx2+tbw//2-lb.get_width()//2, cy2+1)); tx2 += tbw+4
    cy2 += 14
    desc_h = int(ch*0.10)
    pygame.draw.rect(surf, (235,228,210), (px, cy2, pw2, desc_h), border_radius=3)
    pygame.draw.rect(surf, (180,160,100), (px, cy2, pw2, desc_h), 1, border_radius=3)
    if m:
        fl_s = F_TINY.render(f"{m.rarity.capitalize()} Pokémon. Lvl {m.level}.", True, (60,50,30))
        surf.blit(fl_s, (px+3, cy2+2))
    cy2 += desc_h + 3
    atk_h = int(ch*0.11)
    pygame.draw.rect(surf, (220,215,200), (px, cy2, pw2, atk_h), border_radius=3)
    pygame.draw.rect(surf, (160,140,80), (px, cy2, pw2, atk_h), 1, border_radius=3)
    if m:
        if m.types:
            ec2 = TYPE_COLORS.get(m.types[0], (150,150,150))
            pygame.draw.circle(surf, ec2, (px+8, cy2+atk_h//2), 6)
            pygame.draw.circle(surf, (255,255,255), (px+8, cy2+atk_h//2), 6, 1)
        move_name = "Tackle" if r=="common" else ("Angriff" if r=="uncommon" else
                    ("Spezial" if r=="rare" else ("Mega-Angriff" if r=="epic" else "ULTRA-MOVE")))
        surf.blit(F_TINY.render(move_name, True, (30,30,30)), (px+18, cy2+2))
        dmg_s = F_SMALL.render(str(m.attack*10), True, (20,20,20))
        surf.blit(dmg_s, (body_x+body_w-dmg_s.get_width()-5, cy2+1))
    cy2 += atk_h + 3
    foot_y = body_y + body_h - 16
    pygame.draw.line(surf, (160,140,80), (px, foot_y-1), (px+pw2, foot_y-1), 1)
    if m:
        wk_t = m.types[-1] if m.types else "Normal"
        surf.blit(F_TINY.render(f"Schwäche: {wk_t[:5]}", True, (80,40,40)), (px, foot_y+1))
        retreat = {"common":1,"uncommon":1,"rare":2,"epic":3,"legendary":4}.get(r,1)
        for ri2 in range(retreat):
            pygame.draw.circle(surf, (60,60,60), (px+pw2-6-ri2*13, foot_y+7), 5)
            pygame.draw.circle(surf, (120,120,120), (px+pw2-6-ri2*13, foot_y+7), 5, 1)
    star_y = foot_y - 11
    if is_shiny:
        shiny_col = (255, int(200+55*abs(math.sin(anim_t*0.08+idx))), 0)
        sh_s = F_TINY.render("✦ SHINY ✦", True, shiny_col)
        surf.blit(sh_s, (px+pw2//2-sh_s.get_width()//2, star_y))
    else:
        n_stars = {"common":1,"uncommon":2,"rare":3,"epic":4,"legendary":5}.get(r,1)
        sym = "●" if r in ("common","uncommon") else ("◆" if r=="rare" else ("★" if r=="epic" else "✦"))
        st_s = F_TINY.render(sym*n_stars, True, accent)
        surf.blit(st_s, (px+pw2//2-st_s.get_width()//2, star_y))
    if selected:
        glow = pygame.Surface((cw+10, ch+10), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255,220,50,90), (0,0,cw+10,ch+10), border_radius=14)
        surf.blit(glow, (x-5, y-5))


class CardAlbumScreen:
    COLS = 5
    ROWS = 4
    PER_PAGE = COLS * ROWS

    def __init__(self, save):
        self.save   = save
        self.sel    = 0
        self.filter = "all"
        self.anim_t = 0
        self.detail = None

    def _visible(self):
        album = self.save.get("card_album", {})
        names = sorted(album.keys())
        if self.filter == "normal":
            names = [n for n in names if album[n].get("count",0) > 0]
        elif self.filter == "shiny":
            names = [n for n in names if album[n].get("shiny",0) > 0]
        elif self.filter == "dupes":
            names = [n for n in names if (album[n].get("count",0)+album[n].get("shiny",0)) > 1]
        return names

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key
        if self.detail:
            self.detail = None
            return None
        if k in (pygame.K_ESCAPE, pygame.K_x):
            return "close"
        vis = self._visible()
        if k == pygame.K_LEFT:
            self.sel = max(0, self.sel-1)
        elif k == pygame.K_RIGHT:
            self.sel = min(len(vis)-1, self.sel+1)
        elif k == pygame.K_UP:
            self.sel = max(0, self.sel-self.COLS)
        elif k == pygame.K_DOWN:
            self.sel = min(len(vis)-1, self.sel+self.COLS)
        elif k in (pygame.K_RETURN, pygame.K_z):
            if vis:
                self.detail = vis[self.sel]
        elif k == pygame.K_f:
            filters = ["all","normal","shiny","dupes"]
            self.filter = filters[(filters.index(self.filter)+1) % len(filters)]
            self.sel = 0
        return None

    def draw(self, surf):
        self.anim_t += 1
        surf.fill((18, 38, 24))
        for gx in range(0, SW, 30):
            pygame.draw.line(surf, (22,44,28), (gx,0),(gx,SH))
        for gy in range(0, SH, 30):
            pygame.draw.line(surf, (22,44,28), (0,gy),(SW,gy))
        album = self.save.get("card_album", {})
        total_unique = len(album)
        total_cards  = sum(v.get("count",0)+v.get("shiny",0) for v in album.values())
        total_shiny  = sum(v.get("shiny",0) for v in album.values())
        draw_rounded_rect(surf, (12,28,18), (0,0,SW,50), 0)
        pygame.draw.line(surf, (80,180,80), (0,50),(SW,50), 2)
        draw_text(surf, "📖 Karten-Album", F_BIG, C_YELLOW, SW//2, 4, center=True, shadow=True)
        filter_labels = {"all":"Alle","normal":"Normal","shiny":"✨ Glitzer","dupes":"Doppelte"}
        fl = filter_labels.get(self.filter, "Alle")
        draw_text(surf, f"{total_unique} versch. | {total_cards} gesamt | {total_shiny} ✨  |  [F] Filter: {fl}  |  ENTER Detail  |  ESC zurück",
                  F_TINY, (160,220,160), SW//2, 35, center=True)
        vis = self._visible()
        if not vis:
            draw_text(surf, "Keine Karten in dieser Kategorie.", F_MED, C_GRAY, SW//2, SH//2, center=True)
            draw_notifications(surf)
            return
        cw, ch = 148, 207
        cols = 5
        total_w = cols*cw + (cols-1)*6
        pad_x = (SW-total_w)//2; pad_y = 56
        visible_rows = max(1, (SH-pad_y-30)//(ch+8))
        per_page = cols*visible_rows
        page  = self.sel//per_page
        start = page*per_page
        end   = min(start+per_page, len(vis))
        for i, idx in enumerate(range(start, end)):
            name  = vis[idx]
            entry = album.get(name, {})
            cnt   = entry.get("count",0); shiny = entry.get("shiny",0)
            m     = ALL_MOONIES_DICT.get(name)
            col_i = i%cols; row_i = i//cols
            x = pad_x + col_i*(cw+6); y = pad_y + row_i*(ch+8)
            sel = (idx == self.sel)
            draw_tcg_card(surf, x, y, cw, ch, name, m, is_shiny=(shiny>0), anim_t=self.anim_t, idx=idx, selected=sel)
            total_owned = cnt+shiny
            if total_owned > 1:
                bx2, by2 = x+cw-18, y+ch-18
                pygame.draw.circle(surf, (30,30,30), (bx2,by2), 12)
                pygame.draw.circle(surf, C_YELLOW, (bx2,by2), 12, 2)
                draw_text(surf, str(total_owned), F_TINY, C_YELLOW, bx2, by2-5, center=True)
        total_pages = max(1,(len(vis)+per_page-1)//per_page)
        draw_text(surf, f"◄  Seite {page+1}/{total_pages}  ►", F_TINY, (160,220,160), SW//2, SH-14, center=True)
        if self.detail:
            self._draw_detail(surf, self.detail, album.get(self.detail,{}))
        draw_notifications(surf)

    def _draw_detail(self, surf, name, entry):
        overlay = pygame.Surface((SW,SH), pygame.SRCALPHA)
        overlay.fill((0,0,0,200))
        surf.blit(overlay,(0,0))
        m = ALL_MOONIES_DICT.get(name)
        has_shiny = entry.get("shiny",0) > 0
        cnt = entry.get("count",0); shiny = entry.get("shiny",0)
        cw2, ch2 = 280, 392
        cx = SW//2-cw2//2; cy = SH//2-ch2//2-20
        draw_tcg_card(surf, cx, cy, cw2, ch2, name, m, is_shiny=has_shiny, anim_t=self.anim_t, idx=0, selected=False)
        info_y = cy+ch2+8
        draw_text(surf, f"Normale Karten: {cnt}   ✨ Glitzerkarten: {shiny}", F_MED, C_YELLOW, SW//2, info_y, center=True)
        if has_shiny:
            pulse = abs(math.sin(self.anim_t*0.07))
            sc = (255, int(200+55*pulse), 0)
            draw_text(surf,"✨ GLITZERKARTE IM BESITZ ✨", F_SMALL, sc, SW//2, info_y+28, center=True, shadow=True)
        draw_text(surf,"[ beliebige Taste ] schließen", F_TINY, C_GRAY, SW//2, SH-16, center=True)



# ══════════════════════════════════════════════════════════════════════════════
# RANG-SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

RANKS = [
    (0,    "Bronze",  (180, 100,  40), 0),
    (100,  "Silber",  (180, 190, 200), 100),
    (300,  "Gold",    (255, 210,  50), 300),
    (700,  "Platin",  (140, 200, 255), 700),
    (1500, "Meister", (220,  80, 220), 1500),
]

def get_rank_info(rank_points):
    """Return (tier_idx, name, color, points_needed_for_next)."""
    tier = 0
    for i, (thresh, name, col, _) in enumerate(RANKS):
        if rank_points >= thresh:
            tier = i
    nxt_thresh = RANKS[tier+1][0] if tier+1 < len(RANKS) else None
    name  = RANKS[tier][1]
    col   = RANKS[tier][2]
    return tier, name, col, nxt_thresh

def add_rank_points(save, points, label=""):
    old_pts  = save.get("rank_points", 0)
    new_pts  = old_pts + points
    save["rank_points"] = new_pts
    old_tier, _, _, _ = get_rank_info(old_pts)
    new_tier, new_name, new_col, _ = get_rank_info(new_pts)
    if new_tier > old_tier:
        save["rank"] = new_tier
        notify(f"🏆 RANG AUFGESTIEGEN: {new_name}!", new_col, 300)
    elif points > 0 and label:
        notify(f"+{points} RP  ({label})", (200, 220, 255), 120)

# ══════════════════════════════════════════════════════════════════════════════
# POKÉDEX-BESCHREIBUNGEN
# ══════════════════════════════════════════════════════════════════════════════

# ── Type effectiveness chart ────────────────────────────────────────────────
# For each attacking type: {defending_type: multiplier}
TYPE_CHART = {
    "Feuer":   {"Pflanze":2,"Eis":2,"Käfer":2,"Stahl":2, "Feuer":0.5,"Wasser":0.5,"Gestein":0.5,"Drache":0.5},
    "Wasser":  {"Feuer":2,"Boden":2,"Gestein":2,          "Wasser":0.5,"Pflanze":0.5,"Drache":0.5},
    "Pflanze": {"Wasser":2,"Boden":2,"Gestein":2,          "Feuer":0.5,"Pflanze":0.5,"Gift":0.5,"Flug":0.5,"Käfer":0.5,"Drache":0.5,"Stahl":0.5},
    "Elektro": {"Wasser":2,"Flug":2,                       "Pflanza":0.5,"Elektro":0.5,"Drache":0.5,"Boden":0},
    "Eis":     {"Pflanze":2,"Boden":2,"Flug":2,"Drache":2, "Feuer":0.5,"Wasser":0.5,"Eis":0.5,"Stahl":0.5},
    "Kampf":   {"Normal":2,"Eis":2,"Gestein":2,"Dunkel":2,"Stahl":2, "Gift":0.5,"Flug":0.5,"Psycho":0.5,"Käfer":0.5,"Fee":0.5,"Geist":0},
    "Gift":    {"Pflanze":2,"Fee":2,                        "Gift":0.5,"Boden":0.5,"Gestein":0.5,"Geist":0.5,"Stahl":0},
    "Boden":   {"Feuer":2,"Elektro":2,"Gift":2,"Gestein":2,"Stahl":2, "Pflanze":0.5,"Käfer":0.5,"Flug":0},
    "Flug":    {"Pflanze":2,"Kampf":2,"Käfer":2,            "Elektro":0.5,"Gestein":0.5,"Stahl":0.5},
    "Psycho":  {"Kampf":2,"Gift":2,                         "Psycho":0.5,"Stahl":0.5,"Dunkel":0},
    "Käfer":   {"Pflanze":2,"Psycho":2,"Dunkel":2,          "Feuer":0.5,"Kampf":0.5,"Flug":0.5,"Geist":0.5,"Stahl":0.5,"Fee":0.5},
    "Gestein": {"Feuer":2,"Eis":2,"Flug":2,"Käfer":2,       "Kampf":0.5,"Boden":0.5,"Stahl":0.5},
    "Geist":   {"Geist":2,"Psycho":2,                       "Normal":0,"Dunkel":0.5},
    "Drache":  {"Drache":2,                                 "Stahl":0.5,"Fee":0},
    "Dunkel":  {"Geist":2,"Psycho":2,                       "Kampf":0.5,"Dunkel":0.5,"Fee":0.5},
    "Stahl":   {"Eis":2,"Gestein":2,"Fee":2,                "Feuer":0.5,"Wasser":0.5,"Elektro":0.5,"Stahl":0.5},
    "Fee":     {"Kampf":2,"Drache":2,"Dunkel":2,            "Feuer":0.5,"Gift":0.5,"Stahl":0.5},
    "Normal":  {},
}

def get_type_matchups(types):
    """Given a list of defending types, return {type: multiplier} for all attacking types."""
    result = {}
    all_types = list(TYPE_CHART.keys())
    for atk in all_types:
        mult = 1.0
        for def_t in types:
            mult *= TYPE_CHART.get(atk, {}).get(def_t, 1.0)
        if mult != 1.0:
            result[atk] = mult
    return result

# ── Pokémon size & weight data ────────────────────────────────────────────────
MOONIE_SIZE_WEIGHT = {
    "Bisasam":("0.7m","6.9kg"), "Bisaknosp":("1.0m","13.0kg"), "Bisaflor":("2.0m","100.0kg"),
    "Glumanda":("0.6m","8.5kg"), "Glutexo":("1.1m","19.0kg"), "Glurak":("1.7m","90.5kg"),
    "Schiggy":("0.5m","9.0kg"), "Schillok":("1.0m","22.5kg"), "Turtok":("1.6m","85.5kg"),
    "Raupi":("0.3m","2.9kg"), "Safcon":("0.7m","9.9kg"), "Smettbo":("1.1m","32.0kg"),
    "Hornliu":("0.3m","2.9kg"), "Kokuna":("0.6m","10.2kg"), "Bibor":("1.0m","29.5kg"),
    "Taubsi":("0.3m","1.8kg"), "Tauboga":("0.6m","15.0kg"), "Tauboss":("1.5m","29.5kg"),
    "Rattfratz":("0.3m","3.5kg"), "Rattikarl":("0.7m","18.5kg"),
    "Pichu":("0.3m","2.0kg"), "Pikachu":("0.4m","6.0kg"), "Raichu":("0.8m","30.0kg"),
    "Abra":("0.9m","19.5kg"), "Kadabra":("1.3m","56.5kg"), "Simsala":("1.5m","48.0kg"),
    "Machollo":("0.8m","19.5kg"), "Maschock":("1.5m","70.5kg"), "Machomei":("1.6m","130.0kg"),
    "Dratini":("1.8m","3.3kg"), "Dragonir":("4.0m","16.5kg"), "Dragoran":("2.2m","210.0kg"),
    "Evoli":("0.3m","6.5kg"), "Blitza":("0.9m","24.5kg"), "Aquana":("1.0m","29.0kg"),
    "Flamara":("0.9m","25.0kg"), "Folipurba":("1.0m","29.5kg"), "Nachtara":("1.0m","27.0kg"),
    "Glaziola":("0.9m","25.9kg"), "Feelinara":("0.9m","23.5kg"), "Psiana":("0.9m","26.3kg"),
    "Pummeluff":("0.5m","5.5kg"), "Knuddeluff":("1.0m","13.5kg"),
    "Mauzi":("0.4m","4.2kg"), "Snobilikat":("1.0m","32.0kg"),
    "Sleima":("0.9m","32.0kg"), "Sleimok":("1.7m","65.0kg"),
}

def get_moonie_size_weight(name):
    return MOONIE_SIZE_WEIGHT.get(name, ("?m", "?kg"))

POKEDEX_ENTRIES = {
    "Bisasam":    "Ein seltsames Samenkorn wurde bei seiner Geburt auf seinen Rücken gepflanzt. Es kann einige Zeit dauern, bis es keimt.",
    "Bisaknosp":  "Wenn die Blütenknospe auf seinem Rücken zu erblühen beginnt, wird sein Körpergeruch schärfer und stärker.",
    "Bisaflor":   "Die Blume auf seinem Rücken fängt nach dem Regen Sonnenstrahlen ein. Sie ist weicher als sie aussieht.",
    "Glumanda":   "Offensichtlich zieht es Hitze vor. Wenn es regnet, soll aus der Flamme an seinem Schwanz Dampf strömen.",
    "Glutexo":    "Wenn es zornig wird, speit es heiße Flammen und erschreckt den Feind. Es wächst kontinuierlich.",
    "Glurak":     "Es speit Feuer so heiß, dass es Felsen schmelzen kann. Es verursacht Waldbrände, wenn es außer Kontrolle gerät.",
    "Schiggy":    "Wenn es seinen weichen Körper in seinem Panzer birgt, ist es gegen alle Arten von Angriffen geschützt.",
    "Schillok":   "Es verstärkt seinen Panzer, indem es seine Muskeln zusammenzieht. Weder Wasser noch Wind können ihn durchdringen.",
    "Turtok":     "Es quetscht seinen Körper in seinen Panzer und schießt Wasser aus seinen Düsen. Es kann einen kleinen Hügel hinabstürzen.",
    "Raupi":      "Es frisst seine Gewicht in Blättern jeden Tag. Es benutzt die Fühler auf seinem Kopf, um die Feuchtigkeit zu messen.",
    "Safcon":     "Es schützt seinen weichen Körper durch Aushärten seiner Hülle. Es bereitet sich auf die Metamorphose vor.",
    "Smettbo":    "Die Schuppen seiner Flügel, die wie Augen aussehen, können Angst einflößen. Es tanzt anmutig in der Luft.",
    "Hornliu":    "Es wickelt sich selbst in weicher Seide aus seinem Mund ein. Wenn es bedroht wird, streckt es seine spitzen Hörner heraus.",
    "Kokuna":     "Es bleibt bewegungslos, während es in einem Kokon wartet. Innerlich bereitet es sich für seine Entwicklung vor.",
    "Bibor":      "Obwohl es ein fleißiger Sammler von Nektar ist, kann sein Gift soll der stärkste unter den Insekten-Pokémon sein.",
    "Taubsi":     "Ein sehr verbreitetes Pokémon. Es ist beliebt, weil es so einfach zu fangen ist, macht sich also niemand die Mühe, es zu fangen.",
    "Tauboga":    "Wenn es die Flügel schlägt, fühlt es sich trotz seines Gewichts leicht an. Seine Augen können auch kleine Bewegungen erfassen.",
    "Tauboss":    "Es kann seinen Heimatort immer finden, egal wo es sich befindet. Eine Gruppe von ihnen war im Besitz von Meistern.",
    "Rattfratz":  "Ein Pokémon, das sein Territorium markiert und es mit seinen scharfen Zähnen verteidigt.",
    "Rattikarl":  "Sehr neugierige Pokémon, gefährlich wenn gereizt. Es kann Beton mit seinen langen Schneidezähnen durchbeißen.",
    "Habitak":    "Es fliegt Überpatrouillen seines Territoriums. Wenn es ein Ziel entdeckt, taucht es aus dem Himmel wie eine Bombe.",
    "Ibitak":     "Es ist immer wachsam. Wenn sein Kamm aufersteht, ist es bereit für sofortige Aktion.",
    "Pichu":      "Es ist noch nicht in der Lage, die Elektrizität, die es erzeugt, vollständig zu speichern. Es wird oft von seinem eigenen Schock überrascht.",
    "Pikachu":    "Es sammelt Blitze, wenn es sich mit anderen balgt. Es speichert Strom in seinen Wangenbeuteln.",
    "Raichu":     "Wenn sich überschüssige Energie in seinem Körper angesammelt hat, wird sein Charakter unruhig.",
    "Pummeluff":  "Es rollt sich zusammen, um seinen Körper aufzublähen. Es singt auf einer Frequenz, die für menschliche Ohren unhörbar ist.",
    "Knuddeluff": "Sein Gesang hat die Kraft, den Gegner einzuschläfern. Seine rosigen Wangen sind sein Merkmal.",
    "Mauzi":      "Sein Schatz sind handtellergroße Münzen. Wer eine besitzt, soll Glück haben.",
    "Snobilikat":  "In alten Königshöfen wurde es hoch verehrt. Es leckt seine Pfoten und wischt damit seinen Körper.",
    "Enton":      "Es ist selten anzutreffen. Wenn zwei von ihnen zusammen angetroffen werden, wird ein Glücksbringer gesagt.",
    "Entoron":    "Es bevorzugt feuchte Lebensräume. Es wohnt an Seen und Teichen und ernährt sich von kleinen Fischen.",
    "Abra":       "Es schläft 18 Stunden am Tag. Auch wenn es schläft, kann es Teleportation benutzen.",
    "Kadabra":    "Es hält immer einen Löffel in der Hand. Der Löffel ist gebogen, wenn er aus einem dicken Metall geformt wurde.",
    "Simsala":    "Es ist berühmt für seine Hellsicht. Durch Zusammenfalten seiner Löffel kann es überall teleportieren.",
    "Machollo":   "Es liebt es zu trainieren. Es trainiert stundenlang ohne Pause, egal wie hart das Training ist.",
    "Maschock":   "Sein Körper ist durchdrungen mit Hochspannungsmuskeln. Die Bluttransfusionen in seinen Muskeln machen ihn außergewöhnlich stark.",
    "Machomei":   "Obwohl es die Kraft hat, eine Bergkette zu bewegen, genießt es sanftes Training.",
    "Knofensa":   "Wenn sich das Bulb auf seinem Rücken öffnet, strömt ein erstickender Geruch heraus.",
    "Ultrigaria":  "Die Sporen auf seinem Schirm verbreiten sich mit dem Wind. Giftige Sporen bedecken seinen Schirm.",
    "Sleima":     "Es ist ein Pokémon aus Schleim. Wenn zwei von ihnen zusammenstoßen, kombinieren sie sich.",
    "Sleimok":    "Es ist eine Ansammlung von Schleim. Es ist harmlos, wenn es alleine ist, aber wenn es mit anderen fusioniert, vergrößert es sich.",
    "Krabby":     "Es hält Balance mit seinen Augen, die auf langen Stielen befestigt sind.",
    "Kingler":    "Seine große Klaue hat sich so weit entwickelt, dass sie 10.000 Pferdestärken Kraft besitzt. Es ist so schwer, dass es schwer zu kontrollieren ist.",
    "Magnetilo":  "Es wird von magnetischen Kräften angezogen. Es sammelt sich oft in der Nähe von Kraftwerken.",
    "Magneton":   "Drei Magnetilo verbinden sich, wenn ihre Körper zu magnetisch werden. Eine starke Magnetkraft umhüllt sein Inneres.",
    "Voltilamm":  "Das weiche Vlies auf seinem Körper ist ein natürlicher Isolator, der statische Elektrizität hält.",
    "Lektrobal":  "Ein seltenes Pokémon. Wenn nach einem Sommergewitter das Gras aufflammt, wird manchmal Lektrobal gefunden.",
    "Dratini":    "Es verbirgt sich in tiefen Gewässern. Es wächst, indem es immer wieder häutet.",
    "Dragonir":   "Es wird selten beobachtet, wie es aus dem Wasser taucht. Es schläft auf dem Grund von Seen.",
    "Dragoran":   "Es ist mächtig genug, eine Runde der Erde in einem Tag zu fliegen.",
    "Evoli":      "Es ist beliebt als Haustier. Seine ungewöhnliche Genetik erlaubt ihm, sich in vielfältige Formen zu entwickeln.",
    "Blitza":     "Sein gesamter Körper ist von elektrischer Energie bedeckt. Es kann Blitze mit großer Präzision entladen.",
    "Aquana":     "Wenn es kämpft, hüllt es seinen ganzen Körper in Wasser. Es steuert Wasser mit seinem Verstand.",
    "Flamara":    "Wenn es kämpft, hüllt es seinen ganzen Körper in Feuer. Es greift an, ohne zu zögern.",
    "Folipurba":  "Es zieht im Blattwerk von Bäumen. Es kann auf rauem Terrain laufen, ohne einen Laut zu machen.",
    "Nachtara":   "Es bewegt sich lautlos durch Dunkelheit. Seine roten Augen leuchten in der dunkelsten Nacht.",
    "Glaziola":   "Es hat einen Körper aus Eis. Es taut nie auf, egal wie heiß es wird.",
    "Feelinara":  "Es kommuniziert durch Gefühle. Es fühlt die Herzfrequenz seiner Begleiter und beruhigt sie.",
    "Vegimak":    "Es basiert auf pflanzlichem Material. Es absorbiert Sonnenlicht zur Energiegewinnung.",
    "Psiana":     "Ein psychisches Pokémon von großer Macht. Es kann Gedanken lesen und manipulieren.",
}

def get_pokedex_entry(name):
    return POKEDEX_ENTRIES.get(name, "Über dieses Pokémon ist noch wenig bekannt. Weitere Forschung wird empfohlen.")


# ══════════════════════════════════════════════════════════════════════════════
# FREUNDSCHAFTS-SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

FRIENDSHIP_LEVELS = [
    (0,   "Fremd",      (120, 120, 140), ""),
    (30,  "Bekannt",    (140, 170, 200), ""),
    (80,  "Vertraut",   (100, 200, 140), "💚"),
    (150, "Freund",     (80,  200, 220), "💙"),
    (220, "Bester Freund", (220, 180, 50), "💛"),
    (255, "Seelenpartner", (255, 100, 200), "💖"),
]

def get_friendship(save, name):
    return save.get("friendship", {}).get(name, 0)

def add_friendship(save, name, amount):
    d = save.setdefault("friendship", {})
    old = d.get(name, 0)
    new_val = min(255, old + amount)
    d[name] = new_val
    # Check if tier crossed
    def tier(v):
        t = 0
        for i,(thresh,*_) in enumerate(FRIENDSHIP_LEVELS):
            if v >= thresh: t = i
        return t
    if tier(new_val) > tier(old) and amount > 0:
        _, lname, lcol, icon = FRIENDSHIP_LEVELS[tier(new_val)]
        notify(f"{icon} {name} mag dich jetzt mehr! ({lname})", lcol, 200)

def get_friendship_label(save, name):
    val = get_friendship(save, name)
    label, col, icon = FRIENDSHIP_LEVELS[0][1], FRIENDSHIP_LEVELS[0][2], ""
    for thresh, lname, lcol, licon in FRIENDSHIP_LEVELS:
        if val >= thresh:
            label, col, icon = lname, lcol, licon
    return val, label, col, icon

def friendship_dmg_bonus(save, name):
    """Return damage multiplier based on friendship (1.0 - 1.25)."""
    val = get_friendship(save, name)
    return 1.0 + (val / 255) * 0.25


# ══════════════════════════════════════════════════════════════════════════════
# STATUSEFFEKTE
# ══════════════════════════════════════════════════════════════════════════════

# status: None | "burn" | "poison" | "sleep" | "paralyze" | "freeze"
STATUS_DATA = {
    "burn":     {"icon":"🔥","label":"Verbrennung","col":(255,100,40),  "dot_pct":0.08},
    "poison":   {"icon":"☠","label":"Vergiftung",  "col":(180,60,220),  "dot_pct":0.10},
    "sleep":    {"icon":"💤","label":"Schlaf",      "col":(140,140,200), "dot_pct":0},
    "paralyze": {"icon":"⚡","label":"Lähmung",     "col":(240,220,40),  "dot_pct":0},
    "freeze":   {"icon":"❄","label":"Eingefroren", "col":(100,200,255), "dot_pct":0},
}

def apply_status_end_of_turn(moonie, log_fn):
    """Apply DoT and chance-to-cure. Returns True if still has status."""
    st = getattr(moonie, "status", None)
    if not st: return False
    data = STATUS_DATA.get(st, {})
    # DoT damage
    dot = data.get("dot_pct", 0)
    if dot > 0:
        dmg = max(1, int(moonie.max_hp * dot))
        moonie.take_damage(dmg)
        log_fn(f"{data['icon']} {moonie.name} leidet unter {data['label']}! -{dmg} HP")
    # Sleep: 33% chance to wake each turn
    if st == "sleep":
        if random.random() < 0.33:
            moonie.status = None
            log_fn(f"💤 {moonie.name} ist aufgewacht!")
            return False
    # Freeze: 20% chance to thaw
    if st == "freeze":
        if random.random() < 0.20:
            moonie.status = None
            log_fn(f"❄ {moonie.name} ist aufgetaut!")
            return False
    return True

def try_inflict_status(moonie, status, log_fn, chance=0.25):
    """Try to inflict status. Returns True on success."""
    if getattr(moonie, "status", None): return False  # already has status
    if random.random() < chance:
        moonie.status = status
        data = STATUS_DATA[status]
        log_fn(f"{data['icon']} {moonie.name} ist jetzt {data['label']}!")
        return True
    return False

# ══════════════════════════════════════════════════════════════════════════════
# WETTER-SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

WEATHER_LIST = [
    {"name": "Klar",      "icon": "☀",  "color": (255, 220, 80),  "type_bonus": None,        "spawn_mod": {}},
    {"name": "Regen",     "icon": "🌧",  "color": (80,  140, 220), "type_bonus": "Wasser",    "spawn_mod": {"Wasser": 2.5}},
    {"name": "Gewitter",  "icon": "⛈",  "color": (80,  80,  180), "type_bonus": "Elektro",   "spawn_mod": {"Elektro": 3.0, "Wasser": 1.5}},
    {"name": "Schnee",    "icon": "❄",  "color": (200, 230, 255), "type_bonus": "Eis",        "spawn_mod": {"Eis": 3.0}},
    {"name": "Nebel",     "icon": "🌫",  "color": (180, 180, 200), "type_bonus": "Geist",     "spawn_mod": {"Geist": 2.5, "Normal": 0.5}},
    {"name": "Sonnig",    "icon": "🌞",  "color": (255, 180, 50),  "type_bonus": "Feuer",     "spawn_mod": {"Feuer": 2.5, "Pflanze": 1.5}},
    {"name": "Sandsturm", "icon": "🌪",  "color": (200, 160, 80),  "type_bonus": "Boden",     "spawn_mod": {"Boden": 2.5, "Gestein": 2.0}},
    {"name": "Windig",    "icon": "💨",  "color": (160, 220, 200), "type_bonus": "Flug",      "spawn_mod": {"Flug": 2.5, "Drache": 1.5}},
]

def get_today_weather(save):
    today = _today_str()
    if save.get("weather_date") == today:
        name = save.get("weather", "Klar")
        return next((w for w in WEATHER_LIST if w["name"] == name), WEATHER_LIST[0])
    # New day — pick weather from date seed
    day_seed = int(_dt.date.today().strftime("%Y%m%d"))
    rng = random.Random(day_seed + 7)   # +7 offset to differ from quiz seed
    w = rng.choice(WEATHER_LIST)
    save["weather_date"] = today
    save["weather"] = w["name"]
    return w

def weather_modified_pool(base_pool, weather):
    """Return a weighted pool based on today's weather spawn modifiers."""
    mods = weather.get("spawn_mod", {})
    if not mods:
        return base_pool
    weighted = []
    for m in base_pool:
        weight = 1
        for t in m.types:
            if t in mods:
                weight = max(weight, mods[t])
        weighted.extend([m] * max(1, int(weight)))
    return weighted if weighted else base_pool


# ══════════════════════════════════════════════════════════════════════════════
# GILDEN-CHALLENGES
# ══════════════════════════════════════════════════════════════════════════════

CHALLENGE_TEMPLATES = [
    {"id": "catch_3",      "desc": "Fange 3 Pokémon",             "goal": 3,  "reward_coins": 150,  "stat": "total_catches",           "delta": True},
    {"id": "catch_5",      "desc": "Fange 5 Pokémon",             "goal": 5,  "reward_coins": 300,  "stat": "total_catches",           "delta": True},
    {"id": "win_3",        "desc": "Gewinne 3 Kämpfe",            "goal": 3,  "reward_coins": 200,  "stat": "battles_won",             "delta": True},
    {"id": "win_5",        "desc": "Gewinne 5 Kämpfe",            "goal": 5,  "reward_coins": 400,  "stat": "battles_won",             "delta": True},
    {"id": "trainer_2",    "desc": "Besiege 2 Trainer",           "goal": 2,  "reward_coins": 350,  "stat": "trainer_battles_won",     "delta": True},
    {"id": "rocket_1",     "desc": "Besiege 1 Team Rocket-Trainer","goal":1,  "reward_coins": 500,  "stat": "rocket_battles_won",      "delta": True},
    {"id": "steps_500",    "desc": "Laufe 500 Schritte",          "goal": 500,"reward_coins": 100,  "stat": "step_count",              "delta": True},
    {"id": "steps_1000",   "desc": "Laufe 1000 Schritte",         "goal":1000,"reward_coins": 250,  "stat": "step_count",              "delta": True},
    {"id": "daily_event",  "desc": "Spiele das Tages-Event",       "goal": 1,  "reward_coins": 200,  "stat": "daily_event_streak",      "delta": False},
    {"id": "cards_5",      "desc": "Beantworte 5 Lernkarten",     "goal": 5,  "reward_coins": 150,  "stat": "cards_correct_total",     "delta": True},
    {"id": "cards_10",     "desc": "Beantworte 10 Lernkarten",    "goal": 10, "reward_coins": 300,  "stat": "cards_correct_total",     "delta": True},
    {"id": "evolve_1",     "desc": "Entwickle 1 Pokémon",         "goal": 1,  "reward_coins": 300,  "stat": "evolution_count",         "delta": True},
]

def get_today_challenges(save):
    today = _today_str()
    if save.get("guild_date") == today and save.get("guild_challenges"):
        return save["guild_challenges"]
    # New day — pick 3 challenges via date seed
    day_seed = int(_dt.date.today().strftime("%Y%m%d"))
    rng = random.Random(day_seed + 13)
    chosen = rng.sample(CHALLENGE_TEMPLATES, 3)
    # Snapshot current stat values as baseline
    challenges = []
    for c in chosen:
        stat_val = save.get(c["stat"], 0)
        challenges.append({
            "id":           c["id"],
            "desc":         c["desc"],
            "goal":         c["goal"],
            "progress":     0,
            "baseline":     stat_val,   # track delta from start of day
            "delta":        c["delta"],
            "reward_coins": c["reward_coins"],
            "reward_rp":    c["reward_coins"] // 50,
            "stat":         c["stat"],
            "done":         False,
        })
    save["guild_date"]       = today
    save["guild_challenges"] = challenges
    return challenges

def update_challenges(save):
    """Call after any stat change to update challenge progress."""
    challenges = save.get("guild_challenges", [])
    if not challenges or save.get("guild_date","") != _today_str():
        return
    changed = False
    for c in challenges:
        if c["done"]:
            continue
        if c["delta"]:
            current = save.get(c["stat"], 0) - c["baseline"]
        else:
            current = save.get(c["stat"], 0)
        c["progress"] = min(current, c["goal"])
        if c["progress"] >= c["goal"]:
            c["done"] = True
            save["coins"] = save.get("coins", 0) + c["reward_coins"]
            add_rank_points(save, c["reward_rp"], f"Challenge: {c['desc'][:20]}")
            notify(f"✅ Challenge abgeschlossen: {c['desc'][:30]}! +{c['reward_coins']} Coins", C_YELLOW, 260)
            changed = True
    if changed:
        save["guild_challenges"] = challenges


# ══════════════════════════════════════════════════════════════════════════════
# LERNSTREAK-BONUS
# ══════════════════════════════════════════════════════════════════════════════

def apply_streak_xp_bonus(save, base_xp):
    """Returns boosted XP based on daily_event_streak."""
    streak = save.get("daily_event_streak", 0)
    bonus_pct = min(50, streak * 5)   # +5% per day, max +50%
    boosted = int(base_xp * (1 + bonus_pct / 100))
    return boosted, bonus_pct


# ── Wer ist das Pokémon? — Quiz Screen ────────────────────────────────────────
import datetime as _dt

def _today_str():
    return _dt.date.today().isoformat()

def _pick_reward_pokemon(correct, total, for_raid=False):
    """
    Pick a reward Pokémon based on correct answers.
    correct: how many questions answered correctly (0-5 for daily, 0-5 for raid)
    Returns a Moonie object or None.
    For daily: need >= 3 correct.
    Rarity chances scale with correct answers:
      3 correct → rare 95%, legendary 5%
      4 correct → rare 80%, legendary 20%
      5 correct → rare 60%, legendary 40%
    For raid the pool skews rarer.
    """
    if correct < 3:
        return None
    rares      = [m for m in ALL_MOONIES_DICT.values() if m.rarity == "rare"]
    legendaries= [m for m in ALL_MOONIES_DICT.values() if m.rarity == "legendary"]
    # Scale legendary chance: 5% per correct answer above 2, max 40%
    leg_chance  = min(0.40, (correct - 2) * 0.10)
    if for_raid:
        leg_chance = min(0.50, (correct - 2) * 0.15)
    pool = legendaries if (random.random() < leg_chance and legendaries) else rares
    if not pool:
        pool = list(ALL_MOONIES_DICT.values())
    pick = random.choice(pool)
    m = pick.clone_for_battle()
    m.level = random.randint(20, 45)
    m.max_hp = m.max_hp + m.level * 2
    m.current_hp = m.max_hp
    m.catch_rate = max(0.12, m.catch_rate)  # slightly boosted catch rate for reward
    return m


class WhosThatPokemonScreen:
    """
    Daily 'Wer ist das Pokémon?' quiz.
    Shows 5 silhouettes, player types the name.
    3/5 correct → passive reward encounter.
    Resets once per calendar day.
    """
    N = 5
    NEEDED = 3

    def __init__(self, save, all_moonies, flashcards=None):
        self.save       = save
        self.all_moonies= all_moonies
        self.flashcards = flashcards or []
        self.anim_t     = 0
        self.phase      = "quiz"   # quiz | result | done
        # Pick 5 random pokémon (reproducible per day via date seed)
        day_seed = int(_dt.date.today().strftime("%Y%m%d"))
        rng = random.Random(day_seed)
        pool = [m for m in all_moonies.values() if m.image]
        self.questions  = rng.sample(pool, min(self.N, len(pool)))
        self.current_q  = 0
        self.correct    = 0
        self.input_text = ""
        self.feedback   = ""
        self.feedback_col = C_WHITE
        self.q_state    = "show"   # show | answered
        self.reward_mon = None     # set after quiz if earned
        self._sil_cache = {}
        self.cursor_blink = 0

    def _silhouette(self, img):
        key = id(img)
        if key not in self._sil_cache:
            sil = img.copy()
            dark = pygame.Surface(sil.get_size(), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 255))
            sil.blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            self._sil_cache[key] = sil
        return self._sil_cache[key]

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key

        if self.phase == "result":
            if k in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE, pygame.K_ESCAPE):
                if self.reward_mon:
                    return ("reward", self.reward_mon)
                return "close"
            return None

        if self.phase == "done":
            return "close"

        # quiz phase
        if self.q_state == "show":
            if k == pygame.K_RETURN:
                self.q_state = "answered"
                self.input_text = ""
        elif self.q_state == "answered":
            if k == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif k == pygame.K_RETURN:
                self._check_answer()
            elif k == pygame.K_ESCAPE:
                self._next_question(skipped=True)
            elif len(self.input_text) < 30:
                self.input_text += event.unicode
        return None

    def _check_answer(self):
        q = self.questions[self.current_q]
        user = self.input_text.strip().lower()
        correct_name = q.name.lower()
        if user == correct_name or user in correct_name or correct_name in user:
            self.correct += 1
            self.feedback = f"✓ Richtig! Es war {q.name}!"
            self.feedback_col = C_GREEN
            add_particles(SW//2, 350, (80, 220, 100), n=25)
        else:
            self.feedback = f"✗ Falsch. Es war: {q.name}"
            self.feedback_col = C_RED
        self._next_question()

    def _next_question(self, skipped=False):
        if skipped:
            q = self.questions[self.current_q]
            self.feedback = f"Übersprungen. Es war: {q.name}"
            self.feedback_col = C_GRAY
        self.current_q += 1
        if self.current_q >= self.N:
            # Quiz done
            self.save["daily_event_date"] = _today_str()
            self.save["daily_event_streak"] = self.save.get("daily_event_streak", 0) + 1
            if self.correct >= self.NEEDED:
                self.reward_mon = _pick_reward_pokemon(self.correct, self.N)
            self.phase = "result"
        else:
            self.q_state = "show"
            self.input_text = ""
            self.feedback = ""

    def draw(self, surf):
        self.anim_t += 1
        surf.fill((8, 10, 24))
        # Starfield bg
        rng2 = random.Random(42)
        for _ in range(60):
            sx = rng2.randint(0, SW); sy = rng2.randint(0, SH); ss = rng2.randint(1,3)
            alpha = int(100 + 80*math.sin(self.anim_t*0.04 + rng2.random()*6.28))
            s2 = pygame.Surface((ss*2,ss*2),pygame.SRCALPHA)
            pygame.draw.circle(s2,(200,200,255,alpha),(ss,ss),ss)
            surf.blit(s2,(sx,sy))

        # Header
        draw_rounded_rect(surf, (12,14,30), (0,0,SW,50), 0)
        draw_text(surf,"❓ Wer ist das Pokémon?",F_BIG,C_YELLOW,SW//2,6,center=True,shadow=True)
        draw_text(surf,"Tägliches Event — einmal pro Tag",F_TINY,C_GRAY,SW//2,36,center=True)

        if self.phase in ("quiz",):
            # Progress bar top-right
            for i in range(self.N):
                col = C_GREEN if i < self.correct else (C_GRAY if i >= self.current_q else C_YELLOW)
                pygame.draw.circle(surf, col, (SW - 80 + i*18, 25), 7)
                pygame.draw.circle(surf, C_WHITE, (SW - 80 + i*18, 25), 7, 1)

            # Needed counter
            draw_text(surf,f"Noch {max(0,self.NEEDED-self.correct)} richtig für Belohnung",
                      F_TINY,(180,230,180),20,38)

            q = self.questions[self.current_q]
            img = load_img(q.image, (180, 180))

            if self.q_state == "show":
                # Silhouette
                sil = self._silhouette(img)
                # Pulsing glow behind silhouette
                pulse = abs(math.sin(self.anim_t*0.05))
                glow = pygame.Surface((200,200),pygame.SRCALPHA)
                pygame.draw.circle(glow,(100,120,255,int(40+40*pulse)),(100,100),100)
                surf.blit(glow,(SW//2-100,160))
                surf.blit(sil,(SW//2-90,170))
                draw_text(surf,f"Frage {self.current_q+1}/{self.N}",F_MED,C_WHITE,SW//2,380,center=True)
                draw_text(surf,"[ ENTER ] Antwort eingeben",F_SMALL,C_GRAY,SW//2,420,center=True)
                # Show feedback from previous question
                if self.feedback:
                    fb_lines = wrap_text(self.feedback, F_MED, SW-100)
                    fy = 470
                    for line in fb_lines:
                        draw_text(surf,line,F_MED,self.feedback_col,SW//2,fy,center=True)
                        fy += 30

            elif self.q_state == "answered":
                # Still silhouette while typing
                sil = self._silhouette(img)
                surf.blit(sil,(SW//2-90,150))
                draw_text(surf,f"Frage {self.current_q+1}/{self.N} — Wer ist das?",F_MED,C_WHITE,SW//2,350,center=True)
                # Input box
                draw_rounded_rect(surf,C_DARK,(SW//2-200,380,400,48),10,2,C_BLUE)
                self.cursor_blink = (self.cursor_blink+1)%60
                cursor = "|" if self.cursor_blink < 30 else " "
                draw_text(surf,self.input_text+cursor,F_BIG,C_YELLOW,SW//2,390,center=True)
                draw_text(surf,"[ ENTER ] bestätigen   [ ESC ] überspringen",F_TINY,C_GRAY,SW//2,440,center=True)

        elif self.phase == "result":
            # Result summary
            stars = "★" * self.correct + "☆" * (self.N - self.correct)
            col = C_GREEN if self.correct >= self.NEEDED else C_RED
            draw_text(surf,stars,F_HUGE,C_YELLOW,SW//2,120,center=True,shadow=True)
            draw_text(surf,f"{self.correct} / {self.N} richtig!",F_BIG,col,SW//2,185,center=True,shadow=True)

            if self.correct >= self.NEEDED and self.reward_mon:
                r = self.reward_mon
                img = load_img(r.image,(140,140))
                pulse = abs(math.sin(self.anim_t*0.07))
                glow = pygame.Surface((160,160),pygame.SRCALPHA)
                pygame.draw.circle(glow,(255,220,50,int(60+60*pulse)),(80,80),80)
                surf.blit(glow,(SW//2-80,230))
                surf.blit(img,(SW//2-70,240))
                draw_text(surf,"🎉 Belohnungs-Begegnung!",F_BIG,C_YELLOW,SW//2,395,center=True,shadow=True)
                r_col = r.get_rarity_color()
                draw_text(surf,f"Ein {r.rarity.capitalize()} Pokémon wartet!",F_MED,r_col,SW//2,432,center=True)
                draw_text(surf,"[ ENTER ] Begegnung starten",F_SMALL,C_GREEN,SW//2,470,center=True)
            else:
                draw_text(surf,"Leider kein Belohnungs-Pokémon.",F_MED,C_GRAY,SW//2,280,center=True)
                draw_text(surf,f"Mindestens {self.NEEDED}/5 nötig.",F_SMALL,C_GRAY,SW//2,310,center=True)
                draw_text(surf,"[ ENTER ] Zurück",F_SMALL,C_GRAY,SW//2,370,center=True)

            # Show all answers
            ay = 510
            for i, q in enumerate(self.questions):
                # We can't know per-question correctness easily here, just show all names
                draw_text(surf,f"#{i+1}: {q.name}",F_TINY,C_GRAY,SW//2-200+i*100,ay,center=True)

        update_particles(surf)
        draw_notifications(surf)


# ── Passiver Fang-Battle (kein Gegner-Angriff) ────────────────────────────────
class PassiveCatchBattle(Battle):
    """
    Battle-Modus wo das wilde Pokémon nie angreift.
    Wird für tägliche Belohnungs-Begegnungen und Raid-Fang verwendet.
    Nur Ball werfen und Fliehen möglich — btn 1 (Ball) und btn 3 (Fliehen).
    """
    # Die zwei erlaubten Buttons: 1 = Ball, 3 = Fliehen
    _PASSIVE_BTNS = [1, 3]

    def __init__(self, player_team, wild_moonie, flashcards=None):
        super().__init__(player_team, None, wild_moonie=wild_moonie,
                         flashcards=flashcards, is_wild=True)
        self.passive = True
        self.selected_btn = 1   # start on Ball
        intro_name = wild_moonie.name if wild_moonie else "???"
        self.log = [f"Ein {intro_name} taucht auf! Du kannst nur Bälle werfen!"]

    def _enemy_turn(self):
        """Kein Angriff — nur gelegentliche Flavour-Texte."""
        if random.random() < 0.3:
            em = self.enemy_moonie
            if em:
                self.push_log(random.choice([
                    f"{em.name} schaut dich an...",
                    f"{em.name} wartet geduldig.",
                    f"{em.name} beobachtet dich.",
                ]))

    def handle_event(self, event, save_data):
        """Wie Battle.handle_event, aber Navigation nur zwischen Ball und Fliehen."""
        self.save_data_ref = save_data
        if self.flash_game and not self.flash_game.done:
            self.flash_game.handle_event(event)
            if self.flash_game.done:
                self.flash_game = None
                self.state = "player_turn"
            return
        if event.type != pygame.KEYDOWN or self.turn_cooldown > 0:
            return
        if self.state in ("done", "andreas_steal"):
            return
        if self.state == "intro":
            self.state = "player_turn"
        elif self.state in ("ball_pick", "item_pick"):
            super().handle_event(event, save_data)   # reuse parent logic
        elif self.state == "player_turn":
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                # Toggle between btn 1 (Ball) and btn 3 (Fliehen)
                idx = self._PASSIVE_BTNS.index(self.selected_btn) if self.selected_btn in self._PASSIVE_BTNS else 0
                idx = (idx + 1) % len(self._PASSIVE_BTNS)
                self.selected_btn = self._PASSIVE_BTNS[idx]
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                self._player_action(self.selected_btn, save_data)
        elif self.state == "result":
            if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_ESCAPE, pygame.K_SPACE):
                self.state = "done"


# ══════════════════════════════════════════════════════════════════════════════
# GILDEN-SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class CardEditorScreen:
    """In-game flashcard editor: add, edit, delete cards."""

    def __init__(self, cards, csv_path):
        self.cards    = cards        # live list ref
        self.csv_path = csv_path
        self.state    = "list"       # list | edit_q | edit_a | confirm_del
        self.sel      = 0
        self.input_q  = ""
        self.input_a  = ""
        self.edit_idx = None         # None = new card
        self.edit_field = "q"        # "q" | "a"
        self.scroll   = 0
        self.search   = ""
        self.searching= False
        self.del_confirm = False

    def _visible(self):
        if not self.search:
            return list(range(len(self.cards)))
        s = self.search.lower()
        return [i for i,c in enumerate(self.cards)
                if s in c["q"].lower() or s in c["a"].lower()]

    def _save_csv(self):
        try:
            import csv as _csv
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                w = _csv.writer(f)
                for c in self.cards:
                    w.writerow([c["q"], c["a"]])
            notify("💾 Karten gespeichert!", C_GREEN, 150)
        except Exception as e:
            notify(f"⚠ Speicherfehler: {e}", C_RED, 180)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key

        if self.state == "list":
            if self.searching:
                if k in (pygame.K_ESCAPE, pygame.K_RETURN):
                    self.searching = False; self.sel = 0
                elif k == pygame.K_BACKSPACE:
                    self.search = self.search[:-1]
                else:
                    ch = event.unicode
                    if ch.isprintable(): self.search += ch
                return None
            vis = self._visible()
            total = len(vis)
            if k == pygame.K_UP:    self.sel = max(0, self.sel - 1)
            elif k == pygame.K_DOWN: self.sel = min(max(0,total-1), self.sel + 1)
            elif k == pygame.K_RETURN or k == pygame.K_e:
                # Edit selected
                if 0 <= self.sel < total:
                    self.edit_idx = vis[self.sel]
                    c = self.cards[self.edit_idx]
                    self.input_q = c["q"]; self.input_a = c["a"]
                    self.edit_field = "q"; self.state = "edit_q"
            elif k == pygame.K_n:
                # New card
                self.edit_idx = None; self.input_q = ""; self.input_a = ""
                self.edit_field = "q"; self.state = "edit_q"
            elif k == pygame.K_DELETE or k == pygame.K_d:
                if 0 <= self.sel < total:
                    self.del_confirm = vis[self.sel]; self.state = "confirm_del"
            elif k == pygame.K_s:
                self.searching = True; self.search = ""
            elif k == pygame.K_F5:
                self._save_csv()
            elif k in (pygame.K_ESCAPE, pygame.K_x):
                self._save_csv()
                return "close"

        elif self.state in ("edit_q", "edit_a"):
            field = self.state[-1]   # "q" or "a"
            target = "input_" + field
            val = getattr(self, target)
            if k == pygame.K_BACKSPACE:
                setattr(self, target, val[:-1])
            elif k == pygame.K_TAB or k == pygame.K_DOWN:
                # Switch between q/a field
                self.state = "edit_a" if self.state == "edit_q" else "edit_q"
            elif k == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                # Ctrl+Enter = save
                self._save_edit()
            elif k == pygame.K_ESCAPE:
                self.state = "list"
            elif len(val) < 300:
                ch = event.unicode
                if ch and ch.isprintable():
                    setattr(self, target, val + ch)

        elif self.state == "confirm_del":
            if k == pygame.K_RETURN or k == pygame.K_y:
                idx = self.del_confirm
                if 0 <= idx < len(self.cards):
                    self.cards.pop(idx)
                    self.sel = max(0, self.sel - 1)
                notify("🗑 Karte gelöscht", C_RED, 120)
                self.state = "list"; self.del_confirm = False
            elif k in (pygame.K_ESCAPE, pygame.K_n):
                self.state = "list"; self.del_confirm = False

        return None

    def _save_edit(self):
        q = self.input_q.strip(); a = self.input_a.strip()
        if not q or not a:
            notify("⚠ Frage und Antwort dürfen nicht leer sein!", C_RED, 150)
            return
        if self.edit_idx is None:
            # New card with SR defaults
            self.cards.append({
                "q": q, "a": a, "known": False, "shown": 0,
                "ease": 2.5, "interval": 0, "due": "", "reps": 0, "streak": 0,
            })
            notify("✅ Neue Karte hinzugefügt!", C_GREEN, 130)
            self.sel = len(self.cards) - 1
        else:
            self.cards[self.edit_idx]["q"] = q
            self.cards[self.edit_idx]["a"] = a
            notify("✏ Karte aktualisiert!", C_YELLOW, 130)
        self.state = "list"

    def draw(self, surf):
        surf.fill((10, 12, 20))
        draw_rounded_rect(surf, C_PANEL, (0, 0, SW, 54), 0)
        draw_text(surf, "✏ Karteneditor", F_BIG, C_YELLOW, SW//2, 6, center=True, shadow=True)
        draw_text(surf, f"{len(self.cards)} Karten  |  N=Neu  E=Bearbeiten  D=Löschen  S=Suche  F5=Speichern  ESC=Fertig",
                  F_TINY, C_GRAY, SW//2, 38, center=True)

        vis = self._visible()
        total = len(vis)
        # Clamp scroll
        per_page = 12
        page = self.sel // per_page if total else 0
        start = page * per_page; end = min(start + per_page, total)

        if self.searching or self.search:
            draw_rounded_rect(surf, (30,40,60), (SW//2-240,56,480,26), 8, 2, C_BLUE if self.searching else C_GRAY)
            cur = "|" if self.searching and int(time.time()*2)%2==0 else ""
            draw_text(surf, f"Suche: {self.search}{cur}", F_SMALL, C_WHITE, SW//2, 62, center=True)

        list_y = 88 if (self.searching or self.search) else 60
        card_h = 52
        for i, vidx in enumerate(vis[start:end]):
            c = self.cards[vidx]
            iy = list_y + i * card_h
            sel = ((start + i) == self.sel)
            bg = (40, 60, 100) if sel else (22, 26, 38)
            bc = C_YELLOW if sel else (45, 50, 70)
            draw_rounded_rect(surf, bg, (16, iy, SW-32, card_h-4), 8, 2 if sel else 1, bc)
            # SR indicator
            ease = c.get("ease", 2.5)
            reps  = c.get("reps", 0)
            due   = c.get("due", "")
            today = _today_str()
            if reps == 0:     sr_col=(180,180,180); sr_txt="Neu"
            elif due <= today: sr_col=(255,120,40);  sr_txt=f"Fällig"
            else:              sr_col=(80,200,120);  sr_txt=f"{c.get('interval',0)}d"
            draw_rounded_rect(surf, (30,34,50), (SW-100, iy+4, 80, 20), 6)
            draw_text(surf, sr_txt, F_TINY, sr_col, SW-60, iy+8, center=True)
            # Ease dots (1-3 filled)
            ease_dots = max(1, min(3, round(ease / 2.5 * 1.5)))
            for di in range(3):
                dc = sr_col if di < ease_dots else (50,50,60)
                pygame.draw.circle(surf, dc, (SW-110 + di*10, iy+14), 4)
            # Q/A preview
            q_short = c["q"][:70] + ("…" if len(c["q"])>70 else "")
            a_short = c["a"][:60] + ("…" if len(c["a"])>60 else "")
            draw_text(surf, q_short, F_SMALL, C_WHITE, 28, iy+6)
            draw_text(surf, a_short, F_TINY, C_GRAY, 28, iy+28)

        if total == 0:
            draw_text(surf, "Keine Karten." if self.search else "Noch keine Karten — drücke N!", F_MED, C_GRAY, SW//2, 300, center=True)

        draw_text(surf, f"Seite {page+1}/{max(1,(total+per_page-1)//per_page)}  |  {total} Karte(n) gefunden",
                  F_TINY, C_GRAY, SW//2, SH-20, center=True)

        # Edit overlay
        if self.state in ("edit_q","edit_a"):
            self._draw_edit(surf)
        elif self.state == "confirm_del" and self.del_confirm is not False:
            self._draw_confirm(surf)

        draw_notifications(surf)

    def _draw_edit(self, surf):
        overlay = pygame.Surface((SW,SH), pygame.SRCALPHA)
        overlay.fill((0,0,0,170))
        surf.blit(overlay,(0,0))
        pw,ph = 780, 380
        px,py = SW//2-pw//2, SH//2-ph//2
        draw_rounded_rect(surf, C_PANEL, (px,py,pw,ph), 16, 2, C_YELLOW)
        title = "✏ Karte bearbeiten" if self.edit_idx is not None else "➕ Neue Karte"
        draw_text(surf, title, F_MED, C_YELLOW, px+pw//2, py+12, center=True, shadow=True)
        for fi,(fstate,flbl,fval) in enumerate([("edit_q","Frage:",self.input_q),("edit_a","Antwort:",self.input_a)]):
            fy = py + 56 + fi * 130
            active = (self.state == fstate)
            draw_text(surf, flbl, F_SMALL, C_YELLOW if active else C_GRAY, px+24, fy)
            bc = C_YELLOW if active else (60,65,85)
            draw_rounded_rect(surf, (25,30,48), (px+24, fy+24, pw-48, 90), 8, 2, bc)
            cur = "|" if active and int(time.time()*2)%2==0 else ""
            lines = wrap_text(fval + cur, F_SMALL, pw-68)
            for li,ln in enumerate(lines[:3]):
                draw_text(surf, ln, F_SMALL, C_WHITE, px+34, fy+30+li*26)
        draw_text(surf, "TAB=Feld wechseln   CTRL+ENTER=Speichern   ESC=Abbruch", F_TINY, C_GRAY, px+pw//2, py+ph-18, center=True)

    def _draw_confirm(self, surf):
        overlay = pygame.Surface((SW,SH), pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        surf.blit(overlay,(0,0))
        c = self.cards[self.del_confirm]
        pw,ph = 500,200
        px,py = SW//2-pw//2, SH//2-ph//2
        draw_rounded_rect(surf, C_PANEL, (px,py,pw,ph), 14, 2, C_RED)
        draw_text(surf, "🗑 Karte löschen?", F_MED, C_RED, px+pw//2, py+16, center=True, shadow=True)
        draw_text(surf, c["q"][:60], F_SMALL, C_GRAY, px+pw//2, py+70, center=True)
        draw_text(surf, "ENTER / Y = Ja    ESC / N = Nein", F_SMALL, C_WHITE, px+pw//2, py+130, center=True)


class GuildScreen:
    def __init__(self, save):
        self.save = save
        self.anim_t = 0
        self.challenges = get_today_challenges(save)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN: return None
        if event.key in (pygame.K_ESCAPE, pygame.K_x, pygame.K_g): return "close"
        return None

    def draw(self, surf):
        self.anim_t += 1
        surf.fill((8, 12, 22))
        # Stars bg
        rng = random.Random(99)
        for _ in range(80):
            sx = rng.randint(0, SW); sy = rng.randint(0, SH)
            a = int(80 + 60*math.sin(self.anim_t*0.03 + rng.random()*6.28))
            s = pygame.Surface((3,3), pygame.SRCALPHA)
            pygame.draw.circle(s, (200,210,255,a), (1,1), 1)
            surf.blit(s, (sx, sy))

        # Header
        draw_rounded_rect(surf, (12,16,35), (0,0,SW,60), 0)
        draw_text(surf, "⚔ Gilden-Challenges", F_BIG, C_ORANGE, SW//2, 8, center=True, shadow=True)
        draw_text(surf, "Täglich neue Aufgaben — setzt sich um Mitternacht zurück", F_TINY, C_GRAY, SW//2, 44, center=True)

        # Rang-Banner
        rp = self.save.get("rank_points", 0)
        tier, rname, rcol, nxt = get_rank_info(rp)
        pygame.draw.rect(surf, (*rcol, 40), (0, 60, SW, 44))
        pygame.draw.line(surf, rcol, (0,60), (SW,60), 2)
        draw_text(surf, f"🏆 Rang: {rname}", F_MED, rcol, 20, 70)
        draw_text(surf, f"{rp} RP", F_SMALL, C_YELLOW, 200, 73)
        if nxt:
            bar_w = 400
            filled = int(bar_w * min(1.0, rp / nxt))
            pygame.draw.rect(surf, (40,40,60), (SW//2 - bar_w//2, 73, bar_w, 14), border_radius=7)
            pygame.draw.rect(surf, rcol,        (SW//2 - bar_w//2, 73, filled, 14), border_radius=7)
            draw_text(surf, f"{rp}/{nxt} RP bis {RANKS[tier+1][1]}", F_TINY, C_GRAY, SW//2, 90, center=True)
        else:
            draw_text(surf, "MAX RANG!", F_SMALL, rcol, SW//2, 76, center=True)

        # Challenges
        cy = 130
        for c in self.challenges:
            prog_pct = min(1.0, c["progress"] / max(1, c["goal"]))
            done = c["done"]
            bg   = (20, 40, 20) if done else (18, 22, 40)
            bdr  = C_GREEN if done else C_ORANGE
            draw_rounded_rect(surf, bg, (40, cy, SW-80, 100), 12, 2, bdr)

            # Icon
            icon_col = C_GREEN if done else C_ORANGE
            draw_text(surf, "✅" if done else "🎯", F_BIG, icon_col, 80, cy+30, center=True)

            # Description
            draw_text(surf, c["desc"], F_MED, C_WHITE if not done else C_GREEN, 130, cy+14, shadow=True)
            draw_text(surf, f"+{c['reward_coins']} Coins  +{c['reward_rp']} RP", F_TINY, C_YELLOW, 130, cy+42)

            # Progress bar
            bw = SW - 320
            pygame.draw.rect(surf, (40,40,60), (130, cy+62, bw, 16), border_radius=8)
            if prog_pct > 0:
                p_col = C_GREEN if done else C_ORANGE
                pygame.draw.rect(surf, p_col, (130, cy+62, int(bw*prog_pct), 16), border_radius=8)
            draw_text(surf, f"{c['progress']}/{c['goal']}", F_TINY, C_WHITE, 130+bw+8, cy+64)

            # Pulsing glow if just completed
            if done:
                pulse = abs(math.sin(self.anim_t*0.07))
                glow = pygame.Surface((SW-80+10, 110), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*C_GREEN, int(20+20*pulse)), (0,0,SW-80+10,110), border_radius=14)
                surf.blit(glow, (35, cy-5))

            cy += 116

        draw_text(surf, "[ ESC ] Schließen", F_TINY, C_GRAY, SW//2, SH-24, center=True)
        update_particles(surf)
        draw_notifications(surf)


# ══════════════════════════════════════════════════════════════════════════════
# PRÜFUNGSMODUS-SCREEN (20 Fragen)
# ══════════════════════════════════════════════════════════════════════════════
class ExamScreen:
    N = 20

    def __init__(self, save, flashcards):
        self.save       = save
        self.flashcards = flashcards
        self.anim_t     = 0
        self.phase      = "intro"   # intro | question | result
        self.questions  = []
        self.current_q  = 0
        self.correct    = 0
        self.wrong_idxs = []
        self.input_text = ""
        self.feedback   = ""
        self.feedback_col = C_WHITE
        self.cursor_blink = 0
        self.q_state    = "show"    # show | answering

    def _start(self):
        if len(self.flashcards) < 5:
            self.phase = "no_cards"
            return
        pool = self.flashcards.copy()
        random.shuffle(pool)
        self.questions = pool[:self.N]
        self.phase     = "question"
        self.current_q = 0
        self.correct   = 0
        self.wrong_idxs= []
        self.q_state   = "answering"
        self.input_text= ""
        self.feedback  = ""

    def _check(self):
        q    = self.questions[self.current_q]
        user = self.input_text.strip().lower()
        ans  = str(q.get("answer","")).strip().lower()
        ok   = (user == ans or user in ans or ans in user)
        if ok:
            self.correct += 1
            self.feedback = "✓ Richtig!"
            self.feedback_col = C_GREEN
            add_particles(SW//2, 300, (80,220,100), n=18)
        else:
            self.wrong_idxs.append(self.current_q)
            self.feedback = f"✗ Richtig wäre: {q.get('answer','?')}"
            self.feedback_col = C_RED
        self.q_state = "show"

    def _next(self):
        self.current_q += 1
        if self.current_q >= len(self.questions):
            self._finish()
        else:
            self.q_state    = "answering"
            self.input_text = ""
            self.feedback   = ""

    def _finish(self):
        score = self.correct
        self.save["exam_attempts"] = self.save.get("exam_attempts",0)+1
        if score > self.save.get("exam_best_score",0):
            self.save["exam_best_score"] = score
        # RP reward based on score
        rp = score * 3
        add_rank_points(self.save, rp, f"Prüfung: {score}/{self.N}")
        # Streak contribution
        streak = self.save.get("daily_event_streak",0)
        if score >= 15:
            self.save["daily_event_streak"] = streak + 1
        self.phase = "result"

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN: return None
        k = event.key
        if self.phase == "intro":
            if k in (pygame.K_RETURN, pygame.K_z): self._start()
            elif k in (pygame.K_ESCAPE, pygame.K_x): return "close"
        elif self.phase in ("no_cards", "result"):
            if k in (pygame.K_RETURN, pygame.K_z, pygame.K_ESCAPE): return "close"
        elif self.phase == "question":
            if self.q_state == "answering":
                if k == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
                elif k == pygame.K_RETURN: self._check()
                elif k == pygame.K_ESCAPE: self._next()
                elif len(self.input_text) < 80: self.input_text += event.unicode
            elif self.q_state == "show":
                if k in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE): self._next()
        return None

    def draw(self, surf):
        self.anim_t += 1
        surf.fill((10, 12, 28))
        draw_rounded_rect(surf, (14,18,40), (0,0,SW,58), 0)
        draw_text(surf, "📚 Prüfungsmodus", F_BIG, C_BLUE, SW//2, 8, center=True, shadow=True)

        if self.phase == "intro":
            draw_text(surf, f"{self.N} Fragen • Für jede richtige Antwort: +3 RP", F_MED, C_WHITE, SW//2, 150, center=True)
            draw_text(surf, f"Ab 15/20: Tages-Streak +1", F_SMALL, C_YELLOW, SW//2, 190, center=True)
            best = self.save.get("exam_best_score",0)
            att  = self.save.get("exam_attempts",0)
            draw_text(surf, f"Bestes Ergebnis: {best}/{self.N}   Versuche: {att}", F_SMALL, C_GRAY, SW//2, 230, center=True)
            draw_text(surf, "[ ENTER ] Starten    [ ESC ] Zurück", F_SMALL, C_GRAY, SW//2, 300, center=True)

        elif self.phase == "no_cards":
            draw_text(surf, "Keine Lernkarten vorhanden!", F_BIG, C_RED, SW//2, 250, center=True)
            draw_text(surf, "[ ENTER ] Zurück", F_SMALL, C_GRAY, SW//2, 310, center=True)

        elif self.phase == "question":
            q = self.questions[self.current_q]
            # Progress
            prog_w = SW - 100
            filled = int(prog_w * self.current_q / max(1, len(self.questions)))
            pygame.draw.rect(surf, (40,40,60), (50, 70, prog_w, 10), border_radius=5)
            pygame.draw.rect(surf, C_BLUE,     (50, 70, filled, 10), border_radius=5)
            draw_text(surf, f"Frage {self.current_q+1}/{len(self.questions)}  |  Richtig: {self.correct}",
                      F_SMALL, C_GRAY, SW//2, 88, center=True)

            # Question box
            q_text = q.get("question", "?")
            lines  = wrap_text(q_text, F_MED, SW-120)
            qy = 140
            draw_rounded_rect(surf, (20,24,50), (50, qy-14, SW-100, len(lines)*32+28), 10, 1, C_BLUE)
            for line in lines:
                draw_text(surf, line, F_MED, C_WHITE, SW//2, qy, center=True)
                qy += 32

            if self.q_state == "answering":
                draw_rounded_rect(surf, C_DARK, (SW//2-300, qy+30, 600, 52), 10, 2, C_BLUE)
                self.cursor_blink = (self.cursor_blink+1)%60
                cur = "|" if self.cursor_blink < 30 else " "
                display = self.input_text if len(self.input_text)<=40 else "…"+self.input_text[-38:]
                draw_text(surf, display+cur, F_BIG, C_YELLOW, SW//2, qy+42, center=True)
                draw_text(surf, "[ ENTER ] Antworten   [ ESC ] Überspringen", F_TINY, C_GRAY, SW//2, qy+95, center=True)
            elif self.q_state == "show":
                fb_lines = wrap_text(self.feedback, F_MED, SW-120)
                fy = qy + 30
                for line in fb_lines:
                    draw_text(surf, line, F_MED, self.feedback_col, SW//2, fy, center=True)
                    fy += 32
                draw_text(surf, "[ ENTER/LEERTASTE ] Weiter", F_TINY, C_GRAY, SW//2, fy+20, center=True)

        elif self.phase == "result":
            score = self.correct
            pct   = score / max(1, len(self.questions)) * 100
            grade_col = C_GREEN if pct >= 75 else C_YELLOW if pct >= 50 else C_RED
            grade = "Sehr gut! 🎉" if pct>=90 else "Gut 👍" if pct>=75 else "Bestanden" if pct>=50 else "Nicht bestanden"
            draw_text(surf, f"{score}/{len(self.questions)}", F_HUGE, grade_col, SW//2, 150, center=True, shadow=True)
            draw_text(surf, grade, F_BIG, grade_col, SW//2, 220, center=True)
            draw_text(surf, f"+{score*3} Rang-Punkte erhalten", F_MED, C_YELLOW, SW//2, 275, center=True)
            if score > self.save.get("exam_best_score",0) - score*3:
                draw_text(surf, "🏆 Neues Bestergebnis!", F_MED, C_ORANGE, SW//2, 310, center=True)
            draw_text(surf, "[ ENTER ] Zurück", F_SMALL, C_GRAY, SW//2, 380, center=True)

        update_particles(surf)
        draw_notifications(surf)


# ══════════════════════════════════════════════════════════════════════════════
# EINSTELLUNGS-SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class SettingsScreen:
    ITEMS = [
        {"key": "sfx_vol",    "label": "SFX Lautstärke",     "type": "range", "min": 0, "max": 10},
        {"key": "music_vol",  "label": "Musik Lautstärke",   "type": "range", "min": 0, "max": 10},
        {"key": "game_speed", "label": "Spielgeschwindigkeit","type": "choice","choices": [1,2], "labels": ["Normal","Schnell"]},
        {"key": "show_hints", "label": "Tipps anzeigen",      "type": "bool"},
    ]

    def __init__(self, save):
        self.save = save
        self.sel  = 0
        self.anim_t = 0
        self.settings = save.setdefault("settings", {
            "sfx_vol": 5, "music_vol": 5, "game_speed": 1, "show_hints": True})

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN: return None
        k = event.key
        if k in (pygame.K_ESCAPE, pygame.K_x): return "close"
        if k in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % len(self.ITEMS)
        elif k in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % len(self.ITEMS)
        item = self.ITEMS[self.sel]
        if item["type"] == "range":
            if k in (pygame.K_LEFT, pygame.K_a):
                self.settings[item["key"]] = max(item["min"], self.settings.get(item["key"],5)-1)
            elif k in (pygame.K_RIGHT, pygame.K_d):
                self.settings[item["key"]] = min(item["max"], self.settings.get(item["key"],5)+1)
        elif item["type"] == "choice":
            if k in (pygame.K_LEFT,pygame.K_a,pygame.K_RIGHT,pygame.K_d,pygame.K_RETURN,pygame.K_z):
                choices = item["choices"]
                cur = self.settings.get(item["key"], choices[0])
                idx = choices.index(cur) if cur in choices else 0
                self.settings[item["key"]] = choices[(idx+1)%len(choices)]
        elif item["type"] == "bool":
            if k in (pygame.K_LEFT,pygame.K_a,pygame.K_RIGHT,pygame.K_d,pygame.K_RETURN,pygame.K_z):
                self.settings[item["key"]] = not self.settings.get(item["key"],True)
        self.save["settings"] = self.settings
        return None

    def draw(self, surf):
        self.anim_t += 1
        overlay = pygame.Surface((SW,SH),pygame.SRCALPHA)
        overlay.fill((0,0,0,200)); surf.blit(overlay,(0,0))
        pw,ph = 600,420; px,py = SW//2-pw//2, SH//2-ph//2
        draw_rounded_rect(surf,(14,18,40),(px,py,pw,ph),16,2,(80,100,160))
        draw_text(surf,"⚙ Einstellungen",F_BIG,C_WHITE,SW//2,py+10,center=True,shadow=True)

        iy = py+60
        for i,item in enumerate(self.ITEMS):
            sel = (i == self.sel)
            bg  = (30,50,90) if sel else (22,28,50)
            draw_rounded_rect(surf,bg,(px+20,iy,pw-40,52),8,2 if sel else 1,C_BLUE if sel else (50,60,90))
            draw_text(surf,item["label"],F_SMALL,C_YELLOW if sel else C_WHITE,px+40,iy+10)
            val = self.settings.get(item["key"])
            if item["type"] == "range":
                bar_x = px+270; bar_w = pw-320
                mx = item["max"]; mn = item["min"]
                filled = int(bar_w*(val-mn)/(mx-mn)) if mx!=mn else 0
                pygame.draw.rect(surf,(40,40,60),(bar_x,iy+18,bar_w,16),border_radius=8)
                pygame.draw.rect(surf,C_BLUE,    (bar_x,iy+18,filled,16),border_radius=8)
                draw_text(surf,str(val),F_SMALL,C_YELLOW,bar_x+bar_w+14,iy+16)
                if sel:
                    draw_text(surf,"◄ ►",F_TINY,C_GRAY,bar_x-28,iy+18)
            elif item["type"] == "choice":
                choices,labels = item["choices"],item["labels"]
                idx = choices.index(val) if val in choices else 0
                lbl = labels[idx]
                draw_text(surf,f"◄ {lbl} ►",F_SMALL,C_YELLOW,px+pw-120,iy+16,center=True)
            elif item["type"] == "bool":
                onoff = "EIN" if val else "AUS"
                col   = C_GREEN if val else C_RED
                draw_text(surf,onoff,F_MED,col,px+pw-80,iy+12,center=True)
            iy += 62

        draw_text(surf,"↑↓ navigieren   ◄► ändern   ESC schließen",F_TINY,C_GRAY,SW//2,py+ph-24,center=True)
        draw_notifications(surf)


# ══════════════════════════════════════════════════════════════════════════════
# REISE-MENÜ — Welt-Auswahl
# ══════════════════════════════════════════════════════════════════════════════
class TravelMenuScreen:
    COLS = 6
    ROWS = 3   # 18 maps / 6 cols

    def __init__(self, save, current_map="Normal"):
        self.save        = save
        self.current_map = current_map
        self.sel         = MAP_ORDER.index(current_map) if current_map in MAP_ORDER else 0
        self.anim_t      = 0
        self.confirm     = None   # map_key waiting for confirm, or None

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN: return None
        k = event.key
        if self.confirm:
            if k in (pygame.K_RETURN, pygame.K_z, pygame.K_y):
                target = self.confirm
                self.confirm = None
                return ("travel", target)
            else:
                self.confirm = None
            return None
        if k in (pygame.K_ESCAPE, pygame.K_x, pygame.K_r): return "close"
        if k in (pygame.K_LEFT,  pygame.K_a): self.sel = (self.sel - 1) % len(MAP_ORDER)
        if k in (pygame.K_RIGHT, pygame.K_d): self.sel = (self.sel + 1) % len(MAP_ORDER)
        if k in (pygame.K_UP,    pygame.K_w): self.sel = (self.sel - self.COLS) % len(MAP_ORDER)
        if k in (pygame.K_DOWN,  pygame.K_s): self.sel = (self.sel + self.COLS) % len(MAP_ORDER)
        if k in (pygame.K_RETURN, pygame.K_z):
            target = MAP_ORDER[self.sel]
            if target == self.current_map:
                return None   # already here
            self.confirm = target
        return None

    def draw(self, surf):
        self.anim_t += 1
        t = self.anim_t

        # Starfield background
        surf.fill((4, 6, 16))
        rng = random.Random(42)
        for _ in range(120):
            sx = rng.randint(0, SW); sy = rng.randint(0, SH)
            a  = int(60 + 80 * math.sin(t * 0.02 + rng.random() * 6.28))
            s  = pygame.Surface((3,3), pygame.SRCALPHA)
            s.fill((0,0,0,0))
            pygame.draw.circle(s, (200,210,255), (1,1), 1)
            s.set_alpha(a)
            surf.blit(s, (sx, sy))

        # Header
        draw_rounded_rect(surf, (8,10,24), (0,0,SW,56), 0)
        draw_text(surf, "✈  Reise", F_BIG, C_YELLOW, SW//2, 6, center=True, shadow=True)
        draw_text(surf, "Wähle eine Welt  ·  ↑↓←→ navigieren  ·  ENTER reisen  ·  ESC zurück",
                  F_TINY, C_GRAY, SW//2, 38, center=True)

        # Grid of map cards
        card_w, card_h = 180, 110
        gap_x, gap_y   = 12, 12
        total_w = self.COLS * card_w + (self.COLS-1) * gap_x
        start_x = (SW - total_w) // 2
        start_y = 70

        for idx, mk in enumerate(MAP_ORDER):
            col_i = idx % self.COLS
            row_i = idx // self.COLS
            cx = start_x + col_i * (card_w + gap_x)
            cy = start_y + row_i * (card_h + gap_y)

            md    = MAP_DEFS[mk]
            is_sel     = (idx == self.sel)
            is_current = (mk == self.current_map)

            # Card background — tinted with map's grass color
            tint = md["grass_tint"]
            r2 = min(255, tint[0]//4 + 12)
            g2 = min(255, tint[1]//4 + 12)
            b2 = min(255, tint[2]//4 + 12)
            card_bg = (r2, g2, b2)

            border_col = C_YELLOW if is_sel else (C_GREEN if is_current else (50,55,70))
            border_w   = 3 if is_sel else (2 if is_current else 1)

            # Pulsing glow for selected
            if is_sel:
                pulse = abs(math.sin(t * 0.08))
                glow = pygame.Surface((card_w+20, card_h+20), pygame.SRCALPHA)
                gc = (*C_YELLOW, int(30 + 50*pulse))
                pygame.draw.rect(glow, gc, (0,0,card_w+20,card_h+20), border_radius=14)
                surf.blit(glow, (cx-10, cy-10))

            draw_rounded_rect(surf, card_bg, (cx, cy, card_w, card_h), 10, border_w, border_col)

            # Grass color swatch strip at top
            swatch_col = tint if tint != (255,255,255) else (80,200,80)
            pygame.draw.rect(surf, swatch_col, (cx+2, cy+2, card_w-4, 18), border_radius=8)

            # Icon + name
            draw_text(surf, md["icon"], F_BIG, C_WHITE, cx + card_w//2, cy+24, center=True)
            draw_text(surf, md["name"], F_SMALL, C_WHITE, cx + card_w//2, cy+58, center=True, shadow=True)

            # Type bonus label
            weather_label = " · ".join(md["weather_pool"][:2])
            draw_text(surf, weather_label, F_TINY, (160,170,200), cx + card_w//2, cy+80, center=True)

            # Badges: buildings present
            bld_icons = {"shop":"🏪","center":"💊","arena":"⚔","blackmarket":"💀","daily":"❓","guild":"⚔","pc":"💾"}
            bx2 = cx + 6
            for bk in sorted(md["buildings"]):
                if bk == "pc": continue
                ico = bld_icons.get(bk,"·")
                draw_text(surf, ico, F_TINY, (200,200,160), bx2, cy+card_h-18)
                bx2 += 18

            # "HIER" label
            if is_current:
                draw_rounded_rect(surf, C_GREEN, (cx+card_w-46, cy+4, 40, 16), 8, 0)
                draw_text(surf, "HIER", F_TINY, C_DARK, cx+card_w-26, cy+6, center=True)

        # Bottom: confirm dialog or selected map info
        sel_mk  = MAP_ORDER[self.sel]
        sel_md  = MAP_DEFS[sel_mk]
        info_y  = start_y + self.ROWS * (card_h + gap_y) + 8

        if self.confirm:
            tgt_md = MAP_DEFS[self.confirm]
            draw_rounded_rect(surf, (30,20,10), (SW//2-280, info_y, 560, 48), 12, 2, C_YELLOW)
            draw_text(surf,
                f"Reisen nach {tgt_md['icon']} {tgt_md['name']}?  [ ENTER ] Ja   [ Andere Taste ] Abbrechen",
                F_SMALL, C_YELLOW, SW//2, info_y+14, center=True, shadow=True)
        else:
            blds = ", ".join(b for b in sorted(sel_md["buildings"]) if b != "pc") or "–"
            draw_rounded_rect(surf, (14,16,30), (SW//2-300, info_y, 600, 44), 10, 1, (50,55,80))
            draw_text(surf,
                f"{sel_md['icon']} {sel_md['name']}  |  Wetter: {' · '.join(sel_md['weather_pool'])}  |  Gebäude: {blds}",
                F_TINY, (180,190,220), SW//2, info_y+14, center=True)

        update_particles(surf)
        draw_notifications(surf)


# ── Raid Pass Selection ────────────────────────────────────────────────────────
class RaidPassSelectScreen:
    def __init__(self, save, raid):
        self.save  = save; self.raid = raid; self.sel = 0; self.anim_t = 0

    def _options(self):
        opts = []
        if self.save.get("premium_raid_passes", 0) > 0:
            opts.append(("premium","Premium Raid-Pass","Raid erleichtert: ½ Boss-HP, -2 Lernkarten nötig","premium_raid_passes",(255,160,80)))
        if self.save.get("raid_passes", 0) > 0:
            opts.append(("normal","Raid-Pass","Normaler Raid-Zutritt","raid_passes",(80,180,255)))
        return opts

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN: return None
        k = event.key
        if k in (pygame.K_ESCAPE, pygame.K_x): return "close"
        opts = self._options()
        if k in (pygame.K_UP, pygame.K_w): self.sel = max(0, self.sel-1)
        elif k in (pygame.K_DOWN, pygame.K_s): self.sel = min(len(opts)-1, self.sel+1)
        elif k in (pygame.K_RETURN, pygame.K_z):
            if opts:
                chosen = opts[self.sel]
                self.save[chosen[3]] -= 1
                return ("start_raid", chosen[0])
        return None

    def draw(self, surf):
        self.anim_t += 1
        overlay = pygame.Surface((SW,SH), pygame.SRCALPHA); overlay.fill((0,0,0,190)); surf.blit(overlay,(0,0))
        pw, ph = 560, 300; px, py = SW//2-pw//2, SH//2-ph//2
        draw_rounded_rect(surf,(18,20,40),(px,py,pw,ph),16,3,(255,160,40))
        draw_text(surf,"⚔ Raid betreten",F_BIG,(255,160,40),SW//2,py+12,center=True,shadow=True)
        draw_text(surf,f"Boss: {self.raid.get('name','???')}  Lv {self.raid.get('level','?')}",F_MED,C_WHITE,SW//2,py+48,center=True)
        opts = self._options()
        if not opts:
            draw_text(surf,"Kein Raid-Pass vorhanden!",F_MED,C_RED,SW//2,py+120,center=True)
        else:
            for i,(kind,name,desc,key,col) in enumerate(opts):
                sel=(i==self.sel); oy=py+90+i*76
                bg=(40,50,80) if sel else (22,26,44)
                draw_rounded_rect(surf,bg,(px+20,oy,pw-40,64),12,2 if sel else 1,col if sel else (60,65,90))
                icon=item_icon(key,44)
                if icon: surf.blit(icon,(px+30,oy+10))
                draw_text(surf,name,F_MED,col if sel else C_WHITE,px+86,oy+8,shadow=True)
                draw_text(surf,desc,F_SMALL,C_GRAY,px+86,oy+34)
                draw_text(surf,f"×{self.save.get(key,0)}",F_SMALL,col,px+pw-50,oy+20,center=True)
        draw_text(surf,"↑↓ wählen   ENTER benutzen   ESC abbrechen",F_TINY,C_GRAY,SW//2,py+ph-20,center=True)
        draw_notifications(surf)


# ── Black Market screen ────────────────────────────────────────────────────────
BLACKMARKET_REFRESH_SECONDS = 120

class BlackMarketScreen:
    STOCK_SIZE = 4

    def __init__(self, save):
        self.save=save; self.sel=0; self.anim_t=0; self._ensure_stock()

    def _ensure_stock(self):
        now = time.time()
        bm = self.save.setdefault("blackmarket",{"stock":[],"refresh_at":0})
        if now >= bm.get("refresh_at",0) or len(bm.get("stock",[]))==0:
            self._refresh_stock(bm, now)

    def _refresh_stock(self, bm, now):
        all_names=list(ALL_MOONIES_DICT.keys()); picks=[]; used=set()
        for _ in range(self.STOCK_SIZE*10):
            if len(picks)>=self.STOCK_SIZE: break
            name=random.choice(all_names)
            if name in used: continue
            used.add(name); m=ALL_MOONIES_DICT[name]
            is_shiny=random.random()<0.15
            base_prices={"common":8000,"uncommon":14000,"rare":28000,"epic":55000,"legendary":120000}
            price=base_prices.get(m.rarity,800)
            if is_shiny: price=int(price*3.5)
            picks.append({"name":name,"shiny":is_shiny,"price":price})
        bm["stock"]=picks; bm["refresh_at"]=now+BLACKMARKET_REFRESH_SECONDS
        self.save["blackmarket"]=bm

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN: return None
        k=event.key
        if k in (pygame.K_ESCAPE,pygame.K_x): return "close"
        stock=self.save.get("blackmarket",{}).get("stock",[])
        if k in (pygame.K_UP,pygame.K_w,pygame.K_LEFT,pygame.K_a): self.sel=max(0,self.sel-1)
        elif k in (pygame.K_DOWN,pygame.K_s,pygame.K_RIGHT,pygame.K_d): self.sel=min(len(stock)-1,self.sel+1)
        elif k in (pygame.K_RETURN,pygame.K_z): self._buy(stock)
        return None

    def _buy(self, stock):
        if not stock or self.sel>=len(stock): return
        item=stock[self.sel]; price=item["price"]
        if self.save.get("coins",0)<price:
            notify("Nicht genug Coins! 💰",C_RED,160); return
        self.save["coins"]-=price
        album=self.save.setdefault("card_album",{})
        entry=album.setdefault(item["name"],{"count":0,"shiny":0})
        key="shiny" if item["shiny"] else "count"
        entry[key]+=1
        notify(f"{'✨ Glitzerkarte' if item['shiny'] else '🃏 Karte'} von {item['name']} gekauft!",C_YELLOW,200)
        stock.pop(self.sel); self.sel=min(self.sel,max(0,len(stock)-1))
        self.save["blackmarket"]["stock"]=stock

    def draw(self, surf):
        self.anim_t+=1; self._ensure_stock()
        surf.fill((6,6,10))
        skull=load_img("assets/skull.png",(SW,SH)); surf.blit(skull,(0,0))
        dark_overlay=pygame.Surface((SW,SH),pygame.SRCALPHA); dark_overlay.fill((0,0,0,170)); surf.blit(dark_overlay,(0,0))
        draw_rounded_rect(surf,(18,10,30),(0,0,SW,50),0)
        draw_text(surf,"💀 Schwarzmarkt",F_BIG,(180,50,220),SW//2,5,center=True,shadow=True)
        draw_text(surf,f"💰 {self.save.get('coins',0)} Coins   Sortiment aktualisiert sich alle {BLACKMARKET_REFRESH_SECONDS}s   ESC zurück",F_TINY,C_GRAY,SW//2,35,center=True)
        bm=self.save.get("blackmarket",{}); secs_left=max(0,int(bm.get("refresh_at",0)-time.time()))
        mins,secs2=divmod(secs_left,60)
        draw_text(surf,f"🔄 Nächste Aktualisierung: {mins}:{secs2:02d}",F_TINY,(140,80,200),SW-200,38)
        stock=bm.get("stock",[])
        if not stock:
            draw_text(surf,"Kein Sortiment verfügbar.",F_MED,C_GRAY,SW//2,SH//2,center=True); draw_notifications(surf); return
        card_w,card_h=175,245
        total_cw=len(stock)*card_w+(len(stock)-1)*18
        cards_x=SW//2-total_cw//2; cards_y=60
        for i,item in enumerate(stock):
            sel=(i==self.sel); name=item["name"]; shiny=item["shiny"]; price=item["price"]
            m=ALL_MOONIES_DICT.get(name); cx=cards_x+i*(card_w+18); cy=cards_y
            if sel: cy-=12
            draw_tcg_card(surf,cx,cy,card_w,card_h,name,m,is_shiny=shiny,anim_t=self.anim_t,idx=i,selected=sel)
            price_y=cy+card_h+6; can_afford=self.save.get("coins",0)>=price
            pc=C_GREEN if can_afford else C_RED
            draw_rounded_rect(surf,(30,50,20) if can_afford else (50,20,20),(cx,price_y,card_w,24),6,2,pc)
            draw_text(surf,f"💰 {price:,}",F_SMALL,pc,cx+card_w//2,price_y+3,center=True)
            if sel:
                draw_text(surf,"[ ENTER ] Kaufen",F_TINY,C_YELLOW,cx+card_w//2,price_y+30,center=True,shadow=True)
        draw_notifications(surf)


# ── Shop screen ────────────────────────────────────────────────────────────────
class ShopScreen:
    ITEMS = [
        {"name": "Pokéball x5",       "cost":    50, "desc": "Fange wilde Pokémon (5 Stück)",       "key": "balls",               "amount": 5,  "icon": "balls"},
        {"name": "Trank",             "cost":    20, "desc": "Heilt 30 HP",                         "key": "potions",             "amount": 1,  "icon": "potions"},
        {"name": "Super Trank",       "cost":    45, "desc": "Heilt 80 HP",                         "key": "super_potions",       "amount": 1,  "icon": "super_potions"},
        {"name": "Trank x5",          "cost":    80, "desc": "Heilt 30 HP (5 Stück)",               "key": "potions",             "amount": 5,  "icon": "potions"},
        {"name": "Hyper Trank",       "cost":   120, "desc": "Heilt 150 HP",                        "key": "hyper_potions",       "amount": 1,  "icon": "hyper_potions"},
        {"name": "Energy Drink",      "cost":  3000, "desc": "3 Runden 2× Angriff, dann Pause",     "key": "redbull",             "amount": 1,  "icon": "redbull"},
        {"name": "Sonderbonbon",      "cost":  5000, "desc": "+1 Level für ein Pokémon",            "key": "sonderbonbons",       "amount": 1,  "icon": "sonderbonbons"},
        {"name": "Beleber",           "cost":   400, "desc": "Belebt besiegtes Pokémon (½ HP)",     "key": "beleber",             "amount": 1,  "icon": "beleber"},
        {"name": "Top-Beleber",       "cost":   800, "desc": "Belebt besiegtes Pokémon (voll HP)",  "key": "top_beleber",         "amount": 1,  "icon": "top_beleber"},
        {"name": "💎 Entwicklungsstein","cost":50000,"desc": "Entwickelt ein Pokémon sofort!",      "key": "entwicklungsstein",   "amount": 1,  "icon": "entwicklungsstein"},
        {"name": "Raid-Pass",         "cost": 10000, "desc": "Zutritt zu einem Raid",               "key": "raid_passes",         "amount": 1,  "icon": "raid_passes"},
        {"name": "Premium Raid-Pass", "cost": 30000, "desc": "Raid erleichtert + Zutritt",          "key": "premium_raid_passes", "amount": 1,  "icon": "premium_raid_passes"},
    ]
    VISIBLE = 6
    ROW_H   = 58
    PANEL_X = 50
    PANEL_W = 520
    PANEL_Y = 75

    def __init__(self, save_data, team):
        self.save=save_data; self.team=team; self.sel=0; self.scroll=0

    def _clamp_scroll(self):
        if self.sel < self.scroll: self.scroll=self.sel
        elif self.sel >= self.scroll+self.VISIBLE: self.scroll=self.sel-self.VISIBLE+1
        self.scroll=max(0,min(self.scroll,max(0,len(self.ITEMS)-self.VISIBLE)))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.sel=(self.sel-1)%len(self.ITEMS); self._clamp_scroll()
            elif event.key == pygame.K_DOWN:
                self.sel=(self.sel+1)%len(self.ITEMS); self._clamp_scroll()
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                self.buy(self.sel)
            elif event.key in (pygame.K_ESCAPE, pygame.K_x):
                return "close"
        return None

    def buy(self, idx):
        item=self.ITEMS[idx]
        if self.save.get("coins",0)<item["cost"]:
            notify("Nicht genug Münzen! 💰",C_RED); return
        self.save["coins"]-=item["cost"]
        self.save[item["key"]]=self.save.get(item["key"],0)+item["amount"]
        notify(f"+{item['amount']}× {item['name']} gekauft!",C_GREEN)

    def draw(self, surf):
        surf.fill(C_BG)
        shop_img=load_img("assets/shop.png",(SW,SH)); surf.blit(shop_img,(0,0))
        px=self.PANEL_X; pw=self.PANEL_W; py=self.PANEL_Y
        header_h=80; list_h=self.VISIBLE*self.ROW_H+8; footer_h=30; total_h=header_h+list_h+footer_h
        panel=pygame.Surface((pw,total_h),pygame.SRCALPHA); panel.fill((15,18,28,225)); surf.blit(panel,(px,py))
        pygame.draw.rect(surf,C_YELLOW,(px,py,pw,total_h),2,border_radius=10)
        draw_text(surf,"Pokéstore",F_BIG,C_YELLOW,px+pw//2,py+8,center=True,shadow=True)
        coins=self.save.get('coins',0); balls=self.save.get('balls',0)
        mb=self.save.get('master_balls',0); sb=self.save.get('sonderbonbons',0)
        st=self.save.get('entwicklungsstein',0)
        info=f"💰 {coins:,}   🎯 {balls} Bälle"
        if mb: info+=f"   ✦ {mb} MB"
        if sb: info+=f"   🍬 {sb} SB"
        if st: info+=f"   💎 {st} Stein"
        draw_text(surf,info,F_SMALL,C_WHITE,px+pw//2,py+48,center=True)
        list_y=py+header_h
        clip=surf.get_clip(); surf.set_clip(pygame.Rect(px,list_y,pw,list_h))
        for i in range(self.scroll,min(self.scroll+self.VISIBLE,len(self.ITEMS))):
            item=self.ITEMS[i]; row=i-self.scroll; iy=list_y+4+row*self.ROW_H
            sel=(i==self.sel); can_afford=self.save.get("coins",0)>=item["cost"]
            bg=(35,60,110) if sel else (22,26,40); bdr=C_YELLOW if sel else (55,60,80)
            if sel:
                glow=pygame.Surface((pw-20,self.ROW_H-6),pygame.SRCALPHA); glow.fill((255,220,50,30)); surf.blit(glow,(px+10,iy))
            draw_rounded_rect(surf,bg,(px+10,iy,pw-20,self.ROW_H-6),8,2 if sel else 1,bdr)
            icon=item_icon(item.get("icon",""),38)
            if icon: surf.blit(icon,(px+18,iy+(self.ROW_H-6-38)//2))
            nc=C_YELLOW if sel else C_WHITE
            draw_text(surf,item["name"],F_MED,nc,px+64,iy+6,shadow=True)
            draw_text(surf,item["desc"],F_TINY,(160,165,180),px+64,iy+28)
            price_str=f"💰 {item['cost']:,}"; price_col=C_GREEN if can_afford else (180,60,60)
            price_surf=F_MED.render(price_str,True,price_col)
            surf.blit(price_surf,(px+pw-price_surf.get_width()-16,iy+12))
        surf.set_clip(clip)
        if len(self.ITEMS)>self.VISIBLE:
            sb_x=px+pw-10; sb_top=list_y+4; sb_total=list_h-8
            thumb_h=max(20,sb_total*self.VISIBLE//len(self.ITEMS))
            thumb_y=sb_top+(sb_total-thumb_h)*self.scroll//max(1,len(self.ITEMS)-self.VISIBLE)
            pygame.draw.rect(surf,(40,45,60),(sb_x,sb_top,6,sb_total),border_radius=3)
            pygame.draw.rect(surf,C_YELLOW,(sb_x,thumb_y,6,thumb_h),border_radius=3)
        foot_y=py+header_h+list_h+6
        draw_text(surf,"↑↓ scrollen   ENTER kaufen   ESC zurück",F_TINY,C_GRAY,px+pw//2,foot_y,center=True)
        draw_notifications(surf)


# ── Pokémon Center ─────────────────────────────────────────────────────────────
class PokeCenterScreen:
    def __init__(self, save_data, team):
        self.save=save_data; self.team=team; self.healed=False; self.anim_t=0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN: return None
        k=event.key
        if k in (pygame.K_ESCAPE, pygame.K_x, pygame.K_b): return "close"
        if k in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
            if not self.healed:
                for m in self.team: m.current_hp=m.max_hp
                self.healed=True; notify("Team vollständig geheilt!",C_GREEN,200)
            else: return "close"
        return None

    def draw(self, surf):
        center_img=load_img("assets/center.png",(SW,SH)); surf.blit(center_img,(0,0))
        panel=pygame.Surface((440,360),pygame.SRCALPHA); panel.fill((10,14,24,220)); surf.blit(panel,(SW//2-220,SH//2-200))
        draw_text(surf,"Pokémon Center",F_BIG,(255,180,220),SW//2,SH//2-192,center=True,shadow=True)
        draw_text(surf,"Willkommen! Wir heilen dein Team.",F_SMALL,C_WHITE,SW//2,SH//2-155,center=True)
        if self.team:
            tw=min(len(self.team),3); cw=120; sx=SW//2-(tw*(cw+8))//2
            for i,m in enumerate(self.team[:6]):
                col_x=sx+(i%3)*(cw+8); col_y=SH//2-120+(i//3)*90
                draw_rounded_rect(surf,C_PANEL,(col_x,col_y,cw,82),8,1,C_GREEN if m.current_hp==m.max_hp else C_RED)
                img=load_img(m.image,(44,44)); surf.blit(img,(col_x+4,col_y+4))
                draw_text(surf,m.name[:10],F_TINY,C_WHITE,col_x+cw//2,col_y+52,center=True)
                draw_hp_bar(surf,col_x+4,col_y+68,cw-8,8,m.current_hp,m.max_hp,label=False)
        if not self.healed:
            draw_rounded_rect(surf,(40,120,60),(SW//2-200,SH//2+70,190,48),12,2,C_GREEN)
            draw_text(surf,"[ ENTER ] Heilen",F_SMALL,C_WHITE,SW//2-105,SH//2+84,center=True,shadow=True)
        else:
            self.anim_t+=1
            pulse=abs(math.sin(self.anim_t*0.1)); col=(int(80+pulse*120),int(200+pulse*50),int(80+pulse*80))
            draw_text(surf,"✓ Team vollständig geheilt!",F_MED,col,SW//2,SH//2+80,center=True,shadow=True)
        draw_rounded_rect(surf,(120,40,40),(SW//2+10,SH//2+70,190,48),12,2,C_RED)
        draw_text(surf,"[ ESC ] Verlassen",F_SMALL,C_WHITE,SW//2+105,SH//2+84,center=True,shadow=True)
        draw_notifications(surf)


# ── Overworld / Main map ───────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
# TAG/NACHT-ZYKLUS
# ══════════════════════════════════════════════════════════════════════════════

def get_time_of_day():
    """Returns (phase, label, overlay_rgba) based on real clock."""
    h = _dt.datetime.now().hour
    m = _dt.datetime.now().minute
    hf = h + m / 60.0  # fractional hour
    if  5.5 <= hf <  7:  return "dawn",    "Morgenröte",  (255, 140,  60, 55)
    if  7   <= hf < 11:  return "morning", "Morgen",      (255, 220, 150, 15)
    if 11   <= hf < 16:  return "day",     "Tag",         (255, 255, 200,  0)
    if 16   <= hf < 18:  return "afternoon","Nachmittag", (255, 180,  80, 25)
    if 18   <= hf < 20:  return "dusk",    "Abendrot",    (220,  80,  30, 60)
    if 20   <= hf < 22:  return "evening", "Abend",       ( 40,  20,  90, 90)
    if 22   <= hf < 24:  return "night",   "Nacht",       (  5,   5,  40,130)
    return "night", "Mitternacht", (0, 0, 35, 150)

def get_sun_moon_pos(phase):
    """Returns (x, y, radius, color, is_moon) for sky object."""
    h = _dt.datetime.now().hour + _dt.datetime.now().minute / 60.0
    if phase in ("night","evening"):
        # Moon arc: rises ~20h, sets ~6h
        t = ((h - 20) % 24) / 10.0  # 0..1 across night
        t = max(0, min(1, t))
        x = int(SW * 0.15 + t * SW * 0.7)
        y = int(SH * 0.3 - math.sin(t * math.pi) * SH * 0.22)
        return x, y, 18, (220, 230, 255), True
    elif phase in ("dawn","morning","day","afternoon","dusk"):
        # Sun arc: rises ~6h, sets ~19h
        t = max(0, min(1, (h - 6) / 13.0))
        x = int(SW * 0.08 + t * SW * 0.84)
        y = int(SH * 0.35 - math.sin(t * math.pi) * SH * 0.25)
        col = (255, 200, 60) if phase == "day" else               (255, 140, 40) if phase in ("dusk","dawn") else (255, 220, 100)
        return x, y, 22, col, False
    return SW//2, 80, 20, (255,220,100), False

def get_night_spawn_bonus(all_moonies_dict):
    """At night, ghost/dark/psychic types spawn more often."""
    night_types = {"Geist","Dunkel","Psycho"}
    return night_types

def apply_day_night_overlay(surf, phase, overlay_rgba):
    """Blit a colored overlay for time-of-day atmosphere."""
    r,g,b,a = overlay_rgba
    if a == 0: return
    ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
    ov.fill((r,g,b,a))
    surf.blit(ov, (0,0))

def day_night_star_overlay(surf, phase):
    """Draw stars at night/evening + sun or moon object."""
    # Stars
    if phase in ("night","evening","dusk","dawn"):
        n_stars = {"night":80,"evening":40,"dusk":15,"dawn":10}.get(phase,0)
        alpha   = {"night":210,"evening":130,"dusk":50,"dawn":25}.get(phase,0)
        t_ms = pygame.time.get_ticks()
        rng = random.Random(42)
        for i in range(n_stars):
            sx = rng.randint(0, SW)
            sy = rng.randint(56, SH//2 - 20)
            sz = rng.choice([1,1,1,2])
            # Twinkling: each star has its own phase
            twinkle = int(alpha * (0.6 + 0.4 * math.sin(t_ms * 0.001 * rng.uniform(0.5, 2.5) + i)))
            twinkle = max(20, min(255, twinkle))
            s2 = pygame.Surface((sz*2+1, sz*2+1), pygame.SRCALPHA)
            pygame.draw.circle(s2, (255, 255, 220, twinkle), (sz, sz), sz)
            surf.blit(s2, (sx - sz, sy - sz))

    # Sun / Moon
    sx, sy, sr, scol, is_moon = get_sun_moon_pos(phase)
    if sy < SH - 60:  # only draw if in sky area
        if is_moon:
            # Moon: glowing circle with slightly darker crescent hint
            glow = pygame.Surface((sr*6, sr*6), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*scol, 30), (sr*3, sr*3), sr*3)
            pygame.draw.circle(glow, (*scol, 60), (sr*3, sr*3), int(sr*2))
            surf.blit(glow, (sx - sr*3, sy - sr*3))
            pygame.draw.circle(surf, scol, (sx, sy), sr)
            # Crescent shadow
            pygame.draw.circle(surf, (15, 15, 50), (sx + sr//3, sy - sr//4), int(sr * 0.8))
        else:
            # Sun: radial glow layers
            for radius, a in [(sr*4, 20), (sr*3, 35), (sr*2, 55)]:
                glow = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*scol, a), (radius, radius), radius)
                surf.blit(glow, (sx - radius, sy - radius))
            pygame.draw.circle(surf, scol, (sx, sy), sr)
            pygame.draw.circle(surf, (255, 255, 240), (sx, sy), max(1, sr - 5))

# Moon icon displayed in HUD at night
def day_night_icon(phase):
    return {"day":"☀","morning":"🌤","afternoon":"🌤","dawn":"🌅","dusk":"🌇","evening":"🌙","night":"🌑"}.get(phase,"☀")


# ══════════════════════════════════════════════════════════════════════════════
# MAP-DEFINITIONEN — 18 Pokémon-Typen
# ══════════════════════════════════════════════════════════════════════════════

# Each map definition:
#   bg_color     : base ground fill color
#   grid_color   : grid line color
#   grass_tint   : (R,G,B) multiplicative tint applied over grass tiles
#   particle_col : grass rustle particle color
#   weather_pool : list of weather names allowed on this map (random each day)
#   buildings    : set of building keys present on this map
#   spawn_types  : pokémon types that spawn here (None = all)
#   ambient      : optional ambient overlay color + alpha (R,G,B,A) or None
#   name         : display name
#   icon         : emoji icon

MAP_DEFS = {
    "Normal":   {"bg":(45,80,45),  "grid":(42,75,42),   "grass_tint":(255,255,255),
                 "particle":(80,180,80),  "weather_pool":["Klar","Sonnig","Windig"],
                 "buildings":{"shop","center","pc","daily","guild"},
                 "spawn_types":["Normal"],
                 "ambient":None, "name":"Normal-Welt", "icon":"⬜"},

    "Feuer":    {"bg":(80,30,10),  "grid":(90,35,12),   "grass_tint":(255,80,20),
                 "particle":(255,100,30), "weather_pool":["Sonnig","Klar"],
                 "buildings":{"pc"},
                 "spawn_types":["Feuer"],
                 "ambient":(255,60,0,18), "name":"Feuer-Welt", "icon":"🔥"},

    "Wasser":   {"bg":(10,40,80),  "grid":(12,45,90),   "grass_tint":(30,120,255),
                 "particle":(50,150,255), "weather_pool":["Regen","Klar"],
                 "buildings":{"pc","center"},
                 "spawn_types":["Wasser"],
                 "ambient":(0,80,200,20), "name":"Wasser-Welt", "icon":"💧"},

    "Pflanze":  {"bg":(20,60,20),  "grid":(22,65,22),   "grass_tint":(80,255,60),
                 "particle":(100,220,60), "weather_pool":["Klar","Regen","Sonnig"],
                 "buildings":{"pc"},
                 "spawn_types":["Pflanze"],
                 "ambient":(40,200,0,15), "name":"Pflanze-Welt", "icon":"🌿"},

    "Elektro":  {"bg":(50,50,10),  "grid":(55,55,12),   "grass_tint":(255,240,30),
                 "particle":(255,240,50), "weather_pool":["Gewitter","Klar"],
                 "buildings":{"pc"},
                 "spawn_types":["Elektro"],
                 "ambient":(255,220,0,15), "name":"Elektro-Welt", "icon":"⚡"},

    "Eis":      {"bg":(180,220,240),"grid":(170,210,230),"grass_tint":(200,240,255),
                 "particle":(200,240,255),"weather_pool":["Schnee","Klar"],
                 "buildings":{"pc","center"},
                 "spawn_types":["Eis"],
                 "ambient":(180,230,255,20), "name":"Eis-Welt", "icon":"❄"},

    "Kampf":    {"bg":(80,20,20),  "grid":(85,22,22),   "grass_tint":(220,60,40),
                 "particle":(220,80,50),  "weather_pool":["Klar","Sonnig"],
                 "buildings":{"pc","arena"},
                 "spawn_types":["Kampf"],
                 "ambient":(180,30,0,18), "name":"Kampf-Welt", "icon":"🥊"},

    "Gift":     {"bg":(50,10,60),  "grid":(55,12,65),   "grass_tint":(180,40,220),
                 "particle":(180,60,220), "weather_pool":["Nebel","Klar"],
                 "buildings":{"pc"},
                 "spawn_types":["Gift"],
                 "ambient":(120,0,180,20), "name":"Gift-Welt", "icon":"☠"},

    "Boden":    {"bg":(100,70,30), "grid":(105,73,33),  "grass_tint":(200,150,60),
                 "particle":(200,150,60), "weather_pool":["Sandsturm","Klar","Sonnig"],
                 "buildings":{"pc"},
                 "spawn_types":["Boden"],
                 "ambient":(180,120,0,15), "name":"Boden-Welt", "icon":"🪨"},

    "Flug":     {"bg":(100,140,200),"grid":(105,145,205),"grass_tint":(160,210,255),
                 "particle":(160,210,255),"weather_pool":["Windig","Klar"],
                 "buildings":{"pc"},
                 "spawn_types":["Flug"],
                 "ambient":(100,160,255,15), "name":"Flug-Welt", "icon":"🦅"},

    "Psycho":   {"bg":(80,20,80),  "grid":(85,22,85),   "grass_tint":(255,80,200),
                 "particle":(255,100,220),"weather_pool":["Nebel","Klar"],
                 "buildings":{"pc","daily"},
                 "spawn_types":["Psycho"],
                 "ambient":(200,0,200,18), "name":"Psycho-Welt", "icon":"🔮"},

    "Käfer":    {"bg":(30,60,10),  "grid":(32,63,12),   "grass_tint":(100,200,40),
                 "particle":(120,200,50), "weather_pool":["Klar","Regen"],
                 "buildings":{"pc"},
                 "spawn_types":["Käfer"],
                 "ambient":(60,180,0,15), "name":"Käfer-Welt", "icon":"🐛"},

    "Gestein":  {"bg":(80,70,60),  "grid":(83,73,63),   "grass_tint":(180,160,120),
                 "particle":(180,160,120),"weather_pool":["Sandsturm","Klar"],
                 "buildings":{"pc"},
                 "spawn_types":["Gestein"],
                 "ambient":(150,120,60,15), "name":"Gestein-Welt", "icon":"🗿"},

    "Geist":    {"bg":(20,10,30),  "grid":(22,12,33),   "grass_tint":(120,60,180),
                 "particle":(140,80,200), "weather_pool":["Nebel","Klar"],
                 "buildings":{"pc"},
                 "spawn_types":["Geist"],
                 "ambient":(80,0,120,25), "name":"Geist-Welt", "icon":"👻"},

    "Drache":   {"bg":(20,20,80),  "grid":(22,22,85),   "grass_tint":(60,80,220),
                 "particle":(80,100,240), "weather_pool":["Windig","Gewitter","Klar"],
                 "buildings":{"pc","guild"},
                 "spawn_types":["Drache"],
                 "ambient":(0,40,200,20), "name":"Drachen-Welt", "icon":"🐉"},

    "Dunkel":   {"bg":(10,10,20),  "grid":(12,12,22),   "grass_tint":(60,40,100),
                 "particle":(100,60,160), "weather_pool":["Nebel","Klar"],
                 "buildings":{"pc","blackmarket"},
                 "spawn_types":["Dunkel"],
                 "ambient":(20,0,40,30), "name":"Dunkel-Welt", "icon":"🌑"},

    "Stahl":    {"bg":(60,70,80),  "grid":(63,73,83),   "grass_tint":(160,180,200),
                 "particle":(180,200,220),"weather_pool":["Klar","Windig"],
                 "buildings":{"pc","shop"},
                 "spawn_types":["Stahl"],
                 "ambient":(120,140,180,15), "name":"Stahl-Welt", "icon":"⚙"},

    "Fee":      {"bg":(80,20,60),  "grid":(83,22,63),   "grass_tint":(255,160,220),
                 "particle":(255,180,230),"weather_pool":["Klar","Sonnig"],
                 "buildings":{"pc","center"},
                 "spawn_types":["Fee"],
                 "ambient":(255,100,200,18), "name":"Fee-Welt", "icon":"🌸"},
}

MAP_ORDER = ["Normal","Feuer","Wasser","Pflanze","Elektro","Eis","Kampf","Gift",
             "Boden","Flug","Psycho","Käfer","Gestein","Geist","Drache","Dunkel","Stahl","Fee"]

def tint_surface(surf, tint_rgb):
    """Apply a multiplicative RGB tint to a surface copy."""
    if tint_rgb == (255, 255, 255):
        return surf  # no tint needed
    tinted = surf.copy()
    tint_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    tint_surf.fill((*tint_rgb, 255))
    tinted.blit(tint_surf, (0,0), special_flags=pygame.BLEND_RGB_MULT)
    return tinted

_tint_cache = {}  # (image_path, tint_rgb) → tinted Surface

def load_img_tinted(path, size, tint):
    key = (path, size, tint)
    if key in _tint_cache:
        return _tint_cache[key]
    base = load_img(path, size)
    result = tint_surface(base, tint)
    _tint_cache[key] = result
    return result

def get_map_weather(map_key, save):
    """Get today's weather for a specific map (independent per map)."""
    today = _today_str()
    weather_data = save.setdefault("map_weather", {})
    if weather_data.get(map_key, {}).get("date") == today:
        name = weather_data[map_key]["weather"]
        return next((w for w in WEATHER_LIST if w["name"] == name), WEATHER_LIST[0])
    # New day — pick from map's weather pool
    pool_names = MAP_DEFS[map_key]["weather_pool"]
    pool = [w for w in WEATHER_LIST if w["name"] in pool_names] or WEATHER_LIST
    day_seed = int(_dt.date.today().strftime("%Y%m%d"))
    rng = random.Random(day_seed + hash(map_key) % 10000)
    w = rng.choice(pool)
    weather_data[map_key] = {"date": today, "weather": w["name"]}
    return w


class OverworldScreen:
    GRASS_RECTS = [
        pygame.Rect(100, 210, 200, 170),
        pygame.Rect(500, 160, 240, 190),
        pygame.Rect(300, 390, 200, 150),
        pygame.Rect(650, 360, 170, 140),
        pygame.Rect(55, 430, 145, 115),
    ]
    SHOP_RECT   = pygame.Rect(30,   58, 140, 90)
    CENTER_RECT = pygame.Rect(210,  58, 140, 90)
    PC_RECT     = pygame.Rect(SW - 300, 58, 130, 80)
    ARENA_RECT  = pygame.Rect(SW//2 - 70, 58, 140, 90)
    SKULL_RECT  = pygame.Rect(SW - 160, SH - 120, 130, 85)
    DAILY_RECT  = pygame.Rect(SW//2 + 100, SH - 120, 130, 85)
    MAX_TRAINERS = 4

    def __init__(self, save_data, flashcards, map_key="Normal"):
        self.save=save_data; self.cards=flashcards
        self.map_key = map_key
        self.map_def = MAP_DEFS.get(map_key, MAP_DEFS["Normal"])
        self.player_x=450.0; self.player_y=350.0; self.speed=3.0
        self.step_anim=0; self.encounter_timer=0
        self.trainer_cooldown={}; self.center_cooldown=0; self.blackmarket_cooldown=0; self.daily_cooldown=0
        self.pending_action=None; self.in_grass=False; self.grass_particle_t=0
        self._ach_cb=None; self._trainers=[]; self._spawn_timer=random.randint(180,480)
        self._spawn_initial()
        self.raid=None; self.raid_timer=0; self._raid_spawn_timer=random.randint(1800,5400)
        # Buildings active on this map
        self._buildings = self.map_def["buildings"]
        # Weather particles
        self._wx_particles = []   # list of dicts per weather type
        self._wx_t = 0            # weather animation timer
        self._lightning_t = 0     # countdown to next lightning flash
        self._lightning_flash = 0 # brightness of current flash (fades)
        self._fog_offset = 0.0    # drifting fog offset

    # ── Weather system ──────────────────────────────────────────────────────────

    def _update_weather(self):
        self._wx_t += 1
        w = get_map_weather(self.map_key, self.save)
        name = w["name"]

        # ── Rain ──
        if name == "Regen":
            for _ in range(3):
                self._wx_particles.append({
                    "type": "rain",
                    "x": random.uniform(-80, SW),
                    "y": random.uniform(-60, -2),
                    "vx": -3.0, "vy": random.uniform(16, 22),
                    "life": 1.0,
                })

        # ── Thunderstorm: rain + lightning ──
        elif name == "Gewitter":
            for _ in range(5):
                self._wx_particles.append({
                    "type": "rain",
                    "x": random.uniform(-80, SW),
                    "y": random.uniform(-60, -2),
                    "vx": -4.0, "vy": random.uniform(18, 26),
                    "life": 1.0,
                })
            # Tick lightning countdown
            self._lightning_t -= 1
            if self._lightning_t <= 0 and self._lightning_flash == 0:
                # New strike
                self._lightning_t  = random.randint(90, 300)
                self._lightning_flash = 220
            # Fade flash
            if self._lightning_flash > 0:
                self._lightning_flash = max(0, self._lightning_flash - 18)

        # ── Snow ──
        elif name == "Schnee":
            for _ in range(2):
                self._wx_particles.append({
                    "type": "snow",
                    "x": random.uniform(0, SW),
                    "y": random.uniform(-20, -2),
                    "vx": random.uniform(-0.4, 0.4),
                    "vy": random.uniform(1.2, 3.0),
                    "wobble": random.uniform(0, 6.28),
                    "size": random.randint(2, 5),
                    "life": 1.0,
                })

        # ── Fog: just drift the offset, rendered as smooth overlays ──
        elif name == "Nebel":
            self._fog_offset = (self._fog_offset + 0.4) % (SW * 2)

        # ── Sandstorm: many streaks flying across ──
        elif name == "Sandsturm":
            for _ in range(6):
                self._wx_particles.append({
                    "type": "sand",
                    "x": -random.uniform(10, 60),
                    "y": random.uniform(54, SH - 20),
                    "vx": random.uniform(10, 20),
                    "vy": random.uniform(-0.8, 0.8),
                    "length": random.randint(8, 28),
                    "alpha": random.randint(140, 220),
                    "life": 1.0,
                })

        # ── Wind: long light streaks ──
        elif name == "Windig":
            if self._wx_t % 2 == 0:
                self._wx_particles.append({
                    "type": "wind",
                    "x": -random.uniform(20, 80),
                    "y": random.uniform(54, SH - 60),
                    "vx": random.uniform(8, 14),
                    "vy": random.uniform(-0.3, 0.3),
                    "length": random.randint(40, 100),
                    "alpha": random.randint(50, 110),
                    "life": 1.0,
                })

        # ── Sunny sparkles ──
        elif name == "Sonnig":
            if self._wx_t % 6 == 0:
                self._wx_particles.append({
                    "type": "sparkle",
                    "x": random.uniform(0, SW),
                    "y": random.uniform(54, SH),
                    "size": random.randint(2, 5),
                    "life": 1.0,
                    "phase": random.uniform(0, 6.28),
                })

        # ── Update + cull all particles ──
        alive = []
        for p in self._wx_particles:
            pt = p["type"]
            if pt == "rain":
                p["x"] += p["vx"]; p["y"] += p["vy"]
                if p["y"] > SH + 10: continue
            elif pt == "snow":
                p["wobble"] += 0.04
                p["x"] += p["vx"] + math.sin(p["wobble"]) * 0.5
                p["y"] += p["vy"]
                if p["y"] > SH + 10: continue
            elif pt == "sand":
                p["x"] += p["vx"]; p["y"] += p["vy"]
                p["life"] -= 0.006
                if p["x"] > SW + 40 or p["life"] <= 0: continue
            elif pt == "wind":
                p["x"] += p["vx"]; p["y"] += p["vy"]
                p["life"] -= 0.009
                if p["x"] > SW + 120 or p["life"] <= 0: continue
            elif pt == "sparkle":
                p["life"] -= 0.022
                if p["life"] <= 0: continue
            alive.append(p)
        self._wx_particles = alive[-800:]

    def _draw_weather(self, surf):
        w = get_map_weather(self.map_key, self.save)
        name = w["name"]

        # ── Lightning flash overlay ──
        if name == "Gewitter" and self._lightning_flash > 0:
            flash = pygame.Surface((SW, SH), pygame.SRCALPHA)
            flash.fill((220, 230, 255, min(255, self._lightning_flash)))
            surf.blit(flash, (0, 0))

        # ── Fog: 3 smooth drifting semi-transparent bands ──
        if name == "Nebel":
            t = self._wx_t
            for layer, (speed, alpha, thick) in enumerate([
                (0.4,  45, 80),   # slow thick front layer
                (0.25, 28, 60),   # medium mid layer
                (0.12, 18, 100),  # fast thin back layer
            ]):
                offset = int((self._fog_offset * speed * (layer + 1)) % SW)
                fog_s = pygame.Surface((SW + 20, thick), pygame.SRCALPHA)
                # Horizontal gradient fill — feathered top and bottom
                for row in range(thick):
                    fade = math.sin(row / thick * math.pi)  # 0→1→0
                    a = int(alpha * fade)
                    if a < 2: continue
                    fog_s.fill((200, 210, 225, a), (0, row, SW + 20, 1))
                base_y = 200 + layer * 180 + int(12 * math.sin(t * 0.008 + layer * 2.1))
                # Draw twice to wrap seamlessly
                surf.blit(fog_s, (-offset, base_y))
                surf.blit(fog_s, (SW - offset, base_y))
                surf.blit(fog_s, (-offset, base_y + 220))
                surf.blit(fog_s, (SW - offset, base_y + 220))

        # ── Draw particles ──
        for p in self._wx_particles:
            pt = p["type"]

            if pt == "rain":
                x, y = int(p["x"]), int(p["y"])
                s = pygame.Surface((2, 16), pygame.SRCALPHA)
                s.fill((150, 190, 255, 160))
                surf.blit(s, (x, y))

            elif pt == "snow":
                x, y = int(p["x"]), int(p["y"])
                sz = p["size"]
                s = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
                pygame.draw.circle(s, (235, 245, 255, 210), (sz, sz), sz)
                surf.blit(s, (x - sz, y - sz))

            elif pt == "sand":
                # Draw as a short horizontal streak line
                x, y = int(p["x"]), int(p["y"])
                a = int(p["alpha"] * p["life"])
                ln = p["length"]
                s = pygame.Surface((ln + 2, 3), pygame.SRCALPHA)
                # Gradient: bright centre, fade at ends
                for i in range(ln):
                    fade = math.sin(i / ln * math.pi)
                    pygame.draw.line(s, (210, 170, 80, int(a * fade)), (i, 1), (i, 1))
                surf.blit(s, (x, y))

            elif pt == "wind":
                x, y = int(p["x"]), int(p["y"])
                a = int(p["alpha"] * p["life"])
                length = int(p["length"])
                if length < 4: continue
                s = pygame.Surface((length + 4, 3), pygame.SRCALPHA)
                for i in range(length):
                    fade = math.sin(i / length * math.pi)
                    pygame.draw.line(s, (210, 230, 210, int(a * fade)), (i, 1), (i, 1))
                surf.blit(s, (x, y))

            elif pt == "sparkle":
                x, y = int(p["x"]), int(p["y"])
                a = int(200 * math.sin(p["life"] * math.pi))
                sz = p["size"]
                s = pygame.Surface((sz*4+2, sz*4+2), pygame.SRCALPHA)
                cx2, cy2 = sz*2, sz*2
                hs = max(1, sz)
                pygame.draw.line(s, (255, 240, 100, a), (cx2-hs*2, cy2), (cx2+hs*2, cy2), 1)
                pygame.draw.line(s, (255, 240, 100, a), (cx2, cy2-hs*2), (cx2, cy2+hs*2), 1)
                pygame.draw.circle(s, (255, 255, 200, a//2), (cx2, cy2), max(1,sz-1))
                surf.blit(s, (x - sz*2, y - sz*2))

        # ── Subtle color tint strip at top of play area ──
        badge_s = pygame.Surface((SW, 5), pygame.SRCALPHA)
        badge_s.fill((*w["color"], 50))
        surf.blit(badge_s, (0, 54))

    def _spawn_initial(self):
        import addEnemy; n=random.randint(1,self.MAX_TRAINERS); all_e=addEnemy.ALL_ENEMIES
        for _ in range(n): self._spawn_trainer(all_e)

    def _spawn_trainer(self, all_enemies=None):
        if len(self._trainers)>=self.MAX_TRAINERS: return
        # At night fewer trainers spawn (30% skip chance)
        phase_t, _, _ = get_time_of_day()
        if phase_t in ("night","evening") and random.random() < 0.35:
            return
        if all_enemies is None:
            import addEnemy; all_enemies=addEnemy.ALL_ENEMIES
        rockets=[e for e in all_enemies if e.isRocket]; normals=[e for e in all_enemies if not e.isRocket]
        # At night rockets appear more often (stealth)
        rocket_chance = 0.55 if phase_t in ("night","evening") else 0.3
        if random.random() < rocket_chance and rockets: enemy=random.choice(rockets)
        else: enemy=random.choice(normals)
        for _ in range(20):
            x=float(random.randint(80,SW-80)); y=float(random.randint(160,SH-80))
            dist=math.sqrt((x-self.player_x)**2+(y-self.player_y)**2)
            if dist>200: break
        self._trainers.append({"enemy":enemy,"x":x,"y":y,
            "vx":random.choice([-1,1])*random.uniform(0.5,1.3),
            "vy":random.choice([-1,1])*random.uniform(0.5,1.3),
            "move_t":0,"move_dir_t":random.randint(80,220),"alive":True})

    def get_trainer_img(self):
        path="assets/trainer2.png" if self.save.get("trainer")==1 else "assets/trainer.png"
        return load_img(path,(48,64))

    def _update_trainers(self):
        for t in self._trainers:
            t["move_t"]+=1
            if t["move_t"]>=t["move_dir_t"]:
                t["move_t"]=0; t["move_dir_t"]=random.randint(60,220)
                t["vx"]=random.choice([-1,1])*random.uniform(0.4,1.3)
                t["vy"]=random.choice([-1,1])*random.uniform(0.4,1.3)
            t["x"]+=t["vx"]; t["y"]+=t["vy"]
            if t["x"]<60 or t["x"]>SW-60: t["vx"]*=-1; t["x"]=max(60,min(SW-60,t["x"]))
            if t["y"]<160 or t["y"]>SH-80: t["vy"]*=-1; t["y"]=max(160,min(SH-80,t["y"]))
        self._spawn_timer-=1
        if self._spawn_timer<=0:
            self._spawn_timer=random.randint(300,900)
            if len(self._trainers)<self.MAX_TRAINERS and random.random()<0.7:
                self._spawn_trainer()

    def _despawn_trainer(self, idx):
        if 0<=idx<len(self._trainers):
            self._trainers.pop(idx)
            self._spawn_timer=min(self._spawn_timer,random.randint(300,600))
            new_cd={}
            for k,v in self.trainer_cooldown.items():
                if k<idx: new_cd[k]=v
                elif k>idx: new_cd[k-1]=v
            self.trainer_cooldown=new_cd

    def _update_raid(self):
        if self.raid is None:
            self._raid_spawn_timer-=1
            if self._raid_spawn_timer<=0: self._try_spawn_raid()
        else:
            if not self.raid.get("defeated") and not self.raid.get("catch_used"):
                self.raid_timer-=1
                if self.raid_timer<=0:
                    add_particles(self.ARENA_RECT.centerx,self.ARENA_RECT.centery,(200,50,50),n=30)
                    notify("Raid abgelaufen! Das Pokémon ist entkommen.",C_RED,200)
                    self.raid=None; self._raid_spawn_timer=random.randint(1800,7200)
            elif self.raid.get("catch_used") or (self.raid.get("defeated") and not self.raid.get("can_catch")):
                self.raid_timer-=1
                if self.raid_timer<=-300: self.raid=None; self._raid_spawn_timer=random.randint(1800,5400)

    def _try_spawn_raid(self):
        legendaries=[m for m in ALL_MOONIES_DICT.values() if m.rarity=="legendary"]
        rares=[m for m in ALL_MOONIES_DICT.values() if m.rarity=="rare"]
        pool=legendaries if legendaries else rares
        if not pool: return
        boss=random.choice(pool); level=random.randint(35,50); cards_needed=random.randint(2,5)
        self.raid={"name":boss.name,"image":boss.image,"level":level,
                   "cards_needed":cards_needed,"defeated":False,"can_catch":False}
        self.raid_timer=60*60
        add_particles(self.ARENA_RECT.centerx,self.ARENA_RECT.centery,(255,200,50),n=50)
        notify(f"⚔ RAID erschienen! {boss.name} in der Arena! ({cards_needed} Lernkarten nötig)",C_YELLOW,300)
        self._raid_spawn_timer=random.randint(3600,10800)

    def handle_event(self, event): pass

    def update(self, keys):
        dx,dy=0.0,0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx-=self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx+=self.speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy-=self.speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy+=self.speed
        if dx or dy:
            norm=math.sqrt(dx*dx+dy*dy); dx,dy=dx/norm*self.speed,dy/norm*self.speed
            self.player_x=max(20,min(SW-40,self.player_x+dx))
            self.player_y=max(160,min(SH-80,self.player_y+dy))
            self.step_anim+=1; self.save["step_count"]=self.save.get("step_count",0)+1
            if self.save["step_count"]%100==0 and hasattr(self,'_ach_cb') and self._ach_cb:
                self._ach_cb()
        self._update_trainers(); self._update_raid(); self._update_weather()
        pr=pygame.Rect(int(self.player_x)-12,int(self.player_y)-20,24,40)
        self.in_grass=any(g.colliderect(pr) for g in self.GRASS_RECTS)
        if self.in_grass:
            self.grass_particle_t+=1
            if self.encounter_timer>0: self.encounter_timer-=1
            elif (dx or dy) and random.random()<0.008:
                self.encounter_timer=120; return "wild_encounter"
        if self.center_cooldown>0: self.center_cooldown-=1
        if self.blackmarket_cooldown>0: self.blackmarket_cooldown-=1
        if self.daily_cooldown>0: self.daily_cooldown-=1
        enter_pressed=keys[pygame.K_RETURN] or keys[pygame.K_z]
        b = self._buildings
        if "shop" in b and self.center_cooldown==0 and pr.colliderect(self.SHOP_RECT):
            self.pending_action="shop"
            if enter_pressed: return "shop"
        elif "center" in b and self.center_cooldown==0 and pr.colliderect(self.CENTER_RECT):
            self.pending_action="center"
            if enter_pressed: return "center"
        elif "arena" in b and pr.colliderect(self.ARENA_RECT):
            self.pending_action="arena"
            if enter_pressed and self.raid:
                if self.raid.get("can_catch") and not self.raid.get("catch_used"):
                    return "raid_catch"
                elif not self.raid.get("defeated"):
                    has_normal=self.save.get("raid_passes",0)>0
                    has_premium=self.save.get("premium_raid_passes",0)>0
                    if not has_normal and not has_premium:
                        notify("Du brauchst einen Raid-Pass! 🎫 Im Shop kaufen.",C_RED,200)
                    else: return "raid_pass_select"
        elif "blackmarket" in b and self.blackmarket_cooldown==0 and pr.colliderect(self.SKULL_RECT):
            self.pending_action="blackmarket"
            if enter_pressed: return "blackmarket"
        elif "daily" in b and self.daily_cooldown==0 and pr.colliderect(self.DAILY_RECT):
            self.pending_action="daily"
            if enter_pressed:
                today = _today_str()
                if self.save.get("daily_event_date","") == today:
                    notify("Du hast das heutige Event bereits gespielt! Komm morgen wieder.", C_GRAY, 180)
                else:
                    return "daily_event"
        elif "guild" in b and pr.colliderect(self.DAILY_RECT):
            self.pending_action="guild_building"
            if enter_pressed: return "guild_from_map"
        elif pr.colliderect(self.PC_RECT):  # pc always available
            self.pending_action="pc"
        else: self.pending_action=None
        for k in list(self.trainer_cooldown.keys()):
            self.trainer_cooldown[k]-=1
            if self.trainer_cooldown[k]<=0: del self.trainer_cooldown[k]
        for i,t in enumerate(self._trainers):
            if i in self.trainer_cooldown: continue
            tr=pygame.Rect(int(t["x"])-28,int(t["y"])-28,56,56)
            if pr.colliderect(tr):
                self.trainer_cooldown[i]=300; return f"trainer_{i}"
        return self.pending_action

    def draw(self, surf):
        md = self.map_def
        tint = md["grass_tint"]
        bg   = md["bg"]
        grid = md["grid"]
        pcol = md["particle"]
        b    = self._buildings

        surf.fill(bg)
        for gx in range(0,SW,40): pygame.draw.line(surf,grid,(gx,54),(gx,SH))
        for gy in range(54,SH,40): pygame.draw.line(surf,grid,(0,gy),(SW,gy))

        # Ambient color overlay
        if md["ambient"]:
            r,g2,b2,a = md["ambient"]
            amb = pygame.Surface((SW,SH),pygame.SRCALPHA)
            amb.fill((r,g2,b2,a))
            surf.blit(amb,(0,0))

        # Day/Night overlay
        phase, phase_label, dn_rgba = get_time_of_day()
        apply_day_night_overlay(surf, phase, dn_rgba)
        day_night_star_overlay(surf, phase)

        # Tinted grass
        grass_img = load_img_tinted("assets/grass.png",(40,40), tint)
        for g in self.GRASS_RECTS:
            for gx in range(g.left,g.right,40):
                for gy in range(g.top,g.bottom,40):
                    surf.blit(grass_img,(gx,gy))
            if self.in_grass and self.grass_particle_t%20==0:
                add_particles(g.centerx,g.centery,pcol,n=3,size=4)

        # Buildings — only draw if present on this map
        if "shop" in b:
            shop_img=load_img("assets/shop.png",(130,85)); surf.blit(shop_img,(self.SHOP_RECT.x,self.SHOP_RECT.y))
            draw_text(surf,"Shop",F_TINY,C_YELLOW,self.SHOP_RECT.centerx,self.SHOP_RECT.bottom+3,center=True,shadow=True)
        if "center" in b:
            center_img=load_img("assets/center.png",(130,85)); surf.blit(center_img,(self.CENTER_RECT.x,self.CENTER_RECT.y))
            draw_text(surf,"Pokecenter",F_TINY,(255,180,220),self.CENTER_RECT.centerx,self.CENTER_RECT.bottom+3,center=True,shadow=True)
        if "arena" in b:
            arena_img=load_img("assets/arena.png",(130,85))
            if self.raid:
                pulse=abs(math.sin(pygame.time.get_ticks()*0.003))
                glow_col=(80,255,120) if self.raid.get("can_catch") else (255,int(150+100*pulse),0)
                glow=pygame.Surface((self.ARENA_RECT.width+20,self.ARENA_RECT.height+20),pygame.SRCALPHA)
                pygame.draw.rect(glow,(*glow_col,int(60+80*pulse)),(0,0,self.ARENA_RECT.width+20,self.ARENA_RECT.height+20),border_radius=12)
                surf.blit(glow,(self.ARENA_RECT.x-10,self.ARENA_RECT.y-10))
            surf.blit(arena_img,(self.ARENA_RECT.x,self.ARENA_RECT.y))
            if self.raid:
                secs=max(0,self.raid_timer)//60
                if self.raid.get("can_catch"):
                    draw_text(surf,f"⚡ {self.raid['name']}",F_TINY,C_GREEN,self.ARENA_RECT.centerx,self.ARENA_RECT.bottom+3,center=True,shadow=True)
                    draw_text(surf,"Fangen bereit!",F_TINY,C_GREEN,self.ARENA_RECT.centerx,self.ARENA_RECT.bottom+14,center=True)
                else:
                    draw_text(surf,f"⚡ RAID: {self.raid['name']}",F_TINY,C_YELLOW,self.ARENA_RECT.centerx,self.ARENA_RECT.bottom+3,center=True,shadow=True)
                    timer_col=C_RED if secs<15 else C_YELLOW
                    draw_text(surf,f"{secs}s",F_TINY,timer_col,self.ARENA_RECT.centerx,self.ARENA_RECT.bottom+14,center=True)
            else:
                draw_text(surf,"Arena",F_TINY,C_GRAY,self.ARENA_RECT.centerx,self.ARENA_RECT.bottom+3,center=True)
        if "blackmarket" in b:
            skull_img=load_img("assets/skull.png",(self.SKULL_RECT.width,self.SKULL_RECT.height))
            surf.blit(skull_img,(self.SKULL_RECT.x,self.SKULL_RECT.y))
            draw_text(surf,"💀 Schwarzmarkt",F_TINY,(180,50,220),self.SKULL_RECT.centerx,self.SKULL_RECT.bottom+3,center=True,shadow=True)
        # PC always visible
        bw=120
        draw_rounded_rect(surf,(30,50,90),(self.PC_RECT.x,self.PC_RECT.y,bw,self.PC_RECT.height),10,2,C_BLUE)
        draw_text(surf,"Pokédex",F_TINY,C_BLUE,self.PC_RECT.x+bw//2,self.PC_RECT.centery-7,center=True)
        draw_text(surf,"[ B ]",F_TINY,C_GRAY,self.PC_RECT.x+bw//2,self.PC_RECT.centery+9,center=True)
        draw_rounded_rect(surf,(30,80,60),(self.PC_RECT.x+bw+6,self.PC_RECT.y,bw,self.PC_RECT.height),10,2,C_GREEN)
        draw_text(surf,"PC-Box",F_TINY,C_GREEN,self.PC_RECT.x+bw+6+bw//2,self.PC_RECT.centery-7,center=True)
        draw_text(surf,"[ P ]",F_TINY,C_GRAY,self.PC_RECT.x+bw+6+bw//2,self.PC_RECT.centery+9,center=True)
        pr=pygame.Rect(int(self.player_x)-12,int(self.player_y)-20,24,40)
        # Daily event or Guild building (share the DAILY_RECT slot)
        pulse_d = abs(math.sin(pygame.time.get_ticks()*0.003))
        if "daily" in b:
            today_done = self.save.get("daily_event_date","") == _today_str()
            daily_col  = (80,80,90) if today_done else (255,200,50)
            daily_bg2  = (20,22,30) if today_done else (35,30,10)
            draw_rounded_rect(surf,daily_bg2,(self.DAILY_RECT.x,self.DAILY_RECT.y,self.DAILY_RECT.width,self.DAILY_RECT.height),10,2,daily_col)
            if not today_done:
                glow_d = pygame.Surface((self.DAILY_RECT.width+16,self.DAILY_RECT.height+16),pygame.SRCALPHA)
                pygame.draw.rect(glow_d,(255,220,50,int(40+40*pulse_d)),(0,0,self.DAILY_RECT.width+16,self.DAILY_RECT.height+16),border_radius=14)
                surf.blit(glow_d,(self.DAILY_RECT.x-8,self.DAILY_RECT.y-8))
            draw_text(surf,"❓",F_BIG,daily_col,self.DAILY_RECT.centerx,self.DAILY_RECT.centery-16,center=True)
            draw_text(surf,"Tages-Event" if not today_done else "✓ Erledigt",F_TINY,daily_col,self.DAILY_RECT.centerx,self.DAILY_RECT.bottom+3,center=True,shadow=True)
            if pr.colliderect(self.DAILY_RECT):
                draw_text(surf,"Bereits gespielt! Komm morgen." if today_done else "[ ENTER ] Wer ist das Pokémon?",
                          F_SMALL,C_GRAY if today_done else C_YELLOW,self.DAILY_RECT.centerx,self.DAILY_RECT.bottom+18,center=True,shadow=not today_done)
        elif "guild" in b:
            draw_rounded_rect(surf,(20,30,55),(self.DAILY_RECT.x,self.DAILY_RECT.y,self.DAILY_RECT.width,self.DAILY_RECT.height),10,2,C_ORANGE)
            glow_g = pygame.Surface((self.DAILY_RECT.width+16,self.DAILY_RECT.height+16),pygame.SRCALPHA)
            pygame.draw.rect(glow_g,(*C_ORANGE,int(30+30*pulse_d)),(0,0,self.DAILY_RECT.width+16,self.DAILY_RECT.height+16),border_radius=14)
            surf.blit(glow_g,(self.DAILY_RECT.x-8,self.DAILY_RECT.y-8))
            draw_text(surf,"⚔",F_BIG,C_ORANGE,self.DAILY_RECT.centerx,self.DAILY_RECT.centery-16,center=True)
            draw_text(surf,"Gilde",F_TINY,C_ORANGE,self.DAILY_RECT.centerx,self.DAILY_RECT.bottom+3,center=True,shadow=True)
            if pr.colliderect(self.DAILY_RECT):
                draw_text(surf,"[ ENTER ] Gilde betreten",F_SMALL,C_ORANGE,self.DAILY_RECT.centerx,self.DAILY_RECT.bottom+18,center=True,shadow=True)
        if "shop" in b and pr.colliderect(self.SHOP_RECT):
            draw_text(surf,"[ ENTER ] Shop betreten",F_SMALL,C_YELLOW,self.SHOP_RECT.centerx,self.SHOP_RECT.bottom+18,center=True,shadow=True)
        if "center" in b and pr.colliderect(self.CENTER_RECT):
            draw_text(surf,"[ ENTER ] Pokecenter",F_SMALL,(255,220,240),self.CENTER_RECT.centerx,self.CENTER_RECT.bottom+18,center=True,shadow=True)
        if "blackmarket" in b and pr.colliderect(self.SKULL_RECT):
            draw_text(surf,"[ ENTER ] Schwarzmarkt",F_SMALL,(200,80,255),self.SKULL_RECT.centerx,self.SKULL_RECT.bottom+18,center=True,shadow=True)
        if "arena" in b and pr.colliderect(self.ARENA_RECT):
            if self.raid and self.raid.get("can_catch") and not self.raid.get("catch_used"):
                draw_text(surf,"[ ENTER ] Raid-Pokémon fangen!",F_SMALL,C_GREEN,self.ARENA_RECT.centerx,self.ARENA_RECT.bottom+18,center=True,shadow=True)
            elif self.raid and not self.raid.get("defeated"):
                has_pass=self.save.get("raid_passes",0)>0 or self.save.get("premium_raid_passes",0)>0
                col=C_YELLOW if has_pass else C_RED
                label="[ ENTER ] Raid starten! 🎫" if has_pass else "Kein Raid-Pass! Im Shop kaufen."
                draw_text(surf,label,F_SMALL,col,self.ARENA_RECT.centerx,self.ARENA_RECT.bottom+18,center=True,shadow=True)
                rp=self.save.get("raid_passes",0); prp=self.save.get("premium_raid_passes",0)
                draw_text(surf,f"Pass: {rp}  Premium: {prp}",F_TINY,C_GRAY,self.ARENA_RECT.centerx,self.ARENA_RECT.bottom+34,center=True)
            elif self.raid and self.raid.get("catch_used"):
                draw_text(surf,"Raid abgeschlossen",F_SMALL,C_GRAY,self.ARENA_RECT.centerx,self.ARENA_RECT.bottom+18,center=True)
            else:
                draw_text(surf,"Kein aktiver Raid",F_SMALL,C_GRAY,self.ARENA_RECT.centerx,self.ARENA_RECT.bottom+18,center=True)
        # Weather effects — drawn above world, below characters
        self._draw_weather(surf)

        for t in self._trainers:
            en=t["enemy"]; img=load_img(en.image,(38,50))
            surf.blit(img,(int(t["x"])-19,int(t["y"])-25))
            is_rocket=getattr(en,"isRocket",False)
            badge_col=C_ROCKET if is_rocket else C_ORANGE
            pygame.draw.circle(surf,badge_col,(int(t["x"]),int(t["y"])-30),5)
            draw_text(surf,en.name[:8],F_TINY,C_WHITE,int(t["x"]),int(t["y"])+28,center=True,shadow=True)
            if is_rocket: draw_text(surf,"R",F_TINY,C_ROCKET,int(t["x"])+14,int(t["y"])-30)
        bob=math.sin(self.step_anim*0.3)*3
        trainer=self.get_trainer_img()
        surf.blit(trainer,(int(self.player_x)-24,int(self.player_y)-32+int(bob)))
        pygame.draw.ellipse(surf,(0,0,0,80),pygame.Rect(int(self.player_x)-18,int(self.player_y)+24,36,10))
        # ── HUD Row 1: Stats (height 28) ──
        draw_rounded_rect(surf,(15,18,28),(0,0,SW,28),0,1,(50,55,70))
        hud_stats=[
            (f"🎯 {self.save.get('balls',0)} Bälle",      C_GREEN),
            (f"💊 {self.save.get('potions',0)} Tränke",   (180,230,180)),
            (f"⚡ {self.save.get('super_potions',0)} S-Tr.",(140,200,255)),
            (f"💰 {self.save.get('coins',0)} Coins",      C_YELLOW),
            (f"🏅 {self.save.get('badges',0)} Badges",    C_ORANGE),
        ]
        if self.save.get("entwicklungsstein",0)>0:
            hud_stats.append((f"💎 ×{self.save.get('entwicklungsstein',0)}",C_STEIN))
        hx=6
        for txt,col in hud_stats:
            draw_text(surf,txt,F_TINY,col,hx,7); hx+=F_TINY.size(txt)[0]+14
        # Rang
        rp = self.save.get("rank_points",0)
        _, rname, rcol, _ = get_rank_info(rp)
        cur_mk   = self.save.get("current_map","Normal")
        cur_mico = MAP_DEFS.get(cur_mk,{}).get("icon","")
        draw_text(surf,f"🏆 {rname} {rp}RP  {cur_mico} {cur_mk}",F_TINY,rcol,SW-360,7)
        # Wetter (per-map) + Tageszeit
        w_data = get_map_weather(cur_mk, self.save)
        phase_now, _, _ = get_time_of_day()
        dn_ico = day_night_icon(phase_now)
        draw_text(surf,f"{dn_ico} {w_data['icon']} {w_data['name']}",F_TINY,w_data["color"],SW-110,7)

        # ── HUD Row 2: Shortcut Buttons (height 26, at y=28) ──
        draw_rounded_rect(surf,(10,12,22),(0,28,SW,26),0,1,(35,40,55))
        btns=[
            ("[B] Pokédex",   C_BLUE),
            ("[P] PC-Box",    C_GREEN),
            ("[T] Team",      C_ORANGE),
            ("[I] Items",     (180,200,140)),
            ("[A] Achiev.",   C_PURPLE),
            ("[C] Karten",    (200,160,80)),
            ("[K] Schwarzm.", (180,50,220)),
            ("[G] Gilde",     C_ORANGE),
            ("[E] Prüfung",   C_BLUE),
            ("[O] Settings",  C_GRAY),
            ("[R] Reisen",    C_YELLOW),
            ("[V] Editor",    (140,80,180)),
        ]
        bx=4
        for label,bcol in btns:
            bw=F_TINY.size(label)[0]+10
            draw_rounded_rect(surf,(*bcol,30),(bx,30,bw,20),5,1,bcol)
            draw_text(surf,label,F_TINY,C_WHITE,bx+bw//2,32,center=True)
            bx+=bw+4
        if self.raid:
            secs=max(0,self.raid_timer)//60
            rx,ry,rw,rh=8,SH-78,290,68
            bg_c=(20,50,20) if self.raid.get("can_catch") else (50,25,10)
            draw_rounded_rect(surf,bg_c,(rx,ry,rw,rh),10,2,C_YELLOW)
            draw_text(surf,f"⚔ RAID: {self.raid['name']}  Lv{self.raid.get('level','?')}",F_SMALL,C_YELLOW,rx+8,ry+6,shadow=True)
            if self.raid.get("can_catch"):
                draw_text(surf,"✓ Gewonnen! Geh zur Arena zum Fangen",F_TINY,C_GREEN,rx+8,ry+28)
            else:
                cards_n=self.raid.get("cards_needed",0); cards_a=self.raid.get("cards_answered",0)
                timer_c=C_RED if secs<15 else (255,200,50)
                draw_text(surf,f"⏱ {secs}s   📚 Lernkarten: {cards_a}/{cards_n}",F_TINY,timer_c,rx+8,ry+28)
                bar_w2=rw-16; pct=min(1.0,cards_a/max(1,cards_n))
                pygame.draw.rect(surf,(40,40,60),(rx+8,ry+46,bar_w2,10),border_radius=5)
                if pct>0: pygame.draw.rect(surf,C_BLUE,(rx+8,ry+46,int(bar_w2*pct),10),border_radius=5)
        update_particles(surf)
        draw_notifications(surf)

# ── Character select / new game ────────────────────────────────────────────────
class CharSelectScreen:
    STARTERS = ["Bisasam", "Glumanda", "Schiggy"]

    def __init__(self):
        self.trainer_sel = 0
        self.starter_sel = 0
        self.name = "Spieler"
        self.state = "pick"

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        if self.state == "pick":
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.trainer_sel = 1 - self.trainer_sel
            elif event.key == pygame.K_RETURN:
                self.state = "name"
        elif self.state == "name":
            if event.key == pygame.K_RETURN:
                if self.name.strip():
                    self.state = "starter"
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.state = "pick"
            elif len(self.name) < 12:
                self.name += event.unicode
        elif self.state == "starter":
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.starter_sel = (self.starter_sel - 1) % len(self.STARTERS)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.starter_sel = (self.starter_sel + 1) % len(self.STARTERS)
            elif event.key == pygame.K_RETURN:
                self.state = "ready"
            elif event.key == pygame.K_ESCAPE:
                self.state = "name"
        elif self.state == "ready":
            if event.key == pygame.K_RETURN:
                return "start"
            elif event.key == pygame.K_ESCAPE:
                self.state = "starter"
        return None

    def draw(self, surf):
        surf.fill(C_BG)
        draw_text(surf, "MoonieQuest", F_HUGE, C_YELLOW, SW//2, 24, center=True, shadow=True)
        draw_text(surf, "AP2 Edition", F_BIG, C_BLUE, SW//2, 84, center=True)
        if self.state == "pick":
            draw_text(surf, "Wähle deinen Trainer:", F_MED, C_WHITE, SW//2, 148, center=True)
            for i in range(2):
                tx = SW//2 - 130 + i*260; ty = 200; sel = (i == self.trainer_sel)
                draw_rounded_rect(surf, C_PANEL2 if not sel else (40,60,120), (tx-70,ty,140,220), 16, 3 if sel else 1, C_YELLOW if sel else C_GRAY)
                img = load_img(f"assets/trainer{'' if i==0 else '2'}.png", (110,160))
                surf.blit(img, (tx-55, ty+10))
                draw_text(surf, f"Trainer {i+1}", F_MED, C_WHITE, tx, ty+178, center=True)
            draw_text(surf, "◄ ►  wählen    ENTER  weiter", F_SMALL, C_GRAY, SW//2, 455, center=True)
        elif self.state == "name":
            draw_text(surf, "Wie ist dein Name?", F_BIG, C_WHITE, SW//2, 200, center=True)
            draw_rounded_rect(surf, C_DARK, (SW//2-160,268,320,52), 10, 2, C_BLUE)
            cursor = "|" if int(time.time()*2)%2==0 else " "
            draw_text(surf, self.name + cursor, F_BIG, C_YELLOW, SW//2, 281, center=True)
            draw_text(surf, "ENTER bestätigen   ESC zurück", F_SMALL, C_GRAY, SW//2, 358, center=True)
        elif self.state == "starter":
            draw_text(surf, "Wähle dein Starter-Pokémon!", F_BIG, C_WHITE, SW//2, 120, center=True, shadow=True)
            draw_text(surf, "◄ ► wählen   ENTER bestätigen", F_SMALL, C_GRAY, SW//2, 156, center=True)
            for i, name in enumerate(self.STARTERS):
                m = ALL_MOONIES_DICT.get(name)
                if not m: continue
                tx = SW//2 - 260 + i*260; ty = 185; sel = (i == self.starter_sel)
                bg = (40,70,120) if sel else C_PANEL
                draw_rounded_rect(surf, bg, (tx-100,ty,200,280), 16, 3 if sel else 1, C_YELLOW if sel else C_GRAY)
                img = load_img(m.image, (130,130)); surf.blit(img, (tx-65, ty+12))
                r_col = m.get_rarity_color()
                pygame.draw.rect(surf, r_col, (tx-100,ty,200,8), border_radius=16)
                draw_text(surf, name, F_MED, C_WHITE, tx, ty+152, center=True, shadow=True)
                tw = len(m.types)*70; bx = tx-tw//2
                for t in m.types:
                    draw_type_badge(surf, t, bx, ty+178); bx += 70
                draw_text(surf, f"HP: {m.max_hp}  Ang: {m.attack}", F_TINY, C_GRAY, tx, ty+204, center=True)
                if m.nextEvolution:
                    evo = m.nextEvolution if isinstance(m.nextEvolution,str) else "?"
                    draw_text(surf, f"→ {evo}", F_TINY, C_BLUE, tx, ty+222, center=True)
        elif self.state == "ready":
            name = self.STARTERS[self.starter_sel]; m = ALL_MOONIES_DICT.get(name)
            if m:
                img = load_img(m.image, (160,160)); surf.blit(img, (SW//2-80, 160))
            draw_text(surf, f"Du hast {name} gewählt!", F_BIG, C_YELLOW, SW//2, 340, center=True, shadow=True)
            draw_text(surf, f"Viel Erfolg, {self.name}!", F_MED, C_WHITE, SW//2, 385, center=True)
            draw_text(surf, "ENTER  Abenteuer beginnen!", F_MED, C_GREEN, SW//2, 435, center=True)
            draw_text(surf, "ESC  zurück", F_TINY, C_GRAY, SW//2, 475, center=True)
        draw_notifications(surf)

# ── Title screen ───────────────────────────────────────────────────────────────
class TitleScreen:
    def __init__(self, has_save):
        self.has_save = has_save; self.t = 0
        self.options = ["Neues Spiel","Spiel laden","Beenden"] if has_save else ["Neues Spiel","Beenden"]
        self.sel = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: self.sel = (self.sel-1) % len(self.options)
            elif event.key == pygame.K_DOWN: self.sel = (self.sel+1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_z): return self.options[self.sel]
        return None

    def draw(self, surf):
        self.t += 1; surf.fill(C_BG)
        for i in range(30):
            r = random.Random(i+1000); px2=r.randint(0,SW); py2=r.randint(0,SH); size=r.randint(2,6)
            alpha=int(128+60*math.sin(self.t*0.03+r.random()*6.28))
            s=pygame.Surface((size*2,size*2),pygame.SRCALPHA)
            pygame.draw.circle(s,(200,200,255,alpha),(size,size),size); surf.blit(s,(px2,py2))
        logo_y = 80 + math.sin(self.t*0.04)*8
        draw_text(surf,"MoonieQuest",F_HUGE,C_YELLOW,SW//2,logo_y,center=True,shadow=True)
        draw_text(surf,"AP2 Edition",F_BIG,C_BLUE,SW//2,logo_y+70,center=True)
        showcase=["glumanda","bisasam","schiggy","evoli","pikachu"]
        for i,name in enumerate(showcase):
            img=load_img(f"assets/moonie/{name}.png",(80,80))
            sx=SW//2-len(showcase)*50+i*100; sy=230+math.sin(self.t*0.05+i)*12
            surf.blit(img,(sx-40,sy))
        for i,opt in enumerate(self.options):
            sel=(i==self.sel); col=C_YELLOW if sel else C_WHITE; by=380+i*62; bw=300
            draw_rounded_rect(surf,C_PANEL if not sel else (40,60,120),(SW//2-bw//2,by,bw,50),14,2 if sel else 1,C_YELLOW if sel else C_GRAY)
            draw_text(surf,("► " if sel else "  ")+opt,F_BIG,col,SW//2,by+9,center=True,shadow=True)
        draw_text(surf,"↑↓  ENTER",F_SMALL,C_GRAY,SW//2,SH-30,center=True)
        draw_notifications(surf)

# ── Main game manager ──────────────────────────────────────────────────────────
# Evoli evolution names — dynamically read from ALL_MOONIES_DICT at runtime
def get_eevee_evolutions():
    """Return the set of all Evoli evolutions as defined in the Moonie registry."""
    evoli = ALL_MOONIES_DICT.get("Evoli")
    if not evoli:
        return set()
    nxt = getattr(evoli, "nextEvolution", None)
    if isinstance(nxt, list):
        return set(nxt)
    if isinstance(nxt, str):
        return {nxt}
    return set()

_eevee_cache = None

def _eevee_set():
    """Return (and lazily cache) the Eeveelution set."""
    global _eevee_cache
    if _eevee_cache is None:
        _eevee_cache = get_eevee_evolutions()
    return _eevee_cache

class GameManager:
    def __init__(self):
        self.flashcards = load_flashcards(os.path.join(BASE, "flashcards.csv"))
        self.card_editor = None
        random.shuffle(self.flashcards)
        self.save = None; self.team = []
        self.screen_state = "title"
        self.title_screen = TitleScreen(os.path.exists(SAVE_FILE))
        self.char_select = None; self.overworld = None; self.battle = None
        self.shop = None; self.pokedex = None; self.center = None
        self.team_screen = None; self.item_bag = None; self.evo_screen = None
        self.pc_box_screen = None; self.ach_screen = None
        self.card_album_screen = None; self.blackmarket_screen = None
        self.raid_pass_screen = None; self.prev_state = None
        # Stein screens
        self.stein_mon_screen = None
        self.stein_evo_screen = None
        # Daily event + raid catch quiz
        self.daily_quiz_screen  = None
        # New feature screens
        self.guild_screen    = None
        self.exam_screen     = None
        self.settings_screen = None
        self.travel_screen   = None

    def _trigger_achievements(self):
        newly = ach_module.check_achievements(self.save, self.flashcards, ALL_MOONIES_DICT)
        for aid, tier_label, title, reward, icon in newly:
            msg = f"{icon} Achievement: {title} – {tier_label}!"
            if reward > 0: msg += f"  +{reward} Coins"
            notify(msg, C_YELLOW, 300)

    def start_new_game(self, save_data):
        self.save = save_data
        starter_name = save_data.get("starter","Bisasam")
        starter = get_moonie(starter_name)
        self.team = [starter]; self.save["team"] = [starter_name]
        pc = self.save.get("pc_box",[])
        if starter_name not in pc: pc.append(starter_name)
        self.save["pc_box"] = pc
        cur_map = self.save.get("current_map", "Normal")
        self.overworld = OverworldScreen(self.save, self.flashcards, cur_map)
        self.overworld._ach_cb = self._trigger_achievements
        self.screen_state = "overworld"
        FlashcardGame._save_ref = self.save
        notify(f"Willkommen, {self.save['name']}! Viel Erfolg mit {starter_name}!", C_YELLOW, 180)

    def load_existing_game(self):
        self.save = load_game()
        if self.save is None: self.save = default_save()
        raw_team = self.save.get("team", ["Bisasam", "Glumanda", "Schiggy"])
        # Support both old format (list of names) and new format (list of dicts)
        self.team = [
            moonie_from_dict(e) if isinstance(e, dict) else get_moonie(e)
            for e in raw_team
        ]
        if not self.team: self.team = [get_moonie("Bisasam")]
        self.overworld = OverworldScreen(self.save, self.flashcards)
        self.overworld._ach_cb = self._trigger_achievements
        self.screen_state = "overworld"
        FlashcardGame._save_ref = self.save
        # Initialise daily systems
        weather = get_today_weather(self.save)
        get_today_challenges(self.save)
        save_game(self.save)
        notify(f"Spiel geladen! Wetter heute: {weather['icon']} {weather['name']}", C_GREEN, 200)

    def start_wild_battle(self):
        step = self.save.get("step_count",0)
        rarity = "common" if step<500 else "uncommon" if step<2000 else "rare"
        pool = get_wild_pool([rarity])
        # Filter by map spawn types
        cur_map = self.save.get("current_map","Normal")
        md = MAP_DEFS.get(cur_map, MAP_DEFS["Normal"])
        spawn_types = md.get("spawn_types")
        if spawn_types:
            typed_pool = [m for m in pool if any(t in m.types for t in spawn_types)]
            if typed_pool: pool = typed_pool
        # Time-of-day spawn modifier
        phase_w, _, _ = get_time_of_day()
        if phase_w in ("night", "evening"):
            # Ghost/Dark/Psychic more common at night
            bonus_types = {"Geist", "Dunkel", "Psycho"}
            bonus_pool = [m for m in pool if any(t in m.types for t in bonus_types)]
            if bonus_pool: pool = pool + bonus_pool * 2
        elif phase_w in ("dawn", "morning"):
            # Flying/Normal more common in the morning
            bonus_types = {"Flug", "Normal", "Fee"}
            bonus_pool = [m for m in pool if any(t in m.types for t in bonus_types)]
            if bonus_pool: pool = pool + bonus_pool
        elif phase_w in ("day", "afternoon"):
            # Fire/Grass/Bug more common midday
            bonus_types = {"Feuer", "Pflanze", "Käfer"}
            bonus_pool = [m for m in pool if any(t in m.types for t in bonus_types)]
            if bonus_pool: pool = pool + bonus_pool
        # Apply map weather modifier
        weather = get_map_weather(cur_map, self.save)
        pool = weather_modified_pool(pool, weather)
        wild = random.choice(pool).clone_for_battle()
        wild.level = max(1, min(50, step//40 + random.randint(1,5)))
        wild.max_hp = wild.max_hp + wild.level*2; wild.current_hp = wild.max_hp
        # Mark as seen in pokédex
        seen = self.save.setdefault("dex_seen", [])
        if wild.name not in seen:
            seen.append(wild.name)
            self.save["dex_seen"] = seen
        self.battle = Battle(self.team, None, wild_moonie=wild, flashcards=self.flashcards, is_wild=True)
        self.battle.save_data_ref = self.save; self.screen_state = "battle"

    def start_trainer_battle(self, trainer_idx):
        if not self.overworld or trainer_idx >= len(self.overworld._trainers): return
        t = self.overworld._trainers[trainer_idx]; en = t["enemy"]
        if getattr(en,"isRocket",False):
            import copy; en = copy.copy(en); en.strenght = getattr(en,'strenght',2)+2
        self.battle = Battle(self.team, en, flashcards=self.flashcards, is_wild=False)
        self.battle.save_data_ref = self.save; self.battle._trainer_idx = trainer_idx
        self.screen_state = "battle"
        t["vx"]=random.choice([-1,1])*2.5; t["vy"]=random.choice([-1,1])*2.5; t["move_dir_t"]=180

    def start_raid_battle(self, premium=False):
        if not self.overworld or not self.overworld.raid: return
        raid = self.overworld.raid; m = ALL_MOONIES_DICT.get(raid["name"])
        if not m: return
        boss = m.clone_for_battle(); boss.level = raid["level"]
        boss.max_hp = boss.max_hp + boss.level*3; boss.attack = boss.attack + boss.level
        if premium: boss.max_hp = max(10, boss.max_hp//2); raid["_premium_bonus"]=True
        boss.current_hp = boss.max_hp
        cards_needed = max(1, raid["cards_needed"] - (2 if premium else 0))
        self.battle = Battle(self.team, None, wild_moonie=boss, flashcards=self.flashcards, is_wild=True)
        self.battle.save_data_ref = self.save; self.battle.raid_cards_needed = cards_needed
        self.battle.raid_cards_answered = 0; self.battle._is_raid = True
        self.battle._raid_attack_count = 0; self.battle.overworld_ref = self.overworld
        self.screen_state = "battle"
        notify(f"⚔ RAID gegen {boss.name} Lv{boss.level}! {cards_needed} Lernkarten nötig!{'(Premium!)' if premium else ''}", C_YELLOW, 260)

    def start_raid_catch(self):
        if not self.overworld or not self.overworld.raid: return
        raid = self.overworld.raid
        if not raid.get("can_catch") or raid.get("catch_used"): return
        m = ALL_MOONIES_DICT.get(raid["name"])
        if not m: return
        boss = m.clone_for_battle(); boss.level = raid["level"]
        boss.max_hp = 1; boss.current_hp = 1; boss.catch_rate = 0.5
        # Passiver Fangmodus — Raid-Boss greift nicht an
        self.battle = PassiveCatchBattle(self.team, boss, self.flashcards)
        self.battle.save_data_ref = self.save; self.battle._is_raid_catch = True
        self.overworld.raid["catch_used"] = True; self.screen_state = "battle"
        notify(f"Fangversuch: {boss.name}! (greift nicht an)", C_GREEN, 180)

    # ── Entwicklungsstein-Logik ───────────────────────────────────────────────
    def open_stein_picker(self):
        """Open the Pokémon-picker for the Entwicklungsstein."""
        self.stein_mon_screen = SteinMonPickScreen(self.team, self.save)
        self.screen_state = "stein_mon"

    def apply_stein_to(self, moonie_obj):
        """Given a Moonie that received the stone, show evo choice or evolve directly."""
        if not moonie_obj.evolve or not moonie_obj.nextEvolution:
            notify(f"{moonie_obj.name} kann sich nicht entwickeln!", C_RED, 180)
            self.screen_state = "overworld"
            return
        evo = moonie_obj.nextEvolution
        choices = evo if isinstance(evo, list) else [evo]
        choices = [c for c in choices if c in ALL_MOONIES_DICT]
        if not choices:
            notify(f"Entwicklung nicht gefunden!", C_RED, 180); self.screen_state = "overworld"; return
        self.save["entwicklungsstein"] = max(0, self.save.get("entwicklungsstein",0)-1)
        self.save["stein_used_count"] = self.save.get("stein_used_count",0)+1
        if len(choices) == 1:
            self._do_stein_evolution(moonie_obj, choices[0])
        else:
            self.stein_evo_screen = SteinEvoSelectScreen(moonie_obj, self.save, self.team)
            self.screen_state = "stein_evo"

    def _do_stein_evolution(self, moonie_obj, evo_name):
        """Actually evolve a moonie to evo_name via stone."""
        old_name = moonie_obj.name
        new_m = get_moonie(evo_name)
        new_m.level = moonie_obj.level; new_m.xp = moonie_obj.xp
        new_m.max_hp = max(new_m.max_hp, moonie_obj.max_hp+10)
        new_m.attack = max(new_m.attack, moonie_obj.attack+5)
        new_m.current_hp = new_m.max_hp
        idx = self.team.index(moonie_obj)
        self.team[idx] = new_m
        self.save["evolution_count"] = self.save.get("evolution_count",0)+1
        # Track Eeveelution achievement
        if evo_name in _eevee_set():
            s = self.save.setdefault("eevee_evolutions_no_stein", [])
            # Stone evolution does NOT count for the achievement — only non-stone does
        # Add to PC box so it shows in Pokédex
        pc = self.save.get("pc_box",[]); 
        if evo_name not in pc: pc.append(evo_name)
        self.save["pc_box"] = pc
        self.save["team"] = [moonie_to_dict(m) for m in self.team]
        save_game(self.save)
        self._trigger_achievements()
        self.evo_screen = EvolutionScreen(old_name, evo_name, self.team)
        self.screen_state = "evolution"

    def _travel_to(self, map_key):
        """Switch to a different map world."""
        if map_key not in MAP_DEFS:
            return
        self.save["current_map"] = map_key
        # Initialize weather for the new map
        w = get_map_weather(map_key, self.save)
        # Rebuild overworld with new map
        self.overworld = OverworldScreen(self.save, self.flashcards, map_key)
        self.overworld._ach_cb = self._trigger_achievements
        self.screen_state = "overworld"
        self.travel_screen = None
        md = MAP_DEFS[map_key]
        notify(f"{md['icon']} Willkommen in der {md['name']}!  Wetter: {w['icon']} {w['name']}", C_YELLOW, 260)
        save_game(self.save)

    def end_battle(self):
        result = self.battle.result
        is_trainer = not self.battle.is_wild
        is_rocket  = is_trainer and getattr(self.battle.enemy_data,'isRocket',False)

        if result == "win":
            self.save["battles_won"] = self.save.get("battles_won",0)+1
            self.save["coins"] = self.save.get("coins",0)+self.battle.coins_reward
            for m in self.team:
                add_friendship(self.save, m.name, 3)
            if self.save["battles_won"] % 5 == 0:
                self.save["badges"] = self.save.get("badges",0)+1
                notify("Neues Abzeichen erhalten! 🏅", C_YELLOW, 200)
            self.save["cards_known"] = sum(1 for c in self.flashcards if c.get("known"))
            rp_gain = 5 if not is_trainer else (15 if is_rocket else 10)
            add_rank_points(self.save, rp_gain)
            update_challenges(self.save)
            if is_trainer:
                self.save["trainer_battles_won"] = self.save.get("trainer_battles_won",0)+1
                tidx = getattr(self.battle,'_trainer_idx',None)
                if tidx is not None and self.overworld:
                    self.overworld._despawn_trainer(tidx)
                # Masterball drop
                mb_chance = 0.02 if is_rocket else 0.005
                if random.random() < mb_chance:
                    self.save["master_balls"] = self.save.get("master_balls",0)+1
                    notify("✦ MEISTERBALL gefunden! ✦", (255,215,0), 300)
                # ── Entwicklungsstein drop: 1% normal trainer, 3% Rocket ──
                stein_chance = 0.03 if is_rocket else 0.01
                if random.random() < stein_chance:
                    self.save["entwicklungsstein"] = self.save.get("entwicklungsstein",0)+1
                    notify("💎 ENTWICKLUNGSSTEIN gefunden!", C_STEIN, 300)
            if is_rocket:
                self.save["rocket_battles_won"] = self.save.get("rocket_battles_won",0)+1
            # Raid win
            if getattr(self.battle,'_is_raid',False) and self.overworld and self.overworld.raid:
                raid = self.overworld.raid
                cards_ok = self.battle.raid_cards_answered >= self.battle.raid_cards_needed
                if cards_ok:
                    raid["defeated"]=True; raid["can_catch"]=True
                    notify(f"⚔ RAID gewonnen! {raid['name']} kann gefangen werden! → Arena", C_GREEN, 300)
                else:
                    raid["defeated"]=True; raid["can_catch"]=False
                    notify(f"Raid gewonnen, aber nur {self.battle.raid_cards_answered}/{self.battle.raid_cards_needed} Lernkarten! Kein Fangen.", C_RED, 300)
            # Check evolutions (level-based) — branching = random
            self._pending_evos = []
            for m in self.team:
                if m.can_evolve() and m.nextEvolution:
                    evo_val = m.nextEvolution
                    choices = evo_val if isinstance(evo_val,list) else [evo_val]
                    choices = [c for c in choices if c in ALL_MOONIES_DICT]
                    if choices:
                        evo_name = random.choice(choices)
                        self._pending_evos.append((m, evo_name))
            for moonie_obj, evo_name in self._pending_evos:
                if moonie_obj not in self.team: continue
                old_name = moonie_obj.name
                new_m = get_moonie(evo_name)
                new_m.level = moonie_obj.level; new_m.xp = moonie_obj.xp
                new_m.max_hp = max(new_m.max_hp, moonie_obj.max_hp+10)
                new_m.attack = max(new_m.attack, moonie_obj.attack+5)
                new_m.current_hp = new_m.max_hp
                self.team[self.team.index(moonie_obj)] = new_m
                self.save["evolution_count"] = self.save.get("evolution_count",0)+1
                # Track Eeveelution without stone
                if evo_name in _eevee_set():
                    seen = self.save.setdefault("eevee_evolutions_no_stein",[])
                    if evo_name not in seen:
                        seen.append(evo_name)
                        self.save["eevee_evolutions_no_stein"] = seen
                pc = self.save.get("pc_box",[])
                if evo_name not in pc: pc.append(evo_name)
                self.save["pc_box"] = pc

        elif result == "catch":
            caught_name = self.battle.enemy_moonie.name if self.battle.enemy_moonie else "Unbekannt"
            pc = self.save.get("pc_box",[])
            if caught_name not in pc: pc.append(caught_name)
            self.save["pc_box"] = pc
            self.save["total_catches"] = self.save.get("total_catches",0)+1
            add_rank_points(self.save, 3)
            update_challenges(self.save)
            notify(f"{caught_name} wurde zum PC hinzugefügt!", C_GREEN, 160)
            try_card_drop(caught_name, self.save)
            if random.random() < 0.08:
                self.save["sonderbonbons"] = self.save.get("sonderbonbons",0)+1
                notify("🍬 Sonderbonbon erhalten!", (255,180,230), 180)

        elif result == "lose":
            for m in self.team: m.current_hp = m.max_hp
            notify("Du wachst im Pokécenter auf. Team vollständig geheilt!", C_RED, 200)
            if getattr(self.battle,'_is_raid',False) and self.overworld and self.overworld.raid:
                self.overworld.raid["defeated"]=True; self.overworld.raid["can_catch"]=False
                notify("Raid verloren! Das Pokémon ist entkommen.", C_RED, 240)

        elif result == "andreas":
            notify("Psycho Andreas hat das Moonie gestohlen! 😤", (255,80,255), 200)

        self._trigger_achievements()
        self.save["team"] = [moonie_to_dict(m) for m in self.team]
        save_game(self.save)
        self.battle = None

        # Show evolution screens for level-based evos
        if hasattr(self,'_pending_evos') and self._pending_evos:
            _, evo_name = self._pending_evos[-1]
            # Find old name (first in list)
            old_n, _ = (self._pending_evos[0][0].name, evo_name) if self._pending_evos else ("?", evo_name)
            # Build queue for evo screens — simple: show first pending
            self.evo_screen = EvolutionScreen(self._pending_evos[0][0].name if hasattr(self._pending_evos[0][0],'name') else "?", self._pending_evos[0][1], self.team)
            self._pending_evos = []
            self.screen_state = "evolution"; return

        self.screen_state = "overworld"

    def run(self):
        global shake_timer
        running = True
        while running:
            clock.tick(FPS)
            keys = pygame.key.get_pressed()
            if shake_timer > 0: shake_timer -= 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False; continue

                # Title
                if self.screen_state == "title":
                    result = self.title_screen.handle_event(event)
                    if result == "Neues Spiel": self.char_select = CharSelectScreen(); self.screen_state = "char_select"
                    elif result == "Spiel laden": self.load_existing_game()
                    elif result == "Beenden": running = False

                # Char select
                elif self.screen_state == "char_select":
                    result = self.char_select.handle_event(event)
                    if result == "start":
                        sd = default_save()
                        sd["trainer"] = self.char_select.trainer_sel
                        sd["name"]    = self.char_select.name
                        sd["starter"] = self.char_select.STARTERS[self.char_select.starter_sel]
                        self.start_new_game(sd)

                # Overworld
                elif self.screen_state == "overworld":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_b: self.pokedex = PokedexScreen(self.save.get("pc_box",[]), save_ref=self.save); self.screen_state = "pokedex"
                        elif event.key == pygame.K_p: self.pc_box_screen = PCBoxScreen(self.save, self.team); self.screen_state = "pcbox"
                        elif event.key == pygame.K_a: self.ach_screen = AchievementScreen(self.save, self.flashcards, ALL_MOONIES_DICT); self.screen_state = "achievements"
                        elif event.key == pygame.K_c: self.card_album_screen = CardAlbumScreen(self.save); self.screen_state = "card_album"
                        elif event.key == pygame.K_k: self.blackmarket_screen = BlackMarketScreen(self.save); self.screen_state = "blackmarket"
                        elif event.key == pygame.K_t: self.team_screen = TeamScreen(self.team, self.save); self.screen_state = "team"
                        elif event.key == pygame.K_i: self.item_bag = ItemBagScreen(self.save, self.team); self.screen_state = "itembag"
                        elif event.key == pygame.K_g: self.guild_screen = GuildScreen(self.save); self.screen_state = "guild"
                        elif event.key == pygame.K_e: self.exam_screen = ExamScreen(self.save, self.flashcards); self.screen_state = "exam"
                        elif event.key == pygame.K_o: self.settings_screen = SettingsScreen(self.save); self.screen_state = "settings"
                        elif event.key == pygame.K_r:
                            cur = self.save.get("current_map","Normal")
                            self.travel_screen = TravelMenuScreen(self.save, cur)
                            self.screen_state = "travel"
                        elif event.key == pygame.K_ESCAPE: save_game(self.save); notify("Spiel gespeichert!", C_GREEN)

                # Battle
                elif self.screen_state == "battle" and self.battle:
                    self.battle.handle_event(event, self.save)

                # Shop
                elif self.screen_state == "shop" and self.shop:
                    result = self.shop.handle_event(event)
                    if result == "close": self.screen_state = "overworld"; self.overworld.center_cooldown = 90

                # Center
                elif self.screen_state == "center" and self.center:
                    result = self.center.handle_event(event)
                    if result == "close": self.screen_state = "overworld"; self.overworld.center_cooldown = 90

                # Team
                elif self.screen_state == "team" and self.team_screen:
                    result = self.team_screen.handle_event(event)
                    if result == "close": self.screen_state = "overworld"

                # Item Bag
                elif self.screen_state == "itembag" and self.item_bag:
                    result = self.item_bag.handle_event(event)
                    if result == "close": self.screen_state = "overworld"
                    elif isinstance(result, tuple) and result[0] == "use_stein":
                        self.screen_state = "overworld"
                        self.open_stein_picker()

                # PC Box
                elif self.screen_state == "pcbox" and self.pc_box_screen:
                    result = self.pc_box_screen.handle_event(event)
                    if result == "close": self.screen_state = "overworld"

                # Achievements
                elif self.screen_state == "achievements" and self.ach_screen:
                    result = self.ach_screen.handle_event(event)
                    if result == "close": self.screen_state = "overworld"

                # Card Album
                elif self.screen_state == "card_album" and self.card_album_screen:
                    result = self.card_album_screen.handle_event(event)
                    if result == "close": self.screen_state = "overworld"

                # Blackmarket
                elif self.screen_state == "blackmarket" and self.blackmarket_screen:
                    result = self.blackmarket_screen.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"
                        if self.overworld:
                            self.overworld.blackmarket_cooldown = 120
                        
                # Daily Quiz
                elif self.screen_state == "daily_quiz" and self.daily_quiz_screen:
                    result = self.daily_quiz_screen.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"
                        if self.overworld: self.overworld.daily_cooldown = 120
                    elif isinstance(result, tuple) and result[0] == "reward":
                        mon = result[1]
                        self.daily_quiz_screen = None
                        self.screen_state = "overworld"
                        # Start passive catch battle
                        self.battle = PassiveCatchBattle(self.team, mon, self.flashcards)
                        self.battle.save_data_ref = self.save
                        self.screen_state = "battle"


                # Guild
                elif self.screen_state == "guild" and self.guild_screen:
                    result = self.guild_screen.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"
                        save_game(self.save)

                # Exam
                elif self.screen_state == "exam" and self.exam_screen:
                    result = self.exam_screen.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"
                        update_challenges(self.save)
                        save_game(self.save)

                # Settings
                elif self.screen_state == "settings" and self.settings_screen:
                    result = self.settings_screen.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"
                        save_game(self.save)

                # Travel Menu
                elif self.screen_state == "travel" and self.travel_screen:
                    result = self.travel_screen.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"
                    elif isinstance(result, tuple) and result[0] == "travel":
                        target_map = result[1]
                        self._travel_to(target_map)

                # Raid Pass Select
                elif self.screen_state == "raid_pass_select" and hasattr(self,'raid_pass_screen'):
                    result = self.raid_pass_screen.handle_event(event)
                    if result == "close": self.screen_state = "overworld"
                    elif isinstance(result,tuple) and result[0] == "start_raid":
                        self.screen_state = "overworld"
                        self.start_raid_battle(premium=(result[1]=="premium"))

                # Evolution
                elif self.screen_state == "evolution" and self.evo_screen:
                    result = self.evo_screen.handle_event(event)
                    if result == "done": self.evo_screen = None; self.screen_state = "overworld"

                # Pokedex
                elif self.screen_state == "pokedex" and self.pokedex:
                    result = self.pokedex.handle_event(event)
                    if result == "close": self.screen_state = "overworld"

                # ── Stein: Pokémon wählen ──
                elif self.screen_state == "stein_mon" and self.stein_mon_screen:
                    result = self.stein_mon_screen.handle_event(event)
                    if result in ("cancel", "close"):
                        self.stein_mon_screen = None
                        self.screen_state = "overworld"
                    elif isinstance(result, tuple) and result[0] == "picked":
                        idx = result[1]
                        moonie_obj = self.team[idx] if idx < len(self.team) else None
                        self.stein_mon_screen = None
                        if moonie_obj:
                            self.apply_stein_to(moonie_obj)
                        else:
                            self.screen_state = "overworld"
                # ── Stein: Entwicklung wählen ──
                elif self.screen_state == "stein_evo" and self.stein_evo_screen:
                    result = self.stein_evo_screen.handle_event(event)
                    if result in ("cancel", "close"):
                        self.save["entwicklungsstein"] = self.save.get("entwicklungsstein",0)+1
                        self.stein_evo_screen = None
                        self.screen_state = "overworld"
                    elif result == "confirm":
                        evo_name = self.stein_evo_screen.result
                        moonie_obj = self.stein_evo_screen.mon
                        self.stein_evo_screen = None
                        if evo_name:
                            self._do_stein_evolution(moonie_obj, evo_name)
                        else:
                            self.screen_state = "overworld"

            # ── Per-frame updates ──
            if self.screen_state == "overworld" and self.overworld:
                action = self.overworld.update(keys) if self.screen_state == "overworld" else None
                if action == "wild_encounter": self.start_wild_battle()
                elif action == "shop": self.shop = ShopScreen(self.save, self.team); self.screen_state = "shop"
                elif action == "center": self.center = PokeCenterScreen(self.save, self.team); self.screen_state = "center"
                elif action == "blackmarket": self.blackmarket_screen = BlackMarketScreen(self.save); self.screen_state = "blackmarket"
                elif action and action.startswith("trainer_"):
                    idx = int(action.split("_")[1]); self.start_trainer_battle(idx)
                elif action == "daily_event":
                    self.daily_quiz_screen = WhosThatPokemonScreen(
                        self.save, ALL_MOONIES_DICT, self.flashcards)
                    self.screen_state = "daily_quiz"
                elif action == "raid_catch": self.start_raid_catch()
                elif action == "raid_pass_select":
                    self.raid_pass_screen = RaidPassSelectScreen(self.save, self.overworld.raid)
                    self.screen_state = "raid_pass_select"
            elif self.screen_state == "battle" and self.battle:
                self.battle.update()
                if self.battle.state == "done": self.end_battle()
            elif self.screen_state == "evolution" and self.evo_screen:
                self.evo_screen.update()
            elif self.screen_state == "stein_mon" and self.stein_mon_screen:
                self.stein_mon_screen.anim_t += 1
            elif self.screen_state == "stein_evo" and self.stein_evo_screen:
                self.stein_evo_screen.anim_t += 1
            elif self.screen_state == "daily_quiz" and self.daily_quiz_screen:
                self.daily_quiz_screen.anim_t += 1
            elif self.screen_state == "guild"    and self.guild_screen:    self.guild_screen.anim_t += 1
            elif self.screen_state == "exam"     and self.exam_screen:     self.exam_screen.anim_t += 1
            elif self.screen_state == "settings" and self.settings_screen: self.settings_screen.anim_t += 1
            elif self.screen_state == "travel"   and self.travel_screen:   self.travel_screen.anim_t += 1

            # ── Drawing ──
            surface = screen
            if self.screen_state == "title": self.title_screen.draw(surface)
            elif self.screen_state == "char_select": self.char_select.draw(surface)
            elif self.screen_state == "overworld" and self.overworld: self.overworld.draw(surface)
            elif self.screen_state == "battle" and self.battle: self.battle.draw(surface)
            elif self.screen_state == "shop" and self.shop: self.shop.draw(surface)
            elif self.screen_state == "center" and self.center: self.center.draw(surface)
            elif self.screen_state == "team" and self.team_screen: self.team_screen.draw(surface)
            elif self.screen_state == "itembag" and self.item_bag: self.item_bag.draw(surface)
            elif self.screen_state == "evolution" and self.evo_screen: self.evo_screen.draw(surface)
            elif self.screen_state == "pcbox" and self.pc_box_screen: self.pc_box_screen.draw(surface)
            elif self.screen_state == "achievements" and self.ach_screen: self.ach_screen.draw(surface)
            elif self.screen_state == "card_album" and self.card_album_screen: self.card_album_screen.draw(surface)
            elif self.screen_state == "blackmarket" and self.blackmarket_screen: self.blackmarket_screen.draw(surface)
            elif self.screen_state == "daily_quiz"  and self.daily_quiz_screen:  self.daily_quiz_screen.draw(surface)
            elif self.screen_state == "guild"       and self.guild_screen:      self.guild_screen.draw(surface)
            elif self.screen_state == "exam"        and self.exam_screen:       self.exam_screen.draw(surface)
            elif self.screen_state == "settings"    and self.settings_screen:   self.settings_screen.draw(surface)
            elif self.screen_state == "travel"      and self.travel_screen:      self.travel_screen.draw(surface)
            elif self.screen_state == "raid_pass_select" and hasattr(self,'raid_pass_screen'):
                if self.overworld: self.overworld.draw(surface)
                self.raid_pass_screen.draw(surface)
            elif self.screen_state == "pokedex" and self.pokedex: self.pokedex.draw(surface)
            elif self.screen_state == "stein_mon" and self.stein_mon_screen: self.stein_mon_screen.draw(surface)
            elif self.screen_state == "stein_evo" and self.stein_evo_screen: self.stein_evo_screen.draw(surface)
            else: surface.fill(C_BG)

            pygame.display.flip()

        if self.save: save_game(self.save)
        pygame.quit(); sys.exit()

# Alias für Kompatibilität
Game = GameManager

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    game = GameManager()
    game.run()