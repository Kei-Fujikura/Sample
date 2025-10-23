"""Command line demonstration for the simplified Pokemon TCG engine."""
from __future__ import annotations

from poketcg import Attack, Deck, Player, PokemonCard, PokemonGame


def build_demo_deck(name_prefix: str) -> Deck:
    """Create a deterministic 60 card deck for demonstration purposes."""

    pikachu = PokemonCard(
        name=f"{name_prefix} Pikachu",
        hp=60,
        attacks=[Attack(name="Thunder Jolt", damage=30)],
    )
    raichu = PokemonCard(
        name=f"{name_prefix} Raichu",
        hp=90,
        attacks=[Attack(name="Electro Ball", damage=50)],
    )
    cards = [pikachu] * 40 + [raichu] * 20
    return Deck.from_iterable(cards)


def main() -> None:
    deck_one = build_demo_deck("Player One")
    deck_two = build_demo_deck("Player Two")

    player_one = Player(name="Ash", deck=deck_one)
    player_two = Player(name="Gary", deck=deck_two)

    game = PokemonGame(player_one, player_two, seed=42)
    result = game.play(max_turns=50)

    for line in result.log:
        print(line)

    if result.winner is None:
        print("Result: Draw")
    else:
        winner_name = game.players[result.winner].name
        print(f"Result: {winner_name} wins")


if __name__ == "__main__":
    main()
