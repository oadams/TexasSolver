import abc
import collections
import collections.abc
import json
import random

import pandas as pd


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



def describe_strategy(strategy_obj, flop, range):
    """ Given a JSON-like object from TexasSolver describing a flop situation and GTO
    approximations of strategies for each player, produce an easily digestible human-intepretable
    description of the strategy, based on grouping cards together. Groups include:
    - 'Air' that totally misses / undercards
    - two overcards
    - Ace-high air
    - Gut-shot straight draws
    - open-ended straight draws
    - Flush draws
    - Weak pairs
    - Top pair weak kicker
    - Top pair top kicker
    - Trips with two board cards
    - Overpairs
    - Two-pairs 
    - Sets
    - Straights
    - Flushes
    - Nut flushes.
    
    We can also have coarsers grained groupings of hands such as 'TPTK+', 'marginal', 'draws', 'air', 'nuts'.
    The point is that we want a human to quickly be able to understand the strategy.
    We want to show the bet/check/call/raise percentages for each of these parts of our range. We then want to cluster flops
    based on this.

    The output strategy doesn't seem to include the actual original ranges or flop cards, so we need to store these when we make the call to the program.

    
    """

    print(obj.keys())
    print(obj['actions'])
    #print(obj['childrens']['CHECK'].keys())
    print(obj['node_type'])
    print(obj['player'])
    print(obj['strategy']['strategy'])
    #print(obj['childrens'].keys())

    df = pd.DataFrame.from_records([[hole_cards_str]+strategy for hole_cards_str, strategy in obj['strategy']['strategy'].items()],
                                   columns=['hole_cards'] + obj['strategy']['actions'])

    # First determine overall action percentages.
    # Note that this currently assumes each card is either wholly in the range or not.
    total = df[obj['strategy']['actions']].to_numpy().sum()
    for action in obj['strategy']['actions']:
        print(action, df[action].sum(), df[action].sum()/total)
        


deck = Deck()

flop = random.sample(deck, k=3)

#print(flop)

with open('/Users/oadams/code/TexasSolver/strategies/Live_GTO/BU_open/BB_3bet/BU_call/QsJh2h.json') as f:
    obj = json.loads(f.read())
describe_strategy(obj, [Card('Q', 's'), Card('J', 'h'), Card('2', 'h')], None)
