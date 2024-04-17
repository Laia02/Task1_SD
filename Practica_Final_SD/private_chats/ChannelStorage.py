import NameSpace as NameSpace, grpc

import protos.privateServer_pb2 as privateServer_pb2
import protos.privateServer_pb2_grpc as privateServer_pb2_grpc

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

class ChannelStorage:

    def __init__(self):
        self.channels = {}
        self.client_redis= NameSpace.NameSpace(REDIS_HOST, REDIS_PORT)


    def send_message(self,sender, receiver, message):
        # create a stub (client)
        try:
            stub = privateServer_pb2_grpc.PrivateChatServiceStub(self.channels[receiver])

            # create a valid request message
            missatge = privateServer_pb2.Missatge(sender= sender, receiver=receiver, content= message)

            stub.EnviarMissatge(missatge)
            print(f"Message sent to '{receiver}' channel.")
        except Exception as e:
            print(f"Error sending message to '{receiver}', user disconnected.")

        

    def add_channel(self, name):
        ip, port = self.client_redis.get_by_username(name)
        if ip == None:
            print(f"Couldn't deliver your message because the user: '{name}' does not exist.")
        else:
            print(f"Adding channel '{name}' with ip '{ip}' and port '{port}'.")
            # open a gRPC channel
            self.channels[name] = grpc.insecure_channel(ip+':'+str(port))
        

    def receptor_message(self, sender, receiver, message):
        # Check if the channel exists
        if receiver in self.channels:
            print(f"Sending message to '{receiver}' channel.")
            self.send_message(sender, receiver, message)
        else:

            print(f"Channel '{receiver}' does not exist.")
            self.add_channel(receiver)
            self.send_message(sender, receiver, message)
