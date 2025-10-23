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
- Pytest suite showing how to validate the flow programmatically.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # optional, no dependencies required yet
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
