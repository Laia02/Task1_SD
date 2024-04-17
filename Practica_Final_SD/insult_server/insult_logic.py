import pika, threading
from .insult_windows import InsultWindows

class insult_client_logica:
    def __init__(self, ip_rabbit):
        self.stop_event = threading.Event()
        self.thread = None
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip_rabbit))
        self.channel = self.connection.channel()
        self.gui = InsultWindows()
        self.connected = False

    #Connect Server
    def connect_insult_server(self):
        if self.connected == False:
            print("conneected false")
            try:
                self.channel.queue_declare(queue='insults',durable=True)
                self.channel.basic_consume(queue='insults', on_message_callback= self.callback)

                #Start consuming messages
                print("Connected to the Insult Server.")
                self.thread = threading.Thread(target= self.startConsuming)
                self.thread.start()
                self.connected = True
            except Exception as e:
                    print("Error connecting to Insult Server:", e)

    #Send Message
    def send_message_insult_server(self, message):
        self.channel.queue_declare(queue='insults',durable=True)
        self.channel.basic_publish(exchange='', routing_key='insults',body=message, properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent
))
        
        print(f" [x] Sent {message}")

    #Close Connection
    def disconnect_insult_server(self,):
        print("Thread stopped gracefully.")

        if self.channel:
            self.channel.stop_consuming()

        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join()
        
        self.connected = False
        print("Thread stopped gracefully.")


        if self.connection is not None:
            try:
                self.connection.close()
                print("Connection closed successfully.")
            except Exception as e:
                print("Error closing connection:", e)



    def callback(self,ch, method, properties, body):
        message = body.decode("utf-8")
        print(f"Received message: '{message}'")
        self.gui.show_popup(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message


    def startConsuming(self,):
        print("Listening to insults ...")
        while not self.stop_event.is_set():
            #print("Thread is running...")
            try:
                self.channel.start_consuming()
            except pika.exceptions.ReentrancyError:
                print("Already connected to the Insult Server.")
            