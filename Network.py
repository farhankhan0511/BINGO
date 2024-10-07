import pickle
import socket
import sys

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.1.5"  # Replace with the actual server address
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connect()

    def getplayer(self):
        try:
            data = pickle.loads(self.client.recv(2048) ) # Receiving pickled data from the server
            if not data:  # Ensure data is not empty
                raise ValueError("No data received")
            return data  # Deserialize the player object
        except Exception as e:
            print(f"Error receiving player data ffff: {e}")
            return None

    def connect(self):
        try:
            self.client.connect(self.addr)
            print("Connected to server")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.client.close()  # Ensure the socket is closed if connection fails
            sys.exit()

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))  # Send pickled data to the server
            response = self.client.recv(2048)  # Receive server response

            if not response:
                print("No data received from server")
                return None  # Handle empty responses safely
            
            return pickle.loads(response)  # Unpickle the response

        except EOFError as e:
            print("EOFError: Ran out of input", e)
            return None 
          # Receive pickled response and deserialize
        except pickle.UnpicklingError as e:
            print(f"Unpickling error: {e}")
        except socket.error as e:
            print(f"Error sending data: {e}")
            return None
    
    