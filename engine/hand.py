# (c) Blackbird Logical Applications, LLC 2015
# bird_em.hand
"""
Defines Hand class.
"""




#imports
import copy

from api import HandProfile
from deuces3x.deuces import Card

from .street import Street




#constants
#n/a


#classes
class Hand:
    """

    Container for play-time attributes: streets, pot, history, etc. Players
    that start the hand stay in the hand, even if they fold and become
    inactive.
    ====================  =====================================================
    ATTRIBUTE             VALUE
    ====================  =====================================================

    DATA:
    board                 list; property returns concatenated streets
    history               list; all prior performed actions
    players               list; players that started the hand (includes folded)
    pot                   int; chip count on the table
    streets               list; Street instances for flop, turn, and river
 
    FUNCTIONS:
    get_profile()         returns filled out HandProfile (w/o legal actions)
    ====================  =====================================================
    """
    def __init__(self):
        self._flop = Street("FLOP", count=3)
        self._turn = Street("TURN", count=1)
        self._river = Street("RIVER", count=1)
        self.streets = [self._flop, self._turn, self._river]
        #
        self.pot = 0
        self.history = []
        self.players = []

    @property
    def board(self):
        """

        ***property***

        Return a list of cards currently on the board.
        """
        cards = []
        for street in self.streets:
            cards.extend(street.cards)
        return cards

    def get_profile(self):
        """

        Hand.get_profile() -> HandProfile

        Return a profile with ``board``, ``players``, and ``history`` keys
        filled out. 
        """
        form = HandProfile()
        form["board"] = [Card.int_to_pretty_str(card) for card in self.board]
        form["players"] = [player.get_profile() for player in self.players]
        form["history"] = copy.deepcopy(self.history)
        form["pot"] = self.pot
        #
        return form
   
