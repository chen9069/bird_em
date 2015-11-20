# (c) Blackbird Logical Applications, LLC 2015
# bird_em.player
"""
Module defines Player class, which provides a stateful wrapper for bots.
"""




#imports

from api import PlayerProfile
from deuces3x.deuces import Card




#constants
#n/a

#classes
class Player:
    """

    The Player class provides a stateful bot wrapper. Player instances also
    interface directly with a given hand for stack / pot accounting.
    ====================  =====================================================
    ATTRIBUTE             VALUE
    ====================  =====================================================

    DATA:
    active                bool; property, whether player is in hand
    bot                   obj; pointer to underlying bot
    hand                  obj; pointer to the hand that's on the table
    name                  str; name of bot, or of instance if no bot
    pocket                list; strings that represent pocket cards
    stack                 int; chip count
    table                 obj; pointer to table
 
    FUNCTIONS:
    get_action()          delegates to bot, supposed to return legal action
    get_profile()         returns filled out PlayerProfile for instance
    
    activate()            set instance.active to True
    deactivate()          set instance.active to False
    join_table()          add instance to table
    set_pocket()          add pocket cards

    bet()                 take chips from stack and put them in the pot
    credit()              take chips from pot and put them into stack
    fold()                clear pocket cards    
    ====================  =====================================================
    """
    
    def __init__(self, name, bot=None):
        self._active = True
        self._name = name

        self.bot = None
        self.pocket = []
        self.stack = None
        self.table = None

    def __str__(self):
        return self.name

    def get_action(self, hand_info):
        """

        Player.get_action() -> LegalAction
        
        Returns a completed LegalAction from bot.
        """
        return self.bot.get_action(hand_info)

    def get_profile(self):
        """

        Player.get_profile() -> PlayerProfile
        
        Return completed PlayerProfile for instance
        """
        form = PlayerProfile()
        for key in form:
            form[key] = getattr(self, key)
        return form

    #************************************************
    #                   PROPERTIES                  *
    #************************************************
    
    @property
    def active(self):
        """

        **read-only property**

        Returns _active. Toggle via (de)activate methods. 
        """
        return self._active

    @property
    def hand(self):
        """

        **read-only property**

        Returns the hand that's on the table.
        """
        return self.table.hand

    @property
    def name(self):
        """

        **property**

        Return bot name, if bot is specified, otherwise _name. Setter takes
        new values only if the instance is not connected to a bot.
        """
        name = self._name
        if self.bot:
            name = self.bot.name
        return name

    @name.setter
    def name(self, value):
        if not self.bot:
            self._name = value
        else:
            c = "Cannot set name. Player inherits name from bot."
            raise ManagedAttributeError(c)

    #************************************************
    #                 CONFIGURATION                 *
    #************************************************
    
    def activate(self):
        """

        Player.activate() -> None

        Sets ``active`` to True.
        """
        self._active = True
        
    def deactivate(self):
        """

        Player.deactivate() -> None

        Sets ``active`` to False.
        """
        self._active = False

    def join_table(self, table, stack):
        """

        Player.join_table() -> None

        Sets instance poiner to table, joins that table (so the instance
        appears on table.players), and sets the instance stack. 
        """
        table.join(self)
        self.table = table
        self.stack = stack

    def set_pocket(self, card1_int, card2_int):
        """

        Player.set_pocket() -> None
        
        Stores integers on instance, passes down matching strings to bot.
        """
        self.pocket = [card1_int, card2_int]
        
        card1_string = Card.int_to_pretty_str(card1_int)
        card2_string = Card.int_to_pretty_str(card2_int)

        self.bot.set_pocket(card1_string, card2_string)

    #************************************************
    #             MANAGING STACK & POT              *
    #************************************************

    def bet(self, amount):
        """

        Player.bet() -> None
        
        Take chips out of stack, put them in the pot.

        General interface for POST, BET, and RAISE. Will raise
        OutOfMoneyError if the player doesn't have enough money to perform the
        action. 
        """
        if amount <= self.stack:
            self.stack -= amount
            self.hand.pot += amount
        else:
            c = "Player does not have enough money to make the bet."
            raise OutOfMoneyError(c)

    def credit(self, amount):
        """

        Player.credit() -> None

        Take chips out of the pot, put them in the player's stack. Will raise
        StructureError if the pot doesn't have enough chips to perform the
        action.
        """
        self.stack += amount
        if amount <= self.hand.pot:
            self.hand.pot -= amount
        else:
            c = "Not enough money in the pot to cover the credit."
            raise StructureError(c)
        
    def fold(self):
        """

        Player.fold() -> None

        Clears pocket, deactivates instance.
        """
        self.pocket.clear()
        self.deactivate()
        
 

    
    

        




    
