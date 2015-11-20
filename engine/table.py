#(c) Blackbird Logical Applications, LLC 2015
# bird_em.table
"""
Module defines Table class. Table objects manage player roster and positional
attributes like button and blinds. 
"""




#imports
from .exceptions import StructureError




#constants
#n/a

#classes
class Table:
    """

    Container for managing players generally. Players that sit at the table
    stay at the table, even if they run out of chips. 
    ====================  =====================================================
    ATTRIBUTE             VALUE
    ====================  =====================================================

    DATA:
    BUY_IN                int; starting stack size
    BLINDS                list; [small blind, big blind]
    MAX_SEATS             int; total number of seats
    button                int; seat index for dealer on the table
    players               list; players at table, includes inactive
    i_big                 int; seat index for big blind
    i_small               int; seat index for small blind 

    FUNCTIONS:
    get_ordered()         return list of players in order of action
    join()                add a player to the instance, error if already there
    prep()                set hands, activate players with chips, move button               
    ====================  =====================================================
    """
    BLINDS = [1, 2]
    BUY_IN = 200
    MAX_SEATS = 2

    def __init__(self):
        self._button = None
        self._small = None
        self._big = None
        self._hot_seat = None
        self.players = []

    class _WrapAroundDescriptor:
        """
        Descriptor that wraps integers into a valid list index for
        instance.players. So if there are 3 players at the table, a 3 will
        become a 0, a 4 will become a 1, and a 5 will become a 2.

        Will raise a StructureError if the integer doesn't fit after one wrap. 
        """
        def __init__(self, attr_name):
            self.attr_name = attr_name
            # Controls where descriptor looks for instance-level state.
            
        def __get__(self, instance, owner):
            position = getattr(instance, self.attr_name)
            return position

        def __set__(self, instance, value):
            current_position = getattr(instance, self.attr_name)
            player_count = len(instance.players)
            #
            if value >= player_count:
                wrapped_position = value - player_count
                if wrapped_position <= (player_count - 1):
                    # If you have two players, max index can be 3 (which will
                    # become 1). An index of 4 would have to wrap around twice.
                    dashed_attr = getattr(instance, self.attr_name)
                    dashed_attr = wrapped_position
                else:
                    c = "\nCan't wrap around more than once.\n"
                    c += "\n\trequested value: %s\n"
                    c += "\n\tmax length:      %s\n"
                    c = c % (value, player_count)
                    raise StructureError(c)
            else:
                setattr(instance, self.attr_name, value)
                # Value can serve as an index as-is
        
    button = _WrapAroundDescriptor("_button")
    i_small = _WrapAroundDescriptor("_small")
    i_big = _WrapAroundDescriptor("_big")
    hot_seat = _WrapAroundDescriptor("_hot_seat")

    def get_ordered(self, pre_flop=False):
        """

        Table.get_ordered() -> list
        
        Returns a list of players in order of action. Pre-flop, action starts at
        big_blind + 1. Post-flop, action starts at button + 1. 
        """
        if pre_flop:
            self.hot_seat = self.i_big
            self.hot_seat += 1
        else:
            self.hot_seat = self.button
            self.hot_seat += 1
        # Use hot_seat so index wraps around.

        if self.hot_seat is None:
            c = "Invalid hot seat index"
            raise StructureError(c)
        
        ordered = self.players[self.hot_seat :] + self.players[: self.hot_seat]
        return ordered

    def join(self, player):
        """

        Table.join() -> None

        Add player to instance.players. Raie StructureError if the player is
        already sitting at the table. 
        """
        if player not in self.players:
            self.players.append(player)
        else:
            c = "Player is already at the table."
            raise StructureError(c)
    
    def prep(self, hand):
        """

        Table.prep() -> None
        
        Set hand, activate players that have enough money to post the big blind.
        If there are enough people to play, move the button. Will raise a
        StructureError if there are less than 2 active players. 
        """
        self.hand = hand
        active_count = 0

        for player in self.players:
            if player.stack >= self.BLINDS[1]:
                player.activate()
                active_count += 1
            else:
                player.deactivate()
                
        if active_count < 2:
            c = "Table needs at least 2 active players for a game."
            raise StructureError(c)

        if self.button == None:
            self.button = 0
        else:
            self.button += 1

        


    
    
