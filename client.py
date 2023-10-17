import socket
import sys
import math


def serverHello():
    """Generates server hello message"""
    status = "100 Hello"
    return status


def AllGood():
    """Generates 200 OK"""
    status = "200 OK"
    return status


def ErrorCondition():
    """Generates 400 Error"""
    status = "400 Error"
    return status


def PrimeCollect():
    """Accepts a prime number to send to the server"""
    primeNbr = int(input("Enter a prime number between 1031 and 6397: "))

    if not isPrime(primeNbr):
        print(primeNbr, "is not prime")
        return PrimeCollect()
    if primeNbr < 1031 or primeNbr > 6397:
        print(primeNbr, "is not within the range 1031 and 6397")
        return PrimeCollect()

    return primeNbr


def PrimeMsg(prime1, prime2):
    """Generates the first prime number to send"""
    msg = "105 Primes " + str(prime1) + " " + str(prime2)
    return msg


def getLocallyComputedLCM(prime1, prime2):
    """LCM of the primes as calculated by the client"""
    gcd = math.gcd(prime1, prime2)
    lcm = (prime1 * prime2) // gcd
    return lcm


def isPrime(number):
    """Function to determine if a number is a prime"""
    if number <= 3:
        return True
    if number % 2 == 0 or number % 3 == 0 or number <= 1:
        return False

    for i in range(5, int(math.isqrt(number)) + 1, 6):
        if number % i == 0 or number % (i + 2) == 0:
            return False

    return True


# s     = socket
# msg   = message being processed
# state = dictionary containing state variables
def processMsgs(s, msg, state):
    """This function processes messages that are read through the socket. It
    returns 1 for success and 0 for failure."""

    # send initial message if the connection has not been established
    if not state.get("connectionEstablished", False):
        s.send(msg.encode())
        handleMessagePrintouts(msg,state.get("serverHost"),state.get("serverPort"))
        state["connectionEstablished"]=True
  
    # decodes handles decoding incoming requests
    serverMsg = s.recv(1024).decode()
    handleMessagePrintouts(serverMsg)

    # use status code to determine the recursive call

    statusCode = int(serverMsg.split(" ")[0])

    if statusCode == 101:
        handleMessagePrintouts("prime")
        # collect primes from user
        firstPrime = int(PrimeCollect())
        secondPrime = int(PrimeCollect())

        # construct prime message
        primeMessage = PrimeMsg(firstPrime, secondPrime)

        handleMessagePrintouts(primeMessage)
        
        state["firstPrime"] = firstPrime
        state["secondPrime"] = secondPrime

        s.send(primeMessage.encode())
        # processes prime message recursively
        return processMsgs(s, primeMessage, state)

    elif statusCode == 107:
        # get the server computed lcm and compare it to the locally computed lcm
        serverComputedLCM = int(serverMsg.split(" ")[-1])
        locallyComputedLCM = getLocallyComputedLCM(state.get("firstPrime"), state.get("secondPrime"))
    
        print("Locally Computed LCM:",locallyComputedLCM)

        # send the appropriate response based on their equality
        if serverComputedLCM == locallyComputedLCM:
            response = AllGood()
        else:
            response = ErrorCondition()

        # handleMessagePrintouts(response)

        s.send(response.encode())

    
        # Return whether the operation was a success or failure
        return 1 if serverComputedLCM == locallyComputedLCM else 0


def handleMessagePrintouts(message, hostname=None, port=None,locallyComputedLCM=None):
    """Function to handle printouts of outgoing and incoming message on the client side"""
    status_codes = {
        100: ("Connection Request", True),
        101: ("Connection Acknowledgement", True),
        200: ("Success Message", False),
        400: ("Failure Message", False),
        105: ("Prime Number Exchange", False),
        107: ("LCM Calculation", True),
        500: ("Bad Request", False),
    }

    if message == "prime":
        print("\n" + "─" * 28 + "\nPrime Number Collection\n" + "─" * 28 + "\n")
        return
    if message == ":)":
        print("\n" + "─" * 28 + "\nOperation Successful\n" + "─" * 28 + "\n")
        return
    if message == ":(":
        print("\n" + "─" * 28 + "\nOperation Unsuccessful\n" + "─" * 28 + "\n")
        return

    def printInfo(title, outgoing, hostname=None, port=None):
        """function to determine the printout where the message is moving from"""
        print("\n" + "─" * 28 + f"\n{title}\n" + "─" * 28 + "\n")

        if title == "Connection Request" and hostname and port:
            print(f"- Hostname: {hostname}\n- Port: {port}")
        if not outgoing:
            to, fro = "Server", "Client"
        else:
            fro, to = "Server", "Client"

        print(fro, " -> ", to)

    # if the first item cannot be parsed the request is bad
    try:
        statusCode = int(message.split(" ")[0])
    except ValueError:
        statusCode = 500

    # set a default of an unknown request which will have a status code of 500 and a message of "Bad Request"
    title, outgoing = status_codes.get(statusCode, ("Unknown Request", False))
    printInfo(title, outgoing,hostname,port)
  

    if statusCode == 101:
        print(f"Message: {' '.join(message.split(' ')[1:])}\nStatus Code: {message.split()[0]}")
    elif statusCode != 500:
        print(f"Message: {message.split()[1]}\nStatus Code: {message.split()[0]}")
    else:
        print("Status Code: 500\nMessage: Bad Request")
    if statusCode == 105:
        print(f"First Prime: {message.split()[2]}\nSecond Prime: {message.split()[3]}")
    if statusCode == 107:
        print("Server Computed LCM :", message.split(" ")[2])
        


def main():
    """Driver function for the project"""
    args = sys.argv
    if len(args) != 3:
        print("Please supply a server address and port.")
        sys.exit()

    serverHost = str(args[1])  # The remote host
    serverPort = int(args[2])  # The port used by the server

    print("╭" + "─" * 28 + "╮")
    print(f"│{'Client of Joan A. Smith':^28}│")
    print("╰" + "─" * 28 + "╯")
    print(
        """
    The purpose of this program is to collect two prime numbers from the client, and then
    send them to the server. The server will compute their LCM and send it back to the
    client. If the server-computed LCM matches the locally computed LCM, the
    client sends the server a 200 OK status code. Otherwise, it sends a 400 error status code,
    and then closes the socket to the server.
    """
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
        clientSocket.connect((serverHost, serverPort))
        msg = serverHello()

        state = {
            "serverHost": serverHost,
            "serverPort": serverPort,
            "connectionEstablished": False,
            "firstPrime" : None, #just to let you know it exists
            "secondPrime" : None
        }

        result = processMsgs(clientSocket, msg, state)

        if result == 1:
            handleMessagePrintouts(":)")
        else:
            handleMessagePrintouts(":(")

        # connection is automatically closed using the "with as" syntax in python


if __name__ == "__main__":
    main()
