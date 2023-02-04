from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot


import helpers
import eval7
import random

def OpeningStrategy(game_state, round_state, active):
    """Used when on the button, always opens to 2.5x"""
    open_chart = {
        "AAu":1, "AKs":1, "AQs":1, "AJs":1, "ATs":1, "A9s":1, "A8s":1, "A7s":1, "A6s":1, "A5s":1, "A4s":1, "A3s":1, "A2s":1,
        "AKu":1, "KKu":1, "KQs":1, "KJs":1, "KTs":1, "K9s":1, "K8s":1, "K7s":1, "K6s":1, "K5s":1, "K4s":1, "K3s":1, "K2s":1,
        "AQu":1, "KQu":1, "QQu":1, "QJs":1, "QTs":1, "Q9s":1, "Q8s":1, "Q7s":1, "Q6s":1, "Q5s":1, "Q4s":1, "Q3s":1, "Q2s":1,
        "AJu":1, "KJu":1, "QJu":1, "JJu":1, "JTs":1, "J9s":1, "J8s":1, "J7s":1, "J6s":1, "J5s":1, "J4s":1, "J3s":1, "J2s":1,
        "ATu":1, "KTu":1, "QTu":1, "JTu":1, "TTu":1, "T9s":1, "T8s":1, "T7s":1, "T6s":1, "T5s":1, "T4s":1, "T3s":1, "T2s":1,
        "A9u":1, "K9u":1, "Q9u":1, "J9u":1, "T9u":1, "99u":1, "98s":1, "97s":1, "96s":1, "95s":1, "94s":1, "93s":1, "92s":1,
        "A8u":1, "K8u":1, "Q8u":1, "J8u":1, "T8u":1, "98u":1, "88u":1, "87s":1, "86s":1, "85s":1, "84s":1, "83s":1, "82s":1,
        "A7u":1, "K7u":1, "Q7u":1, "J7u":1, "T7u":1, "97u":1, "87u":1, "77u":1, "76s":1, "75s":1, "74s":1, "73s":1, "72s":1,
        "A6u":1, "K6u":1, "Q6u":1, "J6u":1, "T6u":1, "96u":1, "86u":1, "76u":1, "66u":1, "65s":1, "64s":1, "63s":1, "62s":1,
        "A5u":1, "K5u":1, "Q5u":1, "J5u":1, "T5u":1, "95u":1, "85u":1, "75u":1, "65u":1, "55u":1, "54s":1, "53s":1, "52s":1,
        "A4u":1, "K4u":1, "Q4u":1, "J4u":1, "T4u":1, "94u":0, "84u":0, "74u":0, "64u":0, "54u":1, "44u":1, "43s":1, "42s":1,
        "A3u":1, "K3u":1, "Q3u":1, "J3u":1, "T3u":0, "93u":0, "83u":0, "73u":0, "63u":0, "53u":0, "43u":0, "33u":1, "32s":1,
        "A2u":1, "K2u":1, "Q2u":1, "J2u":0, "T2u":0, "92u":0, "82u":0, "72u":0, "62u":0, "52u":0, "42u":0, "32u":0, "22u":1}
    
    my_cards = round_state.hands[active]  # your cards
    parsed_hand = helpers.ParseHoleCards(my_cards)
    # print(f'my_cards:{my_cards}')
    # print(f'parsed cards:{helpers.ParseHoleCards(my_cards)}')

    # --------------- strategy: --------------------
    if open_chart[parsed_hand] == 1:
        return RaiseAction(5) # raise 2.5x
    else:
        return FoldAction()

