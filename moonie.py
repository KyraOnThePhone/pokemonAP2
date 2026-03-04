import random

TYPE_COLORS = {
    "Normal":   (168, 168, 120),
    "Feuer":    (240, 128, 48),
    "Wasser":   (104, 144, 240),
    "Pflanze":  (120, 200, 80),
    "Elektro":  (248, 208, 48),
    "Eis":      (152, 216, 216),
    "Kampf":    (192, 48, 40),
    "Gift":     (160, 64, 160),
    "Boden":    (224, 192, 104),
    "Flug":     (168, 144, 240),
    "Psycho":   (248, 88, 136),
    "Käfer":    (168, 184, 32),
    "Gestein":  (184, 160, 56),
    "Geist":    (112, 88, 152),
    "Drache":   (112, 56, 248),
    "Unlicht":  (112, 88, 72),
    "Stahl":    (184, 184, 208),
    "Fee":      (238, 153, 172),
}

RARITY_COLORS = {
    "common":    (180, 180, 180),
    "uncommon":  (80, 200, 80),
    "rare":      (80, 80, 220),
    "epic":      (160, 32, 240),
    "legendary": (255, 165, 0),
    "":          (180, 180, 180),
}

RARITY_CATCH_RATE = {
    "common":    0.70,
    "uncommon":  0.45,
    "rare":      0.25,
    "epic":      0.12,
    "legendary": 0.05,
    "":          0.50,
}

# ── Typ-Effektivität ──────────────────────────────────────────────────────────
# effectiveness[Angreifer-Typ][Verteidiger-Typ] = Multiplikator
TYPE_EFFECTIVENESS = {
    "Feuer":   {"Pflanze":2, "Eis":2, "Käfer":2, "Stahl":2,  "Wasser":0.5, "Feuer":0.5, "Gestein":0.5, "Drache":0.5},
    "Wasser":  {"Feuer":2, "Boden":2, "Gestein":2, "Wasser":0.5, "Pflanze":0.5, "Drache":0.5},
    "Pflanze": {"Wasser":2, "Boden":2, "Gestein":2, "Feuer":0.5, "Pflanze":0.5, "Gift":0.5, "Flug":0.5, "Käfer":0.5, "Drache":0.5, "Stahl":0.5},
    "Elektro": {"Wasser":2, "Flug":2, "Elektro":0.5, "Drache":0.5, "Boden":0},
    "Eis":     {"Pflanze":2, "Boden":2, "Flug":2, "Drache":2, "Feuer":0.5, "Wasser":0.5, "Eis":0.5, "Stahl":0.5},
    "Kampf":   {"Normal":2, "Eis":2, "Gestein":2, "Unlicht":2, "Stahl":2, "Gift":0.5, "Flug":0.5, "Psycho":0.5, "Käfer":0.5, "Fee":0.5, "Geist":0},
    "Gift":    {"Pflanze":2, "Fee":2, "Gift":0.5, "Boden":0.5, "Gestein":0.5, "Geist":0.5, "Stahl":0},
    "Boden":   {"Feuer":2, "Elektro":2, "Gift":2, "Gestein":2, "Stahl":2, "Pflanze":0.5, "Käfer":0.5, "Flug":0},
    "Flug":    {"Pflanze":2, "Kampf":2, "Käfer":2, "Elektro":0.5, "Gestein":0.5, "Stahl":0.5},
    "Psycho":  {"Kampf":2, "Gift":2, "Psycho":0.5, "Stahl":0.5, "Unlicht":0},
    "Käfer":   {"Pflanze":2, "Psycho":2, "Unlicht":2, "Feuer":0.5, "Kampf":0.5, "Flug":0.5, "Geist":0.5, "Stahl":0.5, "Fee":0.5},
    "Gestein": {"Feuer":2, "Eis":2, "Flug":2, "Käfer":2, "Kampf":0.5, "Boden":0.5, "Stahl":0.5},
    "Geist":   {"Geist":2, "Psycho":2, "Normal":0, "Unlicht":0.5},
    "Drache":  {"Drache":2, "Stahl":0.5, "Fee":0},
    "Unlicht": {"Geist":2, "Psycho":2, "Kampf":0.5, "Unlicht":0.5, "Fee":0.5},
    "Stahl":   {"Eis":2, "Gestein":2, "Fee":2, "Feuer":0.5, "Wasser":0.5, "Elektro":0.5, "Stahl":0.5},
    "Fee":     {"Kampf":2, "Drache":2, "Unlicht":2, "Feuer":0.5, "Gift":0.5, "Stahl":0.5},
    "Normal":  {"Gestein":0.5, "Stahl":0.5, "Geist":0},
}

