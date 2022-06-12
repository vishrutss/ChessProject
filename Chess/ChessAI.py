import random
piece_score = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
"""
Picks a random move
"""
def findRandomMove(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]


"""
Pick the best move based on how many pieces can be captured
"""
def findBestMove(game_state, valid_moves):
    turn_multiplier = 1 if game_state.whiteToMove else -1
    opponent_min_max_score = CHECKMATE
    best_player_move = None
    for player_move in valid_moves:
        game_state.make_move(player_move)
        opponent_move = game_state.getValidMoves()
        random.shuffle(valid_moves)
        opponent_max_score = -CHECKMATE
        for opp in opponent_move:
            game_state.make_move(opp)
            if game_state.checkmate:
                score = -turn_multiplier * CHECKMATE
            elif game_state.stalemate:
                score = STALEMATE
            else:
                score = -turn_multiplier * scoreBoard(game_state.board)  # For white score needs to be as high as
            if score > opponent_max_score:                               # possible and for black the score needs to be
                opponent_max_score = score                               # as negative as possible
            game_state.undo_move()
        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        game_state.undo_move()
    return best_player_move


"""
Score the board based on the pieces on the board
"""
def scoreBoard(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]
    return score
