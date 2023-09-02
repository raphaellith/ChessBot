from chess import *
from random import choice
from time import time
from Audio import say


def num_pieces_by_color(board, color):
    return sum([board.color_at(i) == color for i in SQUARES])


class ChessBot:
    def __init__(self, moves_ahead, cautiousness, defense_to_attack_ratio=6):
        self.moves_ahead = moves_ahead
        self.cautiousness = cautiousness

        def move_eval_func(board_before, board_after, my_color):
            their_color = not my_color

            my_pieces_loss = num_pieces_by_color(board_before, my_color) - num_pieces_by_color(board_after, my_color)
            their_pieces_loss = num_pieces_by_color(board_before, their_color) - num_pieces_by_color(board_after, their_color)

            net_enemy_loss = their_pieces_loss - my_pieces_loss * defense_to_attack_ratio  # The greater the better
            return net_enemy_loss

        self.move_eval_func = move_eval_func
        
    def best_n_moves(self, board, n=None):
        my_color = board.turn
        result = []
        
        legal_moves = list(board.legal_moves)

        legal_moves = [move for move in legal_moves if len(board.attackers(not my_color, move.to_square)) == 0]

        if len(legal_moves) == 0:
            return None

        for move in legal_moves:
            score = 0

            for _ in range(self.cautiousness):
                hypothetical_board_before, hypothetical_board_after = board.copy(), board.copy()
                hypothetical_board_after.push(move)

                for _ in range(self.moves_ahead):
                    if not hypothetical_board_after.is_game_over():
                        hypothetical_board_after.push(choice(list(hypothetical_board_after.legal_moves)))
                    else:
                        break
                score += self.move_eval_func(hypothetical_board_before, hypothetical_board_after, my_color)
            score /= self.cautiousness

            result.append((move, score))

        result = sorted(result, key=lambda x: x[1], reverse=True)

        if n is None:
            return result
        else:
            return result[:n]
    
    def best_move_and_confidence(self, board):
        my_color = board.turn
        result = []

        legal_moves = list(board.legal_moves)

        legal_moves = [move for move in legal_moves if not board.is_attacked_by(not my_color, move.to_square)]

        if len(legal_moves) == 0:
            return None

        for move in legal_moves:
            score = 0
            for _ in range(self.cautiousness):
                hypothetical_board_before, hypothetical_board_after = board.copy(), board.copy()

                hypothetical_board_after.push(move)
                for _ in range(self.moves_ahead):
                    if not hypothetical_board_after.is_game_over():
                        hypothetical_board_after.push(choice(list(hypothetical_board_after.legal_moves)))
                    else:
                        break
                score += self.move_eval_func(hypothetical_board_before, hypothetical_board_after, my_color)
            score /= self.cautiousness

            result.append((move, score))

        return max(result, key=lambda x: x[1])

    def play(self, my_color_is_white, read_aloud=False):
        board = Board()
        if my_color_is_white:
            my_color = WHITE
        else:
            my_color = BLACK

        while board.outcome() is None:
            if board.turn == my_color:
                start_time = time()
                best_five_moves = self.best_n_moves(board, n=5)

                print(f'Best 5 moves ({round(time() - start_time, 2)} seconds):')
                print()
                spoken_message = ''
                for i, move_and_confidence in enumerate(best_five_moves):
                    move, confidence = move_and_confidence
                    from_square = move.from_square
                    to_square = move.to_square
                    print(
                        f'{i}\tMove {piece_name(board.piece_at(from_square).piece_type)} from {square_name(from_square)} to {square_name(to_square)}\t\tConfidence: {round(confidence, 2)}'
                    )

                    if i == 0:
                        spoken_message = f'Move {piece_name(board.piece_at(from_square).piece_type)} from {square_name(from_square)} to {square_name(to_square)}'

                if read_aloud:
                    say(spoken_message)
                print()
                while board.turn == my_color:
                    print('To accept, input 0-4. Alternatively, input a manual move (e.g. "a1-b2").')
                    move_chosen = input('>>> ')
                    if move_chosen in '01234' and len(move_chosen) == 1:
                        if move_chosen == '':
                            move_chosen = '0'
                        board.push(best_five_moves[int(move_chosen)][0])
                    elif len(move_chosen) == 5:
                        from_square = parse_square(move_chosen[:2])
                        to_square = parse_square(move_chosen[3:])
                        move = Move(from_square=from_square, to_square=to_square)
                        if move in board.pseudo_legal_moves:
                            board.push(move)
                        else:
                            print('Move illegal. Try again.')
                    else:
                        print('Input not parsed successfully. Try again.')

            else:
                while board.turn != my_color:
                    print("Input enemy's move.")
                    their_move = input('>>> ')
                    try:
                        from_square = parse_square(their_move[:2])
                        to_square = parse_square(their_move[3:])

                        move = Move(from_square=from_square, to_square=to_square)

                        if move in board.pseudo_legal_moves:
                            board.push(move)
                        else:
                            print('Move illegal. Try again.')
                    except Exception:
                        print('Input not parsed successfully. Try again.')

            print()
            print('Current board:')
            print(board)
            print()
            print('-' * 50)
            print()

        outcome = board.outcome()
        if outcome.winner is None:
            print('Game has ended with a draw.')
        elif outcome.winner == WHITE:
            print(f'Game has ended with the white side as winner.')
        else:
            print(f'Game has ended with the black side as winner.')

        print(f'Reason: {outcome.termination.__str__().split(".")[1]}')
