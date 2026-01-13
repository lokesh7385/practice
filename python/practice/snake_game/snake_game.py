from tkinter import *
import random
#setting
GAME_WIDTH = 600  #screen width
GAME_HEIGHT = 600  # screen height 
SNAKE_SPEED = 50  #snake speed of movement 
SPACE_SIZE = 40   # size of everything snake and food
BODY_SIZE = 3      # number of body part at the starting of the game 
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"
BACKGROUND_COLOR = "#000000"

#class for snake 
class Snake :
    def __init__(self):
        self.body_size = BODY_SIZE
        self.coordinates = []
        self.squares = []

        for i in range (0,BODY_SIZE):
            self.coordinates.append([0,0])
        
        for x,y in self.coordinates:
            square = canvas.create_rectangle(x,y,x+SPACE_SIZE,y+SPACE_SIZE,fill=SNAKE_COLOR,tag="snake")
            self.squares.append(square)
#class for food
class Food :

    def __init__(self):
        x = random.randint(0, (GAME_WIDTH//SPACE_SIZE)-1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT//SPACE_SIZE)-1) * SPACE_SIZE
       
        self.coordinates = [x,y]
       
        canvas.create_oval(x,y,x+SPACE_SIZE,y+SPACE_SIZE,fill=FOOD_COLOR,tag="food")
# all movement logic of snake and food and score update
def Nextturn(snake,food): 
    
    x,y=snake.coordinates[0]

    if direction == "up":
        y -= SPACE_SIZE
    if direction == "down":
        y += SPACE_SIZE
    if direction == "left":
        x -= SPACE_SIZE
    if direction == "right":
        x += SPACE_SIZE

    snake.coordinates.insert(0,[x,y])

    square = canvas.create_rectangle(x,y,x+SPACE_SIZE,y+SPACE_SIZE,fill=SNAKE_COLOR)

    snake.squares.insert(0,square)

    if x== food.coordinates[0] and y== food.coordinates[1]:
        global score
        score += 1
        label.config(text="score:{}".format(score))
        canvas.delete("food")
        food = Food()
    else:
        del snake.coordinates[-1]
        canvas.delete(snake.squares[-1])
        del snake.squares[-1]

    if check_collisions(snake):
        Gameover()
    else:
        window.after(SNAKE_SPEED,Nextturn,snake,food)
#change direction of snake 
def Change_driction(new_direction):
    global direction
    if new_direction == 'left':
        if direction != 'right':
            direction = new_direction
    if new_direction == 'right':
        if direction != 'left':
            direction = new_direction
    if new_direction == 'up':
        if direction != 'down':
            direction = new_direction
    if new_direction == 'down':
        if direction != 'up':
            direction = new_direction
#chech for collision of snake with wall and body
def check_collisions(snake):
   
    x,y = snake.coordinates[0]
    if x < 0 or x >= GAME_WIDTH:
        return True
    if y < 0 or y >= GAME_HEIGHT:
        return True

    for body_part in snake.coordinates[1:]:
        if x == body_part[0] and y == body_part[1]:
            return True
    return False
#game over function
def Gameover() :
    canvas.delete(ALL)
    canvas.create_text(canvas.winfo_width()/2,canvas.winfo_height()/2,text="Game Over",font=("consolas",70),fill="red",tag="gameover")

window = Tk()
window.title("Snake Game")
window.resizable(False,False)

score = 0
direction = "down"

label = Label(window,text="score: {}".format(score),font=("consolas",40))
label.pack()

canvas = Canvas(window,bg=BACKGROUND_COLOR,height=GAME_HEIGHT,width=GAME_WIDTH)
canvas.pack()

window.update()

window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()


x = int((screen_width/2) - (window_width/2))
y = int((screen_height/2) - (window_height/2))

window.geometry(f"{window_width}x{window_height}+{x}+{y}")

window.bind("<Left>",lambda event:Change_driction("left"))
window.bind("<Right>",lambda event:Change_driction("right"))
window.bind("<Up>",lambda event:Change_driction("up"))
window.bind("<Down>",lambda event:Change_driction("down"))

snake = Snake()
food = Food()
Nextturn(snake,food)

window.mainloop()

