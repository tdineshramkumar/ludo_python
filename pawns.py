class Pawn:
    BEGIN = 0
    PROGRESS = 1
    COMPLETE = 2

    def __init__(self, player, num_squares, constrained_num_squares):
        """ Initialize a Pawn with a player and number of total squares on the track,
            Initially pawn at BEGIN state and cannot be updated unless 'started'. Then on updating position,
            Pawn moves till end of track, one more step results in completion.
         """
        self.player = player
        self.status = Pawn.BEGIN
        self.position = 0
        self.num_squares = num_squares
        """ Constrained initial squares, the constraint is removed after first kill """
        self.constrained = True
        self.constrained_num_squares = constrained_num_squares

    def get_player(self):
        return self.player

    def yet_to_start(self):
        return  self.status == Pawn.BEGIN

    def is_complete(self):
        return self.status == Pawn.COMPLETE

    def in_progress(self):
        return self.status == Pawn.PROGRESS

    def reset(self):
        """ Send the pawn back to beginning state, this is called when invaded by opponent """
        self.status = Pawn.BEGIN

    def start(self):
        """ Call this to change state to progress """
        assert self.yet_to_start()
        self.status = Pawn.PROGRESS
        self.position = 0

    def on_last_square(self, num_steps=0):
        """ Returns true if it's last square after num_steps, ie, on more to completion """
        return self.position + num_steps == self.num_squares - 1

    def can_complete(self, num_steps):
        """ Returns true if it can complete after num_steps """
        return self.position + num_steps == self.num_squares

    def can_update(self, num_steps):
        if self.status != Pawn.PROGRESS:
            " Status must be progress for update "
            return False
        """ Not only can move till constraint squares"""
        if self.position + num_steps <= self.constrained_num_squares:
            " If after num_steps, well within range "
            return True
        return False

    def update_player_constraint(self):
        """ This function resets the constraint to maximum, so that pawn can proceed,
        call this function after a kill """
        if self.constrained:
            """ propagate it once only """
            print("------------------------------------------\n" * 3)
            print("PLAYER CONSTRAINT REMOVED !!!")
            print("------------------------------------------\n" * 3)
            self.player.remove_constraints()
            # self.constrained_num_squares = self.num_squares
            # self.constrained = False

    def remove_constraint(self):
        """ This function is called by the player """
        print("PAWN CONSTRAINT REMOVED")
        self.constrained_num_squares = self.num_squares
        self.constrained = False

    def update(self, num_steps):
        assert self.can_update(num_steps)
        # assert num_steps > 0
        " Update the position with num_squares "
        self.position += num_steps
        if self.position == self.num_squares:
            self.status = Pawn.COMPLETE

    def get_position(self, num_steps=0):
        return self.position + num_steps

    def get_remaining(self):
        """ Returns the maximum number of steps the pawn can proceed, may be used later  """
        return self.num_squares - self.position

    def __repr__(self):
        if self.status == Pawn.BEGIN:
            return 'Pawn{BEGIN}'
        elif self.status == Pawn.PROGRESS:
            return 'Pawn{PROGRESS, %d/%d}' % (self.position, self.num_squares)
        else:
            return 'Pawn{COMPLETE}'
