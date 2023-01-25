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
    opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
    pot_size = 800 - my_stack - opp_stack

    # --------------- strategy: --------------------
    # We want a strategy of betting with made hands and draws
    if made_hand in ["Straight Flush", "Quads", "Full House"]:
        # We are going for big value here.
        return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))


    elif made_hand == "Flush":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        if max_board_suits==3:
            # We are going for big value here.
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        elif max_board_suits==4:
            if False:# We should check if we have Ace or King and there are no full house capabilities.
                return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
            elif f'A{msuit}' in my_cards:

                if RaiseAction in legal_actions: return RaiseAction(max_raise)
                else: return CallAction()
            
            elif f'K{msuit}' in my_cards or f'Q{msuit}' in my_cards:
                return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size))))

            else:
                return CheckAction()
        elif max_board_suits >= 5:
            if f'A{msuit}' in my_cards:
                return RaiseAction(max_raise)
            
            elif f'K{msuit}' in my_cards or f'Q{msuit}' in my_cards:
                return RaiseAction(min(max_raise, max(min_raise, int(0.7*pot_size))))
            
            return CheckAction()

            
    elif made_hand == "Straight":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        if max_board_suits <= 3 and straight_possibilities[5] == 0 and straight_possibilities[4] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        elif max_board_suits <= 3 and straight_possibilities[5] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+3))))
        else:
            return CheckAction()
    
    elif made_hand == "Trips":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        if r_occurances[3]>0: # trips on board
            return CheckAction()
        elif max_board_suits < 4 and straight_possibilities[4] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        else:
            bl = 1 if max_board_suits == 4 else 0
            if random.random()>(9*bl+4*straight_possibilities[4])/20: return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+2))))
            else: return CheckAction()
    

    elif made_hand == "Two Pair":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        if r_occurances[2]>=2:
            return CheckAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0:
            if r_occurances[2] == 0 or random.random()<0.15:
                return RaiseAction(min(max_raise, max(min_raise, int(0.4*pot_size))))
            else:
                return CheckAction()
        elif r_occurances[2]==1:
            return RaiseAction(min(max_raise, max(min_raise, int(0.4*pot_size))))
        elif r_occurances[2]==0:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()


    elif made_hand == "Pair":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        
        if r_occurances[2] == 1:
            if random.random()<0.2:
                return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+2))))
            else:
                return CheckAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0:
            return CheckAction()
        else:
            if opp_pip<=pot_size/2+1:
                if random.random()<0.45: return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+2))))
                else: return CheckAction()
            else:
                return CheckAction()
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
    opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
    pot_size = 800 - my_stack - opp_stack

    # --------------- strategy: --------------------
    # We want a strategy of betting with made hands and draws
    if made_hand in ["Straight Flush", "Quads", "Full House"]:
        # We are going for big value here.
        return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))


    elif made_hand == "Flush":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        if max_board_suits==3:
            # We are going for big value here.
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        elif max_board_suits==4:
            if False:# We should check if we have Ace or King and there are no full house capabilities.
                return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
            elif f'A{msuit}' in my_cards:

                if RaiseAction in legal_actions: return RaiseAction(max_raise)
                else: return CallAction()
            
            elif f'K{msuit}' in my_cards or f'Q{msuit}' in my_cards:
                return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size))))
            else:
                return CheckAction()
        elif max_board_suits >= 5:
            if f'A{msuit}' in my_cards:
                return RaiseAction(max_raise)
            
            elif f'K{msuit}' in my_cards or f'Q{msuit}' in my_cards:
                return RaiseAction(min(max_raise, max(min_raise, int(0.3*pot_size))))
            
            return CheckAction()

            
    elif made_hand == "Straight":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        if max_board_suits <= 3 and straight_possibilities[5] == 0 and straight_possibilities[4] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        elif max_board_suits <= 3 and straight_possibilities[5] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+3))))
        else:
            return CheckAction()
    
    elif made_hand == "Trips":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        if r_occurances[3]>0: # trips on board
            return CheckAction()
        elif max_board_suits < 4 and straight_possibilities[4] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        else:
            bl = 1 if max_board_suits == 4 else 0
            if random.random()>(9*bl+4*straight_possibilities[4])/20: return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+2))))
            else: return CheckAction()
    

    elif made_hand == "Two Pair":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        if r_occurances[2]>=2:
            return CheckAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0:
            if r_occurances[2] == 0 or random.random()<0.15:
                return RaiseAction(min(max_raise, max(min_raise, int(0.4*pot_size))))
            else:
                return CheckAction()
        elif r_occurances[2]==1:
            return RaiseAction(min(max_raise, max(min_raise, int(0.4*pot_size))))
        elif r_occurances[2]==0:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()


    elif made_hand == "Pair":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        pairs = helpers.PairChecker(board_cards+my_cards)

        if r_occurances[2] == 1:
            if random.random()<0.2:
                return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+2))))
            else:
                return CheckAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0:
            return CheckAction()
        else:
            if opp_pip<=pot_size/2+1:
                if random.random()<0.45: return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+2))))
                else: return CheckAction()
            else:
                return CheckAction()
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
    opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
    pot_size = 800 - my_stack - opp_stack

    # --------------- strategy: --------------------
    if made_hand in ["Straight Flush", "Quads", "Full House"]:
        # We are going for big value here.
        if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
        else: return CallAction()


    elif made_hand == "Flush":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        if max_board_suits==3:
            # We are going for big value here.
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        elif max_board_suits==4:
            if False:# We should check if we have Ace or King and there are no full house capabilities.
                return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
            elif f'A{msuit}' in my_cards:

                if RaiseAction in legal_actions: return RaiseAction(max_raise)
                else: return CallAction()
            
            elif f'K{msuit}' in my_cards or f'Q{msuit}' in my_cards:
                return CallAction()
            else:
                return CallAction()
        elif max_board_suits >= 5:
            if f'A{msuit}' in my_cards:

                if RaiseAction in legal_actions: return RaiseAction(max_raise)
                else: return CallAction()
            
            elif f'K{msuit}' in my_cards or f'Q{msuit}' in my_cards:
                return CallAction()
            
            return FoldAction()


    elif made_hand == "Straight":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        if max_board_suits <= 3 and straight_possibilities[5] == 0 and straight_possibilities[4] == 0:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        elif max_board_suits <= 3 and straight_possibilities[5] == 0:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+3))))
            else: return CallAction()
        elif max_board_suits == 4:
            if opp_pip < 20:
                return CallAction()
            else:
                return FoldAction()
        else:
            return FoldAction()

    elif made_hand == "Trips":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        if r_occurances[3]>0: # trips on board
            return FoldAction()
        elif max_board_suits < 4 and straight_possibilities[4] == 0:
            if RaiseAction in legal_actions and random.random() > 0.5: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        
        elif opp_pip < 20:
            return CallAction()
        else:
            bl = 1 if max_board_suits == 4 else 0
            if random.random()>(9*bl+4*straight_possibilities[4])/20: return CallAction()
            else: return FoldAction()
    

    elif made_hand == "Two Pair":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        if r_occurances[2]>=2:
            return FoldAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0:
            if opp_pip < 20:
                return CallAction()
            else:
                return FoldAction()
        elif r_occurances[2]==1:
            if opp_pip < 20:
                return CallAction()
            elif opp_pip < 45:
                if random.random()<0.1:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                # if my pair is top pair, call, else fold
                return FoldAction()
        elif r_occurances[2]==0:
            if max_board_suits == 4 or straight_possibilities[4] > 0:
                if opp_pip < 20:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                if opp_pip > 20:
                    return CallAction()
                else:
                    if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                    else: return CallAction()


    elif made_hand == "Pair":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        
        if r_occurances[2] == 1:
            return FoldAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0:
            return FoldAction()
        else:
            if opp_pip<=pot_size/2+1:
                if random.random()<0.45: return CallAction()
                else: return FoldAction()
            else:
                return FoldAction()
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


    elif made_hand == "Flush":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        if max_board_suits==3:
            # We are going for big value here.
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        elif max_board_suits==4:
            if False:# We should check if we have Ace or King and there are no full house capabilities.
                return RaiseAction(min(max_raise, max(min_raise, int(pot_size-1))))
            elif f'A{msuit}' in my_cards:

                if RaiseAction in legal_actions: return RaiseAction(max_raise)
                else: return CallAction()
            
            elif f'K{msuit}' in my_cards or f'Q{msuit}' in my_cards:
                return CallAction()
            else:
                return CallAction()
        elif max_board_suits >= 5:
            if f'A{msuit}' in my_cards:

                if RaiseAction in legal_actions: return RaiseAction(max_raise)
                else: return CallAction()
            
            elif f'K{msuit}' in my_cards or f'Q{msuit}' in my_cards:
                return CallAction()
            
            return FoldAction()


    elif made_hand == "Straight":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        if max_board_suits <= 3 and straight_possibilities[5] == 0 and straight_possibilities[4] == 0:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        elif max_board_suits <= 3 and straight_possibilities[5] == 0:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+3))))
            else: return CallAction()
        elif max_board_suits == 4:
            if opp_pip < 20:
                return CallAction()
            else:
                return FoldAction()
        else:
            return FoldAction()
    

    elif made_hand == "Trips":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        if r_occurances[3]>0: # trips on board
            return FoldAction()
        elif max_board_suits < 4 and straight_possibilities[4] == 0:
            if RaiseAction in legal_actions and random.random() > 0.5: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        
        elif opp_pip < 20:
            return CallAction()
        else:
            bl = 1 if max_board_suits == 4 else 0
            if random.random()>(9*bl+4*straight_possibilities[4])/20: return CallAction()
            else: return FoldAction()
    

    elif made_hand == "Two Pair":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        if r_occurances[2]>=2:
            return FoldAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0:
            if opp_pip < 20:
                return CallAction()
            else:
                return FoldAction()
        elif r_occurances[2]==1:
            if opp_pip < 20:
                return CallAction()
            elif opp_pip < 45:
                if random.random()<0.1:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                # if my pair is top pair, call, else fold
                return FoldAction()
        elif r_occurances[2]==0:
            if max_board_suits == 4 or straight_possibilities[4] > 0:
                if opp_pip < 20:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                if opp_pip > 20:
                    return CallAction()
                else:
                    if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                    else: return CallAction()


    elif made_hand == "Pair":
        max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
        straight_possibilities = helpers.StraightsCheck(board_cards)
        r_occurances = helpers.RankOccuranceCheck(board_cards)
        
        if r_occurances[2] == 1:
            return FoldAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0:
            return FoldAction()
        else:
            if opp_pip<=pot_size/2+1:
                if random.random()<0.45: return CallAction()
                else: return FoldAction()
            else:
                return FoldAction()
            
    elif False: # "Have a good draw":
        return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
    else:
        return FoldAction()


def OnePair():
    pass