from chess import *
from random import choice
from time import time
from Funcs import read_out, num_pieces_by_color


class ChessBot:
    def __init__(self, moves_ahead, cautiousness, defense_to_attack_ratio=6):
        """
        A chess bot which generates the optimal moves in a chess game.

        The bot operates by generating all possible legal moves, evaluating the confidence of each move,
        and then outputting the top few moves.

        Given some board layout B, the confidence of a move M is rated using the following procedure:
        1. Set up a hypothetical board which is identical to the current board layout B.
        2. Perform move M.
        3. On this hypothetical board, randomly choose and perform one of the enemy's legal moves.
        4. Similarly, on the same board, respond by randomly choosing and performing one of the bot's legal move.
        5. Repeat steps 3 to 4 a number of times. The resultant (hypothetical) board layout is called B'.
        6. By comparing B and B' in terms of the number of white/black pieces, generate a "goodness" value for M.
        7. Repeat steps 1 to 6 a number of times. The confidence of M is set to the mean of all goodness values.

        In step 5, the number of times steps 3 to 4 are repeated can be controlled via the moves_ahead parameter.
        In step 7, the number of times steps 1 to 6 are repeated can be controlled via the cautiousness parameter.
        The defense_to_attack_ratio is taken into account when generating the goodness value in step 6.

        :param moves_ahead: The number of moves ahead the bot considers. Ideally set to between 5 and 15.
        :param cautiousness: The number of possibilities the bot considers. Ideally set to between 100 and 1000.
        :param defense_to_attack_ratio: How much the bot values defense over attack. Ideally set to betwen 3 and 10.
        """

        self.moves_ahead = moves_ahead
        self.cautiousness = cautiousness

        def move_eval_func(board_before, board_after, my_color):
            """
            :param board_before: The current board layout.
            :param board_after: The resultant layout of the hypothetical board.
            :param my_color: The side taken by the bot.
            :return: The goodness value for a move.
            """
            their_color = not my_color

            # Decrease in number of my pieces
            my_pieces_loss = num_pieces_by_color(board_before, my_color) - num_pieces_by_color(board_after, my_color)

            # Decrease in number of their pieces
            their_pieces_loss = num_pieces_by_color(board_before, their_color) - num_pieces_by_color(board_after, their_color)

            return their_pieces_loss - my_pieces_loss * defense_to_attack_ratio  # The greater the better

        self.move_eval_func = move_eval_func
        
    def best_n_moves_and_confidence(self, board, n=None):
        """
        :param board: The board for which the best n moves are to be generated.
        :param n: The number of optimal moves to be returned.
        :return: A list of tuples. Each tuple contains a move and its corresponding confidence score.
        """
        my_color = board.turn
        result = []

        # Get legal moves
        legal_moves = list(board.legal_moves)

        # Remove moves where the target square can be immediately attacked
        legal_moves = [move for move in legal_moves if len(board.attackers(not my_color, move.to_square)) == 0]

        # If there are no moves left in the list, return None
        if len(legal_moves) == 0:
            return None

        for move in legal_moves:
            # Confidence score
            score = 0

            for _ in range(self.cautiousness):
                # Hypothetical board layout is set to the current board layout
                hypothetical_board = board.copy()

                # Perform move in question
                hypothetical_board.push(move)

                for _ in range(self.moves_ahead):
                    # Perform random responses (as long as the game is not over)
                    if not hypothetical_board.is_game_over():
                        hypothetical_board.push(choice(list(hypothetical_board.legal_moves)))
                    else:
                        break
                # Add goodness value to score
                score += self.move_eval_func(board, hypothetical_board, my_color)

            # Divide by cautiousness to get mean
            score /= self.cautiousness

            # Append tuple to list
            result.append((move, score))

        # Sort list by descending confidence
        result = sorted(result, key=lambda x: x[1], reverse=True)

        if n is None:
            return result
        else:
            return result[:n]
    
    def best_move_and_confidence(self, board):
        """
        :param board: The board for which the best n moves are to be generated.
        :return: A tuple containing the best move and its corresponding confidence.
        """
        return self.best_n_moves_and_confidence(board, n=1)[0]

    def play(self, my_color_is_white, read_aloud=False):
        """
        Runs a bot demonstration in the console. Suitable for a real-life human-vs-bot game.

        Every time the bot is asked to make a move, it determines and displays the top 5 optimal moves, in descending
        order of confidence. You may choose to accept the move (in which case the move will be performed), or to
        manually input a move yourself. In the case of the latter, use the following format when inputting the move:

        [source position]-[destination position]

        For example: a1-a2. Do not use algebraic chess notation. The same goes for when the enemy's move is to be
        inputted. Other important instructions will be displayed in the console during the demonstration.

        If necessary, a read-aloud feature is provided. If this feature is enabled, the best move (as decided by the
        bot) will be read out through a speaker or headphones.

        :param my_color_is_white: True if the bot takes the white side; False otherwise.
        :param read_aloud: Whether the read-aloud feature is enabled. Defaults to False.
        """

        board = Board()
        if my_color_is_white:
            my_color = WHITE
        else:
            my_color = BLACK

        while board.outcome() is None:  # While the game is not over
            if board.turn == my_color:  # If it is the bot's turn
                start_time = time()

                best_five_moves = self.best_n_moves_and_confidence(board, n=5)

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

                    if i == 0:  # Formats the message to be read aloud
                        spoken_message = f'Move {piece_name(board.piece_at(from_square).piece_type)} from {square_name(from_square)} to {square_name(to_square)}'

                if read_aloud:
                    read_out(spoken_message)  # Reads message aloud
                print()
                while board.turn == my_color:
                    print('To accept, input 0-4. Alternatively, input a manual move (e.g. "a1-b2").')
                    move_chosen = input('>>> ')
                    if move_chosen in ('0', '1', '2', '3', '4'):
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

        # When the game has ended
        outcome = board.outcome()
        if outcome.winner is None:
            print('Game has ended with a draw.')
        elif outcome.winner == WHITE:
            print(f'Game has ended with the white side as winner.')
        else:
            print(f'Game has ended with the black side as winner.')

        # Prints out the cause for the termination of the game.
        # See https://python-chess.readthedocs.io/en/latest/core.html#chess.Termination
        print(f'Reason: {outcome.termination.__str__().split(".")[1]}')

