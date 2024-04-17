class PrivateChatService:

    def __init__(self, app):
        print('PrivateChatService initialized')
        print('GUI initialized')
        self.app = app
         # Create the GUI

    def enviar_missatge(self,sender, receiver, content):
        #print('Message received: ' + sender + ' ' + content)
        #Reenviem a la GUI
        self.app.receive_message(sender, content)
        return 'Done'
    
