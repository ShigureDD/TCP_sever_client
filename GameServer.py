#!/usr/bin/python3

import sys
import socket
import threading
import random

UserList=[]
Rooms = 5
RoomList = []
RoomUserList=[]
RoomCap = 2
Guess=[]
lock = threading.Lock()
random_boolean=None


def ServerThread(client,clientaddress):
    is_active=True
    is_playing=False
    check=False
    Logged_UserName=""
    room_id=""
    idx=0
    while is_active:                # a new connect
        # data received from client
        recvdata = client.recv(1024).decode('ascii')
        if recvdata =='/exit':
            client.send('4001 Bye bye'.encode())
            is_active=False
        elif '/login'in recvdata:
            splitdata=recvdata.split()
            username=splitdata[1]
            password=splitdata[2]
            for data in UserList:
                UserName= data[0]
                Password= data[1]
                if username == UserName and password == Password:
                    check=True
                    Logged_UserName = UserName
            if check == True:
                client.send('1001 Authentication successful'.encode())
            else:
                client.send('1002 Authentication failed'.encode())
        elif recvdata =='/list':
            room_state=""
            for i in RoomList:
                room_state += " "+str(i)
            senddata='3001 '+str(Rooms)+room_state
            client.send(senddata.encode())
        elif '/enter'in recvdata:
            splitdata=recvdata.split()
            room_id=splitdata[1]
            if ((RoomList[int(room_id)-1]+1)==1):   # first cilent in room
                RoomList[int(room_id)-1] += 1
                RoomUserList[int(room_id)-1][0]=client #record the info, can overwrit
                is_playing=True
                idx=0
                print(RoomList)
                print(RoomUserList)
                client.send('3011 Wait'.encode())
            elif ((RoomList[int(room_id)-1]+1)==2): # second cilent in room
                RoomList[int(room_id)-1] += 1
                RoomUserList[int(room_id)-1][1]=client #record the info, can overwrit
                is_playing=True
                idx=1
                print(RoomList)
                print(RoomUserList)
                for c in RoomUserList[int(room_id)-1]:
                    c.send('3012 Game started. Please guess true or false'.encode())
            elif((RoomList[int(room_id)-1]+1)>=2):              # block cilent in room when room full
                client.send('3013 The room is full'.encode())
        else:
            client.send('4002 Unrecognized message'.encode())
        while is_playing == True:           # 2 cilent in room play game
            global Guess,random_boolean
            recvdata = client.recv(1024).decode('ascii')
            if '/guess'in recvdata:
                splitdata=recvdata.split()
                Guess[int(room_id)-1][idx]=splitdata[1]
                print(idx,Guess[int(room_id)-1][idx])
                is_playing=False
                if(Guess[int(room_id)-1][0]==Guess[int(room_id)-1][1]):
                    for pc in RoomUserList[int(room_id)-1]:
                        pc.send('3023 The result is a tie'.encode())
                        Guess[int(room_id)-1]=[None,None] #clean guess pool
                        RoomList[int(room_id)-1] -= 1   #clean the room
                        random_boolean=None
                else:
                    if(random_boolean==None and Guess[int(room_id)-1][0]!=None and Guess[int(room_id)-1][1]!=None):
                        random_bit = random.getrandbits(1)
                        random_boolean = bool(random_bit)
                        print(random_boolean)
                    if(Guess[int(room_id)-1][0]==str(random_boolean).lower()):
                        wc=RoomUserList[int(room_id)-1][0]
                        ls=RoomUserList[int(room_id)-1][1]
                        wc.send('3021 You are the winner'.encode())
                        ls.send('3022 You lost this game'.encode())
                        Guess[int(room_id)-1]=[None,None]
                        RoomList[int(room_id)-1] = 0
                        random_boolean=None
                    elif(Guess[int(room_id)-1][1]==str(random_boolean).lower()):
                        wc=RoomUserList[int(room_id)-1][1]
                        ls=RoomUserList[int(room_id)-1][0]
                        wc.send('3021 You are the winner'.encode())
                        ls.send('3022 You lost this game'.encode())
                        Guess[int(room_id)-1]=[None,None]
                        RoomList[int(room_id)-1] = 0
                        random_boolean=None
            else:
                client.send('4002 Unrecognized message'.encode())
    print("client connection closed")
    client.close()

def main(argv):
    host="127.0.0.1"
    port=int(argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind( ("", port) )
    s.listen(5)
    print("Sever Ready at port "+str(port))
    while True:
        clientsock,clientaddress = s.accept()
        t=threading.Thread(target=ServerThread,args=(clientsock,clientaddress))  #t is a new threading
        t.start()
    s.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 GameServer <Server_port> <UserInfo.txt>")
        sys.exit(1)
    with open(sys.argv[2]) as target:
        for row in target:
            row = row.strip("\n")
            UserList.append(row.split(':'))
    for i in range(Rooms):
        RoomList.append(0)
        RoomUserList.append([None]*RoomCap)
        Guess.append([None]*RoomCap)
    print(RoomList)
    print(RoomUserList)
    print(UserList)
    main(sys.argv)
