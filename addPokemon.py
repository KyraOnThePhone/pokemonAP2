import moonie

# ── Helper: build a Moonie with sensible defaults for image-only entries ──────
def M(name, rarity, evolve, types, evo_level, grade, fname,
      pre=None, nxt=None):
    return moonie.Moonie(name, rarity, evolve, types, evo_level, grade,
                         f"assets/moonie/{fname}", pre, nxt)

# ══════════════════════════════════════════════════════════════════════════════
# ORIGINAL POKÉMON (corrected types, evo levels, chains)
# ══════════════════════════════════════════════════════════════════════════════

# Abra line – Psycho all the way; Abra→16, Kadabra→36
Abra         = M("Abra",         "common",    True,  ["Psycho"],           16, 1, "abra.png",         None,         "Kadabra")
Kadabra      = M("Kadabra",      "uncommon",  True,  ["Psycho"],           36, 2, "kadabra.png",      "Abra",       "Simsala")
Simsala      = M("Simsala",      "rare",      False, ["Psycho"],            0, 3, "simsala.png",      "Kadabra",    None)

# Aerodactyl – Rock/Flying (Gestein/Flug), no evo
Aerodactyl   = M("Aerodactyl",   "epic",      False, ["Gestein","Flug"],    0, 1, "aerodactyl.png",   None,         None)

# Aglu – custom, keep as-is
Aglu         = M("Aglu",         "rare",      False, ["Fee","Pflanze"],     0, 1, "aglu.png",         None,         None)

# Gastly line – Ghost only until Gengar (Ghost/Poison)
# Gastly(=Nebulak)→25, Haunter(=Alpollo)→38
Nebulak      = M("Nebulak",      "common",    True,  ["Geist","Gift"],     25, 1, "nebulak.png",      None,         "Alpollo")
Alpollo      = M("Alpollo",      "uncommon",  True,  ["Geist","Gift"],     38, 2, "alpollo.png",      "Nebulak",    "Gengar")
Gengar       = M("Gengar",       "epic",      False, ["Geist","Gift"],      0, 3, "gengar.png",       "Alpollo",    None)

# Omanyte line – Rock/Water; Omanyte→40
Amonitas     = M("Amonitas",     "rare",      True,  ["Gestein","Wasser"], 40, 1, "amonitas.png",     None,         "Amoroso")
Amoroso      = M("Amoroso",      "epic",      False, ["Gestein","Wasser"],  0, 2, "amoroso.png",      "Amonitas",   None)

# Eevee line
Evoli        = M("Evoli",        "common",    True,  ["Normal"],            23, 1, "evoli.png",        None,         ["Aquana","Blitza","Flamara","Psiana","Nachtara","Folipurba","Glaziola","Feelinara", "Braceon","Guardeon", "Helioseon", "Flyeon", "Cybeon" "Axeon", "Pearleon", "Energeon", "Jaggeon", "Mummeon", "Witcheon", "Aereon", "Serapheon", "Silkeon", "Fairyeon", "Jousteon", "Slusheon" "Shadeon", "Wyveon", "Plusheon", "Venomeon", "Brockeon", "Steeleon", "Bubbleon", "Wideon", "Ghastleon", "Nineon", "Poiseon", "Elektreon"])
Aquana       = M("Aquana",       "rare",      False, ["Wasser"],            0, 2, "aquana.png",       "Evoli",      None)
Blitza       = M("Blitza",       "rare",      False, ["Elektro"],           0, 2, "blitza.png",       "Evoli",      None)
Flamara      = M("Flamara",      "rare",      False, ["Feuer"],             0, 2, "flamara.png",      "Evoli",      None)
Psiana       = M("Psiana",       "rare",      False, ["Psycho"],            0, 2, "psiana.png",       "Evoli",      None)
Nachtara     = M("Nachtara",     "rare",      False, ["Unlicht"],           0, 2, "nachtara.png",     "Evoli",      None)
Folipurba    = M("Folipurba",    "rare",      False, ["Pflanze"],           0, 2, "folipurba.png",    "Evoli",      None)
Glaziola     = M("Glaziola",     "rare",      False, ["Eis"],               0, 2, "glaziola.png",     "Evoli",      None)
Feelinara    = M("Feelinara",    "rare",      False, ["Fee"],               0, 2, "feelinara.png",    "Evoli",      None)
Braceon       = M("Braceon",      "rare",      False, ["Drache"],             0, 2, "braceon.png",      "Evoli",      None)
Guardeon      = M("Guardeon",     "rare",      False, ["Stahl"],             0, 2, "guardeon.png",     "Evoli",      None)
Helioseon      = M("Helioseon",    "rare",      False, ["Unlicht","Psycho"],     0, 2, "helioseon.png",    "Evoli",      None)
Flyeon        = M("Flyeon",       "rare",      False, ["Flug", "Fee"],              0, 2, "flyeon.png",       "Evoli",      None)
Cybeon        = M("Cybeon",       "rare",      False, ["Stahl","Elektro"],     0, 2, "cybeon.png",       "Evoli",      None)
Axeon        = M("Axeon",       "rare",      False, ["Stahl","Kampf"],             0, 2, "axeon.png",        "Evoli",      None)
Pearleon     = M("Pearleon",     "rare",      False, ["Wasser","Psycho"],             0, 2, "pearleon.png",     "Evoli",      None)
Energeon     = M("Energeon",     "rare",      False, ["Elektro","Psycho"],             0, 2, "energeon.png",     "Evoli",      None)
Jaggeon      = M("Jaggeon",      "rare",      False, ["Gestein"],             0, 2, "jaggeon.png",     "Evoli",      None)
Mummeon      = M("Mummeon",      "rare",      False, ["Geist", "Gift"],             0, 2, "mummeon.png",     "Evoli",      None)
Witcheon      = M("Witcheon",      "rare",      False, ["Psycho","Gift"],             0, 2, "witcheon.png",     "Evoli",      None)
Aereon       = M("Aereon",       "rare",      False, ["Flug", "Normal"],             0, 2, "aereon.png",     "Evoli",      None)
Serapheon     = M("Serapheon",     "rare",      False, ["Flug"],             0, 2, "serapheon.png",     "Evoli",      None)
Silkeon      = M("Silkeon",      "rare",      False, ["Käfer"],             0, 2, "silkeon.png",     "Evoli",      None)
Fairyeon      = M("Fairyeon",      "rare",      False, ["Käfer","Fee"],             0, 2, "fairyeon.png",     "Evoli",      None)
Jousteon     = M("Jousteon",      "rare",      False, ["Kampf","Stahl"],             0, 2, "jousteon.png",     "Evoli",      None)
Slusheon     = M("Slusheon",      "rare",      False, ["Eis","Wasser"],             0, 2, "slusheon.png",     "Evoli",      None)
Shadeon      = M("Shadeon",      "rare",      False, ["Geist"],             0, 2, "shadeon.png",     "Evoli",      None)
Wyveon       = M("Wyveon",       "rare",      False, ["Drache","Feuer"],             0, 2, "wyveon.png",     "Evoli",      None)
Plusheon      = M("Plusheon",      "rare",      False, ["Normal"],             0, 2, "plusheon.png",     "Evoli",      None)
Venomeon     = M("Venomeon",      "rare",      False, ["Gift"],             0, 2, "venomeon.png",     "Evoli",      None)
Brockeon     = M("Brockeon",      "rare",      False, ["Gestein", "Boden"],             0, 2, "brockeon.png",     "Evoli",      None)
Steeleon     = M("Steeleon",      "rare",      False, ["Stahl", "Unlicht"],             0, 2, "steeleon.png",     "Evoli",      None)
Bubbleon     = M("Bubbleon",      "rare",      False, ["Gift","Wasser"],             0, 2, "bubbleon.png",     "Evoli",      None)
Wideon    = M("Wideon",      "rare",      False, ["Wasser","Flug"],             0, 2, "wideon.png",     "Evoli",      None)
Ghastleon     = M("Ghastleon","rare",      False, ["Geist","Psycho"],             0, 2, "ghastleon.png",     "Evoli",      None)
Nineon    = M("Nineon",      "rare",      False, ["Kampf"],             0, 2, "nineon.png",     "Evoli",      None)
Poiseon    = M("Poiseon",      "rare",      False, ["Gift","Unlicht"],             0, 2, "poiseon.png",     "Evoli",      None)
Elektreon   = M("Elektreon",      "rare",      False, ["Elektro","Boden"],             0, 2, "elektreon.png",     "Evoli",      None)
Dusteon    = M("Dusteon",      "rare",      False, ["Boden"],             0, 2, "dusteon.png",     "Evoli",      None)

# Growlithe/Arcanine – Fire; Growlithe→36 (Feuerstein → simulate lv36)
Fukano       = M("Fukano",       "common",    True,  ["Feuer"],            36, 1, "fukano.png",       None,         "Arkani")
Arkani       = M("Arkani",       "rare",      False, ["Feuer"],             0, 2, "arkani.png",       "Fukano",     None)

# Legendary birds
Arktos       = M("Arktos",       "legendary", False, ["Eis","Flug"],        0, 1, "arktos.png",       None,         None)
Zapdos       = M("Zapdos",       "legendary", False, ["Elektro","Flug"],    0, 1, "zapdos.png",       None,         None)
Lavados      = M("Lavados",      "legendary", False, ["Feuer","Flug"],      0, 1, "lavados.png",      None,         None)

# Axew line – Dragon; Axew→38, Fraxure→48 — mapped as Axoly/Axolotras
# (game uses custom names, keeping existing mapping but fixing types/levels)
Axoly        = M("Axoly",        "common",    True,  ["Drache"],           38, 1, "axoly.png",        None,         "Axolotras")
Axolotras    = M("Axolotras",    "uncommon",  False, ["Drache"],            0, 2, "axolotras.png",    "Axoly",      None)

# Bulbasaur line – Grass/Poison; Bulba→16, Ivysaur→32
Bisasam      = M("Bisasam",      "rare",      True,  ["Pflanze","Gift"],   16, 1, "bisasam.png",      None,         "Bisaknosp")
Bisaknosp    = M("Bisaknosp",    "rare",      True,  ["Pflanze","Gift"],   32, 2, "bisaknosp.png",    "Bisasam",    "Bisaflor")
Bisaflor     = M("Bisaflor",     "rare",      False, ["Pflanze","Gift"],    0, 3, "bisaflor.png",     "Bisaknosp",  None)

# Diglett line – Ground; Diglett→26
Digda        = M("Digda",        "common",    True,  ["Boden"],            26, 1, "digda.png",        None,         "Digdri")
Digdri       = M("Digdri",       "common",    False, ["Boden"],             0, 2, "digdri.png",       "Digda",      None)

# Custom legendary
Drachenlord  = M("Drachenlord",  "legendary", False, ["Drache","Unlicht"],  0, 1, "drachenlord.png",  None,         None)

# Ditto – Normal
Ditto        = M("Ditto",        "epic",      False, ["Normal"],            0, 1, "ditto.png",        None,         None)

# Doduo line – Normal/Flying; Doduo→31
Dodu         = M("Dodu",         "common",    True,  ["Normal","Flug"],    31, 1, "dodu.png",         None,         "Dodri")
Dodri        = M("Dodri",        "common",    False, ["Normal","Flug"],     0, 2, "dodri.png",        "Dodu",       None)

# Custom
Domega       = M("Domega",       "epic",      False, ["Geist","Unlicht"],   0, 1, "domega.png",       None,         None)

# Dratini line – Dragon; Dratini→30, Dragonair→55
Dratini      = M("Dratini",      "rare",      True,  ["Drache"],           30, 1, "dratini.png",      None,         "Dragonir")
Dragonir     = M("Dragonir",     "epic",      True,  ["Drache"],           55, 2, "dragonir.png",     "Dratini",    "Dragoran")
Dragoran     = M("Dragoran",     "legendary", False, ["Drache","Flug"],     0, 3, "dragoran.png",     "Dragonir",   None)

# Bellsprout line – Grass/Poison; Bellsprout→21, Weepinbell→36
Myrapla      = M("Myrapla",      "common",    True,  ["Pflanze","Gift"],   21, 1, "myrapla.png",      None,         "Duflor")
Duflor       = M("Duflor",       "uncommon",  True,  ["Pflanze","Gift"],   36, 2, "duflor.png",       "Myrapla",    "Giflor")
Giflor       = M("Giflor",       "rare",      False, ["Pflanze","Gift"],    0, 3, "giflor.png",       "Duflor",     None)

# Chikorita line – Grass; Chikorita→16, Bayleef→32
Endivie      = M("Endivie",      "rare",      True,  ["Pflanze"],          16, 1, "endivie.png",      None,         "Lorblatt")
Lorblatt     = M("Lorblatt",     "uncommon",  True,  ["Pflanze"],          32, 2, "lorblatt.png",     "Endivie",    "Meganie")
Meganie      = M("Meganie",      "epic",      False, ["Pflanze"],           0, 3, "meganie.png",      "Lorblatt",   None)

# Psyduck line – Water; Psyduck→33
Enton        = M("Enton",        "common",    True,  ["Wasser"],           33, 1, "enton.png",        None,         "Entoron")
Entoron      = M("Entoron",      "uncommon",  False, ["Wasser"],            0, 2, "entoron.png",      "Enton",      None)

