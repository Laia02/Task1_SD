import random, json,os,subprocess, threading
import private_chats.NameSpace as NameSpace
from group_chats.Pub_Sub_Logica_amb_GUI import Pub_Sub_Logica_amb_GUI
import tkinter as tk
import time


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
SERVER_PATH= 'private_chats/AAprivatechat_server.py'
INSULT_PATH = 'insult_client_options.py'
IP = '127.0.0.1'
IP_RABBIT = "localhost"
#ID = ''

def get_user_info():
    username = input("Enter your name: ")
    ip = IP
    port = random.randint(10000, 49151)
    return username, ip, port

def configure_user(redis_client):
    flag = False
    username, ip, port = get_user_info()
    
    while not flag:
        #We are going to check if the username before addig it to the redis
        flag = redis_client.configure_user(username, ip, port)
        if not flag:
            print("Username already exists.")
            username = input("Please enter a different username: ")
    
    return username, port

def generate_config(username, port):
    config = {
        "username": username,
        "port": port
    }

    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

def execute_script(script_path):
    subprocess.run(['python', script_path])

def access_insult_server():

    #Command to open a cmd window and execute the script
    command = ["start", "cmd", "/k", "python", INSULT_PATH]
    
    # Open a new command prompt window and execute the script
    subprocess.run(command, shell=True)

    #os.system('python AAprivatechat_server.py')



def main():

    # Create a Redis client and connect it to the Redis server
    print("Welcome to Laia's Chat!\nConnecting to Redis...")
    try:
        redis_client = NameSpace.NameSpace(REDIS_HOST, REDIS_PORT)
    except Exception as e:
        print("Error: Redis is not connected. Please check if the Redis server is running.")
        exit(1)

    #We register the user in Redis
    username, p = configure_user(redis_client)
    print("User information has been stored in Redis.")
    
    generate_config(username, p)
    print("config.json has been generated successfully.")

    # Create threads for each script
    server_thread = threading.Thread(target=execute_script, args=(SERVER_PATH,))
    server_thread.start()

    time.sleep(1.3)

    while True:
        print("\nOptions Menu:")
        print("1. Discover Chats")
        print("2. Subscribe to Group Chat")
        print("3. Access Insult Server")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            print("Discovering users...")
            name_list = redis_client.discover_chat()
            if name_list:
                print("Available user names:")
                for name in name_list:
                    print(name)
            else:
                print("No users found.")

        elif choice == "2":
            print("Subscribe to Group Chat")
            root = tk.Tk()
            pub_sub = Pub_Sub_Logica_amb_GUI(root,IP_RABBIT,username)
            root.mainloop()

        elif choice == "3":
            print("Access Insult Server")
            # Create a new thread
            insult_server_thread = threading.Thread(target=access_insult_server)
            # Start the thread
            insult_server_thread.start()
        elif choice == "4":
            redis_client.disconnect_user()
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()