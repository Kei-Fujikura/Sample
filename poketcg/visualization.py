"""Visualization helpers for rendering game progress to HTML."""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Dict, Iterable, Sequence

from .card_data import PokemonCardClient, RemoteCard
from .game import GameSnapshot, PlayerSnapshot, Turn


@dataclass
class CardMetadataResolver:
    """Resolve and cache remote card metadata for visualization."""

    client: PokemonCardClient

    def __post_init__(self) -> None:
        self._cache: Dict[int, RemoteCard] = {}

    def resolve(self, card_id: int) -> RemoteCard | None:
        if card_id in self._cache:
            return self._cache[card_id]
        try:
            card = self.client.fetch(card_id)
        except Exception:
            return None
        self._cache[card_id] = card
        return card


class GameVisualizer:
    """Render a match timeline as an HTML document."""

    def __init__(self, resolver: CardMetadataResolver | None = None):
        self.resolver = resolver or CardMetadataResolver(PokemonCardClient())

    def render_html(self, snapshots: Sequence[GameSnapshot], output_path: str | Path) -> Path:
        if not snapshots:
            raise ValueError("No snapshots to render")
        output = Path(output_path)
        html = self._build_document(snapshots)
        output.write_text(html, encoding="utf-8")
        return output

    def _build_document(self, snapshots: Sequence[GameSnapshot]) -> str:
        sections = [self._render_snapshot(index, snapshot) for index, snapshot in enumerate(snapshots, start=1)]
        joined = "\n".join(sections)
        return f"""<!DOCTYPE html>
<html lang=\"ja\">
<head>
<meta charset=\"utf-8\" />
<title>Pokemon TCG Replay</title>
<style>
body {{ font-family: 'Segoe UI', sans-serif; background: #f5f5f5; margin: 0; padding: 2rem; }}
section {{ background: #ffffff; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
section h2 {{ margin-top: 0; }}
.player {{ display: flex; gap: 1rem; align-items: center; margin-top: 1rem; }}
.player img {{ width: 120px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }}
.player .info {{ background: #f0f4ff; padding: 0.75rem 1rem; border-radius: 6px; flex: 1; }}
small {{ color: #3366cc; display: block; margin-top: 0.5rem; word-break: break-all; }}
</style>
</head>
<body>
<h1>Pokemon TCG Replay</h1>
{joined}
</body>
</html>"""

    def _render_snapshot(self, index: int, snapshot: GameSnapshot) -> str:
        turn_label = escape(snapshot.active_turn.name)
        header = f"<h2>ステップ {index}: Turn {snapshot.turn_count} ({turn_label})</h2>"
        description = f"<p>{escape(snapshot.description)}</p>"
        players_html = "".join(self._render_player(player) for player in self._players_in_order(snapshot))
        return f"<section>{header}{description}{players_html}</section>"

    def _players_in_order(self, snapshot: GameSnapshot) -> Iterable[PlayerSnapshot]:
        yield snapshot.players[Turn.PLAYER_ONE]
        yield snapshot.players[Turn.PLAYER_TWO]

    def _render_player(self, player: PlayerSnapshot) -> str:
        stats = (
            f"手札 {player.hand_size} / 山札 {player.deck_size} / トラッシュ {player.discard_size} / サイド {player.prizes_remaining}"
        )
        active_name = player.active_name or "バトル場なし"
        active_hp = f"HP {player.active_hp}" if player.active_name else ""
        metadata = self._resolve_metadata(player.active_external_id)
        image_html = self._render_image(metadata)
        reference_html = self._render_reference(metadata)
        return (
            "<div class=\"player\">"
            f"{image_html}"
            "<div class=\"info\">"
            f"<strong>{escape(player.name)}</strong><br />"
            f"{escape(active_name)} {escape(active_hp)}<br />"
            f"<span>{escape(stats)}</span>"
            f"{reference_html}"
            "</div>"
            "</div>"
        )

    def _render_image(self, metadata: RemoteCard | None) -> str:
        if metadata is None:
            return "<div class=\"placeholder\">画像なし</div>"
        return f"<img src=\"{escape(metadata.image_url)}\" alt=\"{escape(metadata.name)}\" />"

    def _render_reference(self, metadata: RemoteCard | None) -> str:
        if metadata is None:
            return ""
        return f"<small>参照: <a href=\"{escape(metadata.detail_url)}\" target=\"_blank\" rel=\"noopener\">{escape(metadata.detail_url)}</a></small>"

    def _resolve_metadata(self, card_id: int | None) -> RemoteCard | None:
        if card_id is None:
            return None
        return self.resolver.resolve(card_id)


__all__ = ["CardMetadataResolver", "GameVisualizer"]
