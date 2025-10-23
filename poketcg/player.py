"""Player and board state models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .cards import Card, PokemonCard
from .deck import Deck


@dataclass
class Player:
    """Represents the mutable state of a player during a game."""

    name: str
    deck: Deck
    hand: List[Card] = field(default_factory=list)
    discard_pile: List[Card] = field(default_factory=list)
    prizes: List[Card] = field(default_factory=list)
    active_pokemon: Optional[PokemonCard] = None
    active_hp: int = 0

    def draw(self, n: int = 1) -> List[Card]:
        """Draw ``n`` cards into the hand."""

        cards = self.deck.draw(n)
        self.hand.extend(cards)
        return cards

    def setup_prizes(self, count: int = 6) -> None:
        """Put ``count`` cards aside as prize cards."""

        self.prizes = self.deck.draw(count)

    def take_prize(self) -> Optional[Card]:
        """Take the top prize card if available."""

        if not self.prizes:
            return None
        card = self.prizes.pop(0)
        self.hand.append(card)
        return card

    def has_pokemon_in_hand(self) -> bool:
        return any(isinstance(card, PokemonCard) for card in self.hand)

    def promote_from_hand(self) -> bool:
        """Promote the first Pokemon card in hand to the active spot."""

        for idx, card in enumerate(self.hand):
            if isinstance(card, PokemonCard):
                self.active_pokemon = card
                self.active_hp = card.hp
                del self.hand[idx]
                return True
        return False

    def damage_active(self, amount: int) -> bool:
        """Apply damage to the active Pokemon.

        Returns ``True`` when the Pokemon is knocked out.
        """

        if self.active_pokemon is None:
            raise RuntimeError("No active pokemon to damage")
        self.active_hp = max(self.active_hp - amount, 0)
        return self.active_hp == 0

    def discard_active(self) -> None:
        if self.active_pokemon is None:
            return
        self.discard_pile.append(self.active_pokemon)
        self.active_pokemon = None
        self.active_hp = 0
