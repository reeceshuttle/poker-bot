from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
# from skeleton.states import GameState, TerminalState, RoundState
# from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
# from skeleton.bot import Bot
# from skeleton.runner import parse_args, run_bot

import eval7
import random
import helpers
# import preflop_strategy

high_card_small_float_range = {
            "AAu":0, "AKs":1, "AQs":1, "AJs":1, "ATs":0, "A9s":0, "A8s":0, "A7s":0, "A6s":0, "A5s":0, "A4s":0, "A3s":0, "A2s":0,
            "AKu":1, "KKu":0, "KQs":1, "KJs":0, "KTs":0, "K9s":0, "K8s":0, "K7s":0, "K6s":0, "K5s":0, "K4s":0, "K3s":0, "K2s":0,
            "AQu":1, "KQu":1, "QQu":0, "QJs":0, "QTs":0, "Q9s":0, "Q8s":0, "Q7s":0, "Q6s":0, "Q5s":0, "Q4s":0, "Q3s":0, "Q2s":0,
            "AJu":0, "KJu":0, "QJu":0, "JJu":0, "JTs":0, "J9s":0, "J8s":0, "J7s":0, "J6s":0, "J5s":0, "J4s":0, "J3s":0, "J2s":0,
            "ATu":0, "KTu":0, "QTu":0, "JTu":0, "TTu":0, "T9s":0, "T8s":0, "T7s":0, "T6s":0, "T5s":0, "T4s":0, "T3s":0, "T2s":0,
            "A9u":0, "K9u":0, "Q9u":0, "J9u":0, "T9u":0, "99u":0, "98s":0, "97s":0, "96s":0, "95s":0, "94s":0, "93s":0, "92s":0,
            "A8u":0, "K8u":0, "Q8u":0, "J8u":0, "T8u":0, "98u":0, "88u":0, "87s":0, "86s":0, "85s":0, "84s":0, "83s":0, "82s":0,
            "A7u":0, "K7u":0, "Q7u":0, "J7u":0, "T7u":0, "97u":0, "87u":0, "77u":0, "76s":0, "75s":0, "74s":0, "73s":0, "72s":0,
            "A6u":0, "K6u":0, "Q6u":0, "J6u":0, "T6u":0, "96u":0, "86u":0, "76u":0, "66u":0, "65s":0, "64s":0, "63s":0, "62s":0,
            "A5u":0, "K5u":0, "Q5u":0, "J5u":0, "T5u":0, "95u":0, "85u":0, "75u":0, "65u":0, "55u":0, "54s":0, "53s":0, "52s":0,
            "A4u":0, "K4u":0, "Q4u":0, "J4u":0, "T4u":0, "94u":0, "84u":0, "74u":0, "64u":0, "54u":0, "44u":0, "43s":0, "42s":0,
            "A3u":0, "K3u":0, "Q3u":0, "J3u":0, "T3u":0, "93u":0, "83u":0, "73u":0, "63u":0, "53u":0, "43u":0, "33u":0, "32s":0,
            "A2u":0, "K2u":0, "Q2u":0, "J2u":0, "T2u":0, "92u":0, "82u":0, "72u":0, "62u":0, "52u":0, "42u":0, "32u":0, "22u":0
            }

