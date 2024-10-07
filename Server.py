import socket
from Game import game
from _thread import *
# import threading
import pickle
import sys
import random
from Game import Player 


server="192.168.1.5"
port=5555

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:
    s.bind((server,port))
except socket.error as e:
    print(e)

s.listen()
print("Waiting for connection")
connection=set()
games={}


def threaded_client(conn,player,gameId):
    conn.send(pickle.dumps(player))
    reply=""
    while True:
        data=conn.recv(2048)
        if not data:
            print(f"Error while recieving the data data={data}")
            break
            
        if gameId in games:
            game=games[gameId]
            
            try:
                data=pickle.loads(data)
                if data=="reset":
                    game.reset()

                elif data=="get":
                    try:
                        conn.sendall(pickle.dumps(game))
                          # game should be serializable
                    except Exception as e:
                        print(f"Error sending game object: {e}")
                    
                elif isinstance(data, tuple) and data[0] == "updateplayer":
                    # Handle the update command
                    updatedplayer = pickle.loads(data[1])  # Deserialize the game object
                    id=updatedplayer.id
                    game.players[id]=updatedplayer  # Update the game on the server
                    print(f"Updated game state for game {gameId}")

                    # Send confirmation back to the client
                    conn.sendall(pickle.dumps(games[gameId]))

                elif data=="updatedp":
                    try:
                        conn.sendall(pickle.dumps(game.players[player.id]))
                    except Exception as e:
                        print(f"Error sending game object: {e}")  

                elif isinstance(data, tuple) and data[0] == "update":
                    # Handle the update command
                    updated_game = pickle.loads(data[1])  # Deserialize the game object
                    games[gameId] = updated_game  # Update the game on the server
                    print(f"Updated game state for game {gameId}")

                    # Send confirmation back to the client
                    conn.sendall(pickle.dumps(games[gameId]))

                elif data.startswith("move"):
                    # Extract row, col, and player details from the data tuple
                    _, row, col = data.split(",")
                    row = int(row)
                    col = int(col)
                    
                    # Perform the move for the current player
                    res=game.make_move(row, col, player)
                    if res:
                        curr=game.players[player.id]
                        opp=game.players[(player.id +1)%2]
                        curr.went=True
                        if opp.went:                            
                            opp.went=False
                    else:
                        print("invalid move")

                    
                    # Update the game state on the server (optional, in case you maintain state)
                    games[gameId] = game

                    print(f"Player {player} made a move at ({row}, {col}) in game {gameId}")
                    conn.sendall(pickle.dumps(games[gameId]))
        
            except Exception as e:
                print(e)
                break
            if game.over:
                print(game.winner())
                break
                    
                
                    
    print("Lost Connection")
   
    try:
        if player.id==0:
            del games[gameId]
            print("Closing game ",gameId)
    except:
        pass
   



gamesids=1000
passkey=random.randint(100000,999999)

        
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    try:
        data = pickle.loads(conn.recv(2048))
    except:
        break

    if data == "Create":
        gamesids += 1
        passkey = random.randint(100000, 999999)  # Generate a random passkey
        games[passkey] = game(gamesids,passkey)  # Map passkey to a game ID
        print(f"New game created with passkey: {passkey}")
        games[passkey].passkey=passkey
        conn.sendall(pickle.dumps(games[passkey]))  # Send the passkey to the client
        game_id=passkey
        player=Player(0)
        games[passkey].players[0]=player
        
         

    elif data.startswith("Join"):
        _, passkey = data.split(",")
        passkey = int(passkey)
        
        if passkey in games:
            game_id=passkey
            game1=games[game_id]
            if game1.players[1] is None:  # Check if player 1 slot is empty
                player = Player(1)
                game1.players[1] = player  # Assign the second player
                print(f"Player 1 joined game with passkey: {passkey}")
                conn.send(pickle.dumps(game1))
        else:
            print(f"Invalid passkey: {passkey}")
            conn.sendall(pickle.dumps(None))
            continue
            
            
            

    # Start a new thread to handle the player in the game
    start_new_thread(threaded_client, (conn, player,game_id))