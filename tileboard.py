import random
import copy
import math

from basicsearch_lib.board import Board

class TileBoard(Board):
    def __init__(self, n, multiple_solutions=False, force_state=None,
                 verbose=False):
        """"TileBoard(n, multiple_solutions
        Create a tile board for an n puzzle.
        
        If multipleSolutions are true, the solution need not
        have the space in the center.  This defaults to False but
        is automatically set to True when there is no middle square 
        
        force_state can be used to initialize an n puzzle to a desired
        configuration.  No error checking is done.  It is specified as
        a list with n+1 elements in it, 1:n and None in the desired order.

        verbose is a boolean for turning on debugging
        """
        
        self.verbose = verbose  # not debug state, up to you to use it
        self.boardsize = int(math.sqrt(n+1))
        
        if math.sqrt(n+1) != self.boardsize:
            raise ValueError("Bad board size\n" + "Must be one less than an odd perfect square 8, 24, ...")

        # initialize parent
        super().__init__(self.boardsize, self.boardsize)

        # Compute solution states
        # todo:  Set self.goals to a list of solution tuples
        # If multiple_solutions is true, None can be anywhere:
        if multiple_solutions is True:
            self.goals = []
            
            #Populate the solution list with None in every index position with the tiles in ascending order.
            none_index = 0 #Keep track where to insert the "empty" None tile.
            for i in range(n+1): 
                solution_list = []
                for j in range(1, n+1): #Start from one, not zero tile.
                    solution_list.append(j)
                solution_list.insert(none_index, None)
                self.goals.append(tuple(solution_list))
                none_index += 1 #Insert the None tile at the next index position of the next solution tuple.
                # [(None,1,2,3,...), (1,None,2,3,...), (1,2,None,3,...)]
        else:
            self.goals = [(1,2,3,4,5,6,7,8, None)]
            # Otherwise, must be the last square:  [(1,2,3,...,None)]

        # todo:  Determine inital state and make sure that it is solvable
        self.board_representation = []
    
        if force_state is None:
            solvable = False
            while solvable is False:
            
                self.board_representation = []
                element_sublist_index = 0
            
                for i in range(self.boardsize):
                    sublist = []
                    for j in range(self.boardsize):
                        sublist.append(element_sublist_index)
                        element_sublist_index += 1
                    self.board_representation.append(sublist)
                self.board_representation[0][0] = None
            
                self.row_of_none = 0
                self.column_of_none = 0
            
                random.shuffle(self.board_representation)
            
                for sublist in self.board_representation:
                    random.shuffle(sublist)
                solvable = self.solvable(self.state_tuple())
            
            if force_state is not None:
                
                if not self.solvable(force_state):
                    raise ValueError("Specific forced puzzle configuration is not solvable!")
                
                list_index = 0
            
                for i in range(self.boardsize):
                    sublist = []
                    for j in range(self.boardsize):
                        sublist.append(force_state[list_index])
                        list_index = list_index + 1
                    self.board_representation.append(sublist)
                
            for row in self.board_representation:
                if None in row:
                    self.row_of_none = self.board_representation.index(row)
                    self.column_of_none = row.index(None)
            
            for row in range(self.boardsize):
                for column in range(self.boardsize):
                    self.place(row, column, self.board_representation[row][column])
                    
    
    
    
    
    
        # todo:  Populate the board using self.place
        #        It would be wise to track the empty square location as well
        #        as it will make action generation easier

    def solvable(self, tiles, verbose=False):
        """solvable - Determines if a puzzle is solvable

            Given a list of tiles, determine if the N-puzzle is solvable.
            You do not need to know how to do this, but the calculation
            is based on the inversion order.

            for each number in the list of tiles,
               How many following numbers are less than that one
               e.g. [13, 10, 11, 6, 5, 7, 4, 8, 1, 12, 14, 9, 3, 15, 2, None]
               Example:  Files following 9:  [3, 15, 2, None]
               Two of these are smaller than 9, so the inversion order
                   for 9 is 2

            A puzzle's inversion order is the sum of the tile inversion
            orders.  For puzzles with even numbers of rows and columns,
            the row number on which the blank resides must be added.
            Note that we need not worry about 1 as there are
            no tiles smaller than one.

            See Wolfram Mathworld for further explanation:
                http://mathworld.wolfram.com/15Puzzle.html
            and http://www.cut-the-knot.org/pythagoras/fifteen.shtml

            This lets us know if a problem can be solved.  The inversion
            order modulo 2 is invariant across moves.  This means that
            when we make a legal move, the inversion order will always
            be even or odd.  The solution state always has an even
            inversion order, so any puzzle with an odd inversion
            number cannot be solved.
        """

        inversionorder = 0
        # Make life easy, remove None
        reduced = [t for t in tiles if t is not None]
        # Loop over all but last (no tile after it)
        for idx in range(len(reduced)-1):
            value = reduced[idx]
            after = reduced[idx+1:]  # Remaining tiles
            smaller = [x for x in after if x < value]
            numtiles = len(smaller)
            inversionorder = inversionorder + numtiles
            if verbose:
                print("idx {} value {} tail {} #smaller {} sum: {}".format(
                    idx, value, after, numtiles, inversionorder))

        # Even number of rows must take the blank position into account
        if self.get_rows() % 2 == 0:
            if verbose:
                print("Even # rows, adding for position of blank")
            inversionorder = inversionorder + \
                math.floor(tiles.index(None) / self.boardsize)+1

        solvable = inversionorder % 2 == 0  # Solvable if even
        return solvable
                                
    def __hash__(self):
        "__hash__ - Hash the board state"
        
        # Convert state to a tuple and hash
        return hash(self.state_tuple())
    
    def __eq__(self, other):
        "__eq__ - Check if objects equal:  a == b"

        return self.state_tuple() == other
    
        #raise NotImplementedError("Check ==")

    def state_tuple(self):
        "state_tuple - Return board state as a single tuple"

        list_to_tuple = []
        for sublist in self.board_representation:
            for element in sublist:
                list_to_tuple.append(element)
            return tuple(list_to_tuple)

        #raise NotImplementedError(
        #    "You must create a tuple based on the board state")

    def get_actions(self):
        "Return row column offsets of where the empty tile can be moved"
        
        list_of_actions = []
        
        # Check if any of the 4 possible directions are valid to move.
        if self.row_of_none - 1 >= 0:
            list_of_actions.append([-1,0])
        if self.row_of_none + 1 < 0:
            list_of_actions.append([1,0])
        if self.column_of_none - 1 >= 0:
            list_of_actions.append([0,-1])
        if self.column_of_none - 1 < 0:
            list_of_actions.append([0,1])    
        
        # Return a list of valid actions.
        return list_of_actions
        
        
        #raise NotImplementedError("Return list of valid actions")

            
    def move(self, offset):
        "move - Move the empty space by [delta_row, delta_col] and return new board"

        row_offset = offset[0]
        column_offset = offset[1]

        new_board = copy.deepcopy(self) # Make a "deepcopy" of the "old" board.
    
    
        switch_value = new_board.get(new_board.row_of_none + row_offset, new_board.column_of_none + column_offset)
        
        new_board.place(new_board.row_of_none + row_offset,new_board.column_of_none+column_offset, None)
        new_board.board_representation[new_board.row_of_none + row_offset][new_board.column_of_none + column_offset] = None

        new_board.place(new_board.row_of_none, new_board.column_of_none, switch_value)
        new_board.board_representation[new_board.row_of_none][new_board.column_of_none] = switch_value
    
        
        return new_board
        
    

    
    
    
    
    
    

        # Hint:  Be sure to use deepcopy
        #raise NotImplementedError("Return new TileBoard with action applied")

    
    def solved(self):
        "solved - Is the puzzle solved?  Returns boolean"
        solved_variable = False
        for solution_tuple in self.goals:
            if self.__eq__(solution_tuple):
                solved_variable = True
        return solved_variable
    
    
        #raise NotImplementedError("Puzzle in solved state?")