def FirstToActStrategy(game_state, round_state, active, we_aggress):
    """
    Used when we are first to act in a postflop scenario.
    """
    legal_actions = round_state.legal_actions()  # the actions you are allowed to take
    street = round_state.street  # int representing pre-flop, flop, turn, or river respectively(5 is when river)
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

    max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
    straight_possibilities = helpers.StraightsCheck(board_cards)
    straight_draws = helpers.StraightsCheck(board_cards+my_cards)
    flush_draws = helpers.FlushDrawCheck(my_cards+board_cards)
    board_rank_occurances = helpers.RankOccuranceCheck(board_cards)
    pairs = helpers.PairChecker(board_cards+my_cards)

    # --------------- strategy: --------------------
    # We want a strategy of betting with made hands and draws
    if made_hand in ["Straight Flush", "Quads", "Full House"]:

        # We are going for big value here.
        if street >= 5: # we want max value on river
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        else:
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))

    elif made_hand == "Flush":

        flush_rank = helpers.MyFlushRank(my_cards, board_cards)
        if max_board_suits==3:
            # We are going for big value here.
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        elif max_board_suits==4:
            if 1 in flush_rank:
                if random.random() < 0.15: return RaiseAction(max_raise)
                else: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))

            elif 2 in flush_rank or 3 in flush_rank:
                return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
            elif 4 in flush_rank:
                return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size))))
            else:
                return CheckAction()
        elif max_board_suits >= 5:
            if 1 in flush_rank:
                if random.random() < 0.2: return RaiseAction(max_raise)
                else: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            elif 2 in flush_rank or 3 in flush_rank:
                return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
            elif 4 in flush_rank:
                return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
            else:
                if random.random() < 0.4: return RaiseAction(min_raise)
                else: return CheckAction()

    elif made_hand == "Straight":

        if max_board_suits <= 3 and straight_possibilities[5] == 0 and straight_possibilities[4] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        elif max_board_suits <= 3 and straight_possibilities[5] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size+3))))
        else:
            return CheckAction()

    # ------straight and flush draw checks here???:------ (we need to check if we contribute the straight draws/flush draws)
    elif straight_draws[4] >= 2 and straight_possibilities[4] == 0:
        return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))

    elif straight_draws[4] == 1 and straight_possibilities[4] == 0:
        return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
    #----------------------------------------------------
    
    elif made_hand == "Trips":

        if board_rank_occurances[3]>0: # trips on board
            return CheckAction()
        elif max_board_suits < 4 and straight_possibilities[4] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(1.2*pot_size+2))))
        else:
            bl = 1 if max_board_suits == 4 else 0
            if random.random()>(9*bl+4*straight_possibilities[4])/20: return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+2))))
            else: return CheckAction()

    elif made_hand == "Two Pair":

        if board_rank_occurances[2]>=2:
            return CheckAction()
        # el
        #     if board_rank_occurances[2] == 0 or random.random()<0.15:
        #         # if not we_aggress and random.random() > 0.5:
        #         #     return CheckAction()
        #         # else:
        #             return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
        #     else:
        #         return CheckAction()
        elif board_rank_occurances[2]==1:
            if max_board_suits == 4 or straight_possibilities[4] > 1: # many draws
                pass

            if 1 in pairs:
                return RaiseAction(min(max_raise, max(min_raise, int(0.9*pot_size))))
            elif 2 in pairs:
                return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
            elif 3 in pairs:
                # if we_aggress:
                    return RaiseAction(min(max_raise, max(min_raise, int(0.4*pot_size))))  
                # else:
                #     return CheckAction()
            else:
                # if we_aggress:
                    return RaiseAction(min(max_raise, max(min_raise, int(0.25*pot_size))))
                # else:
                #     return CheckAction()
        elif board_rank_occurances[2]==0:
            if max_board_suits == 4 or straight_possibilities[4] > 1: # many draws
                return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size+2))))
            else:
                return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))

    elif made_hand == "Pair":

        if max_board_suits == 4 or straight_possibilities[4] > 0:
            if 1 in pairs: return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
            else: return CheckAction()

        elif board_rank_occurances[2] == 1: # if the pair is on the board
            return CheckAction()
        else:
            if 1 in pairs: # top pair
                return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            elif 2 in pairs: # second pair
                if we_aggress or street == 3:
                    return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
                else:
                    return CheckAction()
            elif 3 in pairs: # third pair
                if street <= 4 and we_aggress and pot_size < 80: 
                    return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+2))))
                else: 
                    return CheckAction()
            else:
                if we_aggress and pot_size < 30: 
                    return RaiseAction(min(max_raise, max(min_raise, int(0.2*pot_size+2))))
                else: 
                    return CheckAction()
    else:
        if street == 3:
            return RaiseAction(2)
        else:
            return CheckAction()

