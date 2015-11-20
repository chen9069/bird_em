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
from engine.dealer import Dealer
from engine.player import Player




#constants
#n/a

#functions
#n/a

#
valerie = Dealer()
print("valerie will be our dealer.")

matt_damon = Player("Matt")
ed_norton = Player("Ed")

matt_damon.bot = PseudoBot("MattBot")
ed_norton.bot = PseudoBot("EdBot")

valerie.start_game(matt_damon, ed_norton)
c = "To play a hand, run ``valerie.play_hand()``\n"
print(c)




