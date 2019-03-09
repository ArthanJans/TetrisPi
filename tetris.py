import time
import random

from gfxhat import touch, lcd, backlight, fonts
from PIL import Image, ImageFont, ImageDraw

class EndGame(Exception):
    pass

class Layout:
    def __init__(self, size, block0, block1, block2, block3):
        self.size = size
        self.blocks = [block0, block1, block2, block3]
    
class Piece:
    def __init__(self, rotations):
        self.rotations = rotations
        
    def getRotation(self, rota):
        return self.rotations[rota%len(self.rotations)]

backlight.set_all(255, 255, 255)
backlight.show()

width, height = lcd.dimensions()

image = Image.new('P', (width, height))

draw = ImageDraw.Draw(image)

font = ImageFont.truetype(fonts.BitbuntuFull, 10)

text = "Next"

w, h = font.getsize(text)

x = (width+96 - w) // 2
y = 5

draw.text((x, y), text, 1, font)
draw.rectangle([32, 0, 95, 63], outline=1)

x1 = (width+96 - 18) // 2
y1 = 19

draw.rectangle([x1, y1, x1+17, y1+17], outline=1)

touch.set_led(4, 1)
time.sleep(0.1)
touch.set_led(3, 1)
touch.set_led(5, 1)
time.sleep(0.1)
touch.set_led(4, 0)
time.sleep(0.1)
touch.set_led(3, 0)
touch.set_led(5, 0)
time.sleep(0.2)
touch.set_led(3, 1)
touch.set_led(5, 1)


for x2 in range(128):
    for y2 in range(64):
        pixel = image.getpixel((x2, y2))
        lcd.set_pixel(x2, y2, pixel)
        
lcd.show()

board = []
for l in range(16):
    row = []
    for cell in range(16):
        row.append(0)
    board.append(row)
    
pieces = []

square0 = Layout(2, (0, 0), (1, 0), (0, 1), (1, 1))
square = Piece([square0])
pieces.append(square)

line0 = Layout(4, (2, 0), (2, 1), (2, 2), (2, 3))
line1 = Layout(4, (0, 2), (1, 2), (2, 2), (3, 2))
line = Piece([line0, line1])
pieces.append(line)

left0 = Layout(3, (0, 1), (1, 1), (2, 1), (2, 2))
left1 = Layout(3, (1, 0), (1, 1), (1, 2), (0, 2))
left2 = Layout(3, (0, 0), (0, 1), (1, 1), (2, 1))
left3 = Layout(3, (1, 0), (1, 1), (1, 2), (2, 0))
left = Piece([left0, left1, left2, left3])
pieces.append(left)

right0 = Layout(3, (0, 1), (1, 1), (2, 1), (0, 2))
right1 = Layout(3, (1, 0), (1, 1), (1, 2), (0, 0))
right2 = Layout(3, (2, 0), (0, 1), (1, 1), (2, 1))
right3 = Layout(3, (1, 0), (1, 1), (1, 2), (2, 2))
right = Piece([right0, right1, right2, right3])
pieces.append(right)

zig0 = Layout(3, (1, 1), (2, 1), (0, 2), (1, 2))
zig1 = Layout(3, (1, 0), (1, 1), (2, 1), (2, 2))
zigL = Piece([zig0, zig1])
pieces.append(zigL)

tee0 = Layout(3, (0, 1), (1, 1), (2, 1), (1, 2))
tee1 = Layout(3, (1, 0), (1, 1), (1, 2), (0, 1))
tee2 = Layout(3, (1, 0), (0, 1), (1, 1), (2, 1))
tee3 = Layout(3, (1, 0), (1, 1), (1, 2), (2, 1))
tee = Piece([tee0, tee1, tee2, tee3])
pieces.append(tee)

zig2 = Layout(3, (0, 1), (1, 1), (1, 2), (2, 2))
zig3 = Layout(3, (2, 0), (2, 1), (1, 1), (1, 2))
zigR = Piece([zig2, zig3])
pieces.append(zigR)


        
current = None
nex = random.randint(0, len(pieces)-1)
        
