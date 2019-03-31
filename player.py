from pawns import Pawn
from collections import Counter


class Player:
    def __init__(self, player_id, num_pawns, squares, num_constrained_squares):
        self.num_pawns = num_pawns
        self.player_id = player_id
        self.num_squares = len(squares)
        self.squares = squares
        self.pawns = [Pawn(self, self.num_squares, num_constrained_squares) for _ in range(num_pawns)]
        self.on_pawn_status_change_handler = None
        self.__separate_pawns_on_status__()

    def register_pawn_status_change_handler(self, handler):
        self.on_pawn_status_change_handler = handler

    def call_pawn_status_change_handler(self):
        if self.on_pawn_status_change_handler:
            self.on_pawn_status_change_handler(self)

    def __separate_pawns_on_status__(self):
        """ Group pawns based on status """
        self.call_pawn_status_change_handler()
        self.yet_to_start = [pawn for pawn in self.pawns if pawn.yet_to_start()]
        self.in_progress = [pawn for pawn in self.pawns if pawn.in_progress()]
        self.is_complete = [pawn for pawn in self.pawns if pawn.is_complete()]
        assert len(self.yet_to_start) + len(self.in_progress) + len(self.is_complete) == self.num_pawns

    def remove_constraints(self):
        for pawn in self.pawns:
            pawn.remove_constraint()

    def any_yet_to_start(self):
        """ Returns true if any pawn is yet to start """
        return len(self.yet_to_start) > 0

    def num_yet_to_start(self):
        return len(self.yet_to_start)

    def any_in_progress(self):
        """ Returns true if any pawn in progress """
        return len(self.in_progress) > 0

    def start_some_pawn(self):
        assert self.any_yet_to_start()
        " Get some pawn from yet to start list, start it and separate pawns on status "
        pawn = self.yet_to_start.pop(0)
        pawn.start()
        """ Add to first position, as it started """
        self.squares[0].add_pawn(pawn)
        self.__separate_pawns_on_status__()

    def player_win(self):
        return len(self.is_complete) == self.num_pawns

    def num_pawns_in_progress(self):
        return len(self.in_progress)

    # def __can_update_pawn__(self, pawn_id, num_steps):
    #     assert 0 <= pawn_id < self.num_pawns_in_progress()
    #     pawn = self.in_progress[pawn_id]
    #     assert pawn.in_progress()
    #     if pawn.can_update(num_steps):
    #         if pawn.on_last_square(num_steps) or pawn.can_complete(num_steps):
    #             """ If this results is pawn being on last square, then it is only allowed if some pawn exists in
    #             start state or some other pawn in progress is not in last square """
    #             """ Also it may be possible that on update of this pawn, this pawn completes
    #                                                    all other pawns may be in last position """
    #             if self.any_yet_to_start():
    #                 return True
    #             elif len(self.in_progress) > 1 and \
    #                     any(not pawn_.on_last_square() for pawn_ in self.in_progress if pawn_ != pawn):
    #                 """ If any other pawn in progress not on last square """
    #                 return True
    #
    #             if pawn.can_complete(num_steps):
    #                 if len(self.in_progress) == 1:
    #                     """ If this is the only one then complete """
    #                     return True
    #             """ If no other satisfies required criteria, then cannot be updated to last position """
    #             return False
    #         return True
    #     return False

    # def __update_pawn__(self, pawn_id, num_steps):
    #     assert self.__can_update_pawn__(pawn_id, num_steps)
    #     """ Update the pawn by num_steps """
    #     pawn = self.in_progress[pawn_id]
    #     pawn.update(num_steps)
    #     self.__separate_pawns_on_status__()

    def can_update_all(self, pawns_num_steps):
        assert self.num_pawns_in_progress() > 0
        assert self.num_pawns_in_progress() == len(pawns_num_steps)
        new_positions = Counter()
        for pawn_id_, num_steps_ in enumerate(pawns_num_steps):
            pawn = self.in_progress[pawn_id_]
            assert pawn.in_progress()
            if not pawn.can_update(num_steps_):
                """ If can't update some pawn """
                return False
            if pawn.can_complete(num_steps_):
                """ If pawn completes, then check another pawn"""
                continue
            new_position = pawn.get_position(num_steps_)
            """ These prevent cases of moving a pawn from to an old position occupied another pawn, 
                buts its okay as the pawn can go to the position ahead of the position that other pawn may have
                been pushed to
                X X X X P X X X (P) X X X 
                        ^        ^
                X X X X X X X X (P) X X P
                Jump ahead instead of two moves, achieve in single move
            """
            if not self.squares[new_position].can_add_pawn(pawn):
                """ If pawn can't be added, then not suitable for update 
                or another permutation may be suitable """
                return False
            """ Add to new positions list to check if any collisions """
            new_positions[new_position] += 1

        """ Once we all the resultant positions, 
        the duplicate positions must only be either HomeSquare or HubSquares """
        if len(new_positions) != self.num_pawns_in_progress():
            """ If more than one pawn in given position, validate if possible by checking their types """
            for position_ in new_positions:
                if new_positions[position_] > 1:
                    """ In case of collisions, prevent update on Square, 
                    multiple pawns on same square not supported """
                    if not self.squares[position_].can_support_multiple_elements():
                        return False
        """ Multiple pawns supported in those positions, then check other constraints """
        if self.any_yet_to_start():
            """ If some player is yet to start then no problem at the last position, as it can be moved """
            return True

        if all(self.in_progress[pawn_id_].can_complete(num_steps_)
               for pawn_id_, num_steps_ in enumerate(pawns_num_steps)):
            """ If all pawns in progress completes on updates, then allow """
            return True
        """ As only single pawn can be move at a time, that is num_steps can be divided among pawns on same square, 
                all pawns in progress must not be at last position as a result of the move  """
        if all(self.in_progress[pawn_id_].can_complete(num_steps_) or
               self.in_progress[pawn_id_].on_last_square(num_steps_)
               for pawn_id_, num_steps_ in enumerate(pawns_num_steps)):
            """ If result of update is that, all pawns in last step (at-least one) and remaining complete (any no.),
                then don't allow it due to absence of next move"""
            return False
        """ Otherwise return true"""
        return True

    def score_potential(self, pawns_num_steps):
        """ Returns many opponents may be replaced for a given choice """
        assert self.can_update_all(pawns_num_steps)
        completes, kills = 0, 0
        for pawn_id_, num_steps_ in enumerate(pawns_num_steps):
            if self.in_progress[pawn_id_].can_complete(num_steps_):
                """ on completion """
                completes += 1
                continue
            new_position = self.in_progress[pawn_id_].get_position(num_steps_)
            if self.squares[new_position].can_score(self.in_progress[pawn_id_]):
                """ on a kill """
                kills += 1
        """ Score is determined by number of kills and completes """
        return kills, completes

    def update_all(self, pawns_num_steps):
        assert self.can_update_all(pawns_num_steps)
        """ Create a local copy, as the pawns in progress it prone to change """
        pawns_in_progress_ = self.in_progress.copy()
        for pawn_id_, num_steps_ in enumerate(pawns_num_steps):
            pawn_ = pawns_in_progress_[pawn_id_]
            old_position = pawn_.get_position()
            """ Remove the pawn from old position """
            self.squares[old_position].remove_pawn(pawn_)
            pawn_.update(num_steps_)
            """ If pawn status changes, then update """
            self.__separate_pawns_on_status__()
            if not pawn_.is_complete():
                """ If pawn is not complete, then we need to add pawn to new position """
                new_position = pawn_.get_position()
                self.squares[new_position].add_pawn(pawn_)

    # def can_update(self, pawn_id, num_steps):
    #     if self.__can_update_pawn__(pawn_id, num_steps):
    #         """ If pawn can be updated, then check if squares allow """
    #         pawn = self.in_progress[pawn_id]
    #         if pawn.can_complete(num_steps):
    #             """ If it can complete the track """
    #             return True
    #         """ Get the position, and check is square on resultant can accommodate this pawn"""
    #         position = pawn.get_position(num_steps)
    #         if self.squares[position].can_add_pawn(pawn):
    #             return True
    #         # print("Can't be updated as squares don't allow addition")
    #     """ If pawn cannot be updated or square cannot be updated then not possible """
    #     # print("Can't update because pawn can't be updated", pawn_id, num_steps, self.in_progress[pawn_id])
    #     return False

    # def update(self, pawn_id, num_steps):
    #     """ Updates the pawn at given id by num_steps,
    #     this function returns True if the updated pawn completed,
    #     this value is useful if multiple pawns are updated """
    #     assert self.can_update(pawn_id, num_steps)
    #     pawn = self.in_progress[pawn_id]
    #     old_position = pawn.get_position()
    #     """ Remove the pawn from old position """
    #     self.squares[old_position].remove_pawn(pawn)
    #
    #     """ Update the pawn """
    #     self.__update_pawn__(pawn_id, num_steps)
    #     if not pawn.is_complete():
    #         """ Then pawn's new position myst be updated """
    #         new_position = pawn.get_position()
    #         self.squares[new_position].add_pawn(pawn)
    #         """ Adding new pawn may potentially remove another pawn from the square,
    #          so the other player must be updated, not current player """
    #         # self.__separate_pawns_on_status__()
    #         return False
    #     return True

    def __repr__(self):
        return '[' + ','.join(str(pawn) for pawn in self.pawns) + ']'


