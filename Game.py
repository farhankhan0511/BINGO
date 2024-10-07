import pygame
class Box:
    count=0
    def __init__(self):
        self.val=0
        self.cutted=False
        self.color=(75, 86, 87)
    
    def __str__(self) -> str:
        return f"{self.val}======={self.cutted}"
    
    def assign(self):
        self.val=Box.count+1
        Box.count+=1

    def cut(self):
        self.cutted=True
        self.color=(153, 174, 176)
    def draw(self,screen,rect):
        
        pygame.draw.rect(screen, self.color, rect)
        font = pygame.font.SysFont('Arial', 24)
        text_surface = font.render(str(self.val), True, (255, 255, 255))  
        screen.blit(text_surface, (rect.x + 15, rect.y + 15))

    
    

class Player:
    def __init__(self,id) -> None:
        self.id=id
        self.streak=0
        self.board=[[None for i in range(5)] for i in range(5)]
        self.pready=False
        self.went=False
    
    def __str__(self) -> str:
        return f"{self.id}   "
    
    def getboard(self):
        return self.board
    
    def checkstreak(self):

        streak=0
        for j in range(5):
            isstreak=True
            for i in range(5):
                if self.board[i][j].cutted==False:                    
                    isstreak=False
                    break
            if isstreak:
                streak+=1
        for j in range(5):
            isstreak=True
            for i in range(5):
                if self.board[j][i].cutted==False:
                    isstreak=False
                    break
            if isstreak:
                streak+=1
        isstreak=True
        for i in range(5):
            if self.board[i][i].cutted==False:
                isstreak=False
                break
        if isstreak:
            streak+=1
        isstreak=True
        for i in range(5):
            if self.board[i][4-i].cutted==False:
                isstreak=False
                break
        if isstreak:
            streak+=1
        return streak

    def reset(self):
        self.board=[[None for i in range(5)] for i in range(5)]
    
    def editbox(self,row,col):
        self.board[row][col]=Box()
        return self.board[row][col]
        
    


    

        
        



class game():
    def __init__(self,id,passkey):
        self.id=id
        self.ready=False
        self.wins=[0,0]
        self.ties=0
        self.passkey=passkey
        self.players=[None,None]
        self.over=False
    def __str__(self):
        return (f"{self.id} and {self.passkey}")
    
    def make_move(self,row,col,player):
        if player.went:
            return False
        mov=self.players[player.id].board[row][col]
        if mov.cutted==False:
            mov.cut()
            valu=mov.val
            board=self.players[(player.id +1)%2].board
            for r in range(len(board)):
                for c in range(len(board)):
                    if board[r][c].val==valu:
                        board[r][c].cut()
                        break

            
            return True 
        else:
            return False
            

        

        


        
        
    def getpasskey(self):
        return self.passkey
    def setready(self):
        print("HEEHEHEH")
        self.ready= True
    
    
    
    def winner(self,player):
        for i in range(2):
            if self.players[(player.id+i)%2].checkstreak() == 5:
                self.over=True
                return (player.id+i)%2
            
        return -1
    
    def connected(self):
        return self.ready
    
    def gameplayon(self):
        return self.players[0].pready and self.players[1].pready
    
    def reset(self):
        self.players[0].reset()
        self.players[1].reset()
    
    

    



        