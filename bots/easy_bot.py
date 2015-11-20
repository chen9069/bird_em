'''
Created on Nov 18, 2015

@author: chenji
'''
from api import LegalFold, LegalCheck

from bots.bot import Bot
from bots.strategy import Strategy
import deuces3x.deuces as deuces

import itertools
import timeit
import random

class EasyBot(Bot):
    """

    An Bot object gives action for different context of poker game
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================
    DATA:    
    strategy              dict; stores strategy for different information sets

    FUNCTIONS:
    get_action()          prints hand info, gets a human to type in the action
    set_pocket()          stores cards on instance
    set_evaluator()       provides bot with evaluator 
    ====================  ====================================================
    """
    # QuadsZilla 's Color-Coded Hand vs. Random Hand Table 
    # from http://seoblackhat.com/texas-hold-em-poker-statistics/
    _HAND_RANK_TABLE = [
                       [0.852,0.670,0.662,0.654,0.646,0.628,0.619,0.610,0.599,0.599,0.595,0.582,0.574],
                       [0.653,0.824,0.634,0.626,0.618,0.600,0.583,0.575,0.566,0.558,0.549,0.541,0.532],
                       [0.644,0.614,0.799,0.602,0.595,0.577,0.560,0.543,0.536,0.528,0.519,0.510,0.502],
                       [0.636,0.606,0.581,0.775,0.575,0.557,0.540,0.523,0.506,0.500,0.491,0.482,0.474],
                       [0.627,0.597,0.572,0.552,0.750,0.540,0.523,0.506,0.489,0.472,0.465,0.457,0.448],
                       [0.608,0.578,0.554,0.532,0.515,0.720,0.508,0.491,0.474,0.457,0.439,0.433,0.424],
                       [0.599,0.560,0.536,0.515,0.497,0.481,0.692,0.479,0.432,0.445,0.427,0.409,0.403],
                       [0.588,0.552,0.518,0.497,0.479,0.433,0.450,0.662,0.454,0.437,0.418,0.400,0.382],
                       [0.577,0.542,0.510,0.478,0.431,0.445,0.432,0.423,0.633,0.431,0.413,0.395,0.377],
                       [0.577,0.533,0.501,0.472,0.442,0.427,0.414,0.405,0.399,0.603,0.414,0.397,0.378],
                       [0.567,0.523,0.491,0.462,0.435,0.407,0.394,0.385,0.380,0.382,0.567,0.386,0.368],
                       [0.558,0.514,0.482,0.453,0.426,0.400,0.375,0.366,0.361,0.363,0.351,0.537,0.360],
                       [0.549,0.505,0.473,0.443,0.417,0.391,0.368,0.346,0.341,0.343,0.332,0.323,0.503],
                       ]
    _BET_AMOUNTS = [10, 20, 50]
    _PRE_FLOP_MAX_BET = 10

    def __init__(self, name, trainer=None):
        '''
        Constructor
        '''
        Bot.__init__(self, name)
        self.trainer = trainer
        self._strategy = Strategy()
        self._ranks = dict()
           
    @property        
    def strategy(self):
        return self._strategy
    
    @strategy.setter
    def strategy(self, value):
        self._strategy = value
        
        
    #############################################  
    ###                ACTIONS                ###
    #############################################   
    
    def _call(self, context):
        return context["legal_actions"]["CALL"]
    def _check(self, context):
        return LegalCheck()
    def _raise(self, amount, context):
        if amount < context["legal_actions"]["RAISE"]["min"]:
            return context["legal_actions"]["CALL"]
        else:
            action =  context["legal_actions"]["RAISE"].copy()
            action["amount"] = amount
            return action
    def _bet(self, amount, context):
        if amount < context["legal_actions"]["BET"]["min"]:
            return LegalCheck()
        else:
            action =  context["legal_actions"]["BET"].copy()
            action["amount"] = amount
            return action
    
    #############################################  
    ###               FUNCTIONS               ###
    ############################################# 
    
    def get_action(self, context):
        """

        EasyBot.get_action() -> Action

        Decide what to do based on context.
        """
        
        cur_street = context["street"]
        # get current hand rank and store in self._ranks
        if cur_street not in self._ranks:
            self._ranks[context["street"]] = self._get_hand_rank(context)
        # Deal pre-flop street separately
        if cur_street is "PRE_FLOP":
            action = self._pre_flop_action(context)
        else:
            if context["cur_bet"]:
                # bet is on the table; fold, call or raise
                if self._should_fold(context):
                    action = LegalFold()
                else:
                    # 0:call; 1 to n:raise low to high
                    i = self._get_strategy(context)
                    if i == 0:
                        action = context["legal_actions"]["CALL"]
                    else:
                        raise_amount = self._BET_AMOUNTS[i-1] + context["legal_actions"]["CALL"]["amount"]
                        amount = min(raise_amount, context["legal_actions"]["RAISE"]["max"])
                        action = self._raise(amount, context)
            else:
                if self._ranks[cur_street] < 0.5:
                    action = LegalCheck()
                else:
                    i = self._get_strategy(context)
                    if i == 0:
                        action = context["legal_actions"]["CHECK"]
                    else:
                        bet_amount = self._BET_AMOUNTS[i-1]
                        amount = max(context["legal_actions"]["BET"]["min"], min(bet_amount, context["legal_actions"]["BET"]["max"]))
                        action = self._bet(amount, context)
            if self.trainer:
                # currently training
                pass
        print (self.name, action)
        return action
                
    
    def _pre_flop_action(self, context):
        """
        make pre_flop actions, would only bet or raise amount less than _PRE_FLOP_MAX_BET
        """
        if context["cur_bet"]:
            if self._should_fold(context):
                return LegalFold()
            else:
                max_bet = int((self._ranks["PRE_FLOP"] - 0.4) * 2 * self._PRE_FLOP_MAX_BET)
                amount = min(max_bet, context["legal_actions"]["RAISE"]["max"])
                return self._raise(amount, context)
        else:
            max_bet = int((self._ranks["PRE_FLOP"] - 0.4) * 2 * self._PRE_FLOP_MAX_BET)
            amount = min(max_bet, context["legal_actions"]["BET"]["max"])
            return self._bet(amount, context)
                 
    def _get_strategy(self, context):
        """
        read actions from strategy and randomly choose one
        """
        info = self._get_Info(context)
        strategy = self.strategy.get_strategy(info)
        #print(strategy)
        p = random.random()
        for i in range(len(strategy)):
            p -= strategy[i]
            if (p < 0):
                break;
        return i
    
    def _should_fold(self, context):
        """
        return true if expected value of fold is higher than call based on current hand rank
        """
        call_amount = context["legal_actions"]["CALL"]["amount"]
        for player in context["players"]:
            if player["name"] == self.name:
                bet_amount = player["bet_amount"]
                break;
        hand_rank = self._ranks[context["street"]] 
        ev_fold = -bet_amount
        ev_call = (hand_rank - (1 - hand_rank)) * (bet_amount + call_amount)
        return ev_call < ev_fold
    
    
    def _get_Info(self, context):
        """
        generate info -> (hand_rank, street, pot_size, cur_bet)
        """
        info = dict()
        info["hand_rank"] = self._ranks[context["street"]]
        info["street"] = context["street"]
        info["pot_size"] = context["pot"]
        info["cur_bet"] = context["cur_bet"]
        return info
    
    def _get_hand_rank(self, context):
        """
        return a percentage presentation of current hand rank
        sample the rest cards that is not shown, calculate the possibility of win 
        """
        street = context["street"]
        if street is "PRE_FLOP":
            # read hand rank from QuadsZilla's hand rank table
            rank_chars = [v[0] for v in self.pocket]
            suit_chars = [v[1] for v in self.pocket]
            rank_ints = sorted([deuces.Card.CHAR_RANK_TO_INT_RANK[v] for v in rank_chars], reverse=True)
            suit_ints = [deuces.Card.CHAR_SUIT_TO_INT_SUIT[v] for v in suit_chars]
            return self._HAND_RANK_TABLE[12-rank_ints[0]][12-rank_ints[1]] if suit_ints[0] == suit_ints[1] else self._HAND_RANK_TABLE[12-rank_ints[1]][12-rank_ints[0]]
        else:
            board = [deuces.Card.new(v) for v in context["board"]]
            hand = [deuces.Card.new(v) for v in self.pocket]
            # unused cards in the standard 52 card deck
            unused_cards = [v for v in deuces.Deck.GetFullDeck() if v not in board + hand]
            win,tie,lose,_sum = 0,0,0,0
            #start = timeit.default_timer()
            for combo in itertools.combinations(unused_cards, 5-len(board)):
                new_board = board.copy()
                new_board.extend(combo)
                # hand rank in current board
                rank = self.evaluator.evaluate(hand, new_board)
                for opponent_cards in itertools.combinations([v for v in unused_cards if v not in combo], 2):
                    # too much combinations in PRE_FLOP, use 10 percent samples for calculation
                    if street is "FLOP" and random.random() > 0.1:
                        continue
                    opponent_rank = self.evaluator.evaluate(list(opponent_cards), new_board)
                    if rank < opponent_rank:
                        win += 1
                    elif rank > opponent_rank:
                        lose += 1
                    else:
                        tie += 1
                    _sum += 1
                    
            #stop = timeit.default_timer()
            #print ("time:", stop - start )
            return (win+tie/2)/_sum


    def set_pocket(self, card1, card2):
        """

        Bot.set_pocket(cards) -> None

        Dealer provides bots with cards
        """
        self.pocket = [card1, card2]
        
    def set_evaluator(self, evaluator):
        
        """

        Bot.set_evaluator(evaluator) -> None

        Dealer provides bots with evaluator
        """
        self.evaluator = evaluator