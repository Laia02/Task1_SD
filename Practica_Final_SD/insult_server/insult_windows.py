import tkinter as tk

class InsultWindows :
    
    def show_popup(self,message):
        popup = tk.Tk()
        popup.geometry("300x200")
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - 300) // 2
        y = (screen_height - 200) // 2
        popup.geometry(f"+{x}+{y}")
        popup.configure(bg='red')
        popup.title("Received Message")
        font = ("Helvetica", 30)
        frame = tk.Frame(popup, bg='red')
        frame.pack(fill=tk.BOTH, expand=True)
        label = tk.Label(frame, text=message, font=font, bg='red', fg='white')
        label.pack(expand=True)
        popup.after(2000, self.close_popup, popup)
        popup.lift()
        popup.wm_attributes("-topmost", 1)
        popup.mainloop()

    def close_popup(self, window):
        window.destroy()