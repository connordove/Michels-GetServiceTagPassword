import ctypes
import os
import re
import subprocess
import tkinter
from tkinter import messagebox
from datetime import date
import customtkinter
import customtkinter as customTk
import qrcode
from customtkinter import CTkImage

class App(customTk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("900x600")
        self.title("My GUI")

        # --- Frame ---

        self.password_frame = PasswordList(
            master=self,
            on_select=self.create_qr_code,
            width=600,
            height=400
        )

        self.qr_frame = QRCodeFrame (master=self,
                                     width=200,
                                     height=200,
                                     fg_color="transparent")

        # --- Button ---
        self.debug_btn = customTk.CTkButton(self, text="DEBUG")
        self.submit_button = customTk.CTkButton(self, command=self.submit_service_tag, text="Submit")
        self.delete_history_button = customTk.CTkButton(self, command=self.delete_history, text="Delete History")
        self.delete_selected_button = customTk.CTkButton(self, command=self.delete_selected, text="Delete Selected")

        # --- Label ---
        self.sn_label = customTk.CTkLabel(self, text="Service Number", font=('default', 22, "bold"))
        self.password_label = customTk.CTkLabel(self, text="Password will appear below", font=('default', 22, "bold"), anchor="w")
        self.qr_label = customTk.CTkLabel(self, text="")

        # --- Entry ---
        self.sn_entry = customTk.CTkEntry(self, placeholder_text="Enter SN Here", font=('default', 18, "bold"))
        self.sn_entry.bind("<Return>", self.submit_service_tag)

        # --- Layout ---
        self.sn_label.grid(row=0, column=0, padx=20, pady=15)
        self.sn_entry.grid(row=0, column=1, padx=0, pady=5)
        self.submit_button.grid(row=0, column=2, padx=15, pady=5)
        #self.password_label.grid(row=2, column=0, padx=30, pady=10, columnspan=2, sticky="w")
        self.password_frame.grid(row=3, column=0, columnspan=7, rowspan=4,padx=20, pady=20)
        self.qr_label.grid(row=3, column=7, columnspan=4, sticky="n")
        self.qr_frame.grid(row=3, column=7, rowspan=2, padx=5, pady=20, sticky="nsew")
        self.delete_selected_button.grid(row=5, column=7, padx=10, pady=20, sticky = "n")
        self.delete_history_button.grid(row=5, column=7, padx=10, pady=20, sticky="s")


    #region defs
    def submit_service_tag(self, event=None):
        service_number = self.sn_entry.get().upper()
        self.focus()    # changes the focus to main window, removes blinking cursor
        # runs if service number is not blank
        if service_number != "":
            print("SERVICE NUMBER: " + service_number)
            self.password_label.configure(text="Running...")
            self.run_powershell(service_number)

        # runs if service number is blank
        elif service_number == "":
            self.sn_entry.delete(0, "end")
            self.password_label.configure(text="Service Number cannot be blank")

        self.sn_entry.delete(0, "end")

        self.load_history()

    def run_powershell(self, service_number):
        result = subprocess.run(
            ["PowerShell",
             "-Command",
             f"Get-LapsADPassword -Identity {service_number} -asplaintext"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        output = result.stdout
        #print(output)

        password_match = re.search(r"Password\s*:\s*(\S+)", output)
        expiration_match = re.search(r"ExpirationTimestamp\s*:\s*(\S+)", output)

        if expiration_match:
            expired_string = expiration_match.group(1).split('/')
            expired_date = date(int(expired_string[2]), int(expired_string[0]), int(expired_string[1]))
            expired = (expired_date < date.today())
            print("Today: " + str(date.today()) + " Expiration: " + str(expired_date) + " Expired?: " + str(expired))
        else:
            print("No expiration timestamp")

        if password_match:
            password = password_match.group(1)
            if expired:
                password = password_match.group(1) + f"  |{expired_date}|"
        else:
            password = "NO PASSWORD FOUND"

        print("POWERSHELL DONE")

        # create QR Code
        self.create_qr_code(f"{password_match.group(1)}")

        self.password_label.configure(text="SN, Password")

        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"{service_number}, {password}\n")
        except Exception as e:
            print("File write error: ", e)

        self.after(0, self.load_history)

    def load_history(self):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            recent = lines[-100:]

            self.password_frame.delete_all()

            for line in recent:
                self.password_frame.add_item(line.strip())

        except FileNotFoundError:
            print("File History not found")

    def delete_history(self):
        confirm_delete_box = tkinter.messagebox.askyesno("Delete History", "Are you sure you want to delete password history?")
        if confirm_delete_box:
            print("Deleting history file...")
            self.password_frame.delete_all()
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    # Force Windows Explorer refresh
                    HWND_BROADCAST = 0xFFFF
                    WM_COMMAND = 0x0111
                    REFRESH = 41504

                    ctypes.windll.user32.PostMessageW(
                        HWND_BROADCAST, WM_COMMAND, REFRESH, 0
                    )
                    # delete QR code
                    self.qr_frame.label.configure(image=None, text="")
                    self.qr_frame.label.image = None
                    print("File deleted and desktop refreshed successfully.")
                else:
                    print("No history file found.")
            except FileNotFoundError:
                print("File not found.")
        else:
            print("Chose not do delete history.")
            return

    def delete_selected(self):
        try:
            selected_index = self.password_frame.get_selected_index()
            if selected_index is None:
                print("Nothing selected")
                return

            self.password_frame.delete_selected()

            with open(file_path, "r", encoding="utf-8") as fr:
                lines = fr.readlines()
                with open(file_path, "w", encoding="utf-8") as fw:
                    for i, line in enumerate(lines):
                        if i != selected_index:
                            fw.write(line)
            self.load_history()

            if self.password_frame.items:
                last_text = self.password_frame.items[-1][0]

                parts = last_text.split(", ", 1)
                password = parts[1] if len(parts) > 1 else parts[0]
                password = password.split("  |")[0]

                self.create_qr_code(password)
            else:
                # Clear QR if empty
                self.qr_label.configure(image=None, text="")
                self.qr_label.image = None

            print("Finished deleting selected")
        except Exception as e:
            print("Error deleting line: ", e)

    def create_qr_code(self, data):
        qr = qrcode.make(data)
        qr = qr.resize((200, 200))
        img = customTk.CTkImage(
            light_image=qr,
            dark_image=qr,
            size=(200, 200)
        )

        self.qr_frame.label.configure(image=img, text="")
        self.qr_frame.label.image = img  # prevent garbage collection
    #endregion

class PasswordList(customTk.CTkScrollableFrame):
    def __init__(self, master, on_select=None, **kwargs):
        super().__init__(master, **kwargs)

        self.items = []
        self.selected = None
        self.on_select = on_select

    def add_item(self, text):
        btn = customTk.CTkButton(
            self,
            text=text,
            anchor="w",
            font=("Consolas", 25, "bold"),
            height=60
        )
        btn.configure(command=lambda b=btn: self.select_item(b))

        btn.pack(fill="x", padx=5, pady=2)

        self.items.append((text, btn))

    def select_item(self, selected_btn):
        self.selected = selected_btn

        for t, btn in self.items:
            if btn == selected_btn:
                btn.configure(fg_color="#b91c1c")  # selected
            else:
                btn.configure(fg_color=("gray75", "gray25"))

        selected_text = next((t for t, b in self.items if b == selected_btn), None)

        if self.on_select and selected_text:
            # Split "SN,password"
            parts = selected_text.split(", ", 1)
            password_part = parts[1] if len(parts) > 1 else parts[0]

            password = password_part.split("  |")[0]

            self.on_select(password)

    def delete_selected(self):
        if self.selected is None:
            return

        deleted_text = next((t for t, b in self.items if b == self.selected), None)

        self.selected.destroy()
        self.items = [(t, b) for t, b in self.items if b != self.selected]
        self.selected = None

        print("Deleted: ", deleted_text)

    def delete_all(self):
        for text, btn in self.items:
            btn.destroy()
        self.items.clear()
        self.selected = None

    def get_selected_index(self):
        for i, (text, btn) in enumerate(self.items):
            if btn == self.selected:
                return i
        return None

class QRCodeFrame(customTk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # prevent frame from resizing
        self.grid_propagate(False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = customTk.CTkLabel(self, text="QR Code Will Appear Here", font=('Roboto', 16))
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

if __name__ == '__main__':
    customtkinter.set_default_color_theme(
        r"C:\Users\cdove\PycharmProjects\Michels-GetServiceTagPassword\newGUI\blue.json")
    app = App()
    print("Today's Date: ", date.today())
    desktop = os.path.join(os.environ["USERPROFILE"], "OneDrive - Michels Corporation", "Desktop")
    file_path = os.path.join(desktop, "LAPSHistory.txt")
    print("File path: ", file_path)
    app.load_history()
    app.title("Get LAPS History")
    app.iconbitmap('michels_icon.ico')

    app.mainloop()
