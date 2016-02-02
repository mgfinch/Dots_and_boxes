from bot1 import *
from bot2 import *
from dots_and_boxes import *



def get_Q_move_and_update(Q,board,l_rate=1,random_move_prob=1):
    # l_rate is the learning rate
    # random_move_prob ~ one of how many moves will not be random

    board_num = board2num(board)    
    potential_moves = get_potential_moves(board)
    m = len(potential_moves)
    total_score = get_total_score(board)
    max_score = (BOARD_SIZE-1)**2
    
    sucet = 0
    pocet = 0
    for move in potential_moves:
        edge_num = edge2num(move)
        q_tmp = Q[m-1].get(str(board_num+edge_num),0)
        sucet +=  q_tmp
        pocet += 1 if q_tmp else 0 
    Q_default = (max_score-total_score)/2 if pocet<2 else sucet/pocet 
    q_old = Q[m].get(str(board_num),Q_default)
    
    q_max = -np.inf
    for move in potential_moves:
        edge_num = edge2num(move)
        q_tmp = Q[m-1].get(str(board_num+edge_num),Q_default) # gamma=1
        reward = check_surrounding_squares(board,move,3)
        if reward: 
            # it is our move again and we can get at least Q-value of score
            q_tmp += reward   # we add reward  
        else: 
            # it is the opponents move, so Qvalue is the score he can get
            q_tmp = (max_score - total_score - q_tmp)
        
        if q_tmp > q_max: 
            q_max = q_tmp
            best_move = move
            
    q_new = q_old + l_rate*(q_max - q_old) # q_max is the max_a{reward_a + q_next_state_a}   
    
    if random.randrange(int(random_move_prob)): 
        best_move = random.choice(potential_moves)
    
    return(best_move,q_new)
    
    
def init_Q2():
    board = init_board()
    Q = [dict() for i in xrange(len(sum(board,[]))+1)]
    for i,row in enumerate(board):
        for j,val in enumerate(row):
            board[i][j] = True
    Q[0][str(board2num(board))] = 0
    return(Q)
    
    
def train2(num_games,Q = None,l_rate=1,random_move_prob=2, print_score=False, bot=0):
    
    if Q == None:
        # initialize Q
        Q = init_Q2()
    
    board = init_board()
    M = len(sum(board,[]))
    
    
    # load learned end_game for bot2
    k = 10
    #Qedge = []
    #Qedge = bot2_load(k)    
    
    
    start_player = 1
    wins = [0,0]
    
    for game_num in range(num_games):
        board = init_board()
        current_player = start_player
        m = M
        score = [0,0]
        game_moves = []
        q_updates = []
        while m>0:
            
            board_num = board2num(board)
            if current_player == 1:
                move = player_move(board,Qedge,k,bot)
                # We will update Q also on opponents position
                tmp,update = get_Q_move_and_update(Q,board,l_rate,random_move_prob)
            else:
                move,update = get_Q_move_and_update(Q,board,l_rate,random_move_prob)
            
            Q[m][str(board_num)] = update
            
            game_moves.append(move)
            i,j = move
            
            if board[i][j] == True: 
                print('neplatny tah! na rade bol hrac ' + str(current_player))
                print('predcasne ukoncene pri hre cislo ' + str(game_num))
                return(Q)
                
            gain = check_surrounding_squares(board,move,3)
            
            if (gain > 0):
                score[current_player] += gain   # update score
            else: 
                current_player = (1 + current_player)%2 # update current_player
            
            board[i][j] = True      # update board
            m -= 1
            
        # reconsider the game_moves and update Q if neccessary
#        m = 0
#        board_num = board2num(board) # number of the full board
#        for move in game_moves[::-1]:
#            q_tmp = Q[m][str(board_num)]
#            m += 1
#            board_num -= edge2num(move) 
#            q_old = Q[m][str(board_num)]
#            reward = check_surrounding_squares(board,move,3)
#            if reward: 
#                # it is our move again and we can get at least Q-value of score
#                q_tmp += reward   # we add reward  
#            else: 
#                # it is the opponents move, so Qvalue is the score he can get
#                total_score = get_total_score(board)
#                max_score = (BOARD_SIZE-1)**2
#                q_tmp = (max_score - total_score - q_tmp)
#                
#            q_update = q_old + l_rate*(q_tmp - q_old)
#            Q[m][str(board_num)] = q_update
        
        if print_score: print(score)
        winner = score.index(max(score))
        # also for even board_size the tie is possible
        if not score[0] == score[1]: wins[winner] += 1  
         
        start_player = (1 + start_player) % 2 
        
    return(Q,wins)
        
        
def player_move(board,Qedge,k,bot):
    
    if bot == 0: 
        move = get_random_move(board)
    elif bot == 1:
        move = first_available_move(board)   
    elif bot == 2:
        move = always4never3(board)
    elif bot == 3:
        move = bot2_move(board,Qedge,k)
    else:
        if random.randrange(3):
            move = bot2_move(board,Qedge,k)
        else: 
            move = get_random_move(board)
    return(move)

    
#    
#### UNCOMMENT FOR TESTING AND TRAINING BOTS

Qedge = bot2_load(10) 

### play with parameters and rerun this part :)
##Q,wins = train2(5000,l_rate = 1,random_move_prob = 3, bot = 3)   #training games
##print(wins)
##Q,wins = train2(5000,Q, l_rate = 1,random_move_prob = 2, bot = 3)   #training games
##print(wins)
##Q1,wins = train2(1000,Q, l_rate = 0, random_move_prob = 1, print_score = False, bot = 0) #testing games
##print(wins)
##Q1,wins = train2(1000,Q, l_rate = 0, random_move_prob = 1, print_score = False, bot = 1) #testing games
##print(wins)
##Q1,wins = train2(1000,Q, l_rate = 0, random_move_prob = 1, print_score = False, bot = 2) #testing games
##print(wins)
##Q1,wins = train2(100,Q, l_rate = 0, random_move_prob = 1, print_score = False, bot = 3) #testing games
##print(wins)
#
#
#
## final match!
Q,wins = Q,wins = train2(5000,l_rate = 1,random_move_prob = 3, bot = 0) 
Q1,wins = train2(100,Q, l_rate = 0, random_move_prob = 1, print_score = False, bot = 3) #testing games
print('Kolo '+ str(0) + ': ' + str(wins))
i = 1

while wins[0]<wins[1]:
    Q,wins = train2(5000,Q, l_rate = 0.05,random_move_prob = 2, bot = 0) 
    Q,wins = train2(1000,Q, l_rate = 0.05,random_move_prob = 1, bot = 3) 
    Q1,wins = train2(100,Q, l_rate = 0, random_move_prob = 1, print_score = False, bot = 3) #testing games
    print('Kolo '+ str(i) + ': ' + str(wins))
    i += 1

#
