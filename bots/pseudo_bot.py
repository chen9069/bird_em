#(c) Blackbird Logical Applications, LLC 2015
"""
Module defines a PseudoBot, kind of like a bot but not. A pseudobot gets hand
information from the engine and then asks a person to make all of the
decisions (ie, respond with an action).

Useful for playing against your real bot with the correct interface.
"""




#imports
from textwrap import TextWrapper

from api import LegalFold

from .bot import Bot




#constants
#n/a

#classes
class PseudoBot(Bot):
    """

    The bot that lets YOU do all the hard work! Useful for playing against your
    machine opponents. PseudoBot will prompt you to input an action every time
    the dealer asks it to do something.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA: 
    DEFAULT_WIDTH         int; line width for printing hand info 
    MAX_ATTEMPTS          int; retries before sending back a bad entry
    human                 bool; controls whether engine will apply timing

    FUNCTIONS:
    get_action()          prints hand info, gets a human to type in the action
    set_pocket()          stores cards on instance
    ====================  ====================================================
    """
    _ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    _NUM_FIELD = 5
    DEFAULT_WIDTH = 60
    MAX_ATTEMPTS = 5

    paragraph = TextWrapper(width=DEFAULT_WIDTH)
    sub_paragraph = TextWrapper(width=DEFAULT_WIDTH,
                                initial_indent=(_NUM_FIELD * " "),
                                subsequent_indent=(_NUM_FIELD * " "))

    def __init__(self, name=None):
        Bot.__init__(self, name)
        self.human = True
    
    def get_action(self, context):
        """

        PseudoBot.get_action() -> Action

        Decide what to do based on context. Engine will call this method when
        it's your turn to play.
        """
        line = "-" * self.DEFAULT_WIDTH
        identifier = "<%s>" % self.name
        identifier = identifier.center(self.DEFAULT_WIDTH)

        print()
        print(line)
        print(identifier)
        print(line)
        print()
        print("Players: \n")
        for player in context["players"]:
            print(self.sub_paragraph.fill(str(player)))
        print()
        print("Board:   \n\n", context["board"])
        print()
        print("History: \n")
        for number, performed_action in enumerate(context["history"]):
            num_field = str(number).ljust(self._NUM_FIELD)
            self.sub_paragraph.initial_indent = num_field
            print(self.sub_paragraph.fill(str(performed_action)))
        else:
            self.sub_paragraph.initial_indent = self._NUM_FIELD * " "
            # Reset sub_paragraph so we can use it again later.  
        print()
        print("Pot:     \n\n", context["pot"])
        print()
        print("Legal Actions:\n")
        for action_type, params in context["legal_actions"].items():
            params = params.copy()
            # Make a copy so we can keep the ``real`` context intact.
            params.pop("type")
            print(self.sub_paragraph.fill(str(action_type)+str(params)))
        print("\n")
        hand_header = "--- YOUR HAND ---".center(self.DEFAULT_WIDTH)
        print(hand_header)
        print(self.pocket)
        print("\n")
        move_header = "--- YOUR MOVE ---".center(self.DEFAULT_WIDTH)
        print(move_header)
        
        prompt = "Enter move type and, if necessary, amount.\n"
        prompt += "Input is not case sensitive.\n\n"
        prompt = self.paragraph.fill(prompt)
        prompt += "\n\nEx.1: ``FOLD``\n"
        prompt += "Ex.2: ``raise 10``\n" 
        prompt += "\n\n"

        repeat = "[Attempt %s of %s]\n"
        repeat += "You didn't specify a valid action type. Let's try again."
        repeat = self.paragraph.fill(repeat)
        repeat += "\n\n"
        
        loop = True
        action = None
        attempts = 0
        
        while loop:
            if attempts:
                prompt = repeat % (attempts, self.MAX_ATTEMPTS)
            
            your_move = input(prompt)
            specs = your_move.split()
            your_type = specs[0].upper()
            
            your_amount = None
            if len(specs) > 1:
                your_amount = int(specs[1])

            if your_type in context["legal_actions"]:
                action = context["legal_actions"][your_type].copy()
                if your_amount:
                    action["amount"] = your_amount
                break
            
            else:
                attempts +=1
                if attempts > self.MAX_ATTEMPTS:
                    print("Exceeded max attempts. Folding.")
                    action = LegalFold()
                    break
                else:
                    continue

        print()
        print(line)
        print()
        
        return action
    
    def set_pocket(self, card1, card2):
        """

        Bot.set_pocket(cards) -> None

        Dealer provides bot with cards
        """
        self.pocket = [card1, card2]
