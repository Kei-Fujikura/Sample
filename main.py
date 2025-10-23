"""Command line demonstration for the simplified Pokemon TCG engine."""
from __future__ import annotations

import argparse

from poketcg import Attack, Deck, Player, PokemonCard, PokemonGame
from poketcg.card_data import PokemonCardClient
from poketcg.visualization import CardMetadataResolver, GameVisualizer


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


def build_remote_deck(client: PokemonCardClient, start: int, end: int) -> Deck:
    """Build a deck using card names fetched from the official database."""

    remotes = client.fetch_range(start, end)
    if not remotes:
        raise RuntimeError("カードデータが取得できませんでした。別のID範囲を指定してください。")

    cards = []
    for remote in remotes:
        hp = 60 + (remote.card_id % 5) * 10
        damage = 20 + (remote.card_id % 4) * 10
        cards.append(
            PokemonCard(
                name=remote.name,
                hp=hp,
                attacks=[Attack(name="Remote Attack", damage=damage)],
                external_id=remote.card_id,
            )
        )

    # Repeat cards until we reach 60 cards.
    while len(cards) < 60:
        cards.extend(cards)
    cards = cards[:60]
    return Deck.from_iterable(cards)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pokemon TCG シミュレーター")
    parser.add_argument("--render-html", metavar="PATH", help="シミュレーションのHTMLリプレイを保存します。")
    parser.add_argument(
        "--card-range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="カードIDの範囲を指定してデッキを生成します。例: --card-range 48000 48100",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client: PokemonCardClient | None = None

    if args.card_range:
        start, end = args.card_range
        client = PokemonCardClient()
        deck_one = build_remote_deck(client, start, end)
        deck_two = build_remote_deck(client, start, end)
    else:
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

    if args.render_html:
        metadata_client = client or PokemonCardClient()
        resolver = CardMetadataResolver(metadata_client)
        visualizer = GameVisualizer(resolver)
        visualizer.render_html(result.snapshots, args.render_html)
        print(f"Saved HTML replay to {args.render_html}")


if __name__ == "__main__":
    main()
