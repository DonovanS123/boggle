# Donovan Schroeder

######################################################################

## This version of boggle will work with words of any length greater than 3
## Allows for movement in cardinal and diagonal directions
## Allows for any size board
## readData can take in multiple files (as long as they're formatted the same way as words.dat)
## There are minor changes throughout to allow these

from random import choices
from string import ascii_lowercase
from tkinter import *

class Boggle():
    # calls readData to get trie and frequency
    # creates board and launches TKinter
    def __init__(self, files='words.dat', size=5):
        '''takes paramters files and size
files should be a container of words, seperated by new lines, set to 'words.dat' by default (should be a tuple if multiple files)
size is the length/width of the board, set to 5 by default'''
        readData = self.readData(files)
        self.frequency = readData[0] # cumulative weights from readData
        self.trie = readData[1] # nestled dictionaries of letters with deepest layer being words
        self.size = size
        # self.board is 5 rows of 5 columns of random letters with weights from self.frequency
        self.board = self.boardGen(self.frequency, size)
        self.soln = []
        self.playTK()

    # selects random letters with weights from readData
    def boardGen(self, frequency, size=5):
        '''generates new board
frequency is used for letter weights, defaults to self.frequency
size is used for board's column and row lenght, defaults to 5
Example Output: [['i', 't', 't', 'o', 't'], ['g', 'd', 'e', 't', 'e'], ['k', 'a', 's', 'm', 'p'], ['o', 'r', 'y', 'c', 'n'], ['s', 'w', 'e', 'e', 'n']]'''
        return([choices(list(frequency.keys()), cum_weights=list(frequency.values()), k=size) for r in range(size)])
        
    def readData(self, files=('words.dat','words4.txt')): # words4.txt is my file of 4 letter words
        '''generates trie and letter frequency dictionaries
files are the files used to extract words, can be string or tuple of strings of file names
default to ('words.dat','words4.txt') words4.txt is a 4 letter word file
outputs in form (letterFrequency, wordTrie)'''
        letterDict = {letter:0 for letter in ascii_lowercase} # initialize counters
        mainTrie = dict()
        if type(files) == str:
            files = (files,) # to keep compatible with multi file functionality
        # generates trie and frequency
        def dictGen(word, wSlice, trieDict, letterCount):
            '''recursive function used to generate trie and count letters
word is the whole word
wSlice is a slice of the word, initially the whole word
trieDict is the dictionary that will eventually become the trie
letterCount is the letter counter dictionary
outputs (trie, letterFrequency)'''
            letterCount[wSlice[0]] += 1 # handles counting letters
            if len(wSlice) == 1: # base step
                if wSlice in trieDict:
                    trieDict[wSlice]['word'] = word # setup to work with words of varying length
                else:
                    trieDict[wSlice] = dict()
                    trieDict[wSlice]['word'] = word
                return((trieDict, letterCount))
            else: # recursive step
                if wSlice[0] not in trieDict: # if new letter to dict layer
                    trieDict[wSlice[0]] = dict() # add new layer
                finalDict = dictGen(word, wSlice[1:], trieDict[wSlice[0]], letterCount) # recursive call
                trieDict[wSlice[0]] = finalDict[0]
            return((trieDict, letterCount))
        
        try:
            for file in files: # multiple file functionality, tested with 4 letter word file
                with open(file) as fopen:
                    for row in fopen: # interate through words
                        word = row.strip().lower()
                        dictOutput = dictGen(word, word, mainTrie, letterDict) # update main dictionary
                        mainTrie, letterDict = dictOutput[0], dictOutput[1]
                    totalCount, keys = sum(dict.values(letterDict)), list(dict.keys(letterDict))
                    for i in range(len(keys)): # converts counts into cum weights
                        letterDict[keys[i]] = letterDict[keys[i]]/totalCount
                        if i != 0:
                            letterDict[keys[i]] += letterDict[keys[i-1]]
            return((letterDict, mainTrie))
        except:
            print("File couldn't be opened: ", files)
            exit()

    # generates moves contiguous to a position
    def contGen(self, pos):
        '''takes a position and generates a tuple of tuples of coordinates
coordinates are one away in the cardinal or diagonal directions'''
        return( ( (x,y) for x in range(pos[0]-1, pos[0]+2) for y in range(pos[1]-1, pos[1]+2)
                  if x in range(self.size) and y in range(self.size)
                  and not (x == pos[0] and y == pos[1])) ) 

    # check if solution, given as list of coordinates of letters in form (row,column), is a valid solution
    # solution not valid if each position in soln is not above or
    # ckSoln will work even if we had a trie with words of different lengths
    def ckSoln(self, soln):
        '''checks if solution is valid
soln is a list of coordinates that correspond to letters on self.board
letters must be adjacent (not diagonal) and on board
word must be in self.trie to be valid
potential outputs: word, trie, (False, trie), (False, string)'''
        # recursively checks solution
        def checker(coord, trie):
            '''checks word is in trie, takes inputs coord and dictionary
coord is a list of coordinate(s) in tuples, ex: [(0,1),(1,1),(1,2)]
trie is a dictionary corresponding to current level of trie being checked
each recursion cuts off the first pair of coordinates and goes a level deeper into trie
outputs string of word (if found), last level of dictionary reached, or False and last level of dictionary reached'''
            letter = self.board[coord[0][0]][coord[0][1]]
            # checking type(wDict) will prevent longer solutions from indexing strings by letter if letter in word
            if letter in trie and type(trie) == dict:
                if len(coord) == 1: # base step
                    if 'word' in trie[letter]:
                        return(trie[letter]['word']) # return found word
                    return(trie[letter]) # return level of trie reached
                else: # recursive step
                    return( checker( coord[1:],trie[letter] ) )
            return(False, trie)

        if any([soln[x] == soln[y] for x in range(len(soln)) for y in range(x+1, len(soln))]) and len(soln) > 1:
            # checks if a position is used twice in the solution
            return(False, 'duplicate') # remove string
        for i in range(len(soln)-1):
            pairx, pairy = soln[i],soln[i+1] # checking each solution against the solution after it
            if pairy not in self.contGen(pairx):
                return (False, 'invalid positions')
        return(checker(soln, self.trie)) # returns word if valid, else returns False and deepest layer of dictionary reached

    # finds all words from a starting position
    def wordFind(self, soln, wordList):
        '''search recursively for words from starting position, takes inputs soln and wordList
soln is solution in form list of tuples of coordinates, starts with one set of coordinates and expands till it reaches a word or dead end
wordList is a list of words found so far, starts as empty list
outputs list of words found from starting position'''
        checkValid = self.ckSoln(soln)
        if not(checkValid == False or (type(checkValid) == tuple and False in checkValid)): # if move is valid
            for direction in self.contGen(soln[-1]): # all available moves around last position
                # construct word
                if direction not in soln:
                    newSoln = soln[:]
                    newSoln.append(direction)
                    ckdSoln = self.ckSoln(newSoln)
                    if len(soln) > 1 and type(ckdSoln) == str: # checks for word in layer of trie
                        wordList.append(ckdSoln) # base step
                    if len(self.wordFind(newSoln, [])) > 0: # do not append empy lists
                        wordList.extend(self.wordFind(newSoln,[])) # recursive step
            return(wordList)
        else:
            return()

    # finds all words on board
    def solve(self):
        '''returns a list of ALL found words on board, including duplicates found through different combinations
can be altered to return only unique words with conversion to set'''
        solved = list() # word container
        for x in range(self.size):
            for y in range(self.size):
                solved.extend(self.wordFind([(x,y)],[])) # extend by words found from each starting location
        return(solved)  

    def playTK(self):
        '''launch game in TKinter'''
        self.initTK()
        self.window.mainloop()

    # initialize board
    def initTK(self):
        '''set up TK window and canvas to initial state'''
        self.window = Tk()
        self.window.title('Boggle')
        self.canvas = Canvas(self.window, width = self.size*20, height = self.size*20, bg='white')
        self.canvas.pack()
        self.newTK() # display grid
        self.canvas.bind("<Button-1>", self.extend) # LMB place move
        self.canvas.bind("<Button-3>", self.reset) # RMB reset current board
        self.canvas.bind("<Button-2>", self.new) # MMB create new board
        # focus mouse on canvas
        self.canvas.focus_set()
        # put letters on board
        self.updateTK()

    # displays letters
    def updateTK(self):
        '''displays letters on board in their positions'''
        for i in range(self.size):
            for j in range(self.size):
                self.canvas.create_text((i*20)+10, (j*20)+10, text=self.board[j][i].upper())

    # displays whited out grid
    def newTK(self):
        '''displays whited out grid'''
        for i in range(self.size):
            for j in range(self.size):
                self.canvas.create_rectangle(i*20,j*20,(i+1)*20,(j+1)*20,fill='white')

    # Left Click, add/check position, update board
    def extend(self, event):
        '''Left Mouse Button
checks if move is valid, if so, updates solution list and marks with green circle
if invalid, marks with red circle
also if selected letter completes a word, prints the word'''
        # click coordinates
        col = event.x//20
        row = event.y//20
        self.soln.append((row, col)) # append selected position
        checked = self.ckSoln(self.soln) # check solution
        if all(checked) == False: # if choice is invalid
            if not(len(checked) > 1 and checked[1] == 'duplicate'): # this is to not overwrite green circles on selected letters
                # mark invalid choice with red circle
                self.canvas.create_oval(col*20+1, row*20+1, (col+1)*20-1,(row+1)*20-1, fill='red')
                self.updateTK() # display letters over new circle
            self.soln = self.soln[:-1] # remove last choice from solution
        else: # if choice is valid
            # mark with green circle
            self.canvas.create_oval(col*20+1, row*20+1, (col+1)*20-1, (row+1)*20-1, fill='green2')
            self.updateTK() # display letters over new circle
            if len(self.soln) > 1 and type(checked) == str: # checks if word found
                print(checked) # prints word

    # reset board
    def reset(self, event):
        '''Right Mouse Button
resets choices in solution and overwrites any seletion circles on board'''
        self.soln = [] # reset solution
        self.newTK() # white out grids
        self.updateTK() # redisplay letters

    # setup new game
    def new(self, event):
        '''Middle Mouse Button
play new game by randomizing board and displaying fresh game'''
        self.board = self.boardGen(self.frequency) # generate fresh board
        self.reset(event) # sets up fresh game

    # printed representation
    def __str__(self):
        return('\n'.join([' '.join([self.board[i][j] for j in range(self.size)]) for i in range(self.size)])) # print the game board


######################################################################
