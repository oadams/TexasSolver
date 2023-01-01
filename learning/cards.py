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
    @classmethod
    def from_str(cls, card_str):
        # Assumes representation of the form 'As', '2c', etc.
        return cls(card_str[0], card_str[1])


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


RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
RANK_TO_INT = {rank: score for score, rank in enumerate(RANKS)}


def group_holecards(hole_cards, flop):
    # TODO problem with this approach is that there is mutual exclusitivity

    # Make sure flop is sorted, so that it's easy to tell what top pair is
    flop = sorted(flop, key=lambda x: RANK_TO_INT[x.rank], reverse=True)

    # Sets
    if hole_cards[0].rank == hole_cards[1].rank:
        for flop_card in flop:
            if flop_card.rank == hole_cards[0].rank:
                # NOTE: 4 of a kind returned as a set
                return 'Set'
        if RANK_TO_INT[hole_cards[0].rank] < RANK_TO_INT[flop[0].rank]:
            # Then it's an underpair
            return 'Pocket underpair'

    # Pair-related
    # TODO Currently ignoring two pairs
    # TODO Need to handle TPTK where Ace is on the flop elegantly.
    if hole_cards[0].rank == flop[0].rank:
        # If there's not an ace on the flop then top kicker is A
        if RANK_TO_INT[flop[0].rank] != RANK_TO_INT['A'] and hole_cards[1].rank == 'A':
            return 'TPTK'
    if hole_cards[1].rank == flop[0].rank:
        # If there's not an ace on the flop then top kicker is A
        if RANK_TO_INT[flop[0].rank] != RANK_TO_INT['A'] and hole_cards[0].rank == 'A':
            return 'TPTK'
    for card in hole_cards:
        if card.rank == flop[0].rank:
            return 'TP'

    for card in hole_cards:
        if card.rank == flop[1].rank or card.rank == flop[2].rank:
            return 'pair'

    # Flush-related
    if hole_cards[0].suit == hole_cards[1].suit:
        count = 0
        for card in flop:
            if card.suit == hole_cards[0].suit:
                count += 1
        if count == 3:
            return 'Flush'
        if count == 2:
            return 'FD'
        #if count == 1:
        #    return 'BDFD'

    # Straight-related
    hole_and_flop = sorted(list(hole_cards) + flop, key=lambda x: RANK_TO_INT[x.rank])
    #print(hole_and_flop)
    max_count = 0
    count = 0

    # TODO: Need to account for gutshot straight draws
    # TODO: Need to discount draws capped at Aces that are effectively gutshot.
    for i, card in enumerate(hole_and_flop):
        if i + 1 == len(hole_and_flop):
            break
        if RANK_TO_INT[card.rank] == RANK_TO_INT[hole_and_flop[i+1].rank] - 1:
            count += 1
        else:
            if count > max_count:
                max_count = count
            count = 0
    if count > max_count:
        max_count = count
    if max_count == 3:
        #print('Straight draw', hole_cards, flop)
        return 'SD'
    if max_count == 4:
        return 'Straight'

    # Overcards
    # TODO Make card class have a lt/gt comparators so we can abstract away RANK_TO_IN T
    if RANK_TO_INT[hole_cards[0].rank] > RANK_TO_INT[flop[0].rank] and RANK_TO_INT[hole_cards[1].rank] > RANK_TO_INT[flop[0].rank]:
        return 'Overcards'

    # Ace-high
    if hole_cards[0].rank == 'A' or hole_cards[1].rank == 'A':
        return 'Ace high'

    #print(hole_cards, flop)
        
    return 'Air'


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

    The output strategy doesn't seem to include the actual original fractional ranges or flop cards, so we need to store these when we make the call to the program.

    
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

    df = df.set_index('hole_cards')
    print(df)
    df = df.groupby(by=lambda holecards_str: group_holecards((Card.from_str(holecards_str[0:2]), Card.from_str(holecards_str[2:4])),
                                                    flop)).mean()

    print(df)
    return


        


#deck = Deck()

#flop = random.sample(deck, k=3)

#print(flop)

with open('/Users/oadams/code/TexasSolver/strategies/Live_GTO/BU_open/BB_3bet/BU_call/QsJh2h.json') as f:
    obj = json.loads(f.read())
describe_strategy(obj, [Card('Q', 's'), Card('J', 'h'), Card('2', 'h')], None)
