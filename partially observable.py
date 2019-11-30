import itertools as it
from collections import deque, namedtuple

class Matrix_Bot_Dirt():
    '''
    here we define everything but optimal sequence:
    '''

    def __init__(self, rows=5, cols=5, bot_row=None, bot_col=None):
        
        self.matrix_rows = 5
        self.matrix_cols = 5
        
        self.bot_coords = (bot_row, bot_col,)
        
        self.tmp_matrix_filename = "tmp_matrix.txt"
        

    def __update_matrix(self,old_matrix_view):
        """
        bot has limited view, so this reassignment with checking EACH matrix cell is not optimal
        clearly we have to check and update not more than 9 cells (even less, actually)
        but for now I don't see any reason to optimize this step
        I am certain - it's not bottleneck of the program
        """
        #if we've cleaned dirt - we will see it on our next move, so we substitute only unseen cells
        #which are marked with "o"
        new_matrix_view = []
        for row in range(self.matrix_rows):
            new_matrix_view.append([char for char in input()])
        
        if old_matrix_view:
            for row in range(self.matrix_rows):
                for col in range(self.matrix_cols):
                    if new_matrix_view[row][col] == "o": 
                        new_matrix_view[row][col] = old_matrix_view[row][col] 
        
        return new_matrix_view
    
    def __read_matrix_file(self):
        try:
            old_matrix_view = []
            
            with open(self.tmp_matrix_filename, "r") as f:
                for row in range(self.matrix_rows):
                    old_matrix_view.append([symbol for symbol in f.readline()])
            return old_matrix_view        
        except FileNotFoundError:
            old_matrix_view = []   #I intentionally repeat  setting as empty list, for clarity
            return old_matrix_view
    
    def __write_matrix_to_file(self,new_matrix_view):
        with open(self.tmp_matrix_filename, "w+") as f:
            for row in self.matrix:
                string_from_row = row.join(" ")
                f.write(row)
                f.write("\n")
    
    @property
    def matrix(self):
        """
        makes 2D list with 'd' for dirt stains, 'b' for bot, 'o' for unseen cells and '-' for clean cells
        it works with saved tmp file, updating view with no
        """
        try:
            return self.__matrix
        except AttributeError:
            old_matrix_view = self.__read_matrix_file()
            new_matrix_view = self.__update_matrix(old_matrix_view)
            self.__write_matrix_to_file(new_matrix_view)
            self.__matrix = new_matrix_view
            return self.__matrix
    
    @property
    def dirt_coords(self):
        """
        we go row by row, from left to right and collect coordinates of dirt stains
        dirt_coords (which are seen) are already sorted (first by row, then by col)
        """
        try:
            return self.__dirt_coords
        except AttributeError:
            self.__dirt_coords = []
            for row_ind, row in enumerate(self.matrix):
                for col_ind, cell in enumerate(row):
                    if cell == "d":
                        self.__dirt_coords.append((row_ind, col_ind,))
            
            self.__dirt_coords = self._dirt_coords
            return self.__dirt_coords
    
    @property 
    def closest_dirt_coord(self):
        try:
            return self.__closest_dirt_coord
        except AttributeError:
            self.dirt_coords.sort(key=self.calc_distance(self.bot_coords,key))
            self.__closest_dirt_coord = self.dirt_coords[0]
            return self.__closest_dirt_coord
    
    @property
    def unknown_coords(self):
        try:
            return self.__unknown_coords
        except AttributeError:
            self.__unknown_coords = []
            for row_ind, row in enumerate(self.matrix):
                for col_ind,cell in enumerate(row):
                    if cell == "o":
                        self.__unknown_coords.append((row_ind,col_ind,))
            self.__unknown_coords = tuple(self.__unknown_coords)
            return self.__unknown_coords
    
    @property
    def closest_waypoint_coord(self):
        try:
            return self.__closest_waypoint_coord
        except AttributeError:
            self.unknown_coords.sort(key=self.calc_distance(self.bot_coords,key))
            self.__waypoint_coord = self.unknown_coords[0]
            return self.__closest_waypoint_coord

    def calc_distance(self, node_1_coords, node_2_coords):
        distance = abs(node_1_coords[0] - node_2_coords[0]) + abs(node_1_coords[1] - node_2_coords[1])
        return distance

    def make_a_turn(self):

        if (self.calc_distance(self.bot_coords, self.closest_waypoint_coord)
            < self.calc_distance(self.bot_coords, self.closest_dirt_coord)):
            target_coords = self.closest_waypoint_coord
        else:
            target_coords = self.closest_dirt_coord
        
        if self.bot_coords == target_coords:
            print("CLEAN")

        elif target_coords[0] > self.bot_coords[0]:
                print("DOWN")
        elif target_coords[0] < self.bot_coords[0]:
                print("UP")
        elif target_coords[1] > self.bot_coords[1]:
                print("RIGHT")
        else:
                print("LEFT")


[bot_row, bot_col] = [int(coord) for coord in input().split()]

bot_solve = Matrix_Bot_Dirt(bot_row=bot_row, bot_col=bot_col)
bot_solve.make_a_turn()
