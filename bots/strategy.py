'''
Created on Nov 19, 2015

@author: chenji
'''

import itertools

class Strategy(dict):
    """

    Dictionary that describes the current mixed strategy.
    Key: (street, pot_size, hand_rank, cur_bet)
        street: FLOP, TURN, RIVER
        pot_size: SMALL -> LARGE
        hand_rank: LOW -> HIGH
        cur_bet: NONE -> HIGH
        
    value: (p1, p2, p3, p4)
        p1: possibility of call/check
        p2 - p4: possibility of raise/bet LOW -> HIGH   
    """


    _NORMALIZE_MINIMUM = 0.1
 
    _DEFAULT_KEYS = list(itertools.product(*[["FLOP", "TURN", "RIVER"], ["SMALL", "MID", "BIG", "LARGE"], ["LOW", "MID", "HIGH"], ["NONE", "LOW", "MID", "HIGH"]]))    
    _DEFAULT_CONTENTS = dict.fromkeys(_DEFAULT_KEYS, (1/4, 1/4, 1/4, 1/4))
    def __init__(self):
        '''
        Constructor
        '''
        super(Strategy, self).__init__(self._DEFAULT_CONTENTS)
        # regret matrix used for regret minimization
        self.regrets = dict.fromkeys(self._DEFAULT_KEYS, (0, 0, 0, 0))
        
    def get_strategy(self, info):
        """
        Strategy.get_strategy(info) -> (p1, p2, p3, p4)
        
        get the mixed strategy from the given information
        """
        street = info["street"]
        hand_rank = self._hand_abstraction(info["hand_rank"])
        pot_size = self._pot_abstractoin(info["pot_size"])
        cur_bet = self._bet_abstraction(info["cur_bet"])
        # TODO hand_compare (worse,same,better)
        return self[(street, pot_size, hand_rank, cur_bet)]

    
    def refine(self):
        """
        Strategy.refine() -> VOID
        
        refine the strategy from the inside regret matrix
        """
        for key, value in self.regrets.items():
            normalize_sum = 0
            _strategy = []
            for i in range(len(value)):
                _strategy.append((value[i] if value[i] > 0 else 0) + self._NORMALIZE_MINIMUM)
                normalize_sum += _strategy[i]
            for i in range(len(value)):
                if normalize_sum > 0:
                    _strategy[i] /= normalize_sum
                else:
                    _strategy[i] = 1 / len(value)
            self[key] = tuple(_strategy)
        
    #############################################  
    ###              ABSTRACTION              ###
    ############################################# 
    
    def _hand_abstraction(self, hand_rank):
        if hand_rank < 0.4:
            return "LOW"
        elif hand_rank < 0.65:
            return "MID"
        else:
            return "HIGH"
        
    def _pot_abstractoin(self, pot_size):
        if pot_size < 20:
            return "SMALL"
        elif pot_size < 40:
            return "MID"
        elif pot_size < 100:
            return "BIG"
        else:
            return "LARGE"
    
    def _bet_abstraction(self, cur_bet):
        if cur_bet == 0:
            return "NONE"
        elif cur_bet < 10:
            return "LOW"
        elif cur_bet < 20:
            return "MID"
        else:
            return "HIGH"
                
         