from poketcg.card_data import RemoteCard
from poketcg.game import GameSnapshot, PlayerSnapshot, Turn
from poketcg.visualization import CardMetadataResolver, GameVisualizer


class DummyClient:
    def __init__(self):
        self.calls = []

    def fetch(self, card_id: int) -> RemoteCard:
        self.calls.append(card_id)
        return RemoteCard(
            card_id=card_id,
            name=f"Card {card_id}",
            detail_url=f"https://example.com/{card_id}",
            image_url=f"https://example.com/{card_id}.png",
        )


def test_visualizer_renders_without_errors(tmp_path):
    client = DummyClient()

    resolver = CardMetadataResolver(client=client)

    snapshots = [
        GameSnapshot(
            active_turn=Turn.PLAYER_ONE,
            turn_count=1,
            description="After turn 1",
            players={
                Turn.PLAYER_ONE: PlayerSnapshot(
                    name="Alice",
                    deck_size=40,
                    hand_size=5,
                    discard_size=1,
                    prizes_remaining=6,
                    active_name="Card 111",
                    active_hp=60,
                    active_external_id=111,
                ),
                Turn.PLAYER_TWO: PlayerSnapshot(
                    name="Bob",
                    deck_size=39,
                    hand_size=6,
                    discard_size=0,
                    prizes_remaining=6,
                    active_name=None,
                    active_hp=0,
                    active_external_id=None,
                ),
            },
        )
    ]

    visualizer = GameVisualizer(resolver)
    output = tmp_path / "replay.html"
    visualizer.render_html(snapshots, output)

    assert output.exists()
    html = output.read_text(encoding="utf-8")
    assert "https://example.com/111.png" in html
    assert client.calls == [111]
