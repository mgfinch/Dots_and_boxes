from bot1 import *
from dots_and_boxes import init_board
from itertools import combinations
import numpy as np
import json


WEIGHTS = np.array([2**i for i in xrange(2*BOARD_SIZE*(BOARD_SIZE-1))])
gamma = 1 # discount factor
RW = 10   # end score reward constant

def board2num(board):
    b = list(sum(board,[]))
    num = sum(WEIGHTS[i] for i in xrange(len(WEIGHTS))  if b[i])
    return num
    
def edge2num(edge):
    i,j = edge
    num = np.floor(i/2)*(2*BOARD_SIZE-1) + j
    if i % 2 == 1:
        num += BOARD_SIZE-1
    return(WEIGHTS[num])
        

def train_last_k(k):
    board = init_board()
    edges = []
    for i, row in enumerate(board):
        for j, val in enumerate(row):
            board[i][j] = True
            edges.append((i,j))
   
    
    for m in xrange(k): 
    
        board_states = combinations(edges,m)        

        if m==0:    #end states
            board_num = str(board2num(board))
            max_score = (BOARD_SIZE-1)**2
            
            Qedge = [dict()]
            Q = [[ dict() for i in xrange(max_score+1)]]
            for score in xrange(max_score+1):
                Q[m][score][board_num] = RW*(score-(max_score/2))
                
        else:
            # initiate row in Q-value lookup table
            Q.append([ dict() for i in xrange(max_score - int(np.floor(m/4)))])
            Qedge.append(dict())
            for board_state in board_states:
                # construct board from board state
                
                for edge in board_state:
                    i,j = edge
                    board[i][j] = False
                
                # find out how many squares are already filled
                total_score = 0
                for i in xrange(BOARD_SIZE-1):
                    for j in xrange(BOARD_SIZE-1):
                        sq_edges = get_edges((i,j),board)
                        if sum(sq_edges) == 4:
                            total_score += 1
                                            
                # find the best move - it must be the same, regardless of score 
                # we will consider it to be total_score
                potential_moves = []
                
                for i, row in enumerate(board):
                    for j, val in enumerate(row):
                        if val == False:
                            gain = check_surrounding_squares(board,(i,j),3)
                            # move remembers edge inserted and score gain,  
                            potential_moves.append(((i,j), gain))
                            
                # map potential_moves on Q-values
                qmax = -np.inf
                board_num = board2num(board)
                for move in potential_moves:
                    edge,gain = move
                    edge_num = edge2num(edge)
                    if gain:
                        qval = gamma*Q[m-1][total_score+gain][str(board_num + edge_num)]
                    else:
                        qval = -gamma*Q[m-1][0][str(board_num + edge_num)]
                    
                    if qmax < qval: 
                        qmax = qval
                        best_edge = edge
                
                # insert Q-values
                for score_state in xrange(total_score+1):
                    Q[m][score_state][str(board_num)] = qmax - RW*(total_score-score_state)
                # insert best move
                Qedge[m][str(board_num)] = best_edge
                    
                for edge in board_state:
                    i,j = edge
                    board[i][j] = True
                
    return(Q, Qedge)
    
    

def bot2_train_and_save(k):
    
    Q,Qedge = train_last_k(k)

    f = open('Q_' + str(k)+ '_'+ str(BOARD_SIZE) + '.txt','w')
    json.dump(Q,f)
    f.close()    
    
    f = open('Qedge_' + str(k)+ '_'+ str(BOARD_SIZE) + '.txt','w')
    json.dump(Qedge,f)
    f.close()    
    
def bot2_load(k):
    
    f = open('Qedge_' + str(k)+ '_'+ str(BOARD_SIZE) + '.txt','r')
    Qedge = json.load(f)
    f.close()  
    
    return(Qedge)


def bot2_move(board,Qedge,k):
    # last k moves are best possible, the rest is played by always4never3 strategy

    m = 0
    for i, row in enumerate(board):
        for j, val in enumerate(row):
            if val == False: m += 1
    
    if m < k:
        board_num = board2num(board)
        move = Qedge[m][str(board_num)]
    else:
        move = always4never3(board)
    
    return(move)
    