rotation = 0
move = 0
drop = 0

def movef(amount):
    global move
    for block in pieces[current].getRotation(rotation).blocks:
        if block[0] + move + amount > 8 or block[0] + move + amount < -7 or board[block[1] + drop][block[0] + move + amount + 7] == 1:
            return
    move += amount
    
def rotate(amount):
    global rotation
    for block in pieces[current].getRotation(rotation + amount).blocks:
        while block[0] + move > 8:
            movef(-1)
        while block[0] + move < -7:
            movef(1)
    rotation += amount

def rot(ch, event):
    hidePiece()
    if event == 'press':
        if ch == 0:
            rotate(1)
        else:
            rotate(-1)
            
    showPiece()
    lcd.show()

def mov(ch, event):
    hidePiece()
    if event == 'press':
        if ch == 3:
            movef(-1)
        else:
            movef(1)
            
    showPiece()
    lcd.show()
    
bd = False
    
def bigDown(ch, event):
    global current
    if event == 'press' and not bd:
        bd = True
        while current != None:
            print(current)
            dropf()
        bd = False

touch.on(0, rot)
touch.on(1, rot)
touch.on(3, mov)
touch.on(5, mov)
#touch.on(4, bigDown)



def viewNext():
    for x3 in range(16):
        for y3 in range(16):
            lcd.set_pixel(x1+1+x3, y1+1+y3, (x3//4, y3//4) in pieces[nex].rotations[0].blocks)

def viewBoard():
    for x4 in range(1, 63):
        for y4 in range(1, 63):
            lcd.set_pixel(32+x4, 0+y4, board[y4//4][x4//4])

def nextBlock():
    global nex
    global current
    f = True
    for block in pieces[nex].rotations[0].blocks:
        if board[block[1]][7 + block[0]] == 1:
            f = False
            raise EndGame()
    if f:
        current = nex
        nex = random.randint(0, len(pieces) - 1)
        viewNext()
            
def showPiece():
    if current == None:
        return
    for x in range(16):
        for y in range(16):
            if (x//4, y//4) in pieces[current].getRotation(rotation).blocks:
                lcd.set_pixel(x + 32 + (move+7)*4, y + drop*4, 1)
                
def hidePiece():
    if current == None:
        return
    for x in range(16):
        for y in range(16):
            if x + 32 + (move+7)*4 == 32 or x + 32 + (move+7)*4 == 95 or y + drop*4 == 0 or y + drop*4 == 63:
                continue
            if (x//4, y//4) in pieces[current].getRotation(rotation).blocks:
                lcd.set_pixel(x + 32 + (move+7)*4, y + drop*4, 0)
     
def checkFull():
    while [1] * 16 in board:
        board.remove([1] * 16)
        newRow = []
        for _ in range(16):
            newRow.append(0)
        board.insert(0, newRow)
     
def fixPiece():
    global rotation
    global drop
    global move
    global current
    for block in pieces[current].getRotation(rotation).blocks:
        board[block[1] + drop][7 + block[0] + move] = 1
    current = None
    rotation = 0
    drop = 0
    move = 0
    checkFull()
     
def dropf():
    if current == None:
        return
    hidePiece()
    global drop
    for block in pieces[current].getRotation(rotation).blocks:
        if block[1] + drop + 1 > 15 or board[block[1] + drop + 1][7 + block[0] + move] == 1:
            fixPiece()
            return
    drop += 1
    showPiece()

try:
    while True:
        if current == None:
            nextBlock()
        time.sleep(0.5)
        dropf()
        viewBoard()
        showPiece()
        lcd.show()
        
except (KeyboardInterrupt, EndGame):
    for x in range(6):
        backlight.set_pixel(x, 0, 0, 0)
        touch.set_led(x, 0)
    backlight.show()
    lcd.clear()
    lcd.show()