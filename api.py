#(c) Blackbird Logical Applications, LLC 2015
# bird_em.api
"""
Module defines the communication protocol between bots and the engine. Protocol
generally follows the MIT PokerBots 3.0 spec, but uses dictionaries instead of
sockets to simplify parsing. 
"""




#imports
#n/a




#constants
#n/a

#classes
class HandProfile(dict):
    """

    Dictionary that describes the current hand.
    ====================  =====================================================
    Key                   Value
    ====================  =====================================================
    pot                   int; amount of chips in the pot
    board                 list; 0 to 5 two-character card strings
    history               list; performed actions, from oldest to newest
    legal_actions         dict; keys are types, values are LegalAction dicts
    players               list; PlayerProfile dicts for each player at table
    ====================  =====================================================
    """
    def __init__(self):
        self["legal_actions"] = dict()
        self["history"] = []
        self["board"] = []
        self["players"] = []

class PlayerProfile(dict):
    """

    Dictionary that describes a player at the table.
    ====================  =====================================================
    Key                   Value
    ====================  =====================================================
    active                bool; is the player participating in the hand
    name                  string; player name, will stay constant across time
    stack                 int; player stack size
    ====================  =====================================================
    """
    def __init__(self):
        self["active"] = False
        self["name"] = None
        self["stack"] = None

#************************************************
#                1.LEGAL ACTIONS                *
#************************************************

class LegalAction(dict):
    """

    Dictionary that describes an action that a player can take

    Keys in [brackets] are optional.
    ====================  =====================================================
    Key                   Value
    ====================  =====================================================
    type                  string; "FOLD", "CALL", "CHECK", "BET", or "RAISE"
    
    amount                int or None; specified for "CALL"

    [min]                 int; on BET or RAISE, lowest permitted amount

    [max]                 int; on BET or RAISE, highest permitted amount
    ====================  =====================================================
    """
    def __init__(self):
        self["type"] = None
        self["amount"] = None
        
class LegalBet(LegalAction):
    """
    Player must specify a bet such that min <= bet <= max. Max bet is the
    player's stack.
    """
    def __init__(self, min_amount=0 , max_amount=0):
        LegalAction.__init__(self)
        self["type"] = "BET"
        self["min"] = min_amount
        self["max"] = max_amount

class LegalCheck(LegalAction):
    def __init__(self):
        LegalAction.__init__(self)
        self["type"] = "CHECK"

class LegalCall(LegalAction):
    def __init__(self, amount = 0):
        LegalAction.__init__(self)
        self["type"] = "CALL"
        self["amount"] = amount

class LegalFold(LegalAction):
    def __init__(self):
        LegalAction.__init__(self)
        self["type"] = "FOLD"

class LegalRaise(LegalAction):
    """

    Raise TO an amount, such that min <= amount max. Min is the lower of the
    player's stack or 2x the prior bet.
    """
    def __init__(self, min_amount = 0, max_amount = 0):
        self["type"] = "RAISE"
        self["min"] = min_amount
        self["max"] = max_amount

#************************************************
#             2.PERFORMED ACTIONS               *
#************************************************

class PerformedAction(LegalAction):
    """

    Supplements LegalAction with additional information, permits each of the
    types in PokerBot API.

    Dictionary that describes an action that a player can take

    Keys in [brackets] are optional. 
    ====================  =====================================================
    Key                   Value
    ====================  =====================================================
    type                  string; "FOLD", "CALL", "CHECK", "BET", "RAISE",
                          "POST", "DEAL", "REFUND", "SHOW", "TIE", or "WIN"

    amount                int or None; specified for "CALL"

    actor                 string or None; player name, None for dealer
    
    [street]              string; for DEAL, either "FLOP", "TURN", or
                          "RIVER"

    [card1]               string; for SHOW, pocket card #1
    
    [card2]               string; for SHOW, pocket card #2
    ====================  =====================================================
    """
    def __init__(self):
        LegalAction.__init__(self)
        self["actor"] = None


             
