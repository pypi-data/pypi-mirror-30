"""baraja.card

this module contains classes and functions for working with individual cards

"""
import copy

from baraja import exceptions as ex


class Card(object):
    """a single immutable card"""
    def __init__(self, name, value=None):
        """
        Keyword arguments:

        name       --  name of the card
        value      --  a numeric value for comparing cards (default = None)

        """
        self._name = name
        self._value = value

    def __eq__(self, other):
        """return true if self and other have the same name, and value"""
        if other.name == self._name and other.value == self._value:
            return True
        return False

    def __ne__(self, other):
        """return true if self and other have differing name or value"""
        return not self.__eq__(other)

    def __mul__(self, count):
        """return a list of Cards"""
        cardlist = [self]
        for i in range(count-1):
            cardlist.append(copy.deepcopy(self))
        return cardlist

    def __repr__(self):
        """a Card repr should be baraja.card.Card('name', value)"""
        return 'baraja.card.Card' + str((self._name, self._value))

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self._name


class PlayingCard(Card):
    """a french style playing card implementation

    A PlayingCard has a suit and a value. The suit can be one of Club,
    Diamond, Heart, or Spade. Values can range from 1(Ace) to 12(King).

    """
    CLUB = 'Club'
    DIAMOND = 'Diamond'
    HEART = 'Heart'
    SPADE = 'Spade'

    SUITS = [CLUB, DIAMOND, HEART, SPADE]

    _value_lookup = {
        1: 'Ace', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six',
        7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', 11: 'Jack',
        12: 'Queen', 13: 'King'
    }

    def __init__(self, value, suit):
        """
        Keyword arguments:

        value      -- 1 through 13 (Ace is low)
        suit       -- suit of the card (SUIT_CLUB, ...)

        """
        if suit not in PlayingCard.SUITS:
            raise ex.CardException('Unrecognized suit {}.'.format(suit))
        if value < 1 or value > 13:
            raise ex.CardException('Value must be between 1 and 13.')
        super(PlayingCard, self).__init__(
            name='{0} of {1}s'.format(self._value_lookup[value], suit),
            value=value)
        self._suit = suit

    def __eq__(self, other):
        """PlayingCard must check suit as well"""
        if super(PlayingCard, self).__eq__(other) and self.suit == other.suit:
            return True
        return False

    @property
    def suit(self):
        return self._suit
