import itertools as it
from collections import deque, namedtuple
import random
from abc import ABC, abstractmethod
import re
import math
import copy


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

    
class MLOptimizedBotClean(Matrix_Bot_Dirt):
    '''
    this class is collection of methods for optimizing sequence of coords for bot to pass
    '''

    
    
    def __init__(self, epochs = 20, iterations=250, population = 100, generator_type="swap", **kwargs):
        self.iterations = iterations
        self.sequences_distances = {}
        self.epochs = epochs
        self.population = population
        self.checked_solutions_set = set()
        
        super().__init__(**kwargs)
            
        generators = {"swap":self.swap_generator,
                      "pair":self.pair_generator,
                      "cross-breed": self.cross_breed_generator,
                      "preferrably closest": self.always_preferrably_closest_generator}
        
        self.sequence_generator = generators[generator_type]

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
            
            yield tuple(new_sequence)
            
    def swap_generator(self):

        while True:
            [sequence] = random.choices(list(self.sequences_distances.keys()),
                                                    weights = list(self.sequences_distances.values()),
                                                    k = 1)
            new_sequence = list(sequence)
            swap_index_left = random.randint(0, len(sequence) - 2)
            swap_index_right = random.randint(swap_index_left+1,len(sequence)-1)

            tmp_left = new_sequence[swap_index_left]
            tmp_right = new_sequence[swap_index_right] 
            new_sequence[swap_index_right] = tmp_left
            new_sequence[swap_index_left] = tmp_right
            yield tuple(new_sequence)
            
    def cross_breed_generator(self):
        while True:
            [sequence1, sequence2] = random.choices(list(self.sequences_distances.keys()),
                                                    weights = list(self.sequences_distances.values()),
                                                    k = 2)
            new_sequence = []
            collected_nodes_set = set()
            
            sequence1 = list(sequence1)
            sequence2 = list(sequence2)
            
            for [node1,node2] in zip(sequence1,sequence2):
                node_to_add = random.choice([node1,node2])
                if not (node_to_add in collected_nodes_set):
                    new_sequence.append(node_to_add)
                    collected_nodes_set.add(node_to_add)
                else:
                    if not(node1 in collected_nodes_set):
                        new_sequence.append(node1)
                        collected_nodes_set.add(node1)
                    elif not(node2 in collected_nodes_set):
                        new_sequence.append(node2)
                        collected_nodes_set.add(node2)
                    else:
                        nodes_not_added = list(set(self.dirt_coords) - collected_nodes_set)
                        node_to_add = random.choice(nodes_not_added)
                        new_sequence.append(node_to_add)
                        collected_nodes_set.add(node_to_add)
            
            yield tuple(new_sequence)
            
    @property
    def node_to_nodes_distance_dicts_dict(self):
        """
        bad style nested dictionary - need to change that mess later
        """
        try:
            return self._node_to_nodes_dicts_dict
        except AttributeError:
            self._node_to_nodes_dicts_dict = {}
            for node_1_coords in self.dirt_coords:
                tmp_dict_for_node_1 = {}
                for node_2_coords in self.dirt_coords:
                    if node_2_coords != node_1_coords:
                        tmp_dict_for_node_1[node_2_coords] = self.calc_distance(node_1_coords,node_2_coords)
            self._node_to_nodes_dicts_dict[node_1_coords] = copy.deepcopy(tmp_dict_for_node_1)
        return self._node_to_nodes_dicts_dict
            
    @property
    def bot_to_nodes_distance_dict(self):
        """
        clearly bad style - nighttime coding at its' worst
        """
        try:
            return self._bot_to_nodes_distance_dict
        except AttributeError:
            self._bot_to_nodes_distance_dict = {}
            for node_coords in self.dirt_coords:
                self._bot_to_nodes_distance_dict[node_coords] = self.calc_distance(self.bot_coords,node_coords)
        return self._bot_to_nodes_distance_dict
    
    def always_preferrably_closest_generator(self):
        """
        we try here to make something resembling to always_choose_closest_node method
        from HardCodedBotClean class
        except that we add variation - our choice is weighted: probability of choosing next closest node is highest
        while probability of choosing farthest node - is lowest
        
        BAD STYLE!!! NINJACODING 
        So not only it does not work... it is just bad and therefore this part of
        code is just a graveyard of preconceptions
        """
        raise NotImplementedError
        while True:
            sequence = []
            already_added_nodes = set()
            
            [current_node] = random.choices(list(self.bot_to_nodes_distance_dict.keys()),
                                       weights = list(self.bot_to_nodes_distance_dict.values()),
                                       k = 1)
            
            tmp_node_to_nodes_distance_dicts_dict = copy.deepcopy(self.node_to_nodes_distance_dicts_dict) 
            
            
            
            while len(sequence) < len(self.dirt_coords):
                already_added_nodes.add(current_node)
                
                for node in already_added_nodes:
                    tmp_node_to_nodes_distance_dicts_dict[current_node].pop(node, None)

                [next_node] = random.choices(list(tmp_node_to_nodes_distance_dicts_dict[current_node].keys()),
                                       weights = list(tmp_node_to_nodes_distance_dicts_dict[current_node].values()),
                                       k = 1)
                #tmp_node_to_nodes_distance_dicts_dict.pop(current_node)
                sequence.append(current_node)
                current_node = next_node
            
            yield current_node
                

                
