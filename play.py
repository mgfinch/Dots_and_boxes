#!/usr/bin/env python

import curses, sys, re
from time import sleep
from random import randint
from bot1 import *
from bot2 import *
from dots_and_boxes import *

OFFSET_X, OFFSET_Y = 2, 1
#BOARD_SIZE = 4
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# init curses
stdscr = curses.initscr()
curses.noecho()
curses.start_color()
stdscr.keypad(1)

curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)


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

def draw_dot(x, y):
    sx = OFFSET_X + x * 4
    sy = OFFSET_Y + y
    stdscr.addstr(sy, sx, "o")
    stdscr.addstr(sy, sx + 4, "o")

def draw_line(x, y, color=0):
    # print "%d, %d" % (x, y)
    if y % 2 == 0:
        sy = OFFSET_Y + y
        sx = OFFSET_X + x * 4 + 1
        stdscr.addstr(sy, sx, '---', curses.color_pair(color))
    else:
        sy = OFFSET_Y + y
        sx = OFFSET_X + x * 4
        stdscr.addstr(sy, sx, "|", curses.color_pair(color))

def draw_filling(x, y, player):
    screen_x = OFFSET_X + x * 4 + 2
    screen_y = OFFSET_Y + y * 2 + 1
    stdscr.addstr(screen_y, screen_x, str(player), curses.color_pair(player))

def play_game():
    board = init_board()
    score = init_score()
    
    draw_board(board, score)
    
    current_player = 1 # alternates between 1 and 2
    
    def check_and_set_square(x, y):    
        if score[x][y]:
            return 0
        
        if (board[x * 2][y] and         # above
            board[x * 2 + 1][y] and     # left
            board[x * 2 + 1][y + 1] and # right
            board[x * 2 + 2][y]):       # bottom 
                score[x][y] = current_player
                return 1
        return 0
    
    selected_x, selected_y = 0, 0
    
    while first_available_move(board):            
        y = OFFSET_Y + BOARD_SIZE * 2 + 1
        
        # Let's handle the selector:
        selected_x, selected_y = closest_free(board, selected_x, selected_y)
        
        # Read from the keyboard
        c = None
        while c != ord("\n") or board[selected_x][selected_y]:
            stdscr.clear()
            draw_board(board, score)
            color = board[selected_x][selected_y] and 3 or current_player
            draw_line(selected_y, selected_x, color)
            
            c = stdscr.getch()
            if c == curses.KEY_UP:
                size = selected_x  % 2 == 0 and 2 * BOARD_SIZE - 1 or 2 * BOARD_SIZE
                selected_x = (selected_x - 1) % size
                
                if selected_y >= len(board[selected_x]):
                    selected_y = len(board[selected_x]) - 1
                elif selected_y == len(board[selected_x]) - 2 and selected_x % 2 == 1:
                    selected_y += 1
            elif c == curses.KEY_DOWN:
                size = selected_x  % 2 == 0 and 2 * BOARD_SIZE - 1 or 2 * BOARD_SIZE
                selected_x = (selected_x + 1) % size
                
                if selected_y >= len(board[selected_x]):
                    selected_y = len(board[selected_x]) - 1
                elif selected_y == len(board[selected_x]) - 2 and selected_x % 2 == 1:
                    selected_y += 1
            elif c == curses.KEY_LEFT:
                size = selected_x  % 2 == 0 and BOARD_SIZE - 1 or BOARD_SIZE
                selected_y = (selected_y - 1) % size
            elif c == curses.KEY_RIGHT:
                size = selected_x  % 2 == 0 and BOARD_SIZE - 1 or BOARD_SIZE
                selected_y = (selected_y + 1) % size
                        
        x1,y1 = selected_x,selected_y
        
        filled_boxes = 0
        board[selected_x][selected_y] = True
        
        if selected_x % 2 == 0:
            # Now it's time to check for new boxes
            # o   o   
            #        
            # o---o  A new horizontal line can only fill in above
            #        or below
            # o   o
            
            if x1 > 0:
                # check above
                filled_boxes += check_and_set_square((x1-1)/2, y1)
            
            if (x1-1)/2+1 < BOARD_SIZE-1:
                # check below
                filled_boxes += check_and_set_square((x1-1)/2+1, y1)
        else:
            # Now it's time to check for new boxes
            # o   o   o   A new vertical line can only fill in
            #     |       on the left or right
            # o   o   o
            
            if y1 > 0:
                # check left
                filled_boxes += check_and_set_square((x1-1)/2, y1-1)
            
            if y1 < BOARD_SIZE - 1:
                # check right
                filled_boxes += check_and_set_square((x1-1)/2, y1)
    
        if filled_boxes == 0:
            # switch players
            current_player = current_player % 2 + 1
        
        draw_board(board, score)
        stdscr.refresh()

    draw_board(board,score)
    score_vals = [0,0]
    for i,row in enumerate(score):
        for j,p in enumerate(row):
            if p==1:
                score_vals[1] += 1 
            else: 
                score_vals[0] += 1
    
    curses.endwin()
    print("score ->   player1: " +  str(score_vals[1]) + ",     player2: " + str(score_vals[0]))
    
        
    

