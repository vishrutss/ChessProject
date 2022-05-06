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
    print(game_state.board)
    loadImages()
    running = True
    selected_square = () # Keep tract of last click
    player_click = [] # Keep track of player clicks
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse click handlers
            elif e.type == p.MOUSEBUTTONDOWN:
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
                    if move in valid_moves:  # Check if the move is valid
                        game_state.make_move(move)
                        move_made = True
                    selected_square = ()  # Reset player click
                    player_click = []
            # Key press handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Undo move by pressing Z on the keyboard
                    game_state.undo_move()
                    move_made = True

        if move_made:  # After a move is made we need to generate all possible moves again
            valid_moves = game_state.getValidMoves()
            move_made = False

        drawGameState(screen, game_state)
        clock.tick(MAX_FPS)
        p.display.flip()

"""
Handles all graphics related to current game state
"""
def drawGameState(screen, game_state):
    drawOnBoard(screen) # Draw the squares on the board
    drawPieces(screen, game_state.board) # Draw the pieces on the board


"""
Draw the squares on the board. Top left square is always light
"""
def drawOnBoard(screen):
    colors = [p.Color("white"), p.Color("brown")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) %2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


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
























