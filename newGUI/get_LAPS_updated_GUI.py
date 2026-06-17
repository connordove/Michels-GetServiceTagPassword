import ctypes
import os
import re
import subprocess
import sys
import threading
import time
import tkinter
from tkinter import messagebox
from datetime import date
import customtkinter
import customtkinter as customTk
import qrcode
from PIL import Image, ImageTk
from keyring import set_keyring
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from unicodedata import unidata_version


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

customtkinter.set_default_color_theme(
    resource_path("newGUI/michels_theme.json")
)

class App(customTk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("920x630")
        self.title("My GUI")
        self.icon_path = (resource_path('newGUI/michels_icon.ico'))
        try:
            self.iconbitmap(self.icon_path)
        except Exception as e:
            print("iconbitmap failed, falling back: ", e)

            icon=ImageTk.PhotoImage(Image.open(self.icon_path))
            self.icon = icon
            self.iconphoto(False, self.icon)
        #region grid
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.grid_columnconfigure(5, weight=1)
        self.grid_columnconfigure(6, weight=1)
        self.grid_columnconfigure(7, weight=1)
        self.grid_columnconfigure(8, weight=1)
        self.grid_columnconfigure(9, weight=1)
        self.grid_columnconfigure(10, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=2)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, weight=1)
        self.grid_rowconfigure(9, weight=1)
        self.grid_rowconfigure(10, weight=1)
        #endregion

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
                                     fg_color="#2b2b2b",
                                     border_color="#fff",
                                     border_width=2

                                     )

        self.menu_frame = MenuFrame(master=self,
                                    submit_callback=self.submit_service_tag,
                                    submit_service_tag_callback=self.submit_service_tag,
                                    run_servicenow_callback=self.password_frame.run_servicenow,
                                    width=680, height=60)

        self.delete_buttons_frame = DeleteButtonsFrame(master=self,
                                                       delete_history_callback=self.delete_history,
                                                       delete_selected_callback=self.delete_selected,
                                                       width=100,
                                                       height=100)


        # --- Button ---
        self.debug_btn = customTk.CTkButton(self, text="DEBUG")
        self.reset_button = customTk.CTkButton(self, text="Remove GIFs",
                                               command=self.reset_function,
                                               fg_color="#deb10d",
                                               hover_color="#f0c93e",
                                               text_color="black")

        self.browser_buttons = customTk.CTkSegmentedButton(self, values=["Edge", "Chrome"], command=self.browser_button_change)
        self.browser_buttons.set("Edge")
        self.browser_buttons.configure(selected_color="#0078D7", selected_hover_color="#0087F5")

        # --- Label ---
        self.password_label = customTk.CTkLabel(self, text="Password will appear below", font=('default', 22, "bold"), anchor="w")
        self.qr_label = customTk.CTkLabel(self, text="")
        self.debug_label = customTk.CTkLabel(self, text="", font=('default', 16, "bold"), text_color="black")


        # --- Entry ---

        # --- Image ---
        self.image_file = customtkinter.CTkImage(light_image=Image.open(resource_path("newGUI\\MichelsWeDoThat.png")),
                                            dark_image=Image.open(resource_path("newGUI\\MichelsWeDoThat.png")),
                                            size=(850, 50))
        self.michels_label = customTk.CTkLabel(self, text="", image=self.image_file)
        self.m_click_count = 0
        self.michels_label.bind("<Button-1>", lambda e: self.click(e, "Michels"))

        # --- GIF ---
        self.gif1 = CTkGif(self, resource_path("newGUI\\djCat.gif"), size=(600,400))
        self.gif2 = CTkGif(self, resource_path("newGUI\\HappyCat.gif"), size=(100, 100))
        self.gif3 = CTkGif(self, resource_path("newGUI\\JackHammer.gif"), size=(100, 100))

        #region Layout
        # --- Layout ---
        self.menu_frame.grid(row=0, column=0, rowspan=1, columnspan=8, padx=20, pady=10, sticky="w")
        self.browser_buttons.grid(row=1, column=6, sticky="e")
        #self.password_label.grid(row=1, column=0, padx=30, pady=10, columnspan=2, sticky="w")
        self.password_frame.grid(row=3, column=0, columnspan=7, rowspan=4,padx=20, pady=20, sticky="nsew")
        #self.qr_label.grid(row=3, column=7, columnspan=4, sticky="n")
        self.qr_frame.grid(row=3, column=7, rowspan=2, padx=5, pady=20, sticky="nsew")
        self.delete_buttons_frame.grid(row=5, column=7, rowspan=2, padx=5, pady=20, sticky="nsew")

        self.michels_label.grid(row=7, column=0, padx=20, pady=10, columnspan=10, sticky="w")

        #endregion

    #region defs
    def browser_button_change(self, value):
        browser = value
        if browser == "Edge":
            self.browser_buttons.configure(selected_color="#0078D7", selected_hover_color="#0087F5")
        else:
            self.browser_buttons.configure(selected_color="#309C4D", selected_hover_color="#35AC54")

    def click(self, event, source):
        x,y = event.x, event.y
        #print(f"Clicked at: {x}, {y}")
        #print(source)
        if source == "Michels":
            if 5 < x <= 54 and 2 < y <= 46:
                self.m_click_count += 1
                #print(self.m_click_count)
                if self.m_click_count >= 10:
                    self.surprise("Michels")

    def submit_service_tag(self, event=None):
        service_number = self.menu_frame.sn_entry.get().upper()
        self.focus()    # changes the focus to main window, removes blinking cursor
        if service_number == "DOVE":
            self.surprise("Dove")
            self.menu_frame.sn_entry.delete(0, "end")
            return
        elif service_number == "5QFT9Y3":
            self.menu_frame.sn_entry.delete(0, "end")
            self.run_powershell(service_number)
            self.create_qr_code("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            self.debug_label.place(x=660, y=280)
            self.debug_label.configure(text="Oh! You found an easter egg!")
            self.after(15000, self.reset_function)

        # runs if service number is not blank
        elif service_number != "":
            print("SERVICE NUMBER: " + service_number)
            self.password_label.configure(text="Running...")
            self.run_powershell(service_number)

        # runs if service number is blank
        elif service_number == "":
            self.menu_frame.sn_entry.delete(0, "end")
            self.password_label.configure(text="Service Number cannot be blank")
            self.topmost_messagebox(messagebox.showerror,
                                    "Error",
                                    "Service Number Cannot Be Blank")

        self.menu_frame.sn_entry.delete(0, "end")

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
            self.topmost_messagebox(messagebox.showerror,
                                    "Error",
                                    f"Error Finding Password for {service_number}")

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

    def surprise(self, name):
        if name == "Michels":

            self.gif1.place(x=150, y=80)
        else:
            self.gif2.place(x=20, y=20)
            self.gif3.place(x=750, y=445)
        self.gif1.start()
        self.gif2.start()
        self.gif3.start()
        self.reset_button.place(x=740, y=25)

    def reset_function(self):
        self.gif1.place_forget()
        self.gif2.place_forget()
        self.gif3.place_forget()
        self.debug_label.place_forget()

        self.m_click_count = 0
        self.reset_button.place_forget()

    def service_now(self, service_number):
        self.after(0, lambda: self._service_now_task(service_number))
        """threading.Thread(
            target=self._service_now_task,
            args=(service_number,),
            daemon=True
        ).start()
        """

    def _service_now_task(self, service_number):
        print("ServiceNow thread started")
        print("Browser:", self.browser_buttons.get())
        driver = None
        try:
            if self.browser_buttons.get() == "Edge":
                driver_path = resource_path("newGUI\\msedgedriver.exe")
                service = Service(driver_path)
                driver = webdriver.Edge(service=service)
                print("Edge started")
            elif self.browser_buttons.get() == "Chrome":
                driver_path = resource_path("newGUI\\chromedriver.exe")
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service)
                print("Chrome started")

            #self.after(2000, self.iconify)
            wait = WebDriverWait(driver, 10)

            driver.get(f"https://itsupport.michels.us/now/nav/ui/classic/params/target/alm_hardware.do%3Fsysparm_query=asset_tag%3D{service_number}%26sysparm_view=MyCompanyAssets")
            time.sleep(3)
            #messagebox.askyesno("Hey", "Sup")
            login = self.topmost_messagebox(
                messagebox.askyesno,
                "Login",
                message="Confirm ServiceNow Login",
                icon="question"
            )

            if login:
                try:
                    macroponent = driver.find_element(By.CSS_SELECTOR,"macroponent-f51912f4c700201072b211d4d8c26010")
                    root1 = macroponent.shadow_root
                    print("Found macro root!")

                    iframe = root1.find_element(By.ID, "gsft_main")
                    print("Found iframe!")
                    driver.switch_to.frame(iframe)
                    print("Entered iframe")

                    asset_tag_element = driver.find_element(By.ID, "sys_readonly.alm_hardware.asset_tag")
                    print("Found asset_tag_element!")

                    state_element = driver.find_element(By.ID, "alm_hardware.install_status")
                    print("Fount state_element!")

                    substate_element = driver.find_element(By.ID, "alm_hardware.substatus")
                    print("Fount substate_element!")

                    stockroom_element = driver.find_element(By.ID, "sys_display.alm_hardware.stockroom")
                    print("Fount stockroom_element!")

                    driver.execute_script("arguments[0].style.border='3px solid red'", asset_tag_element)
                    driver.execute_script("arguments[0].style.border='3px solid red'", state_element)
                    driver.execute_script("arguments[0].style.border='3px solid red'", substate_element)
                    driver.execute_script("arguments[0].style.border='3px solid red'", stockroom_element)

                    select = Select(state_element)
                    select.select_by_value("6")

                    select = Select(substate_element)
                    select.select_by_value("available")

                    if stockroom_element.get_attribute("value") != "Brownsville Warehouse":
                        stockroom_element.send_keys("Brownsville Warehouse")
                        time.sleep(1)

                    update_button_element = driver.find_element(By.ID, "sysverb_update")
                    driver.execute_script("arguments[0].style.border='5px solid #512888'", update_button_element)

                    correct_info = self.topmost_messagebox(
                                                        messagebox.askyesno,
                                                        "Confirm Info",
                                                        "Confirm the input info is correct:\nDoes info require modification?",
                                                        icon="question"
                                                        )
                    if not correct_info:
                        update_button_element.click()

                except Exception as e:
                    messagebox.showerror("ServiceNow Error", str(e))

        finally:
            if driver:
                driver.quit()
            #self.deiconify

    # MADE WITH COPILOT
    def topmost_messagebox(self, func, *args, **kwargs):
        temp = customTk.CTkToplevel()

        # Hide window visually
        temp.withdraw()

        # Give it your icon
        temp.iconbitmap(self.icon_path)

        # IMPORTANT: remove window decorations entirely
        temp.overrideredirect(True)

        # Make only THIS invisible window topmost
        temp.attributes('-topmost', True)

        # Ensure it's created before dialog
        temp.update()

        result = func(*args, parent=temp, **kwargs)

        temp.destroy()
        return result

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

    def run_servicenow(self):
        if self.selected is None:
            messagebox.showerror("Error", "Please select a Service Number.")
            return
        selected_text = next((t for t, b in self.items if b == self.selected), None)
        if not selected_text:
            messagebox.showerror("Error", "Could not find selected item.")
            return

        parts = selected_text.split(",", 1)
        service_number = parts[0]
        print("Running Service Now... SN:", service_number)
        app.service_now(service_number)