def draw_board(board, scores):
    # +-------> y-axis
    # |   1 2
    # | A . .
    # | B . .
    # v
    # x-axis
    #
    # draw the headers
    
    # now draw the board
    for i, row in enumerate(board):
        for j, column in enumerate(row):
            # print "here %d, %d" % (i, j)
            if i % 2 == 0:
                draw_dot(j, i)
            if column:
                draw_line(j, i)
    
    stdscr.refresh()
    
    # We need to draw the letters in the boxes too and add the score
    player1, player2 = 0, 0
    for i, row in enumerate(scores):
        for j, score in enumerate(row):
            if score == 1: player1 += 1
            if score == 2: player2 += 1
            if score:
                draw_filling(j, i, score)
    
    # Draw the score board
    screen_y = OFFSET_Y + BOARD_SIZE * 2
    screen_x = OFFSET_X
    stdscr.addstr(screen_y, screen_x, "Player 1: %d" % player1, 
                    curses.color_pair(1))
    stdscr.addstr(screen_y + 1, screen_x, "Player 2: %d" % player2, 
                    curses.color_pair(2))
    
    stdscr.refresh()



def play_game_human_vs_bot(bot_num):
    board = init_board()
    score = init_score()
    
    draw_board(board, score)
    
    current_player = 1 # alternates between 1 and 2
    
    if bot_num == 2:
        Qedge = bot2_load(10)
    
    def check_and_set_square(x, y):    
        if score[x][y]:
            return 0
        
        if (board[x * 2][y] and         # above
            board[x * 2 + 1][y] and     # left
            board[x * 2 + 1][y + 1] and # right
            board[x * 2 + 2][y]):       # bottom 
                score[x][y] = current_player
                return 1
        return 0
    
    selected_x, selected_y = 0, 0
    
    while first_available_move(board):            
        y = OFFSET_Y + BOARD_SIZE * 2 + 1
        
        # Let's handle the selector:
        selected_x, selected_y = closest_free(board, selected_x, selected_y)
        
        # Read from the keyboard
        if current_player == 1:
            c = None
            while c != ord("\n") or board[selected_x][selected_y]:
                stdscr.clear()
                draw_board(board, score)
                color = board[selected_x][selected_y] and 3 or current_player
                draw_line(selected_y, selected_x, color)
                
                c = stdscr.getch()
                if c == curses.KEY_UP:
                    size = selected_x  % 2 == 0 and 2 * BOARD_SIZE - 1 or 2 * BOARD_SIZE
                    selected_x = (selected_x - 1) % size
                    
                    if selected_y >= len(board[selected_x]):
                        selected_y = len(board[selected_x]) - 1
                    elif selected_y == len(board[selected_x]) - 2 and selected_x % 2 == 1:
                        selected_y += 1
                elif c == curses.KEY_DOWN:
                    size = selected_x  % 2 == 0 and 2 * BOARD_SIZE - 1 or 2 * BOARD_SIZE
                    selected_x = (selected_x + 1) % size
                    
                    if selected_y >= len(board[selected_x]):
                        selected_y = len(board[selected_x]) - 1
                    elif selected_y == len(board[selected_x]) - 2 and selected_x % 2 == 1:
                        selected_y += 1
                elif c == curses.KEY_LEFT:
                    size = selected_x  % 2 == 0 and BOARD_SIZE - 1 or BOARD_SIZE
                    selected_y = (selected_y - 1) % size
                elif c == curses.KEY_RIGHT:
                    size = selected_x  % 2 == 0 and BOARD_SIZE - 1 or BOARD_SIZE
                    selected_y = (selected_y + 1) % size
        else:
            if bot_num == 1:
                selected_x, selected_y = always4never3(board)
            elif bot_num == 2:
                selected_x, selected_y = bot2_move(board,Qedge,10)

                
                 
        x1,y1 = selected_x,selected_y
        
        filled_boxes = 0
        board[selected_x][selected_y] = True
            
        if selected_x % 2 == 0:
            # Now it's time to check for new boxes
            # o   o   
            #        
            # o---o  A new horizontal line can only fill in above
            #        or below
            # o   o
            
            if x1 > 0:
                # check above
                filled_boxes += check_and_set_square((x1-1)/2, y1)
            
            if (x1-1)/2+1 < BOARD_SIZE-1:
                # check below
                filled_boxes += check_and_set_square((x1-1)/2+1, y1)
        else:
            # Now it's time to check for new boxes
            # o   o   o   A new vertical line can only fill in
            #     |       on the left or right
            # o   o   o
            
            if y1 > 0:
                # check left
                filled_boxes += check_and_set_square((x1-1)/2, y1-1)
            
            if y1 < BOARD_SIZE - 1:
                # check right
                filled_boxes += check_and_set_square((x1-1)/2, y1)
    
        if filled_boxes == 0:
            # switch players
            current_player = current_player % 2 + 1
        
        draw_board(board, score)
        stdscr.refresh()
        
    draw_board(board,score)
    score_vals = [0,0]
    for i,row in enumerate(score):
        for j,p in enumerate(row):
            if p==1:
                score_vals[1] += 1 
            else: 
                score_vals[0] += 1
    
    c = stdscr.getch()
    curses.endwin()
    print("score ->   player1: " +  str(score_vals[1]) + ",     player2: " + str(score_vals[0]))
    
        


if __name__ == '__main__':
    try:
        # play_game()
        # play_game_human_vs_bot(1)
        play_game_human_vs_bot(2)
        
        
    except KeyboardInterrupt:
        pass
    finally:
        curses.endwin()
