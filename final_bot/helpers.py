# from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
# from skeleton.states import GameState, TerminalState, RoundState
# from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
# from skeleton.bot import Bot
# from skeleton.runner import parse_args, run_bot

import eval7

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


def FlushDrawCheck(cards):
    suits = SuitsCheck(cards)
    ans = {i:0 for i in range(6)}
    for suit in suits:
        if suits[suit] in ans:
            ans[suits[suit]] += 1
        else:
            ans[suits[suit]] = 1
    return ans


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
        for rank in possibilities[i:i+5]:
            count += stuff[rank]
        ans[count] += 1
    return ans


# ans1=StraightsCheck(['Qd', 'Ks', '9s'])
# ans2=StraightsCheck(['Ac', 'Th', 'Qd', 'Ks', '9s'])
# import pdb; pdb.set_trace()


def PairChecker(my_cards, board_cards):
    """
    checks what pairs you have and returns their ranks.
    For example, if you have a single top pair, this will return [1].
    """
    answers = []
    ranks = '23456789TJQKA'
    found = set()
    non_pairs = []
    pairs = []

    board_found = set()
    cleansed_board_cards = []
    for card in board_cards:
        if card[0] not in board_found:
            board_found.add(card[0])
            cleansed_board_cards.append(card[0])

    cards = my_cards+cleansed_board_cards
    for card in cards:
        if card[0] in found:
            # pair found
            pairs.append(card[0]) 
        else:
            found.add(card[0])
    for pair in pairs:
        ans = 1
        non_pairs = []
        for card in board_cards:
            if card[0] != pair and card[0] not in non_pairs:
                non_pairs.append(card[0])
        for card in non_pairs:
            if ranks.index(card) > ranks.index(pair):
                ans += 1
        answers.append(ans)
    return answers

ans = PairChecker(['7c', '3c'], ['Ad', 'Ac', 'Kd', 'Kd', '7s'])
print(ans)

# ans = PairChecker(['Qc', '3c'], ['Ad', 'Qc', 'Kd', '7d', '7s'])
# print(ans)


def TwoPairValueChecker(my_cards, board_cards):
    """
    this function is to be used only when we have two pair when there is at least 1 pair on the board.

    ['Ac', '8c'], ['As', '2c', '2d', '3d', '3s']
    board_pairs_final:[2], all_pairs_final:[14]

    ['2c', '8c'], ['As', 'Ac', '2d', '3d', '3s']
    board_pairs_final:[], all_pairs_final:[]

    ['2c', '8c'], ['As', 'Ac', '2d', '3d', '7s']
    board_pairs_final:[], all_pairs_final:[2]

    ['Ac', '8c'], ['As', '8c', '2d', '3d', '3s']
    board_pairs_final:[3], all_pairs_final:[14, 8]

    one overpair to the double pair: if all_pairs_final[0]>board_pairs_final[0]

    we provide pair but it doesnt play: both are []

    We provide a pair to single paired board: board_pairs_final:[], all_pairs_final:[value of provided pair]

    two overpairs to single paired board:

    heuristic to use:
    max in all is bigger than max in board
    """
    mapping = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A': 14}
    mine = [mapping[card[0]] for card in my_cards]
    board = [mapping[card[0]] for card in board_cards]
    not_pairs = []
    board_pairs = []
    for rank in board:
        if rank not in not_pairs:
            not_pairs.append(rank)
        else:
            board_pairs.append(rank)
    all_not_pairs = []
    all_pairs = []
    for rank in board+mine:
        if rank not in all_not_pairs:
            all_not_pairs.append(rank)
        else:
            all_pairs.append(rank)
    while len(board_pairs) > 2:
        board_pairs.remove(min(board_pairs))
    while len(all_pairs) > 2:
        all_pairs.remove(min(all_pairs))
    board_pairs_final = [card for card in board_pairs]
    all_pairs_final = [card for card in all_pairs]
    for card in all_pairs:
        if card in board_pairs:
            board_pairs_final.remove(card)
            all_pairs_final.remove(card)
    # import pdb; pdb.set_trace()
    # we want to normalize all_pairs_final
    # we return answers, which returns numbers corresponding to pairs that we provide. If we dont help, it is []. If we provide top pair, it has a 1.
    answers = []
    for pair in all_pairs_final:
        ans = 1
        non_pairs = []
        for card in board_cards:
            if card[0] != pair and mapping[card[0]] not in non_pairs:
                non_pairs.append(mapping[card[0]])
        print(non_pairs)
        for card in non_pairs:
            if card > pair:
                ans += 1
        answers.append(ans)
    # import pdb; pdb.set_trace()
    return answers