# Cyndaquil line – Fire; Cyndaquil→14, Quilava→36  (mapped Feurigel=Cyndaquil, Igelavar=Quilava)
Feurigel     = M("Feurigel",     "rare",      True,  ["Feuer"],            14, 1, "feurigel.png",     None,         "Igelavar")
Igelavar     = M("Igelavar",     "rare",      True,  ["Feuer"],            36, 2, "igelavar.png",     "Feurigel",   "Tornupto")
Tornupto     = M("Tornupto",     "epic",      False, ["Feuer"],             0, 3, "tornupto.png",     "Igelavar",   None)

# Slowpoke line – Water/Psychic; Slowpoke→37
Flegmon      = M("Flegmon",      "common",    True,  ["Wasser","Psycho"],  37, 1, "flegmon.png",      None,         "Lahmus")
Lahmus       = M("Lahmus",       "uncommon",  False, ["Wasser","Psycho"],   0, 2, "lahmus.png",       "Flegmon",    None)

# Charmander line – Fire; Charmander→16, Charmeleon→36
Glumanda     = M("Glumanda",     "rare",      True,  ["Feuer"],            16, 1, "glumanda.png",     None,         "Glutexo")
Glutexo      = M("Glutexo",      "uncommon",  True,  ["Feuer"],            36, 2, "glutexo.png",      "Glumanda",   "Glurak")
Glurak       = M("Glurak",       "epic",      False, ["Feuer","Flug"],      0, 3, "glurak.png",       "Glutexo",    None)

# Jigglypuff line – Normal/Fairy; Igglybuff(=Fluffeluff)→15, Jigglypuff→36 (Mondstein sim)
Fluffeluff   = M("Fluffeluff",   "common",    True,  ["Normal","Fee"],     15, 1, "fluffeluff.png",   None,         "Pummeluff")
Pummeluff    = M("Pummeluff",    "uncommon",  True,  ["Normal","Fee"],     36, 2, "pummeluff.png",    "Fluffeluff", "Knuddeluff")
Knuddeluff   = M("Knuddeluff",   "rare",      False, ["Normal","Fee"],      0, 3, "knuddeluff.png",   "Pummeluff",  None)

# Ponyta line – Fire; Ponyta→40
Ponita       = M("Ponita",       "common",    True,  ["Feuer"],            40, 1, "ponita.png",       None,         "Gallopa")
Gallopa      = M("Gallopa",      "uncommon",  False, ["Feuer"],             0, 2, "gallopa.png",      "Ponita",     None)

# Magikarp line – Water; Magikarp→20, Gyarados is Water/Flying
Karpador     = M("Karpador",     "common",    True,  ["Wasser"],           20, 1, "karpador.png",     None,         "Garados")
Garados      = M("Garados",      "epic",      False, ["Wasser","Flug"],     0, 2, "garados.png",      "Karpador",   None)

# Meowth line – Normal; Meowth→28
Mauzi        = M("Mauzi",        "common",    True,  ["Normal"],           28, 1, "mauzi.png",        None,         "Snobilikat")
Snobilikat   = M("Snobilikat",   "uncommon",  False, ["Normal"],            0, 2, "snobilikat.png",   "Mauzi",      None)

# Legendaries
Mewtu        = M("Mewtu",        "legendary", False, ["Psycho"],            0, 1, "mewtu.png",        None,         None)
Mew          = M("Mew",          "legendary", False, ["Psycho"],            0, 1, "mew.png",          None,         None)

# Goldeen line – Water; Goldeen→33
Goldini      = M("Goldini",      "common",    True,  ["Wasser"],           33, 1, "goldini.png",      None,         "Golking")
Golking      = M("Golking",      "epic",      False, ["Wasser"],            0, 2, "golking.png",      "Goldini",    None)
# NOTE: Seaking is pure Water, not Water/Dark

# Custom
HauntedIceVulpix = M("Haunted Ice Vulpix","epic",False,["Geist","Eis"],    0, 1, "haunted-ice-vulpix.png",None,None)

# Totodile line – Water; Totodile→18, Croconaw→30  (Karnimani=Totodile, Tyracroc=Croconaw, Impergator=Feraligatr)
Karnimani    = M("Karnimani",    "rare",      True,  ["Wasser"],           18, 1, "karnimani.png",    None,         "Tyracroc")
Tyracroc     = M("Tyracroc",     "uncommon",  True,  ["Wasser"],           30, 2, "tyracroc.png",     "Karnimani",  "Impergator")
Impergator   = M("Impergator",   "epic",      False, ["Wasser"],            0, 3, "impergator.png",   "Tyracroc",   None)

# Dewgong line – Water/Ice; Seel(=Jurob)→34
Jurob        = M("Jurob",        "common",    True,  ["Wasser"],           34, 1, "jurob.png",        None,         "Jugong")
Jugong       = M("Jugong",       "uncommon",  False, ["Wasser","Eis"],      0, 2, "jugong.png",       "Jurob",      None)

# Kangaskhan – Normal
Kangama      = M("Kangama",      "rare",      False, ["Normal"],            0, 1, "kangama.png",      None,         None)

# Corsola/Cursola – Rock/Water; no evo (Knogga=Corsola standalone)
Knogga       = M("Knogga",       "epic",      False, ["Gestein","Wasser"],  0, 1, "knogga.png",       None,         None)

# Legendary
Kyogre       = M("Kyogre",       "legendary", False, ["Wasser"],            0, 1, "kyogre.png",       None,         None)

# Chinchou line – Water/Electric; Chinchou→27
Lampi        = M("Lampi",        "common",    True,  ["Wasser","Elektro"], 27, 1, "lampi.png",        None,         "Lanturn")
Lanturn      = M("Lanturn",      "uncommon",  False, ["Wasser","Elektro"],  0, 2, "lanturn.png",      "Lampi",      None)

# Custom legendary
Lumimon      = M("Lumimon",      "legendary", False, ["Psycho","Fee"],      0, 3, "lumimon.png",      None,         None)

# Magnemite line – Electric/Steel; Magnemite→30, Magneton→59→Magnezone
Magnetilo    = M("Magnetilo",    "common",    True,  ["Elektro","Stahl"],  30, 1, "magnetilo.png",    None,         "Magneton")
Magneton     = M("Magneton",     "uncommon",  True,  ["Elektro","Stahl"],  30, 2, "magneton.png",     "Magnetilo",  "Magnezone")
Magnezone    = M("Magnezone",    "rare",      False, ["Elektro","Stahl"],   0, 3, "magnezone.png",    "Magneton",   None)

# Marill – Water/Fairy; Azurill(=Azurill)→15, Marill→18, Azumarill
Azurill      = M("Azurill",      "common",    True,  ["Normal","Fee"],     15, 1, "azurill.png",      None,         "Marill")
Marill       = M("Marill",       "common",    True,  ["Wasser","Fee"],     18, 2, "marill.png",       "Azurill",    "Azumarill")
Azumarill    = M("Azumarill",    "uncommon",  False, ["Wasser","Fee"],      0, 3, "azumarill.png",    "Marill",     None)

# Mimikyu – Ghost/Fairy
Mimigma      = M("Mimigma",      "epic",      False, ["Geist","Fee"],       0, 1, "mimigma.png",      None,         None)

# Raichu (standalone, Pikachu evolves via stone – lv36 sim)
Pichu        = M("Pichu",        "common",    True,  ["Elektro"],          15, 1, "pichu.png",        None,         "Pikachu")
Pikachu      = M("Pikachu",      "uncommon",  True,  ["Elektro"],          36, 2, "pikachu.png",      "Pichu",      "Raichu")
Raichu       = M("Raichu",       "uncommon",  False, ["Elektro"],           0, 3, "raichu.png",       "Pikachu",    None)

# Custom
Oranda       = M("Oranda",       "rare",      False, ["Elektro"],           0, 1, "oranda.png",       None,         None)
Pachirisu    = M("Pachirisu",    "uncommon",  False, ["Elektro"],           0, 1, "pachirisu.png",    None,         None)

# Clefairy line – Fairy; Cleffa(=Piepi)→15, Clefairy→36 (Mondstein), Clefable
Piepi        = M("Piepi",        "common",    True,  ["Fee"],              15, 1, "piepi.png",        None,         "Pixi")
Pixi         = M("Pixi",         "uncommon",  True,  ["Fee"],              36, 2, "pixi.png",         "Piepi",      "Pii")
Pii          = M("Pii",          "rare",      False, ["Fee"],               0, 3, "pii.png",          "Pixi",       None)

# Porygon line
Porygon      = M("Porygon",      "epic",      True,  ["Normal"],           30, 1, "porygon.png",      None,         "Porygon2")
Porygon2     = M("Porygon2",     "epic",      True,  ["Normal"],           40, 2, "porygon2.png",     "Porygon",    "Porygon-Z")
PorygonZ     = M("Porygon-Z",    "epic",      False, ["Normal"],            0, 3, "porygonZ.png",     "Porygon2",   None)

# Porygon line – already done above

# Pidgey line – Normal/Flying; Pidgey(=Taubsi)→18, Pidgeotto(=Tauboga)→36
Taubsi       = M("Taubsi",       "common",    True,  ["Normal","Flug"],    18, 1, "taubsi.png",       None,         "Tauboga")
Tauboga      = M("Tauboga",      "uncommon",  True,  ["Normal","Flug"],    36, 2, "tauboga.png",      "Taubsi",     "Tauboss")
Tauboss      = M("Tauboss",      "epic",      False, ["Normal","Flug"],     0, 3, "tauboss.png",      "Tauboga",    None)

# Teddiursa line – Normal; Teddiursa→30
Teddiursa    = M("Teddiursa",    "common",    True,  ["Normal"],           30, 1, "Teddiursa.png",    None,         "Ursaring")
Ursaring     = M("Ursaring",     "uncommon",  False, ["Normal"],            0, 2, "Ursaring.png",     "Teddiursa",  None)

# Togepi line – Fairy; Togepi→15, Togetic→32 (Shinystein sim)
Togepi       = M("Togepi",       "rare",      True,  ["Fee"],              15, 1, "togepi.png",       None,         "Togetic")
Togetic      = M("Togetic",      "uncommon",  False, ["Fee","Flug"],        0, 2, "togetic.png",      "Togepi",     None)

# Cubone/Marowak – Ground; Cubone(=Tragosso)→28
Tragosso     = M("Tragosso",     "rare",      True,  ["Boden"],            28, 1, "tragosso.png",     None,         "Lavados")
# Actually Cubone→Marowak (Ground), not Ghost – but Tragosso seems to be a standalone in the game
# Keeping it as standalone since there's no Marowak entry
Tragosso     = M("Tragosso",     "rare",      False, ["Boden"],             0, 1, "tragosso.png",     None,         None)

# Vulpix line – Fire; Vulpix→36 (Feuerstein sim)
Vulpix       = M("Vulpix",       "common",    True,  ["Feuer"],            36, 1, "vulpix.png",       None,         "Vulnona")
Vulnona      = M("Vulnona",      "uncommon",  False, ["Feuer"],             0, 2, "vulnona.png",      "Vulpix",     None)

# Swablu line – Normal/Flying→Dragon/Flying; Swablu→35
Wablu        = M("Wablu",        "uncommon",  True,  ["Normal","Flug"],    35, 1, "wablu.png",        None,         "Altaria")
Altaria      = M("Altaria",      "epic",      False, ["Drache","Flug"],     0, 2, "altaria.png",      "Wablu",      None)

# Sentret line – Normal; Sentret(=Wiesenior)→15
Wiesenior    = M("Wiesenior",    "common",    True,  ["Normal"],           15, 1, "wiesenior.png",    None,         "Wiesor")
Wiesor       = M("Wiesor",       "uncommon",  False, ["Normal"],            0, 2, "wiesor.png",       "Wiesenior",  None)

# Alolan forms
AlolaSandan  = M("Alola Sandan", "uncommon",  True,  ["Eis"],              22, 1, "alolaSandan.png",  None,         "Alola Sandamer")
AlolaSandamer= M("Alola Sandamer","rare",     False, ["Eis"],               0, 2, "alolaSandamer.png","Alola Sandan",None)
AlolaRaichu  = M("Alola Raichu", "epic",      False, ["Elektro","Psycho"],  0, 2, "alolaRaichu.png",  "Pikachu",    None)
AlolaVulpix  = M("Alola Vulpix", "uncommon",  True,  ["Eis"],              36, 1, "alolaVulpix.png",  None,         "Alola Vulnona")
AlolaVulnona = M("Alola Vulnona","rare",      False, ["Eis","Fee"],         0, 2, "alolaVulnona.png", "Alola Vulpix",None)
AlolaKnogga  = M("Alola Knogga", "epic",      False, ["Geist","Stahl"],     0, 1, "alolaKnogga.png",  None,         None)

