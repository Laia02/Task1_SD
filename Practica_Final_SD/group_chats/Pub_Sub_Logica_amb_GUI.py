import json,random, string
from tkinter import messagebox
import pika, threading,time
from pika.exchange_type import ExchangeType
import tkinter as tk

class Pub_Sub_Logica_amb_GUI:

    def __init__(self, master, ip_rabbit, username):

        self.username = username
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        print(f'User ID: {self.id} is {self.username}')
        self.connection_parameters = pika.ConnectionParameters(ip_rabbit)
        self.connection = pika.BlockingConnection(self.connection_parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='topics', exchange_type=ExchangeType.topic)
        self.queue = self.channel.queue_declare(queue='', auto_delete=True)
        self.channel.queue_bind(exchange='topics', queue=self.queue.method.queue, routing_key="discover")
        self.channel.basic_consume(queue=self.queue.method.queue, auto_ack=True, on_message_callback=self.on_message_received)
        self.discovered_topics = []
        
        
        #List that saves all the topics that the user is suscribed to
        self.list_topics = ["discover"]
        #Start consuming messages
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target= self.start_consuming, args=())
        self.thread.start()

        #Iniciem la interficie gráfica
        self.root = master
        self.gadgets = {}
        
        self.topic_label = tk.Label(master, text="Topic:")
        self.topic_label.grid(row=0, column=0, sticky="w")
        self.topic_entry = tk.Entry(master)
        self.topic_entry.grid(row=0, column=1, sticky="ew")
        
        self.message_label = tk.Label(master, text="Message:")
        self.message_label.grid(row=1, column=0, sticky="w")
        self.message_entry = tk.Entry(master)
        self.message_entry.grid(row=1, column=1, sticky="ew")
        
        self.send_button = tk.Button(master, text="Send", command=self.send_message_from_gui)
        self.send_button.grid(row=2, columnspan=2, sticky="ew")

        self.topic_listbox = tk.Listbox(master)
        self.topic_listbox.grid(row=3, column=0, columnspan=2, sticky="nsew")

        self.delete_button = tk.Button(master, text="Delete", command=self.delete_selected_topic)
        self.delete_button.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.discover_button = tk.Button(master, text="Discover Topics", command=self.discover_topics_from_gui)
        self.discover_button.grid(row=5, column=0, columnspan=2, sticky="ew")

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    #Methods to receive messages and print them in the GUI
    def start_consuming(self):
        while not self.stop_event.is_set():
            print("Thread is running...")
            try:
                self.channel.start_consuming()
            except Exception as e:
                print("Already connected.")

    def on_message_received(self, ch, method, properties, body):
        routing_key = method.routing_key
        print(f'{self.username} - received new message: {body} from {routing_key}')
        if routing_key == "discover":
            queue_name = body.decode()
            print(f'{self.username} - received discover message: {queue_name}')
            if (self.list_topics != None):
                message = json.dumps(self.list_topics)
                print(f'Sending the topics{message}')
                self.channel.basic_publish(exchange='',routing_key=queue_name, body=message, properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
        
        elif routing_key == self.id:  
            print(f'{self.username} - received a new list of topics "{self.id}": {body}')
            received_data = json.loads(body)

            # Add the topics avaible
            for item in received_data:
                if (item not in self.discovered_topics):
                    self.discovered_topics.append(item)
        else:
            print(f'{self.username} - received new message from topic "{routing_key}": {body}')
            self.receive_message_with_topic_to_gui(routing_key, body.decode())

    def receive_message_with_topic_to_gui(self, topic, message):
        if topic not in self.gadgets:
            self.create_gadget(topic, message)
        else:
            _, gadget_text = self.gadgets[topic]
            gadget_text.config(state=tk.NORMAL)
            gadget_text.insert(tk.END, "\n" + message)
            gadget_text.config(state=tk.DISABLED)

    #Methods to unsuscribe from a topic and delete it from the GUI
    def unsuscribe(self, topic):
        if topic in self.list_topics:
            self.list_topics.remove(""+topic)
            message = "#."+ topic + ".#"
            print("Unsuscribed to this topics:"+message)
            self.channel.queue_unbind(exchange='topics', queue=self.queue.method.queue, routing_key=message)
        else:
            print("You are not suscribed to this topic")

    def delete_selected_topic(self):
        selected_topic_index = self.topic_listbox.curselection()
        if selected_topic_index:
            selected_topic = self.topic_listbox.get(selected_topic_index)
            #Ens desuscribim del topic
            self.unsuscribe(selected_topic)
            if selected_topic in self.gadgets:
                gadget_frame, _ = self.gadgets[selected_topic]
                gadget_frame.grid_forget()  # Remove gadget from the grid
                del self.gadgets[selected_topic]  # Delete gadget from the dictionary
                self.topic_listbox.delete(selected_topic_index)
                # Reconfigure the grid layout
                for i, (topic, (frame, _)) in enumerate(self.gadgets.items()):
                    row_index = i // 4 + 6
                    column_index = i % 4 * 2
                    frame.grid(row=row_index, column=column_index, columnspan=2, padx=5, pady=5, sticky="ew")

    #Metodes per tractar la sortida de la finestra
    def quit_pub_sub_chats(self):
        print("Thread stopped gracefully.")
        if self.channel.is_open:
            try:
                self.channel.stop_consuming()
                self.channel.close()
                print("Thread stopped gracefully.")
            except Exception as e:
                print("Error stopping consuming: ")

        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            print("Thread stopped gracefully.")
            try:
                self.thread.join()
            except Exception as e:
                print("")
        print("Thread stopped gracefully.")
    
    def on_closing(self):
        # Ask the user if they want to quit
        if messagebox.askokcancel("Quit", "Do you want to exit from the GroupChat Server?\nAll messages and suscriptions will be deleted. Do you want to quit"):
            self.quit_pub_sub_chats()
            self.root.destroy()


    #Discovering topics from buttom in GUI
    def discover_topics_from_gui(self):
        self.discovered_topics = []
        list_of_gadgets = self.discover_topics()
        topic_list_window = tk.Toplevel(self.root)
        topic_list_window.title("Discover Topics")
        
        topic_list_label = tk.Label(topic_list_window, text="Existing Topics:")
        topic_list_label.pack()
        
        for item in list_of_gadgets:
            topic_label = tk.Label(topic_list_window, text=item)
            topic_label.pack()

    def discover_topics(self):
        print("Discovering topics")
        self.channel.queue_declare(queue=self.id, auto_delete=True)
        print("Queue declared")
        self.channel.basic_consume(queue=self.id, on_message_callback= self.on_message_received)
        print("Consuming")
        #Envia missatge de descoberta
        self.channel.basic_publish(exchange='topics', routing_key='discover', body=self.id)
        print("Looking for topics")
        time.sleep(5)
        
        return self.discovered_topics
    

    #Methods to send messages from the GUI, si esta suscrito, envia el missatge, 
    #sino, se suscribe al topic y envia el missatge
    def send_message(self, topic, message):
            if not topic in self.list_topics:
                print(f'{self.username} - you are not subscribed to the topic "{topic}"')
            else:
                print(f'{self.username} - sending message "{message}" to topic "{topic}"')
                self.channel.basic_publish(exchange='topics', routing_key=topic, body=message, properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
                print(f'{self.username} - message sent')    

    def suscribe(self, topic):
        if not topic in self.list_topics:
            print("Suscribed to this topic:" + topic)
            self.list_topics.append(topic)
            message = "#."+ topic + ".#"
            print("Suscribed to this topics:")

            for item in self.list_topics:
                print(item)

            self.channel.queue_bind(exchange='topics', queue=self.queue.method.queue, routing_key=message)
        else:  
            print("You are already suscribed to this topic")

    def send_message_from_gui(self):
        topic = self.topic_entry.get()
        message = self.username +": " +self.message_entry.get()

        if topic not in self.gadgets:
            self.suscribe(topic)
            welcome_message=f'Welcome to the {topic} GroupChat!'
            self.create_gadget(topic, welcome_message)

        else:
            """_, gadget_text = self.gadgets[topic]
            gadget_text.config(state=tk.NORMAL)
            gadget_text.insert(tk.END, "\n" + message)
            gadget_text.config(state=tk.DISABLED)"""

        self.send_message(topic, message)


    #Creates where the groupchats will be displayed
    def create_gadget(self, topic, message):
        row_index = len(self.gadgets) // 4 + 6
        column_index = len(self.gadgets) % 4 * 2
        
        gadget_frame = tk.Frame(self.root, relief=tk.GROOVE, borderwidth=2)
        gadget_frame.grid(row=row_index, column=column_index, columnspan=2, padx=5, pady=5, sticky="ew")
        
        gadget_label = tk.Label(gadget_frame, text=f"Topic: {topic}")
        gadget_label.pack(side=tk.TOP)
        
        gadget_text = tk.Text(gadget_frame, height=5, width=40, state=tk.DISABLED)
        gadget_text.pack(side=tk.TOP)
        gadget_text.config(state=tk.NORMAL)  # Make gadget editable
        gadget_text.insert(tk.END, message)  # Insert message
        gadget_text.config(state=tk.DISABLED)  # Disable editing
        
        self.gadgets[topic] = (gadget_frame, gadget_text)

        self.topic_listbox.insert(tk.END, topic)