ans = TwoPairValueChecker(['7c', '3c'], ['Ad', 'Ac', 'Kd', 'Kd', '7s'])
print(ans)

# ans = TwoPairValueChecker(['Ac', '8c'], ['As', '2c', '2d', '3d', '3s'])
# print("['Ac', '8c'], ['As', '2c', '2d', '3d', '3s']")
# print(ans)
# ans = TwoPairValueChecker(['2c', '8c'], ['As', 'Ac', '2d', '3d', '3s'])
# print("['2c', '8c'], ['As', 'Ac', '2d', '3d', '3s']")
# print(ans)
# ans = TwoPairValueChecker(['2c', '8c'], ['As', 'Ac', '2d', '3d', '7s'])
# print("['2c', '8c'], ['As', 'Ac', '2d', '3d', '7s']")
# print(ans)
# ans = TwoPairValueChecker(['Ac', '8c'], ['As', '8c', '2d', '3d', '3s'])
# print("['Ac', '8c'], ['As', '8c', '2d', '3d', '3s']")
# print(ans)

# ans = TwoPairValueChecker(['2d', '2c'], ['As', '8c', '4d', '3d', '3s'])
# print("['2d', '2c'], ['As', '8c', '4d', '3d', '3s']")
# print(ans)



def MyFlushRank(my_cards, board_cards):
    """
    When you have a flush, sees if you contribute to a flush and what contribution you have.
    For example, it will rank all the suits on the board and you hand and use that to determine the ranks.
    (will need to accomodate multiple flush possibilities.)
    nut flush would return [1], unhelpful would return [6+].
    only returns cards if they play.
    Example: 
    >> MyFlushRank(['9c', '7s'], ['2h', 'Tc', 'Jc', 'Qd', '5s', 'Qc', 'Kc', 'Ac'])
    returns []
    >> MyFlushRank(['8c', '7s'], ['2h', 'Tc', 'Jc', 'Qd', '5s', 'Qc', 'Kc', '2c'])
    returns [3]
    >> MyFlushRank(['8c', '7c'], ['2h', 'Tc', 'Jc', 'Qd', '5s', 'Qc', 'Kc', '2c'])
    returns [3, 4]

    THIS FUNCTION SHOULD BE USED TO FIND THE MAX AKA IF 1 IS IN THE ANS, WE HAVE NUT FLUSH.
    DONT READ INTO THE OTHER NUMBERS THAT MUCH.
    """
    full_ranks = 'AKQJT98765432'
    ans = []
    hand_suits = SuitsCheck(my_cards+board_cards)
    for suit in hand_suits:
        ranks = 'AKQJT98765432'
        if hand_suits[suit] >= 5: # made flush
            suit_ans = []
            board_this_suit = []
            mine_this_suit = []
            
            for card in board_cards:
                if card[1] == suit:
                    ranks = ranks.replace(card[0], '')
                    board_this_suit.append(card[0])

            for card in my_cards:
                if card[1] == suit:
                    mine_this_suit.append(card[0])
            hand_plays = False
            for card in mine_this_suit: # this for loop checks for if my top flush plays
                if full_ranks.index(card) < ranks.index(card) + 5:
                    hand_plays = True

            if hand_plays:
                for card in mine_this_suit:
                    suit_ans.append(ranks.index(card)+1)
                ans += suit_ans
    return ans

            
# tests:
# ans1 = MyFlushRank(['6c', '7s'], ['2h', '2c', '9c', 'Qd', '5s', '3c', '7c', 'Ac'])
# ans2 = MyFlushRank(['9c', '7s'], ['2h', 'Tc', 'Jc', 'Qd', '5s', 'Qc', 'Kc', 'Ac'])
# ans3 = MyFlushRank(['Tc', '7s'], ['2h', '9c', 'Jc', 'Qd', '5s', 'Qc', 'Kc', 'Ac'])
# ans4 = MyFlushRank(['8c', '7s'], ['2h', 'Tc', 'Jc', 'Qd', '5s', 'Qc', 'Kc', '2c'])
  
