"""Card model definitions for the simplified Pokemon TCG engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Attack:
    """Describes a Pokemon attack.

    Attributes
    ----------
    name:
        Display name used when logging or debugging.
    damage:
        Amount of damage dealt to the opposing active Pokemon when used.
    text:
        Optional reminder text for the attack effect. The engine does not
        currently simulate these effects, but keeping the text available makes
        it easy to extend the model in the future.
    """

    name: str
    damage: int
    text: str | None = None


@dataclass(frozen=True)
class Card:
    """Base class for all card types."""

    name: str

    def describe(self) -> str:
        """Return a human-readable string describing the card."""

        return self.name


@dataclass(frozen=True)
class PokemonCard(Card):
    """Simplified Pokemon card representation used for the core flow."""

    hp: int
    attacks: List[Attack] = field(default_factory=list)
    external_id: int | None = None

    def describe(self) -> str:
        attacks = ", ".join(f"{a.name} ({a.damage})" for a in self.attacks)
        return f"{self.name} [HP {self.hp}] :: {attacks}"


@dataclass(frozen=True)
class EnergyCard(Card):
    """Placeholder energy card model."""

    energy_type: str


@dataclass(frozen=True)
class TrainerCard(Card):
    """Placeholder trainer card model."""

    text: str
