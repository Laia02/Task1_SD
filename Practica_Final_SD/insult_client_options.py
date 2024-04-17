from insult_server.insult_logic import insult_client_logica
IP_RABBIT = "localhost"

def main():

    print("Welcome to the Insult Server!")
    print("\nSelect and option. Remeber that before sending and insult you have to connect to the server\n")

    client = insult_client_logica(IP_RABBIT)

    while True:
        print("1. Connect to the Insult Server")
        print("2. Send an insult to a random person")
        print("3. Quit the Insult Server :(\n")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':

            #OPCIO DE CONNECTARSE SERVER
            print("You chose Option 1, Welcome to the Insult Server!")
            #Connect to the server
            client.connect_insult_server()
            #Start consuming messages
                

        elif choice == '2':
            
            message = input("You chose Option 2, Enter the insult you want to send: ")
            print("Your message is:", message)
            client.send_message_insult_server(message)
            
        elif choice == '3':
            print("You chose Option 3, Bye Bye!")
            client.disconnect_insult_server()
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
