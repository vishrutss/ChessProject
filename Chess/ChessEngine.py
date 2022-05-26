"""
Responsible for storing all the info of the current state of the chess game. Also, responsible for determining possible
moves based on current state. Also keeps move log
"""


class GameState:
    def __init__(self):
        # Initialize the board according to the positions of the pieces.
        # First letter denotes color of the pieces "b" or "w"
        # Second letter denotes the rank of the pieces "R - Rook, N - Knight, B - Bishop, Q - Queen, K - King"
        # "--" denotes empty block.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunction = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                             'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False

    """ 
    Function to execute the move specified by the Player
    """
    def make_move(self, move):
        if self.board[move.start_row][move.start_col] != "--":
            self.board[move.start_row][move.start_col] = "--"
            self.board[move.end_row][move.end_col] = move.piece_moved
            self.moveLog.append(move) # Logging each move
            self.whiteToMove = not self.whiteToMove # Switch turns
            if move.piece_moved == 'wK': # Update Kings location if King was moved
                self.whiteKingLocation = (move.end_row, move.end_col)
            elif move.piece_moved == 'bK': # Update Kings location if King was moved
                self.blackKingLocation = (move.end_row, move.end_col)

            if move.pawn_promotion:  # Pawn promotion
                self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

    """
    Function to undo the last move
    """
    def undo_move(self):
        if len(self.moveLog) != 0:  # Make sure at least 1 move has been made
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove # Switch turns back
            if move.piece_moved == 'wK':  # Update Kings location if King was moved
                self.whiteKingLocation = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':  # Update Kings location if King was moved
                self.blackKingLocation = (move.start_row, move.start_col)

    """
    Function to determine valid moves considering checks
    """
    def getValidMoves(self):
        # 1.) Generate all possible moves
        moves = self.getAllPossibleMoves()
        # 2.) For each move, make the move
        for i in range(len(moves)-1, -1, -1):  # Going backwards through the list
            self.make_move(moves[i])
            # 3.) Generate all your opponents moves
            # 4.) For each of your opponents move check if they attack your King
            # Switch turns back for in_check() because make_move() switches turns first
            self.whiteToMove = not self.whiteToMove
            if self.in_check():
                moves.remove(moves[i])  # 5.) Not a valid move since they attack your King
            self.whiteToMove = not self.whiteToMove  # Switch turns back
            self.undo_move()
        if len(moves) == 0:  # Either checkmate or stalemate
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return moves

    """
    Determine if player is in check
    """
    def in_check(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """
    Determine if the enemy can attack square (r, c)
    """
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # Switch to opponents turn
        opp_moves = self.getAllPossibleMoves()  # Generate all your opponents moves
        self.whiteToMove = not self.whiteToMove  # Switch back turn
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:  # Square is under attack
                return True
        return False

    """
    Function to determine valid moves without considering checks
    """
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of cols in selected row
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)  # Calls appropriate move function based on piece type.
                    # Refer Line 23
        return moves

    """
    Get all Pawn moves at a specific location and add to move list
    """
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # Moves for white pawn
            if self.board[r-1][c] == "--":  # Check 1 square ahead is empty
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":  # Condition to check if the Pawn can move 2 squares
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: # Capture to the left
                if self.board[r-1][c-1][0] == 'b':  # Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: # Capture to the right
                if self.board[r-1][c+1][0] == 'b':  # Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))

        elif not self.whiteToMove:  # Moves for black pawn
            if self.board[r+1][c] == "--":  # Check 1 square ahead is empty
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":  # Condition to check if the Pawn can move 2 squares
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c+1 <= 7:  # Capture to the right
                if self.board[r+1][c+1][0] == 'w':  # Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
            if c-1 >= 0:  # Capture to the left
                if self.board[r+1][c-1][0] == 'w':  # Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))




    """
    Get all Rook moves at a specific location and add to move list
    """
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (0, 1), (1, 0))
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: # To make sure piece doesn't move outside the board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--": # Empty space
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color: # Enemy piece present
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else: # Friendly piece present
                        break
                else: # If piece tries to move outside the board
                    break


    """
    Get all Knight moves at a specific location and add to move list
    """
    def getKnightMoves(self, r, c, moves):
        move_set = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1), (2, 1), (1, -2), (1, 2)) # All possible moves
        enemy_color = "b" if self.whiteToMove else "w"
        for m in move_set:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # To make sure piece doesn't move outside the board
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    """
    Get all Bishop moves at a specific location and add to move list
    """
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # To make sure piece doesn't move outside the board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # Empty space
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # Enemy piece present
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # Friendly piece present
                        break
                else:  # If piece tries to move outside the board
                    break

    """
    Get all Queen moves at a specific location and add to move list
    """
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    """
    Get all King moves at a specific location and add to move list
    """
    def getKingMoves(self, r, c, moves):
        move_set = ((-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1))  # All possible moves
        enemy_color = "b" if self.whiteToMove else "w"
        for i in range(0, 8):
            end_row = r + move_set[i][0]
            end_col = c + move_set[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # To make sure piece doesn't move outside the board
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

class Move:
    # maps keys to values
    # key : value
    ranks_to_rows = {"1": 7, "2": 6,  "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.pawn_promotion = False
        if (self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 7):
            self.pawn_promotion = True
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    """
    Overriding equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):  # Get coordinates in real Chess notation like "a2", "b5", etc.
        return self.getRankFile(self.start_row, self.start_col) + self.getRankFile(self.end_row, self.end_col)

    def getRankFile(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
