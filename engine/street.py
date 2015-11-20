# (c) Blackbird Logical Applications, LLC 2015
# bird_em.street
"""
Defines the Street class
"""




#imports
#n/a




#constants
#n/a

#classes
class Street:
    """

    Container that stores card integers for each of the flop, turn, and river.
    ====================  =====================================================
    ATTRIBUTE             VALUE
    ====================  =====================================================

    DATA:
    cards                 list of card integers
    count                 number of cards in the street
    name                  name to display
 
    FUNCTIONS:
    n/a
    ====================  =====================================================
    """
    def __init__(self, name, count):
        self.cards = []
        self.count = count
        self.name = name
