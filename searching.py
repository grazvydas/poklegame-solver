import random
import itertools as it
from tqdm import tqdm
import numpy as np

from phevaluator import evaluate_cards


SUITS = ["H", "D", "C", "S"]
RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]


def get_full_deck_of_cards():
    deck_of_cards = []
    for rank in RANKS:
        for suit in SUITS:
            deck_of_cards.append(f"{rank}{suit}")
    return deck_of_cards


class TableCards:

    def __init__(self, all_cards):
        self.flop = all_cards[:3]
        self.turn = all_cards[3]
        self.river = all_cards[4]

    def __str__(self):
        return f"{' '.join(self.flop)}  {self.turn}  {self.river}"


def rankings_are_equal(ranking_1, ranking_2):
    o11, o12, o13 = ranking_1
    o21, o22, o23 = ranking_2
    return all([
        np.sign(o11 - o12) == np.sign(o21 - o22),
        np.sign(o12 - o13) == np.sign(o22 - o23),
        np.sign(o11 - o13) == np.sign(o21 - o23)
    ])


def eval_hand(hand, cards):
    _cards_to_eval = list(hand) + list(cards)
    return evaluate_cards(*_cards_to_eval)


def eval_hands(hands, cards_on_table):
    hand_evals = [eval_hand(hands[p], cards_on_table) for p in ['P1', 'P2', 'P3']]
    return hand_evals


def card_deal_search(deck_of_cards, table_cards, hands, expected_hand_ranks):

    found = []
    _deck = deck_of_cards.copy()
    for fc in table_cards:
        _deck.remove(fc)

    for c in _deck:
        tcards = table_cards + [c]
        _hand_ranks = eval_hands(hands, tcards)
        if rankings_are_equal(_hand_ranks, expected_hand_ranks):
            found.append(tcards)

    return found


def find_all_possible_dealt_card(hands: dict, hand_ranks: dict) -> tuple[list]:

    """
    hands = {
        "P1": ["TD", "8S"],
        "P2": ["AD", "2S"],
        "P3": ["9H", "6D"]
    }
    hand_ranks = {
        'flop': (1, 2, 3),  # P1, P2, P3
        'turn': (1, 2, 3),
        'river': (2, 1, 3)
    }
    """

    deck_of_cards = get_full_deck_of_cards()
    for hand_cards in hands.values():
        for card in hand_cards:
            deck_of_cards.remove(card)

    print('Searching for possible flops...')
    flops = []
    for flop in tqdm(it.combinations(deck_of_cards, 3)):
        _flop_ranks = eval_hands(hands, flop)
        if rankings_are_equal(_flop_ranks, hand_ranks['flop']):
            flops.append(list(flop))
    print(f"Possible flop count: {len(flops)}")

    print('Searching for possible flop + river...')
    flop_and_turn_cases = []
    for flop in tqdm(flops):
        flop_and_turn_cases += card_deal_search(deck_of_cards, flop, hands, hand_ranks['turn'])
    print(f"Possible flop + turn count: {len(flop_and_turn_cases)}")

    print('Searching for final cards dealt on table...')
    table_cards = []
    for flop_turn in tqdm(flop_and_turn_cases):
        table_cards += card_deal_search(deck_of_cards, flop_turn, hands, hand_ranks['river'])
    print(f"Possible table card solution count: {len(table_cards)}")

    return flops, flop_and_turn_cases, table_cards


if __name__ == "__main__":

    hands = {
        "P1": ["6C", "AH"],
        "P2": ["9H", "2C"],
        "P3": ["KS", "8D"]
    }
    hand_ranks = {
        'flop': (3, 1, 2),
        'turn': (2, 1, 3),
        'river': (1, 3, 2)
    }
    flops, flops_turns, flops_turns_rivers = find_all_possible_dealt_card(hands, hand_ranks)

    solutions = [TableCards(sol) for sol in flops_turns_rivers]
    for case in solutions:
        print(case)
