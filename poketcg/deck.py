"""Deck construction helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .cards import Card


@dataclass
class Deck:
    """A shuffled stack of cards used by a single player."""

    cards: List[Card]

    def draw(self, n: int = 1) -> List[Card]:
        """Draw ``n`` cards from the top of the deck."""

        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return []
        if len(self.cards) < n:
            raise RuntimeError("Cannot draw more cards than remaining in deck")
        drawn, self.cards = self.cards[:n], self.cards[n:]
        return drawn

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.cards)

    def copy(self) -> "Deck":
        """Return a shallow copy of the deck.

        This helper allows experimentation and RL simulations to clone the
        current deck state without mutating the original list.
        """

        return Deck(list(self.cards))

    @classmethod
    def from_iterable(cls, cards: Iterable[Card]) -> "Deck":
        """Create a deck from ``cards`` preserving order."""

        return cls(list(cards))
