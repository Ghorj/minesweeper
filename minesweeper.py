import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self) -> set:
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # if the number of cells is equal to the count return all cells
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self) -> set:
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # if the count is equal to 0 the cells are safe
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)

        
class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # mark the cell as a move that has been made
        self.moves_made.add(cell)

        # mark the cell as safe
        self.mark_safe(cell)

        # add a new sentence to the AI's knowledge base
        # we need to get the neighbors
        neighbors = set()
        
        # split the tuple in its coordinates
        i, j = cell

        # check cells from (i -1, j -1) to (i + 1, j + 1)
        for x in range(i - 1, i + 2):

            for y in range(j - 1, j + 2):
                
                # if the cell is not on the board don't add to the neighbors
                if 0 <= x < self.height and 0 <= y < self.width:
                    coord = (x, y)

                    # if the coordinates don't match with the cell, add to neighbors
                    if coord != cell:
                        neighbors.add(coord)

        # initiate repeat_neighbors list and new count
        repeat_neighbors = set()

        # check if the neighbors are known mines or safe and update the sentence
        for neighbor in neighbors:
            if neighbor in self.safes:
                repeat_neighbors.add(neighbor)
            elif neighbor in self.mines:
                repeat_neighbors.add(neighbor)
                count -= 1
        
        for old_neighbor in repeat_neighbors:
            neighbors.remove(old_neighbor)

        # add new sentence to the knowledge base                
        self.knowledge.append(Sentence(neighbors, count))
        
        # create a copy of the knowledge base to iterate over it
        knowledge_original = self.knowledge.copy()
        knowledge_modified = self.knowledge.copy()
        
        # loop here
        while True:
            
            # initialize set of new safes and new mines
            new_safes = set()
            new_mines = set()

            # initialize list of sentences to be removed
            sentences_to_remove = []

            # first check if any sentences give conclusions straight away
            for sentence_orig in knowledge_original:

                # if we know they are all safe cells (count == 0)
                if sentence_orig.count == 0:
                    
                    # add cells to new_safes
                    for cell in sentence_orig.cells:
                        new_safes.add(cell)

                    # remove phrase from knowledge
                    sentences_to_remove.append(sentence_orig)
                
                # if we know all cells are mines
                elif sentence_orig.count == len(sentence_orig.cells):

                    # add cells to new_mines
                    for cell in sentence_orig.cells:
                        new_mines.add(cell)

                    # remove phrase from self.knowledge
                    sentences_to_remove.append(sentence_orig)
            
            # mark safe_cells as safe
            for safe_cell in new_safes:
                self.mark_safe(safe_cell)

            # mark mine_cells as mines
            for mine_cell in new_mines:
                self.mark_mine(mine_cell)

            # remove sentences from sentences_to_remove
            for remove_sentence in sentences_to_remove:
                knowledge_modified.remove(remove_sentence)

            # intialize new_sentences list to store new and old sentences
            new_sentences = []
            old_sentences = []

            # iterate between knowledge_original and knowledge_modified to compare them
            for sentence_orig in knowledge_original:

                for sentence_modif in knowledge_modified:
                    
                    # if sentence contained in phrase
                    if sentence_modif.cells.issubset(sentence_orig.cells) and sentence_modif.cells != sentence_orig.cells:
                        
                        # add to old_sentences list to remove later
                        old_sentences.append(sentence_orig)

                        new_cells = sentence_orig.cells - sentence_modif.cells
                        new_count = sentence_orig.count - sentence_modif.count

                        new_sentences.append(Sentence(set(new_cells), new_count))
            
            # remove old sentences from the knowledge base
            for old in old_sentences:
                knowledge_modified.remove(old)

            # add new sentences to the knowledge base
            for new in new_sentences:
                knowledge_modified.append(new)

            # check if the knowledge base hasn't changed and if so break the loop
            if knowledge_modified == knowledge_original:
                break

            else:
                knowledge_original = knowledge_modified
            
        self.knowledge = knowledge_modified

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if not self.safes:
            return None
        
        else:
            options = []

            for element in self.safes:
                if element not in self.moves_made:
                    options.append(element)
            
            try:
                return random.choice(options)
            except IndexError:
                return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        while True:
            # check end game
            if (len(self.mines) + len(self.safes)) == ((self.height) * (self.width)):
                return None
            
            y = random.randrange(self.height)
            x = random.randrange(self.width)
            move = (y, x)

            if move not in self.moves_made and move not in self.mines:
                return move