def get_type_multiplier(attacker_types, defender_types):
    """Calculate combined type effectiveness multiplier."""
    mult = 1.0
    for at in attacker_types:
        chart = TYPE_EFFECTIVENESS.get(at, {})
        for dt in defender_types:
            mult *= chart.get(dt, 1.0)
    return mult

def effectiveness_label(mult):
    if mult == 0:   return "Keine Wirkung!", (100,100,100)
    if mult >= 4:   return "Supereffektiv x4!", (255,80,0)
    if mult >= 2:   return "Supereffektiv!", (255,160,0)
    if mult <= 0.25: return "Nicht sehr effektiv...", (100,160,255)
    if mult < 1:    return "Nicht sehr effektiv", (120,180,255)
    return "", None



def rarity_to_hp(rarity, grade):
    base = {"common": 40, "uncommon": 55, "rare": 70, "epic": 90, "legendary": 120, "": 50}
    return base.get(rarity, 50) + grade * 10

def rarity_to_attack(rarity, grade):
    base = {"common": 30, "uncommon": 45, "rare": 60, "epic": 80, "legendary": 100, "": 40}
    return base.get(rarity, 40) + grade * 5

class Moonie:
    def __init__(self, name, rarity, evolve, types, evolutionLevel, evolutionGrade,
                 image, preEvolution=None, nextEvolution=None):
        self.name = name
        self.rarity = rarity
        self.evolve = evolve
        self.types = types
        self.evolutionLevel = evolutionLevel
        self.evolutionGrade = evolutionGrade
        self.image = image
        self.preEvolution = preEvolution
        self.nextEvolution = nextEvolution

        self.max_hp = rarity_to_hp(rarity, evolutionGrade)
        self.attack = rarity_to_attack(rarity, evolutionGrade)
        self.current_hp = self.max_hp
        self.level = max(1, evolutionLevel if evolutionLevel > 0 else evolutionGrade * 10)
        self.xp = 0
        # XP required grows steeply: level 1→2 needs ~60, level 10→11 needs ~300, level 20→21 needs ~1000
        self.xp_to_next = self._calc_xp_needed(self.level)
        self.catch_rate = RARITY_CATCH_RATE.get(rarity, 0.5)

    def get_type_color(self):
        if self.types:
            return TYPE_COLORS.get(self.types[0], (200, 200, 200))
        return (200, 200, 200)

    def get_rarity_color(self):
        return RARITY_COLORS.get(self.rarity, (180, 180, 180))

    def is_alive(self):
        return self.current_hp > 0

    def take_damage(self, dmg):
        self.current_hp = max(0, self.current_hp - dmg)

    def heal(self, amount=None):
        if amount is None:
            self.current_hp = self.max_hp
        else:
            self.current_hp = min(self.max_hp, self.current_hp + amount)

    def _calc_xp_needed(self, lvl):
        # Medium-slow curve: ~60 at lv1, ~300 at lv10, ~1000 at lv20, ~4000 at lv40
        return int(60 * (lvl ** 1.6))

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        evolutions = []
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = self._calc_xp_needed(self.level)
            # Modest stat gains per level
            self.max_hp  += 2 + self.level // 10
            self.attack  += 1 + self.level // 15
            self.current_hp = self.max_hp
            leveled = True
            if self.can_evolve():
                evolutions.append(self.nextEvolution)
        return leveled, evolutions

    def can_evolve(self):
        return self.evolve and self.evolutionLevel > 0 and self.level >= self.evolutionLevel

    def calculate_damage(self, target, bonus=1.0):
        mult = get_type_multiplier(self.types, target.types)
        base = self.attack + random.randint(-5, 5)
        return max(1, int(base * bonus * mult)), mult

    def clone_for_battle(self):
        """Return a battle copy with full HP"""
        m = Moonie(self.name, self.rarity, self.evolve, self.types,
                   self.evolutionLevel, self.evolutionGrade,
                   self.image, self.preEvolution, self.nextEvolution)
        m.level = self.level
        m.max_hp = self.max_hp
        m.current_hp = self.max_hp
        m.attack = self.attack
        m.xp = self.xp
        m.xp_to_next = self._calc_xp_needed(self.level)
        return m