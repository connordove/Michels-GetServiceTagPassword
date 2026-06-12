import customtkinter
import customtkinter as customTk



class App(customTk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x800")
        self.title("My GUI")

        # --- Button ---
        self.button = customTk.CTkButton(self, command=self.button_clicked)
        self.button.grid(row=0, column=0, padx=20, pady=20)

    def button_clicked(self):
           print("Button clicked")


#if __name__ == '__main__':
app = App()
app.mainloop()