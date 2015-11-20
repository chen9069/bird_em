# (c)Blackbird Logical Applications, LLC 2015
#
# Engine relies on a Python 3x version of the Will Drevo's deuces card evaluator
# (see https://github.com/worldveil/deuces) and uses a simplified version of the
# MIT PokerBots 3.0 communication protocol.
"""
Module loads two PseudoBot players and starts a game.
"""




#imports
from bots.pseudo_bot import PseudoBot
from bots.easy_bot import EasyBot
from bots.trainer import Trainer
from engine.dealer import Dealer
from engine.player import Player
    
#constants
#n/a

#functions
#n/a

#
valerie = Dealer()
#print("valerie will be our dealer.")

matt_damon = Player("Matt")
ed_norton = Player("Ed")
trainer = Trainer()

matt_damon.bot = EasyBot("MattBot")
ed_norton.bot = PseudoBot("EdBot")

# each iteration took about 1 min, default is 100 iters
# trainer = Trainer()
# trainer.train(matt_damon)

valerie.start_game(matt_damon, ed_norton)
#c = "To play a hand, run ``valerie.play_hand()``\n"
valerie.play_hand();