def CheckedToStrategy(game_state, round_state, active):
    """
    Used when we are checked to in a postflop scenario.
    """
    legal_actions = round_state.legal_actions()  # the actions you are allowed to take
    street = round_state.street  # int representing pre-flop, flop, turn, or river respectively(5 is when river)
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

    max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
    straight_possibilities = helpers.StraightsCheck(board_cards)
    straight_draws = helpers.StraightsCheck(board_cards+my_cards)
    flush_draws = helpers.FlushDrawCheck(my_cards+board_cards)
    board_rank_occurances = helpers.RankOccuranceCheck(board_cards)
    pairs = helpers.PairChecker(board_cards+my_cards)

    # --------------- strategy: --------------------
    # We want a strategy of betting with made hands and draws
    if made_hand in ["Straight Flush", "Quads", "Full House"]:

        # We are going for big value here.
        if street >= 5: # we want max value on river
            return RaiseAction(max_raise)
            # return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        else:
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))

    elif made_hand == "Flush":

        flush_rank = helpers.MyFlushRank(my_cards, board_cards)
        if max_board_suits==3:
            # We are going for big value here.
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        elif max_board_suits==4:
            if 1 in flush_rank:
                if random.random() < 0.15: return RaiseAction(max_raise)
                else: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))

            elif 2 in flush_rank or 3 in flush_rank:
                return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
            elif 4 in flush_rank:
                return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size))))
            else:
                return CheckAction()
        elif max_board_suits >= 5:
            if 1 in flush_rank:
                if random.random() < 0.2: return RaiseAction(max_raise)
                else: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            elif 2 in flush_rank or 3 in flush_rank:
                return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
            elif 4 in flush_rank:
                return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
            else:
                if random.random() < 0.4: return RaiseAction(min_raise)
                else: return CheckAction()

    elif made_hand == "Straight":

        if max_board_suits <= 3 and straight_possibilities[5] == 0 and straight_possibilities[4] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(1.1*pot_size+2))))
        elif max_board_suits <= 3 and straight_possibilities[5] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size+3))))
        else:
            return CheckAction()

    # ------straight and flush draw checks here???:------ (we need to check if we contribute the straight draws/flush draws)
    elif straight_draws[4] >= 2 and straight_possibilities[4] == 0:
        return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))

    elif straight_draws[4] == 1 and straight_possibilities[4] == 0:
        return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
    #----------------------------------------------------
    
    elif made_hand == "Trips":

        if board_rank_occurances[3]>0: # trips on board
            return CheckAction()
        elif max_board_suits < 4 and straight_possibilities[4] == 0:
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
        else:
            bl = 1 if max_board_suits == 4 else 0
            print(f'bl:{bl}')
            if random.random()>(9*bl+4*straight_possibilities[4])/20: return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+2))))
            else: return CheckAction()

    elif made_hand == "Two Pair":

        if board_rank_occurances[2]>=2:
            return CheckAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0:
            if board_rank_occurances[2] == 0 or random.random()<0.15:
                return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
            else:
                return CheckAction()
        elif board_rank_occurances[2]==1:
            if 1 in pairs:
                return RaiseAction(min(max_raise, max(min_raise, int(0.9*pot_size))))
            elif 2 in pairs:
                return RaiseAction(min(max_raise, max(min_raise, int(0.6*pot_size))))
            elif 3 in pairs:
                return RaiseAction(min(max_raise, max(min_raise, int(0.4*pot_size))))  
            else:
                return RaiseAction(min(max_raise, max(min_raise, int(0.25*pot_size))))
        elif board_rank_occurances[2]==0:
            return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))

    elif made_hand == "Pair":

        if max_board_suits == 4 or straight_possibilities[4] > 0:
            if 1 in pairs: return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
            else: return CheckAction()

        elif board_rank_occurances[2] == 1: # if the pair is on the board
            if street == 3 or random.random() < 0.5: return RaiseAction(2)
            else: return CheckAction()
        else:
            if 1 in pairs: # top pair
                return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            elif 2 in pairs: # second pair
                return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
            elif 3 in pairs: # third pair
                if random.random() < 0.8: return RaiseAction(min(max_raise, max(min_raise, int(0.5*pot_size+2))))
                else: return CheckAction()
            else:
                if random.random() < 0.1: return RaiseAction(min(max_raise, max(min_raise, int(0.2*pot_size+2))))
                else: return CheckAction()
    else: # high card
        if street == 3 or random.random() < 0.5: return RaiseAction(2)
        else: return CheckAction()

