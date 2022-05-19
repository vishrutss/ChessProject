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

    """ 
    Function to execute the move specified by the Player
    """
    def make_move(self, move):
        if self.board[move.start_row][move.start_col] != "--":
            self.board[move.start_row][move.start_col] = "--"
            self.board[move.end_row][move.end_col] = move.piece_moved
            self.moveLog.append(move) # Logging each move
            self.whiteToMove = not self.whiteToMove # Switch turns

    """
    Function to undo the last move
    """
    def undo_move(self):
        if len(self.moveLog) != 0: # Make sure at least 1 move has been made
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove # Switch turns back

    """
    Function to determine valid moves considering checks
    """
    def getValidMoves(self):
        return self.getAllPossibleMoves() #For now no need to consider checks

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
        if self.whiteToMove: # Moves for white pawn
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

        elif not self.whiteToMove: # Moves for black pawn
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
