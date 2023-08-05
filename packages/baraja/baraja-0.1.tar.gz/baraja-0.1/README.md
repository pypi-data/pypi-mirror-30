Baraja is a package for emulating card deck behavior.

### Installation

Baraja uses setuptools for installation.

    $ python setup.py install

To run tests either use the test in setup or the nose testing suite.

    $ python setup.py test

or

    $ nosetests

### Basic Usage

    >>> from baraja.deck import Deck
    >>> from baraja.card import Card
    >>> d = Deck([Card('One', 1), Card('Two', 2)])
    >>> d.draw()
    baraja.card.Card('Two', 2)
    >>> d.draw()
    baraja.card.Card('One', 1)
    >>> d.draw()
    >>> d.shuffle()
    >>> d.draw()
    baraja.card.Card('One', 1)
    >>>

### Easy Card Lists

    >>> from baraja.card import Card
    >>> cardlist = Card('one') * 2
    >>> cardlist += Card('two') * 3
    >>> len(cardlist)
    5
    >>> for c in cardlist:
    ...     print(c)
    ...
    baraja.card.Card('one', None)
    baraja.card.Card('one', None)
    baraja.card.Card('two', None)
    baraja.card.Card('two', None)
    baraja.card.Card('two', None)
    >>>