def ICheckedTheyBetStrategy(game_state, round_state, active):
    """
    Used when I checked postflop and they bet.
    """
    legal_actions = round_state.legal_actions()  # the actions you are allowed to take
    street = round_state.street  # int representing pre-flop, flop, turn, or river respectively
    my_cards = round_state.hands[active]  # your cards
    board_cards = round_state.deck[:street]  # the board cards
    parsed_hand = helpers.ParseHoleCards(my_cards)
    hand = [eval7.Card(card) for card in my_cards+board_cards]
    made_hand = eval7.handtype(eval7.evaluate(hand))
    if RaiseAction in legal_actions:
        min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
    my_stack = round_state.stacks[active]  # the number of chips you have remaining
    opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
    opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
    pot_size = 800 - my_stack - opp_stack

    max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
    straight_possibilities = helpers.StraightsCheck(board_cards)
    straight_draws = helpers.StraightsCheck(board_cards+my_cards)
    flush_draws = helpers.FlushDrawCheck(my_cards+board_cards)
    board_rank_occurances = helpers.RankOccuranceCheck(board_cards)
    pairs = helpers.PairChecker(board_cards+my_cards)

    # --------------- strategy: --------------------
    if made_hand in ["Straight Flush", "Quads", "Full House"]:

        # We are going for big value here.
        if street >= 5: # we want max value on river
            if RaiseAction in legal_actions: return RaiseAction(max_raise)
            # if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        else:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()

    elif made_hand == "Flush":

        flush_rank = helpers.MyFlushRank(my_cards, board_cards)
        if flush_rank == []:
            # finish this later: if we also have two pair or trips, continue for non big bets
            # if made_hand == "Trips" and opp_pip <= 50:
            #     return CallAction()
            # elif made_hand == "Two Pair" and opp_pip < 40:
            #     return CallAction()
            # else:
                return FoldAction()
        elif max_board_suits==3:
            # We are going for big value here.
            if RaiseAction in legal_actions: 
                if random.random() < 0.2: return RaiseAction(max_raise)
                else: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        elif max_board_suits==4:
            if 1 in flush_rank:
                if RaiseAction in legal_actions: 
                    if random.random() < 0.4: return RaiseAction(max_raise)
                    else: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                else: return CallAction()
            elif 2 in flush_rank:
                if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size))))
                else: return CallAction()
            elif 3 in flush_rank:
                if opp_pip < 20:
                    if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
                    else: return CallAction()
                else: # this might be a leak
                    return CallAction()
            elif 4 in flush_rank:
                if opp_pip < 35:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                if opp_pip < 10:
                    return CallAction()
                else:
                    return FoldAction()
        elif max_board_suits >= 5:
            if 1 in flush_rank:
                if RaiseAction in legal_actions: 
                    if random.random() < 0.5: return RaiseAction(max_raise)
                    else: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+5))))
                else: return CallAction()
            elif 2 in flush_rank:
                if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size))))
                else: return CallAction()
            elif 3 in flush_rank:
                if opp_pip < 20:
                    if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
                    else: return CallAction()
                else: # this might be a leak
                    return CallAction()
            elif 4 in flush_rank:
                if opp_pip < 50:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                if opp_pip < 40:
                    return CallAction()
                else:
                    return FoldAction()

    elif made_hand == "Straight":

        if max_board_suits <= 3 and straight_possibilities[5] == 0 and straight_possibilities[4] == 0:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(1.1*pot_size+2))))
            else: return CallAction()
        elif max_board_suits <= 3 and straight_possibilities[5] == 0:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(0.9*pot_size+2))))
            else: return CallAction()
        elif max_board_suits == 4 and straight_possibilities[5] == 0: # extend this
            if opp_pip < 40:
                return CallAction()
            else:
                return FoldAction()
        else:
            return FoldAction()

    # ----- straight and flush draw checks here???: --------

    elif made_hand == "Trips":

        if board_rank_occurances[3]>0: # trips on board
            return FoldAction()
        elif max_board_suits < 4 and straight_possibilities[4] == 0:
            if RaiseAction in legal_actions:
                if street >= 5 or random.random() > 0.5: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                else: return CallAction()
            else: return CallAction()
        elif opp_pip <= 30:
            return CallAction()
        else:
            bl = 1 if max_board_suits == 4 else 0
            if random.random()>(9*bl+4*straight_possibilities[4])/30: return CallAction()
            else: return FoldAction()
    
    elif made_hand == "Two Pair":

        if board_rank_occurances[2]>=2:
            return FoldAction()
            # --- work starting here ---
        elif max_board_suits == 4 and straight_possibilities[4] > 0:
            if board_rank_occurances[2]==0 and opp_pip < 50:
                return CallAction()
            elif opp_pip < 20:
                return CallAction()
            else:
                return FoldAction()
        elif max_board_suits == 4:
            if board_rank_occurances[2]==0 and opp_pip < 75:
                return CallAction()
            elif 1 in pairs and opp_pip < 60:
                return CallAction()
            elif opp_pip < 25:
                return CallAction()
            else:
                return FoldAction()
        elif board_rank_occurances[2]==1:
            if 1 in pairs:
                if opp_pip < 100 or random.random() < 0.20:
                    return CallAction()
                else:
                    return FoldAction()
            elif 2 in pairs:
                if opp_pip < 70 or random.random() < 0.1:
                    return CallAction()
                else:
                    return FoldAction()
            elif 3 in pairs:
                if opp_pip < 30:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                return FoldAction()
        elif board_rank_occurances[2]==0:
            if straight_possibilities[4] > 0:
                if 1 in pairs:
                    if opp_pip > 25:
                        return CallAction()
                    else:
                        if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size))))
                        else: return CallAction()
                elif 2 in pairs:
                    if opp_pip < 100 or random.random() < 0.2*(2-straight_possibilities[4]):
                        return CallAction()
                    else: return FoldAction()
                else:
                    if opp_pip < 80 or random.random() < 0.15*(2-straight_possibilities[4]):
                        return CallAction()
                    else: return FoldAction()
            else: # no one card draws
                if opp_pip > 20 and street < 5:
                    if 1 in pairs and random.random() < 0.25:
                        if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                        else: return CallAction()
                    else:
                        return CallAction()
                else:
                    if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                    else: return CallAction()

    elif made_hand == "Pair":
        
        if board_rank_occurances[2] == 1: # pair is on the board
            return FoldAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0: # we make the pair, but one card draws
            bl = 1 if max_board_suits == 4 else 0
            if 1 in pairs:
                if opp_pip < 80 or random.random()>(9*bl+4*straight_possibilities[4])/25:
                    return CallAction()
                else: return FoldAction()
            elif 2 in pairs:
                if opp_pip < 20 or random.random()>(9*bl+4*straight_possibilities[4])/12:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                return FoldAction()
        else: # we make the pair and no one card draws
            if 1 in pairs:
                # is this too wide?
                if RaiseAction in legal_actions and opp_pip < 25: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                else: return CallAction()
            elif 2 in pairs:
                if opp_pip < 50 or random.random() < 0.15:
                    return CallAction()
                else: return FoldAction()
            else:
                if opp_pip < 8:
                    return CallAction()
                else:
                    return FoldAction()
    else: # we have high card
        if opp_pip <= 5 and high_card_small_float_range[parsed_hand] == 1:
            return CallAction()
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
    parsed_hand = helpers.ParseHoleCards(my_cards)
    my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
    opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        
    hand = [eval7.Card(card) for card in my_cards+board_cards]
    made_hand = eval7.handtype(eval7.evaluate(hand))
    if RaiseAction in legal_actions:
        min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
    my_stack = round_state.stacks[active]  # the number of chips you have remaining
    opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
    pot_size = 800 - my_stack - opp_stack

    max_board_suits, msuit = helpers.MaxSuitCount(board_cards)
    straight_possibilities = helpers.StraightsCheck(board_cards)
    straight_draws = helpers.StraightsCheck(board_cards+my_cards)
    flush_draws = helpers.FlushDrawCheck(my_cards+board_cards)
    board_rank_occurances = helpers.RankOccuranceCheck(board_cards)
    pairs = helpers.PairChecker(board_cards+my_cards)

    # --------------- strategy: --------------------
    if made_hand in ["Straight Flush", "Quads", "Full House"]:

        # We are going for big value here.
        if street >= 5: # we want max value on river
            if RaiseAction in legal_actions: return RaiseAction(max_raise)
            # if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        else:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()

    elif made_hand == "Flush":

        flush_rank = helpers.MyFlushRank(my_cards, board_cards)
        if flush_rank == []:
            # finish this later: if we also have two pair or trips, continue for non big bets
            # if made_hand == "Trips" and opp_pip <= 50:
            #     return CallAction()
            # elif made_hand == "Two Pair" and opp_pip < 40:
            #     return CallAction()
            # else:
                return FoldAction()
        elif max_board_suits==3:
            # We are going for big value here.
            if RaiseAction in legal_actions: 
                if random.random() < 0.2: return RaiseAction(max_raise)
                else: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        elif max_board_suits==4:
            if 1 in flush_rank:
                if RaiseAction in legal_actions: 
                    if random.random() < 0.4: return RaiseAction(max_raise)
                    else: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                else: return CallAction()
            elif 2 in flush_rank:
                if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size))))
                else: return CallAction()
            elif 3 in flush_rank:
                if opp_pip < 20:
                    if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
                    else: return CallAction()
                else: # this might be a leak
                    return CallAction()
            elif 4 in flush_rank:
                if opp_pip < 35:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                if opp_pip < 10:
                    return CallAction()
                else:
                    return FoldAction()
        elif max_board_suits >= 5:
            if 1 in flush_rank:
                if RaiseAction in legal_actions: 
                    if random.random() < 0.5: return RaiseAction(max_raise)
                    else: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+5))))
                else: return CallAction()
            elif 2 in flush_rank:
                if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size))))
                else: return CallAction()
            elif 3 in flush_rank:
                if opp_pip < 20:
                    if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(0.8*pot_size))))
                    else: return CallAction()
                else: # this might be a leak
                    return CallAction()
            elif 4 in flush_rank:
                if opp_pip < 50:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                if opp_pip < 40:
                    return CallAction()
                else:
                    return FoldAction()

    elif made_hand == "Straight":

        if max_board_suits <= 3 and straight_possibilities[5] == 0 and straight_possibilities[4] == 0:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
            else: return CallAction()
        elif max_board_suits <= 3 and straight_possibilities[5] == 0:
            if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(0.9*pot_size+2))))
            else: return CallAction()
        elif max_board_suits == 4 and straight_possibilities[5] == 0: # extend this
            if opp_pip < 40:
                return CallAction()
            else:
                return FoldAction()
        else:
            return FoldAction()

    # ----- straight and flush draw checks here???: --------

    elif made_hand == "Trips":

        if board_rank_occurances[3]>0: # trips on board
            return FoldAction()
        elif max_board_suits < 4 and straight_possibilities[4] == 0:
            if RaiseAction in legal_actions:
                if street >= 5 or random.random() > 0.5: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                else: return CallAction()
            else: return CallAction()
        elif opp_pip <= 30:
            return CallAction()
        else:
            bl = 1 if max_board_suits == 4 else 0
            if random.random()>(9*bl+4*straight_possibilities[4])/30: return CallAction()
            else: return FoldAction()
    
    elif made_hand == "Two Pair":

        if board_rank_occurances[2]>=2:
            return FoldAction()
            # --- work starting here ---
        elif max_board_suits == 4 and straight_possibilities[4] > 0:
            if board_rank_occurances[2]==0 and opp_pip < 50:
                return CallAction()
            elif opp_pip < 20:
                return CallAction()
            else:
                return FoldAction()
        elif max_board_suits == 4:
            if board_rank_occurances[2]==0 and opp_pip < 75:
                return CallAction()
            elif 1 in pairs and opp_pip < 60:
                return CallAction()
            elif opp_pip < 25:
                return CallAction()
            else:
                return FoldAction()
        elif board_rank_occurances[2]==1:
            if 1 in pairs:
                if opp_pip < 100 or random.random() < 0.20:
                    return CallAction()
                else:
                    return FoldAction()
            elif 2 in pairs:
                if opp_pip < 70 or random.random() < 0.1:
                    return CallAction()
                else:
                    return FoldAction()
            elif 3 in pairs:
                if opp_pip < 30:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                return FoldAction()
        elif board_rank_occurances[2]==0:
            if straight_possibilities[4] > 0:
                if 1 in pairs:
                    if opp_pip > 25:
                        return CallAction()
                    else:
                        if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size))))
                        else: return CallAction()
                elif 2 in pairs:
                    if opp_pip < 100 or random.random() < 0.2*(2-straight_possibilities[4]):
                        return CallAction()
                    else: return FoldAction()
                else:
                    if opp_pip < 80 or random.random() < 0.15*(2-straight_possibilities[4]):
                        return CallAction()
                    else: return FoldAction()
            else: # no one card draws
                if opp_pip > 20 and street < 5:
                    if 1 in pairs and random.random() < 0.25:
                        if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                        else: return CallAction()
                    else:
                        return CallAction()
                else:
                    if RaiseAction in legal_actions: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                    else: return CallAction()

    elif made_hand == "Pair":
        
        if board_rank_occurances[2] == 1: # pair is on the board
            return FoldAction()
        elif max_board_suits == 4 or straight_possibilities[4] > 0: # we make the pair, but one card draws
            bl = 1 if max_board_suits == 4 else 0
            if 1 in pairs:
                if opp_pip < 80 or random.random()>(9*bl+4*straight_possibilities[4])/25:
                    return CallAction()
                else: return FoldAction()
            elif 2 in pairs:
                if opp_pip < 20 or random.random()>(9*bl+4*straight_possibilities[4])/12:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                return FoldAction()
        else: # we make the pair and no one card draws
            if 1 in pairs:
                # is this too wide?
                if RaiseAction in legal_actions and opp_pip < 25: return RaiseAction(min(max_raise, max(min_raise, int(pot_size+2))))
                else: return CallAction()
            elif 2 in pairs:
                if opp_pip < 50 or random.random() < 0.15:
                    return CallAction()
                else: return FoldAction()
            else:
                if opp_pip < 8:
                    return CallAction()
                else:
                    return FoldAction()
    else: # we have high card
        if opp_pip <= 5 and high_card_small_float_range[parsed_hand] == 1:
            return CallAction()
        else:
            return FoldAction()

def IBetTheyRaisedStrategy(game_state, round_state, active):
    return BetIntoStrategy(game_state, round_state, active)