class AbstractSquare:
    def __init__(self):
        self.on_change_handler = None

    def register_handler(self, handler):
        """ This function is used to register an onchange handler which will be called
        on completion of add_pawn and remove_pawn to indicate any change """
        self.on_change_handler = handler

    def call_change_handler(self):
        if self.on_change_handler:
            self.on_change_handler(self)

    def can_add_pawn(self, pawn):
        raise NotImplementedError("can_add_pawn not implemented")

    def can_score(self, pawn):
        raise NotImplementedError("can_score not implemented")

    def add_pawn(self, pawn):
        raise NotImplementedError("add_pawn not implemented")

    def remove_pawn(self, pawn):
        raise NotImplementedError("remove_pawn not implemented")

    def can_support_multiple_elements(self):
        raise NotImplementedError("can_support_multiple_elements not implemented")

    def num_pawns(self):
        raise NotImplementedError("num_pawns not implemented")

    def get_player(self):
        raise NotImplementedError("get_player not implemented")


class Square(AbstractSquare):
    def __init__(self):
        AbstractSquare.__init__(self)
        self.pawn = None

    def can_add_pawn(self, pawn):
        if not self.pawn:
            return True
        else:
            " If occupied by the pawn of same player, then deny placement "
            if self.pawn.get_player() == pawn.get_player():
                return False
            else:
                return True

    def can_score(self, pawn):
        """ Used to check if an opponent pawn will be replaced """
        if not self.pawn:
            return False
        else:
            if self.pawn.get_player() == pawn.get_player():
                return False
            else:
                return True

    def add_pawn(self, pawn):
        assert self.can_add_pawn(pawn)
        if not self.pawn:
            " If no existing pawn, the set the pawn "
            self.pawn = pawn
        else:
            " If occupied by the pawn of same player, then deny placement "
            assert self.pawn.get_player() != pawn.get_player()

            " If different player, then reset the other pawn "
            print('Pawn got reset:', self.pawn, 'attacker:', pawn)
            self.pawn.reset()
            """ So its best to update player segregation of pawns """
            self.pawn.get_player().__separate_pawns_on_status__()
            self.pawn = pawn
        """ Call event handler """
        self.call_change_handler()

    def remove_pawn(self, pawn):
        assert self.pawn == pawn
        self.pawn = None
        """ Call event handler """
        self.call_change_handler()

    def can_support_multiple_elements(self):
        return False

    def num_pawns(self):
        return 1 if self.pawn else 0

    def get_player(self):
        if self.pawn:
            return self.pawn.get_player()
        return None

    def __repr__(self):
        return 'Square[%d]' % id(self)


class HubSquare(AbstractSquare):
    def __init__(self):
        AbstractSquare.__init__(self)
        self.player = None
        self.pawns = []

    def can_add_pawn(self, pawn):
        if not self.player:
            return True
        else:
            if self.player == pawn.get_player():
                return True
            else:
                return False

    def can_score(self, pawn):
        return False

    def add_pawn(self, pawn):
        assert self.can_add_pawn(pawn)
        if not self.player:
            assert not self.pawns
            self.player = pawn.get_player()
            self.pawns = [pawn]
        else:
            assert self.pawns
            assert self.player == pawn.get_player()
            "If occupied by pawn of same player, just append to list"
            self.pawns.append(pawn)
        """ Call event handler """
        self.call_change_handler()

    def remove_pawn(self, pawn):
        assert pawn in self.pawns
        self.pawns.remove(pawn)
        if not self.pawns:
            " If no more pawns, then it does not belong to player "
            self.pawns = []
            self.player = None
        """ Call event handler """
        self.call_change_handler()

    def can_support_multiple_elements(self):
        return True

    def num_pawns(self):
        return len(self.pawns)

    def get_player(self):
        return self.player

    def __repr__(self):
        return 'HubSquare[%d]' % id(self)


class HomeSquare(AbstractSquare):
    """ Add pawns of the same player """
    def __init__(self):
        AbstractSquare.__init__(self)
        self.pawns = []

    def can_add_pawn(self, pawn):
        return True

    def can_score(self, pawn):
        return False

    def add_pawn(self, pawn):
        self.pawns.append(pawn)
        """ Call event handler """
        self.call_change_handler()

    def remove_pawn(self, pawn):
        assert pawn in self.pawns
        self.pawns.remove(pawn)
        """ Call event handler """
        self.call_change_handler()

    def can_support_multiple_elements(self):
        return True

    def num_pawns(self):
        return len(self.pawns)

    def get_player(self):
        if self.pawns:
            return self.pawns[0].get_player()
        return None

    def __repr__(self):
        return 'HomeSquare[%d]' % id(self)


""" Square does not support two pieces in one block, as it only adds a pawn, not two """
