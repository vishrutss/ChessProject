"""
Driver file. Handles user input. Displays current GameState object.
"""
import pygame as p
from Chess import ChessEngine

p.init()
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""
Initialize a global directory of images. It will be called exactly once in main
"""
def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'wP']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


"""
Main driver of the program. Handles user input and updating graphics
"""
def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False  # Flag variable to check if a move has been made
    animate = False  # Flag for when we want to animate a move
    game_over = False  # Flag for when the game is over
    print(game_state.board)
    loadImages()
    running = True
    selected_square = ()  # Keep tract of last click
    player_click = []  # Keep track of player clicks
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse click handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # Coordinates of the mouse click
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if selected_square == (row, col):  # Condition to check if the user has clicked the same square
                        selected_square = ()  # Reset
                        player_click = []  # Reset
                    else:  # First click
                        selected_square = (row, col)
                        player_click.append(selected_square)
                    if len(player_click) == 2:  # 2nd Click
                        move = ChessEngine.Move(player_click[0], player_click[1], game_state.board)
                        print(move.getChessNotation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:  # Check if the move is valid
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                selected_square = ()  # Reset player click
                                player_click = []
                        if not move_made:
                            player_click = [selected_square]
            # Key press handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo move by pressing Z on the keyboard
                    game_state.undo_move()
                    animate = False
                    move_made = True
                    game_over = False
                if e.key == p.K_r:  # Reset board by pressing R
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    selected_square = ()
                    player_click = []
                    move_made = False
                    animate = False
                    game_over = False

        if move_made:  # After a move is made we need to generate all possible moves again
            if animate:
                animate_move(game_state.moveLog[-1], screen, game_state.board, clock)
            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False

        drawGameState(screen, game_state, valid_moves, selected_square)

        if game_state.checkmate:
            game_over = True
            if game_state.whiteToMove:
                draw_text(screen, 'Black wins by checkmate')
            else:
                draw_text(screen, 'White wins by checkmate')
        elif game_state.stalemate:
            game_over = True
            draw_text(screen, 'Stalemate')
        clock.tick(MAX_FPS)
        p.display.flip()


"""
Highlight square selected and possible moves for piece selected
"""
def highlight_square(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Transparency value: 0 -> Transparent, 255 -> Opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # Highlight possible moves
            s.fill(p.Color('green'))
            for move in validMoves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (SQ_SIZE*move.end_col, SQ_SIZE*move.end_row))


"""
Handles all graphics related to current game state
"""
def drawGameState(screen, game_state, validMoves, sqSelected):
    drawOnBoard(screen)  # Draw the squares on the board
    highlight_square(screen, game_state, validMoves, sqSelected)
    drawPieces(screen, game_state.board)  # Draw the pieces on the board


"""
Draw the squares on the board. Top left square is always light
"""
def drawOnBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("light blue")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) %2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Animating movement of chess pieces
"""
def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 10  # Frames to move square
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = (move.start_row + dR*frame/frame_count, move.start_col + dC*frame/frame_count)
        drawOnBoard(screen)
        drawPieces(screen, board)
        # Erase piece moved from ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # Draw captured piece on rectangle
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_square)
        # Draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)  # FPS


"""
Draw text over the screen
"""
def draw_text(screen, text):
    font = p.font.SysFont('Calibri', 32, True, False)
    text_obj = font.render(text, False, 'Grey')
    text_location = p.Rect(0, 0, HEIGHT, WIDTH).move(WIDTH/2 - text_obj.get_width()/2, HEIGHT/2 - text_obj.get_height()/2)
    screen.blit(text_obj, text_location)
    text_obj = font.render(text, False, 'Red')
    screen.blit(text_obj, text_location.move(2,2))



"""
Draw pieces based on game state
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--': # Check if the piece is not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))



if __name__ == "__main__":
    main()
