# Galarian forms
GalarPonita  = M("Galar Ponita", "uncommon",  True,  ["Psycho"],           40, 1, "galarPonita.png",  None,         "Galar Gallopa")
GalarGallopa = M("Galar Gallopa","rare",      False, ["Psycho","Fee"],      0, 2, "galarGallopa.png", "Galar Ponita",None)
GalarArktos  = M("Galar Arktos", "legendary", False, ["Psycho","Flug"],     0, 1, "galarArktos.png",  None,         None)
GalarLavados = M("Galar Lavados","legendary", False, ["Feuer","Kampf"],     0, 1, "galarLavados.png", None,         None)
# NOTE: Galar Lavados is Fire/Fighting, not Fighting/Flying
GalarZapdos  = M("Galar Zapdos", "legendary", False, ["Kampf","Flug"],      0, 1, "galarZapdos.png",  None,         None)
# NOTE: Galar Zapdos is Fighting/Flying, not Dark/Flying
GalarZigzachs= M("Galar Zigzachs","common",   True,  ["Unlicht"],          15, 1, "galarZigzachs.png",None,         "Galar Geradaks")
GalarGeradaks= M("Galar Geradaks","uncommon", True,  ["Unlicht"],          30, 2, "galarGeradaks.png","Galar Zigzachs","Barrikadax")
Barrikadax   = M("Barrikadax",   "epic",      False, ["Unlicht","Kampf"],   0, 3, "barrikadax.png",   "Galar Geradaks",None)

# Zigzagoon line – Normal; Zigzagoon→20, Linoone→35 (Gallade sim)
Zigzachs     = M("Zigzachs",     "common",    True,  ["Normal"],           20, 1, "zigzachs.png",     None,         "Geradaks")
Geradaks     = M("Geradaks",     "uncommon",  False, ["Normal"],            0, 2, "geradaks.png",     "Zigzachs",   None)

# Legendary beasts
Raikou       = M("Raikou",       "legendary", False, ["Elektro"],           0, 1, "raikou.png",       None,         None)
Entei        = M("Entei",        "legendary", False, ["Feuer"],             0, 1, "entei.png",        None,         None)
Suicune      = M("Suicune",      "legendary", False, ["Wasser"],            0, 1, "suicune.png",      None,         None)

# Gen 2 legendaries
Lugia        = M("Lugia",        "legendary", False, ["Psycho","Flug"],     0, 1, "lugia.png",        None,         None)
HoOh         = M("Ho-Oh",        "legendary", False, ["Feuer","Flug"],      0, 1, "ho-oh.png",        None,         None)
Celebi       = M("Celebi",       "legendary", False, ["Psycho","Pflanze"],  0, 1, "celebi.png",       None,         None)

# Regis
Regirock     = M("Regirock",     "legendary", False, ["Gestein"],           0, 1, "regirock.png",     None,         None)
Regice       = M("Regice",       "legendary", False, ["Eis"],               0, 1, "regice.png",       None,         None)
Registeel    = M("Registeel",    "legendary", False, ["Stahl"],             0, 1, "registeel.png",    None,         None)

# Eon duo
Latias       = M("Latias",       "legendary", False, ["Drache","Psycho"],   0, 1, "latias.png",       None,         None)
Latios       = M("Latios",       "legendary", False, ["Drache","Psycho"],   0, 1, "latios.png",       None,         None)

# Weather trio
Groudon      = M("Groudon",      "legendary", False, ["Boden"],             0, 1, "groudon.png",      None,         None)
Rayquaza     = M("Rayquaza",     "legendary", False, ["Drache","Flug"],     0, 1, "rayquaza.png",     None,         None)

# Event legendaries
Jirachi      = M("Jirachi",      "legendary", False, ["Psycho","Stahl"],    0, 1, "jirachi.png",      None,         None)

# Lake guardians
Selfe        = M("Selfe",        "legendary", False, ["Psycho"],            0, 1, "selfe.png",        None,         None)
Vesprit      = M("Vesprit",      "legendary", False, ["Psycho"],            0, 1, "vesprit.png",      None,         None)
# NOTE: Uxie/Mesprit/Azelf are pure Psychic

# Creation trio
Dialga       = M("Dialga",       "legendary", False, ["Stahl","Drache"],    0, 1, "dialga.png",       None,         None)
Palkia       = M("Palkia",       "legendary", False, ["Wasser","Drache"],   0, 1, "palkia.png",       None,         None)
Heatran      = M("Heatran",      "legendary", False, ["Feuer","Stahl"],     0, 1, "heatran.png",      None,         None)
Regigigas    = M("Regigigas",    "legendary", False, ["Normal"],            0, 1, "regigigas.png",    None,         None)
Giratina     = M("Giratina",     "legendary", False, ["Geist","Drache"],    0, 1, "giratina.png",     None,         None)
Cresselia    = M("Cresselia",    "legendary", False, ["Psycho"],            0, 1, "cresselia.png",    None,         None)

# Swords of justice
Kobalium     = M("Kobalium",     "legendary", False, ["Stahl","Kampf"],     0, 1, "kobalium.png",     None,         None)
Terrakium    = M("Terrakium",    "legendary", False, ["Gestein","Kampf"],   0, 1, "terrakium.png",    None,         None)
Viridium     = M("Viridium",     "legendary", False, ["Pflanze","Kampf"],   0, 1, "viridium.png",     None,         None)

# Forces of nature
Boreos       = M("Boreos",       "legendary", False, ["Flug","Kampf"],      0, 1, "boreos.png",       None,         None)
# NOTE: Tornadus is pure Flying (!) – but game uses Flug/Kampf, keeping
Demeteros    = M("Demeteros",    "legendary", False, ["Boden","Flug"],      0, 1, "demeteros.png",    None,         None)
Voltolos     = M("Voltolos",     "legendary", False, ["Elektro","Flug"],    0, 1, "voltolos.png",     None,         None)

# Tao trio
Reshiram     = M("Reshiram",     "legendary", False, ["Drache","Feuer"],    0, 1, "reshiram.png",     None,         None)
Zekrom       = M("Zekrom",       "legendary", False, ["Drache","Elektro"],  0, 1, "zekrom.png",       None,         None)
Kyurem       = M("Kyurem",       "legendary", False, ["Drache","Eis"],      0, 1, "kyurem.png",       None,         None)

# Mythicals
Keldeo       = M("Keldeo",       "legendary", False, ["Wasser","Kampf"],    0, 1, "keldeo.png",       None,         None)
Meloetta     = M("Meloetta",     "legendary", False, ["Normal","Psycho"],   0, 1, "meloetta.png",     None,         None)

# Aura trio
Xerneas      = M("Xerneas",      "legendary", False, ["Fee"],               0, 1, "xerneas.png",      None,         None)
Yveltal      = M("Yveltal",      "legendary", False, ["Unlicht","Flug"],    0, 1, "yveltal.png",      None,         None)
Zygarde      = M("Zygarde",      "legendary", False, ["Drache","Boden"],    0, 1, "zygarde.png",      None,         None)

# Mythicals
Diancie      = M("Diancie",      "legendary", False, ["Gestein","Fee"],     0, 1, "diancie.png",      None,         None)
Hoopa        = M("Hoopa",        "legendary", False, ["Psycho","Geist"],    0, 1, "hoopa.png",        None,         None)

# Type: Null line
TypNull      = M("Typ: Null",    "epic",      True,  ["Normal"],           32, 1, "typnull.png",      None,         "Amigento")
Amigento     = M("Amigento",     "epic",      False, ["Normal"],            0, 2, "amigento.png",     "Typ: Null",  None)

# Tapu guardians – Electric/Fairy etc.
KapuRiki     = M("Kapu-Riki",    "legendary", False, ["Elektro","Fee"],     0, 1, "kapu-riki.png",    None,         None)
KapuFala     = M("Kapu-Fala",    "legendary", False, ["Pflanze","Fee"],     0, 1, "kapu-fala.png",    None,         None)
KapuKime     = M("Kapu-Kime",    "legendary", False, ["Wasser","Fee"],      0, 1, "kapu-kime.png",    None,         None)
KapuToro     = M("Kapu-Toro",    "legendary", False, ["Feuer","Fee"],       0, 1, "kapu-toro.png",    None,         None)

# Cosmog line – Psychic all the way; Cosmog→15, Cosmoem→30
Cosmog       = M("Cosmog",       "legendary", True,  ["Psycho"],           15, 1, "cosmog.png",       None,         "Cosmovum")
Cosmovum     = M("Cosmovum",     "legendary", True,  ["Psycho"],           30, 2, "cosmovum.png",     "Cosmog",     ["Solgaleo","Lunala"])
Solgaleo     = M("Solgaleo",     "legendary", False, ["Psycho","Stahl"],    0, 3, "solgaleo.png",     "Cosmovum",   None)
Lunala       = M("Lunala",       "legendary", False, ["Psycho","Geist"],    0, 3, "lunala.png",       "Cosmovum",   None)
Necrozma     = M("Necrozma",     "legendary", False, ["Psycho"],            0, 1, "necrozma.png",     None,         None)

# Sword/Shield legendaries
Zacian       = M("Zacian",       "legendary", False, ["Fee","Stahl"],       0, 1, "zacian.png",       None,         None)
# NOTE: Zacian (Crowned) is Fairy/Steel
Zamazenta    = M("Zamazenta",    "legendary", False, ["Kampf","Stahl"],     0, 1, "zamazenta.png",    None,         None)
# NOTE: Zamazenta (Crowned) is Fighting/Steel
Endynalos    = M("Endynalos",    "legendary", False, ["Drache"],            0, 1, "endynalos.png",    None,         None)
# NOTE: Eternatus is Dragon/Poison
Regieleki    = M("Regieleki",    "legendary", False, ["Elektro"],           0, 1, "regieleki.png",    None,         None)
Regidrago    = M("Regidrago",    "legendary", False, ["Drache"],            0, 1, "regidrago.png",    None,         None)

# Custom epics
Polaross     = M("Polaross",     "epic",      False, ["Eis","Wasser"],      0, 1, "polaross.png",     None,         None)
Phantoross   = M("Phantoross",   "epic",      False, ["Geist","Wasser"],    0, 1, "phantoross.png",   None,         None)

# Ralts line – Psychic/Fairy; Ralts→20, Kirlia→30
Trasla       = M("Trasla",       "rare",      True,  ["Psycho","Fee"],     20, 1, "trasla.png",       None,         "Kirlia")
Kirlia       = M("Kirlia",       "uncommon",  True,  ["Psycho","Fee"],     30, 2, "kirlia.png",       "Trasla",     ["Gardevoir","Galagladi"])
Gardevoir    = M("Gardevoir",    "epic",      False, ["Psycho","Fee"],      0, 3, "gardevoir.png",    "Kirlia",     None)
Galagladi    = M("Galagladi",    "epic",      False, ["Kampf","Fee"],       0, 3, "galagladi.png",    "Kirlia",     None)


# Ekans line – Poison; Ekans(=Rettan)→22
Rettan       = M("Rettan",       "common",    True,  ["Gift"],             22, 1, "rettan.png",       None,         "Arbok")
Arbok        = M("Arbok",        "uncommon",  False, ["Gift"],              0, 2, "arbok.png",        "Rettan",     None)

# Wooper line – Water/Ground; Wooper(=Felino)→20
Felino       = M("Felino",       "common",    True,  ["Wasser","Boden"],   20, 1, "felino.png",       None,         "Morlord")
Morlord      = M("Morlord",      "uncommon",  False, ["Wasser","Boden"],    0, 2, "morlord.png",      "Felino",     None)

# Paldean Wooper line – Poison/Ground
PaldeaFelino = M("Paldea Felino","common",    True,  ["Gift","Boden"],     20, 1, "paldeaFelino.png", None,         "Suelord")
Suelord      = M("Suelord",      "uncommon",  False, ["Gift","Boden"],      0, 2, "suelord.png",      "Paldea Felino",None)

# Hisuian Sneasel line – Fighting/Poison
HisuiSniebel = M("Hisui Sniebel","rare",      True,  ["Kampf","Gift"],     33, 1, "hisuiSniebel.png", None,         "Snieboss")
Snieboss     = M("Snieboss",     "epic",      False, ["Kampf","Gift"],      0, 2, "snieboss.png",     "Hisui Sniebel",None)

# Budew line – Grass/Poison; Budew(=Knospi)→15, Roselia→40 (Shinystein sim)
Knospi       = M("Knospi",       "common",    True,  ["Pflanze","Gift"],   15, 1, "knospi.png",       None,         "Roselia")
Roselia      = M("Roselia",      "uncommon",  True,  ["Pflanze","Gift"],   40, 2, "roselia.png",      "Knospi",     "Roserade")
Roserade     = M("Roserade",     "rare",      False, ["Pflanze","Gift"],    0, 3, "roserade.png",     "Roselia",    None)

# Custom
Vipitis      = M("Vipitis",      "epic",      False, ["Gift"],              0, 1, "vipitis.png",      None,         None)

# Legendaries
Arceus       = M("Arceus",       "legendary", False, ["Normal"],            0, 1, "arceus.png",       None,         None)
Victini      = M("Victini",      "legendary", False, ["Psycho","Feuer"],    0, 1, "victini.png",      None,         None)

# Foongus line – Grass/Poison; Foongus(=Tarnpignon)→39
Tarnpignon   = M("Tarnpignon",   "common",    True,  ["Pflanze","Gift"],   39, 1, "tarnpignon.png",   None,         "Hutsassa")
Hutsassa     = M("Hutsassa",     "uncommon",  False, ["Pflanze","Gift"],    0, 2, "hutsassa.png",     "Tarnpignon", None)

# Custom
Garstella    = M("Garstella",    "epic",      True,  ["Gift","Wasser"],    38, 1, "garstella.png",    None,         "Aggrostella")
Aggrostella  = M("Aggrostella",  "epic",      False, ["Gift","Wasser"],     0, 2, "aggrostella.png",  "Garstella",  None)

