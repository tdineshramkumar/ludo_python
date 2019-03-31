from board import Board
from player import Player, PlayerUtils
from utility import Utilities
import random


class Game:
    NUM_PLAYERS = 2
    NUM_PAWNS = 6
    MANAGE_ABLE_ROLLS = 5

    def __init__(self):
        self.board = Board(Game.NUM_PLAYERS)
        self.players = [Player(i, Game.NUM_PAWNS, self.board.get_player_track(i), Board.NUM_CONSTRAINED_SQUARES)
                        for i in range(Game.NUM_PLAYERS)]
        self.player_turn = 0
        self.dice_rolls = []
        self.dice_scores = []
        self.on_dice_roll_handler = None

    def register_dice_roll_handler(self, handler):
        self.on_dice_roll_handler = handler

    def call_dice_roll_handler(self, player_turn, dice):
        if self.on_dice_roll_handler:
            self.on_dice_roll_handler(player_turn, dice)

    def update_turn(self):
        """ Changes turn to next player """
        self.player_turn = (self.player_turn + 1) % Game.NUM_PLAYERS

    def game_step(self):
        """ Moves the game by one move, returns True if game complete """
        if len(self.dice_scores) >= Game.MANAGE_ABLE_ROLLS:
            """ If too many un-handle-able, then roll a pseudo-random dice to terminate throws """
            dice1, dice2 = Utilities.pseudo_roll_dice()
            # input('Enter Pseudo Random Dice:')
            # print('Player:', self.player_turn, 'Throwing a Pseudo Random Dice', (dice1, dice2))
        else:
            dice1, dice2 = Utilities.roll_dice()
        """ Call event handler if any registered """
        self.call_dice_roll_handler(self.player_turn, (dice1, dice2))
        score = Utilities.get_score(dice1, dice2)
        self.dice_rolls.append((dice1, dice2))
        self.dice_scores.append(score)
        # print("Player:", self.player_turn, 'dice thrown', (dice1, dice2), score)
        if not Utilities.can_repeat(score):
            """ End of player turn, update the player pawns if possible """
            player = self.players[self.player_turn]
            while player.any_yet_to_start():
                """ The Bug in the game, this must be done atomically with the next operation """
                if not Utilities.has_one(self.dice_scores):
                    """ If no more ones to start pawns """
                    break
                """ Start some pawn and remove one from scores """
                Utilities.remove_one(self.dice_scores)
                # print("Player:", self.player_turn, 'New Pawn in Progress')
                player.start_some_pawn()

            if player.any_in_progress():
                """ If any pawn to move, then filter permutations for which it moves """
                # print('Player: ', self.player_turn, player)
                # print('In Progress:', self.player_turn, player.in_progress)
                permutations_ = Utilities.get_permutations(self.dice_scores, player.num_pawns_in_progress())
                filtered_permutations_ = PlayerUtils.filter_can_update(player, permutations_)
                # print('Dice Scores:', self.dice_scores)
                # print('Permutations:', permutations_)
                # print('Filtered permutations:', filtered_permutations_)
                if filtered_permutations_:
                    """ If some moves exists, then choose one at random and apply """
                    chosen_permutation_ = random.choice(filtered_permutations_)
                    # print('Chosen Permutation:', chosen_permutation_)
                    player.update_all(chosen_permutation_)

            if player.player_win():
                """ If player won the match, then game over and no need stepping """
                return True

            """ change player turn """
            self.dice_rolls = []
            self.dice_scores = []
            self.update_turn()
            # print('Player:', self.player_turn, 'Start', self.players[self.player_turn].yet_to_start,
            #       'In Progress', self.players[self.player_turn].in_progress,
            #       'Complete', self.players[self.player_turn].is_complete)
        return False

    def get_player(self):
        """ This function is used to get the player after victory """
        return self.player_turn


if __name__ == '__main__':
    game = Game()
    print(game.players)
    print(game.board)
    for i in range(2000):
        print('----------------- Game Step:', i + 1, '------------------')
        if game.game_step():
            print("Done")
            print("Won by ", game.get_player())
            print("Player:", game.players[game.get_player()])
            break





















