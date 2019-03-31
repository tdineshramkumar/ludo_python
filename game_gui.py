import pygame
from squares import *
from colors import *
from game import Game


class GameGUI:
    BOX_WIDTH = 50
    NUM_BOXES = 6  # Indicates the number of boxes on a side
    TOTAL_BOXES = NUM_BOXES * 2 + 3
    WIDTH = BOX_WIDTH * TOTAL_BOXES
    FPS = 10

    def __draw_player__(self, player):

        if player.player_id == 0:
            left = GameGUI.NUM_BOXES + 1
            top = GameGUI.NUM_BOXES + 2
        else:
            left = GameGUI.NUM_BOXES + 1
            top = GameGUI.NUM_BOXES
        box_width = GameGUI.BOX_WIDTH
        square_rect = pygame.Rect(left * box_width, top * box_width, box_width, box_width)

        def __draw__(_player):

            assert _player == player
            # if player.any_yet_to_start():
            #     cur_num_players = player.num_yet_to_start()
            # else:
            #     cur_num_players = 0
            # if cur_num_players != num_players:
            if player.any_yet_to_start():
                player_color = RED if player.player_id == 0 else BLUE
                pygame.draw.ellipse(self.screen, player_color, square_rect)
                num_players = player.num_yet_to_start()
                if num_players > 1:
                    self.__draw_text__(square_rect, str(num_players))
            else:
                pygame.draw.rect(self.screen, WHITE, square_rect)
                self.rectangle_list.append(square_rect)
        __draw__(player)

        def __handler__(_player):
            __draw__(_player)

        return __handler__

    def __draw_text__(self, rect, text):
        text_surf = self.font.render(text, True, BLACK)
        text_rect = text_surf.get_rect()
        text_rect.center = rect.center
        self.screen.blit(text_surf, text_rect)

    def __draw_dice__(self, dice_index, dice):
        assert 0 <= dice_index < len(self.dice_pos)
        assert len(dice) == 2
        left, top = self.dice_pos[dice_index]
        box_width = GameGUI.BOX_WIDTH
        for value in dice:
            assert value in range(0, 4)
            color1 = GRAY if value in (0, 1) else BLACK
            color2 = GRAY if value in (0, 2) else BLACK
            pygame.draw.rect(self.screen, GRAY, (left * box_width, top * box_width, box_width, box_width * 3))
            pygame.draw.ellipse(self.screen, color1, (left * box_width, top * box_width, box_width, box_width))
            pygame.draw.ellipse(self.screen, color2, (left * box_width, (top + 1) * box_width, box_width, box_width))
            pygame.draw.ellipse(self.screen, color1, (left * box_width, (top + 2) * box_width, box_width, box_width))
            self.rectangle_list.append((left * box_width, top * box_width, box_width, box_width * 3))
            left += 2

    def __square__(self, left, top, type, start=True):
        box_width = GameGUI.BOX_WIDTH
        square_rect = pygame.Rect(left * box_width, top * box_width, box_width, box_width)

        def __draw__():
            if type == Square:
                pygame.draw.rect(self.screen, BLACK, square_rect)
            elif type == HubSquare:
                pygame.draw.rect(self.screen, BLACK, square_rect)
                pygame.draw.line(self.screen, WHITE, square_rect.topleft, square_rect.bottomright, 2)
                pygame.draw.line(self.screen, WHITE, square_rect.topright, square_rect.bottomleft, 2)
            else:
                if start:
                    pygame.draw.rect(self.screen, GRAY, square_rect)
                else:
                    pygame.draw.rect(self.screen, WHITE, square_rect)

        __draw__()
        self.rectangle_list.append(square_rect)

        def __handler__(square_):
            num_pawns = square_.num_pawns()
            __draw__()
            if num_pawns > 0:
                player_color = RED if square_.get_player().player_id == 0 else BLUE
                pygame.draw.ellipse(self.screen, player_color, square_rect)
                if num_pawns > 1:
                    self.__draw_text__(square_rect, str(num_pawns))
            self.rectangle_list.append(square_rect)
        return __handler__

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((GameGUI.WIDTH, GameGUI.WIDTH))
        self.screen.fill(WHITE)
        pygame.display.set_caption('Ludo Game')
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font('freesansbold.ttf', GameGUI.BOX_WIDTH // 2)
        self.game_loop = True
        self.rectangle_list = []
        """ positions are list of (top, left) pairs """
        box_width, num_boxes, total_boxes = GameGUI.BOX_WIDTH, GameGUI.NUM_BOXES, GameGUI.TOTAL_BOXES
        self.square_pos = [(num_boxes + 2, total_boxes - i - 1) for i in range(num_boxes)] \
            + [(num_boxes + 3 + i, num_boxes + 2) for i in range(num_boxes)] \
            + [(total_boxes - 1 - i,  num_boxes) for i in range(num_boxes)] \
            + [(num_boxes + 2, num_boxes - i - 1) for i in range(num_boxes)] \
            + [(num_boxes, i) for i in range(num_boxes)] \
            + [(num_boxes - 1 - i, num_boxes) for i in range(num_boxes)] \
            + [(i, num_boxes + 2) for i in range(num_boxes)] \
            + [(num_boxes,  num_boxes + 3 + i) for i in range(num_boxes)]
        self.hub_square_pos = [(num_boxes + 1, total_boxes - 1), (total_boxes - num_boxes, total_boxes - num_boxes),
                               (total_boxes - 1, num_boxes + 1), (total_boxes - num_boxes, num_boxes - 1),
                               (num_boxes + 1, 0), (num_boxes - 1, num_boxes - 1),
                               (0, num_boxes + 1), (num_boxes - 1, total_boxes - num_boxes)]
        self.start_home_square_pos = [[(num_boxes + 1, total_boxes - num_boxes + i) for i in range(num_boxes - 1)],
                                      [(num_boxes + 1, num_boxes - i - 1) for i in range(num_boxes - 1)]]

        self.end_home_square_pos = [[(num_boxes - 1, total_boxes - i - 1) for i in range(num_boxes - 1)]
                                    + [(num_boxes-2, total_boxes - num_boxes + 1)],
                                    [(total_boxes - num_boxes, i) for i in range(num_boxes - 1)]
                                    + [(total_boxes - num_boxes + 1, num_boxes-2)]]
        self.dice_pos = [(total_boxes - 4, total_boxes - 4), (1, 1)]
        self.game = Game()
        self.game.register_dice_roll_handler(self.__draw_dice__)
        for i in range(self.game.NUM_PLAYERS):
            self.game.players[i].register_pawn_status_change_handler(self.__draw_player__(self.game.players[i]))
        assert len(self.square_pos) == len(self.game.board.squares)
        for index_, square_ in enumerate(self.game.board.squares):
            left, top = self.square_pos[index_]
            square_.register_handler(self.__square__(left, top, Square))
        for index_, hub_square_ in enumerate(self.game.board.hub_squares):
            left, top = self.hub_square_pos[index_]
            hub_square_.register_handler(self.__square__(left, top, HubSquare))
        for i in range(self.game.NUM_PLAYERS):
            player_squares_ = self.game.board.player_squares[i]
            for j in range(self.game.board.NUM_START_SQUARES):
                home_square_ = player_squares_[j]
                left, top = self.start_home_square_pos[i][j]
                assert isinstance(home_square_, HomeSquare)
                home_square_.register_handler(self.__square__(left, top, HomeSquare, True))
            for j in range(self.game.board.NUM_END_SQUARES):
                home_square_ = player_squares_[-self.game.board.NUM_END_SQUARES:][j]
                left, top = self.end_home_square_pos[i][j]
                assert isinstance(home_square_, HomeSquare)
                home_square_.register_handler(self.__square__(left, top, HomeSquare, False))

    def loop(self):
        game_done = False
        while self.game_loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
            if not self.game_loop:
                break
            #
            # for left, top in self.square_pos:
            #     print(left, top)
            #     pygame.draw.rect(self.screen, BLACK, (left * GameGUI.BOX_WIDTH, top * GameGUI.BOX_WIDTH, GameGUI.BOX_WIDTH, GameGUI.BOX_WIDTH))
            # for left, top in self.hub_square_pos:
            #     pygame.draw.rect(self.screen, RED, (
            #     left * GameGUI.BOX_WIDTH, top * GameGUI.BOX_WIDTH, GameGUI.BOX_WIDTH, GameGUI.BOX_WIDTH))
            # for i in range(2):
            #     for left, top in self.start_home_square_pos[i]:
            #         pygame.draw.rect(self.screen, BLUE, (
            #             left * GameGUI.BOX_WIDTH, top * GameGUI.BOX_WIDTH, GameGUI.BOX_WIDTH, GameGUI.BOX_WIDTH))
            # for i in range(2):
            #     for left, top in self.end_home_square_pos[i]:
            #         pygame.draw.rect(self.screen, BLUE, (
            #             left * GameGUI.BOX_WIDTH, top * GameGUI.BOX_WIDTH, GameGUI.BOX_WIDTH, GameGUI.BOX_WIDTH))
            # self.__draw_dice__(0, (1, 0))
            # self.__draw_dice__(1, (3, 2))
            # pygame.display.flip()
            if not game_done:
                game_done = self.game.game_step()
            pygame.display.update(self.rectangle_list)
            self.rectangle_list = []
            self.clock.tick(GameGUI.FPS)

    def quit(self):
        self.game_loop = False
        pygame.quit()


gui = GameGUI()
gui.loop()
