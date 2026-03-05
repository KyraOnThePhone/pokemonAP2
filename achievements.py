"""
MoonieQuest Achievement System
Achievements are checked after each relevant game event.
Each achievement can have multiple milestones (tiers).
"""

# ── Achievement definitions ─────────────────────────────────────────────────
# Each entry: id, icon, title, description, milestones: [(threshold, label, reward_coins)]
# If milestones is None → binary (done/not done), threshold=1

ACHIEVEMENTS = [

    # ── Pokédex / Fangen ────────────────────────────────────────────────────
    {
        "id": "catch_first",
        "icon": "🎊", "category": "Fangen",
        "title": "Erstes Fangen",
        "desc": "Fange dein erstes wildes Pokémon",
        "milestones": [(1, "Starter", 50)],
    },
    {
        "id": "catch_pokemon",
        "icon": "🎯", "category": "Fangen",
        "title": "Pokémon-Sammler",
        "desc": "Fange viele verschiedene Pokémon",
        "milestones": [
            (10,  "Bronze",    100),
            (25,  "Silber",    250),
            (50,  "Gold",      500),
            (100, "Platin",   1000),
            (200, "Diamant",  2500),
            (665, "Meister", 10000),
        ],
    },
    {
        "id": "pokedex_type_normal",
        "icon": "⭐", "category": "Typen",
        "title": "Normal-Experte",
        "desc": "Fange Pokémon des Typs Normal",
        "milestones": [(5,"Bronze",100),(15,"Silber",250),(30,"Gold",500),(60,"Meister",1000)],
        "type": "Normal",
    },
    {
        "id": "pokedex_type_feuer",
        "icon": "🔥", "category": "Typen",
        "title": "Feuer-Meister",
        "desc": "Fange Pokémon des Typs Feuer",
        "milestones": [(5,"Bronze",100),(15,"Silber",250),(30,"Gold",500),(40,"Meister",1000)],
        "type": "Feuer",
    },
    {
        "id": "pokedex_type_wasser",
        "icon": "💧", "category": "Typen",
        "title": "Wasser-Meister",
        "desc": "Fange Pokémon des Typs Wasser",
        "milestones": [(5,"Bronze",100),(15,"Silber",250),(30,"Gold",500),(50,"Meister",1000)],
        "type": "Wasser",
    },
    {
        "id": "pokedex_type_pflanze",
        "icon": "🌿", "category": "Typen",
        "title": "Pflanzen-Meister",
        "desc": "Fange Pokémon des Typs Pflanze",
        "milestones": [(5,"Bronze",100),(10,"Silber",200),(25,"Meister",500)],
        "type": "Pflanze",
    },
    {
        "id": "pokedex_type_elektro",
        "icon": "⚡", "category": "Typen",
        "title": "Elektro-Meister",
        "desc": "Fange Pokémon des Typs Elektro",
        "milestones": [(5,"Bronze",100),(15,"Silber",250),(25,"Meister",500)],
        "type": "Elektro",
    },
    {
        "id": "pokedex_type_psycho",
        "icon": "🔮", "category": "Typen",
        "title": "Psycho-Meister",
        "desc": "Fange Pokémon des Typs Psycho",
        "milestones": [(5,"Bronze",100),(20,"Silber",300),(30,"Meister",600)],
        "type": "Psycho",
    },
    {
        "id": "pokedex_type_drache",
        "icon": "🐉", "category": "Typen",
        "title": "Drachen-Meister",
        "desc": "Fange Pokémon des Typs Drache",
        "milestones": [(5,"Bronze",150),(15,"Silber",350),(25,"Meister",700)],
        "type": "Drache",
    },
    {
        "id": "pokedex_type_geist",
        "icon": "👻", "category": "Typen",
        "title": "Geister-Meister",
        "desc": "Fange Pokémon des Typs Geist",
        "milestones": [(5,"Bronze",100),(15,"Silber",250),(26,"Meister",600)],
        "type": "Geist",
    },
    {
        "id": "all_types",
        "icon": "🌈", "category": "Typen",
        "title": "Typ-Encyclopädie",
        "desc": "Fange mindestens 1 Pokémon jedes Typs",
        "milestones": [(1, "Vollständig", 2000)],
    },

    # ── Kämpfe ──────────────────────────────────────────────────────────────
    {
        "id": "battles_won",
        "icon": "⚔️", "category": "Kämpfe",
        "title": "Kämpfer",
        "desc": "Gewinne Trainerkämpfe und wilde Kämpfe",
        "milestones": [
            (10,  "Anfänger",   100),
            (25,  "Kämpfer",    250),
            (50,  "Champion",   500),
            (100, "Legende",   1000),
        ],
    },
    {
        "id": "trainer_battles",
        "icon": "🏆", "category": "Kämpfe",
        "title": "Trainer-Bezwinger",
        "desc": "Besiege Trainer-Kämpfe",
        "milestones": [
            (5,  "Neuling",   150),
            (15, "Profi",     400),
            (30, "Elite",     800),
            (50, "Meister",  1500),
        ],
    },
    {
        "id": "rocket_battles",
        "icon": "🚀", "category": "Kämpfe",
        "title": "Team Rocket Stopper",
        "desc": "Besiege Team Rocket Mitglieder",
        "milestones": [
            (3,  "Widerstand",  200),
            (10, "Held",        600),
            (20, "Retter",     1200),
        ],
    },
    {
        "id": "badges",
        "icon": "🏅", "category": "Kämpfe",
        "title": "Abzeichen-Sammler",
        "desc": "Sammle Orden durch Siege",
        "milestones": [
            (1,  "Erstes Abzeichen", 0),
            (4,  "4 Abzeichen",    200),
            (8,  "8 Abzeichen",    500),
            (16, "Arena-Meister", 1500),
        ],
    },

    # ── Lernkarten ──────────────────────────────────────────────────────────
    {
        "id": "cards_answered",
        "icon": "📚", "category": "Lernen",
        "title": "Lernender",
        "desc": "Beantworte Lernkarten richtig",
        "milestones": [
            (10, "Schüler",    100),
            (30, "Student",    300),
            (60, "Absolvent",  600),
            (74, "Allwissend",1500),
        ],
    },
    {
        "id": "cards_streak",
        "icon": "🎓", "category": "Lernen",
        "title": "Lernstreak",
        "desc": "Beantworte Lernkarten in Folge richtig",
        "milestones": [
            (3,  "3 in Folge",  100),
            (7,  "7 in Folge",  300),
            (15, "15 in Folge", 700),
        ],
    },

    # ── Abenteuer ────────────────────────────────────────────────────────────
    {
        "id": "steps",
        "icon": "👟", "category": "Abenteuer",
        "title": "Weltenbummler",
        "desc": "Lege Schritte auf der Karte zurück",
        "milestones": [
            (500,   "Spaziergänger",  50),
            (2000,  "Wanderer",      150),
            (5000,  "Abenteurer",    300),
            (10000, "Weltreisender", 600),
        ],
    },
    {
        "id": "evolutions",
        "icon": "✨", "category": "Abenteuer",
        "title": "Entwicklungs-Fan",
        "desc": "Entwickle Pokémon",
        "milestones": [
            (1, "Erste Entwicklung",  100),
            (5, "5 Entwicklungen",    300),
            (10,"10 Entwicklungen",   700),
        ],
    },
    {
        "id": "pokedex_complete",
        "icon": "📖", "category": "Pokédex",
        "title": "Pokédex-Vervollständiger",
        "desc": "Vervollständige den Pokédex",
        "milestones": [
            (100, "100 Einträge",   500),
            (250, "250 Einträge",  1500),
            (400, "400 Einträge",  3000),
            (665, "Vollständig!", 10000),
        ],
    },
    {
        "id": "legendary",
        "icon": "⭐", "category": "Pokédex",
        "title": "Legendenjäger",
        "desc": "Fange legendäre Pokémon",
        "milestones": [
            (1, "Erste Legende",  500),
            (3, "3 Legenden",    1500),
            (5, "5 Legenden",    3000),
        ],
    },
]

