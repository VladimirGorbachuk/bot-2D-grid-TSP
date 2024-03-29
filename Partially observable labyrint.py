class Get_Out_of_Lab():
    '''
    While reading Maze Escape description
    I have some second thoughts 
    - do I have control over both bots? - looks like I do
    - do I need to make and store two maps? - seems like I have to
    How and when can I unify these two maps? At which phase? Do I need It at all? - currently I will pass
    
    
    So in this regard I've decided that in head-on approach
    I will just make 2 maps, which are two tmp files (without trying to unite them)
    Also, as I don't know what is the map size... (but I know its' limits, which are 30x30)
    I will create 61x61 sized map which has center in the cell, where the bot is currently positioned
    "o" will stand for unknown cells, "v" - for visited cells and I will mark as "#" those cells, which
    were visited twice
    
    We don't know what is the starting direction of bot (and we won't know), 
    so by default let's take it as "UP", so that
    "RIGHT" would move bot to the RIGHT (and it will change bot's direction to RIGHT) etc
    '''
    
    def __init__(self, bot_ID = None):
        bot_ID = bot_ID
        tmp_map_filenames = {1:"bot1_map.txt",
                             2:"bot2_map.txt"}
        self.tmp_map_filename = tmp_map_filenames[bot_ID]
        self.matrix_rows = 61
        self.matrix_cols = 61
        
    @property
    def matrix(self):
        try:
            return self.__matrix
        except AttributeError: #that means - we did not define self.__matrix yet
            self.__matrix = []
            try:
                with open(self.tmp_map_filename, "r") as f:
                    self.bot_direction = f.readline() #"RIGHT" or "LEFT" or "UP" or "DOWN"
                    self.bot_pos = [int(coord) for coord in f.readline().split()]
                    for _row in range(self.matrix_rows):
                        row_from_file = [char for char in f.readline().split()]
                        self.__matrix.append(row_from_file)
                self.__update_matrix()
            except FileNotFoundError: #that means we did not create file yet - i.e. it's our first turn
                self.__matrix = [["o" for _ in range(61)] for __ in range(61)]
                current position = (30,30,)
                for row_ind in [29,30,31]:
                    row_from_input_gen = (char for char in input())
                    for col_ind in [29,30,31]:
                        self.__matrix[row_ind,col_ind] = next(row_from_input_gen)
                return self.__matrix
    
    def update_matrix(self):
        raise NotImplementedError
        b_c= self.bot_coords
        coords_to_update = ()
        
    def acquire_and_rotate_input_matrix(self):
        """
        
        """
        input_minimatrix = []
        for _row in range(3):
            row_to_add = [char for char in input()]
            input_minimatrix.append(row_to_add)
        if self.bot_direction == "UP":
            return input_minimatrix
        elif self.bot_direction == "RIGHT":
            raise NotImplementedError
        elif self.bot_direction == "LEFT":
            raise NotImplementedError
        else:
            raise NotImplementedError
        
    def direction_change(self, direction_chosen):
        """
        we prepare some dicts to define new direction based on previous direction (key)
        and direction of turn (correspondingly)
        """
        
        directions_switch_turnleft = {"UP":"LEFT","LEFT":"DOWN","DOWN":"RIGHT","RIGHT":"UP"}
        directions_switch_turnright = {"UP":"RIGHT", "RIGHT":"DOWN","DOWN":"LEFT", "LEFT":"UP"}
        directions_switch_turnback = {"UP":"DOWN", "DOWN":"UP", "RIGHT":"LEFT", "LEFT":"RIGHT"}
        
        if direction_chosen == "UP":
            return self.bot_direction
        elif direction_chosen == "DOWN":
            return directions_switch_turnback[direction_chosen]
        elif direction_chosen == "LEFT":
            return directions_switch_turnleft[direction_chosen]
        else:
            return directions_switch_turnright[direction_chosen]
    
    def write_to_file(self):
        with open(self.tmp_map_filename, "w+") as f:
            f.writeline(self.new_bot_direction)
            f.writeline(self.new_bot_coords)
            for row in self.matrix:
                f.writeline(" ".join(row))
    
            
        
    def mark_as_passed(self):
        if self.matrix[self.bot_coords[0]][self.bot_coords[1]] == "-":
            self.matrix[self.bot_coords[0]][self.bot_coords[1]] = "x"
        else:
            self.matrix[self.bot_coords[0]][self.bot_coords[1]] = "#"
            
if __name__ == "__main__":
    bot_runner = Get_Out_of_Lab(int(input()))
    bot_runner.move()
