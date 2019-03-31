import random
from itertools import product


class Utilities:
    @staticmethod
    def roll_dice():
        return random.randint(0, 3), random.randint(0, 3)

    @staticmethod
    def pseudo_roll_dice():
        """ This function is used if number of dice rolls exceeds manage-able levels """
        dice_1 = random.randint(0, 3)
        if dice_1 == 0:
            dice_2 = random.randint(2, 3)
        elif dice_1 == 1:
            dice_2 = random.randint(1, 3)
        elif dice_1 == 2:
            dice_2 = random.randint(0, 2)
        else:   # dice_1 == 3
            dice_2 = random.randint(0, 1)
        return dice_1, dice_2

    @staticmethod
    def get_score(dice_1, dice_2):
        return dice_1 + dice_2 if dice_1 + dice_2 > 0 else 12

    @staticmethod
    def can_repeat(score):
        return score in (1, 5, 6, 12)

    @staticmethod
    def has_one(scores: list):
        return 1 in scores

    @staticmethod
    def remove_one(scores: list):
        scores.remove(1)

    @staticmethod
    def get_permutations(scores, num_pawns):
        """ Constructs permutations of the given scores among the num_pawns, that is, all possible ways
            of distributing the scores among the given number of pawns
            Returns a set of permutations with each permutation representing the score assigned to each of the pawns
            of the num_pawns, list(tuple(size: num_pawns))
        """
        """ Stores the resultant set of permutations of scores """
        permutations_ = set()
        """ just a pawn for each id """
        pawn_ids_ = list(range(num_pawns))
        """ Permutation of which score to give to which pawn """
        for score_id_to_pawn_ in product(pawn_ids_, repeat=len(scores)):
            """ score_id_to_pawn is a tuple with each indicating which score to assign to which pawn """
            pawn_scores_ = [0 for _ in pawn_ids_]
            for score_id_, pawn_id_ in enumerate(score_id_to_pawn_):
                pawn_scores_[pawn_id_] += scores[score_id_]
            """ Add as tuple to remove redundancies to a set """
            permutations_.add(tuple(pawn_scores_))
        return permutations_

