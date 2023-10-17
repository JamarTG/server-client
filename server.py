# Server to implement a simple program to receive two prime numbers from a
# client. The server will compute their LCM and send it back to the client.
# If the server-calculated LCM matches what the client computes, the client
# will send a 200 OK status code to the server. Otherwise a 400 Error code is
# sent to the server.

# Author: Jamari McFarlane
# Last modified: 2023-10-17
#!/usr/bin/python3

import socket
import sys
import time
import math


def clientHello():
    """Generates an acknowledgement for the client hello message"""
    msg = "101 Hello Ack"
    return msg


def generateLCMstring(lcm):
    """Generates the 107 LCM string"""
    msg = "107 LCM " + str(lcm)
    return msg


def serverPrimeLCM(prime1, prime2):
    """Returns the LCM calculated by the server"""
    gcd = math.gcd(prime1, prime2)
    lcm = (prime1 * prime2) // gcd
    return lcm

def processMsgs(s, msg, state):
    """If the message cannot be split then something is wrong with the request"""
    try:
        statusCode = int(msg.split(" ")[0])
    except:
        pass

    """The message is bad if it is 'good' within the list of possible status codes"""
    if statusCode not in [100, 105, 200, 400]:
        statusCode = 500

    if statusCode == 200 or statusCode == 400:
        s.close()
        handleMessagePrintoutsServer("close")
        return 1 if statusCode == 200 else 0

    elif statusCode == 100:
        s.send(clientHello().encode())
        state['clientConnected'] = True
        handleMessagePrintoutsServer(clientHello())
        return processMsgs(s, s.recv(1024).decode(), state)

    elif statusCode == 105:
        prime1, prime2 = map(int, msg.split(" ")[-2:])
        lcmString = generateLCMstring(serverPrimeLCM(prime1, prime2))
        s.send(lcmString.encode())
        handleMessagePrintoutsServer(lcmString)
        return processMsgs(s, s.recv(1024).decode(), state)

    return statusCode


def handleMessagePrintoutsServer(message):
    """Function to handle the printouts of informative messages on the server side"""

    status_codes = {
        100: ("Connection Request", True),
        101: ("Connection Acknowledgement", True),
        200: ("Success Message", False),
        400: ("Failure Message", False),
        105: ("Prime Number Exchange", False),
        107: ("LCM Calculation", True),
        500: ("Bad Request", False),
    }

    if message == "close":
        print("\n" + "─" * 28 + "\nServer Disconnected!\n" + "─" * 28 + "\n")
        return
    if message == ":)":
        print("\n" + "─" * 28 + "\nOperation Successful\n" + "─" * 28 + "\n")
        return
    if message == ":(":
        print("\n" + "─" * 28 + "\nOperation Unsuccessful\n" + "─" * 28 + "\n")
        return

    def printInfo(title, outgoing):
        """Function to determine the printout where the message is moving from"""
        if title != "Connection Request":
            print("\n" + "─" * 28 + f"\n{title}\n" + "─" * 28 + "\n")


        if not outgoing:
            to, fro = "Server", "Client"
        else:
            fro, to = "Server", "Client"

        print(fro, " -> ", to)

    try:
        statusCode = int(message.split(" ")[0])
    except ValueError:
        statusCode = 500

    title, outgoing = status_codes.get(statusCode, ("Unknown Request", False))
    printInfo(title, outgoing)

    if statusCode == 101:
        print(f"Message: {' '.join(message.split(' ')[1:])}\nStatus Code: {message.split()[0]}")
    else:
        print(f"Message: {message.split(' ')[1]}\nStatus Code: {message.split(' ')[0]}")

    if statusCode == 105:
        print(f"First Prime: {message.split()[2]}\nSecond Prime: {message.split()[3]}")
    if statusCode == 107:
        print("Server Computed LCM :", message.split(" ")[2])


def main():
    """Driver function for the server."""
    args = sys.argv
    if len(args) != 2:
        print("Please supply a server port.")
        sys.exit()
    HOST = ""  # Symbolic name meaning all available interfaces
    PORT = int(args[1])  # The port on which the server is listening.
    if PORT < 1023 or PORT > 65535:
        print("Invalid port specified.")
        sys.exit()

    print("╭" + "─" * 28 + "╮")
    print(f"│{'Server of Joan A. Smith':^28}│")
    print("╰" + "─" * 28 + "╯")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        # Bind socket
        serverSocket.bind((HOST, PORT))
        # listen
        serverSocket.listen(10)
        print(f"Awaiting Connection on port {PORT} ...\n")

        while True:  # Keep the server running
            conn, addr = serverSocket.accept()  # Accept connections using the socket
            time.sleep(1)

            # Display IP and Port of connected client
            print(f"\n{'Client Connection Request':^28}\n{'─' * 28}\n- IP Address: {addr[0]}\n- Port: {addr[1]}\n{'─' * 28}\n")

            while True:
                state = {
                    "clientIp": addr[0],
                    "clientPort": addr[0],
                    "clientConnected": False,
                }

                
                # Receive and decode the first message
                msg = conn.recv(1024).decode()
                handleMessagePrintoutsServer(msg)
                
                # Process the message and get a response
                result = processMsgs(conn, msg, state)

                # return whether the operation was a success or failure
                if result == 1:
                    handleMessagePrintoutsServer(":)")
                    sys.exit()
                else:
                    handleMessagePrintoutsServer(":(")
            
     


if __name__ == "__main__":
    main()