def DefenseStrategy(game_state, round_state, active):
    """
    Used when you are raised into.
    """
    under2p5x_defense_chart =  {
            "AAu":2, "AKs":2, "AQs":2, "AJs":2, "ATs":2, "A9s":2, "A8s":2, "A7s":2, "A6s":1, "A5s":1, "A4s":1, "A3s":1, "A2s":1,
            "AKu":2, "KKu":2, "KQs":2, "KJs":2, "KTs":2, "K9s":1, "K8s":1, "K7s":1, "K6s":1, "K5s":1, "K4s":1, "K3s":1, "K2s":1,
            "AQu":2, "KQu":2, "QQu":2, "QJs":2, "QTs":1, "Q9s":1, "Q8s":1, "Q7s":1, "Q6s":1, "Q5s":1, "Q4s":0, "Q3s":0, "Q2s":0,
            "AJu":2, "KJu":2, "QJu":1, "JJu":2, "JTs":2, "J9s":1, "J8s":1, "J7s":1, "J6s":0, "J5s":0, "J4s":0, "J3s":0, "J2s":0,
            "ATu":2, "KTu":1, "QTu":1, "JTu":1, "TTu":2, "T9s":1, "T8s":1, "T7s":1, "T6s":0, "T5s":0, "T4s":0, "T3s":0, "T2s":0,
            "A9u":1, "K9u":1, "Q9u":1, "J9u":1, "T9u":1, "99u":2, "98s":1, "97s":1, "96s":1, "95s":0, "94s":0, "93s":0, "92s":0,
            "A8u":1, "K8u":1, "Q8u":1, "J8u":0, "T8u":0, "98u":1, "88u":2, "87s":1, "86s":1, "85s":0, "84s":0, "83s":0, "82s":0,
            "A7u":1, "K7u":1, "Q7u":0, "J7u":0, "T7u":0, "97u":0, "87u":0, "77u":1, "76s":1, "75s":1, "74s":0, "73s":0, "72s":0,
            "A6u":1, "K6u":1, "Q6u":0, "J6u":0, "T6u":0, "96u":0, "86u":0, "76u":0, "66u":1, "65s":1, "64s":0, "63s":0, "62s":0,
            "A5u":1, "K5u":1, "Q5u":0, "J5u":0, "T5u":0, "95u":0, "85u":0, "75u":0, "65u":0, "55u":1, "54s":1, "53s":0, "52s":0,
            "A4u":1, "K4u":0, "Q4u":0, "J4u":0, "T4u":0, "94u":0, "84u":0, "74u":0, "64u":0, "54u":0, "44u":1, "43s":1, "42s":0,
            "A3u":1, "K3u":0, "Q3u":0, "J3u":0, "T3u":0, "93u":0, "83u":0, "73u":0, "63u":0, "53u":0, "43u":0, "33u":1, "32s":1,
            "A2u":1, "K2u":0, "Q2u":0, "J2u":0, "T2u":0, "92u":0, "82u":0, "72u":0, "62u":0, "52u":0, "42u":0, "32u":0, "22u":1
            }


    under3x_defense_chart =  {
            "AAu":2, "AKs":2, "AQs":2, "AJs":2, "ATs":2, "A9s":2, "A8s":2, "A7s":1, "A6s":1, "A5s":1, "A4s":1, "A3s":1, "A2s":1,
            "AKu":2, "KKu":2, "KQs":2, "KJs":2, "KTs":2, "K9s":1, "K8s":1, "K7s":1, "K6s":1, "K5s":1, "K4s":1, "K3s":1, "K2s":1,
            "AQu":2, "KQu":2, "QQu":2, "QJs":2, "QTs":1, "Q9s":1, "Q8s":1, "Q7s":1, "Q6s":1, "Q5s":1, "Q4s":0, "Q3s":0, "Q2s":0,
            "AJu":2, "KJu":2, "QJu":1, "JJu":2, "JTs":1, "J9s":1, "J8s":1, "J7s":1, "J6s":0, "J5s":0, "J4s":0, "J3s":0, "J2s":0,
            "ATu":2, "KTu":1, "QTu":1, "JTu":1, "TTu":2, "T9s":1, "T8s":1, "T7s":1, "T6s":0, "T5s":0, "T4s":0, "T3s":0, "T2s":0,
            "A9u":1, "K9u":1, "Q9u":1, "J9u":1, "T9u":1, "99u":2, "98s":1, "97s":1, "96s":1, "95s":0, "94s":0, "93s":0, "92s":0,
            "A8u":1, "K8u":1, "Q8u":1, "J8u":0, "T8u":0, "98u":1, "88u":2, "87s":1, "86s":1, "85s":0, "84s":0, "83s":0, "82s":0,
            "A7u":1, "K7u":1, "Q7u":0, "J7u":0, "T7u":0, "97u":0, "87u":0, "77u":1, "76s":1, "75s":1, "74s":0, "73s":0, "72s":0,
            "A6u":1, "K6u":1, "Q6u":0, "J6u":0, "T6u":0, "96u":0, "86u":0, "76u":0, "66u":1, "65s":1, "64s":0, "63s":0, "62s":0,
            "A5u":1, "K5u":1, "Q5u":0, "J5u":0, "T5u":0, "95u":0, "85u":0, "75u":0, "65u":0, "55u":1, "54s":1, "53s":0, "52s":0,
            "A4u":1, "K4u":0, "Q4u":0, "J4u":0, "T4u":0, "94u":0, "84u":0, "74u":0, "64u":0, "54u":0, "44u":1, "43s":1, "42s":0,
            "A3u":1, "K3u":0, "Q3u":0, "J3u":0, "T3u":0, "93u":0, "83u":0, "73u":0, "63u":0, "53u":0, "43u":0, "33u":1, "32s":1,
            "A2u":1, "K2u":0, "Q2u":0, "J2u":0, "T2u":0, "92u":0, "82u":0, "72u":0, "62u":0, "52u":0, "42u":0, "32u":0, "22u":1
            }


    under4x_defense_chart =  {
            "AAu":2, "AKs":2, "AQs":2, "AJs":2, "ATs":2, "A9s":2, "A8s":2, "A7s":1, "A6s":1, "A5s":1, "A4s":1, "A3s":1, "A2s":1,
            "AKu":2, "KKu":2, "KQs":2, "KJs":2, "KTs":2, "K9s":1, "K8s":1, "K7s":1, "K6s":1, "K5s":1, "K4s":1, "K3s":1, "K2s":1,
            "AQu":2, "KQu":2, "QQu":2, "QJs":2, "QTs":1, "Q9s":1, "Q8s":1, "Q7s":1, "Q6s":1, "Q5s":1, "Q4s":0, "Q3s":0, "Q2s":0,
            "AJu":2, "KJu":2, "QJu":1, "JJu":2, "JTs":1, "J9s":1, "J8s":1, "J7s":1, "J6s":0, "J5s":0, "J4s":0, "J3s":0, "J2s":0,
            "ATu":2, "KTu":1, "QTu":1, "JTu":1, "TTu":2, "T9s":1, "T8s":1, "T7s":1, "T6s":0, "T5s":0, "T4s":0, "T3s":0, "T2s":0,
            "A9u":1, "K9u":1, "Q9u":1, "J9u":1, "T9u":1, "99u":2, "98s":1, "97s":1, "96s":1, "95s":0, "94s":0, "93s":0, "92s":0,
            "A8u":1, "K8u":1, "Q8u":0, "J8u":0, "T8u":0, "98u":0, "88u":2, "87s":1, "86s":1, "85s":0, "84s":0, "83s":0, "82s":0,
            "A7u":1, "K7u":1, "Q7u":0, "J7u":0, "T7u":0, "97u":0, "87u":0, "77u":1, "76s":1, "75s":1, "74s":0, "73s":0, "72s":0,
            "A6u":1, "K6u":1, "Q6u":0, "J6u":0, "T6u":0, "96u":0, "86u":0, "76u":0, "66u":1, "65s":1, "64s":0, "63s":0, "62s":0,
            "A5u":1, "K5u":1, "Q5u":0, "J5u":0, "T5u":0, "95u":0, "85u":0, "75u":0, "65u":0, "55u":1, "54s":1, "53s":0, "52s":0,
            "A4u":1, "K4u":0, "Q4u":0, "J4u":0, "T4u":0, "94u":0, "84u":0, "74u":0, "64u":0, "54u":0, "44u":1, "43s":1, "42s":0,
            "A3u":1, "K3u":0, "Q3u":0, "J3u":0, "T3u":0, "93u":0, "83u":0, "73u":0, "63u":0, "53u":0, "43u":0, "33u":1, "32s":0,
            "A2u":1, "K2u":0, "Q2u":0, "J2u":0, "T2u":0, "92u":0, "82u":0, "72u":0, "62u":0, "52u":0, "42u":0, "32u":0, "22u":1
            }

    # over 4x will be more agressive with strong and be folding a lot more.

    over4x_defense_chart = {
            "AAu":3, "AKs":3, "AQs":3, "AJs":2, "ATs":2, "A9s":1, "A8s":1, "A7s":1, "A6s":1, "A5s":1, "A4s":1, "A3s":1, "A2s":1,
            "AKu":3, "KKu":3, "KQs":3, "KJs":2, "KTs":1, "K9s":1, "K8s":1, "K7s":1, "K6s":1, "K5s":1, "K4s":1, "K3s":1, "K2s":1,
            "AQu":3, "KQu":2, "QQu":3, "QJs":2, "QTs":1, "Q9s":1, "Q8s":1, "Q7s":1, "Q6s":1, "Q5s":1, "Q4s":0, "Q3s":0, "Q2s":0,
            "AJu":1, "KJu":1, "QJu":1, "JJu":3, "JTs":1, "J9s":1, "J8s":1, "J7s":1, "J6s":0, "J5s":0, "J4s":0, "J3s":0, "J2s":0,
            "ATu":1, "KTu":1, "QTu":1, "JTu":1, "TTu":3, "T9s":1, "T8s":1, "T7s":1, "T6s":0, "T5s":0, "T4s":0, "T3s":0, "T2s":0,
            "A9u":1, "K9u":1, "Q9u":1, "J9u":1, "T9u":1, "99u":3, "98s":1, "97s":1, "96s":1, "95s":0, "94s":0, "93s":0, "92s":0,
            "A8u":1, "K8u":1, "Q8u":1, "J8u":0, "T8u":0, "98u":0, "88u":2, "87s":1, "86s":1, "85s":0, "84s":0, "83s":0, "82s":0,
            "A7u":1, "K7u":1, "Q7u":0, "J7u":0, "T7u":0, "97u":0, "87u":0, "77u":2, "76s":1, "75s":1, "74s":0, "73s":0, "72s":0,
            "A6u":1, "K6u":1, "Q6u":0, "J6u":0, "T6u":0, "96u":0, "86u":0, "76u":0, "66u":1, "65s":1, "64s":0, "63s":0, "62s":0,
            "A5u":1, "K5u":1, "Q5u":0, "J5u":0, "T5u":0, "95u":0, "85u":0, "75u":0, "65u":0, "55u":1, "54s":1, "53s":0, "52s":0,
            "A4u":1, "K4u":0, "Q4u":0, "J4u":0, "T4u":0, "94u":0, "84u":0, "74u":0, "64u":0, "54u":0, "44u":1, "43s":1, "42s":0,
            "A3u":1, "K3u":0, "Q3u":0, "J3u":0, "T3u":0, "93u":0, "83u":0, "73u":0, "63u":0, "53u":0, "43u":0, "33u":1, "32s":0,
            "A2u":1, "K2u":0, "Q2u":0, "J2u":0, "T2u":0, "92u":0, "82u":0, "72u":0, "62u":0, "52u":0, "42u":0, "32u":0, "22u":1
            }
    my_cards = round_state.hands[active]  # your cards
    parsed_hand = helpers.ParseHoleCards(my_cards)

    legal_actions = round_state.legal_actions()  # the actions you are allowed to take
    my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
    opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
    if RaiseAction in legal_actions:
        min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise

    # --------------- strategy: --------------------
    if opp_pip <= 5:
        if under2p5x_defense_chart[parsed_hand] == 2:
            return RaiseAction(14)
        elif under2p5x_defense_chart[parsed_hand] == 1:
            if random.random() < 0.4: return RaiseAction(min_raise)
            else: return CallAction()
        elif under2p5x_defense_chart[parsed_hand] == 0:
            return FoldAction()
    if opp_pip <= 6:
        if under3x_defense_chart[parsed_hand] == 2:
            return RaiseAction(18)
        elif under3x_defense_chart[parsed_hand] == 1:
            if random.random() < 0.4: return RaiseAction(min_raise)
            else: return CallAction()
        elif under3x_defense_chart[parsed_hand] == 0:
            return FoldAction()
    if opp_pip <= 8:
        if under4x_defense_chart[parsed_hand] == 2:
            return RaiseAction(24)
        elif under4x_defense_chart[parsed_hand] == 1:
            if random.random() < 0.15: return RaiseAction(min_raise)
            else: return CallAction()
        elif under4x_defense_chart[parsed_hand] == 0:
            return FoldAction()
    elif opp_pip <= 30:
        if over4x_defense_chart[parsed_hand] == 3:
            if random.random() < 0.4: return RaiseAction(max_raise)
            else: return RaiseAction(3*opp_pip)
        elif over4x_defense_chart[parsed_hand] == 2:
            return RaiseAction(3*opp_pip)
        elif over4x_defense_chart[parsed_hand] == 1:
            return CallAction()
        elif over4x_defense_chart[parsed_hand] == 0:
            return FoldAction()
    else:
        if over4x_defense_chart[parsed_hand] == 3 or parsed_hand in ['AQu', 'KQs']:
            if RaiseAction in legal_actions: return RaiseAction(max_raise)
            else: return CallAction()
        else:
            return FoldAction()

    

