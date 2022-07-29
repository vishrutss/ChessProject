import random
piece_score = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
"""
Picks a random move
"""
def findRandomMove(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]


"""
Pick the best move based on how many pieces can be captured, min max without recursion
"""
def findBestMoveNoRecursion(game_state, valid_moves):
    turn_multiplier = 1 if game_state.whiteToMove else -1
    opponent_min_max_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        game_state.make_move(player_move)
        opponent_move = game_state.getValidMoves()
        if game_state.stalemate:
            opponent_max_score = STALEMATE
        elif game_state.checkmate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opp in opponent_move:
                game_state.make_move(opp)
                game_state.getValidMoves()
                if game_state.checkmate:
                    score = CHECKMATE
                elif game_state.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * scoreBoard(game_state.board)  # For white score needs to be as high as
                if score > opponent_max_score:                               # possible and for black the score needs to
                    opponent_max_score = score                               # be as negative as possible
                game_state.undo_move()
        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        game_state.undo_move()
    return best_player_move


"""
Helper method to make first recursive call
"""
def findBestMove(game_state, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    findMoveNegaMaxAlphaBeta(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.whiteToMove else -1)
    # findMoveMinMax(game_state, valid_moves, DEPTH, game_state.whiteToMove)
    return next_move


"""
Implementing Min Max algorithm to find best move
"""
def findMoveMinMax(game_state, valid_moves, depth, whiteToMove):
    global next_move
    if depth == 0:
        return scoreBoard(game_state)
    if whiteToMove:
        max_score = -CHECKMATE
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.getValidMoves()
            score = findMoveMinMax(game_state, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            game_state.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.getValidMoves()
            score = findMoveMinMax(game_state, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            game_state.undo_move()
        return min_score


"""
Implementing Nega max algorithm to find the best move
"""
def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta,  turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * scoreBoard(game_state)
    # Ordering all the moves - best to the worst so that we can start pruning worse move trees later on
    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.make_move(move)
        next_moves = game_state.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        game_state.undo_move()
        if max_score > alpha:  # Pruning happens here
            alpha = max_score
        if alpha >= beta:
            break
    return max_score



"""
Positive score is good for White and a negative score is good for Black
"""
def scoreBoard(game_state):
    if game_state.checkmate:
        if game_state.whiteToMove:
            return -CHECKMATE  # White wins
        else:
            return CHECKMATE  # Black wins
    elif game_state.stalemate:
        return STALEMATE
    score = 0
    for row in game_state.board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]
    return score
