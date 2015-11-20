# (c) Blackbird Logical Applications, LLC 2015
# bird_em.exceptions
"""
Module defines custom exception classes. 
"""



#imports
#n/a




#constants
#n/a

#classes
class BirdEmException(Exception):
    c = "Generic parent class for game problems."
    
class OperatingError(BirdEmException):
    c = "The bird_em engine did something wrong."

class StructureError(BirdEmException):
    c = "Some fundamental problem with the game structure."
    
class GameOverError(BirdEmException):
    c = "One of the players at the table has won the game."

class OutOfMoneyError(BirdEmException):
    c = "Player doesn't have enough chips to perform the action."

class ActionError(BirdEmException):
    c = "Player delivered an improperly formatted action."
    