def LimpStrategy(game_state, round_state, active):
    """
    Used when you are limped to.
    """
    limp_chart =  {
        "AAu":1, "AKs":1, "AQs":1, "AJs":1, "ATs":1, "A9s":1, "A8s":1, "A7s":1, "A6s":1, "A5s":1, "A4s":1, "A3s":1, "A2s":1,
        "AKu":1, "KKu":1, "KQs":1, "KJs":1, "KTs":1, "K9s":1, "K8s":1, "K7s":1, "K6s":1, "K5s":1, "K4s":1, "K3s":1, "K2s":1,
        "AQu":1, "KQu":1, "QQu":1, "QJs":1, "QTs":1, "Q9s":1, "Q8s":1, "Q7s":1, "Q6s":1, "Q5s":1, "Q4s":1, "Q3s":0, "Q2s":0,
        "AJu":1, "KJu":1, "QJu":1, "JJu":1, "JTs":1, "J9s":1, "J8s":1, "J7s":1, "J6s":0, "J5s":0, "J4s":0, "J3s":0, "J2s":0,
        "ATu":1, "KTu":1, "QTu":1, "JTu":1, "TTu":1, "T9s":1, "T8s":1, "T7s":1, "T6s":0, "T5s":0, "T4s":0, "T3s":0, "T2s":0,
        "A9u":1, "K9u":1, "Q9u":1, "J9u":2, "T9u":2, "99u":1, "98s":1, "97s":1, "96s":0, "95s":0, "94s":0, "93s":0, "92s":0,
        "A8u":1, "K8u":1, "Q8u":2, "J8u":0, "T8u":0, "98u":2, "88u":1, "87s":1, "86s":1, "85s":0, "84s":0, "83s":0, "82s":0,
        "A7u":1, "K7u":2, "Q7u":0, "J7u":0, "T7u":0, "97u":0, "87u":0, "77u":1, "76s":1, "75s":0, "74s":0, "73s":0, "72s":0,
        "A6u":1, "K6u":2, "Q6u":0, "J6u":0, "T6u":0, "96u":0, "86u":0, "76u":0, "66u":2, "65s":1, "64s":0, "63s":0, "62s":0,
        "A5u":1, "K5u":2, "Q5u":0, "J5u":0, "T5u":0, "95u":0, "85u":0, "75u":0, "65u":0, "55u":2, "54s":1, "53s":0, "52s":0,
        "A4u":1, "K4u":0, "Q4u":0, "J4u":0, "T4u":0, "94u":0, "84u":0, "74u":0, "64u":0, "54u":0, "44u":2, "43s":2, "42s":0,
        "A3u":1, "K3u":0, "Q3u":0, "J3u":0, "T3u":0, "93u":0, "83u":0, "73u":0, "63u":0, "53u":0, "43u":0, "33u":2, "32s":2,
        "A2u":1, "K2u":0, "Q2u":0, "J2u":0, "T2u":0, "92u":0, "82u":0, "72u":0, "62u":0, "52u":0, "42u":0, "32u":0, "22u":2
        }
    my_cards = round_state.hands[active]  # your cards
    parsed_hand = helpers.ParseHoleCards(my_cards)

    # --------------- strategy: --------------------
    if limp_chart[parsed_hand] == 1:
        return RaiseAction(random.randrange(6,8)) # raises to 6 or 7 chips with equal probability
    elif limp_chart[parsed_hand] == 0:
        return CheckAction()
    elif limp_chart[parsed_hand] == 2:
        if random.random()<0.5: return CheckAction()
        else: return RaiseAction(7)
    