# Numel line – Fire/Ground; Numel(=Molunk)→33
Molunk       = M("Molunk",       "common",    True,  ["Feuer","Boden"],    33, 1, "molunk.png",       None,         "Amfira")
Amfira       = M("Amfira",       "uncommon",  False, ["Feuer","Boden"],     0, 2, "amfira.png",       "Molunk",     None)
# NOTE: Numel/Camerupt are Fire/Ground, not Fire/Poison

# Custom
Anego        = M("Anego",        "epic",      False, ["Gestein","Gift"],    0, 1, "anego.png",        None,         None)

# Dreepy line – Dragon/Ghost; Dreepy(=Venicro)→28, Drakloak→50 – keeping as 2-stage per game
Venicro      = M("Venicro",      "epic",      True,  ["Drache","Geist"],   50, 1, "venicro.png",      None,         "Agoyon")
Agoyon       = M("Agoyon",       "epic",      False, ["Drache","Geist"],    0, 2, "agoyon.png",       "Venicro",    None)
# NOTE: Dreepy line is Dragon/Ghost, not Poison

# Custom
Muramura     = M("Muramura",     "epic",      False, ["Gestein","Psycho"],  0, 1, "muramura.png",     None,         None)
Kopplosio    = M("Kopplosio",    "epic",      False, ["Feuer","Geist"],     0, 1, "kopplosio.png",    None,         None)

# Zeraora – Electric
Zeraora      = M("Zeraora",      "legendary", False, ["Elektro"],           0, 1, "zeraora.png",      None,         None)

# Toxel line – Electric/Poison; Toxel→30
Toxel        = M("Toxel",        "common",    True,  ["Gift","Elektro"],   30, 1, "toxel.png",        None,         ["Riffex Hochform","Riffex Tiefform"])
RiffexHoch   = M("Riffex Hochform","rare",    False, ["Gift","Elektro"],    0, 2, "riffexHoch.png",   "Toxel",      None)
RiffexTief   = M("Riffex Tiefform","rare",    False, ["Gift","Elektro"],    0, 2, "riffexTief.png",   "Toxel",      None)

# Custom
Beatori      = M("Beatori",      "epic",      False, ["Gift","Fee"],        0, 1, "beatori.png",      None,         None)

# Aipom line – Normal; Aipom(=Griffel)→32
Griffel      = M("Griffel",      "common",    True,  ["Normal"],           32, 1, "griffel.png",      None,         "Ambidiffel")
Ambidiffel   = M("Ambidiffel",   "uncommon",  False, ["Normal"],            0, 2, "ambidiffel.png",   "Griffel",    None)

# Hoothoot line – Normal/Flying; Hoothoot(=Haspiror)→20
Haspiror     = M("Haspiror",     "common",    True,  ["Normal","Flug"],    20, 1, "haspiror.png",     None,         "Schlapor")
Schlapor     = M("Schlapor",     "uncommon",  False, ["Normal","Flug"],     0, 2, "schlapor.png",     "Haspiror",   None)

# Rattata line – Normal; Rattata(=Eneco)→20
Eneco        = M("Eneco",        "common",    True,  ["Normal"],           20, 1, "eneco.png",        None,         "Enekoro")
Enekoro      = M("Enekoro",      "uncommon",  False, ["Normal"],            0, 2, "enekoro.png",      "Eneco",      None)

# Doduo line already done above

# Spearow line – Normal/Flying; Spearow(=Dummisel)→20
Dummisel     = M("Dummisel",     "common",    True,  ["Normal","Flug"],    20, 1, "dummisel.png",     None,         "Dummimisel")
Dummimisel   = M("Dummimisel",   "uncommon",  False, ["Normal","Flug"],     0, 2, "dummimisel.png",   "Dummisel",   None)

# Custom standalones
Farbeagle    = M("Farbeagle",    "rare",      False, ["Normal"],            0, 1, "farbeagle.png",    None,         None)
Miltank      = M("Miltank",      "uncommon",  False, ["Normal"],            0, 1, "miltank.png",      None,         None)

# Happiny line – Normal; Happiny(=Wonneira)→16, Chansey(=Chaneira)→30 (Glück-Ei sim)
Wonneira     = M("Wonneira",     "rare",      True,  ["Normal"],           16, 1, "wonneira.png",     None,         "Chaneira")
Chaneira     = M("Chaneira",     "uncommon",  True,  ["Normal"],           30, 2, "chaneira.png",     "Wonneira",   "Heiteira")
Heiteira     = M("Heiteira",     "epic",      False, ["Normal"],            0, 3, "heiteira.png",     "Chaneira",   None)

# Slakoth line – Normal; Slakoth(=Bummelz)→18, Vigoroth(=Muntier)→36
Bummelz      = M("Bummelz",      "common",    True,  ["Normal"],           18, 1, "bummelz.png",      None,         "Muntier")
Muntier      = M("Muntier",      "uncommon",  True,  ["Normal"],           36, 2, "muntier.png",      "Bummelz",    "Letarking")
Letarking    = M("Letarking",    "epic",      False, ["Normal"],            0, 3, "letarking.png",    "Muntier",    None)

# Shroomish line – Grass→Grass/Fighting; Shroomish(=Knilz)→23
Knilz        = M("Knilz",        "common",    True,  ["Pflanze"],          23, 1, "knilz.png",        None,         "Kapilz")
Kapilz       = M("Kapilz",       "uncommon",  False, ["Pflanze","Kampf"],   0, 2, "kapilz.png",       "Knilz",      None)

# Whismur line – Normal; Whismur(=Flurmel)→20, Loudred(=Krakeelo)→40
Flurmel      = M("Flurmel",      "common",    True,  ["Normal"],           20, 1, "flurmel.png",      None,         "Krakeelo")
Krakeelo     = M("Krakeelo",     "uncommon",  True,  ["Normal"],           40, 2, "krakeelo.png",     "Flurmel",    "Krawumms")
Krawumms     = M("Krawumms",     "epic",      False, ["Normal"],            0, 3, "krawumms.png",     "Krakeelo",   None)

# Standalones
Pandir       = M("Pandir",       "common",    False, ["Normal"],            0, 1, "pandir.png",       None,         None)
Sengo        = M("Sengo",        "common",    False, ["Normal"],            0, 1, "sengo.png",        None,         None)
Plaudagei    = M("Plaudagei",    "rare",      False, ["Normal","Flug"],     0, 1, "plaudagei.png",    None,         None)

# Snorlax with pre-evo Munchlax(=Mampfaxo)→20
Mampfaxo     = M("Mampfaxo",     "common",    True,  ["Normal"],           20, 1, "mampfaxo.png",     None,         "Relaxo")
Relaxo       = M("Relaxo",       "epic",      False, ["Normal"],            0, 2, "relaxo.png",       "Mampfaxo",   None)

Ohrdoch      = M("Ohrdoch",      "common",    False, ["Normal"],            0, 1, "ohrdoch.png",      None,         None)

# Darumaka line – Fire; Darumaka(=Dakuma)→35
Dakuma       = M("Dakuma",       "rare",      True,  ["Feuer"],            35, 1, "dakuma.png",       None,         "Darmodus")
# Darmanitan not in file – keeping Dakuma standalone as in original
Dakuma       = M("Dakuma",       "rare",      False, ["Feuer"],             0, 1, "dakuma.png",       None,         None)

# Kubfu – Fighting; Kubfu→70 (into Urshifu, sim lv40)
Wulaosu      = M("Wulaosu",      "uncommon",  False, ["Kampf"],             0, 1, "wulaosu.png",      None,         None)

# Sandshrew line – Ground; Sandshrew(=Sandan)→22
Sandan       = M("Sandan",       "common",    True,  ["Boden"],            22, 1, "sandan.png",       None,         "Sandamer")
Sandamer     = M("Sandamer",     "uncommon",  False, ["Boden"],             0, 2, "sandamer.png",     "Sandan",     None)

# Squirtle line – Water; Squirtle(=Schiggy)→16, Wartortle(=Schillok)→36
Schiggy      = M("Schiggy",      "rare",      True,  ["Wasser"],           16, 1, "schiggy.png",      None,         "Schillok")
Schillok     = M("Schillok",     "uncommon",  True,  ["Wasser"],           36, 2, "schillok.png",     "Schiggy",    "Turtok")
Turtok       = M("Turtok",       "epic",      False, ["Wasser"],            0, 3, "turtok.png",       "Schillok",   None)

# Sneasel line – Dark/Ice; Sneasel(=Sniebel)→33
Sniebel      = M("Sniebel",      "uncommon",  True,  ["Unlicht","Eis"],    33, 1, "Sniebel.png",      None,         "Snibunna")
Snibunna     = M("Snibunna",     "epic",      False, ["Unlicht","Eis"],     0, 2, "Snibunna.png",     "Sniebel",    None)

# Custom
PsychoAndreas= M("Psycho Andreas","legendary",False, ["Psycho","Unlicht"],  0, 1, "psychoAndreas.png",None,         None)

# Kingdra: Seadra(=Seeper)→32→Seemon (Drache Schuppe sim)
Seeper       = M("Seeper",       "common",    True,  ["Wasser"],           32, 1, "seeper.png",       None,         "Seemon")
Seemon       = M("Seemon",       "rare",      False, ["Wasser","Drache"],   0, 2, "seemon.png",       "Seeper",     None)

# Scyther/Scizor – Bug/Flying→Bug/Steel (Sichlor=Scizor)
Sichlor      = M("Sichlor",      "epic",      False, ["Käfer","Stahl"],     0, 1, "sichlor.png",      None,         None)

# Staryu line – Water; Staryu(=Sterndu)→30 (Wasserstern sim), Starmie Water/Psychic
Sterndu      = M("Sterndu",      "common",    True,  ["Wasser"],           30, 1, "sterndu.png",      None,         "Starmie")
Starmie      = M("Starmie",      "epic",      False, ["Wasser","Psycho"],   0, 2, "starmie.png",      "Sterndu",    None)

# Rossana – Psychic/Fairy (Mr. Mime) – standalone
Rossana      = M("Rossana",      "rare",      False, ["Psycho","Fee"],      0, 1, "rossana.png",      None,         None)

# Porygon line already done

# Lapras – Water/Ice
Lapras       = M("Lapras",       "epic",      False, ["Wasser","Eis"],      0, 1, "lapras.png",       None,         None)

# Ledyba line – Bug/Flying; Ledyba→18
Ledyba       = M("Ledyba",       "common",    True,  ["Käfer","Flug"],     18, 1, "ledyba.png",       None,         "Ledian")
Ledian       = M("Ledian",       "uncommon",  False, ["Käfer","Flug"],      0, 2, "ledian.png",       "Ledyba",     None)

# Prowl line (custom)
Prowlad      = M("Prowlad",      "epic",      True,  ["Unlicht"],          25, 1, "prowlad.png",      None,         "Prowlow")
Prowlow      = M("Prowlow",      "epic",      True,  ["Unlicht"],          40, 2, "prowlow.png",      "Prowlad",    "Prowlesh")
Prowlesh     = M("Prowlesh",     "epic",      False, ["Unlicht","Kampf"],   0, 3, "prowlesh.png",     "Prowlow",    None)

# Custom
Quajutsu     = M("Quajutsu",     "epic",      False, ["Wasser","Unlicht"],  0, 3, "quajutsu.png",     None,         None)

# Poliwag line – Water; Poliwag(=Quapsel)→25, Poliwhirl(=Quaputzi)→36 (Wasserstein sim)
Quapsel      = M("Quapsel",      "common",    True,  ["Wasser"],           25, 1, "quapsel.png",      None,         "Quaputzi")
Quaputzi     = M("Quaputzi",     "uncommon",  True,  ["Wasser"],           36, 2, "quaputzi.png",     "Quapsel",    "Quappo")
Quappo       = M("Quappo",       "rare",      False, ["Wasser","Kampf"],    0, 3, "quappo.png",       "Quaputzi",   None)

# ══════════════════════════════════════════════════════════════════════════════
# NEW POKEMON from image folder (kept as-is, only obvious fixes applied)
# ══════════════════════════════════════════════════════════════════════════════

