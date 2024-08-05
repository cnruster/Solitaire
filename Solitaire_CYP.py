from tkinter import *
from tkinter import messagebox
from winsound import *
from random import shuffle

RANKS = "A23456789IJQK"
SUITS = "hsdc"


class PlayCard(PhotoImage):
    def __init__(self, rank, suit, *args, **kwargs):
        PhotoImage.__init__(self, *args, **kwargs)
        self.rank = RANKS.index(rank)
        self.suit = SUITS.index(suit)
        self.red = suit in "hd"


"""
Solitaire game
Original version from Github by Jason Alencewicz
https://github.com/jayalen86/Solitaire_With_Tkinter
Totally revised by Yiping Cheng. Email: ypcheng@bjtu.edu.cn
Beijing Jiaotong University, China
"""


class Solitaire:
    def __init__(self):
        self.window = Tk()
        self.window.title("Solitaire")
        self.menubar = Menu(self.window)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New Game", command=self.new_game)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.window.destroy)
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About", command=Solitaire.about)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.window.config(menu=self.menubar)

        self.cards = [PlayCard(rank, suit, file=f"images/{rank}{suit}.png") for rank in RANKS for suit in SUITS]

        # images
        self.bg_img = PhotoImage(file="images/cardtable.png")
        self.boc_img = PhotoImage(file="images/card_back.png")
        self.suit_images = [PhotoImage(file="images/hearts.png"),
                            PhotoImage(file="images/spades.png"),
                            PhotoImage(file="images/diamonds.png"),
                            PhotoImage(file="images/clubs.png")]
        self.empty_pile_img = PhotoImage(file="images/empty_pile.png")

        self.canvas = Canvas(self.window, bg="white", height=725, width=1205)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.onclick)
        self.canvas.bind("<Double-Button-1>", self.ondblclick)
        self.show_canvas_fixed()
        self.new_game()
        self.window.mainloop()

    @staticmethod
    def about():
        messagebox.showinfo("Solitaire", "Original version by Jason Alencewicz. Revised by Yiping Cheng.")

    def new_game(self):
        PlaySound("sounds/shuffling_sound.wav", SND_FILENAME)
        self.new_game_state()
        self.update_canvas()

    def new_game_state(self):
        shuffle(self.cards)
        self.piles = [[None for _ in range(i)] for i in range(1, 8)]
        self.hidden = [*range(7)]
        self.deck = [None for _ in range(24)]
        self.stacks = [[], [], [], []]
        index = 0
        for i in range(1, 8):
            for j in range(i):
                self.piles[i - 1][j] = self.cards[index + j]
            index += i
        while index < 52:
            self.deck[index - 28] = self.cards[index]
            index += 1
        self.deck_index = -1  # initially no deck card is shown
        self.selected_item = ""  # initially no item is selected

    def show_canvas_fixed(self):  # show canvas items that will never change
        # background
        self.canvas.create_image(0, 0, anchor=NW, image=self.bg_img)
        # back of deck
        self.canvas.create_rectangle(20, 50, 170, 250, outline="darkgray", fill="lightgrey", tag="deck_back")
        self.canvas.create_image(20, 50, anchor=NW, image=self.boc_img, tag="deck_back_img")

    def update_canvas(self):
        # the deck card
        self.update_deck_card()

        # the four stacks for the four suits
        for s in range(4):
            self.update_stack(s)

        # the tableau piles
        for x in range(7):
            self.update_pile(x)

    def update_deck_card(self):
        self.canvas.delete("deck_card")
        self.canvas.delete("deck_card_img")
        if self.deck_index >= 0:
            self.canvas.create_rectangle(190, 50, 340, 250, outline="darkgray", fill="lightgrey",
                                         tag="deck_card")
            # we can ensure self.deck_index < len(self.deck) so no need to check it
            self.canvas.create_image(190, 50, anchor=NW, image=self.deck[self.deck_index],
                                     tag="deck_card_img")
            
    def update_stack(self, s):
        rect_tag = f"stack_{SUITS[s]}"
        img_tag = f"stack_{SUITS[s]}_img"
        self.canvas.delete(rect_tag)
        self.canvas.delete(img_tag)
        self.canvas.create_rectangle(530+170*s, 50, 680+170*s, 250, outline="darkgray", fill="lightgrey",
                                     tag=rect_tag)
        stack = self.stacks[s]
        if stack:
            self.canvas.create_image(530+170*s, 50, anchor=NW, image=stack[-1], tag=img_tag)
        else:
            self.canvas.create_image(580+170*s, 125, anchor=NW, image=self.suit_images[s], tag=img_tag)

    def update_pile(self, x):
        rect_tag = f"pile{x}"
        img_tag = f"pile{x}_img"
        self.canvas.delete(rect_tag)
        self.canvas.delete(img_tag)
        pile = self.piles[x]
        pile_len = len(pile)
        pile_left = 20 + 170 * x
        if pile_len:
            self.canvas.create_rectangle(pile_left, 300, 170+170*x, 485+15*pile_len,
                                         outline="darkgray", fill="lightgrey", tag=rect_tag)
            hidden = self.hidden[x]
            for y in range(pile_len):
                self.canvas.create_image(pile_left, 300+15*y, anchor=NW,
                                         image=self.boc_img if y<hidden else pile[y], tag=img_tag)
        else:  # the pile is empty
            self.canvas.create_rectangle(pile_left, 300, 170+170*x, 500,
                                         outline="darkgray", fill="lightgrey", tag=rect_tag)
            self.canvas.create_image(pile_left, 300, anchor=NW,
                                     image=self.empty_pile_img, tag=img_tag)

    def onclick(self, event):
        # deselect the selected item and save it for later use
        src_item = self.deselect()
        cur_item = self.find_item(event)  # find the item currently clicked
        if "deck_back" in cur_item:  # we clicked on the deck back
            self.deck_next()
        elif cur_item and cur_item != src_item:
            if not self.move(src_item, cur_item):  # can't move anything from src to cur
                self.select_item(cur_item)

    def ondblclick(self, event):
        self.deselect()
        cur_item = self.find_item(event)  # find the item currently double-clicked
        if "deck_back" in cur_item:  # we double-clicked on the deck back
            self.deck_next()
        elif cur_item:
            self.move_to_stack(cur_item)

    def find_item(self, event):
        item_id = self.canvas.find_closest(event.x, event.y)
        item_tag = self.canvas.itemcget(item_id, "tag")
        return item_tag.replace(" current", "").replace("_img", "") if item_tag != "current" else ""
    
    def select_item(self, item):
        self.canvas.itemconfig(item, outline="yellow", width=5)
        self.selected_item = item
        
    def deselect(self):
        sel_item = self.selected_item
        if sel_item:
            self.canvas.itemconfig(sel_item, outline="darkgray", width=1)
            self.selected_item = ""
        return sel_item

    def deck_next(self):
        self.deck_index += 1
        if self.deck_index >= len(self.deck):
            self.deck_index = -1
        self.update_deck_card()

    def move(self, src_item, dst_item):
        if "deck_card" in src_item:
            if "pile" in dst_item:
                return self.move_deck_to_pile(int(dst_item[4]))
            elif "stack" in dst_item:
                return self.move_deck_to_stack(SUITS.index(dst_item[6]))
        elif "pile" in src_item:
            if "pile" in dst_item:
                return self.move_pile_to_pile(int(src_item[4]), int(dst_item[4]))
            elif "stack" in dst_item:
                return self.move_pile_to_stack(int(src_item[4]), SUITS.index(dst_item[6]))
        return 0

    def move_to_stack(self, src_item):
        if "deck_card" in src_item:
            return self.move_deck_to_stack(-1)  # move to the stack to which the deck card belongs
        elif "pile" in src_item:
            # move to the stack to which the top card belongs
            return self.move_pile_to_stack(int(src_item[4]), -1)
        return 0
    
    def remove_deck_card(self):
        # we can ensure 0 <= self.deck_index < len(self.deck)
        del self.deck[self.deck_index]
        if self.deck_index >= len(self.deck):
            self.deck_index = -1
        self.update_deck_card()

    def move_deck_to_stack(self, s):
        if self.deck_index < 0:
            return 0  # this should never happen
        deck_card = self.deck[self.deck_index]
        if s >= 0:
            if s != deck_card.suit:  # not the same suit as the deck card
                return 0
        else:
            s = deck_card.suit  # s==-1: move to the stack for the suit of the deck card
        count = 0  # count of cards that can be moved
        stack = self.stacks[s]
        if stack:
            if deck_card.rank-stack[-1].rank == 1:
                count = 1
        elif deck_card.rank == 0:  # deck card is an A which can move into an empty stack
            count = 1
        if count:
            self.remove_deck_card()
            stack.append(deck_card)
            self.update_stack(s)
            self.check_win()
        return count

    def move_pile_to_stack(self, x, s):
        pile = self.piles[x]
        if not pile:
            return 0
        pile_top = pile[-1]
        if s>=0:
            if s != pile_top.suit:  # not the same suit
                return 0
        else:
            s = pile_top.suit  #
        count = 0  # count of cards that can be moved
        stack = self.stacks[s]
        if stack:
            if pile_top.rank-stack[-1].rank == 1:
                count = 1
        elif pile_top.rank == 0:
            count = 1
        if count:
            del pile[-1]
            hidden = self.hidden[x]
            # to ensure that 0<=hidden<len or hidden==len==0
            if hidden == len(pile) and hidden>0:
                self.hidden[x] = hidden-1  # the new top card now shows its front face
            stack.append(pile_top)
            self.update_pile(x)
            self.update_stack(s)
            self.check_win()
        return count

    def move_deck_to_pile(self, x):
        if self.deck_index < 0:
            return 0  # this should never happen
        deck_card = self.deck[self.deck_index]
        count = 0  # count of cards that can be moved
        pile = self.piles[x]
        if pile:
            pile_top = pile[-1]
            if pile_top.rank - deck_card.rank == 1 and pile_top.red != deck_card.red:
                count = 1
        elif deck_card.rank == 12:  # only a K card can move to an empty pile
            count = 1
        if count:
            self.remove_deck_card()
            pile.append(deck_card)
            self.update_pile(x)
        return count

    def move_pile_to_pile(self, x1, x2):
        pile1 = self.piles[x1]
        if not pile1:
            return 0
        # must have 0<=hidden1<len(pile1)
        hidden1 = self.hidden[x1]
        pile2 = self.piles[x2]
        if pile2:
            count = Solitaire.find_tail_straight(pile1, hidden1, pile2[-1])
        else:
            count = Solitaire.find_tail_k_straight(pile1, hidden1)

        if count:
            pile2.extend(pile1[-count:])
            del pile1[-count:]
            # if all the shown segment is moved, then show the top-most card of the hidden segment
            if hidden1 == len(pile1) and hidden1>0:
                self.hidden[x1] = hidden1-1
            # always ensured that 0<=hidden<len or hidden==len==0
            self.update_pile(x1)
            self.update_pile(x2)

        return count

    # find the length of the straight that can follow a lead-card on the tail of the pile's shown segment
    @staticmethod
    def find_tail_straight(pile, hidden, lead_card):
        pile_len = len(pile)
        if hidden == pile_len:  # the shown segment has length 0
            return 0

        index = pile_len-1
        pile_top = pile[index]
        # check if their colors match. if not, then don't go into hopeless loop
        if (lead_card.rank - pile_top.rank)%2 == 0:
            if lead_card.red != pile_top.red:
                return 0
        else:
            if lead_card.red == pile_top.red:
                return 0

        while index >= hidden:
            # to form a straight the ranks must be consecutive and the colors must be alternating
            if (index == pile_len - 1 or
                    (pile[index].rank - pile[index + 1].rank == 1 and
                     pile[index].red != pile[index + 1].red)):
                if pile[index].rank == lead_card.rank - 1:
                    # the straight can follow the specified lead-card
                    return pile_len - index
                index -= 1
            else:
                break
        # the straight can't follow the specified lead-card
        return 0

    # find the length of the straight that begins with a K on the tail of the pile's shown segment
    @staticmethod
    def find_tail_k_straight(pile, hidden):
        pile_len = len(pile)
        if hidden==pile_len:  # the shown segment has length 0
            return 0

        index = pile_len-1
        while index >= hidden:
            # to form a straight the ranks must be consecutive and the colors must be alternating
            if (index==pile_len-1 or
                    (pile[index].rank - pile[index+1].rank == 1 and
                    pile[index].red != pile[index+1].red)):
                if pile[index].rank == 12:  # 12 is the rank of a K card
                    # the straight begins with a K card, so return its length
                    return pile_len - index
                index -= 1
            else:
                break
        # the straight does not begin with a K card
        return 0

    def check_win(self):
        if all([len(stack) == 13 for stack in self.stacks]):
            messagebox.showinfo('Congratulations!', 'You WON!')


Solitaire()