def Defend3betStrategy(game_state, round_state, active):
    """
    Used when either they 3bet your raise or when they limp 3 bet.
    """
    small3bet_defense_chart = {
        "AAu":3, "AKs":3, "AQs":3, "AJs":3, "ATs":2, "A9s":1, "A8s":1, "A7s":1, "A6s":1, "A5s":1, "A4s":1, "A3s":1, "A2s":1,
        "AKu":3, "KKu":3, "KQs":3, "KJs":2, "KTs":1, "K9s":1, "K8s":1, "K7s":1, "K6s":1, "K5s":1, "K4s":1, "K3s":1, "K2s":1,
        "AQu":3, "KQu":2, "QQu":3, "QJs":2, "QTs":1, "Q9s":1, "Q8s":1, "Q7s":1, "Q6s":1, "Q5s":1, "Q4s":0, "Q3s":0, "Q2s":0,
        "AJu":2, "KJu":1, "QJu":1, "JJu":3, "JTs":1, "J9s":1, "J8s":1, "J7s":1, "J6s":0, "J5s":0, "J4s":0, "J3s":0, "J2s":0,
        "ATu":1, "KTu":1, "QTu":1, "JTu":1, "TTu":3, "T9s":1, "T8s":1, "T7s":1, "T6s":0, "T5s":0, "T4s":0, "T3s":0, "T2s":0,
        "A9u":1, "K9u":1, "Q9u":1, "J9u":1, "T9u":1, "99u":3, "98s":1, "97s":1, "96s":1, "95s":0, "94s":0, "93s":0, "92s":0,
        "A8u":1, "K8u":1, "Q8u":1, "J8u":0, "T8u":0, "98u":0, "88u":2, "87s":1, "86s":1, "85s":0, "84s":0, "83s":0, "82s":0,
        "A7u":1, "K7u":1, "Q7u":0, "J7u":0, "T7u":0, "97u":0, "87u":0, "77u":2, "76s":1, "75s":1, "74s":0, "73s":0, "72s":0,
        "A6u":1, "K6u":1, "Q6u":0, "J6u":0, "T6u":0, "96u":0, "86u":0, "76u":0, "66u":2, "65s":1, "64s":0, "63s":0, "62s":0,
        "A5u":1, "K5u":1, "Q5u":0, "J5u":0, "T5u":0, "95u":0, "85u":0, "75u":0, "65u":0, "55u":1, "54s":1, "53s":0, "52s":0,
        "A4u":1, "K4u":0, "Q4u":0, "J4u":0, "T4u":0, "94u":0, "84u":0, "74u":0, "64u":0, "54u":0, "44u":1, "43s":1, "42s":0,
        "A3u":1, "K3u":0, "Q3u":0, "J3u":0, "T3u":0, "93u":0, "83u":0, "73u":0, "63u":0, "53u":0, "43u":0, "33u":1, "32s":0,
        "A2u":1, "K2u":0, "Q2u":0, "J2u":0, "T2u":0, "92u":0, "82u":0, "72u":0, "62u":0, "52u":0, "42u":0, "32u":0, "22u":1
        }
    
    big3bet_defense_chart = {
        "AAu":3, "AKs":3, "AQs":3, "AJs":3, "ATs":2, "A9s":1, "A8s":1, "A7s":1, "A6s":1, "A5s":1, "A4s":1, "A3s":1, "A2s":1,
        "AKu":3, "KKu":3, "KQs":3, "KJs":2, "KTs":1, "K9s":1, "K8s":1, "K7s":1, "K6s":1, "K5s":1, "K4s":1, "K3s":1, "K2s":1,
        "AQu":3, "KQu":2, "QQu":3, "QJs":2, "QTs":1, "Q9s":1, "Q8s":1, "Q7s":1, "Q6s":1, "Q5s":1, "Q4s":0, "Q3s":0, "Q2s":0,
        "AJu":2, "KJu":1, "QJu":1, "JJu":3, "JTs":1, "J9s":1, "J8s":1, "J7s":1, "J6s":0, "J5s":0, "J4s":0, "J3s":0, "J2s":0,
        "ATu":1, "KTu":1, "QTu":1, "JTu":1, "TTu":3, "T9s":1, "T8s":1, "T7s":1, "T6s":0, "T5s":0, "T4s":0, "T3s":0, "T2s":0,
        "A9u":1, "K9u":1, "Q9u":1, "J9u":1, "T9u":1, "99u":3, "98s":1, "97s":1, "96s":1, "95s":0, "94s":0, "93s":0, "92s":0,
        "A8u":1, "K8u":1, "Q8u":1, "J8u":0, "T8u":0, "98u":0, "88u":3, "87s":1, "86s":1, "85s":0, "84s":0, "83s":0, "82s":0,
        "A7u":1, "K7u":1, "Q7u":0, "J7u":0, "T7u":0, "97u":0, "87u":0, "77u":2, "76s":1, "75s":1, "74s":0, "73s":0, "72s":0,
        "A6u":1, "K6u":1, "Q6u":0, "J6u":0, "T6u":0, "96u":0, "86u":0, "76u":0, "66u":2, "65s":1, "64s":0, "63s":0, "62s":0,
        "A5u":1, "K5u":1, "Q5u":0, "J5u":0, "T5u":0, "95u":0, "85u":0, "75u":0, "65u":0, "55u":1, "54s":1, "53s":0, "52s":0,
        "A4u":1, "K4u":0, "Q4u":0, "J4u":0, "T4u":0, "94u":0, "84u":0, "74u":0, "64u":0, "54u":0, "44u":1, "43s":1, "42s":0,
        "A3u":1, "K3u":0, "Q3u":0, "J3u":0, "T3u":0, "93u":0, "83u":0, "73u":0, "63u":0, "53u":0, "43u":0, "33u":1, "32s":0,
        "A2u":1, "K2u":0, "Q2u":0, "J2u":0, "T2u":0, "92u":0, "82u":0, "72u":0, "62u":0, "52u":0, "42u":0, "32u":0, "22u":1
        }

    my_cards = round_state.hands[active]  # your cards
    parsed_hand = helpers.ParseHoleCards(my_cards)

    legal_actions = round_state.legal_actions()  # the actions you are allowed to take
    my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
    opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
    if RaiseAction in legal_actions:
        min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
    
    # --------------- strategy: --------------------
    if opp_pip<=20:
        # this will be one set of ranges, all raise, call, fold
        if small3bet_defense_chart[parsed_hand] == 3:
            if random.random() < 0.05: return RaiseAction(max_raise)
            else: return RaiseAction(int(2.8*opp_pip))
        elif small3bet_defense_chart[parsed_hand] == 2:
            if random.random() < 0.2: return RaiseAction(int(2.9*opp_pip))
            else: return CallAction()
        elif small3bet_defense_chart[parsed_hand] == 1:
            return CallAction()
        elif small3bet_defense_chart[parsed_hand] == 0:
            return FoldAction()

    elif opp_pip<=30:
        if small3bet_defense_chart[parsed_hand] == 3:
            if RaiseAction in legal_actions and random.random() < 0.2: return RaiseAction(max_raise)
            else: return RaiseAction(int(3.1*opp_pip))
        if small3bet_defense_chart[parsed_hand] == 2:
            if RaiseAction in legal_actions and random.random() < 0.2: return RaiseAction(max_raise)
            else: return CallAction()
        elif small3bet_defense_chart[parsed_hand] == 1:
            return CallAction()
        elif small3bet_defense_chart[parsed_hand] == 0:
            return FoldAction()

    elif opp_pip < 40:
        if big3bet_defense_chart[parsed_hand] == 3:
            if RaiseAction in legal_actions: return RaiseAction(max_raise)
            else: return CallAction()
        elif big3bet_defense_chart[parsed_hand] == 2:
            if RaiseAction in legal_actions and random.random() < 0.15: return RaiseAction(max_raise)
            else: return CallAction()
        elif big3bet_defense_chart[parsed_hand] == 1:
            return FoldAction()
        elif big3bet_defense_chart[parsed_hand] == 0:
            return FoldAction()
    
    else:
        if big3bet_defense_chart[parsed_hand] == 3:
            if RaiseAction in legal_actions: return RaiseAction(max_raise)
            else: return CallAction()
        if big3bet_defense_chart[parsed_hand] == 2:
            if RaiseAction in legal_actions and random.random() < 0.1: return RaiseAction(max_raise)
            else: return CallAction()
        elif big3bet_defense_chart[parsed_hand] == 1:
            return FoldAction()
        elif big3bet_defense_chart[parsed_hand] == 0:
            return FoldAction()


        
    
