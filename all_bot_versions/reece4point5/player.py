'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import eval7
import random
import helpers
import preflop_strategy
import postflop_strategy

class Player(Bot):
    ''' 
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        self.hand_num = 0


    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        self.my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        self.round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        #my_cards = round_state.hands[active]  # your cards
        self.big_blind = bool(active)  # True if you are the big blind
        self.hand_num+=1
        self.preflop_bet = 1

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        #previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # int of street representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        pass


    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        # ---------------- provided values: -----------------------
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # int representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        # ---------------- end provided values: -----------------------


        hand = [eval7.Card(card) for card in my_cards+board_cards]
        made_hand = eval7.handtype(eval7.evaluate(hand))
        print(f'---------hand number {self.hand_num}------------')
        print(f'my hand:{my_cards}, board:{board_cards}')
        print(f'hand value:{eval7.handtype(eval7.evaluate(hand))}')
        print(f'board value:{helpers.EvalBoard(game_state, round_state, active)}')

        if my_pip < opp_pip:
            self.we_aggress = 0
            print(f'we_aggress:{self.we_aggress}')

        
        # ---------- pre-flop strategy ------------
        if street == 0: # if we are pre-flop
            if self.my_bankroll > (NUM_ROUNDS-self.hand_num+1)*1.5+2: # if win is secured, check fold
                if FoldAction in legal_actions: return FoldAction()
                else: return CheckAction()
            elif self.my_bankroll > -((NUM_ROUNDS-self.hand_num+1)*1.5+2) and self.my_bankroll < -((NUM_ROUNDS-self.hand_num+1)*1.5-8): # if they havent guarenteed win but are almost at threshold, we start shoving
                if RaiseAction in legal_actions: return RaiseAction(max_raise)
                else: return CallAction()
                        
            # elif self.my_bankroll < -((NUM_ROUNDS-self.hand_num+1)*1.5+2) and self.my_bankroll < -1000:
            #     if RaiseAction in legal_actions: return RaiseAction(max_raise)
            #     else: return CallAction()
            

            elif self.my_bankroll < -((NUM_ROUNDS-self.hand_num+1)*1.5+2) and (NUM_ROUNDS-self.hand_num+1)<30:
                if RaiseAction in legal_actions: return RaiseAction(max_raise)
                else: return CallAction()

            elif my_pip == 1: # in small blind, implement opening ranges
                action = preflop_strategy.OpeningStrategy(game_state, round_state, active)
            elif my_pip == 2 and opp_pip == 2: # they limped, implement limping attack strategy
                action = preflop_strategy.LimpStrategy(game_state, round_state, active)
            elif my_pip == 2 and opp_pip > 2: # they raised from the btn, implement defense strategy
                action = preflop_strategy.DefenseStrategy(game_state, round_state, active)
            elif my_pip > 2 and opp_pip > 2: # they 3 bet my raise or limp 3bet
                action = preflop_strategy.Defend3betStrategy(game_state, round_state, active) # this is really the nth bet defense now.
        

        # ----------- post-flop strategy ------------
        else:

            pot_size = 800 - my_stack - opp_stack

            if my_contribution == 400:
                return CheckAction()

            elif self.my_bankroll > (NUM_ROUNDS-self.hand_num+1)*1.5+2:
                if FoldAction in legal_actions: return FoldAction() # if win is secured, check fold
                else: return CheckAction()
            
            # elif self.my_bankroll > -((NUM_ROUNDS-self.hand_num+1)*1.5+2) and self.my_bankroll < -((NUM_ROUNDS-self.hand_num+1)*1.5-8): # if they havent guarenteed win but are almost at threshold, we start shoving
            #     if RaiseAction in legal_actions: return RaiseAction(max_raise)
            #     else: return CallAction()



            elif my_pip == 0 and opp_pip == 0: # if you start or they checked to you
                if active == 1: # means we start betting round
                    action = postflop_strategy.FirstToActStrategy(game_state, round_state, active, self.we_aggress)
                elif active == 0: # means we are on the btn, we have been checked to
                    action = postflop_strategy.CheckedToStrategy(game_state, round_state, active)
            
            elif my_pip == 0 and opp_pip > 0: # They bet first, meaning they start or I checked to them
                if active == 1: # I checked to them, they bet
                    action = postflop_strategy.ICheckedTheyBetStrategy(game_state, round_state, active)
                elif active == 0: # they bet into me
                    action = postflop_strategy.BetIntoStrategy(game_state, round_state, active)
            
            elif my_pip > 0 and opp_pip > 0: # I bet and they raised
                action = postflop_strategy.IBetTheyRaisedStrategy(game_state, round_state, active)

        print(f'thing:{type(action).__name__}')
        if street == 0:
            self.we_aggress = 0
        if type(action).__name__ == "RaiseAction":
            self.we_aggress = 1
        elif type(action).__name__ == "CallAction":
            self.we_aggress = 0
        
        # else:
        #     return action
        print(f'we_aggress:{self.we_aggress}')

        
        # elif type(action).__name__ == "CheckAction":
        #     self.we_agress = 0
        # action = FoldAction()
        # print(type(action).__name__)




        return action


if __name__ == '__main__':
    run_bot(Player(), parse_args())

