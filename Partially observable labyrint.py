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
    '''
    
    def __init__(self, bot_ID = None):
        self.bot_ID = bot_ID
        self.tmp_map_1_filename = "bot1_map.txt"
        self.tmp_map_2_filename = "bot2_map.txt"
        
        
if __name__ == "__main__":
    bot_runner = Get_Out_of_Lab(int(input()))
    bot_runner.move()
