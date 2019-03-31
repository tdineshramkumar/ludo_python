from squares import Square, HubSquare, HomeSquare


class Board:
    NUM_SQUARES = 48
    NUM_HUB_SQUARES = 8
    NUM_START_SQUARES = 5
    NUM_END_SQUARES = 6
    NUM_CONSTRAINED_SQUARES = 54

    def __init__(self, num_players):
        assert num_players > 0
        assert Board.NUM_SQUARES % Board.NUM_HUB_SQUARES == 0
        self.num_players = num_players
        self.squares = [Square() for _ in range(Board.NUM_SQUARES)]
        self.hub_squares = [HubSquare() for _ in range(Board.NUM_HUB_SQUARES)]
        self.player_squares = []
        for player_id in range(num_players):
            player_track = []
            self.player_squares.append(player_track)
            player_track.extend([HomeSquare() for _ in range(Board.NUM_START_SQUARES)])
            for i in range(Board.NUM_SQUARES):
                if not i % (Board.NUM_SQUARES / Board.NUM_HUB_SQUARES):
                    player_track.append(self.hub_squares[(i // int(Board.NUM_SQUARES / Board.NUM_HUB_SQUARES) +
                                                          player_id * Board.NUM_HUB_SQUARES // num_players)
                                                         % Board.NUM_HUB_SQUARES])
                player_track.append(self.squares[(i + player_id * Board.NUM_SQUARES // num_players)
                                                 % Board.NUM_SQUARES])
            player_track.extend([HomeSquare() for _ in range(Board.NUM_END_SQUARES)])
            assert len(player_track) == Board.NUM_SQUARES + Board.NUM_HUB_SQUARES + \
                Board.NUM_START_SQUARES + Board.NUM_END_SQUARES

    def get_player_track(self, player_id: int):
        assert 0 <= player_id < self.num_players
        return self.player_squares[player_id]