class QRCodeFrame(customTk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # prevent frame from resizing
        self.grid_propagate(False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = customTk.CTkLabel(self, text="QR Code Will Appear Here", font=('Roboto', 16))
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

# THIS WAS MADE FROM COPILOT
class CTkGif(customTk.CTkLabel):
    def __init__(self, master, path, size=None, loop=True):
        """
        Args:
            master: parent widget
            path (str): path to GIF file
            size (tuple): (width, height) or None for original size
            loop (bool): loop animation
        """
        super().__init__(master, text="")

        self.path = path
        self.size = size
        self.loop = loop

        self.frames = []
        self.delays = []

        self._load_gif()

        self._current = 0
        self._running = False

    def _load_gif(self):
        gif = Image.open(self.path)

        try:
            while True:
                frame = gif.copy()

                # Resize if needed
                if self.size:
                    frame = frame.resize(self.size)

                self.frames.append(ImageTk.PhotoImage(frame))

                # Get frame duration (fallback = 100ms)
                delay = gif.info.get("duration", 100)
                self.delays.append(delay)

                gif.seek(len(self.frames))
        except EOFError:
            pass

    def start(self):
        if not self._running:
            self._running = True
            self._animate()

    def stop(self):
        self._running = False

    def _animate(self):
        if not self._running or not self.frames:
            return

        self.configure(image=self.frames[self._current])

        delay = self.delays[self._current]
        self._current += 1

        if self._current >= len(self.frames):
            if self.loop:
                self._current = 0
            else:
                self._running = False
                return

        self.after(delay, self._animate)

class MenuFrame(customTk.CTkFrame):
    def __init__(self, master, submit_callback, submit_service_tag_callback, run_servicenow_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_propagate(False)

        self.sn_label = customTk.CTkLabel(self, text="Service Number", font=('default', 22, "bold"))
        self.submit_button = customTk.CTkButton(self, text="Submit", command=submit_callback)
        self.sn_entry = customTk.CTkEntry(self, placeholder_text="Enter SN Here", font=('default', 18, "bold"))
        self.sn_entry.bind("<Return>", submit_service_tag_callback)
        self.service_now_button = customTk.CTkButton(self, text="ServiceNow",
                                                     command=run_servicenow_callback)

        self.sn_label.grid(row=0, column=0, padx=20, pady=15)
        self.sn_entry.grid(row=0, column=1, padx=0, pady=5)
        self.submit_button.grid(row=0, column=2, padx=15, pady=5)
        self.service_now_button.grid(row=0, column=3, sticky="e")

class DeleteButtonsFrame(customTk.CTkFrame):
    def __init__(self, master, delete_history_callback, delete_selected_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)

        self.grid_columnconfigure(0, weight=1)

        self.delete_history_button = customTk.CTkButton(self, command=delete_history_callback, text="Delete History")
        self.delete_selected_button = customTk.CTkButton(self, command=delete_selected_callback, text="Delete Selected")

        self.delete_selected_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.delete_history_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

if __name__ == '__main__':
    app = App()
    print("Today's Date: ", date.today())
    desktop = os.path.join(os.environ["USERPROFILE"], "OneDrive - Michels Corporation", "Desktop")
    file_path = os.path.join(desktop, "LAPSHistory.txt")
    print("File path: ", file_path)
    app.load_history()
    app.title("Get LAPS History")

    app.mainloop()
