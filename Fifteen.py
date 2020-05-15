import sys
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QDialog, QInputDialog, QErrorMessage, QMessageBox, QLabel, QMainWindow
from random import randint
import simpleaudio as sa
import wave

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, '']
winner = ''

CELL_COUNT = 4
CELL_SIZE = 100
GRID_ORIGINX = 75
GRID_ORIGINY = 100

W_WIDTH = 1000
W_HEIGHT = 650

BLANK_ROW = 0
BLANK_COL = 0
row_index = []
col_index = []
lead_dict = {}
lead_keys = []
lead_vals = []

LEAD_ROW = 5
LEAD_COL = 3
LEAD_WIDTH = 100 # x
LEAD_HEIGHT = 75 # y
LEAD_ORIGINX = 600
LEAD_ORIGINY = 150
rank = [1, 2, 3, 4, 5]

winning_click = 0

class Fifteen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('15-Puzzle')
        self.setGeometry(100, 100, W_WIDTH, W_HEIGHT)
        self.__moves = 0
        self.__winning_move = False
        self.__board = [['', '', '', ''], \
                        ['', '', '', ''], \
                        ['', '', '', ''], \
                        ['', '', '', '']]
        self.generate_game()
        while self.is_solvable() != True or self.repeats_present() == True:
            self.generate_game()

        # Music and Sound Effect Instances
        self.__BTS = sa.WaveObject.from_wave_file('BTS_Go_Go_Instrumental.wav')
        self.__BTS_on = False
        self.__Mii = sa.WaveObject.from_wave_file('Mii_Channel_Music.wav')
        self.__Mii.play()
        self.__Mii_on = True
        self.__Click = sa.WaveObject.from_wave_file('Click.wav')
        self.__Winner = sa.WaveObject.from_wave_file('Winner.wav')

        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        # Drawing Background
        qp.setOpacity(0.5)
        qp.setBrush(QColor(185, 151, 91))
        qp.drawRect(0, 0, 1000, 650)
        qp.setOpacity(1)

        # Drawing Leaderboard
        qp.setFont(QFont("Arial", 36))
        qp.setPen(QPen(Qt.black, 40))
        qp.drawText(650, 90, "Leaderboard")
        qp.setFont(QFont("Arial", 18))
        qp.drawText(628, 135, "Rank")
        qp.drawText(728, 135, "Name")
        qp.drawText(825, 135, "Moves")

        lead_dict = {}
        lead_keys = []
        lead_vals = []
        with open('leaderboard.txt', 'r') as leaderboard:
            for line in leaderboard:
                # print(line)
                line = line.split()
                lead_dict[line[0]] = line[1]
        # print(lead_dict)
        for key in lead_dict.keys():
            lead_keys.append(key)
        for val in lead_dict.values():
            lead_vals.append(val)
        # print(lead_keys)
        # print(lead_vals)

        for r in range(LEAD_ROW):
            for c in range(LEAD_COL):
                if r%2 == 0:
                    qp.setBrush(QColor(17, 87, 64)) # Green
                else:
                    qp.setBrush(QColor(185, 151, 91)) # Gold

                qp.setFont(QFont("Arial", 16))
                qp.setPen(QPen(Qt.black, 2))
                qp.drawRect(LEAD_ORIGINX+c*LEAD_WIDTH, LEAD_ORIGINY+r*LEAD_HEIGHT, LEAD_WIDTH, LEAD_HEIGHT)

                if r%2 == 0:
                    qp.setPen(QColor(185, 151, 91)) # Gold
                    qp.setBrush(QColor(17, 87, 64)) # Green
                else:
                    qp.setPen(QColor(17, 87, 64))
                    qp.setBrush(QColor(185, 151, 91))

                if c == 0:
                    qp.drawText(LEAD_ORIGINX+c*LEAD_WIDTH+(LEAD_WIDTH//2.2), LEAD_ORIGINY+r*LEAD_HEIGHT+(LEAD_HEIGHT//2), \
                    str(rank[r]))
                elif c == 1:
                    qp.drawText(LEAD_ORIGINX+c*LEAD_WIDTH+(LEAD_WIDTH//3), LEAD_ORIGINY+r*LEAD_HEIGHT+(LEAD_HEIGHT//2), \
                    lead_keys[r])
                else:
                    qp.drawText(LEAD_ORIGINX+c*LEAD_WIDTH+(LEAD_WIDTH//2.5), LEAD_ORIGINY+r*LEAD_HEIGHT+(LEAD_HEIGHT//2), \
                    lead_vals[r])

        # Drawing Board
        for row in range(CELL_COUNT):
            for col in range(CELL_COUNT):
                if self.__board[row][col] != '':
                    qp.setBrush(QColor(17, 87, 64))
                    qp.setPen(QPen(Qt.black, 2))
                    qp.drawRect(GRID_ORIGINX+col*CELL_SIZE, GRID_ORIGINY+row*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    if len(str(self.__board[row][col])) < 2:
                        qp.setFont(QFont("Arial", 20))
                        qp.setPen(QColor(185, 151, 91))
                        qp.drawText(GRID_ORIGINX+col*CELL_SIZE+(CELL_SIZE/2.2), GRID_ORIGINY+row*CELL_SIZE+(CELL_SIZE/1.8), \
                        str(self.__board[row][col]))
                    else:
                        qp.setFont(QFont("Arial", 20))
                        qp.setPen(QColor(185, 151, 91))
                        qp.drawText(GRID_ORIGINX+col*CELL_SIZE+(CELL_SIZE/2.4), GRID_ORIGINY+row*CELL_SIZE+(CELL_SIZE/1.8), \
                        str(self.__board[row][col]))
                else:
                    qp.setBrush(QColor(185, 151, 91))
                    qp.setPen(QPen(Qt.black, 2))
                    qp.drawRect(GRID_ORIGINX+col*CELL_SIZE, GRID_ORIGINY+row*CELL_SIZE, CELL_SIZE, CELL_SIZE)

        # Winner Mode
        if self.is_winner() == True:
            qp.setPen(QPen(Qt.red))
            qp.setFont(QFont("Arial", 20))
            qp.drawText(GRID_ORIGINX*2.4, GRID_ORIGINY-20, "Game Over! You Win!")

        # Recording Moves
        qp.setPen(QPen(Qt.blue))
        qp.setFont(QFont("Arial", 14))
        qp.drawText(75, 550, ("Moves: " + str(self.__moves)))

        # Mii Music Button
        qp.setPen(QPen(Qt.black, 1))
        qp.setBrush(QColor(17, 87, 64)) # Green
        qp.drawRect(185, 535, 75, 20)
        qp.setPen(QColor(185, 151, 91)) # Gold
        qp.setFont(QFont("Arial", 14))
        qp.drawText(198, 550, "Play Mii")

        # BTS Music Button
        qp.setPen(QPen(Qt.black, 1))
        qp.drawRect(295, 535, 75, 20)
        qp.setPen(QColor(185, 151, 91)) # Gold
        qp.setFont(QFont("Arial", 14))
        qp.drawText(305, 550, "Play BTS")

        # No Music
        qp.setPen(QPen(Qt.black, 1))
        qp.drawRect(405, 535, 72, 20)
        qp.setPen(QColor(185, 151, 91)) # Gold
        qp.setFont(QFont("Arial", 14))
        qp.drawText(412, 550, "No Music")

        qp.end()

    def mousePressEvent(self, event):
        for row in range(CELL_COUNT):
            for col in range(CELL_COUNT):
                if self.__board[row][col] == '':
                    BLANK_ROW = row
                    BLANK_COL = col
                    #print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)

        #print("x: ", event.x(), " y: ", event.y())
        if self.is_winner() == False:
            if (100 <= event.y() <= 505) and (75 <= event.x() <= 475):
                row = (event.y() - GRID_ORIGINY) // CELL_SIZE
                col = (event.x() - GRID_ORIGINX) // CELL_SIZE
                # print("Click: ", row, col)
                if (row != BLANK_ROW and col == BLANK_COL) or (row == BLANK_ROW and col != BLANK_COL):

                    value = self.__board[row][col]

                    if row - BLANK_ROW == 1 or BLANK_ROW - row == 1:
                        self.__Click.play()
                        temp_row = BLANK_ROW
                        self.__board[row][col] = ''
                        self.__board[temp_row][col] = value
                        BLANK_ROW = row
                        self.__moves += 1
                        # print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)
                    elif col - BLANK_COL == 1 or BLANK_COL - col == 1:
                        self.__Click.play()
                        temp_col = BLANK_COL
                        self.__board[row][col] = ''
                        self.__board[row][temp_col] = value
                        BLANK_COL = col
                        self.__moves += 1
                        # print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)
                    elif BLANK_ROW - row == 2:
                        self.__Click.play()
                        temp_row = BLANK_ROW
                        temp_val = self.__board[row+1][col]
                        self.__board[row][col] = ''
                        self.__board[row+1][col] = value
                        self.__board[temp_row][col] = temp_val
                        BLANK_ROW = row
                        self.__moves += 2
                        # print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)
                    elif row - BLANK_ROW == 2:
                        self.__Click.play()
                        temp_row = BLANK_ROW
                        temp_val = self.__board[row-1][col]
                        self.__board[row][col] = ''
                        self.__board[row-1][col] = value
                        self.__board[temp_row][col] = temp_val
                        BLANK_ROW = row
                        self.__moves += 2
                        # print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)
                    elif BLANK_COL - col == 2:
                        self.__Click.play()
                        temp_col = BLANK_COL
                        temp_val = self.__board[row][col+1]
                        self.__board[row][col] = ''
                        self.__board[row][col+1] = value
                        self.__board[row][temp_col] = temp_val
                        BLANK_COL = col
                        self.__moves += 2
                        # print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)
                    elif col - BLANK_COL == 2:
                        self.__Click.play()
                        temp_col = BLANK_COL
                        temp_val = self.__board[row][col-1]
                        self.__board[row][col] = ''
                        self.__board[row][col-1] = value
                        self.__board[row][temp_col] = temp_val
                        BLANK_COL = col
                        self.__moves += 2
                        # print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)
                    elif BLANK_ROW - row == 3:
                        self.__Click.play()
                        temp_row = BLANK_ROW
                        temp_val1 = self.__board[row+2][col]
                        temp_val2 = self.__board[row+1][col]
                        self.__board[row][col] = ''
                        self.__board[temp_row][col] = temp_val1
                        self.__board[row+2][col] = temp_val2
                        self.__board[row+1][col] = value
                        BLANK_ROW = row
                        self.__moves += 3
                        # print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)
                    elif row - BLANK_ROW == 3:
                        self.__Click.play()
                        temp_row = BLANK_ROW
                        temp_val1 = self.__board[row-2][col]
                        temp_val2 = self.__board[row-1][col]
                        self.__board[row][col] = ''
                        self.__board[temp_row][col] = temp_val1
                        self.__board[row-2][col] = temp_val2
                        self.__board[row-1][col] = value
                        BLANK_ROW = row
                        self.__moves += 3
                        # print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)
                    elif BLANK_COL - col == 3:
                        self.__Click.play()
                        temp_col = BLANK_COL
                        temp_val1 = self.__board[row][col+2]
                        temp_val2 = self.__board[row][col+1]
                        self.__board[row][col] = ''
                        self.__board[row][temp_col] = temp_val1
                        self.__board[row][col+2] = temp_val2
                        self.__board[row][col+1] = value
                        BLANK_COL = col
                        self.__moves += 3
                        # print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)
                    else:
                        self.__Click.play()
                        temp_col = BLANK_COL
                        temp_val1 = self.__board[row][col-2]
                        temp_val2 = self.__board[row][col-1]
                        self.__board[row][col] = ''
                        self.__board[row][temp_col] = temp_val1
                        self.__board[row][col-2] = temp_val2
                        self.__board[row][col-1] = value
                        BLANK_COL = col
                        self.__moves += 3
                        # print("Blank Cell is at row ", BLANK_ROW, " and col ", BLANK_COL)

        if 185 <= event.x() <= 260 and 535 <= event.y() <= 555:
            print("Playing Mii")
            if self.__BTS_on == True:
                sa.stop_all()
                self.__BTS_on = False
            self.__Mii.play()
            self.__Mii_on = True

        if 295 <= event.x() <= 370 and 535 <= event.y() <= 555:
            print("Playing BTS")
            if self.__Mii_on == True:
                sa.stop_all()
                self.__Mii_on = False
            self.__BTS.play()
            self.__BTS_on = True

        if 405 <= event.x() <= 477 and 535 <= event.y() <= 555:
            print("Stopping Music")
            self.__BTS_on = False
            self.__Mii_on = False
            sa.stop_all()

        if self.is_winner() == True and self.__winning_move == False:
            self.__BTS_on = False
            self.__Mii_on = False
            sa.stop_all()
            self.__Winner.play()
            print("WINNER!")
            lead_dict = {}
            lead_keys = []
            lead_vals = []
            winner_index = []
            with open('leaderboard.txt', 'r') as leaderboard:
                for line in leaderboard:
                    # print(line)
                    line = line.split()
                    lead_dict[line[0]] = line[1]
            for key in lead_dict.keys():
                lead_keys.append(key)
            for val in lead_dict.values():
                lead_vals.append(val)

            for n in range(len(lead_vals)):
                if self.__moves < int(lead_vals[n]):
                    print("New Low Score: ", self.__moves, " < ", lead_vals[n])
                    winner_index.append(n)

            if len(winner_index) > 0:
                print("New Winner ranks here: ", winner_index[0])
                winner,ok = QInputDialog.getText(self, "Congratulations!", "You're in the top 5!\nEnter your name here (<= 5 characters): ")
                if len(winner) > 5: # used to be "if"
                    QErrorMessage(self).showMessage('Name too long. Must be less than 5 letters. Please try again.')
                    while len(winner) > 5:
                        winner,ok = QInputDialog.getText(self, "Congratulations!", "You're in the top 5!\nEnter your name here (<= 5 characters): ")
                    winner = winner[0:4] # will truncate longer name
                for k in range(len(lead_keys)):
                    if winner == lead_keys[k]:
                        QErrorMessage(self).showMessage('Name already exists. Please try again. Must be less than 5 letters.')
                    while winner == lead_keys[k]:
                        winner,ok = QInputDialog.getText(self, "Congratulations!", "You're in the top 5!\nEnter your name here (<= 5 characters): ")
                    winner = winner[0:4] # will truncate longer name
                lead_vals.insert(winner_index[0], str(self.__moves))
                lead_keys.insert(winner_index[0], winner)
                print("Re-Drawing Leaderboard...", lead_keys[winner_index[0]], "has score of", lead_vals[winner_index[0]])
                with open('leaderboard.txt', 'w') as new_leaderboard:
                    for row in range(5):
                        new_leaderboard.write(lead_keys[row] + " " + lead_vals[row] + "\n")
                        print(new_leaderboard)
                self.__winning_move = True
                self.continue_game()
            else:
                print("Winner not in the top 5.")
                self.__winning_move = True
                self.continue_game()

        self.update()

    def generate_game(self):
        row_index = []
        col_index = []
        zero_count = 0
        one_count = 0
        two_count = 0
        three_count = 0
        for i in numbers:
            temp_row = randint(0, 3)
            temp_col = randint(0, 3)
            if len(row_index) or len(col_index) != 0:
                while zero_count > 7 and (temp_col or temp_row == 0):
                    temp_row = randint(0, 3)
                    temp_col = randint(0, 3)
                while one_count > 7 and (temp_col or temp_row == 1):
                    temp_row = randint(0, 3)
                    temp_col = randint(0, 3)
                while two_count > 7 and (temp_col or temp_row == 2):
                    temp_row = randint(0, 3)
                    temp_col = randint(0, 3)
                while three_count > 7 and (temp_col or temp_row == 3):
                    temp_row = randint(0, 3)
                    temp_col = randint(0, 3)
                for r in range(len(row_index)):
                    for m in range(len(col_index)):
                        while temp_col == col_index[m] and temp_row == row_index[m]:
                            temp_row = randint(0, 3)
                            temp_col = randint(0, 3)
                row_index.append(temp_row)
                if temp_row == 0:
                    zero_count += 1
                elif temp_row == 1:
                    one_count += 1
                elif temp_row == 2:
                    two_count += 1
                else:
                    three_count += 1
                col_index.append(temp_col)
                if temp_col == 0:
                    zero_count += 1
                elif temp_col == 1:
                    one_count += 1
                elif temp_col == 2:
                    two_count += 1
                else:
                    three_count += 1
            else:
                row_index.append(temp_row)
                col_index.append(temp_col)
        print("Nums: ", numbers)
        print("Rows: ", row_index)
        print("Cols: ", col_index)

        for num in range(16):
            #print("Val: ", numbers[num])
            #print("Row: ", row_index[num], " Col: ", col_index[num])
            self.__board[row_index[num]][col_index[num]] = numbers[num]

        print(self.__board[0])
        print(self.__board[1])
        print(self.__board[2])
        print(self.__board[3])

    def repeats_present(self):
        print("CHECKING FOR REPEATS...")
        repeat_count = 0
        checklist = []
        mult = False
        for count in range(len(row_index)):
            curr_row_index = row_index[count]
            curr_col_index = col_index[count]
            for n in range(len(row_index)):
                if count != n:
                    if curr_row_index == row_index[n] and curr_col_index == col_index[n]:
                        print("These rows are the same: ", count)
                        print("These cols are the same: ", count)
                        repeat_count += 1
        for r in range(CELL_COUNT):
            for c in range(CELL_COUNT):
                checklist.append(self.__board[r][c])
        for nn in range(len(numbers)):
            if checklist.count(numbers[nn]) > 1:
                print("Repeat found for value: ", numbers[nn])
                mult = True
            if checklist.count(numbers[nn]) == 0:
                print("No value ", numbers[nn], " found.")
                mult = True
        if repeat_count > 0 or mult == True:
            print("Must Regenerate...")
            return True
        else:
            return False

    def is_solvable(self):
        blank_index = 0
        row_is_even = False

        curr_row = 0
        curr_col = 0
        total_inversions = 0
        inver_is_even = False

        # Check if blank cell's row is even or odd (counting from bottom up)
        for row in range(CELL_COUNT):
            for col in range(CELL_COUNT):
                if self.__board[row][col] == '':
                    blank_index = row
        print("Blank Cell is in Row ", blank_index)
        if blank_index == 0 or blank_index == 2:
            print("Blank Cell row is even.")
            row_is_even = True
        elif blank_index == 3 or blank_index == 1:
            print("Blank Cell row is odd.")
            row_is_even = False

        # Check if total number of inversions is even or odd
        for num in range(len(numbers)):
            inversions = 0
            for row in range(CELL_COUNT):
                for col in range(CELL_COUNT):
                    if self.__board[row][col] != '':
                        if self.__board[row][col] == numbers[num]:
                            curr_row = row
                            curr_col = col
                            #print(numbers[num], " is in row ", curr_row, " and col ", curr_col)
                            for r in range(CELL_COUNT):
                                for c in range(CELL_COUNT):
                                    if self.__board[r][c] != '':
                                        if (r >= curr_row and c > curr_col) or r > curr_row:
                                            #print(self.__board[curr_row][curr_col], " vs. ", self.__board[r][c])
                                            if self.__board[curr_row][curr_col] > self.__board[r][c]:
                                                inversions += 1
                            #print("Number of Inversions for ", numbers[num], " is ", inversions)
                            total_inversions += inversions
        print("Total Inversions: ", total_inversions)
        if total_inversions%2 == 0:
            print("Number of inversions is even.")
            inver_is_even = True
        else:
            print("Number of inversions is odd.")
            inver_is_even = False

        # Check conditions for solvability
        if row_is_even == True and inver_is_even == False:
            print("Solvable Puzzle Generated")
            return True
        elif row_is_even == False and inver_is_even == True:
            print("Solvable Puzzle Generated")
            return True
        else:
            print("Unsolvable Puzzle...")
            return False

    def is_winner(self):
        winning_seq = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, '']
        curr_seq = []
        winner = False
        win_streak = 0

        for r in range(CELL_COUNT):
            for c in range(CELL_COUNT):
                curr_seq.append(self.__board[r][c])
        #print("Winning Board: ", winning_seq)
        #print("Current Board: ", curr_seq)
        for count in range(len(winning_seq)):
            if winning_seq[count] == curr_seq[count]:
                win_streak += 1
        if win_streak == 16:
            winner = True
        else:
            winner = False
        return winner

    def start_music(self):
        pass

    def continue_game(self):
        cont = QMessageBox()
        cont.setWindowTitle("Play Again?")
        cont.setText("Would you like to play again?")
        cont.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        cont.buttonClicked.connect(self.cont_response)
        game = cont.exec()

    def cont_response(self, i):
        # print(i.text())
        if i.text() == "&No":
            QApplication.quit()
        else:
            self.__moves = 0
            self.__winning_move = False
            self.__board = [['', '', '', ''], \
                            ['', '', '', ''], \
                            ['', '', '', ''], \
                            ['', '', '', '']]
            self.generate_game()
            while self.is_solvable() != True or self.repeats_present() == True:
                self.generate_game()
            self.__Mii_on = True
            self.__Mii.play()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Fifteen()
    sys.exit(app.exec_())
