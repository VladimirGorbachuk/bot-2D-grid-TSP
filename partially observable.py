import itertools as it
from collections import deque, namedtuple
import random #? should we?
import re #I think, it's not necessary


class Matrix_Bot_Dirt():
    '''
    here we define everything but optimal sequence:
    '''

    def __init__(self, rows=5, cols=5, bot_row=None, bot_col=None):
        
        self.matrix_rows = rows
        self.matrix_cols = cols
        
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
        for row in self.matrix_rows:
            new_matrix_view.append([symbol for symbol in input().split()])
        
        if old_matrix_view:
            for row in self.matrix_rows:
                for col in self.matrix_cols:
                    if new_matrix_view[row][col] == "o": 
                        new_matrix_view[row][col] = old_matrix_view[row][col] 
        
        return new_matrix_view
    def __read_matrix_file(self):
        try:
            old_matrix_view = []
            with open(self.tmp_matrix_filename, "r") as f:
                for row in self.matrix_rows:
                    old_matrix_view.append([symbol for symbol in f.readline()])
        except FileNotFoundError:
            old_matrix_view = []   #I intentionally repeat  setting as empty list, for clarity
    
    def.__write_matrix_to_file(self,new_matrix_view):
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
        old_matrix_view = self.__read_matrix_file()
        new_matrix_view = self.__update_matrix(old_matrix_view)
        self.__write_matrix_to_file(new_matrix_view)
        return new_matrix_view
    
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
            self.__dirt_coords = tuple(self._dirt_coords)
            return self.__dirt_coords
        
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
    def waypoints_coords(self):
        try:
            return self.__waypoints_coords
        except AttributeError:
            self.__unknown_coords.sort(key=self.calc_distance(self.bot_coords,key))
            self.__unknown_coords = deque(self.__unknown_coords)
            while self.__unknown_coords:
                first_coord_to_include = self.__unknown_coords.popleft()
                
                

    def calc_distance(self, node_1_coords, node_2_coords):
        distance = abs(node_1_coords[0] - node_2_coords[0]) + abs(node_1_coords[1] - node_2_coords[1])
        return distance

    def define_optimal_sequence(self):
        raise NotImplementedError

    def make_a_turn(self):
        """
        main possible pitfall - the file with coords sequence (if not renamed properly) - can already exist
        """

        target_dirt_coords = self.choose_target_dirt()
        
        if self.bot_coords == target_dirt_coords:
            print("CLEAN")
            self.remove_cleaned_dirt()

        elif target_dirt_coords[0] > self.bot_coords[0]:
                print("DOWN")
        elif target_dirt_coords[0] < self.bot_coords[0]:
                print("UP")
        elif target_dirt_coords[1] > self.bot_coords[1]:
                print("RIGHT")
        else:
                print("LEFT")
        
    def choose_target_dirt(self):
            try:
                with open(self.tmp_filename, "r") as f:
                    txt_optimal_sequence = f.read()
                    optimal_sequence = self.txt_to_tuple(txt_optimal_sequence)

            except FileNotFoundError:
                optimal_sequence = self.define_optimal_sequence()

                with open(self.tmp_filename, "w+") as f:
                    f.write(str(optimal_sequence))
            return optimal_sequence[0]
        
    def remove_cleaned_dirt(self):
            with open(self.tmp_filename, "r") as f:
                optimal_sequence = self.txt_to_tuple(f.read())
                optimal_sequence.pop(0)

            with open(self.tmp_filename, "w+") as f:
                f.write(str(optimal_sequence))

    def txt_to_tuple(self,txt_optimal_sequence):

            single_txt_tuples = re.findall(r'(\d+,\s*\d+)', txt_optimal_sequence)

            int_tuple_list = []
            for txt_tuple in single_txt_tuples:
                substituted_txt_tuple = re.sub(r',\s', ' ', txt_tuple)
                int_tuple = tuple([int(num) for num in substituted_txt_tuple.split()])
                int_tuple_list.append(int_tuple)

            return(int_tuple_list)
        
    def calculate_distance_for_seq(self, sequence=None):

        total_distance = self.calc_distance(self.bot_coords, sequence[0])
        for index, element in enumerate(sequence[:-1]):
            total_distance += self.calc_distance(sequence[index], sequence[index + 1])
        return total_distance

    

[bot_row, bot_col] = [int(coord) for coord in input().split()]

bot_solve = Matrix_Bot_Dirt(bot_row=bot_row, bot_col=bot_col)
bot_solve.make_a_turn()
