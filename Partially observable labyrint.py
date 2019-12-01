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
        except AttributeError:
            self.__matrix = []
            try:
                with open(self.tmp_map_filename, "r") as f:
                    bot_direction_relative_to_starting_direction = f.readline() #"RIGHT" or "LEFT" or "UP" or "DOWN"
                    previous_pos = [int(coord) for coord in f.readline().split()]
                    for row in range(self.matrix_rows):
                        
                        self.__matrix.append()
            except FileNotFoundError:
                self.__matrix = [["o" for _ in range(61)] for __ in range(61)]
    
    def update_matrix(self,prev_pos=None,prev_move =None):
        
if __name__ == "__main__":
    bot_runner = Get_Out_of_Lab(int(input()))
    bot_runner.move()