# Build lookup
ACHIEVEMENT_BY_ID = {a["id"]: a for a in ACHIEVEMENTS}

ALL_TYPES = ["Normal","Feuer","Wasser","Pflanze","Elektro","Eis","Kampf","Gift",
             "Boden","Flug","Psycho","Käfer","Gestein","Geist","Drache","Unlicht","Stahl","Fee"]


def _get_progress(ach_id, save, flashcards, caught_set, all_moonies):
    """Compute current progress value for an achievement."""
    a = ACHIEVEMENT_BY_ID.get(ach_id)
    if not a:
        return 0

    if ach_id == "catch_first":
        return min(1, save.get("total_catches", 0))

    if ach_id == "catch_pokemon":
        return len(caught_set)

    if ach_id == "pokedex_complete":
        return len(caught_set)

    if ach_id == "legendary":
        count = 0
        for name in caught_set:
            m = all_moonies.get(name)
            if m and m.rarity == "legendary":
                count += 1
        return count

    if ach_id == "all_types":
        types_caught = set()
        for name in caught_set:
            m = all_moonies.get(name)
            if m:
                for t in m.types:
                    types_caught.add(t)
        needed = set(ALL_TYPES)
        return 1 if needed.issubset(types_caught) else 0

    if "type" in a:
        typ = a["type"]
        count = 0
        for name in caught_set:
            m = all_moonies.get(name)
            if m and typ in m.types:
                count += 1
        return count

    if ach_id == "battles_won":
        return save.get("battles_won", 0)

    if ach_id == "trainer_battles":
        return save.get("trainer_battles_won", 0)

    if ach_id == "rocket_battles":
        return save.get("rocket_battles_won", 0)

    if ach_id == "badges":
        return save.get("badges", 0)

    if ach_id == "cards_answered":
        return save.get("cards_correct_total", 0)

    if ach_id == "cards_streak":
        return save.get("cards_best_streak", 0)

    if ach_id == "steps":
        return save.get("step_count", 0)

    if ach_id == "evolutions":
        return save.get("evolution_count", 0)

    return 0


