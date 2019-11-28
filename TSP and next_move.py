import itertools as it
from collections import deque, namedtuple
import random
from abc import ABC, abstractmethod
import re


class Matrix_Bot_Dirt(ABC):
    '''
    here we define everything but optimal sequence:
    '''

    def __init__(self, rows=None, cols=None, bot_row=None, bot_col=None):
        
        self.matrix_rows = rows
        self.matrix_cols = cols
        
        self.bot_coords = (bot_row, bot_col,)
        
        self.tmp_filename = "tmp_coord_sequence.txt"

    @property
    def matrix(self):
        """
        makes 2D list with 'd' for dirt stains, 'b' for bot and '-' for clean cells
        Works from stdin ONLY!
        """
        try:
            return self._matrix
        except AttributeError:
            self._matrix = []
            for row_ind in range(self.matrix_rows):
                row = [symb for symb in input()]
                assert (len(row) == self.matrix_cols)
                self._matrix.append(row)
            return self._matrix

    @property
    def dirt_coords(self):
        """
        we go row by row, from left to right and collect coordinates of dirt stains
        dirt_coords are already sorted (first by row, then by col)
        """
        try:
            return self._dirt_coords
        except AttributeError:
            self._dirt_coords = []
            for row_ind, row in enumerate(self.matrix):
                for col_ind, cell in enumerate(row):
                    if cell == "d":
                        self._dirt_coords.append((row_ind, col_ind,))
            self._dirt_coords = tuple(self._dirt_coords)
            return self._dirt_coords

    def calc_distance(self, node_1_coords, node_2_coords):
        distance = abs(node_1_coords[0] - node_2_coords[0]) + abs(node_1_coords[1] - node_2_coords[1])
        return distance

    @abstractmethod
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

    
class OptimizedBotClean(Matrix_Bot_Dirt):
    '''
    this class is collection of methods for optimizing sequence of coords for bot to pass
    '''

    
    
    def __init__(self, epochs = 100, iterations=50, population = 100, type="swap", **kwargs):
        self.iterations = iterations
        self.sequences_distances = {}
        self.epochs = epochs
        self.population = population
        self.checked_solutions_set = set()
        
        super().__init__(**kwargs)
            
        generators = {"swap":self.swap_generator,
                      "pair":self.pair_generator}
        
        self.sequence_generator = generators[type]

    def define_optimal_sequence(self):
        initial_guess = tuple([dirt_coords for dirt_coords in self.dirt_coords])
        self.checked_solutions_set.add(initial_guess)
        self.sequences_distances[initial_guess] = (1 / self.calculate_distance_for_seq(initial_guess)) ** 3

        for shuffled_initial_guess in range(int(self.iterations ** 0.5)):
            additional_guess = list(initial_guess)
            random.shuffle(additional_guess)
            if not tuple(additional_guess) in self.checked_solutions_set:
                self.sequences_distances[tuple(additional_guess)] = (1 /
                                             self.calculate_distance_for_seq(additional_guess)) ** 3

        for epoch in range(self.epochs):
            estimated_solutions = [(v,k,) for k,v in self.sequences_distances.items()]
            estimated_solutions.sort()
            current_best_solutions = estimated_solutions[-50:]
            self.sequences_diestances = {k:v for v,k in current_best_solutions}
            for iteration in range(self.iterations):
                new_sequence = next(self.sequence_generator())
                if not new_sequence in self.checked_solutions_set:
                    self.sequences_distances[new_sequence] = (1 / self.calculate_distance_for_seq(new_sequence)) ** 3

        estimated_solutions = [(v, k,) for k, v in self.sequences_distances.items()]
        best_eval_sequence = max(estimated_solutions)
        return best_eval_sequence[1]

    def pair_generator(self):

        while True:
            [sequence1, sequence2] = random.choices(list(self.sequences_distances.keys()),
                                                    weights = list(self.sequences_distances.values()),
                                                    k = 2)

            slice_delimiter = random.randint(1, len(sequence1) - 1)

            new_sequence = list(sequence1[:slice_delimiter])
            already_present = set(new_sequence)

            for dirt_index in sequence2[slice_delimiter:]:
                if not dirt_index in already_present:  # not so greedy approach
                    new_sequence.append(dirt_index)
                    already_present.add(dirt_index)
            
            left_nodes = list(set(sequence1) - already_present)
            random.shuffle(left_nodes)

            for dirt_index in left_nodes:
                new_sequence.append(dirt_index)
            assert (len(new_sequence) == len(self.dirt_coords))

            yield tuple(new_sequence)
            
    def swap_generator(self):

        while True:
            [sequence] = random.choices(list(self.sequences_distances.keys()),
                                                    weights = list(self.sequences_distances.values()),
                                                    k = 1)
            sequence = list(sequence)
            swap_index_left = random.randint(0, len(sequence) - 2)
            swap_index_right = random.randint(swap_index_left+1,len(sequence)-1)

            sequence[swap_index_left],sequence[swap_index_right]=sequence[swap_index_right],sequence[swap_index_left]

            yield tuple(sequence)


[bot_row, bot_col] = [int(coord) for coord in input().split()]
[rows, cols] = [int(size) for size in input().split()]

bot_solve = OptimizedBotClean(rows=rows, cols=cols, bot_row=bot_row, bot_col=bot_col, type = "pair")
bot_solve.make_a_turn()
