# Pokemon TCG Sample Engine

This repository contains a small Python package that demonstrates the basic
flow of a Pokemon Trading Card Game match. The goal is to provide a clean
starting point for reinforcement learning experiments or for exploring new deck
ideas.

## Features

- Simplified card models (`PokemonCard`, `EnergyCard`, `TrainerCard`).
- Turn-based game engine that handles setup, drawing, attacking, prize cards and
  victory checks.
- Cloneable game state suitable for search or reinforcement learning agents.
- Command line demo that runs a complete game between two sample decks.
- Optional integration with the official Pokemon Card search site to build decks
  and visualizations using real card names and artwork (fetched on demand).
- HTML replay generator that shows turn-by-turn board states with referenced
  artwork.
- Pytest suite showing how to validate the flow programmatically.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Running `python main.py` will print a full turn-by-turn log for a duel between
Ash and Gary, demonstrating the basic phases of play. To run the automated
check, execute:

```bash
pytest
```

The engine is intentionally lightweight. Extend the models in `poketcg/cards.py`
and `poketcg/game.py` to add mechanics such as energy attachment, bench
management or special conditions as needed for your project.

## Using real card data and animations

The command line demo can fetch card names and artwork directly from the
official database. Supply a card ID range (the numeric suffix that appears in a
detail URL such as `https://www.pokemon-card.com/card-search/details.php/card/48342`):

```bash
python main.py --card-range 48300 48360 --render-html replay.html
```

- The simulator builds 60-card decks by repeating the cards discovered in the
  provided range. HP とダメージ値はシミュレーション用に自動生成されます。
- Artwork とカード名は実行時に公式サイトから参照され、ローカルには保存しません。
- `--render-html` オプションを指定すると、試合のスナップショットを基に HTML のリプレイが生成されます。
