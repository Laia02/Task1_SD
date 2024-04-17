import grpc, json
from concurrent import futures

import protos.privateServer_pb2 as privateServer_pb2
import protos.privateServer_pb2_grpc as privateServer_pb2_grpc

from private_chat_gui import MultiChatApp
from privatechat_service import PrivateChatService

# create a class to define the server functions, derived from
# insultingServer_pb2_grpc.InsultingServiceServicer
class PrivateChatServiceServicer(privateServer_pb2_grpc.PrivateChatServiceServicer):

    def EnviarMissatge(self, missatge, context):
        privatechat_service.enviar_missatge(missatge.sender, missatge.receiver, missatge.content)
        response = privateServer_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
        return response

try:     
    
    with open('config.json', 'r') as file:
        data = json.load(file)
        username = data['username']
        port = data['port']

except json.JSONDecodeError as e:
    print(f"Configure the client first before starting the server!': {e}")

# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# listen on port 50051
print('Starting server. Listening on port' + str(port))
server.add_insecure_port('0.0.0.0:'+str(port))
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
privateServer_pb2_grpc.add_PrivateChatServiceServicer_to_server(PrivateChatServiceServicer(),server)

app = MultiChatApp(username)
privatechat_service = PrivateChatService(app)
app.root.mainloop()
