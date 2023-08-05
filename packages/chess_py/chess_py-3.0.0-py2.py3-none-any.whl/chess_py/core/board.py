# -*- coding: utf-8 -*-

"""
Constructs board object which stores the get_location of all the pieces.

Default Array

| [[0th row 0th item,  0th row 1st item,  0th row 2nd item],
|  [1st row 0th item,  1st row 1st item,  1st row 2nd item],
|  [2nd row 0th item, 2nd row 1st item,  2nd row 2nd item]]

| Default board
| 8 ║♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ Black pieces
| 7 ║♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟ Black pawns
| 6 ║a6… … … … … …h6
| 5 ║… … … … … … … …
| 4 ║… … … … … … … …
| 3 ║a3… … … … … …h3 Algebraic
| 2 ║♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙ White pawns
| 1 ║♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖ White pieces
| -—╚═══════════════
| ——-a b c d e f g h

Pieces on the board are flipped in position array so white home row is at index 0
and black home row is at index 7

| Copyright © 2016 Aubhro Sengupta. All rights reserved.
"""

from __future__ import print_function

import inspect
from multiprocessing import Process
from copy import copy as cp
from math import fabs

from .color import white, black
from .algebraic import notation_const
from .algebraic.location import Location
from .algebraic.move import Move
from ..pieces.piece import Piece
from ..pieces.bishop import Bishop
from ..pieces.king import King
from ..pieces.pawn import Pawn
from ..pieces.queen import Queen
from ..pieces.rook import Rook
from ..pieces.knight import Knight


