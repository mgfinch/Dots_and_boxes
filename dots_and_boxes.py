#!/usr/bin/env python

import curses, sys, re
from time import sleep
import numpy as np
import random
from random import randint

OFFSET_X, OFFSET_Y = 2, 1
BOARD_SIZE = 4
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def init_board():
    # The structure of the board is a bit confusing, but it looks like this
    # The even indexed rows have fewer values because there are fewer possible
    # lines on them.
    
    # o---o   o    [  [ True, False ],
    # |               [ True, False, False], 
    # o   o---o       [ False, True ],
    #     |           [ False, True, False],
    # o---o---o       [ True, True]           ]
    
    even = [False for i in xrange(BOARD_SIZE - 1)]
    odd = [False for i in xrange(BOARD_SIZE)]
    
    board = []
    for i in xrange(BOARD_SIZE * 2 - 1):
        if i % 2 == 0:
            board.append(even[:])
        else:
            board.append(odd[:])
    
    return board

def init_score():
    # The scorecard is a little bit redundant, but makes things easier
    # Its size is (BOARD_SIZE-1)^2 because we have to store more lines than
    # dots.
    #
    # o - o   o       [  
    # | 1 |              [ 1, None ],
    # o - o - o       
    #     | 2 |          [ None, 2 ]
    # o   o - o                       ]
    #
    return [[None for a in xrange(BOARD_SIZE-1)] for b in xrange(BOARD_SIZE-1)]

def closest_free(board, x, y):
    def distance(x1, y1, x2, y2):
        from math import sqrt
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    distances = []
    for i,row in enumerate(board):
        for j,val in enumerate(row):
            if val == False: 
                distances.append((distance(x, y, i, j), i, j))
    
    if len(distances) == 0:
        return False
    
    distances.sort(key=lambda x: x[0])
    return distances[0][1:]
    
    

def first_available_move(board):
    try:
        return closest_free(board, 0, 0)
    except IndexError:
        return False
        
         
    
def get_potential_moves(board):
    
    potential_moves = []
        
    for i, row in enumerate(board):
        for j, val in enumerate(row):
            if val == False:
                potential_moves.append((i,j))
                
    return(potential_moves)



def get_total_score(board):
    total_score = 0
    for i in xrange(BOARD_SIZE-1):
        for j in xrange(BOARD_SIZE-1):
            sq_edges = get_edges((i,j),board)
            if sum(sq_edges) == 4:
                total_score += 1
    return(total_score)
    
    
    
def get_edges(square,board):
    #for square (i,j) returns the 4-tuple of 0-1 for the edges of this square
    # ordered(top,left,right,bottom)
    i,j = square
    sq_edges = [board[i * 2][j],          # top 
      board[i * 2 + 1][j],      # left
      board[i * 2 + 1][j + 1],  # right
      board[i * 2 + 2][j]]      # bottom
      
    return(sq_edges)
    
    

def check_surrounding_squares(board,edge,k):
    # will check if any of the surrounding squares has k or more edges 
    # (apart from edge), i.e. k=3 will check for squares to be completet with edge
    # will return number of such squares (0-4)
    i,j = edge
    
    # first trivial cases that can be computed faster without checking the edges
    if k>3: return(0)
    if k<=0:
        if i%2 == 0:
            return(sum([i>0,(i-1)/2+1 < BOARD_SIZE-1]))
        else:
            return(sum([j>0,j < BOARD_SIZE - 1]))
    # now all other cases
    num = 0
    if i % 2 == 0:
        # Now it's time to check for new 3-boxes
        # o   o   
        #        
        # o---o  A new horizontal line can only fill in above
        #        or below
        # o   o
        
        if i > 0:
            # check above
            sq_edges = get_edges(((i-1)/2, j),board)
            if sum(sq_edges)>= k: 
                num += 1
                
        
        if (i-1)/2+1 < BOARD_SIZE-1:
            # check below
            sq_edges = get_edges(((i-1)/2+1, j),board)
            if sum(sq_edges)>= k: 
                num += 1
    else:
        # Now it's time to check for new boxes
        # o   o   o   A new vertical line can only fill in
        #     |       on the left or right
        # o   o   o
        
        if j > 0:
            # check left
            sq_edges = get_edges(((i-1)/2, j-1),board)
            if sum(sq_edges)>= k: 
                num += 1
                
        if j < BOARD_SIZE - 1:
            # check right
            sq_edges = get_edges(((i-1)/2, j),board)
            if sum(sq_edges)>= k: 
                num += 1                        
    
    return(num)

    
def board2vec(board):
    board_vec = np.array(sum(board,[]))
    return(board_vec)
    #todo: try to enrich board_vec by some values
    
def edge2ind(edge):
    i,j = edge
    num = np.floor(i/2)*(2*BOARD_SIZE-1) + j
    if i % 2 == 1:
        num += BOARD_SIZE-1
    return(num)
    