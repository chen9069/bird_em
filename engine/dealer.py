#(c) Blackbird Logical Applications, LLC 2015
# bird_em.dealer
"""
Module defines the Dealer class. Dealer objects do all of the hard work in
running a game. 

Dealer uses Will Drevo's excellent ``deuces`` evaluator library for card-level
logic. See https://github.com/worldveil/deuces.
"""




#imports
import deuces3x.deuces as deuces

from api import LegalBet, LegalCheck, LegalCall, LegalFold, LegalRaise
from api import PerformedAction

from .exceptions import ActionError, GameOverError, OperatingError
from .hand import Hand
from .table import Table





#constants
#n/a


#classes
class Dealer:
    """

    Dealer objects run the poker game. They organize players, coordinate
    betting, determine hand outcomes, and move chips around the table.

    Dealer uses Will Drevo's ``deuces`` library.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA: 
    #n/a

    FUNCTIONS:
    start_game()          activate players and add them to the table
    play_hand()           play a single hand through conclusion
    ====================  ====================================================
    """
    def __init__(self):
        self._table = None
        self._judge = deuces.Evaluator()

    def start_game(self, *players):
        """

        Dealer.start_game() -> None

        Expects 2+ Player objects as args, adds players to the table. Players
        don't take any action yet. 
        """
        self._table = Table()
        for player in players:
            player.join_table(self._table, self._table.BUY_IN)
            player.activate()
        
    def play_hand(self, deck=None):
        """

        Dealer.play_hand() -> None

        Play a hand with all the players at the table. Dealer will hand out
        cards, then ask each Player for actions. The hand concludes when
        everyone folds or after a successful showdown on the river. 

        ``deck`` accepts pre-shuffled decks for duplication.
        """
        see_flop = self._start_hand(deck=deck)
        # Run pre-flop action separately.
        
        if see_flop:
            self.hand.players = self._table.get_ordered()
            # Update hand with post-flop order of action
            
            for street in self.hand.streets:
                self.hand.street = street.name
                if street.cards:
                    # Already dealt cards for this street.
                    continue
                else:
                    self._DEAL(street.name)
                    street.cards = [self.deck.draw() for i in range(street.count)]
                    # Make sure turn and river are lists of one card. Cards are
                    # integers to preserve bitwise ops in deuces.

                    print(street.name)
                    deuces.Card.print_pretty_cards(street.cards)
                    
                    survivors = self._run_betting()
                    
                    if len(survivors) > 1:
                        # Deal the next street. 
                        continue
                    else:
                        # Hand is over. _run_betting() already awarded winner.
                        break
                    
            else:
                # 2+ players survived betting on the river.
                self._compare_hands(*survivors)
                
        # Run confirmation logic for good measure. Routine will raise error if
        # if it detects a problem.
        self._check_ops()        

    #************************************************
    #                1.LEGAL ACTIONS                *
    #************************************************

    # Actions dealer may get back from a player. All functions have identical
    # interfaces so dealer can blindly delegate work to whatever method matches
    # the action type.

    def _FOLD(self, player, action=None, legal_actions=None):
        """
        Return -1 to distinguish from _CHECK and _CALL.
        """
        amount = -1
        player.fold()
        self._write_to_log(actor=player.name, type="FOLD")
        return amount

    def _CHECK(self, player, action, legal_actions):
        amount = 0
        if self._check_type(action, legal_actions):
            player.bet(0)
            self._write_to_log(actor=player.name, type="CHECK")
        else:
            self._FOLD(player)
        return amount

    def _CALL(self, player, action, legal_actions):
        amount = 0
        
        ok_move = self._check_type(action, legal_actions)
        ok_size = True
        if action["amount"] != legal_actions["CALL"]["amount"]:
            ok_size = False

        if ok_move and ok_size:
            amount = action["amount"]
            player.bet(amount)
            self._write_to_log(actor=player.name, type="CALL", amount=amount)
        else:
            self._FOLD(player)
            print("Forced fold on illegal action.")
        #
        return amount
        
    def _BET(self, player, action, legal_actions):
        amount = 0
        ok_move = self._check_type(action, legal_actions)

        requested_type = action["type"]
        bet_parameters = legal_actions[requested_type]
        ok_size = self._check_size(action, bet_parameters)

        if ok_move and ok_size:
            amount = action["amount"]
            player.bet(amount)
            self._write_to_log(actor=player.name, type="BET", amount=amount)
        else:
            self._FOLD(player)
            print("Forced fold on illegal action.")
        #
        return amount

    def _RAISE(self, player, action, legal_actions):
        """
        """
        amount = 0
        ok_move = self._check_type(action, legal_actions)

        requested_type = action["type"]
        raise_parameters = legal_actions[requested_type]
        ok_size = self._check_size(action, raise_parameters)
        
        if ok_move and ok_size:
            amount = action["amount"]
            player.bet(amount)
            self._write_to_log(actor=player.name, type="RAISE", amount=amount)
        else:
            self._FOLD(player)
            print("Forced fold on illegal action.")
        #
        return amount

    #************************************************
    #             2.PERFORMED ACTIONS               *
    #************************************************
    
    # Actions you will never see come back from a player. Only dealer will call
    # these, so they can have custom interfaces. 

    def _WIN(self, player, amount):
        player.credit(amount)
        self._write_to_log(actor=player.name, type="WIN", amount=amount)

    def _REFUND(self, player, amount):
        player.credit(amount)
        self._write_to_log(actor=player.name, type="WIN", amount=amount)

    def _SHOW(self, player, card1, card2):
        self._write_to_log(actor=player.name, type="SHOW",
                           card1=card1, card2=card2)

    def _TIE(self, player, amount):
        player.credit(amount)
        self._write_to_log(actor=player.name, type="TIE", amount=amount)

    def _DEAL(self, street_name):
        self._write_to_log(type="DEAL", street=street_name)

    def _POST(self, player, amount):
        player.bet(amount)
        self._write_to_log(actor=player.name, type="POST", amount=amount)

    #************************************************
    #               3. HAND START-UP                *
    #************************************************
    
    def _start_hand(self, deck=None):
        """

        Dealer._start_hand() -> bool 

        Returns True if at least 2 players are ready to see the flop, False
        otherwise. 
        """
        self.hand = Hand()
        self.hand.street = "PRE_FLOP"
        self._table.prep(self.hand)       
        # Generally, Dealer modifies the hand. Table serves as an access
        # point to the hand for all of the players. 
        
        if deck is None:
            self.deck = deuces.Deck()
            # Every deck instance is shuffled.
        else:
            self.deck = deck
        
        for player in self._table.players:
            # Deal to every player at the table to preserve duplication. 
            cards = self.deck.draw(2)
            player.set_pocket(*cards)
            player.set_evaluator(self._judge)

        self._post_blinds()

        print()
        print("Blinds posted.")
        print()
        print("button:  ", self._table.button)
        print("small:   ", self._table.i_small)
        print("big:     ", self._table.i_big)
        print("hot_seat:", self._table.hot_seat)
        print()
        
        self.hand.players = self._table.get_ordered(pre_flop=True)
        # Once players post blinds, you know the order of action

        print("About to start betting ...")
        print("hot_seat:", self._table.hot_seat)
        
        in_the_hand = self._run_betting()
        see_flop = False
        
        if len(in_the_hand) > 1:
            see_flop = True
            
        return see_flop
    
    def _post_blinds(self):
        """

        Works for 2+ person tables. 
        """

        # Figure out which seat at the table **should** post small blind.

        self._table.i_small = self._table.button
        if len(self._table.players) > 2:
            self._table.i_small = self._table.button + 1
        # Use i_small so the index can roll over.
        small = self._table.i_small

        # In heads-up play, the button posts small blind. Otherwise, player
        # to the left of the dealer posts small.

        # We will now check if the player that **should** post small blind has
        # the money to do so. If not, go around the table until you find someone
        # who can. After you find the small blind, go through the remaining
        # players to find a big blind. If can't find both, can't run game. 

        candidates = self._table.players[small :] + self._table.players[: small]
        offset = small
        
        for i in range(len(candidates)):
            # Outer loop looks for a player that can post small blind.
            player_1 = candidates[i]

            if player_1.stack < self._table.BLINDS[1]:
                # Only players who can post the big blind can sit at the table.
                player_1.deactivate()
                # Keep looking.
                continue
            else:
                self._POST(player_1, self._table.BLINDS[0])
                self._table.i_small = i + offset

                # Now look for the big blind. Only get here after small has posted.
                remaining = candidates[(i+1):]
                
                for j in range(len(remaining)):
                    # Inner loop looks for a player that can post big blind.
                    player_2 = remaining[j]
                    
                    if player_2.stack < self._table.BLINDS[1]:
                        player_2.deactivate()
                        # Keep looking.
                        continue
                    else:
                        self._POST(player_2, self._table.BLINDS[1])
                        self._table.i_big = j + offset + 1
                        break
                        # Big blind posted, go back to outer loop for wrap-up.
                else:
                    # Run off from inner loop.
                    c = "No players can post big blind"
                    raise GameOverError(c)

                # If make it here without exception, successfully posted both
                # small blind and big blind.
                break
        else:
            # Run off from outer loop.
            c = "No players can post small blind"
            raise GameOverError(c)    
    
        # Super-simple alternative for 2 people only.
