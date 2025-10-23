"""Simplified Pokemon TCG gameplay loop."""
from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple

from .cards import PokemonCard
from .deck import Deck
from .player import Player


class Turn(Enum):
    PLAYER_ONE = auto()
    PLAYER_TWO = auto()

    def opposite(self) -> "Turn":
        return Turn.PLAYER_TWO if self is Turn.PLAYER_ONE else Turn.PLAYER_ONE


@dataclass
class GameResult:
    winner: Optional[Turn]
    log: List[str]


class PokemonGame:
    """Controller that runs a simplified Pokemon TCG match.

    The goal of this class is to expose a deterministic, easy to extend state
    machine that resembles the structure of a full Pokemon TCG match. A number
    of mechanics are intentionally omitted (energy requirements, abilities,
    status conditions, bench management) so that the basic flow is easy to
    follow and suitable for experimentation.
    """

    def __init__(self, player_one: Player, player_two: Player, *, seed: int | None = None):
        self.random = random.Random(seed)
        self.players = {
            Turn.PLAYER_ONE: player_one,
            Turn.PLAYER_TWO: player_two,
        }
        self.turn = Turn.PLAYER_ONE
        self.turn_count = 0
        self.log: List[str] = []

    def _setup_player(self, player: Player) -> None:
        self.random.shuffle(player.deck.cards)
        player.hand.clear()
        player.discard_pile.clear()
        player.prizes.clear()
        player.active_pokemon = None
        player.active_hp = 0
        player.draw(7)
        player.setup_prizes()
        if not player.promote_from_hand():
            raise RuntimeError(f"Player {player.name} has no Pokemon to start the game")

    def setup(self) -> None:
        """Shuffle decks, draw opening hands and promote the initial Pokemon."""

        for player in self.players.values():
            self._setup_player(player)
        self.turn = Turn.PLAYER_ONE
        self.turn_count = 0
        self.log.append("Game setup complete.")
        for turn in Turn:
            player = self.players[turn]
            assert player.active_pokemon is not None
            self.log.append(
                f"{player.name} opens with {player.active_pokemon.name} (HP {player.active_hp})."
            )

    def _draw_phase(self, player: Player) -> bool:
        """Handle the start-of-turn draw. Returns False if the player decks out."""

        if len(player.deck.cards) == 0:
            self.log.append(f"{player.name} cannot draw and loses by deck out.")
            return False
        card = player.draw()[0]
        self.log.append(f"{player.name} draws {card.name}.")
        return True

    def _attack(self, attacker: Player, defender: Player) -> None:
        pokemon = attacker.active_pokemon
        if pokemon is None:
            self.log.append(f"{attacker.name} has no active Pokemon and loses the turn.")
            return
        if not pokemon.attacks:
            self.log.append(f"{pokemon.name} cannot attack.")
            return
        attack = pokemon.attacks[0]
        self.log.append(f"{attacker.name}'s {pokemon.name} uses {attack.name} for {attack.damage} damage.")
        knocked_out = defender.damage_active(attack.damage)
        if knocked_out:
            self.log.append(f"{defender.name}'s {defender.active_pokemon.name} is knocked out!")
            defender.discard_active()
            prize = attacker.take_prize()
            if prize is not None:
                self.log.append(f"{attacker.name} takes a prize card: {prize.name}.")
            if not attacker.prizes:
                self.log.append(f"{attacker.name} takes the final prize and wins!")
            if not defender.promote_from_hand():
                self.log.append(f"{defender.name} has no replacement Pokemon and loses!")

    def _check_victory(self) -> Optional[Turn]:
        for turn, player in self.players.items():
            if not player.prizes:
                return turn
            if player.active_pokemon is None and not player.has_pokemon_in_hand():
                return turn.opposite()
        return None

    def step(self) -> Optional[Turn]:
        """Play a single turn and return the winner if the game ends."""

        active_turn = self.turn
        player = self.players[active_turn]
        opponent = self.players[active_turn.opposite()]
        self.turn_count += 1
        self.log.append(f"--- Turn {self.turn_count}: {player.name} ---")

        if not self._draw_phase(player):
            return active_turn.opposite()

        self._attack(player, opponent)

        winner = self._check_victory()
        self.turn = active_turn.opposite()
        return winner

    def play(self, *, max_turns: int = 100) -> GameResult:
        """Play until a winner is decided or ``max_turns`` is reached."""

        self.setup()
        winner: Optional[Turn] = None
        while winner is None and self.turn_count < max_turns:
            winner = self.step()
        if winner is None:
            self.log.append("Game ended due to turn limit.")
        else:
            self.log.append(f"Winner: {self.players[winner].name}")
        return GameResult(winner=winner, log=list(self.log))

    def clone(self) -> "PokemonGame":
        """Return a deep-ish copy of the game state for experimentation."""

        cloned_players = {
            turn: Player(
                name=player.name,
                deck=Deck(player.deck.cards.copy()),
                hand=list(player.hand),
                discard_pile=list(player.discard_pile),
                prizes=list(player.prizes),
                active_pokemon=player.active_pokemon,
                active_hp=player.active_hp,
            )
            for turn, player in self.players.items()
        }
        clone = PokemonGame(cloned_players[Turn.PLAYER_ONE], cloned_players[Turn.PLAYER_TWO])
        clone.turn = self.turn
        clone.turn_count = self.turn_count
        clone.log = list(self.log)
        return clone

    def current_state(self) -> Tuple[Player, Player, Turn]:
        """Expose a snapshot of the current state.

        This is designed to be consumed by reinforcement learning agents.
        The first player in the tuple always corresponds to ``Turn.PLAYER_ONE``.
        """

        return (
            self.players[Turn.PLAYER_ONE],
            self.players[Turn.PLAYER_TWO],
            self.turn,
        )
