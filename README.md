# MoonieQuest – AP2 Edition 🎮📚

Ein Pokémon-inspiriertes Lernspiel für deine AP2-Prüfungsvorbereitung!

## Starten
```bash
pip install pygame
python game.py
```

## Steuerung
| Taste | Aktion |
|-------|--------|
| WASD / Pfeiltasten | Bewegen |
| ENTER | Interagieren / Bestätigen |
| B | PC Box öffnen (gefangene Moonies) |
| ESC | Spiel speichern (Overworld) |

## Kampfsystem
- **⚔ Angriff** – Greife den Gegner an (manchmal erscheint eine Lernkarte als Bonus!)
- **🎯 Pokéball** – Wirf einen Ball auf wilde Moonies (klappt bei niedrigem HP besser)
- **📚 Lernkarte** – Beantworte eine AP2-Frage → heilt dein Team
- **🏃 Fliehen** – Aus wilden Kämpfen fliehen

## Lernkarten-System
- Lernkarten erscheinen automatisch während Kämpfen
- Korrekte Antworten geben XP-Bonus und heilen dein Team
- Schlüsselwörter werden verglichen (nicht exakter Match nötig)
- ESC überspringt eine Frage

## Features
- 665+ Pokémon/Moonies mit korrekten Typen, Seltenheiten & Evolutions
- 47 Trainergegner inkl. Team Rocket
- Wilde Begegnungen im hohen Gras
- Pokémon fangen & PC Box
- Shop (Bälle, Tränke)
- Level-System & XP
- Automatisches Speichern

## Dateistruktur
```
game.py          – Hauptspiel
moonie.py        – Moonie-Klasse
addPokemon.py    – Alle 665+ Pokémon
enemy.py         – Gegner-Klasse  
addEnemy.py      – Alle Trainer
flashcards.csv   – AP2 Lernkarten
assets/
  moonie/        – Pokémon-Bilder
  ppl/           – Trainer-Bilder
  shop.png
  trainer.png / trainer2.png
  pokeball.png
  grass.png
```