##        if len == 2:
##            p_small = self.players[self.button]
##            p_big = self.players[not self.button]
##        try:
##            p_small.post_blind(small_blind)
##            p_big.post_blind(big_blind)
##        except OutOfMoneyError:
##            raise GameError

    #************************************************
    #                4. HAND CONTROL                *
    #************************************************

    def _check_ops(self):
        """

        Run validation logic on hand record:
        
        - check that history ends with a WIN or a TIE
        - check that pot is at zero (all winnings distributed)

        Method will raise an OperatorError if it finds a problem.
        """
        last_action = self.hand.history[-1]
        if last_action["type"] not in {"WIN", "TIE"}:
            raise OperatingError("Hand must end with a win or a tie.")
        
        if self.hand.pot:
            raise OperatingError("Pot should be at zero.")
    
    def _run_betting(self):
        """
        Return list of players in the hand.

        """
        need_action = self.hand.players[:]
        in_the_hand = []
        next_round = []
        
        high_bet = 0
        high_better = None
        
        while need_action:
            count = len(need_action)
            for i in range(count):
                player = need_action.pop(0)                

                if not player.active:
                    continue

                self.hand.cur_bet = high_bet
                hand_profile = self._set_params(player, high_bet)
                action = player.get_action(hand_profile)
                legal_actions = hand_profile["legal_actions"]
                # Compare action against those we told the player are ok.
                new_bet = self._process_action(player, action, legal_actions)