class PlayerUtils:
    """ Methods have some bug """
    # @staticmethod
    # def can_update(player: Player, pawns_num_steps):
    #     """ This utility function checks if possible to move PROGRESS pawns be given num steps per pawn """
    #     assert player.num_pawns_in_progress() == len(pawns_num_steps)
    #     for pawn_id_, num_steps_ in enumerate(pawns_num_steps):
    #         if not player.can_update(pawn_id_, num_steps_):
    #             """ If some pawn can't be updated, then this set of steps can't be used """
    #             return False
    #
    #     """ Addition not allowed if many added to same position, due to constraints of the model """
    #     new_positions_ = set()
    #     for pawn_id_, num_steps_ in enumerate(pawns_num_steps):
    #         """ Add the possible new position to set """
    #         new_positions_.add(player.in_progress[pawn_id_].get_position(num_steps_))
    #     """ If collision in new positions update not possible """
    #     if len(new_positions_) < player.num_pawns_in_progress():
    #         """ Collisions are un-acceptable"""
    #         return False
    #     """ Also check if one update of all pawns, if all in last step """
    #     if not player.any_yet_to_start():
    #         """ If nothing to start """
    #         """ If all can complete """
    #         if all(player.in_progress[pawn_id_].can_complete(num_steps_)
    #                for pawn_id_, num_steps_ in enumerate(pawns_num_steps)):
    #             return True
    #         if all(player.in_progress[pawn_id_].on_last_square(num_steps_)
    #                or player.in_progress[pawn_id_].can_complete(num_steps_)
    #                for pawn_id_, num_steps_ in enumerate(pawns_num_steps)):
    #             """ And on update all reach last step or can complete, then update not possible """
    #             return False
    #
    #     return True

    @staticmethod
    def filter_can_update(player: Player, permutations_pawns_num_steps):
        """ This utility function checks if each of the permutations can update
         and returns only those which can update"""
        filtered_permutations_ = []
        for pawns_num_steps_ in permutations_pawns_num_steps:
            if player.can_update_all(pawns_num_steps_):
                filtered_permutations_.append(pawns_num_steps_)
        return filtered_permutations_

    # @staticmethod
    # def update(player: Player, pawns_num_steps):
    #     """ This utility function is used to update player with givens steps for each pawn """
    #     assert PlayerUtils.can_update(player, pawns_num_steps)
    #     """ num_completed_ is just a hack """
    #     num_completed_ = 0
    #     for pawn_id_, num_steps_ in enumerate(pawns_num_steps):
    #         print('Updated id:', pawn_id_ + num_completed_)
    #         if player.update(pawn_id_ + num_completed_, num_steps_):
    #             """ If player update results in completion we need to use updated pawn_id,
    #              which is reflected using num_completed_"""
    #             num_completed_ -= 1

    @staticmethod
    def max_move_able_steps(player: Player):
        """ Returns the maximum number of total steps which given player can move"""
        return sum(pawn_.get_remaining() for pawn_ in player.in_progress)


""" Player has a bug, it can start some pawn, even if after starting pawns can't move """
