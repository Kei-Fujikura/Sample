from poketcg import Attack, Deck, Player, PokemonCard, PokemonGame


def build_linear_deck(prefix: str, hp: int, damage: int) -> Deck:
    card = PokemonCard(name=f"{prefix} Pokemon", hp=hp, attacks=[Attack(name="Hit", damage=damage)])
    return Deck.from_iterable([card] * 60)


def test_basic_game_flow():
    deck_one = build_linear_deck("P1", hp=60, damage=30)
    deck_two = build_linear_deck("P2", hp=50, damage=20)

    player_one = Player("Player 1", deck_one)
    player_two = Player("Player 2", deck_two)

    game = PokemonGame(player_one, player_two, seed=1)
    result = game.play(max_turns=40)

    assert result.winner is not None
    assert game.players[result.winner].name == "Player 1"
    assert any("takes the final prize" in line for line in result.log)
    assert result.snapshots
    assert result.snapshots[0].description == "Setup complete"
    assert result.snapshots[-1].description == "Game end"
    for snapshot in result.snapshots:
        assert snapshot.players
