'''
Created on Nov 19, 2015

@author: chenji
'''
from bots.pseudo_bot import PseudoBot
from bots.exceptions import HeardsUpError
from bots.easy_bot import EasyBot
from engine.dealer import Dealer
from engine.player import Player
from engine.table import Table
from engine.hand import Hand

import deuces3x.deuces as deuces
import itertools
import timeit
import random
import api
import numpy as np

class Trainer(object):
    """

    Trainer objects trains the bot through let the bot play against itself and
    use regret minimization algorithm to adjust the mixed strategy to reach a
    Nash Equilibrium. 
    
    Acts as a dealer, redesigned game logic to fit heads up games.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA: 
    history               list; stores training history (on going)

    FUNCTIONS:
    train()               train the bot and adjust its strategy
    headsup_simulate()    simulate heads up game
    ====================  ====================================================
    """

    def __init__(self):
        '''
        Constructor
        '''
        self.history = []
        self._table = None
        self.evaluator = deuces.Evaluator()
      

    _ACTIONS = ["CALL", "CHECK", "FOLD", "RAISE", "BET"]
    _SAMPLE_ITER = 2
    _TRAIN_ITER = 1
    
    def train(self, player):
        # create new a new bot shares the same strategy
        player2 = Player(player.name + "COPY")
        player2.bot = EasyBot(player.bot.name + "_COPY")
        player2.bot.strategy = player.bot.strategy
        for _ in range(self._TRAIN_ITER):
            self.headsup_simulate(player, player2)
            
    def headsup_simulate(self, *players):
        if len(players) != 2:
            # should only be 2 player2 game
            raise HeardsUpError()
        self._prepare_table(*players)
        # get expected value for both players using current strategy
        evs = self._get_expected_values(players[0], players[1])
        
        for n in range(len(players)):
            player = players[n];
            for _iter in range(self._SAMPLE_ITER):
                for key, value in player.bot.strategy.items():
                    regrets = []
                    for i in range(len(value)):
                        # change the strategy
                        new_value = [0]*len(value)
                        new_value[i] = 1
                        player.bot.strategy[key] = tuple(new_value)
                        # compare the new ev and update the regrets
                        new_evs = self._get_expected_values(players[0], players[1])
                        regrets.append(new_evs[n]-evs[n])
                        player.bot.strategy[key] = value
                    # sum up regrets
                    player.bot.strategy.regrets[key] = tuple(np.add(player.bot.strategy.regrets[key], regrets))

            player.bot.strategy.refine();
    
    def _prepare_table(self, *players):
        """
        create new table and new hand, add players
        """
        self.evaluator = deuces.Evaluator()
        self._table = Table()
        self.hand = Hand()
        deck = deuces.Deck()
        self.board = deck.draw(5)
        self.board = [deuces.Card.new("Jd"),deuces.Card.new("Ah"),deuces.Card.new("Td"),deuces.Card.new("Ac"),deuces.Card.new("9d")]
        for player in players:
            player.join_table(self._table, Table.BUY_IN)
            player.activate()
            player.set_pocket(*deck.draw(2))
            player.set_evaluator(self.evaluator)
        players[0].set_pocket(deuces.Card.new("As"), deuces.Card.new("Th"))
        players[1].set_pocket(deuces.Card.new("Qd"), deuces.Card.new("Kd"))
        self.hand.players = self._table.players
        self._table.prep(self.hand)
                
             
    def _get_expected_values(self, player1, player2):
        """
        sample the game and get expected value for both players
        """
        evs = (0,0)
        for _iter in range(self._SAMPLE_ITER):
            self._play_game()
            evs = np.add(evs, self._refound(player1, player2))
        return [v/self._SAMPLE_ITER for v in evs]
    
    def _play_game(self):
        """
        """
        self._reset_game()
        self._run_preflop()     
        for street in self.hand.streets:
            self._reset_hand(street.name)
            self._reset_actions()
            self._run_betting()
        
    def _run_preflop(self):
        self._reset_hand("PRE_FLOP")
        # post blinds
        for player in self._table.players:
            player.bet(Table.BLINDS[1])
            player.FOLD = False
        self._reset_actions()
        self._run_betting()
        
    def _run_betting(self, display=False):
        i = 0
        while self._need_action():
            player = self._table.players[i]
            context = self.hand.get_profile()
            context["legal_actions"] = self._get_legal_action(player)
            action = player.bot.get_action(context)
            self._process_action(player, action)
            if display:
                print(action)
            i = 1 - i 
             
    def _refound(self, player1, player2):
        """
        return the refound for both players after game ends
        """
        effective_stack = min(player1.bet_amount, player2.bet_amount)
        if player1.FOLD:
            player1.ev = -effective_stack
        elif player2.FOLD:
            player1.ev = effective_stack
        else:
            for player in self._table.players:
                rank = self.evaluator.evaluate(player.pocket, self.hand.board) 
                player.rank = rank
            if player1.rank == player2.rank:
                player1.ev = 0
            elif player1.rank < player2.rank:
                player1.ev = effective_stack
            else:
                player1.ev = -effective_stack
        player2.ev = -player1.ev
        return (player1.ev, player2.ev)
        
    def _get_legal_action(self, player):
        legal_actions = dict()
        legal_actions["FOLD"] = api.LegalFold()
        cur_bet = self.hand.cur_bet
        if cur_bet:
            call = api.LegalCall()
            call["amount"] = min(cur_bet, player.stack)
            legal_actions["CALL"] = call
            raise_ = api.LegalRaise()
            raise_["min"] = cur_bet + max(cur_bet, Table.BLINDS[1])
            raise_["max"] = player.stack
            legal_actions["RAISE"] = raise_
            
        else:
            legal_actions["CHECK"] = api.LegalCheck()
            new_bet = api.LegalBet()
            new_bet["min"] = min(player.stack, Table.BLINDS[1])
            new_bet["max"] = player.stack
            legal_actions["BET"] = new_bet
        return legal_actions

    def _reset_game(self):
        for player in self._table.players:
            player.stack = Table.BUY_IN
            player.bet_amount = 0
        self.hand._flop.cards = []
        self.hand._turn.cards = []
        self.hand._river.cards = []
        self.hand.pot = 0
     
    def _reset_hand(self, street): 
        self.hand.street = street
        self.hand.cur_bet = 0
        if street is "PRE_FLOP":
            return
        elif street is "FLOP":
            self.hand._flop.cards.extend(self.board[0:3])
        elif street is "TURN":
            self.hand._turn.cards.extend(self.board[3:4])
        else:
            self.hand._river.cards.extend(self.board[4:5])
            
    def _reset_actions(self):
        for player in self._table.players:
            player.CALL = False
            player.CHECK = False
        
    def _need_action(self):
        """
        check if all call or fold except the last one who bet
        for 2 player game, anyone who fold or call will end the street
        """
        checked = True
        for player in self._table.players:
            if player.CALL | player.FOLD:
                return False
            checked &= player.CHECK
        return not checked  
    
    def _process_action(self, player, action):
        setattr(player, action["type"], True)
        if action["amount"]:
            player.bet(action["amount"])
            self.hand.cur_bet = action["amount"]
        elif action["type"] == "CHECK":
            player.bet(0)
            self.hand.cur_bet = 0
        elif action["type"] == "FOLD":
            player.fold()
            self.hand.cur_bet = -1
        