"""baraja.deck

the deck module contains classes and functions for representing card decks.

"""
from copy import copy
import random

from baraja import card


class Deck(object):
    """a deck of cards

    This object is a stateful representation of a deck of cards.

    In all card sequences returned from a Deck, item [-1] is considered to be
    the top of that stack.

    """
    def __init__(self, sourcelist):
        """create a deck by passing in a list of card objects

        New decks are shuffled once.

        """
        self._master_deck = tuple(sourcelist)
        self._drawn = []
        self._undrawn = list(sourcelist)
        self.shuffle()

    def draw(self):
        """draw a card

        Pop a card from undrawn and push it to drawn, returning a copy of
        the card or None if the deck is empty.

        """
        try:
            c = self._undrawn.pop()
            self._drawn.append(c)
            return copy(c)
        except IndexError:
            return None

    @property
    def drawn(self):
        """return a copy of the list of drawn cards"""
        return tuple(self._drawn)

    def shuffle(self):
        """shuffle the undrawn and drawn cards together"""
        self._undrawn.extend(self._drawn)
        del self._drawn[:]
        random.shuffle(self._undrawn)

    @property
    def undrawn(self):
        """return a copy of the undrawn card list"""
        return tuple(self._undrawn)


class PlayingCardDeck(Deck):
    """a french style deck

    This deck contains 52 cards in four suits with value 1 through 13 in each.
    With 1, 11, 12, and 13 representing Ace, Jack, Queen, and King
    repsectively.

    """
    def __init__(self):
        """create a deck of french style playing cards"""
        cardlist = []
        for suit in card.PlayingCard.SUITS:
            for value in range(1, 14):
                cardlist.append(card.PlayingCard(value, suit))
        super(PlayingCardDeck, self).__init__(sourcelist=cardlist)