class HardCodedBotClean(Matrix_Bot_Dirt):
    
    def __init__(self, optimizer_type = "closest", **kwargs):
        super().__init__(**kwargs)
        
        self.hard_coded_solvers = {"closest":self.always_choose_closest_node,
                                   "two closest":self.always_try_two_closest_nodes}
        self.optimizer = self.hard_coded_solvers[optimizer_type]
        
        
    def define_optimal_sequence(self):
        return self.optimizer()
    
    def always_choose_closest_node(self):
        current_node = self.bot_coords
        nodeset = set(self.dirt_coords)
        sequence = []
        
        while nodeset:
            closest_distance = math.inf
            closest_node = None
            
            for node in nodeset:
                new_distance = self.calc_distance(current_node,node)
                if new_distance < closest_distance:
                    closest_distance = new_distance
                    closest_node = node
                    
            sequence.append(closest_node)
            current_node = closest_node
            nodeset.remove(closest_node)
            
        return tuple(sequence)
    
    def always_try_two_closest_nodes(self):
        """
        CURRENTLY IT IS NOT OPTIMAL DUE TO SOME MISTAKE
        it wins only 3 out of 4 and its' paths are LONGER than expected (so there are clearly MISTAKES in code)
        in contrast to all other methods all sequences will start with bot coords
        so we don't need this first node in resulting sequence
        """
        current_node = self.bot_coords
        nodeset = set(self.dirt_coords)
        
        Path_Seq_Nodeset = namedtuple("PathSeqNodeset",['distance','sequence','nodeset']) 
        self.path_sequence_nodeset_triples = deque([ Path_Seq_Nodeset(0,[current_node],nodeset) ])
    
        current_shortest_path = math.inf
        finished_sequences = []
        
        while self.path_sequence_nodeset_triples: 
            '''
            simply couldn't think of better loop
            which doubles on each turn... mb there is one.
            '''
            sequence_nodeset_triple = self.path_sequence_nodeset_triples.pop()
            #first we decide if current sequence can be continued. If not - we add it to finished sequences
            if not sequence_nodeset_triple.nodeset:
                finished_sequences.append((sequence_nodeset_triple))
                if sequence_nodeset_triple.distance < current_shortest_path:
                    current_shortest_path = sequence_nodeset_triple.distance
            elif sequence_nodeset_triple.distance < current_shortest_path:
                self.make_two_seqs_from_one(sequence_nodeset_triple)
            else:
                pass
        #now we need to find best of finished sequences based on their length
        finished_sequences.sort()
        best_sequence = finished_sequences[0].sequence
        return best_sequence[1:] #we exclude first node from sequence because in this method it's bot coords

    def make_two_seqs_from_one(self,sequence_nodeset_triple):

                
        #now we collect available nodes, and sort them by their distance from current node
        available_distance_node_pairs = []
        current_node = sequence_nodeset_triple.sequence[-1]       
        for node in sequence_nodeset_triple.nodeset:
            assert(len(node)==2)
            new_distance = self.calc_distance(current_node,node)
            available_distance_node_pairs.append((new_distance,node,))
                
        #now we define first closest node
        available_distance_node_pairs.sort()
        first_dist_node_to_add = available_distance_node_pairs[0]
        self.add_node_triple_to_seq(sequence_nodeset_triple,first_dist_node_to_add)
        
        for dist_node_pair in available_distance_node_pairs[1:]:
            possible_second_dist_node = dist_node_pair
            if self.check_if_second_is_not_excessive(current_node,
                                                     first_dist_node_to_add[1],
                                                     possible_second_dist_node[1]):
                self.add_node_triple_to_seq(sequence_nodeset_triple,possible_second_dist_node)
            else:
                pass
            
    def add_node_triple_to_seq(self,current_nodeset_triple,dist_node_to_add):
        
        tmp_nodeset_triple = copy.deepcopy(current_nodeset_triple)
        #we collect neccessary data to add to our deque
        current_node = tmp_nodeset_triple.sequence[-1]
        distance_to_node = dist_node_to_add[0]
        node_to_add = dist_node_to_add[1]
        assert(len(node_to_add) == 2)
        tmp_nodeset_triple.nodeset.remove(dist_node_to_add[1])
        tmp_nodeset_triple._replace(distance =   tmp_nodeset_triple.distance + distance_to_node)
        new_sequence = tmp_nodeset_triple.sequence
        new_sequence.append(node_to_add)
        tmp_nodeset_triple._replace(sequence = new_sequence)
        #and add it to our deque
        self.path_sequence_nodeset_triples.append(tmp_nodeset_triple)
        
    def check_if_second_is_not_excessive(self,current_node,first_node_to_add,possible_second_node):
        row_upper_limit = max(current_node[0],possible_second_node[0])
        row_lower_limit = min(current_node[0],possible_second_node[0])
        col_upper_limit = max(current_node[1],possible_second_node[1])
        col_lower_limit = min(current_node[1],possible_second_node[1])
        if (row_lower_limit<=first_node_to_add[0]<=row_upper_limit and
            col_lower_limit<=first_node_to_add[1]<=col_upper_limit ):
            return False
        else:
            return True
        
if __name__ == '__main__':
    [bot_row, bot_col] = [int(coord) for coord in input().split()]
    [rows, cols] = [int(size) for size in input().split()]

    #bot_solve = HardCodedBotClean(rows=rows, cols=cols, bot_row=bot_row, bot_col=bot_col, optimizer_type = "closest")
    #bot_solve = MLOptimizedBotClean(rows=rows, cols=cols, bot_row=bot_row, bot_col=bot_col, generator_type = "swap")
    #bot_solve = MLOptimizedBotClean(rows=rows, cols=cols, bot_row=bot_row, 
    #                               bot_col=bot_col, generator_type = "preferrably closest")
    bot_solve = HardCodedBotClean(rows=rows, cols=cols, bot_row=bot_row, 
                                  bot_col=bot_col, optimizer_type = "two closest") 
    
    bot_solve.make_a_turn()
