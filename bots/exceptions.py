'''
Created on Nov 20, 2015

@author: chenji
'''


class TrainException(Exception):
    c = "Generic parent class for training problems."

class HeardsUpError(TrainException):
    c = "Should be 2 players in heads-up game"