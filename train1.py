from bot1 import *
from bot2 import *
from dots_and_boxes import *
import numpy as np
import random

from sklearn.neural_network import MLPClassifier

from sklearn.tree import DecisionTreeRegressor



def train1(num_games):
    
    Q = init_Q()    
    
    
    for i in xrange(num_games):
        board = init_board()
        score = [0,0]
        current_player = 1
        
        while first_avalible_move(board):
            if current_player == 1:
                move = always4never3(board)
            else:
                move = get_Q_move(Qreg,board)
            
                gain = check_surrounding_squares(board,move,3)
                
            
            
            
def init_Q():
    # make some dummy training set
    board = init_board()
    board_vec = board2vec(board)
    X = np.array([board_vec])
    y = [(BOARD_SIZE-1)**2]
    board_vec = np.invert(board_vec)
    X = np.append(X,np.array([board_vec]),axis=0)
    y.append(0)
    
    edges = get_potential_moves(board) # all the edges, since the board is empty
    for edge in edges:
        i = edge2ind(edge)
        board_vec[i] = False
        X = np.append(X,np.array([board_vec]),axis=0)
        y.append(check_surrounding_squares(board,edge,0))
        board_vec[i] = True       
    
    
        
    Q = MLPClassifier(warm_start=True, 
                      hidden_layer_sizes=(BOARD_SIZE,10*BOARD_SIZE,BOARD_SIZE), 
                      tol = 1e-10,
                      )
    # Q = DecisionTreeRegressor()
                     
    #    shf = range(len(y))
    #    for j in xrange(100):
    #        random.shuffle(shf)
    #        Xshf = [X[i] for i in shf]
    #        yshf = [y[i] for i in shf]
    triedy = range((BOARD_SIZE-1)**2+1)
    Q.partial_fit(np.repeat(X,100,axis=0),np.repeat(y,100,axis=0),classes=triedy)
    print(Q.predict(X))
    return(Q)
    
Q = init_Q()
Q.predict([board_vec])
    
def get_Q_move(Q,board):

    board_vec = board2vec(board)
    
    potential_moves = get_potential_moves(board)
    q_max = -np.inf
    for move in potential_moves:
        ind = edge2ind(move)
        board_vec[ind] = True # change board to look like after the move
        q_tmp = Q.predict([board_vec])[0] # gamma=1
        reward = check_surrounding_squares(board,move,3)
        if reward: 
            q_tmp += reward   # we add reward  
        else:
            total_score = get_total_score(board)
            max_score = (BOARD_SIZE-1)**2
            q_tmp = (max_score - total_score - q_tmp
        
        if q_tmp > q_max: 
            q_max = q_tmp
            best_move = move
        
        board_vec[ind] = False # change board back to original state
    
    return(best_move)
    
    
def get_Q_move_and_update(Q,board,l_rate):
    #l_rate is the learning rate    
    board_vec = board2vec(board)
    q_old = Q.predict([board_vec])
    
    potential_moves = get_potential_moves(board)
    q_max = -np.inf
    for move in potential_moves:
        ind = edge2ind(move)
        board_vec[ind] = True # change board to look like after the move
        q_tmp = Q.predict([board_vec])[0] # gamma=1
        reward = check_surrounding_squares(board,move,3)
        if reward: 
            q_tmp += reward   # we add reward  
        else:
            total_score = get_total_score(board)
            max_score = (BOARD_SIZE-1)**2
            q_tmp = (max_score - total_score - q_tmp)
        
        if q_tmp > q_max: 
            q_max = q_tmp
            best_move = move
        
        board_vec[ind] = False # change board back to original state
    
    q_new = q_old + l_rate*(q_max - q_old) # q_max is the max_a{reward_a + q_next_state_a}   
    
    return(best_move,q_new)
                

    