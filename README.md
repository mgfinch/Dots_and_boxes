# Dots_and_boxes

Dots and Boxes is a simple 2 player game, played on square grid.
In this project we apply methods of reinforcement learning for training 
an automatic player. The method used is a version of Q-learnig adjusted
for this particular game to allow smaller memory costs. 

The motivation, details of the implementation and the results are summarized
only in `slovak language` in the report `latex/projekt-ML-dots-and-boxes.pdf`


In the process of working on this project, several python programs were 
developed.

### Programs

- `play.py` is the modified version of 
[terminal Dots and Boxes GUI](https://gist.github.com/stephenroller/3163995) 
implemented by stephenroller.

Running the ```$ python play.py``` in the terminal you can play against my 
best trained bot2(10) or you can easily modify this file to play against 
another automated player.

- `dots_and_boxes.py` contains all the global variables (i.e. BOARD_SIZE) 
and functions that can be universally used for developing, training and testing
new automatic players. It is imported in all other used python programs.

- `bot1.py` contains simple heuristics for automatic players

- `bot2.py` contains functions used for training, saving and using a 
powerfull player which plays last k moves optimally and the rest by simple 
heuristics always4never3 inpired by 
[another Dots and Boxes automatic player](https://github.com/Normangorman/DeepBox)

- `train1.py` is not really working, it was intended to provide functions 
to train Q function as MLP neural network (or decision tree) but it had very poor 
performance while testing its parts so I gave up trying and didn't even finish it.

- `train2.py` can be used to training and testing of the Q-learning automated 
player - just uncomment the bottom part and play with it. Or you can try to
change the training process.

    - If trained Q is saved (recommended as json) it can be used in play.py
by loading Q and using function `get_Q_move_and_update` to get moves 
in play.py on line 329. inserting 

```move,update = get_Q_move_and_update(Q,board,l_rate=0,random_move_prob=1)
   selected_x, selected_y = move
```
instead of currend code for getting bot moves.



