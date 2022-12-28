import abc
import collections
import collections.abc
import random


class Card(collections.namedtuple('Card', ['rank', 'suit'])):
    __slots__ = ()
    def __str__(self):
        return f'{self.rank}{self.suit}'
    def __repr__(self):
        return f'{self.rank}{self.suit}'


class Deck(collections.abc.Sequence):
    ranks = [str(n) for n in range(2, 10)] + list('TJQKA')
    suits = ['s', 'd', 'c', 'h']

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits
                                        for rank in self.ranks]
        
    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]


deck = Deck()

flop = random.sample(deck, k=3)

print(flop)