class Board:
    """
    Standard starting position in a chess game.
    Initialized upon startup and is used when init_default constructor is used

    """

    def __init__(self, position):
        """
        Creates a ``Board`` given an array of ``Piece`` and ``None``
        objects to represent the given position of the board.

        :type: position: list
        """
        self.position = position
        self.possible_moves = dict()
        try:
            self.king_loc_dict = {white: self.find_king(white),
                                  black: self.find_king(black)}
        except ValueError:
            self.king_loc_dict = None

    @classmethod
    def init_default(cls):
        """
        Creates a ``Board`` with the standard chess starting position.

        :rtype: Board
        """
        return cls([

            # First rank
            [Rook(white, Location(0, 0)), Knight(white, Location(0, 1)), Bishop(white, Location(0, 2)),
             Queen(white, Location(0, 3)), King(white, Location(0, 4)), Bishop(white, Location(0, 5)),
             Knight(white, Location(0, 6)), Rook(white, Location(0, 7))],

            # Second rank
            [Pawn(white, Location(1, file)) for file in range(8)],

            # Third rank
            [None for _ in range(8)],

            # Fourth rank
            [None for _ in range(8)],

            # Fifth rank
            [None for _ in range(8)],

            # Sixth rank
            [None for _ in range(8)],

            # Seventh rank
            [Pawn(black, Location(6, file)) for file in range(8)],

            # Eighth rank
            [Rook(black, Location(7, 0)), Knight(black, Location(7, 1)), Bishop(black, Location(7, 2)),
             Queen(black, Location(7, 3)), King(black, Location(7, 4)), Bishop(black, Location(7, 5)),
             Knight(black, Location(7, 6)), Rook(black, Location(7, 7))]
        ])

    @property
    def position_tuple(self):
        return ((str(piece) for piece in self.position[index]) for index, row in enumerate(self.position))

    def __key(self):
        return self.position

    def __hash__(self):
        return hash(tuple([hash(piece) for piece in self]))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Cannot compare other type to Board")

        for i, row in enumerate(self.position):
            for j, piece in enumerate(row):

                if piece != other.position[i][j]:
                    return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        board_string = ""
        for i, row in enumerate(self.position):
            board_string += str(8 - i) + " "
            for j, square in enumerate(row):

                piece = self.piece_at_square(Location(7 - i, j))
                if isinstance(piece, Piece):
                    board_string += piece.symbol + " "
                else:
                    board_string += "_ "

            board_string += "\n"

        board_string += "  a b c d e f g h"
        return board_string

    def __iter__(self):
        for row in self.position:
            for square in row:
                yield square

    def __copy__(self):
        """
        Copies the board faster than deepcopy

        :rtype: Board
        """
        return Board([[cp(piece) or None
                       for piece in self.position[index]]
                      for index, row in enumerate(self.position)])

    def piece_at_square(self, location):
        """
        Finds the chess piece at a square of the position.

        :type: location: Location
        :rtype: Piece
        """
        return self.position[location.rank][location.file]

    def is_square_empty(self, location):
        """
        Finds whether a chess piece occupies a square of the position.

        :type: location: Location
        :rtype: bool
        """
        return self.position[location.rank][location.file] is None

    def material_advantage(self, input_color, val_scheme):
        """
        Finds the advantage a particular side possesses given a value scheme.

        :type: input_color: Color
        :type: val_scheme: PieceValues
        :rtype: double
        """

        if self.get_king(input_color).in_check(self) and self.no_moves(input_color):
            return -100

        if self.get_king(input_color.opponent()).in_check(self) and self.no_moves(input_color.opponent()):
            return 100

        return sum([val_scheme.val(piece, input_color) for piece in self])

    def advantage_as_result(self, move, val_scheme):
        """
        Calculates advantage after move is played

        :type: move: Move
        :type: val_scheme: PieceValues
        :rtype: double
        """
        test_board = cp(self)
        test_board.update(move)
        return test_board.material_advantage(move.color, val_scheme)

    def all_possible_moves(self, input_color):
        """
        Checks if all the possible moves has already been calculated
        and is stored in `possible_moves` dictionary. If not, it is calculated
        with `_calc_all_possible_moves`.
        
        :type: input_color: Color
        :rtype: list
        """
        position_tuple = self.position_tuple
        if position_tuple not in self.possible_moves:
            self.possible_moves[position_tuple] = tuple(self._calc_all_possible_moves(input_color))

        return self.possible_moves[position_tuple]

    def _calc_all_possible_moves(self, input_color):
        """
        Returns list of all possible moves

        :type: input_color: Color
        :rtype: list
        """
        for piece in self:

            # Tests if square on the board is not empty
            if piece is not None and piece.color == input_color:

                for move in piece.possible_moves(self):

                    test = cp(self)
                    test_move = Move(end_loc=move.end_loc,
                                     piece=test.piece_at_square(move.start_loc),
                                     status=move.status,
                                     start_loc=move.start_loc)
                    test.update(test_move)

                    if self.king_loc_dict is None:
                        yield move
                        continue

                    my_king = test.piece_at_square(self.king_loc_dict[input_color])

                    if my_king is None or \
                            not isinstance(my_king, King) or \
                            my_king.color != input_color:
                        self.king_loc_dict[input_color] = test.find_king(input_color)
                        my_king = test.piece_at_square(self.king_loc_dict[input_color])

                    if not my_king.in_check(test):
                        yield move

    def runInParallel(*fns):
        """
        Runs multiple processes in parallel.

        :type: fns: def
        """
        proc = []
        for fn in fns:
            p = Process(target=fn)
            p.start()
            proc.append(p)
        for p in proc:
            p.join()

    def no_moves(self, input_color):

        # Loops through columns
        for piece in self:

            # Tests if square on the board is not empty
            if piece is not None and piece.color == input_color:

                for move in piece.possible_moves(self):

                    test = cp(self)
                    test.update(move)

                    if not test.get_king(input_color).in_check(test):
                        return False

        return True

    def find_piece(self, piece):
        """
        Finds Location of the first piece that matches piece.
        If none is found, Exception is raised.

        :type: piece: Piece
        :rtype: Location
        """
        for i, _ in enumerate(self.position):
            for j, _ in enumerate(self.position):
                loc = Location(i, j)

                if not self.is_square_empty(loc) and \
                        self.piece_at_square(loc) == piece:
                    return loc

        raise ValueError("{} \nPiece not found: {}".format(self, piece))

    def get_piece(self, piece_type, input_color):
        """
        Gets location of a piece on the board given the type and color.
        
        :type: piece_type: Piece
        :type: input_color: Color 
        :rtype: Location
        """
        for loc in self:
            piece = self.piece_at_square(loc)

            if not self.is_square_empty(loc) and \
                    isinstance(piece, piece_type) and \
                    piece.color == input_color:
                return loc

        raise Exception("{} \nPiece not found: {}".format(self, piece_type))

    def find_king(self, input_color):
        """
        Finds the Location of the King of input_color

        :type: input_color: Color
        :rtype: Location
        """
        return self.find_piece(King(input_color, Location(0, 0)))

    def get_king(self, input_color):
        """
        Returns King of input_color

        :type: input_color: Color
        :rtype: King
        """
        return self.piece_at_square(self.find_king(input_color))

    def remove_piece_at_square(self, location):
        """
        Removes piece at square

        :type: location: Location
        """
        self.position[location.rank][location.file] = None

    def place_piece_at_square(self, piece, location):
        """
        Places piece at given get_location

        :type: piece: Piece
        :type: location: Location
        """
        self.position[location.rank][location.file] = piece
        piece.location = location

    def move_piece(self, initial, final):
        """
        Moves piece from one location to another

        :type: initial: Location
        :type: final: Location
        """
        self.place_piece_at_square(self.piece_at_square(initial), final)
        self.remove_piece_at_square(initial)

    def update(self, move):
        """
        Updates position by applying selected move

        :type: move: Move
        """
        if move is None:
            raise TypeError("Move cannot be type None")

        if self.king_loc_dict is not None and isinstance(move.piece, King):
            self.king_loc_dict[move.color] = move.end_loc

        # Invalidates en-passant
        for square in self:
            pawn = square
            if isinstance(pawn, Pawn):
                pawn.just_moved_two_steps = False

        # Sets King and Rook has_moved property to True is piece has moved
        if type(move.piece) is King or type(move.piece) is Rook:
            print('caller name:', inspect.stack()[1][3])
            move.piece.has_moved = True

        elif move.status == notation_const.MOVEMENT and \
                isinstance(move.piece, Pawn) and \
                fabs(move.end_loc.rank - move.start_loc.rank) == 2:
            move.piece.just_moved_two_steps = True

        if move.status == notation_const.KING_SIDE_CASTLE:
            self.move_piece(Location(move.end_loc.rank, 7), Location(move.end_loc.rank, 5))
            self.piece_at_square(Location(move.end_loc.rank, 5)).has_moved = True

        elif move.status == notation_const.QUEEN_SIDE_CASTLE:
            self.move_piece(Location(move.end_loc.rank, 0), Location(move.end_loc.rank, 3))
            self.piece_at_square(Location(move.end_loc.rank, 3)).has_moved = True

        elif move.status == notation_const.EN_PASSANT:
            self.remove_piece_at_square(Location(move.start_rank, move.end_loc.file))

        elif move.status == notation_const.PROMOTE or \
                move.status == notation_const.CAPTURE_AND_PROMOTE:
            self.remove_piece_at_square(Location(move.start_rank, move.start_file))
            self.place_piece_at_square(move.promoted_to_piece(move.color, move.end_loc), move.end_loc)
            return

        self.move_piece(move.piece.location, move.end_loc)