def check_achievements(save, flashcards, all_moonies):
    """
    Check all achievements against current save state.
    Returns list of newly unlocked (ach_id, milestone_label, reward_coins) tuples.
    """
    caught_set = set(save.get("pc_box", []))
    unlocked = save.setdefault("achievements", {})  # {ach_id: milestone_index_reached}
    newly_unlocked = []

    for a in ACHIEVEMENTS:
        aid = a["id"]
        progress = _get_progress(aid, save, flashcards, caught_set, all_moonies)
        current_tier = unlocked.get(aid, -1)

        for tier_idx, (threshold, label, reward) in enumerate(a["milestones"]):
            if tier_idx <= current_tier:
                continue   # already unlocked
            if progress >= threshold:
                unlocked[aid] = tier_idx
                save["coins"] = save.get("coins", 0) + reward
                newly_unlocked.append((aid, label, a["title"], reward, a["icon"]))
            else:
                break   # milestones are ordered; stop early

    return newly_unlocked


def get_all_status(save, flashcards, all_moonies):
    """Return list of (achievement, progress, current_tier) for display."""
    caught_set = set(save.get("pc_box", []))
    unlocked = save.get("achievements", {})
    result = []
    for a in ACHIEVEMENTS:
        aid = a["id"]
        progress = _get_progress(aid, save, flashcards, caught_set, all_moonies)
        tier = unlocked.get(aid, -1)
        result.append((a, progress, tier))
    return result

# ── Card achievements (appended) ────────────────────────────────────────────
CARD_ACHIEVEMENTS = [
    {
        "id": "cards_collected",
        "icon": "🃏", "category": "Karten",
        "title": "Karten-Sammler",
        "desc": "Sammle Pokémon-Karten",
        "milestones": [
            (1,   "Erste Karte",   100),
            (10,  "10 Karten",     300),
            (25,  "25 Karten",     600),
            (50,  "50 Karten",    1200),
            (100, "100 Karten",   3000),
        ],
    },
    {
        "id": "shiny_cards",
        "icon": "✨", "category": "Karten",
        "title": "Glitzer-Jäger",
        "desc": "Sammle Glitzerkarten",
        "milestones": [
            (1,  "Erste Glitzerkarte",  500),
            (5,  "5 Glitzerkarten",    2000),
            (10, "10 Glitzerkarten",   5000),
        ],
    },
    {
        "id": "unique_cards",
        "icon": "📦", "category": "Karten",
        "title": "Vollständige Sammlung",
        "desc": "Sammle verschiedene Pokémon-Karten",
        "milestones": [
            (10,  "10 verschiedene",    200),
            (50,  "50 verschiedene",   1000),
            (100, "100 verschiedene",  3000),
            (200, "200 verschiedene", 10000),
        ],
    },
]

ACHIEVEMENTS.extend(CARD_ACHIEVEMENTS)
ACHIEVEMENT_BY_ID.update({a["id"]: a for a in CARD_ACHIEVEMENTS})

def _get_card_progress(ach_id, save):
    album = save.get("card_album", {})
    if ach_id == "cards_collected":
        return sum(v.get("count",0) for v in album.values())
    if ach_id == "shiny_cards":
        return sum(v.get("shiny",0) for v in album.values())
    if ach_id == "unique_cards":
        return len(album)
    return 0

# Monkey-patch _get_progress to handle card achievements
_orig_get_progress = _get_progress
def _get_progress(ach_id, save, flashcards, caught_set, all_moonies):
    if ach_id in ("cards_collected", "shiny_cards", "unique_cards"):
        return _get_card_progress(ach_id, save)
    return _orig_get_progress(ach_id, save, flashcards, caught_set, all_moonies)