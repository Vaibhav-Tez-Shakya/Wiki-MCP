# Game Quests Wiki

A cross-game quest/chapter wiki covering five source pages:

1. **[Skyrim Creation Club — Quest Index](skyrim-creation-club-index.md)** — 96 quest files across every Creation Club pack for *The Elder Scrolls V: Skyrim Anniversary Edition*.
   Source: https://elderscrolls.fandom.com/wiki/Quests_(Skyrim_Creation_Club)

2. **[The Witcher 3: Wild Hunt — Main Quests Index](witcher3-main-quests-index.md)** — 61 quest files covering every main-story quest, organized by chapter.
   Source: https://witcher.fandom.com/wiki/The_Witcher_3_main_quests

3. **[Dragon's Dogma 2 — Quest Index](dragons-dogma-2-quests-index.md)** — 81 quest files covering all Main Quests (Vermund, Battahl, Unmoored World) and Side Quests, including points-of-no-return groupings.
   Source: https://dragonsdogma2.wiki.fextralife.com/Quests

4. **[Dying Light 2: Stay Human — Quest Index](dying-light-2-quests-index.md)** — 149 quest files covering all Story Quests (Acts 1–3) and Side Quests (Survivor, Peacekeeper, Carriers Guild, The Baba, Peacekeeper Library, and the Bloody Ties DLC).
   Source: https://dyinglight.fandom.com/wiki/Quests_(Dying_Light_2_Stay_Human)

5. **[Uncharted 4: A Thief's End — Chapter Index](uncharted-4-chapters-index.md)** — 24 chapter files. Uncharted 4 is a linear game with no quest system, so its **chapters** are treated as the structural equivalent.
   Source: https://uncharted.fandom.com/wiki/Uncharted_4:_A_Thief%27s_End

**Total: 411 quest/chapter files across 5 games.**

## Cross-game connections

- **[[games-index|Games Index]]** — all 5 games grouped by genre (`#genre/action-rpg`, `#genre/open-world`, etc.), with genre tags now added to the frontmatter of each game's index file.
- **[[quest-connections|Quest Connections & Similarities]]** — quests/chapters from all 5 games clustered by theme (home & belonging, family & legacy, political intrigue, secrets & shadows, monster hunting, death & the undead, thieves & heists, faction allegiance).

## Structure

```
wiki/
├── README.md                            (this file)
├── skyrim-creation-club-index.md        (index for game 1)
├── witcher3-main-quests-index.md        (index for game 2)
├── dragons-dogma-2-quests-index.md      (index for game 3)
├── dying-light-2-quests-index.md        (index for game 4)
├── uncharted-4-chapters-index.md        (index for game 5)
├── skyrim-creation-club/                (96 individual quest files)
│   └── *.md
├── witcher3-main-quests/                (61 individual quest files)
│   └── *.md
├── dragons-dogma-2-quests/              (81 individual quest files)
│   └── *.md
├── dying-light-2-quests/                (149 individual quest files)
│   └── *.md
└── uncharted-4-chapters/                (24 individual chapter files)
    └── *.md
```

Each quest/chapter file contains its game, pack/act/group, level/location/difficulty where known, a source link back to the original wiki page, and a summary stub. Full walkthroughs, dialogue, NPCs, and rewards live on the linked source pages — these files are a structured index/finding-aid layer on top of them, not a copy of their content.

## Notes on link reliability

- **Skyrim**, **Dragon's Dogma 2**, and **Uncharted 4** entry links were copied directly from each source page's markup, so they're exact.
- **Witcher 3** and **Dying Light 2** quest links are constructed from the standard wiki URL pattern (spaces → underscores) since those source pages listed many quests as plain text without links. A few may need a disambiguation suffix if the direct link 404s — the index page is still the reliable route in.

## Notes on scope

- The `Assassin's Creed (series)` Fandom page fetched earlier was a franchise overview (list of games, films, novels, comics), not a quest list, so no Assassin's Creed game has been added yet. Send a specific game's quest-list page (e.g. "Quests (Assassin's Creed Valhalla)") to add one.
