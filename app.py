from flask import Flask, render_template, request, redirect, url_for,session,jsonify
from enum import Enum
import math
import random


app = Flask(__name__, template_folder='templates') 
app.secret_key = 'Secret Key'


#ENUM SELECTION FOR DIFFICULTY
class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

# Winning Matrix
w = [
    [[0, 0], [0, 1], [0, 2]],  
    [[1, 0], [1, 1], [1, 2]],  
    [[2, 0], [2, 1], [2, 2]],  
    [[0, 0], [1, 0], [2, 0]],  
    [[0, 1], [1, 1], [2, 1]],  
    [[0, 2], [1, 2], [2, 2]],  
    [[0, 0], [1, 1], [2, 2]],  
    [[0, 2], [1, 1], [2, 0]],  
]


#Check First Player
def get_symbols():
    first_player = session.get('FirstPlayer', 'HUMAN')
    if first_player == 'HUMAN':
        return 'O', 'X' 
    else:
        return 'X', 'O' 



#Default Route
@app.route('/')
def Home():

    if ('Board'  in session and 'Difficulty'in session):
        return redirect(url_for('start_game'))

    return render_template('home.html')


#Route TO Difficulty Page
@app.route('/difficulty', methods=['GET', 'POST'])
def select_difficulty():
    session.clear()
    return render_template('difficulty.html')

#Accepts Difficulty And Set It
@app.route('/SetDifficulty',methods=['GET','POST'])
def SetDifficulty():
    selected_value = request.form.get('difficulty')
    first_player = request.form.get('first_player') 
    
    if not selected_value or selected_value not in Difficulty.__members__:
        return redirect(url_for('select_difficulty'))
        
    session['Difficulty'] = selected_value
    session['FirstPlayer'] = first_player
    return redirect(url_for('start_game'))

#Route TO START Game Page
@app.route('/start-game',methods=['GET','POST'])
def start_game():
    selected_value = session.get('Difficulty')
    first_player = session.get('FirstPlayer', 'HUMAN')
    
    if not selected_value or selected_value not in Difficulty.__members__:
        return redirect(url_for('select_difficulty'))

    if 'Board' not in session:
        Board = [[' ', ' ', ' '],
                 [' ', ' ', ' '],
                 [' ', ' ', ' '] ]
        session['Board'] = Board
        
        if first_player == 'NPC':
            PlayerSymbol, NPCSymbol = get_symbols()
            NPC_MOVE(Board, selected_value, PlayerSymbol, NPCSymbol)
    

    current_board = session.get('Board')
    PlayerSymbol, NPCSymbol = get_symbols()

    ans = CheckWinner(current_board, PlayerSymbol, NPCSymbol)
    if ( ans == ' ' ):
        result = 'Make Your Move..'
    elif(ans == PlayerSymbol):
        result = 'Player Won'
    elif(ans == NPCSymbol):
        result = 'NPC Won'
    else:
        result = 'Tie'
   

    return render_template('game.html',difficulty = selected_value,Board=current_board,result=result )

#Handles Button Press Using Json Data from game Html Which Has Java Script To Control Real Time Updation Without Full Reload Of Website
@app.route('/play_turn', methods=['POST'])
def play_turn():

    data = request.get_json()
    row = int(data.get('row'))
    col = int(data.get('col'))

    current_board = session.get('Board')
    Difficulty = session.get('Difficulty') 
    PlayerSymbol, NPCSymbol = get_symbols()

    ans = CheckWinner(current_board, PlayerSymbol, NPCSymbol)

    if ( ans == ' ' ):
        result = 'Make Your Move..'
    elif(ans == PlayerSymbol):
        result = 'Player Won'
        
    elif(ans == NPCSymbol):
        result = 'NPC Won'
    else:
        result = 'Tie'

    if (current_board [row] [col] == ' ' and ans == ' '):
        current_board [row] [col] = PlayerSymbol
        session['Board'] = current_board
        session.modified = True
    else:
        return jsonify({
        "board": current_board,
        "result": result
    })


    ans = CheckWinner(current_board, PlayerSymbol, NPCSymbol)

    if(ans == ' '):
        NPC_MOVE(current_board, Difficulty, PlayerSymbol, NPCSymbol)

    ans = CheckWinner(current_board, PlayerSymbol, NPCSymbol)

    if ( ans == ' ' ):
        result = 'Make Your Move..'
    elif(ans == PlayerSymbol):
        result = 'Player Won'
        
    elif(ans == NPCSymbol):
        result = 'NPC Won'
    else:
        result = 'Tie'

    return jsonify({
        "board": current_board,
        "result": result
    })



