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

SW, SH = 900, 640
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

# ── Flashcard loader ───────────────────────────────────────────────────────────
def load_flashcards(path):
    cards = []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    q = row[0].replace('$', '').strip()
                    a = row[1].replace('$', '').strip()
                    cards.append({"q": q, "a": a, "known": False, "shown": 0})
    except Exception as e:
        print(f"Flashcard load error: {e}")
    return cards

# ── Save / Load ────────────────────────────────────────────────────────────────
SAVE_FILE = os.path.join(BASE, "savegame.json")

def default_save():
    return {
        "trainer": 0, "name": "Spieler",
        "team": [], "pc_box": [],
        "balls": 10, "coins": 0,
        "potions": 3, "super_potions": 0,
        "badges": 0, "battles_won": 0,
        "cards_known": 0, "total_catches": 0,
        "step_count": 0,
        # Achievement stat tracking
        "trainer_battles_won":  0,
        "rocket_battles_won":   0,
        "evolution_count":      0,
        "cards_correct_total":  0,
        "cards_best_streak":    0,
        "cards_current_streak": 0,
        "achievements": {},
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

def get_moonie(name):
    m = ALL_MOONIES_DICT.get(name)
    if m:
        return m.clone_for_battle()
    # fallback
    import moonie as mmod
    return mmod.Moonie(name,"common",False,["Normal"],0,1,"assets/moonie/ditto.png")

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

    # rarity stripe
    pygame.draw.rect(surf, r_color, (x, y, w, 8), border_radius=14)

    # image
    img = load_img(moonie_obj.image, (w-20, h-100))
    if flip:
        img = pygame.transform.flip(img, True, False)
    surf.blit(img, (x+10, y+14))

    # name
    draw_text(surf, moonie_obj.name, F_SMALL, C_WHITE, x + w//2, y + h - 78, center=True, shadow=True)

    # types
    types = moonie_obj.types
    tx = x + w//2 - (len(types)*34)
    for t in types:
        draw_type_badge(surf, t, tx, y + h - 58)
        tx += 68

    # level / hp
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

# ── Flashcard mini-game ────────────────────────────────────────────────────────
class FlashcardGame:
    _save_ref = None   # set by Game to allow achievement tracking

    def __init__(self, cards, reward_callback, n=3):
        self.cards = cards
        self.reward_cb = reward_callback
        self.n_required = n
        self.answered = 0
        self.correct = 0
        self.card = None
        self.state = "question"   # question | answer | result
        self.input_text = ""
        self.feedback = ""
        self.feedback_color = C_WHITE
        self.done = False
        self.pick_card()
        self.cursor_blink = 0

    def pick_card(self):
        unknown = [c for c in self.cards if not c["known"]]
        pool = unknown if unknown else self.cards
        self.card = random.choice(pool) if pool else None
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
        if matches >= threshold or user in answer or answer in user:
            self.feedback = "✓ Richtig! " + self.card["a"]
            self.feedback_color = C_GREEN
            self.correct += 1
            self.card["known"] = True
            add_particles(SW//2, 300, (80,220,100), n=30)
            # Track for achievements via global save ref
            if FlashcardGame._save_ref is not None:
                s = FlashcardGame._save_ref
                s["cards_correct_total"] = s.get("cards_correct_total", 0) + 1
                s["cards_current_streak"] = s.get("cards_current_streak", 0) + 1
                best = s.get("cards_best_streak", 0)
                if s["cards_current_streak"] > best:
                    s["cards_best_streak"] = s["cards_current_streak"]
        else:
            self.feedback = "✗ Falsch. Antwort: " + self.card["a"]
            self.feedback_color = C_RED
            if FlashcardGame._save_ref is not None:
                FlashcardGame._save_ref["cards_current_streak"] = 0
        self.state = "result"

    def draw(self, surf):
        # Overlay
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((10, 12, 20, 230))
        surf.blit(overlay, (0, 0))

        # Panel
        pw, ph = 780, 440
        px, py = SW//2 - pw//2, SH//2 - ph//2
        draw_rounded_rect(surf, C_PANEL, (px, py, pw, ph), 18, 2, C_BLUE)

        # Header
        hdr = "📚 Lernkarte – Frage" if self.state == "question" else \
              "📝 Deine Antwort" if self.state == "answer" else "✅ Ergebnis"
        draw_text(surf, hdr, F_BIG, C_YELLOW, SW//2, py+18, center=True, shadow=True)

        prog = f"Frage {self.answered+1} / {self.n_required}   Richtig: {self.correct}"
        draw_text(surf, prog, F_SMALL, C_GRAY, SW//2, py+60, center=True)

        if self.card:
            # Question box
            q_lines = wrap_text(self.card["q"], F_MED, pw-60)
            qy = py + 95
            for line in q_lines:
                draw_text(surf, line, F_MED, C_WHITE, SW//2, qy, center=True)
                qy += 30

            if self.state == "question":
                draw_text(surf, "[ ENTER ] um Antwort einzugeben", F_SMALL, C_GRAY, SW//2, py+ph-60, center=True)

            elif self.state == "answer":
                # Input field
                ify = qy + 20
                draw_rounded_rect(surf, C_DARK, (px+30, ify, pw-60, 44), 8, 2, C_BLUE)
                self.cursor_blink = (self.cursor_blink+1) % 60
                cursor = "|" if self.cursor_blink < 30 else " "
                inp_display = self.input_text + cursor
                # wrap input display
                inp_lines = wrap_text(inp_display, F_MED, pw-80)
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
    STATES = ["intro","player_turn","enemy_turn","catch_anim","flashcard","result","run"]

    def __init__(self, player_team, enemy_data, wild_moonie=None, flashcards=None, is_wild=False):
        self.player_team  = player_team   # list of Moonie objects
        self.enemy_data   = enemy_data    # Enemy object or None
        self.wild_moonie  = wild_moonie   # Moonie for wild encounter
        self.flashcards   = flashcards or []
        self.is_wild      = is_wild
        self.state        = "intro"
        self.log          = []
        self.log_timer    = 0
        self.result       = None          # "win","lose","catch","run"
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
        self.item_pick_sel = 0
        self.raid_cards_needed = 0   # for raid battles
        self.raid_cards_answered = 0
        self.overworld_ref = None    # set by Game for raid card tracking
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

        # 1. Always add the named moonies from the object
        for name in en.moonies:
            m = get_moonie(name)
            m.level = max(1, strength * 8 + random.randint(-3, 3))
            m.max_hp = m.max_hp + m.level * 2
            m.attack = m.attack + m.level
            m.current_hp = m.max_hp
            self.enemy_moonies.append(m)

        # 2. Add 0–(6 - len(fixed)) random pokemon matching the trainer's types
        max_extra = 6 - len(self.enemy_moonies)
        if max_extra > 0:
            n_extra = random.randint(0, max_extra)
            trainer_types = set(en.pokemonTypes)
            # Build pool of moonies matching any of the trainer's types
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
        self.save_data_ref = save_data  # store for draw method
        if self.flash_game and not self.flash_game.done:
            self.flash_game.handle_event(event)
            if self.flash_game.done:
                self.flash_game = None
                self.state = "player_turn"
                # bonus
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
        elif self.state == "player_turn":
            if event.key == pygame.K_LEFT:
                self.selected_btn = (self.selected_btn - 1) % 4
            elif event.key == pygame.K_RIGHT:
                self.selected_btn = (self.selected_btn + 1) % 4
            elif event.key == pygame.K_UP:
                self.selected_btn = (self.selected_btn - 2) % 4
            elif event.key == pygame.K_DOWN:
                self.selected_btn = (self.selected_btn + 2) % 4
            elif event.key == pygame.K_RETURN or event.key == pygame.K_z:
                self._player_action(self.selected_btn, save_data)
        elif self.state == "result":
            if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_ESCAPE, pygame.K_SPACE):
                self.state = "done"   # signal to main loop: close battle

    def _player_action(self, btn, save_data):
        pm = self.player_moonie
        em = self.enemy_moonie
        if not em:
            self.state = "result"; self.result = "win"; return

        if btn == 0:  # Attack
            # Raid: flashcard every 2nd attack; normal battles: 40% chance
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
                    # Count correct raid answers
                    if is_raid and correct > 0:
                        self.raid_cards_answered = getattr(self, 'raid_cards_answered', 0) + correct
                        if self.overworld_ref:
                            self.overworld_ref.raid["cards_answered"] = self.raid_cards_answered
                self.flash_game = FlashcardGame(self.flashcards, reward, n=1)
                self.push_log("Lernfrage!" if not is_raid else f"📚 Raid-Lernkarte! ({getattr(self,'raid_cards_answered',0)}/{getattr(self,'raid_cards_needed',0)})")
                return
            dmg, mult = pm.calculate_damage(em)
            em.take_damage(dmg)
            self.shake_enemy = 12
            add_particles(650, 250, (220,60,60), n=20)
            eff_lbl, eff_col = effectiveness_label(mult) if mult != 1.0 else ("", None)
            log_msg = f"{pm.name} greift an! -{dmg} HP"
            if eff_lbl: log_msg += f"  {eff_lbl}"
            self.push_log(log_msg)
            self.last_effectiveness = (mult, eff_lbl, eff_col or C_WHITE)
            if not em.is_alive():
                self._enemy_faint()
                return
            self.turn_cooldown = 40
            self._enemy_turn()

        elif btn == 1:  # Bag / Pokéball
            if save_data["balls"] <= 0:
                self.push_log("Keine Pokébälle mehr!")
                return
            if not self.is_wild:
                self.push_log("Du kannst keine Trainer-Moonies fangen!")
                return
            save_data["balls"] -= 1
            self.balls_used += 1
            # 8% chance Psycho Andreas appears and steals the pokemon
            if random.random() < 0.08:
                self.state = "andreas_steal"
                self.andreas_anim_t = 0
                self.push_log("Psycho Andreas taucht auf!!!")
                return
            chance = em.catch_rate * (1 - em.current_hp/em.max_hp*0.5)
            self.state = "catch_anim"
            self.catch_anim_t = 0
            self.catch_result = random.random() < chance
            self.push_log(f"Pokéball geworfen! (Bälle: {save_data['balls']})")

        elif btn == 2:  # Item bag — open picker
            self.state = "item_pick"
            self.item_pick_sel = 0

        elif btn == 3:  # Run
            if self.is_wild:
                if random.random() < 0.6:
                    self.state = "result"; self.result = "run"
                    self.push_log("Du bist geflohen!")
                else:
                    self.push_log("Flucht fehlgeschlagen!")
                    self._enemy_turn()
            else:
                self.push_log("Aus Trainer-Kämpfen kann man nicht fliehen!")

    def _enemy_faint(self):
        em = self.enemy_moonie
        add_particles(650, 250, (255,200,50), n=40, size=8)
        self.xp_gained += em.level * 8
        self.coins_reward += em.level * (8 if not self.is_wild else 3)  # trainers pay more
        self.push_log(f"{em.name} wurde besiegt!")
        self.enemy_idx += 1
        if self.enemy_idx >= len(self.enemy_moonies):
            self.state = "result"; self.result = "win"
            pm = self.player_moonie
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
        dmg, mult = em.calculate_damage(pm)
        pm.take_damage(dmg)
        self.shake_player = 12
        add_particles(250, 380, (220,60,60), n=15)
        self.push_log(f"{em.name} greift an! -{dmg} HP")
        if not pm.is_alive():
            # Try next team member
            alive = [m for m in self.player_team if m.is_alive()]
            if not alive:
                self.state = "result"; self.result = "lose"
                self.push_log("Alle deine Moonies sind besiegt!")
            else:
                self.player_idx = self.player_team.index(alive[0])
                self.push_log(f"{alive[0].name} kämpft weiter!")

    def _get_usable_items(self, save_data):
        items = []
        if save_data.get("potions", 0) > 0:
            items.append(("Trank", "+30 HP", "potions", 30))
        if save_data.get("super_potions", 0) > 0:
            items.append(("Super Trank", "+80 HP", "super_potions", 80))
        return items

    def _use_item(self, item, save_data):
        name, desc, key, heal = item
        pm = self.player_moonie
        save_data[key] -= 1
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
        self.anim_t += 1

        # Andreas steal animation
        if self.state == "andreas_steal":
            self.andreas_anim_t += 1
            # Try to play audio once at start
            if self.andreas_anim_t == 1:
                try:
                    snd = pygame.mixer.Sound(os.path.join(BASE, "assets/audio/haltStop.mp3"))
                    snd.play()
                    self._andreas_audio_len = int(snd.get_length() * 60) + 30  # frames to wait
                except Exception:
                    self._andreas_audio_len = 150  # fallback ~2.5s
            # Wait until audio is done
            if self.andreas_anim_t >= getattr(self, '_andreas_audio_len', 150):
                em = self.enemy_moonie
                self.push_log(f"Psycho Andreas hat {em.name} weggeschnappt!")
                add_particles(SW//2, SH//2, (180,20,180), n=40)
                self.state = "result"; self.result = "andreas"

        # Catch animation
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

        # Top HUD bar with controls and inventory
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

        # Raid card progress in battle HUD
        if getattr(self, '_is_raid', False):
            needed = getattr(self, 'raid_cards_needed', 0)
            answered = getattr(self, 'raid_cards_answered', 0)
            ok = answered >= needed
            rc = C_GREEN if ok else C_YELLOW
            draw_text(surf, f"📚 RAID: {answered}/{needed} Lernkarten", F_SMALL, rc, SW//2, 10, center=True, shadow=True)

        # Background
        bg_color = (20, 18, 35) if not self.is_wild else (15, 30, 18)
        surf.fill(bg_color)

        # Ground line
        pygame.draw.rect(surf, (50,60,40), (0, SH-160, SW, 160))
        pygame.draw.line(surf, (80,100,60), (0, SH-160), (SW, SH-160), 2)

        # --- Enemy moonie ---
        em = self.enemy_moonie
        if em:
            ex_base = 620
            ey_base = 160
            ex = ex_base + (random.randint(-3,3) if self.shake_enemy > 0 else 0)
            ey = ey_base
            img = load_img(em.image, (160, 160))
            bob = math.sin(self.anim_t * 0.05) * 4
            surf.blit(img, (ex - 80, ey + bob))
            # Shadow
            pygame.draw.ellipse(surf, (0,0,0,60),
                pygame.Rect(ex-60, SH-165, 120, 20))
            # HP bar + name
            draw_rounded_rect(surf, C_PANEL, (ex-90, ey-55, 200, 50), 8)
            draw_text(surf, em.name, F_SMALL, C_WHITE, ex-84, ey-50, shadow=True)
            lbl = f"Lv {em.level}"
            draw_text(surf, lbl, F_TINY, C_GRAY, ex+60, ey-50)
            draw_hp_bar(surf, ex-84, ey-25, 180, 10, em.current_hp, em.max_hp, label=True)
            for i, t in enumerate(em.types):
                draw_type_badge(surf, t, ex-84 + i*70, ey-12)

        # --- Player moonie ---
        pm = self.player_moonie
        if pm:
            px_base = 200
            py_base = 300
            px = px_base + (random.randint(-3,3) if self.shake_player > 0 else 0)
            py = py_base
            img = load_img(pm.image, (160, 160))
            img = pygame.transform.flip(img, True, False)
            bob = math.sin(self.anim_t * 0.05 + 1) * 4
            surf.blit(img, (px - 80, py + bob))
            # HP bar + name
            draw_rounded_rect(surf, C_PANEL, (px-90, py+168, 200, 55), 8)
            draw_text(surf, pm.name, F_SMALL, C_WHITE, px-84, py+173, shadow=True)
            draw_text(surf, f"Lv {pm.level}", F_TINY, C_GRAY, px+60, py+173)
            draw_hp_bar(surf, px-84, py+198, 180, 10, pm.current_hp, pm.max_hp, label=True)
            # XP bar
            xp_pct = pm.xp / pm.xp_to_next if pm.xp_to_next else 0
            pygame.draw.rect(surf, (60,60,80), (px-84, py+216, 180, 6), border_radius=3)
            if xp_pct > 0:
                pygame.draw.rect(surf, C_BLUE, (px-84, py+216, int(180*xp_pct), 6), border_radius=3)

        # --- Log panel ---
        log_rect = (20, SH - 148, SW - 260, 130)
        draw_rounded_rect(surf, C_DARK, log_rect, 10, 1, (80,80,100))
        for i, txt in enumerate(self.log[-4:]):
            color = C_WHITE if i == len(self.log[-4:])-1 else C_GRAY
            draw_text(surf, txt, F_SMALL, color, log_rect[0]+10, log_rect[1]+10+i*28)

        # Effectiveness flash
        mult, lbl, ecol = self.last_effectiveness
        if lbl and self.state == "player_turn":
            draw_text(surf, lbl, F_SMALL, ecol, log_rect[0]+10, log_rect[1]+120, shadow=True)

        # --- Buttons ---
        if self.state == "item_pick":
            items = self._get_usable_items(self.save_data_ref)
            pw, ph = 320, 200
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
                    draw_rounded_rect(surf, ibg, (px2+16, py2+48+i*46, pw-32, 38), 8, 2 if sel else 1, ibc)
                    draw_text(surf, f"{name}  ({cnt}x)  {desc}", F_SMALL, C_WHITE, px2+pw//2, py2+58+i*46, center=True)
            draw_text(surf, "↑↓ wählen   ENTER nutzen   ESC zurück", F_TINY, C_GRAY, px2+pw//2, py2+ph-20, center=True)
        elif self.state == "player_turn":
            btn_labels = ["⚔ Angriff", "🎯 Pokéball", "💊 Tasche", "🏃 Fliehen"]
            btn_colors = [(60,90,150),(90,150,60),(80,140,80),(150,60,60)]
            bw, bh = 118, 52
            bx = SW - 250
            by = SH - 148
            for i, (lbl, col) in enumerate(zip(btn_labels, btn_colors)):
                bxi = bx + (i%2)*(bw+8)
                byi = by + (i//2)*(bh+8)
                sel = (i == self.selected_btn)
                bc = C_YELLOW if sel else (*col,)
                draw_rounded_rect(surf, col, (bxi, byi, bw, bh), 10,
                                  3 if sel else 1, bc)
                if sel:
                    glow = pygame.Surface((bw+6,bh+6), pygame.SRCALPHA)
                    pygame.draw.rect(glow,(255,220,50,80),(0,0,bw+6,bh+6),border_radius=12)
                    surf.blit(glow,(bxi-3,byi-3))
                draw_text(surf, lbl, F_SMALL, C_WHITE, bxi+bw//2, byi+bh//2-10, center=True, shadow=True)
                # Show potion counts on bag button
                if i == 2:
                    pot = self.save_data_ref.get("potions",0) if hasattr(self,"save_data_ref") else 0
                    sp  = self.save_data_ref.get("super_potions",0) if hasattr(self,"save_data_ref") else 0
                    draw_text(surf, f"T:{pot} ST:{sp}", F_TINY, C_GRAY, bxi+bw//2, byi+bh//2+14, center=True)

        elif self.state == "andreas_steal":
            # Andreas overlay
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
            # Progress bar for audio
            total = getattr(self, '_andreas_audio_len', 150)
            pct = min(1.0, self.andreas_anim_t / total)
            pygame.draw.rect(surf, (60,20,60), (SW//2-150, SH-50, 300, 14), border_radius=7)
            pygame.draw.rect(surf, (220,60,220), (SW//2-150, SH-50, int(300*pct), 14), border_radius=7)
            draw_text(surf, "Warte auf Andreas...", F_TINY, C_GRAY, SW//2, SH-70, center=True)

        elif self.state == "catch_anim":
            # Pokéball animation
            t = self.catch_anim_t
            ball_x = SW//2 + math.sin(t*0.2)*100
            ball_y = SH//2 - abs(math.cos(t*0.08))*120
            ball_img = load_img("assets/pokeball.png", (48,48))
            surf.blit(ball_img, (int(ball_x)-24, int(ball_y)-24))
            if t > 60:
                msg = "Gefangen!" if self.catch_result else "Ausgebrochen!"
                col = C_GREEN if self.catch_result else C_RED
                draw_text(surf, msg, F_BIG, col, SW//2, SH//2, center=True, shadow=True)

        elif self.state in ("result", "done"):
            overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            surf.blit(overlay, (0,0))
            msgs = {
                "win":      "Sieg! 🎉",
                "lose":     "Niederlage...",
                "catch":    "Gefangen! 🎊",
                "run":      "Geflohen!",
                "andreas":  "Psycho Andreas war schneller!",
                "end":      "Ende"
            }
            cols = {
                "win":     C_YELLOW,
                "lose":    C_RED,
                "catch":   C_GREEN,
                "run":     C_GRAY,
                "andreas": (255, 80, 255),
                "end":     C_WHITE
            }
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

        # Particles & notifications
        update_particles(surf)
        draw_notifications(surf)

# ── Pokedex screen ─────────────────────────────────────────────────────────────
class PokedexScreen:
    COLS = 5
    ROWS = 4
    PER_PAGE = COLS * ROWS

    def __init__(self, caught_list):
        self.caught_set  = set(caught_list)
        self.all_names   = sorted(ALL_MOONIES_DICT.keys())
        self.only_caught = True   # default: show only caught
        self.search      = ""
        self.searching   = False
        self.sel         = 0
        self.detail_name = None
        self._sil_cache  = {}

    def _visible(self):
        pool = [n for n in self.all_names
                if (not self.only_caught or n in self.caught_set)
                and (not self.search or self.search.lower() in n.lower())]
        return pool

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key

        # Close detail overlay
        if self.detail_name:
            self.detail_name = None
            return None

        # Search mode
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

        # Normal navigation
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
            if 0 <= self.sel < total and vis[self.sel] in self.caught_set:
                self.detail_name = vis[self.sel]
        elif k == pygame.K_f:   # toggle filter
            self.only_caught = not self.only_caught
            self.sel = 0
        elif k == pygame.K_s:   # search
            self.searching = True
            self.search = ""
        elif k == pygame.K_ESCAPE or k == pygame.K_x:
            return "close"
        return None

    def _make_silhouette(self, img):
        sil = img.copy()
        sil.blit(pygame.Surface(sil.get_size(), 0), (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        # Actually: just overlay pure black with BLEND_RGB_MULT
        dark = pygame.Surface(sil.get_size(), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 255))
        sil.blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        return sil

    def draw(self, surf):
        surf.fill((12, 14, 22))
        vis = self._visible()
        total = len(vis)

        # Header bar
        draw_rounded_rect(surf, C_PANEL, (0, 0, SW, 54), 0)
        draw_text(surf, "Pokédex", F_BIG, C_YELLOW, SW//2, 4, center=True, shadow=True)
        caught_count = len(self.caught_set)
        status = "Nur Gefangene" if self.only_caught else "Alle"
        draw_text(surf, f"{caught_count}/{len(self.all_names)} gefangen  |  Filter: {status}  |  F=Filter  S=Suche  ESC=zurück  ENTER=Detail", F_TINY, C_GRAY, SW//2, 38, center=True)

        # Search bar (if active or has text)
        if self.searching or self.search:
            bar_col = C_BLUE if self.searching else (60, 60, 80)
            draw_rounded_rect(surf, bar_col, (SW//2-200, 56, 400, 28), 8, 2, C_YELLOW if self.searching else C_GRAY)
            cursor = "|" if self.searching and int(time.time()*2)%2 == 0 else ""
            draw_text(surf, f"Suche: {self.search}{cursor}", F_SMALL, C_WHITE, SW//2, 62, center=True)

        # Grid
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

            bg  = (40, 55, 40) if caught else (28, 28, 38)
            bdr = C_YELLOW if sel else ((80, 160, 80) if caught else (45, 45, 65))
            draw_rounded_rect(surf, bg, (x+2, y+2, cw-4, ch-4), 8, 2 if sel else 1, bdr)

            m = ALL_MOONIES_DICT.get(name)
            if m:
                img = load_img(m.image, (68, 68))
                if not caught:
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
            else:
                draw_text(surf, "???", F_SMALL, C_GRAY, x + cw//2, y + ch - 24, center=True)

            # Global dex number
            global_idx = self.all_names.index(name)
            draw_text(surf, f"#{global_idx+1:03d}", F_TINY, C_GRAY, x+4, y+5)

        if total == 0:
            draw_text(surf, "Keine Pokémon gefunden." if self.search else "Noch keine gefangen!", F_MED, C_GRAY, SW//2, 300, center=True)

        # Page / filter buttons
        total_pages = max(1, (total + self.PER_PAGE - 1) // self.PER_PAGE)
        draw_text(surf, f"Seite {page+1}/{total_pages}", F_TINY, C_GRAY, SW//2, SH-18, center=True)

        # Filter toggle button (bottom right)
        fc = C_GREEN if self.only_caught else C_GRAY
        draw_rounded_rect(surf, (30, 40, 30) if self.only_caught else (40, 40, 50), (SW-180, SH-36, 172, 28), 8, 2, fc)
        draw_text(surf, f"[F] {'Alle zeigen' if self.only_caught else 'Nur Gefangene'}", F_TINY, fc, SW-94, SH-24, center=True)

        # Detail overlay
        if self.detail_name and self.detail_name in self.caught_set:
            m = ALL_MOONIES_DICT.get(self.detail_name)
            if m:
                self._draw_detail(surf, m)

        draw_notifications(surf)

    def _draw_detail(self, surf, m):
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))
        pw, ph = 500, 380
        px, py = SW//2 - pw//2, SH//2 - ph//2
        draw_rounded_rect(surf, C_PANEL, (px, py, pw, ph), 18, 2, C_YELLOW)
        r_col = m.get_rarity_color()
        pygame.draw.rect(surf, r_col, (px, py, pw, 10), border_radius=18)
        img = load_img(m.image, (180, 180))
        surf.blit(img, (px + pw//2 - 90, py + 15))
        draw_text(surf, m.name, F_BIG, C_WHITE, px + pw//2, py + 205, center=True, shadow=True)
        draw_text(surf, m.rarity.capitalize(), F_SMALL, r_col, px + pw//2, py + 238, center=True)
        tw = len(m.types) * 74
        tx = px + pw//2 - tw//2
        for t in m.types:
            draw_type_badge(surf, t, tx, py + 262)
            tx += 74
        draw_text(surf, f"HP: {m.max_hp}   Angriff: {m.attack}   Level: {m.level}", F_SMALL, C_GRAY, px + pw//2, py + 300, center=True)
        if m.nextEvolution and isinstance(m.nextEvolution, str):
            draw_text(surf, f"Entwicklung: {m.nextEvolution}", F_SMALL, C_BLUE, px + pw//2, py + 326, center=True)
        draw_text(surf, "[ beliebige Taste ] schließen", F_TINY, C_GRAY, px + pw//2, py + ph - 20, center=True)

# ── PC Box screen ──────────────────────────────────────────────────────────────
class PCBoxScreen:
    """Move Pokémon between team and PC box."""

    def __init__(self, save_data, team):
        self.save   = save_data
        self.team   = team   # live list – modifications here affect the game
        self.search = ""
        self.searching = False
        # panel: 0=team, 1=box
        self.panel  = 0
        self.sel    = [0, 0]   # sel index per panel
        self.msg    = ""

    def _box_names(self):
        """Names in PC box that are NOT currently in the active team."""
        team_names = {m.name for m in self.team}
        raw = self.save.get("pc_box", [])
        # Deduplicate and exclude anything already in team
        seen = set()
        pool = []
        for n in raw:
            if n not in team_names and n not in seen:
                seen.add(n)
                pool.append(n)
        if self.search:
            pool = [n for n in pool if self.search.lower() in n.lower()]
        return pool

    def _team_list(self):
        if self.search:
            return [m for m in self.team if self.search.lower() in m.name.lower()]
        return list(self.team)

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
        if k == pygame.K_TAB or k == pygame.K_LEFT or k == pygame.K_RIGHT:
            self.panel = 1 - self.panel
            return None

        # Vertical navigation within current panel
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

        if self.panel == 0:   # team → box
            if not team_list:
                return
            idx = min(self.sel[0], len(team_list)-1)
            mon = team_list[idx]
            if len(self.team) <= 1:
                self.msg = "Du kannst nicht dein letztes Pokémon in die Box!"
                return
            self.team.remove(mon)
            # Add to pc_box if not already there
            pc = self.save.get("pc_box", [])
            if mon.name not in pc:
                pc.append(mon.name)
            self.save["pc_box"] = pc
            self.save["team"] = [m.name for m in self.team]
            self.msg = f"{mon.name} in die Box gelegt."
            self.sel[0] = min(self.sel[0], max(0, len(self.team)-1))

        else:   # box → team
            if not box_names:
                return
            idx = min(self.sel[1], len(box_names)-1)
            name = box_names[idx]
            if len(self.team) >= 6:
                self.msg = "Team ist voll! (max 6)"
                return
            m = get_moonie(name)
            self.team.append(m)
            self.save["team"] = [m.name for m in self.team]
            self.msg = f"{name} ins Team geholt."
            self.sel[1] = min(self.sel[1], max(0, len(self._box_names())-1))

    def draw(self, surf):
        surf.fill((10, 14, 26))
        # Header
        draw_rounded_rect(surf, C_PANEL, (0, 0, SW, 50), 0)
        draw_text(surf, "PC Box", F_BIG, C_YELLOW, SW//2, 4, center=True, shadow=True)
        draw_text(surf, "TAB/←→ Panel wechseln  ↑↓ navigieren  ENTER Transfer  S Suche  ESC zurück", F_TINY, C_GRAY, SW//2, 36, center=True)

        # Search bar
        sy = 52
        if self.searching or self.search:
            bar_col = C_BLUE if self.searching else (50, 50, 70)
            draw_rounded_rect(surf, bar_col, (SW//2-200, sy, 400, 26), 7, 2, C_YELLOW if self.searching else C_GRAY)
            cursor = "|" if self.searching and int(time.time()*2)%2 == 0 else ""
            draw_text(surf, f"Suche: {self.search}{cursor}", F_SMALL, C_WHITE, SW//2, sy+5, center=True)
            sy += 28

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

        # Status message
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

        # Left: list
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

            # Type badges
            tx = 82
            for t in m.types[:2]:
                tc = TYPE_COLORS.get(t, (150,150,150))
                pygame.draw.rect(surf, tc, (tx, y + 68, 52, 12), border_radius=6)
                draw_text(surf, t[:5], F_TINY, C_WHITE, tx+26, y+69, center=True)
                tx += 56

        # Right: detail panel for selected
        if self.sel < len(self.team):
            m = self.team[self.sel]
            px, py_d, pw, ph = 308, 54, SW - 320, SH - 66
            draw_rounded_rect(surf, C_PANEL, (px, py_d, pw, ph), 14, 2, C_BLUE)

            # Big image
            img = load_img(m.image, (140, 140))
            bob = int(math.sin(self.anim_t * 0.06) * 5)
            surf.blit(img, (px + pw//2 - 70, py_d + 10 + bob))

            cy = py_d + 158
            draw_text(surf, m.name, F_BIG, C_WHITE, px + pw//2, cy, center=True, shadow=True)
            cy += 36

            # Rarity
            rc = m.get_rarity_color()
            draw_text(surf, m.rarity.capitalize(), F_SMALL, rc, px + pw//2, cy, center=True)
            cy += 24

            # Types
            tw = len(m.types) * 72
            tx = px + pw//2 - tw//2
            for t in m.types:
                draw_type_badge(surf, t, tx, cy)
                tx += 72
            cy += 26

            # Stats bars
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

            # Evolution info
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
        self.mode = "items"  # items | pick_target

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        if self.mode == "items":
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.sel_item = max(0, self.sel_item - 1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.sel_item = min(1, self.sel_item + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                # Check if we have the item
                if self.sel_item == 0 and self.save.get("potions",0) > 0:
                    self.mode = "pick_target"
                    self.sel_mon = 0
                elif self.sel_item == 1 and self.save.get("super_potions",0) > 0:
                    self.mode = "pick_target"
                    self.sel_mon = 0
                else:
                    notify("Keinen Trank mehr!", C_RED)
            elif event.key in (pygame.K_ESCAPE, pygame.K_x, pygame.K_i):
                return "close"
        elif self.mode == "pick_target":
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.sel_mon = max(0, self.sel_mon - 1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.sel_mon = min(len(self.team)-1, self.sel_mon + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                self._use_item()
            elif event.key in (pygame.K_ESCAPE, pygame.K_x):
                self.mode = "items"
        return None

    def _use_item(self):
        m = self.team[self.sel_mon] if self.sel_mon < len(self.team) else None
        if not m: return
        if self.sel_item == 0:  # potion
            self.save["potions"] -= 1
            m.heal(30)
            notify(f"{m.name} +30 HP geheilt! ({self.save['potions']} übrig)", C_GREEN)
        elif self.sel_item == 1:  # super potion
            self.save["super_potions"] -= 1
            m.heal(80)
            notify(f"{m.name} +80 HP geheilt! ({self.save['super_potions']} übrig)", C_GREEN)
        self.mode = "items"

    def draw(self, surf):
        surf.fill((12, 16, 28))
        draw_rounded_rect(surf, C_PANEL, (0, 0, SW, 44), 0)
        draw_text(surf, "Item-Beutel", F_BIG, C_YELLOW, SW//2, 6, center=True, shadow=True)
        draw_text(surf, "[ I / ESC ] zurück", F_TINY, C_GRAY, SW//2, 32, center=True)

        # Items list
        items = [
            {"name": "Trank",       "key": "potions",       "heal": 30,  "col": (100,200,130)},
            {"name": "Super Trank", "key": "super_potions", "heal": 80,  "col": (80,160,255)},
        ]
        ix = 40
        for i, item in enumerate(items):
            count = self.save.get(item["key"], 0)
            sel = (i == self.sel_item) and self.mode == "items"
            bg = (40,60,100) if sel else C_PANEL
            draw_rounded_rect(surf, bg, (ix, 60, 360, 70), 12, 2 if sel else 1, C_YELLOW if sel else C_GRAY)
            draw_text(surf, item["name"], F_MED, item["col"], ix+16, 70, shadow=True)
            draw_text(surf, f"+{item['heal']} HP", F_SMALL, C_GRAY, ix+16, 96)
            count_col = C_WHITE if count > 0 else C_RED
            draw_text(surf, f"x{count}", F_BIG, count_col, ix+320, 77, center=True)
            ix = 440

        if self.mode == "items":
            draw_text(surf, "↑↓ wählen   ENTER benutzen", F_SMALL, C_GRAY, SW//2, 160, center=True)
        else:
            draw_text(surf, "Welches Moonie heilen?", F_MED, C_YELLOW, SW//2, 155, center=True)

        # Team list
        for i, m in enumerate(self.team):
            y = 180 + i * 78
            sel = (i == self.sel_mon) and self.mode == "pick_target"
            bg = (40,80,50) if sel else (28,32,45)
            draw_rounded_rect(surf, bg, (40, y, SW-80, 70), 10, 2 if sel else 1, C_GREEN if sel else (55,60,75))
            img = load_img(m.image, (48, 48))
            surf.blit(img, (52, y+11))
            draw_text(surf, m.name, F_MED, C_WHITE, 112, y+12)
            draw_text(surf, f"Lv {m.level}", F_TINY, C_GRAY, 112, y+34)
            draw_hp_bar(surf, 220, y+26, 380, 12, m.current_hp, m.max_hp)
            hp_col = C_RED if m.current_hp < m.max_hp * 0.3 else C_WHITE
            draw_text(surf, f"{m.current_hp}/{m.max_hp}", F_TINY, hp_col, 615, y+26)

        draw_notifications(surf)

# ── Evolution screen ───────────────────────────────────────────────────────────
class EvolutionScreen:
    def __init__(self, old_name, new_name, team):
        self.old_name = old_name
        self.new_name = new_name
        self.team = team
        self.anim_t = 0
        self.phase = "flash"  # flash | show | done

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
            # Glow
            glow = pygame.Surface((220, 220), pygame.SRCALPHA)
            pulse = abs(math.sin(t * 0.05))
            pygame.draw.circle(glow, (255,220,50, int(80*pulse)), (110,110), 110)
            surf.blit(glow, (SW//2-110, 130))
            draw_text(surf, f"{self.old_name} wurde zu", F_MED, C_GRAY, SW//2, 360, center=True)
            draw_text(surf, self.new_name + "!", F_HUGE, C_YELLOW, SW//2, 390, center=True, shadow=True)
            draw_text(surf, "[ beliebige Taste ]", F_SMALL, C_GRAY, SW//2, 460, center=True)
        add_particles(SW//2, 300, (255,220,80), n=2, size=5)
        update_particles(surf)

# ── Achievement screen ────────────────────────────────────────────────────────
class AchievementScreen:
    CATEGORIES = ["Alle", "Fangen", "Typen", "Kämpfe", "Lernen", "Abenteuer", "Pokédex"]

    def __init__(self, save, flashcards, all_moonies):
        self.save       = save
        self.flashcards = flashcards
        self.all_moonies= all_moonies
        self.cat_sel    = 0   # selected category tab
        self.scroll     = 0   # vertical scroll offset
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

        # Header
        draw_rounded_rect(surf, C_PANEL, (0, 0, SW, 48), 0)
        draw_text(surf, "Achievements", F_BIG, C_YELLOW, SW//2, 5, center=True, shadow=True)

        # Count unlocked
        all_status = ach_module.get_all_status(self.save, self.flashcards, self.all_moonies)
        total_tiers  = sum(len(a["milestones"]) for a,_,_ in all_status)
        unlocked_cnt = sum(t+1 for _,_,t in all_status if t >= 0)
        draw_text(surf, f"{unlocked_cnt}/{total_tiers} freigeschaltet   ESC zurück   ◄► Kategorie   ↑↓ scrollen",
                  F_TINY, C_GRAY, SW//2, 33, center=True)

        # Category tabs
        tab_w = SW // len(self.CATEGORIES)
        for i, cat in enumerate(self.CATEGORIES):
            sel = (i == self.cat_sel)
            bg  = (40, 60, 120) if sel else (25, 28, 45)
            bdr = C_YELLOW if sel else (50, 55, 75)
            draw_rounded_rect(surf, bg, (i*tab_w+2, 50, tab_w-4, 24), 6, 2 if sel else 1, bdr)
            draw_text(surf, cat, F_TINY, C_YELLOW if sel else C_GRAY, i*tab_w + tab_w//2, 56, center=True)

        # Filter by category
        cat_filter = self.CATEGORIES[self.cat_sel]
        if cat_filter == "Alle":
            visible = all_status
        else:
            visible = [(a,p,t) for a,p,t in all_status if a["category"] == cat_filter]

        # Draw achievement cards
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

            # Card bg
            if completed:
                bg = (30, 55, 30)
                bdr = C_GREEN
            elif has_any:
                bg = (35, 40, 60)
                bdr = C_BLUE
            else:
                bg = (20, 22, 35)
                bdr = (45, 48, 65)

            draw_rounded_rect(surf, bg, (10, cy, SW-20, card_h), 10, 2, bdr)

            # Icon + title
            draw_text(surf, a["icon"], F_BIG, C_WHITE, 28, cy+8)
            title_col = C_YELLOW if completed else (C_WHITE if has_any else C_GRAY)
            draw_text(surf, a["title"], F_MED, title_col, 60, cy+8, shadow=completed)
            draw_text(surf, a["desc"], F_TINY, C_GRAY, 60, cy+30)

            # Milestone badges
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

            # Progress bar toward next milestone
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

        # Clamp scroll
        self.scroll = min(self.scroll, max(0, len(visible) - 7))

        draw_notifications(surf)

# ── Shop screen ────────────────────────────────────────────────────────────────
class ShopScreen:
    ITEMS = [
        {"name": "Pokéball x5",   "cost": 50,  "desc": "Fange wilde Moonies (5 Stück)",  "key": "balls",   "amount": 5},
        {"name": "Trank",         "cost": 20,  "desc": "Heilt 30 HP (1 Stück)",          "key": "potions", "amount": 1, "heal": 30},
        {"name": "Super Trank",   "cost": 45,  "desc": "Heilt 80 HP (1 Stück)",          "key": "super_potions", "amount": 1, "heal": 80},
        {"name": "Trank x5",      "cost": 80,  "desc": "Heilt 30 HP (5 Stück)",          "key": "potions", "amount": 5, "heal": 30},
    ]

    def __init__(self, save_data, team):
        self.save = save_data
        self.team = team
        self.sel = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.sel = (self.sel-1) % len(self.ITEMS)
            elif event.key == pygame.K_DOWN:
                self.sel = (self.sel+1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                self.buy(self.sel)
            elif event.key in (pygame.K_ESCAPE, pygame.K_x):
                return "close"
        return None

    def buy(self, idx):
        item = self.ITEMS[idx]
        if item["key"] is None: return
        if self.save["coins"] < item["cost"]:
            notify("Nicht genug Münzen!", C_RED)
            return
        self.save["coins"] -= item["cost"]
        if item["key"] == "balls":
            self.save["balls"] = self.save.get("balls", 0) + item["amount"]
            notify(f"+{item['amount']} Pokébälle!", C_GREEN)
        elif item["key"] == "potions":
            self.save["potions"] = self.save.get("potions", 0) + item["amount"]
            notify(f"+{item['amount']} Tränke! (jetzt: {self.save['potions']})", C_GREEN)
        elif item["key"] == "super_potions":
            self.save["super_potions"] = self.save.get("super_potions", 0) + item["amount"]
            notify(f"+{item['amount']} Super Tränke! (jetzt: {self.save['super_potions']})", C_GREEN)

    def draw(self, surf):
        surf.fill(C_BG)
        shop_img = load_img("assets/shop.png", (SW, SH))
        surf.blit(shop_img, (0,0))
        # Semi-transparent panel
        panel = pygame.Surface((400, 400), pygame.SRCALPHA)
        panel.fill((15,18,28,220))
        surf.blit(panel, (50, 100))

        draw_text(surf, "Pokéstore", F_BIG, C_YELLOW, 250, 112, center=True, shadow=True)
        draw_text(surf, f"💰 {self.save['coins']} Münzen   🎯 {self.save.get('balls',0)} Bälle   💊 {self.save.get('potions',0)} Tr. / {self.save.get('super_potions',0)} STr.",
                  F_SMALL, C_WHITE, 250, 152, center=True)

        for i, item in enumerate(self.ITEMS):
            y = 185 + i*65
            sel = (i == self.sel)
            col = C_PANEL2 if not sel else C_BLUE
            draw_rounded_rect(surf, col, (65, y, 370, 55), 10, 2 if sel else 1, C_YELLOW if sel else C_GRAY)
            draw_text(surf, item["name"], F_MED, C_WHITE, 85, y+8, shadow=True)
            draw_text(surf, item["desc"], F_SMALL, C_GRAY, 85, y+32)
            if item["cost"] > 0:
                draw_text(surf, f"💰 {item['cost']}", F_MED, C_YELLOW, 380, y+16)

        draw_text(surf, "↑↓ wählen  ENTER kaufen  ESC zurück", F_TINY, C_GRAY, 250, 500, center=True)
        draw_notifications(surf)

# ── Pokémon Center screen ──────────────────────────────────────────────────────
class PokeCenterScreen:
    def __init__(self, save_data, team):
        self.save = save_data
        self.team = team
        self.healed = False
        self.anim_t = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key
        if k == pygame.K_ESCAPE or k == pygame.K_x or k == pygame.K_b:
            return "close"
        if k == pygame.K_RETURN or k == pygame.K_z or k == pygame.K_SPACE:
            if not self.healed:
                for m in self.team:
                    m.current_hp = m.max_hp
                self.healed = True
                notify("Team vollständig geheilt!", C_GREEN, 200)
            else:
                return "close"
        return None

    def draw(self, surf):
        center_img = load_img("assets/center.png", (SW, SH))
        surf.blit(center_img, (0, 0))

        # Dark overlay panel
        panel = pygame.Surface((440, 360), pygame.SRCALPHA)
        panel.fill((10, 14, 24, 220))
        surf.blit(panel, (SW//2 - 220, SH//2 - 200))

        draw_text(surf, "Pokémon Center", F_BIG, (255, 180, 220), SW//2, SH//2 - 192, center=True, shadow=True)
        draw_text(surf, "Willkommen! Wir heilen dein Team.", F_SMALL, C_WHITE, SW//2, SH//2 - 155, center=True)

        # Show team
        if self.team:
            tw = min(len(self.team), 3)
            cw = 120
            sx = SW//2 - (tw * (cw+8)) // 2
            for i, m in enumerate(self.team[:6]):
                col_x = sx + (i % 3) * (cw + 8)
                col_y = SH//2 - 120 + (i // 3) * 90
                draw_rounded_rect(surf, C_PANEL, (col_x, col_y, cw, 82), 8, 1, C_GREEN if m.current_hp == m.max_hp else C_RED)
                img = load_img(m.image, (44, 44))
                surf.blit(img, (col_x + 4, col_y + 4))
                draw_text(surf, m.name[:10], F_TINY, C_WHITE, col_x + cw//2, col_y + 52, center=True)
                draw_hp_bar(surf, col_x + 4, col_y + 68, cw - 8, 8, m.current_hp, m.max_hp, label=False)

        if not self.healed:
            draw_rounded_rect(surf, (40, 120, 60), (SW//2 - 200, SH//2 + 70, 190, 48), 12, 2, C_GREEN)
            draw_text(surf, "[ ENTER ] Heilen", F_SMALL, C_WHITE, SW//2 - 105, SH//2 + 84, center=True, shadow=True)
        else:
            self.anim_t += 1
            pulse = abs(math.sin(self.anim_t * 0.1))
            col = (int(80 + pulse*120), int(200 + pulse*50), int(80 + pulse*80))
            draw_text(surf, "✓ Team vollständig geheilt!", F_MED, col, SW//2, SH//2 + 80, center=True, shadow=True)
        # Always show exit button
        draw_rounded_rect(surf, (120, 40, 40), (SW//2 + 10, SH//2 + 70, 190, 48), 12, 2, C_RED)
        draw_text(surf, "[ ESC ] Verlassen", F_SMALL, C_WHITE, SW//2 + 105, SH//2 + 84, center=True, shadow=True)

        draw_notifications(surf)
# ── Overworld / Main map ───────────────────────────────────────────────────────
class OverworldScreen:
    GRASS_RECTS = [
        pygame.Rect(100, 210, 200, 170),
        pygame.Rect(500, 160, 240, 190),
        pygame.Rect(300, 390, 200, 150),
        pygame.Rect(650, 360, 170, 140),
        pygame.Rect(55, 430, 145, 115),
    ]
    SHOP_RECT   = pygame.Rect(20,  20, 130, 85)
    CENTER_RECT = pygame.Rect(170, 20, 130, 85)
    PC_RECT     = pygame.Rect(740, 30, 120, 75)
    ARENA_RECT  = pygame.Rect(SW//2 - 65, 25, 130, 85)  # arena in center-top
    MAX_TRAINERS = 4

    def __init__(self, save_data, flashcards):
        self.save = save_data
        self.cards = flashcards
        self.player_x = 450.0
        self.player_y = 350.0
        self.speed = 3.0
        self.step_anim = 0
        self.encounter_timer = 0
        self.trainer_cooldown = {}
        self.center_cooldown = 0
        self.pending_action = None
        self.in_grass = False
        self.grass_particle_t = 0
        self._ach_cb = None

        # Trainer spawning
        self._trainers = []
        self._spawn_timer = random.randint(180, 480)  # frames until next spawn check
        self._spawn_initial()

        # Raid state
        self.raid = None          # None or RaidData dict
        self.raid_timer = 0       # countdown in frames
        self._raid_spawn_timer = random.randint(1800, 5400)  # 30–90 sec until first raid

    def _spawn_initial(self):
        import addEnemy
        n = random.randint(1, self.MAX_TRAINERS)
        all_e = addEnemy.ALL_ENEMIES
        for _ in range(n):
            self._spawn_trainer(all_e)

    def _spawn_trainer(self, all_enemies=None):
        if len(self._trainers) >= self.MAX_TRAINERS:
            return
        if all_enemies is None:
            import addEnemy
            all_enemies = addEnemy.ALL_ENEMIES
        # 30% chance it's a Rocket member
        rockets = [e for e in all_enemies if e.isRocket]
        normals = [e for e in all_enemies if not e.isRocket]
        if random.random() < 0.3 and rockets:
            enemy = random.choice(rockets)
        else:
            enemy = random.choice(normals)
        # Pick spawn location away from player
        for _ in range(20):
            x = float(random.randint(80, SW-80))
            y = float(random.randint(130, SH-80))
            dist = math.sqrt((x-self.player_x)**2 + (y-self.player_y)**2)
            if dist > 200:
                break
        self._trainers.append({
            "enemy":      enemy,
            "x":          x,
            "y":          y,
            "vx":         random.choice([-1,1]) * random.uniform(0.5, 1.3),
            "vy":         random.choice([-1,1]) * random.uniform(0.5, 1.3),
            "move_t":     0,
            "move_dir_t": random.randint(80, 220),
            "alive":      True,
        })

    def get_trainer_img(self):
        path = "assets/trainer2.png" if self.save.get("trainer") == 1 else "assets/trainer.png"
        return load_img(path, (48, 64))

    def _update_trainers(self):
        for t in self._trainers:
            t["move_t"] += 1
            if t["move_t"] >= t["move_dir_t"]:
                t["move_t"] = 0
                t["move_dir_t"] = random.randint(60, 220)
                t["vx"] = random.choice([-1,1]) * random.uniform(0.4, 1.3)
                t["vy"] = random.choice([-1,1]) * random.uniform(0.4, 1.3)
            t["x"] += t["vx"]
            t["y"] += t["vy"]
            if t["x"] < 60 or t["x"] > SW - 60:
                t["vx"] *= -1
                t["x"] = max(60, min(SW-60, t["x"]))
            if t["y"] < 130 or t["y"] > SH - 80:
                t["vy"] *= -1
                t["y"] = max(130, min(SH-80, t["y"]))

        # Random spawn
        self._spawn_timer -= 1
        if self._spawn_timer <= 0:
            self._spawn_timer = random.randint(300, 900)  # 5–15 sec between spawns
            if len(self._trainers) < self.MAX_TRAINERS and random.random() < 0.7:
                self._spawn_trainer()

    def _despawn_trainer(self, idx):
        """Remove trainer at index after battle defeat."""
        if 0 <= idx < len(self._trainers):
            self._trainers.pop(idx)
            # Reschedule next spawn soon
            self._spawn_timer = min(self._spawn_timer, random.randint(300, 600))
            # Clean up cooldown keys
            new_cd = {}
            for k, v in self.trainer_cooldown.items():
                if k < idx:
                    new_cd[k] = v
                elif k > idx:
                    new_cd[k-1] = v
            self.trainer_cooldown = new_cd

    def _update_raid(self):
        """Tick raid spawn timer and raid countdown."""
        if self.raid is None:
            self._raid_spawn_timer -= 1
            if self._raid_spawn_timer <= 0:
                self._try_spawn_raid()
        else:
            self.raid_timer -= 1
            if self.raid_timer <= 0 and not self.raid.get("defeated"):
                # Raid expired
                add_particles(self.ARENA_RECT.centerx, self.ARENA_RECT.centery, (200,50,50), n=30)
                notify("Raid abgelaufen! Das Pokémon ist entkommen.", C_RED, 200)
                self.raid = None
                self._raid_spawn_timer = random.randint(1800, 7200)

    def _try_spawn_raid(self):
        """Pick a legendary/rare Pokémon and start a raid."""
        legendaries = [m for m in ALL_MOONIES_DICT.values() if m.rarity == "legendary"]
        rares = [m for m in ALL_MOONIES_DICT.values() if m.rarity == "rare"]
        pool = legendaries if legendaries else rares
        if not pool:
            return
        boss = random.choice(pool)
        level = random.randint(45, 60)
        cards_needed = random.randint(3, 8)  # must answer this many correctly during fight
        self.raid = {
            "name":          boss.name,
            "image":         boss.image,
            "level":         level,
            "cards_needed":  cards_needed,
            "defeated":      False,
            "can_catch":     False,
        }
        self.raid_timer = 60 * 60  # 60 seconds
        add_particles(self.ARENA_RECT.centerx, self.ARENA_RECT.centery, (255,200,50), n=50)
        notify(f"⚔ RAID erschienen! {boss.name} in der Arena! ({cards_needed} Lernkarten nötig)", C_YELLOW, 300)
        self._raid_spawn_timer = random.randint(3600, 10800)

    def handle_event(self, event):
        pass

    def update(self, keys):
        dx, dy = 0.0, 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += self.speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += self.speed

        if dx or dy:
            norm = math.sqrt(dx*dx+dy*dy)
            dx, dy = dx/norm*self.speed, dy/norm*self.speed
            self.player_x = max(20, min(SW-40, self.player_x + dx))
            self.player_y = max(115, min(SH-80, self.player_y + dy))
            self.step_anim += 1
            self.save["step_count"] = self.save.get("step_count",0) + 1
            if self.save["step_count"] % 100 == 0 and hasattr(self, '_ach_cb') and self._ach_cb:
                self._ach_cb()

        self._update_trainers()
        self._update_raid()

        pr = pygame.Rect(int(self.player_x)-12, int(self.player_y)-20, 24, 40)
        self.in_grass = any(g.colliderect(pr) for g in self.GRASS_RECTS)

        if self.in_grass:
            self.grass_particle_t += 1
            if self.encounter_timer > 0:
                self.encounter_timer -= 1
            elif (dx or dy) and random.random() < 0.008:
                self.encounter_timer = 120
                return "wild_encounter"

        if self.center_cooldown > 0:
            self.center_cooldown -= 1

        enter_pressed = keys[pygame.K_RETURN] or keys[pygame.K_z]
        if self.center_cooldown == 0 and pr.colliderect(self.SHOP_RECT):
            self.pending_action = "shop"
            if enter_pressed:
                return "shop"
        elif self.center_cooldown == 0 and pr.colliderect(self.CENTER_RECT):
            self.pending_action = "center"
            if enter_pressed:
                return "center"
        elif pr.colliderect(self.ARENA_RECT):
            self.pending_action = "arena"
            if enter_pressed and self.raid:
                if self.raid.get("can_catch") and not self.raid.get("catch_used"):
                    return "raid_catch"
                elif not self.raid.get("defeated"):
                    return "raid_battle"
        elif pr.colliderect(self.PC_RECT):
            self.pending_action = "pc"
        else:
            self.pending_action = None

        # Decrement trainer cooldowns
        for k in list(self.trainer_cooldown.keys()):
            self.trainer_cooldown[k] -= 1
            if self.trainer_cooldown[k] <= 0:
                del self.trainer_cooldown[k]

        for i, t in enumerate(self._trainers):
            if i in self.trainer_cooldown:
                continue
            tr = pygame.Rect(int(t["x"])-28, int(t["y"])-28, 56, 56)
            if pr.colliderect(tr):
                self.trainer_cooldown[i] = 300
                return f"trainer_{i}"

        return self.pending_action

    def draw(self, surf):
        surf.fill((45, 80, 45))
        for gx in range(0, SW, 40):
            pygame.draw.line(surf, (42,75,42), (gx,0),(gx,SH))
        for gy in range(0, SH, 40):
            pygame.draw.line(surf, (42,75,42), (0,gy),(SW,gy))

        grass_img = load_img("assets/grass.png", (40,40))
        for g in self.GRASS_RECTS:
            for gx in range(g.left, g.right, 40):
                for gy in range(g.top, g.bottom, 40):
                    surf.blit(grass_img, (gx, gy))
            if self.in_grass and self.grass_particle_t % 20 == 0:
                add_particles(g.centerx, g.centery, (80,180,80), n=3, size=4)

        # Buildings
        shop_img = load_img("assets/shop.png", (130, 85))
        surf.blit(shop_img, (self.SHOP_RECT.x, self.SHOP_RECT.y))
        draw_text(surf, "Shop", F_TINY, C_YELLOW, self.SHOP_RECT.centerx, self.SHOP_RECT.bottom + 3, center=True, shadow=True)

        center_img = load_img("assets/center.png", (130, 85))
        surf.blit(center_img, (self.CENTER_RECT.x, self.CENTER_RECT.y))
        draw_text(surf, "Pokecenter", F_TINY, (255,180,220), self.CENTER_RECT.centerx, self.CENTER_RECT.bottom + 3, center=True, shadow=True)

        # Arena building (center-top)
        arena_img = load_img("assets/arena.png", (130, 85))
        if self.raid:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
            glow_col = (80, 255, 120) if self.raid.get("can_catch") else (255, int(150+100*pulse), 0)
            glow = pygame.Surface((self.ARENA_RECT.width+20, self.ARENA_RECT.height+20), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*glow_col, int(60+80*pulse)), (0,0,self.ARENA_RECT.width+20, self.ARENA_RECT.height+20), border_radius=12)
            surf.blit(glow, (self.ARENA_RECT.x-10, self.ARENA_RECT.y-10))
        surf.blit(arena_img, (self.ARENA_RECT.x, self.ARENA_RECT.y))
        if self.raid:
            secs = self.raid_timer // 60
            if self.raid.get("can_catch"):
                draw_text(surf, f"⚡ {self.raid['name']}", F_TINY, C_GREEN, self.ARENA_RECT.centerx, self.ARENA_RECT.bottom+3, center=True, shadow=True)
                draw_text(surf, "Fangen bereit!", F_TINY, C_GREEN, self.ARENA_RECT.centerx, self.ARENA_RECT.bottom+14, center=True)
            else:
                draw_text(surf, f"⚡ RAID: {self.raid['name']}", F_TINY, C_YELLOW, self.ARENA_RECT.centerx, self.ARENA_RECT.bottom+3, center=True, shadow=True)
                timer_col = C_RED if secs < 15 else C_YELLOW
                draw_text(surf, f"{secs}s", F_TINY, timer_col, self.ARENA_RECT.centerx, self.ARENA_RECT.bottom+14, center=True)
        else:
            draw_text(surf, "Arena", F_TINY, C_GRAY, self.ARENA_RECT.centerx, self.ARENA_RECT.bottom + 3, center=True)

        # PC Building
        bw = 120
        draw_rounded_rect(surf, (30,50,90), (self.PC_RECT.x, self.PC_RECT.y, bw, self.PC_RECT.height), 10, 2, C_BLUE)
        draw_text(surf, "Pokédex", F_TINY, C_BLUE, self.PC_RECT.x + bw//2, self.PC_RECT.centery - 7, center=True)
        draw_text(surf, "[ B ]", F_TINY, C_GRAY, self.PC_RECT.x + bw//2, self.PC_RECT.centery + 9, center=True)
        draw_rounded_rect(surf, (30,80,60), (self.PC_RECT.x + bw + 6, self.PC_RECT.y, bw, self.PC_RECT.height), 10, 2, C_GREEN)
        draw_text(surf, "PC-Box", F_TINY, C_GREEN, self.PC_RECT.x + bw + 6 + bw//2, self.PC_RECT.centery - 7, center=True)
        draw_text(surf, "[ P ]", F_TINY, C_GRAY, self.PC_RECT.x + bw + 6 + bw//2, self.PC_RECT.centery + 9, center=True)

        # Interact prompts
        pr = pygame.Rect(int(self.player_x)-12, int(self.player_y)-20, 24, 40)
        if pr.colliderect(self.SHOP_RECT):
            draw_text(surf, "[ ENTER ] Shop betreten", F_SMALL, C_YELLOW, self.SHOP_RECT.centerx, self.SHOP_RECT.bottom + 18, center=True, shadow=True)
        if pr.colliderect(self.CENTER_RECT):
            draw_text(surf, "[ ENTER ] Pokecenter", F_SMALL, (255,220,240), self.CENTER_RECT.centerx, self.CENTER_RECT.bottom + 18, center=True, shadow=True)
        if pr.colliderect(self.ARENA_RECT):
            if self.raid and self.raid.get("can_catch") and not self.raid.get("catch_used"):
                draw_text(surf, "[ ENTER ] Raid-Pokémon fangen!", F_SMALL, C_GREEN, self.ARENA_RECT.centerx, self.ARENA_RECT.bottom+18, center=True, shadow=True)
            elif self.raid and not self.raid.get("defeated"):
                draw_text(surf, "[ ENTER ] Raid starten!", F_SMALL, C_YELLOW, self.ARENA_RECT.centerx, self.ARENA_RECT.bottom+18, center=True, shadow=True)
            elif self.raid and self.raid.get("catch_used"):
                draw_text(surf, "Raid abgeschlossen", F_SMALL, C_GRAY, self.ARENA_RECT.centerx, self.ARENA_RECT.bottom+18, center=True)
            else:
                draw_text(surf, "Kein aktiver Raid", F_SMALL, C_GRAY, self.ARENA_RECT.centerx, self.ARENA_RECT.bottom+18, center=True)

        # Roaming trainers
        for t in self._trainers:
            en = t["enemy"]
            img = load_img(en.image, (38, 50))
            surf.blit(img, (int(t["x"])-19, int(t["y"])-25))
            is_rocket = getattr(en, "isRocket", False)
            badge_col = C_ROCKET if is_rocket else C_ORANGE
            pygame.draw.circle(surf, badge_col, (int(t["x"]), int(t["y"])-30), 5)
            draw_text(surf, en.name[:8], F_TINY, C_WHITE, int(t["x"]), int(t["y"])+28, center=True, shadow=True)
            if is_rocket:
                draw_text(surf, "R", F_TINY, C_ROCKET, int(t["x"])+14, int(t["y"])-30)

        # Player
        bob = math.sin(self.step_anim * 0.3) * 3
        trainer = self.get_trainer_img()
        surf.blit(trainer, (int(self.player_x)-24, int(self.player_y)-32+int(bob)))
        pygame.draw.ellipse(surf, (0,0,0,80), pygame.Rect(int(self.player_x)-18, int(self.player_y)+24, 36, 10))

        # Top HUD bar
        draw_rounded_rect(surf, (15, 18, 28), (0, 0, SW, 32), 0, 1, (50, 55, 70))
        hud_items = [
            (f"🎯 Bälle: {self.save.get('balls',0)}", C_GREEN),
            (f"💊 Tränke: {self.save.get('potions',0)}", (180,230,180)),
            (f"⚡ S-Tränke: {self.save.get('super_potions',0)}", (140,200,255)),
            (f"💰 Coins: {self.save.get('coins',0)}", C_YELLOW),
            (f"🏅 Badges: {self.save.get('badges',0)}", C_ORANGE),
        ]
        hx = 8
        for txt, col in hud_items:
            draw_text(surf, txt, F_TINY, col, hx, 9)
            hx += 160

        # Raid HUD mini-panel (bottom left when active)
        if self.raid:
            secs = self.raid_timer // 60
            rx, ry, rw, rh = 8, SH-78, 290, 68
            bg_c = (20,50,20) if self.raid.get("can_catch") else (50,25,10)
            draw_rounded_rect(surf, bg_c, (rx, ry, rw, rh), 10, 2, C_YELLOW)
            draw_text(surf, f"⚔ RAID: {self.raid['name']}  Lv{self.raid.get('level','?')}", F_SMALL, C_YELLOW, rx+8, ry+6, shadow=True)
            if self.raid.get("can_catch"):
                draw_text(surf, "✓ Gewonnen! Geh zur Arena zum Fangen", F_TINY, C_GREEN, rx+8, ry+28)
            else:
                cards_n = self.raid.get("cards_needed", 0)
                cards_a = self.raid.get("cards_answered", 0)
                timer_c = C_RED if secs < 15 else (255,200,50)
                draw_text(surf, f"⏱ {secs}s   📚 Lernkarten: {cards_a}/{cards_n}", F_TINY, timer_c, rx+8, ry+28)
                bar_w = rw - 16
                pct = min(1.0, cards_a / max(1, cards_n))
                pygame.draw.rect(surf, (40,40,60), (rx+8, ry+46, bar_w, 10), border_radius=5)
                if pct > 0:
                    pygame.draw.rect(surf, C_BLUE, (rx+8, ry+46, int(bar_w*pct), 10), border_radius=5)

        # Button strip (top right)
        btns = [
            ("B", "Pokédex",      C_BLUE),
            ("P", "PC-Box",       C_GREEN),
            ("T", "Team",         C_ORANGE),
            ("I", "Items",        (180,120,220)),
            ("A", "Achievements", C_YELLOW),
        ]
        bx = SW - 8
        for key, label, col in reversed(btns):
            bw2 = len(label)*7 + 32
            bx -= bw2 + 4
            draw_rounded_rect(surf, (20, 24, 36), (bx, 4, bw2, 24), 6, 1, col)
            draw_text(surf, f"[{key}] {label}", F_TINY, col, bx + bw2//2, 10, center=True)

        update_particles(surf)
        draw_notifications(surf)

# ── Character select / new game ────────────────────────────────────────────────
class CharSelectScreen:
    STARTERS = ["Bisasam", "Glumanda", "Schiggy"]

    def __init__(self):
        self.trainer_sel = 0
        self.starter_sel = 0
        self.name = "Spieler"
        self.state = "pick"   # pick | name | starter | ready

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
                tx = SW//2 - 130 + i*260
                ty = 200
                sel = (i == self.trainer_sel)
                draw_rounded_rect(surf, C_PANEL2 if not sel else (40,60,120), (tx-70, ty, 140, 220), 16, 3 if sel else 1, C_YELLOW if sel else C_GRAY)
                img = load_img(f"assets/trainer{'' if i==0 else '2'}.png", (110, 160))
                surf.blit(img, (tx-55, ty+10))
                draw_text(surf, f"Trainer {i+1}", F_MED, C_WHITE, tx, ty+178, center=True)
            draw_text(surf, "◄ ►  wählen    ENTER  weiter", F_SMALL, C_GRAY, SW//2, 455, center=True)

        elif self.state == "name":
            draw_text(surf, "Wie ist dein Name?", F_BIG, C_WHITE, SW//2, 200, center=True)
            draw_rounded_rect(surf, C_DARK, (SW//2-160, 268, 320, 52), 10, 2, C_BLUE)
            cursor = "|" if int(time.time()*2)%2==0 else " "
            draw_text(surf, self.name + cursor, F_BIG, C_YELLOW, SW//2, 281, center=True)
            draw_text(surf, "ENTER bestätigen   ESC zurück", F_SMALL, C_GRAY, SW//2, 358, center=True)

        elif self.state == "starter":
            draw_text(surf, "Wähle dein Starter-Pokémon!", F_BIG, C_WHITE, SW//2, 120, center=True, shadow=True)
            draw_text(surf, "◄ ► wählen   ENTER bestätigen", F_SMALL, C_GRAY, SW//2, 156, center=True)
            for i, name in enumerate(self.STARTERS):
                m = ALL_MOONIES_DICT.get(name)
                if not m: continue
                tx = SW//2 - 260 + i * 260
                ty = 185
                sel = (i == self.starter_sel)
                bg = (40, 70, 120) if sel else C_PANEL
                border = C_YELLOW if sel else C_GRAY
                draw_rounded_rect(surf, bg, (tx-100, ty, 200, 280), 16, 3 if sel else 1, border)
                if sel:
                    glow = pygame.Surface((216, 296), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (255,220,50,50), (0,0,216,296), border_radius=18)
                    surf.blit(glow, (tx-108, ty-8))
                img = load_img(m.image, (130, 130))
                surf.blit(img, (tx-65, ty+12))
                r_col = m.get_rarity_color()
                pygame.draw.rect(surf, r_col, (tx-100, ty, 200, 8), border_radius=16)
                draw_text(surf, name, F_MED, C_WHITE, tx, ty+152, center=True, shadow=True)
                tw = len(m.types) * 70
                bx = tx - tw//2
                for t in m.types:
                    draw_type_badge(surf, t, bx, ty+178)
                    bx += 70
                draw_text(surf, f"HP: {m.max_hp}  Ang: {m.attack}", F_TINY, C_GRAY, tx, ty+204, center=True)
                if m.nextEvolution:
                    evo = m.nextEvolution if isinstance(m.nextEvolution, str) else "?"
                    draw_text(surf, f"→ {evo}", F_TINY, C_BLUE, tx, ty+222, center=True)

        elif self.state == "ready":
            name = self.STARTERS[self.starter_sel]
            m = ALL_MOONIES_DICT.get(name)
            if m:
                img = load_img(m.image, (160, 160))
                surf.blit(img, (SW//2-80, 160))
            draw_text(surf, f"Du hast {name} gewählt!", F_BIG, C_YELLOW, SW//2, 340, center=True, shadow=True)
            draw_text(surf, f"Viel Erfolg, {self.name}!", F_MED, C_WHITE, SW//2, 385, center=True)
            draw_text(surf, "ENTER  Abenteuer beginnen!", F_MED, C_GREEN, SW//2, 435, center=True)
            draw_text(surf, "ESC  zurück", F_TINY, C_GRAY, SW//2, 475, center=True)

        draw_notifications(surf)

# ── Title screen ───────────────────────────────────────────────────────────────
class TitleScreen:
    def __init__(self, has_save):
        self.has_save = has_save
        self.t = 0
        self.options = ["Neues Spiel", "Spiel laden", "Beenden"] if has_save else ["Neues Spiel", "Beenden"]
        self.sel = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.sel = (self.sel-1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.sel = (self.sel+1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                return self.options[self.sel]
        return None

    def draw(self, surf):
        self.t += 1
        # Animated bg
        surf.fill(C_BG)
        for i in range(30):
            r = random.Random(i+1000)
            px = r.randint(0,SW)
            py = r.randint(0,SH)
            size = r.randint(2,6)
            alpha = int(128 + 60*math.sin(self.t*0.03 + r.random()*6.28))
            s = pygame.Surface((size*2,size*2), pygame.SRCALPHA)
            pygame.draw.circle(s,(200,200,255,alpha),(size,size),size)
            surf.blit(s,(px,py))

        # Logo
        logo_y = 80 + math.sin(self.t*0.04)*8
        draw_text(surf, "MoonieQuest", F_HUGE, C_YELLOW, SW//2, logo_y, center=True, shadow=True)
        draw_text(surf, "AP2 Edition", F_BIG, C_BLUE, SW//2, logo_y+70, center=True)

        # Moonie showcase
        showcase = ["glumanda","bisasam","schiggy","evoli","pikachu"]
        for i, name in enumerate(showcase):
            img = load_img(f"assets/moonie/{name}.png", (80,80))
            sx = SW//2 - len(showcase)*50 + i*100
            sy = 230 + math.sin(self.t*0.05 + i)*12
            surf.blit(img, (sx-40, sy))

        # Menu
        for i, opt in enumerate(self.options):
            sel = (i == self.sel)
            col = C_YELLOW if sel else C_WHITE
            by = 380 + i*62
            bw = 300
            draw_rounded_rect(surf, C_PANEL if not sel else (40,60,120), (SW//2-bw//2, by, bw, 50), 14, 2 if sel else 1, C_YELLOW if sel else C_GRAY)
            draw_text(surf, ("► " if sel else "  ") + opt, F_BIG, col, SW//2, by+9, center=True, shadow=True)

        draw_text(surf, "↑↓  ENTER", F_SMALL, C_GRAY, SW//2, SH-30, center=True)
        draw_notifications(surf)

# ── Main game manager ──────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.flashcards = load_flashcards(os.path.join(BASE, "flashcards.csv"))
        random.shuffle(self.flashcards)
        self.save = None
        self.team = []
        self.screen_state = "title"  # title | char_select | overworld | battle | shop | pokedex | center
        self.title_screen = TitleScreen(os.path.exists(SAVE_FILE))
        self.char_select   = None
        self.overworld     = None
        self.battle        = None
        self.shop          = None
        self.pokedex       = None
        self.center        = None
        self.team_screen   = None
        self.item_bag      = None
        self.evo_screen    = None
        self.pc_box_screen = None
        self.ach_screen    = None
        self.prev_state    = None

    def _trigger_achievements(self):
        """Check all achievements and fire notifications for newly unlocked ones."""
        newly = ach_module.check_achievements(self.save, self.flashcards, ALL_MOONIES_DICT)
        for aid, tier_label, title, reward, icon in newly:
            msg = f"{icon} Achievement: {title} – {tier_label}!"
            if reward > 0:
                msg += f"  +{reward} Coins"
            notify(msg, C_YELLOW, 300)

    def start_new_game(self, save_data):
        self.save = save_data
        starter_name = save_data.get("starter", "Bisasam")
        starter = get_moonie(starter_name)
        self.team = [starter]
        self.save["team"] = [starter_name]
        # Register starter in pc_box so the Pokédex shows it as "seen/caught".
        # It is NOT physically in the box — _box_names() excludes team members,
        # so it won't appear as a second copy in the PC Box screen.
        pc = self.save.get("pc_box", [])
        if starter_name not in pc:
            pc.append(starter_name)
        self.save["pc_box"] = pc
        self.overworld = OverworldScreen(self.save, self.flashcards)
        self.overworld._ach_cb = self._trigger_achievements
        self.screen_state = "overworld"
        FlashcardGame._save_ref = self.save
        notify(f"Willkommen, {self.save['name']}! Viel Erfolg mit {starter_name}!", C_YELLOW, 180)

    def load_existing_game(self):
        self.save = load_game()
        if self.save is None:
            self.save = default_save()
        team_names = self.save.get("team", ["Bisasam","Glumanda","Schiggy"])
        self.team = [get_moonie(n) for n in team_names]
        if not self.team:
            self.team = [get_moonie("Bisasam")]
        self.overworld = OverworldScreen(self.save, self.flashcards)
        self.overworld._ach_cb = self._trigger_achievements
        self.screen_state = "overworld"
        FlashcardGame._save_ref = self.save
        notify("Spiel geladen!", C_GREEN)

    def start_wild_battle(self):
        # Pick wild moonie based on step count
        step = self.save.get("step_count", 0)
        rarity = "common" if step < 500 else "uncommon" if step < 2000 else "rare"
        pool = get_wild_pool([rarity])
        wild = random.choice(pool).clone_for_battle()
        # Scale to rough area level
        wild.level = max(1, min(50, step // 40 + random.randint(1, 5)))
        wild.max_hp = wild.max_hp + wild.level * 2
        wild.current_hp = wild.max_hp
        self.battle = Battle(self.team, None, wild_moonie=wild,
                             flashcards=self.flashcards, is_wild=True)
        self.battle.save_data_ref = self.save
        self.screen_state = "battle"

    def start_trainer_battle(self, trainer_idx):
        if not self.overworld or trainer_idx >= len(self.overworld._trainers):
            return
        t = self.overworld._trainers[trainer_idx]
        en = t["enemy"]
        # Rocket members get +2 strength bonus
        if getattr(en, "isRocket", False):
            import copy
            en = copy.copy(en)
            en.strenght = getattr(en, 'strenght', 2) + 2
        self.battle = Battle(self.team, en, flashcards=self.flashcards, is_wild=False)
        self.battle.save_data_ref = self.save
        self.battle._trainer_idx = trainer_idx   # remember for despawn
        self.screen_state = "battle"
        # Push trainer away
        t["vx"] = random.choice([-1, 1]) * 2.5
        t["vy"] = random.choice([-1, 1]) * 2.5
        t["move_dir_t"] = 180

    def start_raid_battle(self):
        if not self.overworld or not self.overworld.raid:
            return
        raid = self.overworld.raid
        m = ALL_MOONIES_DICT.get(raid["name"])
        if not m:
            return
        boss = m.clone_for_battle()
        boss.level = raid["level"]
        boss.max_hp = boss.max_hp + boss.level * 5
        boss.attack = boss.attack + boss.level * 2
        boss.current_hp = boss.max_hp
        self.battle = Battle(self.team, None, wild_moonie=boss, flashcards=self.flashcards, is_wild=True)
        self.battle.save_data_ref = self.save
        self.battle.raid_cards_needed = raid["cards_needed"]
        self.battle.raid_cards_answered = 0
        self.battle._is_raid = True
        self.battle.overworld_ref = self.overworld
        # Force flashcards during raid (always show flashcard before attack)
        self.screen_state = "battle"
        notify(f"⚔ RAID-KAMPF gegen {boss.name} Lv{boss.level}! Beantworte {raid['cards_needed']} Lernkarten!", C_YELLOW, 240)

    def start_raid_catch(self):
        """Start a wild catch attempt for the raid boss."""
        if not self.overworld or not self.overworld.raid:
            return
        raid = self.overworld.raid
        if not raid.get("can_catch") or raid.get("catch_used"):
            return
        m = ALL_MOONIES_DICT.get(raid["name"])
        if not m:
            return
        boss = m.clone_for_battle()
        boss.level = raid["level"]
        boss.max_hp = 1   # very low hp so catch is possible
        boss.current_hp = 1
        boss.catch_rate = 0.5
        self.battle = Battle(self.team, None, wild_moonie=boss, flashcards=self.flashcards, is_wild=True)
        self.battle.save_data_ref = self.save
        self.battle._is_raid_catch = True
        self.overworld.raid["catch_used"] = True
        self.screen_state = "battle"
        notify(f"Fangversuch: {boss.name}!", C_GREEN, 180)

    def end_battle(self):
        result = self.battle.result
        is_trainer = not self.battle.is_wild
        is_rocket  = is_trainer and getattr(self.battle.enemy_data, 'isRocket', False)

        if result == "win":
            self.save["battles_won"] = self.save.get("battles_won",0) + 1
            self.save["coins"] = self.save.get("coins",0) + self.battle.coins_reward
            if self.save["battles_won"] % 5 == 0:
                self.save["badges"] = self.save.get("badges",0) + 1
                notify("Neues Abzeichen erhalten! 🏅", C_YELLOW, 200)
            self.save["cards_known"] = sum(1 for c in self.flashcards if c.get("known"))
            # Track trainer/rocket wins separately
            if is_trainer:
                self.save["trainer_battles_won"] = self.save.get("trainer_battles_won",0) + 1
                # Despawn the defeated trainer
                tidx = getattr(self.battle, '_trainer_idx', None)
                if tidx is not None and self.overworld:
                    self.overworld._despawn_trainer(tidx)
            if is_rocket:
                self.save["rocket_battles_won"] = self.save.get("rocket_battles_won",0) + 1
            # Handle raid boss defeat
            if getattr(self.battle, '_is_raid', False) and self.overworld and self.overworld.raid:
                raid = self.overworld.raid
                cards_ok = self.battle.raid_cards_answered >= self.battle.raid_cards_needed
                if cards_ok:
                    raid["defeated"] = True
                    raid["can_catch"] = True
                    notify(f"⚔ RAID gewonnen! {raid['name']} kann jetzt gefangen werden! → Arena", C_GREEN, 300)
                else:
                    raid["defeated"] = True
                    raid["can_catch"] = False
                    needed = self.battle.raid_cards_needed
                    got = self.battle.raid_cards_answered
                    notify(f"Raid gewonnen, aber nur {got}/{needed} Lernkarten! Kein Fangen möglich.", C_RED, 300)
            # Check evolutions
            self._pending_evos = []
            for m in self.team:
                if m.can_evolve() and m.nextEvolution:
                    evo_name = m.nextEvolution if isinstance(m.nextEvolution, str) else None
                    if evo_name and evo_name in ALL_MOONIES_DICT:
                        self._pending_evos.append((m.name, evo_name))
                        new_m = get_moonie(evo_name)
                        new_m.level = m.level
                        new_m.xp = m.xp
                        new_m.max_hp  = max(new_m.max_hp, m.max_hp + 10)
                        new_m.attack  = max(new_m.attack, m.attack + 5)
                        new_m.current_hp = new_m.max_hp
                        self.team[self.team.index(m)] = new_m
                        self.save["evolution_count"] = self.save.get("evolution_count",0) + 1
        elif result == "catch":
            caught_name = self.battle.enemy_moonie.name if self.battle.enemy_moonie else "Unbekannt"
            pc = self.save.get("pc_box", [])
            if caught_name not in pc:
                pc.append(caught_name)
            self.save["pc_box"] = pc
            self.save["total_catches"] = self.save.get("total_catches",0) + 1
            notify(f"{caught_name} wurde zum PC hinzugefügt!", C_GREEN, 160)
        elif result == "lose":
            for m in self.team:
                m.current_hp = m.max_hp
            notify("Du wachst im Pokécenter auf. Team vollständig geheilt!", C_RED, 200)
            # If this was a raid battle, mark it as failed so we don't re-enter
            if getattr(self.battle, '_is_raid', False) and self.overworld and self.overworld.raid:
                self.overworld.raid["defeated"] = True
                self.overworld.raid["can_catch"] = False
                notify("Raid verloren! Das Pokémon ist entkommen.", C_RED, 240)
        elif result == "andreas":
            notify("Psycho Andreas hat das Moonie gestohlen! 😤", (255,80,255), 200)

        # ── Check achievements ──────────────────────────────────────────────
        self._trigger_achievements()

        # Save after battle
        self.save["team"] = [m.name for m in self.team]
        save_game(self.save)
        self.battle = None
        # Check for pending evolutions
        if hasattr(self, '_pending_evos') and self._pending_evos:
            old_n, new_n = self._pending_evos.pop(0)
            self.evo_screen = EvolutionScreen(old_n, new_n, self.team)
            self.screen_state = "evolution"
            return
        self.screen_state = "overworld"

    def run(self):
        global shake_timer
        running = True
        while running:
            dt = clock.tick(FPS)
            keys = pygame.key.get_pressed()
            ox, oy = get_shake_offset()
            if shake_timer > 0:
                shake_timer -= 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                # ── Title ──
                if self.screen_state == "title":
                    result = self.title_screen.handle_event(event)
                    if result == "Neues Spiel":
                        self.char_select = CharSelectScreen()
                        self.screen_state = "char_select"
                    elif result == "Spiel laden":
                        self.load_existing_game()
                    elif result == "Beenden":
                        running = False

                # ── Char select ──
                elif self.screen_state == "char_select":
                    result = self.char_select.handle_event(event)
                    if result == "start":
                        sd = default_save()
                        sd["trainer"] = self.char_select.trainer_sel
                        sd["name"]    = self.char_select.name
                        sd["starter"] = self.char_select.STARTERS[self.char_select.starter_sel]
                        self.start_new_game(sd)

                # ── Overworld ──
                elif self.screen_state == "overworld":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_b:
                            self.pokedex = PokedexScreen(self.save.get("pc_box", []))
                            self.screen_state = "pokedex"
                        elif event.key == pygame.K_p:
                            self.pc_box_screen = PCBoxScreen(self.save, self.team)
                            self.screen_state = "pcbox"
                        elif event.key == pygame.K_a:
                            self.ach_screen = AchievementScreen(self.save, self.flashcards, ALL_MOONIES_DICT)
                            self.screen_state = "achievements"
                        elif event.key == pygame.K_t:
                            self.team_screen = TeamScreen(self.team, self.save)
                            self.screen_state = "team"
                        elif event.key == pygame.K_i:
                            self.item_bag = ItemBagScreen(self.save, self.team)
                            self.screen_state = "itembag"
                        elif event.key == pygame.K_ESCAPE:
                            save_game(self.save)
                            notify("Spiel gespeichert!", C_GREEN)

                # ── Battle ──
                elif self.screen_state == "battle" and self.battle:
                    self.battle.handle_event(event, self.save)

                # ── Shop ──
                elif self.screen_state == "shop" and self.shop:
                    result = self.shop.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"
                        self.overworld.center_cooldown = 90

                # ── Pokécenter ──
                elif self.screen_state == "center" and self.center:
                    result = self.center.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"
                        self.overworld.center_cooldown = 90  # prevent immediate re-entry

                # ── Team ──
                elif self.screen_state == "team" and self.team_screen:
                    result = self.team_screen.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"

                # ── Item Bag ──
                elif self.screen_state == "itembag" and self.item_bag:
                    result = self.item_bag.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"

                # ── PC Box ──
                elif self.screen_state == "pcbox" and self.pc_box_screen:
                    result = self.pc_box_screen.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"

                # ── Achievements ──
                elif self.screen_state == "achievements" and self.ach_screen:
                    result = self.ach_screen.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"

                # ── Evolution ──
                elif self.screen_state == "evolution" and self.evo_screen:
                    result = self.evo_screen.handle_event(event)
                    if result == "done":
                        self.evo_screen = None
                        # More evolutions pending?
                        if hasattr(self, '_pending_evos') and self._pending_evos:
                            old_n, new_n = self._pending_evos.pop(0)
                            self.evo_screen = EvolutionScreen(old_n, new_n, self.team)
                            self.screen_state = "evolution"
                        else:
                            self.screen_state = "overworld"

                # ── Pokedex ──
                elif self.screen_state == "pokedex" and self.pokedex:
                    result = self.pokedex.handle_event(event)
                    if result == "close":
                        self.screen_state = "overworld"

            # ── Per-frame updates ──
            if self.screen_state == "overworld" and self.overworld:
                action = self.overworld.update(keys)
                if action == "wild_encounter":
                    self.start_wild_battle()
                elif action == "shop":
                    self.shop = ShopScreen(self.save, self.team)
                    self.screen_state = "shop"
                elif action == "center":
                    self.center = PokeCenterScreen(self.save, self.team)
                    self.screen_state = "center"
                elif action and action.startswith("trainer_"):
                    idx = int(action.split("_")[1])
                    self.start_trainer_battle(idx)
                elif action == "raid_battle":
                    self.start_raid_battle()
                elif action == "raid_catch":
                    self.start_raid_catch()

            elif self.screen_state == "battle" and self.battle:
                self.battle.update()
                if self.battle.state == "done":
                    self.end_battle()

            elif self.screen_state == "evolution" and self.evo_screen:
                self.evo_screen.update()

            # ── Drawing ──
            surface = screen
            if self.screen_state == "title":
                self.title_screen.draw(surface)
            elif self.screen_state == "char_select":
                self.char_select.draw(surface)
            elif self.screen_state == "overworld" and self.overworld:
                self.overworld.draw(surface)
            elif self.screen_state == "battle" and self.battle:
                self.battle.draw(surface)
            elif self.screen_state == "shop" and self.shop:
                self.shop.draw(surface)
            elif self.screen_state == "center" and self.center:
                self.center.draw(surface)
            elif self.screen_state == "team" and self.team_screen:
                self.team_screen.draw(surface)
            elif self.screen_state == "itembag" and self.item_bag:
                self.item_bag.draw(surface)
            elif self.screen_state == "evolution" and self.evo_screen:
                self.evo_screen.draw(surface)
            elif self.screen_state == "pcbox" and self.pc_box_screen:
                self.pc_box_screen.draw(surface)
            elif self.screen_state == "achievements" and self.ach_screen:
                self.ach_screen.draw(surface)
            elif self.screen_state == "pokedex" and self.pokedex:
                self.pokedex.draw(surface)
            else:
                surface.fill(C_BG)

            pygame.display.flip()

        # Final save
        if self.save:
            save_game(self.save)
        pygame.quit()
        sys.exit()

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    game = Game()
    game.run()