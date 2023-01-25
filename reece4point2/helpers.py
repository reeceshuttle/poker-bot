from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import eval7
import random

ranks = 'AKQJT98765432'

def ParseHoleCards(hole_cards):
    """
    hole_cards will look like this: ["Ac", "Ts"]
    """
    # dealing with suits
    if hole_cards[0][1] == hole_cards[1][1]: # suited
        last = 's'
    else: # unsuited
        last = 'u'

    # dealing with card ranks
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    if ranks.index(hole_cards[0][0]) >= ranks.index(hole_cards[1][0]):
        first = f"{hole_cards[0][0]}{hole_cards[1][0]}"
    else:
        first = f"{hole_cards[1][0]}{hole_cards[0][0]}"
    return first + last


def EvalBoard(game_state, round_state, active):
    """
    evaluates board. Returns string saying what the board has. 
    """
    street = round_state.street  # int representing pre-flop, flop, turn, or river respectively
    board_cards = round_state.deck[:street]  # the board cards
    hand = [eval7.Card(card) for card in board_cards]
    return eval7.handtype(eval7.evaluate(hand))

def InitializeOpponentRange(vpip):
    """
    returns a postflop range based on their preflop actions.
    If they limp, we use that range.
    If they raised from btn and we called, we use that percentage.
    If we raised and they 3bet, we use that percentage.
    Initially, we will assume a typical range that we use.
    """
    raise NotImplementedError

# what they give us:
# my hand:['6c', '7s'], board:['2h', '2c', '9c', 'Qd', '5s']
# ['6c', '7s','2h', '2c', '9c', 'Qd', '5s']


def RankOccuranceCheck(cards):
    """
    returns the number of certain frequencies on the board.
    example: 
    > RankOccuranceCheck(['2h', '2c', '9c', 'Qc', '2s'])
    {4: 0, 3: 1, 2: 0, 1: 2, 0: 10}
    """
    ans ={4:0, 3:0, 2:0, 1:0, 0:0}
    stuff = {}
    ranks = 'AKQJT98765432'
    for rank in ranks:
        stuff[rank] = 0
    for card in cards:
        stuff[card[0]] += 1
    # return stuff
    for k in stuff:
        ans[stuff[k]] += 1
    return ans


def SuitsCheck(cards):
    """
    returns the number of each suit in cards.
    """
    ans = {'s':0, 'd':0, 'h':0, 'c':0}
    for card in cards:
        ans[card[-1]]+=1
    return ans


def MaxSuitCount(cards):
    mx = 0
    msuit = ''
    ans = SuitsCheck(cards)
    for suit in ans:
        if ans[suit]>mx:
            mx = ans[suit]
            msuit = suit
    return mx, msuit


def StraightsCheck(cards):
    ans = {0:0,1:0,2:0,3:0,4:0,5:0}
    stuff = {}
    ranks = 'AKQJT98765432'
    for rank in ranks:
        stuff[rank] = 0
    for card in cards:
        stuff[card[0]] = 1
    possibilities = 'A23456789TJQKA'
    for i in range(10):
        count = 0
        print(possibilities[i:i+5])
        for rank in possibilities[i:i+5]:
            count += stuff[rank]
        ans[count] += 1
    return ans


def PairChecker(cards):
    """
    checks what pairs you have and returns their ranks.
    For example, if you have a single top pair, this will return [1].
    """
    answers = []
    ranks = '23456789TJQKA'
    found = set()
    non_pairs = []
    pairs = []
    for card in cards:
        if card[0] in found:
            # pair found
            pairs.append(card[0]) 
        else:
            found.add(card[0])
    print(pairs)
    for pair in pairs:
        ans = 1
        non_pairs = []
        for card in cards:
            if card[0] != pair:
                non_pairs.append(card[0])
        for card in non_pairs:
            if ranks.index(card) > ranks.index(pair):
                ans += 1
        answers.append(ans)
    return answers


def StraightDrawCheck(cards):
    """
    checks for straight draws, returns number of straight draws found.
    """
    raise NotImplementedError


def StraightBoardCheck(cards):
    """
    checks if there is a straight on the board.
    """
    raise NotImplementedError
    

def FourFlushBoardCheck(cards):
    """
    checks if there is a four flush on the board.
    """
    raise NotImplementedError


def FlushBoardCheck(cards):
    """
    checks if there is a flush on the board.
    """
    raise NotImplementedError
    