#Check Winner Using Winner Matrix
def CheckWinner(Board, PlayerSymbol, NPCSymbol):
    
    for pair in w:
        one = Board[pair[0][0]][pair[0][1]] == Board[pair[1][0]][pair[1][1]]
        two = Board[pair[1][0]][pair[1][1]] == Board[pair[2][0]][pair[2][1]]

        
        if one and two and Board[pair[0][0]][pair[0][1]] != ' ':
            
            if Board[pair[0][0]][pair[0][1]] == PlayerSymbol:
                return PlayerSymbol
            else:
                return NPCSymbol
    
    
    for i in range(3):
        for j in range(3):
            if Board[i][j] == ' ': 
                return ' '

    return 'Tie'




#NPC MOVE FUNCTION
def NPC_MOVE(current_board, Difficulty, PlayerSymbol, NPCSymbol):
    Scores = {NPCSymbol: 1, PlayerSymbol: -1, 'Tie': 0}
    
    if Difficulty == "EASY":
        empty_cells = [(i, j) for i in range(3) for j in range(3) if current_board[i][j] == ' ']
        if empty_cells:
            i, j = random.choice(empty_cells)
            current_board[i][j] = NPCSymbol
            session['Board'] = current_board
            session.modified = True
        return

    if Difficulty == "MEDIUM" and random.random() < 0.3:
        empty_cells = [(i, j) for i in range(3) for j in range(3) if current_board[i][j] == ' ']
        if empty_cells:
            i, j = random.choice(empty_cells)
            current_board[i][j] = NPCSymbol
            session['Board'] = current_board
            session.modified = True
        return

    bestScore = -math.inf
    bestMove = None
    
    for i in range(3):
        for j in range(3):
            if current_board[i][j] == ' ':
                current_board[i][j] = NPCSymbol
                score = minimax(current_board, 0, -math.inf, math.inf, False, PlayerSymbol, NPCSymbol, Scores)
                current_board[i][j] = ' '
                
                if score > bestScore:
                    bestScore = score
                    bestMove = (i, j)
                    
    if bestMove:
        current_board[bestMove[0]][bestMove[1]] = NPCSymbol
        session['Board'] = current_board
        session.modified = True



#MINIMAX ALGORITHM USES ALPHA AND BETA FOR BETTER PERFORMANCE DOESNT REALLY USES DEPTH
def minimax(Board, depth, alpha, beta, isMaximizing, PlayerSymbol, NPCSymbol, Scores):
    result = CheckWinner(Board, PlayerSymbol, NPCSymbol)
    
    if result != ' ':
        return Scores.get(result)
        
    if isMaximizing:
        bestScore = -math.inf
        
        for i in range(3):
            brk = False
            for j in range(3):
                if Board[i][j] == ' ':
                    Board[i][j] = NPCSymbol
                    score = minimax(Board, depth + 1, alpha, beta, False, PlayerSymbol, NPCSymbol, Scores)
                    Board[i][j] = ' '
                    
                    bestScore = max(score, bestScore)
                    alpha = max(score, alpha)
                    
                    if beta <= alpha:
                        brk = True
                        break
            if brk:
                break
        return bestScore
    else:
        bestScore = math.inf
        
        for i in range(3):
            brk = False
            for j in range(3):
                if Board[i][j] == ' ':
                    Board[i][j] = PlayerSymbol
                    score = minimax(Board, depth + 1, alpha, beta, True, PlayerSymbol, NPCSymbol, Scores)
                    Board[i][j] = ' '
                    
                    bestScore = min(score, bestScore)
                    beta = min(score, beta)
                    
                    if beta <= alpha:
                        brk = True
                        break
            if brk:
                break
        return bestScore

#HOSTING THE APP
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)