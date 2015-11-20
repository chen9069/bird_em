#(c) Blackbird Logical Applications, LLC 2015
"""
Module defines a Bot class. The Bot class defines a generic shell with the
public interface the engine expects to see. 
"""




#imports
from api import LegalFold




#constants
#n/a

#classes
class Bot:
    """

    A Bot object provides the standard communication interface for the engine
    but does no thinking of its own. You can subclass it to implement your own
    logic.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA: 
    name                  string; identifies your bot

    FUNCTIONS:
    get_action()          send an action to the engine for the hand
    get_memory()          send a memory dictionary to the engine
    set_memory()          receive a memory dictionary from the engine
    set_pocket()          receive your cards from the engine
    ====================  ====================================================
    """
    def __init__(self, name=None):
        self.name = name
        
    def get_action(self, context):
        """

        Bot.get_action() -> Action

        Decide what to do based on context. Engine will call this method when
        it's your turn to play.
        """
        action = LegalFold()
        #check by default, insert decision logic here
        #
        return action
    
    def set_pocket(self, card1, card2):
        """

        Bot.set_pocket(cards) -> None

        Dealer provides bot with cards
        """
        #insert storage and analysis logic
        #
        return None

    def get_memory(self):
        """

        Bot.get_memory() -> dict()

        Deliver state that you want to preserve between run times. Return a
        dictionary. Keys and values must be strings without newline characters.
        Maximum memory size is 10kb. Engine will discard nonconforming memory.
        """
        # Many bots will not use this feature.
        notes = {"matt_damon" : "always leaves outs"}
        return notes

    def set_memory(self, notes):
        """

        Bot.set_notes(notes) -> None
        
        Receive your state from the engine.
        """
        pass


