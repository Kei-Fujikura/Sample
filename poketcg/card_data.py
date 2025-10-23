"""Utilities for retrieving Pokemon card metadata from the official database."""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Dict, Iterable, List
from urllib.error import URLError
from urllib.request import urlopen

DETAIL_URL_TEMPLATE = "https://www.pokemon-card.com/card-search/details.php/card/{card_id}"


@dataclass(frozen=True)
class RemoteCard:
    """Description of a card resolved from the official search portal."""

    card_id: int
    name: str
    detail_url: str
    image_url: str


class _MetaTagParser(HTMLParser):
    """Minimal parser that extracts meta tag properties."""

    def __init__(self) -> None:
        super().__init__()
        self.meta: Dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs):  # type: ignore[override]
        if tag.lower() != "meta":
            return
        attr_dict = {key.lower(): value for key, value in attrs if value is not None}
        prop = attr_dict.get("property") or attr_dict.get("name")
        content = attr_dict.get("content")
        if prop and content:
            self.meta[prop] = content


class PokemonCardClient:
    """Fetch card metadata by parsing the official Pokemon Card database."""

    def __init__(self, *, timeout: float = 10.0):
        self.timeout = timeout
        self._cache: Dict[int, RemoteCard] = {}

    def build_detail_url(self, card_id: int) -> str:
        return DETAIL_URL_TEMPLATE.format(card_id=card_id)

    def fetch(self, card_id: int) -> RemoteCard:
        if card_id in self._cache:
            return self._cache[card_id]
        detail_url = self.build_detail_url(card_id)
        html = self._download(detail_url)
        parser = _MetaTagParser()
        parser.feed(html)
        name = parser.meta.get("og:title") or parser.meta.get("title")
        if not name:
            raise ValueError("Unable to extract card name from detail page")
        image_url = parser.meta.get("og:image", detail_url)
        card = RemoteCard(card_id=card_id, name=name.strip(), detail_url=detail_url, image_url=image_url.strip())
        self._cache[card_id] = card
        return card

    def fetch_range(self, start: int, end: int) -> List[RemoteCard]:
        if end < start:
            raise ValueError("end must be greater than or equal to start")
        results: List[RemoteCard] = []
        for card_id in range(start, end + 1):
            try:
                results.append(self.fetch(card_id))
            except (URLError, ValueError):
                continue
        return results

    def iter_range(self, start: int, end: int) -> Iterable[RemoteCard]:
        for card in self.fetch_range(start, end):
            yield card

    def _download(self, url: str) -> str:
        with urlopen(url, timeout=self.timeout) as response:
            data = response.read()
        return data.decode("utf-8", errors="ignore")


__all__ = ["RemoteCard", "PokemonCardClient"]