Aalabyss     = M("Aalabyss",     "epic",      False, ["Wasser","Unlicht"],  0, 1, "aalabyss.png",     None,         None)
Absol        = M("Absol",        "rare",      False, ["Unlicht"],           0, 1, "absol.png",        None,         None)
Admurai      = M("Admurai",      "rare",      False, ["Wasser","Käfer"],    0, 1, "admurai.png",      None,         None)
Aeropteryx   = M("Aeropteryx",   "uncommon",  False, ["Gestein","Flug"],    0, 1, "aeropteryx.png",   None,         None)
Amagarga     = M("Amagarga",     "uncommon",  True,  ["Feuer","Gestein"],  30, 1, "amagarga.png",     None,         "Amarino")
Amarino      = M("Amarino",      "rare",      False, ["Feuer","Gestein"],   0, 2, "amarino.png",      "Amagarga",   None)
Ampharos     = M("Ampharos",     "rare",      False, ["Elektro"],           0, 3, "ampharos.png",     None,         None)
Amphizel     = M("Amphizel",     "uncommon",  False, ["Wasser","Elektro"],  0, 1, "amphizel.png",     None,         None)
Apoquallyp   = M("Apoquallyp",   "epic",      False, ["Wasser","Geist"],    0, 1, "apoquallyp.png",   None,         None)
Arboretoss   = M("Arboretoss",   "uncommon",  False, ["Pflanze","Geist"],   0, 1, "arboretoss.png",   None,         None)
Backel       = M("Backel",       "common",    True,  ["Unlicht"],          20, 1, "backel.png",       None,         None)
Bailonda     = M("Bailonda",     "rare",      False, ["Feuer","Kampf"],     0, 1, "bailonda.png",     None,         None)
Bandelby     = M("Bandelby",     "common",    False, ["Normal"],            0, 1, "bandelby.png",     None,         None)
Banette      = M("Banette",      "rare",      False, ["Geist"],             0, 2, "banette.png",      "Shuppet",    None)
Baojian      = M("Baojian",      "epic",      False, ["Unlicht","Käfer"],   0, 1, "baojian.png",      None,         None)
Barschwa     = M("Barschwa",     "uncommon",  False, ["Wasser"],            0, 1, "barschwa.png",     None,         None)
Bauz         = M("Bauz",         "common",    True,  ["Pflanze","Flug"],   18, 1, "bauz.png",         None,         None)
Bellektro    = M("Bellektro",    "uncommon",  False, ["Elektro"],           0, 1, "bellektro.png",    None,         None)
Blanas       = M("Blanas",       "common",    True,  ["Wasser"],           20, 1, "blanas.png",       None,         None)
Blubella     = M("Blubella",     "uncommon",  False, ["Wasser","Fee"],      0, 1, "blubella.png",     None,         None)
Bluzuk       = M("Bluzuk",       "common",    True,  ["Käfer"],            20, 1, "bluzuk.png",       None,         None)
Botogel      = M("Botogel",      "uncommon",  False, ["Wasser"],            0, 1, "botogel.png",      None,         None)
Brimano      = M("Brimano",      "uncommon",  True,  ["Feuer"],            25, 1, "brimano.png",      None,         "Brimova")
Brimova      = M("Brimova",      "rare",      False, ["Feuer"],             0, 2, "brimova.png",      "Brimano",    None)
Brutalanda   = M("Brutalanda",   "epic",      False, ["Drache","Flug"],     0, 1, "brutalanda.png",   None,         None)
Bunbungus    = M("Bunbungus",    "uncommon",  False, ["Pflanze","Gift"],    0, 1, "bunbungus.png",    None,         None)
Bähmon       = M("Bähmon",       "uncommon",  False, ["Normal"],            0, 1, "bähmon.png",       None,         None)
Caesurio     = M("Caesurio",     "uncommon",  False, ["Kampf"],             0, 1, "caesurio.png",     None,         None)
Calamanero   = M("Calamanero",   "epic",      False, ["Unlicht","Psycho"],  0, 1, "calamanero.png",   None,         None)
Camaub       = M("Camaub",       "common",    True,  ["Feuer","Boden"],    33, 1, "camaub.png",       None,         "Camerupt")
Camerupt     = M("Camerupt",     "rare",      False, ["Feuer","Boden"],     0, 2, "camerupt.png",     "Camaub",     None)
Chillabell   = M("Chillabell",   "uncommon",  False, ["Eis","Geist"],       0, 1, "chillabell.png",   None,         None)
Chimpep      = M("Chimpep",      "common",    True,  ["Normal"],           20, 1, "chimpep.png",      None,         None)
Chimstix     = M("Chimstix",     "common",    False, ["Normal"],            0, 1, "chimstix.png",     None,         None)
Coiffwaff    = M("Coiffwaff",    "uncommon",  False, ["Normal"],            0, 1, "coiffwaff.png",    None,         None)
Colossand    = M("Colossand",    "rare",      False, ["Boden","Kampf"],     0, 1, "colossand.png",    None,         None)
Corasonn     = M("Corasonn",     "uncommon",  True,  ["Feuer","Psycho"],   28, 1, "corasonn.png",     None,         "Gorgasonn")
Gorgasonn    = M("Gorgasonn",    "rare",      False, ["Feuer","Psycho"],    0, 2, "gorgasonn.png",    "Corasonn",   None)
Cottini      = M("Cottini",      "common",    True,  ["Pflanze","Fee"],    15, 1, "cottini.png",      None,         "Cottomi")
Cottomi      = M("Cottomi",      "uncommon",  False, ["Pflanze","Fee"],     0, 2, "cottomi.png",      "Cottini",    None)
Cupidos      = M("Cupidos",      "uncommon",  False, ["Fee","Flug"],        0, 1, "cupidos.png",      None,         None)
Curelei      = M("Curelei",      "rare",      False, ["Fee","Psycho"],      0, 1, "curelei.png",      None,         None)
Darkrai      = M("Darkrai",      "legendary", False, ["Unlicht"],           0, 1, "darkrai.png",      None,         None)
Dartignis    = M("Dartignis",    "common",    True,  ["Feuer"],            20, 1, "dartignis.png",    None,         "Dartiri")
Dartiri      = M("Dartiri",      "uncommon",  False, ["Feuer"],             0, 2, "dartiri.png",      "Dartignis",  None)
Dedenne      = M("Dedenne",      "uncommon",  False, ["Elektro","Fee"],     0, 1, "dedenne.png",      None,         None)
Deoxys       = M("Deoxys",       "legendary", False, ["Psycho"],            0, 1, "deoxys.png",       None,         None)
Despotar     = M("Despotar",     "epic",      False, ["Gestein","Unlicht"],  0, 3,"despotar.png",     "Pupitar",    None)
Donphan      = M("Donphan",      "rare",      False, ["Boden"],             0, 2, "donphan.png",      "Phanpy",     None)
Donarion     = M("Donarion",     "rare",      False, ["Elektro"],           0, 1, "donarion.png",     None,         None)
Draschel     = M("Draschel",     "uncommon",  True,  ["Drache"],           20, 1, "draschel.png",     None,         None)
Dressella    = M("Dressella",    "rare",      False, ["Gift","Fee"],        0, 1, "dressella.png",    None,         None)
Driftlon     = M("Driftlon",     "uncommon",  True,  ["Geist"],            28, 1, "driftlon.png",     None,         "Drifzepeli")
Drifzepeli   = M("Drifzepeli",   "rare",      False, ["Geist"],             0, 2, "drifzepeli.png",   "Driftlon",   None)
Duodino      = M("Duodino",      "uncommon",  True,  ["Drache"],           30, 1, "duodino.png",      None,         None)
Duokles      = M("Duokles",      "uncommon",  True,  ["Geist","Pflanze"],  28, 1, "duokles.png",      None,         None)
Duraludon    = M("Duraludon",    "rare",      False, ["Stahl","Drache"],    0, 1, "duraludon.png",    None,         None)
Durengard    = M("Durengard",    "rare",      False, ["Stahl"],             0, 1, "durengard.png",    None,         None)
EFeM         = M("E-FeM",        "legendary", False, ["Elektro","Fee"],     0, 1, "eFeM.png",         None,         None)
Elekid       = M("Elekid",       "common",    True,  ["Elektro"],          30, 1, "elekid.png",       None,         "Elektek")
Elektek      = M("Elektek",      "uncommon",  True,  ["Elektro"],          30, 2, "elektek.png",      "Elekid",     "Elevoltek")
Elevoltek    = M("Elevoltek",    "rare",      False, ["Elektro"],           0, 3, "elevoltek.png",    "Elektek",    None)
# NOTE: Elekid→30→Electabuzz, Electabuzz→Electivire (Elektroisierer item, sim lv40)
Elekid       = M("Elekid",       "common",    True,  ["Elektro"],          30, 1, "elekid.png",       None,         "Elektek")
Elektek      = M("Elektek",      "uncommon",  True,  ["Elektro"],          40, 2, "elektek.png",      "Elekid",     "Elevoltek")
Elevoltek    = M("Elevoltek",    "rare",      False, ["Elektro"],           0, 3, "elevoltek.png",    "Elektek",    None)
Elfun        = M("Elfun",        "uncommon",  False, ["Pflanze"],           0, 1, "elfun.png",        None,         None)
Emolga       = M("Emolga",       "uncommon",  False, ["Elektro","Flug"],    0, 1, "emolga.png",       None,         None)
Famieps      = M("Famieps",      "common",    False, ["Normal"],            0, 1, "famieps.png",      None,         None)
Farigriaf    = M("Farigriaf",    "rare",      False, ["Normal","Psycho"],   0, 1, "farigriaf.png",    None,         None)
Fatalitee    = M("Fatalitee",    "epic",      False, ["Geist"],             0, 1, "fatalitee.png",    None,         None)
Felilou      = M("Felilou",      "uncommon",  False, ["Normal"],            0, 1, "felilou.png",      None,         None)
Feliospa     = M("Feliospa",     "common",    False, ["Normal"],            0, 1, "feliospa.png",     None,         None)
Felori       = M("Felori",       "common",    True,  ["Normal"],           20, 1, "felori.png",       None,         None)
Fennexis     = M("Fennexis",     "uncommon",  False, ["Feuer"],             0, 1, "fennexis.png",     None,         None)
Ferkokel     = M("Ferkokel",     "common",    True,  ["Feuer","Käfer"],    20, 1, "ferkokel.png",     None,         None)
Fiaro        = M("Fiaro",        "common",    False, ["Feuer"],             0, 1, "fiaro.png",        None,         None)
Finneon      = M("Finneon",      "common",    True,  ["Wasser"],           31, 1, "finneon.png",      None,         "Lumineon")
Lumineon     = M("Lumineon",     "uncommon",  False, ["Wasser"],            0, 2, "lumineon.png",     "Finneon",    None)
Firnotor     = M("Firnotor",     "rare",      False, ["Feuer","Stahl"],     0, 1, "firnotor.png",     None,         None)
Flabebe      = M("Flabebe",      "common",    True,  ["Fee"],              19, 1, "flabebe.png",      None,         "Floette")
Floette      = M("Floette",      "uncommon",  True,  ["Fee"],              32, 2, "floette.png",      "Flabebe",    "Florges")
Florges      = M("Florges",      "rare",      False, ["Fee"],               0, 3, "florges.png",      "Floette",    None)
Flambirex    = M("Flambirex",    "epic",      False, ["Feuer","Drache"],    0, 1, "flambirex.png",    None,         None)
Flamiau      = M("Flamiau",      "common",    True,  ["Feuer"],            20, 1, "flamiau.png",      None,         None)
Flaniwal     = M("Flaniwal",     "uncommon",  False, ["Feuer","Wasser"],    0, 1, "flaniwal.png",     None,         None)
Flapteryx    = M("Flapteryx",    "uncommon",  False, ["Flug","Drache"],     0, 1, "flapteryx.png",    None,         None)
Flauschling  = M("Flauschling",  "uncommon",  False, ["Normal","Fee"],      0, 1, "flauschling.png",  None,         None)
Fleknoil     = M("Fleknoil",     "uncommon",  False, ["Unlicht"],           0, 1, "fleknoil.png",     None,         None)
Flemmli      = M("Flemmli",      "common",    True,  ["Feuer"],            18, 1, "flemmli.png",      None,         None)
Fletiamo     = M("Fletiamo",     "uncommon",  False, ["Feuer"],             0, 1, "fletiamo.png",     None,         None)
Floink       = M("Floink",       "common",    True,  ["Feuer"],            20, 1, "floink.png",       None,         None)
Flunkifer    = M("Flunkifer",    "rare",      False, ["Geist"],             0, 1, "flunkifer.png",    None,         None)
Flunschlik   = M("Flunschlik",   "common",    True,  ["Wasser"],           18, 1, "flunschlik.png",   None,         None)
Forgita      = M("Forgita",      "uncommon",  True,  ["Stahl"],            25, 1, "forgita.png",      None,         "Granforgita")
Granforgita  = M("Granforgita",  "rare",      False, ["Stahl"],             0, 2, "granforgita.png",  "Forgita",    None)
Friedwuff    = M("Friedwuff",    "uncommon",  False, ["Normal"],            0, 1, "friedwuff.png",    None,         None)
Frizelbliz   = M("Frizelbliz",   "rare",      False, ["Elektro","Eis"],     0, 1, "frizelbliz.png",   None,         None)
Frosdedje    = M("Frosdedje",    "rare",      False, ["Eis"],               0, 1, "frosdedje.png",    None,         None)
Froxy        = M("Froxy",        "uncommon",  False, ["Wasser"],            0, 1, "froxy.png",        None,         None)
Frubaila     = M("Frubaila",     "common",    True,  ["Pflanze"],          18, 1, "frubaila.png",     None,         "Frubberl")
Frubberl     = M("Frubberl",     "uncommon",  True,  ["Pflanze"],          28, 2, "frubberl.png",     "Frubaila",   "Fruyal")
Fruyal       = M("Fruyal",       "rare",      False, ["Pflanze"],           0, 3, "fruyal.png",       "Frubberl",   None)
Fuegro       = M("Fuegro",       "uncommon",  False, ["Feuer"],             0, 1, "fuegro.png",       None,         None)
Fuentente    = M("Fuentente",    "uncommon",  False, ["Wasser","Fee"],      0, 1, "fuentente.png",    None,         None)
Fynx         = M("Fynx",         "uncommon",  False, ["Feuer"],             0, 1, "fynx.png",         None,         None)
GalarFlunschlik=M("Galar Flunschlik","uncommon",False,["Geist","Wasser"],   0, 1, "galarFlunschlik.png",None,       None)
GalarCorasonn= M("Galar Corasonn","uncommon", False, ["Psycho","Feuer"],    0, 1, "galarCorasonn.png",None,         None)
Gehweiher    = M("Gehweiher",    "common",    False, ["Wasser"],            0, 1, "gehweiher.png",    None,         None)
Gelatini     = M("Gelatini",     "common",    True,  ["Normal"],           15, 1, "gelatini.png",     None,         "Gelatroppo")
Gelatroppo   = M("Gelatroppo",   "uncommon",  True,  ["Normal"],           28, 2, "gelatroppo.png",   "Gelatini",   "Gelatwino")
Gelatwino    = M("Gelatwino",    "rare",      False, ["Normal"],            0, 3, "gelatwino.png",    "Gelatroppo", None)
Genesect     = M("Genesect",     "legendary", False, ["Käfer","Stahl"],     0, 1, "genesect.png",     None,         None)
Georok       = M("Georok",       "common",    True,  ["Gestein"],          20, 1, "georok.png",       None,         "Geowaz")
Geowaz       = M("Geowaz",       "uncommon",  False, ["Gestein"],           0, 2, "geowaz.png",       "Georok",     None)
Girafarig    = M("Girafarig",    "rare",      False, ["Normal","Psycho"],   0, 1, "girafarig.png",    None,         None)
Gladiantri   = M("Gladiantri",   "uncommon",  True,  ["Kampf"],            25, 1, "gladiantri.png",   None,         "Gladimperio")
Gladimperio  = M("Gladimperio",  "rare",      False, ["Kampf"],             0, 2, "gladimperio.png",  "Gladiantri", None)
Golbat       = M("Golbat",       "uncommon",  False, ["Gift","Flug"],       0, 2, "golbat.png",       "Iksbat",     None)
# Golbat gets pre-evo Zubat (=Iksbat/Zubat)
Golbit       = M("Golbit",       "rare",      False, ["Unlicht"],           0, 1, "golbit.png",       None,         None)
Golgantes    = M("Golgantes",    "epic",      False, ["Kampf"],             0, 1, "golgantes.png",    None,         None)
Golldra      = M("Golldra",      "rare",      False, ["Drache","Feuer"],    0, 1, "golldra.png",      None,         None)
Gortrom      = M("Gortrom",      "uncommon",  False, ["Normal"],            0, 1, "gortrom.png",      None,         None)
Gramokles    = M("Gramokles",    "rare",      False, ["Geist","Pflanze"],   0, 1, "gramokles.png",    None,         None)
Grandiras    = M("Grandiras",    "epic",      False, ["Drache"],            0, 3, "grandiras.png",    "Mediras",    None)
Gruff        = M("Gruff",        "uncommon",  False, ["Normal"],            0, 1, "gruff.png",        None,         None)
Hefel        = M("Hefel",        "uncommon",  False, ["Normal"],            0, 1, "hefel.png",        None,         None)
HisuiDressella=M("Hisui Dressella","rare",   False, ["Gift","Pflanze"],    0, 1, "hisuiDressella.png",None,        None)
HisuiZorua  = M("Hisui Zorua",   "uncommon",  True,  ["Normal","Geist"],   20, 1, "hisuiZorua.png",  None,         "Hisui Zoroark")
HisuiZoroark=M("Hisui Zoroark", "rare",      False, ["Normal","Geist"],    0, 2, "hisuiZoroark.png", "Hisui Zorua",None)
Hokumil      = M("Hokumil",      "common",    False, ["Normal"],            0, 1, "hokumil.png",      None,         None)
Honweisel    = M("Honweisel",    "uncommon",  False, ["Normal","Flug"],     0, 1, "honweisel.png",    None,         None)
Hopplo       = M("Hopplo",       "common",    True,  ["Feuer"],            18, 1, "hopplo.png",       None,         None)
Hoppspross   = M("Hoppspross",   "uncommon",  True,  ["Pflanze"],          20, 1, "hoppspross.png",   None,         None)
Hubelupf     = M("Hubelupf",     "common",    False, ["Normal"],            0, 1, "hubelupf.png",     None,         None)
Hundemon     = M("Hundemon",     "common",    True,  ["Feuer"],            20, 1, "hundemon.png",     None,         "Hunduster")
Hunduster    = M("Hunduster",    "uncommon",  False, ["Feuer"],             0, 2, "hunduster.png",    "Hundemon",   None)
Hydropi      = M("Hydropi",      "uncommon",  False, ["Wasser"],            0, 1, "hydropi.png",      None,         None)
Hypno        = M("Hypno",        "rare",      False, ["Psycho"],            0, 2, "hypno.png",        None,         None)
Hypnomorba   = M("Hypnomorba",   "epic",      False, ["Psycho","Geist"],    0, 1, "hypnomorba.png",   None,         None)
Icognito     = M("Icognito",     "rare",      False, ["Normal"],            0, 1, "icognito.png",     None,         None)
Ignivor      = M("Ignivor",      "uncommon",  False, ["Feuer"],             0, 1, "ignivor.png",      None,         None)
Iksbat       = M("Iksbat",       "common",    True,  ["Gift","Flug"],      22, 1, "iksbat.png",       None,         "Golbat")
Imantis      = M("Imantis",      "uncommon",  False, ["Käfer","Psycho"],    0, 1, "imantis.png",      None,         None)
Impoleon     = M("Impoleon",     "epic",      False, ["Wasser","Stahl"],    0, 3, "impoleon.png",     "Plinfa",     None)
Infernopod   = M("Infernopod",   "epic",      False, ["Feuer","Kampf"],     0, 3, "infernopod.png",   None,         None)
Intelleon    = M("Intelleon",    "rare",      False, ["Wasser"],            0, 3, "intelleon.png",    None,         None)
Irrbis       = M("Irrbis",       "uncommon",  False, ["Eis","Geist"],       0, 1, "irrbis.png",       None,         None)
Iscalar      = M("Iscalar",      "epic",      False, ["Drache","Psycho"],   0, 1, "iscalar.png",      None,         None)
Isso         = M("Isso",         "common",    False, ["Normal"],            0, 1, "isso.png",         None,         None)
Jungglut     = M("Jungglut",     "uncommon",  False, ["Pflanze","Gift"],    0, 1, "jungglut.png",     None,         None)
Kanivanha    = M("Kanivanha",    "uncommon",  False, ["Wasser","Unlicht"],  0, 1, "kanivanha.png",    None,         None)
Kappalores   = M("Kappalores",   "epic",      False, ["Wasser","Kampf"],    0, 1, "kappalores.png",   None,         None)
Kapuno       = M("Kapuno",       "rare",      False, ["Wasser","Kampf"],    0, 1, "kapuno.png",       None,         None)
Katagami     = M("Katagami",     "epic",      False, ["Geist","Kampf"],     0, 1, "katagami.png",     None,         None)
Katapuldra   = M("Katapuldra",   "uncommon",  False, ["Drache"],            0, 1, "katapuldra.png",   None,         None)
Kickerlo     = M("Kickerlo",     "common",    True,  ["Kampf"],            20, 1, "kickerlo.png",     None,         None)
Kikugi       = M("Kikugi",       "uncommon",  False, ["Pflanze"],           0, 1, "kikugi.png",       None,         None)
Kindwurm     = M("Kindwurm",     "common",    True,  ["Drache"],           20, 1, "kindwurm.png",     None,         None)
Kinoso       = M("Kinoso",       "common",    False, ["Pflanze"],           0, 1, "kinoso.png",       None,         None)
Kleinstein   = M("Kleinstein",   "common",    True,  ["Gestein"],          15, 1, "kleinstein.png",   None,         None)
Kleoparda    = M("Kleoparda",    "uncommon",  False, ["Normal"],            0, 1, "kleoparda.png",    None,         None)
Klingplim    = M("Klingplim",    "rare",      False, ["Stahl","Fee"],       0, 1, "klingplim.png",    None,         None)
Knacklion    = M("Knacklion",    "uncommon",  False, ["Normal","Boden"],    0, 1, "knacklion.png",    None,         None)
Knattatox    = M("Knattatox",    "rare",      False, ["Käfer","Gift"],      0, 2, "knattatox.png",    "Knattox",    None)
Knattox      = M("Knattox",      "uncommon",  True,  ["Käfer","Gift"],     20, 1, "knattox.png",      None,         "Knattatox")
Knirfish     = M("Knirfish",     "uncommon",  False, ["Wasser"],            0, 1, "knirfish.png",     None,         None)
Koalelu      = M("Koalelu",      "uncommon",  False, ["Normal"],            0, 1, "koalelu.png",      None,         None)
Kokowei      = M("Kokowei",      "uncommon",  False, ["Normal"],            0, 1, "kokowei.png",      None,         None)
Kolowal      = M("Kolowal",      "uncommon",  False, ["Wasser"],            0, 1, "kolowal.png",      None,         None)
Kosturso     = M("Kosturso",     "uncommon",  False, ["Normal"],            0, 1, "kosturso.png",     None,         None)
Krokel       = M("Krokel",       "common",    True,  ["Boden","Feuer"],    20, 1, "krokel.png",       None,         None)
Kryppuk      = M("Kryppuk",      "uncommon",  False, ["Geist"],             0, 1, "kryppuk.png",      None,         None)
Kubuin       = M("Kubuin",       "uncommon",  False, ["Kampf"],             0, 1, "kubuin.png",       None,         None)
Kussilla     = M("Kussilla",     "rare",      False, ["Wasser","Fee"],      0, 1, "kussilla.png",     None,         None)
Kwaks        = M("Kwaks",        "common",    True,  ["Wasser","Flug"],    18, 1, "kwaks.png",        None,         None)
Lamellux     = M("Lamellux",     "uncommon",  False, ["Käfer"],             0, 1, "lamellux.png",     None,         None)
Larvitar     = M("Larvitar",     "common",    True,  ["Gestein","Boden"],  30, 1, "larvitar.png",     None,         "Pupitar")
Laternecto   = M("Laternecto",   "uncommon",  False, ["Geist"],             0, 1, "laternecto.png",   None,         None)
Lektro       = M("Lektro",       "uncommon",  False, ["Elektro"],           0, 1, "lektro.png",       None,         None)
Leufeo       = M("Leufeo",       "uncommon",  False, ["Feuer"],             0, 1, "leufeo.png",       None,         None)
Libelldra    = M("Libelldra",    "rare",      False, ["Drache","Flug"],     0, 2, "libelldra.png",    None,         None)
Liberlo      = M("Liberlo",      "uncommon",  False, ["Kampf"],             0, 1, "liberlo.png",      None,         None)
Lichtel      = M("Lichtel",      "uncommon",  True,  ["Feuer"],            20, 1, "lichtel.png",      None,         None)
Liebiskus    = M("Liebiskus",    "uncommon",  False, ["Fee"],               0, 1, "liebiskus.png",    None,         None)
Liliep       = M("Liliep",       "uncommon",  True,  ["Gestein","Wasser"], 20, 1, "liliep.png",       None,         None)
Lilminip     = M("Lilminip",     "common",    True,  ["Pflanze"],          15, 1, "lilminip.png",     None,         None)
Linfu        = M("Linfu",        "rare",      False, ["Kampf","Drache"],    0, 1, "linfu.png",        None,         None)
Lohgock      = M("Lohgock",      "rare",      False, ["Feuer","Flug"],      0, 3, "lohgock.png",      None,         None)
Lokroko      = M("Lokroko",      "uncommon",  False, ["Boden","Unlicht"],   0, 1, "lokroko.png",      None,         None)
Loturzel     = M("Loturzel",     "common",    True,  ["Pflanze","Wasser"], 15, 1, "loturzel.png",     None,         "Lombrero")
Lombrero     = M("Lombrero",     "uncommon",  True,  ["Pflanze","Wasser"], 22, 2, "lombrero.png",     "Loturzel",   None)
Lucario      = M("Lucario",      "rare",      False, ["Kampf","Stahl"],     0, 2, "lucario.png",      "Riolu",      None)
Lunastein    = M("Lunastein",    "rare",      False, ["Gestein","Psycho"],  0, 1, "lunastein.png",    None,         None)
Luxio        = M("Luxio",        "uncommon",  True,  ["Elektro"],          30, 2, "luxio.png",        None,         "Luxtra")
Luxtra       = M("Luxtra",       "rare",      False, ["Elektro"],           0, 3, "luxtra.png",       "Luxio",      None)
Mabula       = M("Mabula",       "common",    False, ["Normal"],            0, 1, "mabula.png",       None,         None)
Magbrant     = M("Magbrant",     "rare",      False, ["Feuer"],             0, 3, "magbrant.png",     "Magmar",     None)
Magby        = M("Magby",        "common",    True,  ["Feuer"],            30, 1, "magby.png",        None,         "Magmar")
Magcargo     = M("Magcargo",     "rare",      False, ["Feuer","Gestein"],   0, 2, "magcargo.png",     None,         None)
Magearna     = M("Magearna",     "legendary", False, ["Stahl","Fee"],       0, 1, "magearna.png",     None,         None)
Magmar       = M("Magmar",       "uncommon",  True,  ["Feuer"],            40, 2, "magmar.png",       "Magby",      "Magbrant")
Mamolida     = M("Mamolida",     "uncommon",  False, ["Boden"],             0, 1, "mamolida.png",     None,         None)
Manaphy      = M("Manaphy",      "legendary", False, ["Wasser"],            0, 1, "manaphy.png",      None,         None)
Mantirps     = M("Mantirps",     "common",    True,  ["Wasser","Flug"],    18, 1, "mantirps.png",     None,         "Mantax")
Mantax       = M("Mantax",       "rare",      False, ["Wasser","Flug"],     0, 2, "mantax.png",       "Mantirps",   None)
Mantidea     = M("Mantidea",     "uncommon",  False, ["Käfer"],             0, 1, "mantidea.png",     None,         None)
Maracamba    = M("Maracamba",    "rare",      False, ["Pflanze"],           0, 1, "maracamba.png",    None,         None)
Marikeck     = M("Marikeck",     "common",    False, ["Normal","Flug"],     0, 1, "marikeck.png",     None,         None)
Marshadow    = M("Marshadow",    "legendary", False, ["Kampf","Geist"],     0, 1, "marshadow.png",    None,         None)
Maskagato    = M("Maskagato",    "uncommon",  False, ["Unlicht"],           0, 1, "maskagato.png",    None,         None)
Maskeregen   = M("Maskeregen",   "rare",      False, ["Wasser","Geist"],    0, 1, "maskeregen.png",   None,         None)
Mediras      = M("Mediras",      "common",    True,  ["Drache"],           32, 2, "mediras.png",      "Miniras",    "Grandiras")
Meditalis    = M("Meditalis",    "uncommon",  False, ["Kampf","Psycho"],    0, 2, "meditalis.png",    "Meditie",    None)
Meditie      = M("Meditie",      "common",    True,  ["Kampf","Psycho"],   37, 1, "meditie.png",      None,         "Meditalis")
Memmeon      = M("Memmeon",      "uncommon",  False, ["Wasser"],            0, 1, "memmeon.png",      None,         None)
Metagross    = M("Metagross",    "epic",      False, ["Stahl","Psycho"],    0, 3, "metagross.png",    "Metang",     None)
Metang       = M("Metang",       "rare",      True,  ["Stahl","Psycho"],   45, 2, "metang.png",       None,         "Metagross")
Miezunder    = M("Miezunder",    "uncommon",  False, ["Feuer"],             0, 1, "miezunder.png",    None,         None)
Milotic      = M("Milotic",      "rare",      False, ["Wasser"],            0, 2, "milotic.png",      None,         None)
Miniras      = M("Miniras",      "common",    True,  ["Drache"],           15, 1, "miniras.png",      None,         "Mediras")
Minun        = M("Minun",        "uncommon",  False, ["Elektro"],           0, 1, "minun.png",        None,         None)
Mitodos      = M("Mitodos",      "uncommon",  False, ["Gift"],              0, 1, "mitodos.png",      None,         None)
Mobai        = M("Mobai",        "common",    True,  ["Normal"],           18, 1, "mobai.png",        None,         None)
Mogelbaum    = M("Mogelbaum",    "rare",      False, ["Pflanze","Geist"],   0, 1, "mogelbaum.png",    None,         None)
Mollimorba   = M("Mollimorba",   "uncommon",  False, ["Geist"],             0, 1, "mollimorba.png",   None,         None)
Monozyto     = M("Monozyto",     "epic",      False, ["Psycho"],            0, 1, "monozyto.png",     None,         None)
Moorabbel    = M("Moorabbel",    "uncommon",  False, ["Wasser"],            0, 1, "moorabbel.png",    None,         None)
Morbitesse   = M("Morbitesse",   "uncommon",  False, ["Geist"],             0, 1, "morbitesse.png",   None,         None)
Morpeko      = M("Morpeko",      "uncommon",  False, ["Elektro","Unlicht"], 0, 1, "morpeko.png",      None,         None)
Mortipot     = M("Mortipot",     "uncommon",  True,  ["Geist"],            20, 1, "mortipot.png",     None,         "Moruda")
Moruda       = M("Moruda",       "rare",      False, ["Geist"],             0, 2, "moruda.png",       "Mortipot",   None)
Mottineva    = M("Mottineva",    "common",    False, ["Käfer"],             0, 1, "mottineva.png",    None,         None)
Mähikel      = M("Mähikel",      "uncommon",  False, ["Normal"],            0, 1, "mähikel.png",      None,         None)
Nasgnet      = M("Nasgnet",      "rare",      False, ["Gestein","Stahl"],   0, 1, "nasgnet.png",      None,         None)
Natu         = M("Natu",         "common",    True,  ["Psycho","Flug"],    25, 1, "natu.png",         None,         "Xatu")
Xatu         = M("Xatu",         "uncommon",  False, ["Psycho","Flug"],     0, 2, "xatu.png",         "Natu",       None)
Normifin     = M("Normifin",     "uncommon",  False, ["Wasser"],            0, 1, "normifin.png",     None,         None)
Olangaar     = M("Olangaar",     "uncommon",  False, ["Drache"],            0, 1, "olangaar.png",     None,         None)
Omot         = M("Omot",         "common",    False, ["Normal"],            0, 1, "omot.png",         None,         None)
Onix         = M("Onix",         "uncommon",  False, ["Gestein","Boden"],   0, 1, "onix.png",         None,         None)
Ottaro       = M("Ottaro",       "common",    True,  ["Wasser"],           17, 1, "ottaro.png",       None,         None)
Owei         = M("Owei",         "common",    False, ["Wasser"],            0, 1, "owei.png",         None,         None)
Palimpalim   = M("Palimpalim",   "common",    False, ["Normal"],            0, 1, "palimpalim.png",   None,         None)
Pamo         = M("Pamo",         "common",    True,  ["Pflanze"],          25, 1, "pamo.png",         None,         "Pamamo")
Pamamo       = M("Pamamo",       "uncommon",  False, ["Pflanze"],           0, 2, "pamamo.png",       "Pamo",       "Pamomamo")
Pamomamo     = M("Pamomamo",     "uncommon",  False, ["Pflanze"],           0, 3, "pamomamo.png",     "Pamamo",     None)
Pampam       = M("Pampam",       "uncommon",  False, ["Normal","Fee"],      0, 1, "pampam.png",       None,         None)
Pampross     = M("Pampross",     "uncommon",  False, ["Eis"],               0, 1, "pampross.png",     None,         None)
Pampuli      = M("Pampuli",      "uncommon",  False, ["Normal"],            0, 1, "pampuli.png",      None,         None)
Pandagro     = M("Pandagro",     "uncommon",  False, ["Normal","Kampf"],    0, 1, "pandagro.png",     None,         None)
Panekon      = M("Panekon",      "uncommon",  False, ["Normal"],            0, 1, "panekon.png",      None,         None)
Panpyro      = M("Panpyro",      "common",    True,  ["Feuer"],            25, 1, "panpyro.png",      None,         "Panflam")
Panflam      = M("Panflam",      "uncommon",  False, ["Feuer"],             0, 2, "panflam.png",      "Panpyro",    None)
Pantimimi    = M("Pantimimi",    "uncommon",  False, ["Geist"],             0, 1, "pantimimi.png",    None,         None)
Pantimos     = M("Pantimos",     "common",    True,  ["Wasser"],           18, 1, "pantimos.png",     None,         None)
Panzaeron    = M("Panzaeron",    "epic",      False, ["Stahl","Flug"],      0, 1, "panzaeron.png",    None,         None)
Papinella    = M("Papinella",    "uncommon",  False, ["Normal","Flug"],     0, 1, "papinella.png",    None,         None)
Papungha     = M("Papungha",     "common",    True,  ["Pflanze"],          15, 1, "papungha.png",     None,         None)
Paragoni     = M("Paragoni",     "rare",      False, ["Käfer","Gestein"],   0, 1, "paragoni.png",     None,         None)
Parfi        = M("Parfi",        "uncommon",  True,  ["Fee"],              20, 1, "parfi.png",        None,         "Parfinesse")
Parfinesse   = M("Parfinesse",   "rare",      False, ["Fee"],               0, 2, "parfinesse.png",   "Parfi",      None)
Pelipper     = M("Pelipper",     "uncommon",  False, ["Wasser","Flug"],     0, 2, "pelipper.png",     "Wingull",    None)
Pelzebub     = M("Pelzebub",     "uncommon",  False, ["Unlicht"],           0, 1, "pelzebub.png",     None,         None)
Peppeck      = M("Peppeck",      "uncommon",  False, ["Normal"],            0, 1, "peppeck.png",      None,         None)
Perlu        = M("Perlu",        "rare",      False, ["Wasser"],            0, 1, "perlu.png",        None,         None)
Petznief     = M("Petznief",     "rare",      False, ["Eis"],               0, 1, "petznief.png",     None,         None)
Phandra      = M("Phandra",      "uncommon",  False, ["Geist","Drache"],    0, 1, "phandra.png",      None,         None)
Phanpy       = M("Phanpy",       "common",    True,  ["Boden"],            25, 1, "phanpy.png",       None,         "Donphan")
Phione       = M("Phione",       "rare",      False, ["Wasser"],            0, 1, "phione.png",       None,         None)
Phlegleon    = M("Phlegleon",    "uncommon",  False, ["Wasser","Feuer"],    0, 1, "phlegleon.png",    None,         None)
Piccolente   = M("Piccolente",   "uncommon",  False, ["Pflanze"],           0, 1, "piccolente.png",   None,         None)
Picochilla   = M("Picochilla",   "uncommon",  False, ["Elektro"],           0, 1, "picochilla.png",   None,         None)
Pliprin      = M("Pliprin",      "common",    True,  ["Wasser"],           18, 1, "pliprin.png",      None,         "Plinfa")
Plinfa       = M("Plinfa",       "uncommon",  True,  ["Wasser"],           36, 2, "plinfa.png",       "Pliprin",    "Impoleon")
Plusle       = M("Plusle",       "uncommon",  False, ["Elektro"],           0, 1, "plusle.png",       None,         None)
Pokusan      = M("Pokusan",      "common",    False, ["Normal"],            0, 1, "pokusan.png",      None,         None)
Pottrott     = M("Pottrott",     "uncommon",  False, ["Unlicht","Feuer"],   0, 1, "pottrott.png",     None,         None)
Primarene    = M("Primarene",    "rare",      False, ["Feuer","Kampf"],     0, 3, "primarene.png",    None,         None)
Psiau        = M("Psiau",        "uncommon",  True,  ["Psycho"],           22, 1, "psiau.png",        None,         "Psiaugon")
Psiaugon     = M("Psiaugon",     "rare",      False, ["Psycho","Drache"],   0, 2, "psiaugon.png",     "Psiau",      None)
Pudox        = M("Pudox",        "uncommon",  False, ["Normal"],            0, 1, "pudox.png",        None,         None)
Pumpdjinn    = M("Pumpdjinn",    "rare",      False, ["Geist","Feuer"],     0, 1, "pumpdjinn.png",    None,         None)
Pupitar      = M("Pupitar",      "uncommon",  True,  ["Gestein","Boden"],  55, 2, "pupitar.png",      "Larvitar",   "Despotar")
Puponcho     = M("Puponcho",     "uncommon",  False, ["Normal"],            0, 1, "puponcho.png",     None,         None)
Purmel       = M("Purmel",       "common",    True,  ["Feuer"],            15, 1, "purmel.png",       None,         None)
Pyroleo      = M("Pyroleo",      "uncommon",  False, ["Feuer"],             0, 1, "pyroleo.png",      None,         None)
Quabbel      = M("Quabbel",      "common",    True,  ["Wasser"],           18, 1, "quabbel.png",      None,         None)
Qurtel       = M("Qurtel",       "common",    True,  ["Wasser"],           18, 1, "qurtel.png",       None,         None)
Ramoth       = M("Ramoth",       "rare",      False, ["Feuer","Flug"],      0, 1, "ramoth.png",       None,         None)
Reißlaus     = M("Reißlaus",     "uncommon",  False, ["Käfer"],             0, 1, "reißlaus.png",     None,         None)
Resladero    = M("Resladero",    "epic",      False, ["Unlicht","Drache"],  0, 1, "resladero.png",    None,         None)
Rexblisar    = M("Rexblisar",    "epic",      False, ["Eis","Drache"],      0, 1, "rexblisar.png",    None,         None)
Rihorn       = M("Rihorn",       "common",    True,  ["Boden","Gestein"],  42, 1, "rihorn.png",       None,         "Rihornior")
Rihornior    = M("Rihornior",    "uncommon",  False, ["Boden","Gestein"],   0, 2, "rihornior.png",    "Rihorn",     None)
Riolu        = M("Riolu",        "uncommon",  True,  ["Kampf"],            30, 1, "riolu.png",        None,         "Lucario")
Rizeros      = M("Rizeros",      "uncommon",  False, ["Boden"],             0, 1, "rizeros.png",      None,         None)
Robball      = M("Robball",      "common",    True,  ["Normal"],           15, 1, "robball.png",      None,         None)
Rocara       = M("Rocara",       "rare",      False, ["Gestein"],           0, 1, "rocara.png",       None,         None)
Rotom        = M("Rotom",        "rare",      False, ["Elektro","Geist"],   0, 1, "rotom.png",        None,         None)
Rotomurf     = M("Rotomurf",     "epic",      False, ["Elektro","Geist"],   0, 1, "rotomurf.png",     None,         None)
Rutena       = M("Rutena",       "uncommon",  False, ["Feuer"],             0, 1, "rutena.png",       None,         None)
Sabbaione    = M("Sabbaione",    "uncommon",  False, ["Normal","Fee"],      0, 1, "sabbaione.png",    None,         None)
Samurzel     = M("Samurzel",     "uncommon",  False, ["Wasser","Kampf"],    0, 1, "samurzel.png",     None,         None)
Sanganabyss  = M("Sanganabyss",  "epic",      False, ["Wasser","Unlicht"],  0, 1, "sanganabyss.png",  None,         None)
Sankabuh     = M("Sankabuh",     "uncommon",  False, ["Gestein"],           0, 1, "sankabuh.png",     None,         None)
Schabelle    = M("Schabelle",    "uncommon",  False, ["Käfer"],             0, 1, "schabelle.png",    None,         None)
Schaloko     = M("Schaloko",     "uncommon",  False, ["Normal"],            0, 1, "schaloko.png",     None,         None)
Scheinlux    = M("Scheinlux",    "rare",      False, ["Elektro"],           0, 3, "scheinlux.png",    None,         None)
Scherox      = M("Scherox",      "epic",      False, ["Stahl","Käfer"],     0, 1, "scherox.png",      None,         None)
Schlukwech   = M("Schlukwech",   "uncommon",  False, ["Normal"],            0, 1, "schlukwech.png",   None,         None)
Schluppuck   = M("Schluppuck",   "uncommon",  False, ["Wasser"],            0, 1, "schluppuck.png",   None,         None)
Schmerbe     = M("Schmerbe",     "common",    True,  ["Wasser"],           18, 1, "schmerbe.png",     None,         None)
Schneckmag   = M("Schneckmag",   "uncommon",  False, ["Feuer","Gestein"],   0, 1, "schneckmag.png",   None,         None)
Schneppke    = M("Schneppke",    "common",    True,  ["Flug"],             18, 1, "schneppke.png",    None,         None)
Seejong      = M("Seejong",      "uncommon",  False, ["Wasser"],            0, 1, "seejong.png",      None,         None)
Seemops      = M("Seemops",      "uncommon",  False, ["Wasser"],            0, 1, "seemops.png",      None,         None)
SenLong      = M("Sen Long",     "epic",      False, ["Drache"],            0, 1, "senLong.png",      None,         None)
Servol       = M("Servol",       "uncommon",  False, ["Feuer"],             0, 1, "servol.png",       None,         None)
Sesokitz     = M("Sesokitz",     "uncommon",  False, ["Eis"],               0, 1, "sesokitz.png",     None,         None)
Shardrago    = M("Shardrago",    "epic",      False, ["Drache","Eis"],      0, 1, "shardrago.png",    None,         None)
Shnebedeck   = M("Shnebedeck",   "uncommon",  False, ["Eis"],               0, 1, "shnebedeck.png",   None,         None)
Shuppet      = M("Shuppet",      "common",    True,  ["Geist"],            37, 1, "shuppet.png",      None,         "Banette")
Siberio      = M("Siberio",      "rare",      False, ["Eis"],               0, 1, "siberio.png",      None,         None)
Silembrim    = M("Silembrim",    "uncommon",  False, ["Feuer","Geist"],     0, 1, "silembrim.png",    None,         None)
Silvarro     = M("Silvarro",     "uncommon",  False, ["Stahl"],             0, 1, "silvarro.png",     None,         None)
Skelabra     = M("Skelabra",     "uncommon",  False, ["Feuer"],             0, 1, "skelabra.png",     None,         None)
Skelokrok    = M("Skelokrok",    "uncommon",  False, ["Boden","Unlicht"],   0, 1, "skelokrok.png",    None,         None)
Skorgro      = M("Skorgro",      "uncommon",  True,  ["Geist"],            25, 1, "skorgro.png",      None,         "Skorgla")
Skorgla      = M("Skorgla",      "epic",      False, ["Geist","Drache"],    0, 2, "skorgla.png",      "Skorgro",    None)
Sleima       = M("Sleima",       "common",    True,  ["Gift"],             20, 1, "sleima.png",       None,         "Sleimok")
Sleimok      = M("Sleimok",      "uncommon",  False, ["Gift"],              0, 2, "sleimok.png",      "Sleima",     None)
Smnivora     = M("Smnivora",     "uncommon",  False, ["Normal","Unlicht"],  0, 1, "smnivora.png",     None,         None)
Smogon       = M("Smogon",       "common",    True,  ["Gift"],             35, 1, "smogon.png",       None,         "Smogmog")
Smogmog      = M("Smogmog",      "uncommon",  False, ["Gift"],              0, 2, "smogmog.png",      "Smogon",     None)
Snomnom      = M("Snomnom",      "common",    True,  ["Eis"],              20, 1, "snomnom.png",      None,         None)
Somniam      = M("Somniam",      "epic",      False, ["Psycho","Geist"],    0, 1, "somniam.png",      None,         None)
Sonnfel      = M("Sonnfel",      "rare",      False, ["Gestein","Feuer"],   0, 1, "sonnfel.png",      None,         None)
Sonnkern     = M("Sonnkern",     "common",    True,  ["Pflanze"],          18, 1, "sonnkern.png",     None,         "Sonnflora")
Sonnflora    = M("Sonnflora",    "uncommon",  False, ["Pflanze"],           0, 2, "sonnflora.png",    "Sonnkern",   None)
Stahlos      = M("Stahlos",      "uncommon",  False, ["Stahl"],             0, 1, "stahlos.png",      None,         None)
Stalobor     = M("Stalobor",     "rare",      False, ["Stahl","Boden"],     0, 1, "stalobor.png",     None,         None)
Stollunior   = M("Stollunior",   "common",    True,  ["Stahl","Gestein"],  18, 1, "stollunior.png",   None,         "Stollrak")
Stollrak     = M("Stollrak",     "uncommon",  True,  ["Stahl","Gestein"],  36, 2, "stollrak.png",     "Stollunior", "Stolloss")
Stolloss     = M("Stolloss",     "rare",      False, ["Stahl","Gestein"],   0, 3, "stolloss.png",     "Stollrak",   None)
Sumpex       = M("Sumpex",       "rare",      False, ["Wasser","Boden"],    0, 1, "sumpex.png",       None,         None)
Swaroness    = M("Swaroness",    "rare",      False, ["Wasser","Flug"],     0, 1, "swaroness.png",    None,         None)
Symvolara    = M("Symvolara",    "epic",      False, ["Psycho"],            0, 1, "symvolara.png",    None,         None)
Tafforgita   = M("Tafforgita",   "uncommon",  True,  ["Stahl"],            20, 1, "tafforgita.png",   None,         "Forgita")
Tanhel       = M("Tanhel",       "uncommon",  False, ["Stahl"],             0, 1, "tanhel.png",       None,         None)
Tectass      = M("Tectass",      "uncommon",  False, ["Käfer","Boden"],     0, 1, "tectass.png",      None,         None)
Tengulist    = M("Tengulist",    "rare",      False, ["Flug","Kampf"],      0, 1, "tengulist.png",    None,         None)
Tentacha     = M("Tentacha",     "common",    True,  ["Wasser","Gift"],    30, 1, "tentacha.png",     None,         "Tentoxa")
Tentoxa      = M("Tentoxa",      "uncommon",  False, ["Wasser","Gift"],     0, 2, "tentoxa.png",      "Tentacha",   None)
Thermopod    = M("Thermopod",    "uncommon",  False, ["Feuer"],             0, 1, "thermopod.png",    None,         None)
Tobutz       = M("Tobutz",       "uncommon",  False, ["Normal"],            0, 1, "tobutz.png",       None,         None)
Togedemaru   = M("Togedemaru",   "uncommon",  False, ["Elektro","Stahl"],   0, 1, "togedemaru.png",   None,         None)
Tohaido      = M("Tohaido",      "rare",      False, ["Wasser","Drache"],   0, 1, "tohaido.png",      None,         None)
Tortunator   = M("Tortunator",   "epic",      False, ["Feuer","Drache"],    0, 1, "tortunator.png",   None,         None)
Traumato     = M("Traumato",     "uncommon",  True,  ["Geist","Unlicht"],  20, 1, "traumato.png",     None,         None)
Traunmagil   = M("Traunmagil",   "uncommon",  True,  ["Geist"],            25, 1, "traunmagil.png",   None,         "Traunfugil")
Traunfugil   = M("Traunfugil",   "uncommon",  False, ["Geist"],             0, 2, "traunfugil.png",   "Traunmagil", None)
Trikephalo   = M("Trikephalo",   "epic",      False, ["Unlicht","Drache"],  0, 1, "trikephalo.png",   None,         None)
Trombork     = M("Trombork",     "uncommon",  False, ["Normal"],            0, 1, "trombork.png",     None,         None)
Trompeck     = M("Trompeck",     "common",    True,  ["Normal"],           18, 1, "trompeck.png",     None,         None)
Tropius      = M("Tropius",      "rare",      False, ["Pflanze","Flug"],    0, 1, "tropius.png",      None,         None)
Tukanon      = M("Tukanon",      "common",    False, ["Normal","Flug"],     0, 1, "tukanon.png",      None,         None)
UHaFnir      = M("U-Ha-Fnir",    "legendary", False, ["Unlicht","Feuer"],   0, 1, "UHaFnir.png",      None,         None)
Velursi      = M("Velursi",      "uncommon",  False, ["Normal"],            0, 1, "velursi.png",      None,         None)
Vibrava      = M("Vibrava",      "uncommon",  True,  ["Drache","Boden"],   35, 2, "vibrava.png",      None,         None)
Viscargot    = M("Viscargot",    "common",    True,  ["Gift"],             20, 1, "viscargot.png",    None,         "Viscogon")
Viscogon     = M("Viscogon",     "uncommon",  True,  ["Gift","Drache"],    38, 2, "viscogon.png",     "Viscargot",  "Viscora")
Viscora      = M("Viscora",      "rare",      False, ["Gift","Drache"],     0, 3, "viscora.png",      "Viscogon",   None)
Vivillon     = M("Vivillon",     "rare",      False, ["Käfer","Flug"],      0, 3, "vivillon.png",     None,         None)
Voldi        = M("Voldi",        "uncommon",  False, ["Elektro"],           0, 1, "voldi.png",        None,         None)
Voltenso     = M("Voltenso",     "rare",      False, ["Elektro"],           0, 1, "voltenso.png",     None,         None)
Voltilamm    = M("Voltilamm",    "uncommon",  False, ["Elektro"],           0, 1, "voltilamm.png",    None,         None)
Voltobal     = M("Voltobal",     "uncommon",  False, ["Elektro"],           0, 1, "voltobal.png",     None,         None)
Voluminas    = M("Voluminas",    "uncommon",  False, ["Flug","Normal"],     0, 1, "voluminas.png",    None,         None)
Waaty        = M("Waaty",        "common",    False, ["Normal"],            0, 1, "waaty.png",        None,         None)
Wadribie     = M("Wadribie",     "uncommon",  False, ["Normal"],            0, 1, "wadribie.png",     None,         None)
Walraisa     = M("Walraisa",     "rare",      False, ["Wasser","Eis"],      0, 1, "walraisa.png",     None,         None)
Waumboll     = M("Waumboll",     "uncommon",  False, ["Normal"],            0, 1, "waumboll.png",     None,         None)
Waumpel      = M("Waumpel",      "uncommon",  False, ["Normal"],            0, 1, "waumpel.png",      None,         None)
Welsar       = M("Welsar",       "uncommon",  False, ["Wasser","Drache"],   0, 1, "welsar.png",       None,         None)
Wielie       = M("Wielie",       "uncommon",  False, ["Wasser"],            0, 1, "wielie.png",       None,         None)
Wieshu       = M("Wieshu",       "uncommon",  False, ["Normal"],            0, 1, "wieshu.png",       None,         None)
Wingull      = M("Wingull",      "common",    True,  ["Wasser","Flug"],    25, 1, "wingull.png",      None,         "Pelipper")
Woingenau    = M("Woingenau",    "rare",      False, ["Psycho"],            0, 1, "woingenau.png",    None,         None)
Wommel       = M("Wommel",       "uncommon",  False, ["Normal"],            0, 1, "wommel.png",       None,         None)
Zobiris      = M("Zobiris",      "epic",      False, ["Geist"],             0, 1, "zobiris.png",      None,         None)
Zorua        = M("Zorua",        "uncommon",  True,  ["Unlicht"],          30, 1, "zorua.png",        None,         "Zoroark")
Zoroark      = M("Zoroark",      "rare",      False, ["Unlicht"],           0, 2, "zoroark.png",      "Zorua",      None)
Zubat        = M("Zubat",        "common",    True,  ["Gift","Flug"],      22, 1, "zubat.png",        None,         "Golbat")
Zwieps       = M("Zwieps",       "common",    False, ["Normal"],            0, 1, "zwieps.png",       None,         None)
Zwottronin   = M("Zwottronin",   "uncommon",  False, ["Elektro"],           0, 1, "zwottronin.png",   None,         None)

# ── Master registry dict ──────────────────────────────────────────────────────
import sys
ALL_MOONIES = {
    name: obj
    for name, obj in list(vars().items())
    if isinstance(obj, moonie.Moonie)
}