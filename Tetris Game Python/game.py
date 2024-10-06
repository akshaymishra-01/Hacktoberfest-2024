#!/usr/bin/python

"""
Python implementation of text-mode version of the Tetris game
with a scoring system and levels.
"""

import os
import random
import sys
import time
from copy import deepcopy

# DECLARE ALL THE CONSTANTS
BOARD_SIZE = 20
# Extra two are for the walls, playing area will have size as BOARD_SIZE
EFF_BOARD_SIZE = BOARD_SIZE + 2

PIECES = [

    [[1], [1], [1], [1]],

    [[1, 0],
     [1, 0],
     [1, 1]],

    [[0, 1],
     [0, 1],
     [1, 1]],

    [[0, 1],
     [1, 1],
     [1, 0]],

    [[1, 1],
     [1, 1]]

]

# Constants for user input
MOVE_LEFT = 'a'
MOVE_RIGHT = 'd'
ROTATE_ANTICLOCKWISE = 'w'
ROTATE_CLOCKWISE = 's'
NO_MOVE = 'e'
QUIT_GAME = 'q'

# Scoring system constants
LINES_PER_LEVEL = 10
SCORE_PER_LINE = 100
LEVEL_UP_BONUS = 500

def print_board(board, curr_piece, piece_pos, score, level, error_message=''):
    """
    Prints the game board, score, level, and instructions.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Text mode version of the TETRIS game\n\n")

    board_copy = deepcopy(board)
    curr_piece_size_x = len(curr_piece)
    curr_piece_size_y = len(curr_piece[0])
    for i in range(curr_piece_size_x):
        for j in range(curr_piece_size_y):
            board_copy[piece_pos[0]+i][piece_pos[1]+j] = curr_piece[i][j] | board[piece_pos[0]+i][piece_pos[1]+j]

    # Print the board to STDOUT
    for i in range(EFF_BOARD_SIZE):
        for j in range(EFF_BOARD_SIZE):
            if board_copy[i][j] == 1:
                print("*", end='')
            else:
                print(" ", end='')
        print("")

    print(f"\nScore: {score}  |  Level: {level}\n")
    print("Quick play instructions:\n")
    print(" - a (return): move piece left")
    print(" - d (return): move piece right")
    print(" - w (return): rotate piece counter clockwise")
    print(" - s (return): rotate piece clockwise")
    print(" - e (return): just move the piece downwards as is")
    print(" - q (return): to quit the game anytime")

    if error_message:
        print(error_message)
    print("Your move:",)


def init_board():
    board = [[0 for x in range(EFF_BOARD_SIZE)] for y in range(EFF_BOARD_SIZE)]
    for i in range(EFF_BOARD_SIZE):
        board[i][0] = 1
    for i in range(EFF_BOARD_SIZE):
        board[EFF_BOARD_SIZE-1][i] = 1
    for i in range(EFF_BOARD_SIZE):
        board[i][EFF_BOARD_SIZE-1] = 1
    return board


def get_random_piece():
    idx = random.randrange(len(PIECES))
    return PIECES[idx]


def get_random_position(curr_piece):
    curr_piece_size = len(curr_piece)
    x = 0
    y = random.randrange(1, EFF_BOARD_SIZE-curr_piece_size)
    return [x, y]


def is_game_over(board, curr_piece, piece_pos):
    if not can_move_down(board, curr_piece, piece_pos) and piece_pos[0] == 0:
        return True
    return False


def get_left_move(piece_pos):
    new_piece_pos = [piece_pos[0], piece_pos[1] - 1]
    return new_piece_pos


def get_right_move(piece_pos):
    new_piece_pos = [piece_pos[0], piece_pos[1] + 1]
    return new_piece_pos


def get_down_move(piece_pos):
    new_piece_pos = [piece_pos[0] + 1, piece_pos[1]]
    return new_piece_pos


def rotate_clockwise(piece):
    piece_copy = deepcopy(piece)
    reverse_piece = piece_copy[::-1]
    return list(list(elem) for elem in zip(*reverse_piece))


def rotate_anticlockwise(piece):
    piece_copy = deepcopy(piece)
    piece_1 = rotate_clockwise(piece_copy)
    piece_2 = rotate_clockwise(piece_1)
    return rotate_clockwise(piece_2)


def merge_board_and_piece(board, curr_piece, piece_pos):
    curr_piece_size_x = len(curr_piece)
    curr_piece_size_y = len(curr_piece[0])
    for i in range(curr_piece_size_x):
        for j in range(curr_piece_size_y):
            board[piece_pos[0]+i][piece_pos[1]+j] = curr_piece[i][j] | board[piece_pos[0]+i][piece_pos[1]+j]

    empty_row = [0]*EFF_BOARD_SIZE
    empty_row[0] = 1
    empty_row[EFF_BOARD_SIZE-1] = 1

    filled_row = [1]*EFF_BOARD_SIZE
    filled_rows = 0
    for row in board:
        if row == filled_row:
            filled_rows += 1

    filled_rows -= 1

    for i in range(filled_rows):
        board.remove(filled_row)

    for i in range(filled_rows):
        board.insert(0, empty_row)

    return filled_rows


def overlap_check(board, curr_piece, piece_pos):
    curr_piece_size_x = len(curr_piece)
    curr_piece_size_y = len(curr_piece[0])
    for i in range(curr_piece_size_x):
        for j in range(curr_piece_size_y):
            if board[piece_pos[0]+i][piece_pos[1]+j] == 1 and curr_piece[i][j] == 1:
                return False
    return True


def can_move_left(board, curr_piece, piece_pos):
    piece_pos = get_left_move(piece_pos)
    return overlap_check(board, curr_piece, piece_pos)


def can_move_right(board, curr_piece, piece_pos):
    piece_pos = get_right_move(piece_pos)
    return overlap_check(board, curr_piece, piece_pos)


def can_move_down(board, curr_piece, piece_pos):
    piece_pos = get_down_move(piece_pos)
    return overlap_check(board, curr_piece, piece_pos)


def can_rotate_anticlockwise(board, curr_piece, piece_pos):
    curr_piece = rotate_anticlockwise(curr_piece)
    return overlap_check(board, curr_piece, piece_pos)


def can_rotate_clockwise(board, curr_piece, piece_pos):
    curr_piece = rotate_clockwise(curr_piece)
    return overlap_check(board, curr_piece, piece_pos)


def play_game():
    board = init_board()
    curr_piece = get_random_piece()
    piece_pos = get_random_position(curr_piece)

    score = 0
    level = 1
    lines_cleared = 0
    piece_speed = 1.0

    print_board(board, curr_piece, piece_pos, score, level)

    player_move = input()
    while not is_game_over(board, curr_piece, piece_pos):
        ERR_MSG = ""
        do_move_down = False
        if player_move == MOVE_LEFT:
            if can_move_left(board, curr_piece, piece_pos):
                piece_pos = get_left_move(piece_pos)
                do_move_down = True
            else:
                ERR_MSG = "Cannot move left!"
        elif player_move == MOVE_RIGHT:
            if can_move_right(board, curr_piece, piece_pos):
                piece_pos = get_right_move(piece_pos)
                do_move_down = True
            else:
                ERR_MSG = "Cannot move right!"
        elif player_move == ROTATE_ANTICLOCKWISE:
            if can_rotate_anticlockwise(board, curr_piece, piece_pos):
                curr_piece = rotate_anticlockwise(curr_piece)
                do_move_down = True
            else:
                ERR_MSG = "Cannot rotate anti-clockwise!"
        elif player_move == ROTATE_CLOCKWISE:
            if can_rotate_clockwise(board, curr_piece, piece_pos):
                curr_piece = rotate_clockwise(curr_piece)
                do_move_down = True
            else:
                ERR_MSG = "Cannot rotate clockwise!"
        elif player_move == NO_MOVE:
            do_move_down = True
        elif player_move == QUIT_GAME:
            print("Bye. Thank you for playing!")
            sys.exit(0)
        else:
            ERR_MSG = "That is not a valid move!"

        if do_move_down and can_move_down(board, curr_piece, piece_pos):
            piece_pos = get_down_move(piece_pos)

        if not can_move_down(board, curr_piece, piece_pos):
            filled_rows = merge_board_and_piece(board, curr_piece, piece_pos)
            score += filled_rows * SCORE_PER_LINE
            lines_cleared += filled_rows

            if lines_cleared >= LINES_PER_LEVEL:
                level += 1
                piece_speed *= 0.9  # increase speed with each level
                lines_cleared = 0  # reset lines count for new level
                score += LEVEL_UP_BONUS  # level up bonus

            curr_piece = get_random_piece()
            piece_pos = get_random_position(curr_piece)

        print_board(board, curr_piece, piece_pos, score, level, ERR_MSG)
        time.sleep(piece_speed)
        player_move = input()

    print("GAME OVER")
    sys.exit(0)


if __name__ == "__main__":
    play_game()
