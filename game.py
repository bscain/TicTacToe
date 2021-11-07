'''
Created on Oct 3, 2021

@author: Brian
'''

import random
import copy

from model import TicTacToeModel

class TicTacToeGame(object):
    '''
    classdocs
    '''
    BOARD_SIZE = 3
    EMPTY_VAL = 0
    X_VAL = -1
    O_VAL = 1
    
    GAME_NOT_OVER = 2
    X_WINS = -1
    O_WINS = 1
    DRAW = 0

    HORIZONTAL_SEPARATOR = ' | '
    VERTICAL_SEPARATOR = '----------'

    def __init__(self):
        '''
        Constructor
        '''
        self.resetGame()
        self.trainingHistory = []
    # end __init__
    
    
    def resetGame(self):
        """
        The Reset game operation, which resets the board back to all 0's.
        """
        self.board = []
        for _ in range(self.BOARD_SIZE):
            row = []
            for _ in range(self.BOARD_SIZE):
                row.append(self.EMPTY_VAL)
            self.board.append(row)
        self.boardHistory = []
    # end resetGame
        
    
    def printBoard(self, board=None):

        if (board==None):
            board = self.board
        
        data = ""
        for i in range(len(board)):
            data += "{val1} | {val2} | {val3}\n".format(val1 = board[i][0], val2 = board[i][1], val3 = board[i][2])
            if( i < len(board) - 1):
                data += self.VERTICAL_SEPARATOR + "\n"
            # end if
        # end for
        print(data.replace(str(self.X_VAL), "X").replace(str(self.O_VAL), "O").replace(str(self.EMPTY_VAL), " "))
        
    # end printBoard
            
    
    def getGameState(self):
        
        # Check the rows to see if there is a winner
        # Also rotate the board to check the columns
        # TODO not size agnostic
        gameState = self.GAME_NOT_OVER
        rotBoard = self._rotateBoard()
        comboBoard  = self.board + rotBoard
        
        for b in comboBoard:
            if (self.X_VAL == b[0] == b[1] == b[2]):
                gameState = self.X_WINS
            elif (self.O_VAL == b[0] == b[1] == b[2]):
                gameState = self.O_WINS
            # end if
        # end for
        
        if (gameState == self.GAME_NOT_OVER):
            if (self.X_VAL == self.board[0][0] == self.board[1][1] == self.board[2][2]):
                gameState = self.X_WINS
            elif (self.O_VAL == self.board[0][0] == self.board[1][1] == self.board[2][2]):
                gameState = self.O_WINS
        # end if game not over
        
        if (gameState == self.GAME_NOT_OVER):
            if (self.X_VAL == rotBoard[0][0] == rotBoard[1][1] == rotBoard[2][2]):
                gameState = self.X_WINS
            elif (self.O_VAL == rotBoard[0][0] == rotBoard[1][1] == rotBoard[2][2]):
                gameState = self.O_WINS
        # end if game not over
        
        if (gameState == self.GAME_NOT_OVER):
            if len(self.getAvailableMoves()) == 0:
                gameState = self.DRAW
            # end if
        # end if
        return gameState
        
        
        
    def getAvailableMoves(self):
        """
        This function searches through each of the board squares and returns the squares which contain a 0 as an 
        array coordinate tuples [(x1,y1), (x2, y2)]
        """
        retVal = []
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                if self.board[y][x] == self.EMPTY_VAL:
                    retVal.append([x,y])
        return retVal 
    
    def addToHistory(self, board):
        self.boardHistory.append(board)
    
    def printHistory(self, formatted = False):
        if formatted == False:
            for i in self.boardHistory:
                print(i)
        else:
            counter = 0
            for i in self.boardHistory:
                print("Move number: "  + str(counter))
                counter += 1
                self.printBoard(i)
        # end if
    # end printHistory
    
    def getTrainingHistory(self):
        return self.trainingHistory
    
    def move(self, position, player):
        assert player in [self.X_VAL, self.O_VAL]
        
        availableMoves = self.getAvailableMoves()
        if position in availableMoves:
            self.board[position[1]][position[0]] = player
            
        # Perform a deep copy (e.g., replicate) of the board to preserve the history
        self.addToHistory(copy.deepcopy(self.board))
    # end move
    
    # Simulates a random game using the system random function
    def simulateGame(self):
        
        player = self.X_VAL
        
        while self.getGameState() == self.GAME_NOT_OVER:
            move = random.choice(self.getAvailableMoves())
            self.move(move, player)
            
            # Swap players
            player = self.X_VAL if (player == self.O_VAL) else self.O_VAL 
            
        # end while
        
        #Log the game into a training data set
        for h in self.boardHistory:
            self.trainingHistory.append((self.getGameState(), copy.deepcopy(h)))
    # end simulateGame 
    
    def simulateNeuralNetworkGame(self, neuralPlayer, model):
        self.resetGame()
        player = self.X_VAL
        while self.getGameState() == self.GAME_NOT_OVER:
            if player == neuralPlayer:
                # Feed all of the available moves into into the Neural network and utilize it to predict the winner
                availableMoves = self.getAvailableMoves()
                
                
                # Set the max prediction to 0 as the network is predicting %s 
                maxPrediction = 0
                bestMove = availableMoves[0]
                
                for move in availableMoves:
                    boardCopy = copy.deepcopy(self.board)
                    boardCopy[move[0]][move[1]] = player
                    
                    # print(move)
                    value = model.predict(boardCopy, 2) #todo whats 0 e.g., index?
                    
                    if value > maxPrediction:
                        maxPrediction = value
                        bestMove = move
                    # end if
                # end for
                
                move = bestMove
                            
            else: # Random move player
                move = random.choice(self.getAvailableMoves())
            # end if
            
            # print("Move: " + str(move))
            self.move(move, player)
            # self.printBoard(self.board)
            # print("*"*20)            
            # Swap players
            player = self.X_VAL if (player == self.O_VAL) else self.O_VAL 
        #end while
        # self.printBoard(self.board)           
    
    def simulateNerualNetworkGames(self, model, player, numberOfGames = 10000):
        xWins = 0
        oWins = 0
        draws = 0
        
        for _ in range(numberOfGames):
            self.resetGame()
            self.simulateNeuralNetworkGame(self.X_VAL, model)
            if self.getGameState() == self.X_WINS:
                xWins += 1
            elif self.getGameState() == self.O_WINS:
                oWins += 1
            else:
                draws += 1
                
        total = xWins + oWins + draws
        print ('X Wins: ' + str(int(xWins * 100/ total)) + '%')
        print('O Wins: ' + str(int(oWins * 100 / total)) + '%')
        print('Draws: ' + str(int(draws * 100 / total)) + '%')
        
    def simulateGames(self, numberOfGames = 10000):
        
        xWins = 0
        oWins = 0
        draws = 0
        
        for _ in range(numberOfGames):
            self.resetGame()
            self.simulateGame()
            if self.getGameState() == self.X_WINS:
                xWins += 1
            elif self.getGameState() == self.O_WINS:
                oWins += 1
            else:
                draws += 1
                
        total = xWins + oWins + draws
        print ('X Wins: ' + str(int(xWins * 100/ total)) + '%')
        print('O Wins: ' + str(int(oWins * 100 / total)) + '%')
        print('Draws: ' + str(int(draws * 100 / total)) + '%')
        
    
    def _rotateBoard(self):
        return list(zip(*self.board[::-1]))
        
# end class TicTacToeGame

if __name__ == "__main__":
    game = TicTacToeGame()
    game.simulateGames(numberOfGames=1000)
    
    trainingData = game.getTrainingHistory()
    ticTacToeModel = TicTacToeModel(numberOfInputs=9, numberOfOutputs=3, epochs=100, batchSize=32)
    ticTacToeModel.train(trainingData)
    
    game.simulateNerualNetworkGames(ticTacToeModel, game.X_VAL)
    
#     game.simulateGame()
#     
#     game.printBoard()
#     state = game.getGameState()
#     if (state == game.X_WINS):
#         print ("X Won")
#     elif (state == game.O_WINS):
#         print ("O Won")
#     elif (state == game.DRAW):
#         print("Cats Game")
#         
#     game.printHistory(formatted=True)
#     
    