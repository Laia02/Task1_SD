import redis
import json

class NameSpace:

    def __init__(self,redis_ip, redis_port):
        try:
            self.redis_client = redis.StrictRedis(host=redis_ip, port=redis_port, decode_responses=True)
            #Code to check if the connection is working
            existing_user_info_list = self.redis_client.lrange('user_info_list', 0, -1)
        except Exception as e:
            print("Error: Redis is not connected. Please check if the Redis server is running.")
            exit(1)

    def discover_chat(self):
        # Retrieve user information list from Redis
        user_info_list_json = self.redis_client.lrange('user_info_list', 0, -1)
        name_list = []
        if user_info_list_json:
            for user_info_json in user_info_list_json:
                user_info_dict = json.loads(user_info_json)
                for name in user_info_dict:  # Iterate over each dictionary in the list
                    if name != self.username:
                        name_list.append(name)
            return name_list
        else:
            return name_list

    def configure_user(self, username, ip, port):
        self.username = username
        self.ip = ip
        self.port = port
        
        # Create a dictionary with user information
        user_info = {self.username: {'ip': self.ip, 'port': self.port}}

        # Retrieve existing user info list or initialize an empty list
        existing_user_info_list = self.redis_client.lrange('user_info_list', 0, -1)

        if not existing_user_info_list:
             # If the list doesn't exist, create a new list with the user info
            self.redis_client.rpush('user_info_list', json.dumps(user_info))  # Encode the list properly
            return True
        else:
            #Check if the user exists
            doesExist = self.does_user_exist( existing_user_info_list, self.username)
            if doesExist:
                return False
            else:
                # If the list already exists, and the user is not registered, append the new user info
                existing_user_info_list.append(json.dumps(user_info))  # Serialize the dictionary to JSON
                self.redis_client.delete('user_info_list')  # Clear the existing list
                self.redis_client.rpush('user_info_list', *existing_user_info_list)  # Push the updated list
                return True
           
    def does_user_exist(self, existing_user_info_list, username):
        for user_info_json in existing_user_info_list:
            user_info_dict = json.loads(user_info_json)
            if username in user_info_dict:
                return True
        return False
            
    def get_by_username(self,username):
        print("Connecting to chat...")
        user_info_list_json = self.redis_client.lrange('user_info_list', 0, -1)

        if user_info_list_json:
            for user_info_json in user_info_list_json:
                user_info_dict = json.loads(user_info_json)
                if username in user_info_dict:
                    user_info = user_info_dict[username]
                    #print("User information retrieved from Redis:")
                    #print(f"Name: {username}")
                    #print(f"IP address: {user_info['ip']}")
                    #print(f"Port: {user_info['port']}")
                    return user_info['ip'], user_info['port']
                    
        return None, None


    def disconnect_user(self):
        # Retrieve existing user info list or initialize an empty list
        existing_user_info_list = self.redis_client.lrange('user_info_list', 0, -1)
        if existing_user_info_list:
            # If the list already exists, iterate over each user info
            for index, user_info_json in enumerate(existing_user_info_list):
                user_info_dict = json.loads(user_info_json)
                if self.username in user_info_dict:
                    self.redis_client.lrem('user_info_list', index, user_info_json)  # Remove the user info at index
                    break  # Stop iterating after the first occurrence is removed

    
 