##                print("New bet:  ", new_bet)
##                print("High bet: ", high_bet)

                if new_bet == -1:
                    # Player folded, automatically falls out of hand.

                    # Check for special case: if only one player remaining,
                    # and no one is in the pot, remaining player wins by
                    # default, without having to take an action.
                    special_case = False
                    
                    if not in_the_hand:
                        if len(need_action) == 1:
                            special_case = True
                            # No one in the hand and one player remaining
                    
                    if special_case:
                        last_man = need_action.pop()
                        in_the_hand.append(last_man)
                        # Now need_action will be empty. We are going to break
                        # out of the for loop. The while loop will stop on its
                        # own. 
                        break
                    else:
                        continue
    
                elif 0 <= new_bet <= high_bet:
                    
                    delta = high_bet - new_bet
                    if delta:
                        self._REFUND(high_better, delta)
                        # Automatic refunds, 2-player only

                    if player.active:
                        # Check, in case an inactive one snuck in somehow.
                        in_the_hand.append(player)
                else:                
                    high_bet = new_bet
                    high_better = player

                    next_round = need_action + in_the_hand

                    in_the_hand.clear()
                    in_the_hand.append(player)
                    # Only the high better is currently in the hand; waiting to
                    # hear from all the others.
                    
                    break
                    # Break out of the for loop
            need_action = next_round
            # Start the while loop all over again, but without folded players.
                        
        if not in_the_hand:
            c = "Must finish betting with at least one player in the hand."
            raise OperatingError(c)

        if len(in_the_hand) == 1:
            self._award_pot(*in_the_hand)

        return in_the_hand

        # Re sidegames: could put another Hand instance on the current hand as
        # the side game. Then can be as recursive as you want it to be.
        #
        # Outline: if delta, increment hand.side_game.pot and add high better to
        # hand.side_game.players. Then, in the high_bet logic, check if there is
        # a side game, and add people to it. Would then need to walk through the
        # side games recursively.
        
    def _award_pot(self, *players):
        """

        Dealer._award_pot() -> None
        
        Award pot to player(s). Discard fractional chips.
        """
        count = len(players)
        share = self.hand.pot // count
        # Use classic division, discard fractional chips.
        
        if count == 1:
            self._WIN(players[0], share)
        elif count > 1:
            for player in players:
                self._TIE(players[0], share)
        else:
            raise OperatingError
        
    def _compare_hands(self, *players, display=True):
        """
        eval cards for each player
        print eval
        post show actions
        post win action for winners.

        -> list

        Return list of winning players
        """
        worst_possible_rank = deuces.lookup.LookupTable.MAX_HIGH_CARD
        # 7-high. 
        best_rank = worst_possible_rank + 1
        # Start with a rank below the worst possible, so any real hand beats it.
        
        winners = []
        for player in players:
            rank = self._judge.evaluate(player.pocket, self.hand.board)
            # Rank of 1 is best. Ace-high royal flush is ranked 1.
            
            card_strings = [deuces.Card.int_to_pretty_str(card) for card in player.pocket]
            # Cards are integers, turn them into ``[Rank][suit]`` strings for logging.
            self._SHOW(player, card_strings[0], card_strings[1])

            if display:
                rank_class = self._judge.get_rank_class(rank)
                class_string = self._judge.class_to_string(rank_class)
                percentage = 1.0 - self._judge.get_five_card_rank_percentage(rank)
                # Higher percentage is better.
                announcement = "Player %s hand = %s, percentage rank among all hands = %f"
                announcement = announcement % (player.name, class_string, percentage)
                print(announcement)
            
            if rank == best_rank:
                winners.append(player)
                # Current hand tied with other hands. More than one winner.
            elif rank < best_rank:
                # Current hand is better than prior ones, one winner only.
                winners = [player]
                best_rank = rank

        if display:
            print()
            if len(winners) == 1:
                blurb = "Player %s is the winner with a %s\n"
                blurb = blurb % (winners[0].name,
                         self._judge.class_to_string(
                             self._judge.get_rank_class(
                                 self._judge.evaluate(winners[0].pocket, self.hand.board)
                                 )
                             )
                         )
            else:
                blurb = "Players %s tied for the win with a %s\n"
                blurb = blurb % (winners,
                         self._judge.class_to_string(
                             self._judge.get_rank_class(
                                 self._judge.evaluate(winners[0].pocket, self.hand.board)
                                 )
                             )
                         )
            print(blurb)
                
        self._award_pot(*winners)
        
        return winners
    

    def _set_params(self, player, current_bet):
        """

        Return HandInfo dictionary populated for player.
        """
        params = self.hand.get_profile()
        legal_actions = params["legal_actions"]
        legal_actions["FOLD"] = LegalFold()
        # Players can always fold.

        # A player's legal actions depend on the betting that has already taken
        # place on the current street. Add the appropriate actions here. If a
        # player is not active, they must fold.
        if player.active:
            
            if current_bet:
                # bet is on the table; call or raise
                call = LegalCall()
                call["amount"] = min(current_bet, player.stack)
                legal_actions["CALL"] = call

                # raise is always TO a number. raise must be at least 2x prior
                # bet. 
                raise_ = LegalRaise()
                raise_["min"] = current_bet + min(
                    max(current_bet, self._table.BLINDS[1]),
                    player.stack
                    )
                raise_["max"] = player.stack
                # when player doesn't have enough chips to double the current
                # bet, she can only raise by going all-in. 
                legal_actions["RAISE"] = raise_
                
            else:
                #so far, no bets on the table
                legal_actions["CHECK"] = LegalCheck()

                new_bet = LegalBet()
                new_bet["min"] = min(player.stack, self._table.BLINDS[1])
                new_bet["max"] = player.stack
                legal_actions["BET"] = new_bet
    
        return params
        
    def _check_size(self, action, action_params):
        """


        Dealer._check_amount() -> bool()

        
        Returns True if action["amount"] fits in [params["min"], params["max"]],
        False otherwise.

        If params is missing keys, will raise OperatingError. If action is
        missing a key, will raise ActionError. 
        """
        result = False

        lo_bound = action_params.get("min")
        hi_bound = action_params.get("max")
        if not all([lo_bound, hi_bound]):
            c = "Cannot perform check. Parameters missing a bound."
            c += "\n\tparams[``min``] : %s"
            c += "\n\tparams[``max``] : %s\n"
            c = c % (lo_bound, hi_bound)
            raise OperatingError(c)
        
        amount = action.get("amount")
        if not amount:
            c = "Action is missing an ``amount`` key"
            raise ActionError(c)
        
        if lo_bound <= amount <= hi_bound:
            result = True
            # Will return True if action == lo_bound == hi_bound. lo_bound and
            # hi_bound are the same number when a player can only raise by
            # pushing all-in (i.e., she doesn't have 2x the last bet). 
       
        return result

    def _check_type(self, action, legal_actions):
        """

        Dealer._check_type() -> bool
        
        Return True if legal_actions include action type, False otherwise.
        """
        result = False
        if action["type"] in legal_actions:
            result = True
    
        return result

    def _process_action(self, player, action, legal_actions):
        """

        -> int
        
        find the right action, pass args down
        """
        method = self._FOLD
        # Fold by default.
        requested_name = action.get("type")
    
        if requested_name:
            method_name = "_" + requested_name
            try:
                method = getattr(self, method_name)
            except AttributeError:
                pass
        new_bet = method(player, action, legal_actions)
        # Method will be _FOLD unless we found an exact match.
        
        return new_bet
        
    def _write_to_log(self, **kwargs):
        """

        Dealer._write_to_log() -> None

        Add an entry to the hand history. Entry will be a PerformedAction
        updated with kwargs. 
        """
        new_entry = PerformedAction()
        new_entry.update(kwargs)        
        self.hand.history.append(new_entry)

            
            
        
        
