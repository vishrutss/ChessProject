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
        self.enpassant_possible = ()  # Coordinates for a square where en passant is possible
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castleRightLog = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                            self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    """ 
    Function to execute the move specified by the Player
    """
    def make_move(self, move):
        if self.board[move.start_row][move.start_col] != "--":
            self.board[move.start_row][move.start_col] = "--"
            self.board[move.end_row][move.end_col] = move.piece_moved
            self.moveLog.append(move)  # Logging each move
            self.whiteToMove = not self.whiteToMove  # Switch turns
            if move.piece_moved == 'wK':  # Update Kings location if King was moved
                self.whiteKingLocation = (move.end_row, move.end_col)
            elif move.piece_moved == 'bK':  # Update Kings location if King was moved
                self.blackKingLocation = (move.end_row, move.end_col)

            # Pawn promotion
            if move.pawn_promotion:
                self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

            # Enpassant move
            if move.isEnpassant:
                self.board[move.start_row][move.end_col] = '--'  # Capturing the piece

            # Update enpassant_possible variable
            if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:  # Only on 2 square advances
                self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
            else:
                self.enpassant_possible = ()

            # Castle move
            if move.isCastle:
                if move.end_col - move.start_col == 2:  # King side castle
                    self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]  # Moves rook
                    self.board[move.end_row][move.end_col+1] = '--'  # Erase old rook
                else:  # Queen side castle
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]  # Moves rook
                    self.board[move.end_row][move.end_col-2] = '--'  # Erase old rook

            self.enpassant_possible_log.append(self.enpassant_possible)

            # Update current_castling_rights variable - only for King or Rook
            self.updateCastleRights(move)
            self.castleRightLog.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                    self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    """
    Function to undo the last move
    """
    def undo_move(self):
        if len(self.moveLog) != 0:  # Make sure at least 1 move has been made
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove  # Switch turns back
            if move.piece_moved == 'wK':  # Update Kings location if King was moved
                self.whiteKingLocation = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':  # Update Kings location if King was moved
                self.blackKingLocation = (move.start_row, move.start_col)

            # Undo enpassant move
            if move.isEnpassant:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured
            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            # Undo castling rights
            self.castleRightLog.pop()  # Remove the new castle rights for the undo move
            new_rights = self.castleRightLog[-1]  # Reset current castle rights to last one on list
            self.current_castling_rights = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)

            # Undo castling move
            if move.isCastle:
                if move.end_col - move.start_col == 2:  # King side castle
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]  # Moves rook
                    self.board[move.end_row][move.end_col-1] = '--'  # Erase old rook
                else:  # Queen side castle
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]  # Moves rook
                    self.board[move.end_row][move.end_col+1] = '--'  # Erase old rook
            self.checkmate = False
            self.stalemate = False

    """
    Function to update castle rights
    """
    def updateCastleRights(self, move):
        if move.piece_moved == 'wK':  # If piece was a white King
            self.current_castling_rights.wks = False  # After 1 move piece loses castling rights
            self.current_castling_rights.wqs = False
        elif move.piece_moved == 'bK':  # If piece was a black King
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # Left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # Right rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # Left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # Right rook
                    self.current_castling_rights.bks = False
        if move.piece_captured == 'wR':  # If rook is captured
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.bks = False

    """
    Function to determine valid moves considering checks
    """
    def getValidMoves(self):
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        # 1.) Generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
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
        self.enpassant_possible = temp_enpassant_possible  # Reset enpassant value back to original value
        self.current_castling_rights = temp_castle_rights
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
            if c-1 >= 0:  # Capture to the left
                if self.board[r-1][c-1][0] == 'b':  # Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassant=True))
            if c+1 <= 7:  # Capture to the right
                if self.board[r-1][c+1][0] == 'b':  # Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassant=True))

        else:  # Moves for black pawn
            if self.board[r+1][c] == "--":  # Check 1 square ahead is empty
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":  # Condition to check if the Pawn can move 2 squares
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c+1 <= 7:  # Capture to the right
                if self.board[r+1][c+1][0] == 'w':  # Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassant=True))
            if c-1 >= 0:  # Capture to the left
                if self.board[r+1][c-1][0] == 'w':  # Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassant=True))

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
    Get all Knight moves at a specific location and add to move list
    """
    def getKnightMoves(self, r, c, moves):
        move_set = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1), (2, 1), (1, -2), (1, 2))  # All possible moves
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

    """
    Get all possible castle moves for King at (r, c) and add to the list of moves
    """
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  # Cannot castle if in check
        if (self.whiteToMove and self.current_castling_rights.wks) or (not self.whiteToMove and self.current_castling_rights.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.current_castling_rights.wqs) or (not self.whiteToMove and self.current_castling_rights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastle=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastle=True))

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # maps keys to values
    # key : value
    ranks_to_rows = {"1": 7, "2": 6,  "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, isEnpassant=False, isCastle=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        # Pawn promotion code
        self.pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 7)
        # Enpassant code
        self.isEnpassant = isEnpassant
        if self.isEnpassant:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'
        self.isCapture = self.piece_captured != "--"
        # Castling
        self.isCastle = isCastle
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

    # Overriding str() function
    def __str__(self):
        # Castle move
        if self.isCastle:
            return "O-O" if self.end_col == 6 else "O-O-O"
        end_square = self.getRankFile(self.end_row, self.end_col)
        # Pawn move
        if self.piece_moved[1] == 'P':
            if self.isCapture:
                return self.cols_to_files[self.start_col]+" x "+end_square
            else:
                return end_square

        # Piece moves
        move_string = self.piece_moved[1]
        if self.isCapture:
            move_string += "x"
        return move_string + end_square
