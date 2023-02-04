from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import eval7
import random
import helpers
import preflop_strategy

def FirstToActStrategy(game_state, round_state, active):
    """
    Used when we are first to act in a postflop scenario.
    """

    legal_actions = round_state.legal_actions()  # the actions you are allowed to take
    street = round_state.street  # int representing pre-flop, flop, turn, or river respectively
    my_cards = round_state.hands[active]  # your cards
    board_cards = round_state.deck[:street]  # the board cards
    hand = [eval7.Card(card) for card in my_cards+board_cards]
    made_hand = eval7.handtype(eval7.evaluate(hand))
    if RaiseAction in legal_actions:
        min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
    my_stack = round_state.stacks[active]  # the number of chips you have remaining
    opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
    pot_size = 800 - my_stack - opp_stack

    # --------------- strategy: --------------------
    # We want a strategy of betting with made hands and draws
    if made_hand in ["Straight Flush", "Quads", "Full House"]:
        # We are going for big value here.
        return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
    # elif made_hand == "Flush":
    #     board_suits = helpers.SuitsCheck(board_cards)
    
    elif made_hand in ["Flush", "Straight", "Trips", "Two Pair"] and helpers.EvalBoard(game_state, round_state, active)!=made_hand:
        # We are going for big value here.
        return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
    elif made_hand == "Pair" and helpers.EvalBoard(game_state, round_state, active) not in ["Pair"]:
        return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size))))
        # Still value but less confident. 1/2 Pot
    elif False: # "Have a good draw":
        return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
    else:
        return CheckAction()

def CheckedToStrategy(game_state, round_state, active):
    """
    Used when we are checked to in a postflop scenario.
    """
    legal_actions = round_state.legal_actions()  # the actions you are allowed to take
    street = round_state.street  # int representing pre-flop, flop, turn, or river respectively
    my_cards = round_state.hands[active]  # your cards
    board_cards = round_state.deck[:street]  # the board cards
    hand = [eval7.Card(card) for card in my_cards+board_cards]
    made_hand = eval7.handtype(eval7.evaluate(hand))
    if RaiseAction in legal_actions:
        min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
    my_stack = round_state.stacks[active]  # the number of chips you have remaining
    opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
    pot_size = 800 - my_stack - opp_stack

    # --------------- strategy: --------------------
    # We want a strategy of betting with made hands and draws, but being wider than if leading
    if made_hand in ["Straight Flush", "Quads", "Full House"]:
        # We are going for big value here.
        return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
    elif made_hand in ["Flush", "Straight", "Trips", "Two Pair"] and helpers.EvalBoard(game_state, round_state, active)!=made_hand:
        # We are going for big value here.
        return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
    elif made_hand in ["Pair"] and helpers.EvalBoard(game_state, round_state, active) not in ["Pair"]:
        return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size))))
        # Still value but less confident. 1/2 Pot
    elif False: # "Have a good draw":
        return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
    else:
        if random.random()<0.1: return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size))))
        else: return CheckAction()

def ICheckedTheyBetStrategy(game_state, round_state, active):
    """
    Used when I checked postflop and they bet.
    """
    legal_actions = round_state.legal_actions()  # the actions you are allowed to take
    street = round_state.street  # int representing pre-flop, flop, turn, or river respectively
    my_cards = round_state.hands[active]  # your cards
    board_cards = round_state.deck[:street]  # the board cards
    hand = [eval7.Card(card) for card in my_cards+board_cards]
    made_hand = eval7.handtype(eval7.evaluate(hand))
    if RaiseAction in legal_actions:
        min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
    my_stack = round_state.stacks[active]  # the number of chips you have remaining
    opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
    pot_size = 800 - my_stack - opp_stack

    # --------------- strategy: --------------------
    if made_hand in ["Straight Flush", "Quads", "Full House"]:
        # We are going for big value here.
        if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
        else: return CallAction()
    elif made_hand in ["Flush", "Straight", "Trips", "Two Pair"] and helpers.EvalBoard(game_state, round_state, active)!=made_hand:
        # We are going for big value here.
        if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
        else: return CallAction()
    elif made_hand in ["Pair"] and helpers.EvalBoard(game_state, round_state, active) not in ["Pair"]:
        if random.random()<0.5: return CallAction()
        else: return FoldAction()
        # Still value but less confident. 1/2 Pot
    elif False: # "Have a good draw":
        return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
    else:
        return FoldAction()

def BetIntoStrategy(game_state, round_state, active):
    """
    Used When I am bet into postflop.
    """
    legal_actions = round_state.legal_actions()  # the actions you are allowed to take
    street = round_state.street  # int representing pre-flop, flop, turn, or river respectively
    my_cards = round_state.hands[active]  # your cards
    board_cards = round_state.deck[:street]  # the board cards
    my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
    opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        
    hand = [eval7.Card(card) for card in my_cards+board_cards]
    made_hand = eval7.handtype(eval7.evaluate(hand))
    if RaiseAction in legal_actions:
        min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
    my_stack = round_state.stacks[active]  # the number of chips you have remaining
    opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
    pot_size = 800 - my_stack - opp_stack

    # --------------- strategy: --------------------
    if made_hand in ["Straight Flush", "Quads", "Full House"]:
        # We are going for big value here.
        if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
        else: return CallAction()
    elif made_hand in ["Flush", "Straight", "Trips", "Two Pair"] and helpers.EvalBoard(game_state, round_state, active)!=made_hand:
        # We are going for big value here.
        if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
        else: return CallAction()
    elif made_hand in ["Pair"] and helpers.EvalBoard(game_state, round_state, active) not in ["Pair"]:
        if opp_pip<=pot_size/2+1:
            if random.random()<0.45: return CallAction()
            else: return FoldAction()
        else:
            return FoldAction()
        # Still value but less confident. 1/2 Pot
    elif False: # "Have a good draw":
        return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
    else:
        return FoldAction()