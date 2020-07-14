import sys
import socket

def login(s):   #login function
    username = input('Please input your user name:\n')
    password = input('Please input your password:\n')

    while(len(username)== 0 or len(password) == 0):         #check user input
        username = input('Please input your user name:\n')
        password = input('Please input your password:\n')

    login= "/login " +username+ " "+password
    s.send(login.encode())
    recvdata=s.recv(1024).decode('ascii')
    return recvdata                             #return the sever respond

def Hall(s):
    while True:
        senddata=input('')
        s.send(senddata.encode())
        recvdata=s.recv(1024).decode('ascii')
        print(recvdata)
        while '3011' in recvdata: #wait others player
            recvdata=s.recv(1024).decode('ascii')
            print(recvdata)
        while '3012' in recvdata:  #when 2 player in room
            senddata=input('')
            s.send(senddata.encode())
            recvdata=s.recv(1024).decode('ascii')
            print(recvdata)
        if senddata=='/exit':
            break
    s.close()

def main(argv):
    address=argv[1]
    port=int(argv[2])
    if(address=="localhost"):
        address="127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((address, port))
    except Exception as emsg:
        print("Socket error: ", emsg)
        sys.exit(1)

    login_state = login(s)
    print(login_state)
    while (login_state!='1001 Authentication successful'): #break when successful
        login_state=login(s)
        print(login_state)
    while True:         #go to game hall
        Hall(s)
        break
    print("Cilent ends")

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Usage: python3 GameClient.py <Server_addr> <Server_port>")
		sys.exit(1)
	main(sys.argv)
