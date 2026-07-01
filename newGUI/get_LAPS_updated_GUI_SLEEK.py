import ctypes
import os
import re
import subprocess
import sys
import time
import tkinter
from datetime import date
from tkinter import messagebox
import print_label
import customtkinter
import customtkinter as customTk
import qrcode
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

theme_path = resource_path("michels_theme.json")

print("THEME PATH:", theme_path)
print("EXISTS:", os.path.exists(theme_path))

customtkinter.set_default_color_theme(theme_path)

class App(customTk.CTk):
    def __init__(self):
        super().__init__()
        self.printer = print_label.LabelPrinter()
        self.geometry("900x600")
        self.title("My GUI")
        self.desktop = os.path.join(os.environ["LOCALAPPDATA"])
        self.file_path = os.path.join(self.desktop, "LAPSHistory.txt")
        self.icon_path = (resource_path('Unlock_2_HighRes.ico'))
        self.settings_path = os.path.join(
            os.environ["LOCALAPPDATA"],
            "LAPSSettings.json"
        )
        self.resizable(False, False)

        self.bind_all("<Up>", lambda e: self.password_frame.on_arrow_up(e))
        self.bind_all("<Down>", lambda e: self.password_frame.on_arrow_down(e))
        self.bind_all("<Delete>", self.handle_delete_key)
        self.bind_all("<Button-1>", self.handle_click)
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
        self.grid_rowconfigure(5, weight=1)
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
            height=400,
            fg_color="transparent"
        )

        self.qr_frame = QRCodeFrame (master=self,
                                     width=200,
                                     height=200,
                                     fg_color=("#D6D6D6","#1e1e1e"),
                                     border_color=("#333333","#fff"),
                                     border_width=2
                                     )

        self.menu_frame = MenuFrame(master=self,
                                    submit_callback=self.submit_service_tag,
                                    submit_service_tag_callback=self.submit_service_tag,
                                    run_servicenow_callback=self.password_frame.run_servicenow,
                                    browser_button_callback=self.browser_button_change,
                                    width=856, height=60, border_width=1, border_color="#333333")

        self.delete_buttons_frame = DeleteButtonsFrame(master=self,
                                                       delete_history_callback=self.delete_history,
                                                       delete_selected_callback=self.delete_selected,
                                                       reset_button_callback=self.reset_function,
                                                       print_label_callback=self.gen_and_print_label,
                                                       width=100,
                                                       height=100,
                                                       border_width=1,
                                                       border_color="#333333")


        # --- Button ---
        self.debug_btn = customTk.CTkButton(self, text="DEBUG")

        # --- Label ---
        self.qr_label = customTk.CTkLabel(self, text="")
        self.debug_label = customTk.CTkLabel(self, text="", font=('default', 16, "bold"), text_color="black")


        # --- Entry ---

        # --- Image ---
        self.image_file = customtkinter.CTkImage(light_image=Image.open(resource_path("Michels Logo We Do That And More Two Lines.png")),
                                            dark_image=Image.open(resource_path("Michels Logo We Do That And More Two Lines White.png")),
                                            size=(600, 100))
        self.michels_label = customTk.CTkLabel(self, text="", image=self.image_file)
        self.m_click_count = 0
        self.michels_label.bind("<Button-1>", lambda e: self.click(e, "Michels"))


        # --- GIF ---
        self.gif1 = CTkGif(self, resource_path("djCat.gif"), size=(800,500))
        self.gif2 = CTkGif(self, resource_path("HappyCat.gif"), size=(100, 100))
        self.gif3 = CTkGif(self, resource_path("JackHammer.gif"), size=(100, 100))

        #region Layout
        # --- Layout ---
        self.menu_frame.grid(row=0, column=0, rowspan=1, columnspan=11, padx=20, pady=(20, 0), sticky="w")
        self.password_frame.grid(row=3, column=0, columnspan=7, rowspan=3,padx=20, pady=0, sticky="nsew")
        #self.qr_label.grid(row=3, column=7, columnspan=4, sticky="n")
        self.qr_frame.grid(row=2, column=7, rowspan=3, padx=5, pady=(30,0), sticky="n")
        self.delete_buttons_frame.grid(row=5, column=7, rowspan=2, padx=5, pady=(0,10), sticky="nsew")
        self.michels_label.grid(row=6, column=0, padx=20, pady=0, columnspan=4, sticky="sw")

        #endregion

    #region defs

    def gen_and_print_label(self):
        if self.password_frame.selected is None:
            print("Nothing selected")
            return

        # Get selected text
        selected_text = next(
            (t for t, b in self.password_frame.items if b == self.password_frame.selected),
            None
        )

        if not selected_text:
            print("No text found for selection")
            return

        # Extract serial number (before comma)
        parts = selected_text.split(",", 1)
        serial_number = parts[0].strip()

        confirm_print = messagebox.askyesno("Confirm Print", f"Confirm you want to print label for {serial_number}", icon="question")
        if confirm_print:
            print("Printing label for:", serial_number)
            # Send to printer
            self.printer.generate_label(serial_number)
        else:
            print("CANCELLED printing label for:", serial_number)

    def browser_button_change(self, value):
        browser = value
        if browser == "Edge":
            self.menu_frame.browser_buttons.configure(selected_color="#0078D7", selected_hover_color="#0087F5")
        else:
            self.menu_frame.browser_buttons.configure(selected_color="#309C4D", selected_hover_color="#35AC54")

        # SAVE selection
        try:
            with open(self.settings_path, "w") as f:
                import json
                json.dump({"browser": browser}, f)
                print("Saved browser:", browser)
        except Exception as e:
            print("Error saving settings:", e)

    def click(self, event, source):
        x,y = event.x, event.y
        #print(f"Clicked at: {x}, {y}")
        #print(source)
        if source == "Michels":
            if 0 < x <= 98 and 20 < y <= 109:
                self.m_click_count += 1
                #print(self.m_click_count)
                if self.m_click_count >= 10:
                    self.surprise("Michels")

    def submit_service_tag(self, event=None):
        service_number = self.menu_frame.sn_entry.get().upper()
        #self.focus()    # changes the focus to main window, removes blinking cursor
        if service_number == "DOVE":
            self.surprise("Dove")
            self.menu_frame.sn_entry.delete(0, "end")
            return
        elif service_number == "5QFT9Y3":
            self.menu_frame.sn_entry.delete(0, "end")
            self.run_powershell(service_number)
            self.debug_label.place(x=660, y=310)
            self.debug_label.configure(text="Oh! You found an easter egg!")
            print("SECRET QR")
            self.create_qr_code("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            self.after(15000, self.reset_function)

            return

        # runs if service number is not blank
        elif service_number.strip() != "":
            print("SERVICE NUMBER: " + service_number)
            self.run_powershell(service_number)

        # runs if service number is blank
        elif service_number == "":
            self.menu_frame.sn_entry.delete(0, "end")
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

        expired = False
        expired_date = None
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
            print("Password QR")
            self.create_qr_code(f"{password_match.group(1)}")
            print("POWERSHELL DONE")
        else:
            password = "NO PASSWORD FOUND"
            self.topmost_messagebox(messagebox.showerror,
                                    "Error",
                                    f"Error Finding Password for {service_number}")
            print("POWERSHELL DONE NO PASSWORD FOUND")

            return


        # create QR Code
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(f"{service_number}, {password}\n")
        except Exception as e:
            print("File write error: ", e)

        self.load_history()

    def load_history(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            recent = lines[-100:]

            self.password_frame.delete_all()

            for line in recent:
                if "," not in line:
                    continue
                self.password_frame.add_item(line.strip())


            self.password_frame.select_last_item()

        except FileNotFoundError:
            print("File History not found")

    def delete_history(self):
        confirm_delete_box = tkinter.messagebox.askyesno("Delete History", "Are you sure you want to delete password history?")
        if confirm_delete_box:
            print("Deleting history file...")
            self.password_frame.delete_all()
            try:
                if os.path.exists(self.file_path):
                    os.remove(self.file_path)
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
                    self.current_qr_image = None

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

            with open(self.file_path, "r", encoding="utf-8") as fr:
                lines = fr.readlines()
                with open(self.file_path, "w", encoding="utf-8") as fw:
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
                self.qr_frame.label.configure(image=None, text="")
                self.qr_frame.label.image = None
                self.current_qr_image = None

            print("Finished deleting selected")
        except Exception as e:
            print("Error deleting line: ", e)

    def create_qr_code(self, data):
        qr = qrcode.make(data)
        qr = qr.resize((200, 200))
        self.current_qr_image = customTk.CTkImage(
            light_image=qr,
            dark_image=qr,
            size=(200, 200)
        )

        self.qr_frame.label.configure(image=self.current_qr_image, text="")
        self.qr_frame.label.image = self.current_qr_image

    def surprise(self, name):
        if name == "Michels":

            self.gif1.place(x=20, y=20)
        else:
            self.gif2.place(x=30, y=10)
            self.gif3.place(x=540, y=420)
        self.delete_buttons_frame.reset_button.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        self.gif1.start()
        self.gif2.start()
        self.gif3.start()

    def reset_function(self):
        self.gif1.place_forget()
        self.gif2.place_forget()
        self.gif3.place_forget()
        self.debug_label.place_forget()

        self.m_click_count = 0
        self.delete_buttons_frame.reset_button.grid_forget()

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
        print("Browser:", self.menu_frame.browser_buttons.get())
        driver = None
        try:
            if self.menu_frame.browser_buttons.get() == "Edge":
                driver_path = resource_path("msedgedriver.exe")
                service = Service(driver_path)
                try:
                    driver = webdriver.Edge(service=service)
                except Exception as e:
                    messagebox.showerror("Browser Error", str(e))
                    return
                print("Edge started")
            elif self.menu_frame.browser_buttons.get() == "Chrome":
                driver_path = resource_path("chromedriver.exe")
                service = Service(driver_path)
                try:
                    driver = webdriver.Chrome(service=service)
                except Exception as e:
                    messagebox.showerror("Browser Error", str(e))
                    return                (
                print("Chrome started"))

            #self.after(2000, self.iconify)
            #wait = WebDriverWait(driver, 10)

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
                                                        "Confirm the input info is correct.",
                                                        icon="question"
                                                        )
                    if correct_info:
                        update_button_element.click()
                    else:
                        if driver:
                            driver.quit()
                        self.topmost_messagebox(messagebox.showerror, "Error", "Input Info Was Incorrect\nPlease Fix Manually")


                except Exception as e:
                    messagebox.showerror("ServiceNow Error", str(e))
            else:
                self.topmost_messagebox(messagebox.showerror, "Error", "Error Logging In To ServiceNow")

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

    def handle_delete_key(self, event=None):
        focus = self.focus_get()

        if focus and str(focus).startswith(str(self.menu_frame.sn_entry)):
            print("Didn't delete, in Entry")
            return

        self.delete_selected()

    def handle_click(self, event):
        widget = event.widget

        if not str(widget).startswith(str(self.menu_frame.sn_entry)):
            self.focus()

    def load_settings(self):
        try:
            import json
            with open(self.settings_path, "r") as f:
                settings = json.load(f)

            print("Settings:", settings)
            browser = settings.get("browser", "Edge")
            print("Browser JSON:", browser)

            # Set the button
            self.menu_frame.after(0, lambda: (self.menu_frame.browser_buttons.set(browser),
                                  self.browser_button_change(browser)))

        except FileNotFoundError:
            # First run → default to Edge
            self.menu_frame.browser_buttons.set("Edge")
            self.browser_button_change("Edge")

        except Exception as e:
            print("Error loading settings:", e)

    #endregion

class PasswordList(customTk.CTkScrollableFrame):
    def __init__(self, master, on_select=None, **kwargs):
        super().__init__(master, **kwargs)

        self.items = []  # [(text, button)] oldest -> newest
        self.selected = None
        self.on_select = on_select
        self.spacer = customTk.CTkFrame(self, height=20, fg_color="transparent")

    def add_item(self, text):
        btn = customTk.CTkButton(
            self,
            text=text,
            anchor="w",
            font=("Segoe UI Semibold", 24, "normal"),
            height=60,
            corner_radius=2,
            border_width=2,
            border_color=("#C02918","#333333"),
            hover_color=("#EB6A5C","#df1f36"),
        )
        btn.configure(command=lambda b=btn: self.select_item(b))

        # Store chronologically (oldest -> newest)
        self.items.append((text, btn))

        # Repack UI so newest appears at TOP
        self._repack_buttons()

    def _repack_buttons(self):
        # Clear UI
        for _, b in self.items:
            b.pack_forget()

        self.spacer.pack_forget()  # ensure no duplicates

        self.spacer.pack(fill="x")


        # Pack newest first (top of UI)
        for _, b in reversed(self.items):
            b.pack(fill="x", padx=1, pady=1)


    def select_item(self, selected_btn):
        self.selected = selected_btn

        for _, btn in self.items:
            if btn == selected_btn:
                btn.configure(fg_color=("#EF8B80", "#b91c1c"))  # selected
            else:
                btn.configure(fg_color=("#D6D6D6", "#333333"))

        # Get selected text
        selected_text = next((t for t, b in self.items if b == selected_btn), None)

        if self.on_select and selected_text:
            parts = selected_text.split(", ", 1)
            password_part = parts[1] if len(parts) > 1 else parts[0]
            password = password_part.split("  |")[0]
            self.on_select(password)

    def delete_selected(self):
        if self.selected is None:
            return

        # Find index BEFORE removal
        index = self.get_selected_index()
        deleted_btn = self.selected

        # Remove from list
        self.items = [(t, b) for t, b in self.items if b != deleted_btn]

        # Destroy widget
        deleted_btn.destroy()
        self.selected = None

        # Repack remaining buttons
        self._repack_buttons()

        # Select nearest item
        if self.items:
            new_index = min(index, len(self.items) - 1)
            _, new_btn = self.items[new_index]
            self.select_item(new_btn)


    def delete_all(self):
        for _, btn in self.items:
            btn.destroy()
        self.items.clear()
        self.selected = None

    def get_selected_index(self):
        for i, (_, btn) in enumerate(self.items):
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

    def select_last_item(self):
        if self.items:
            _, last_btn = self.items[-1]  # newest item
            self.select_item(last_btn)

    def on_arrow_down(self, event):
        if not self.items:
            return

        index = self.get_selected_index()

        # If nothing selected, go to last item
        if index is None:
            index = len(self.items) - 1
        else:
            index = max(0, index - 1)

        _, btn = self.items[index]
        self.select_item(btn)

    def on_arrow_up(self, event):
        if not self.items:
            return

        index = self.get_selected_index()

        # If nothing selected, go to first item
        if index is None:
            index = 0
        else:
            index = min(len(self.items) - 1, index + 1)

        _, btn = self.items[index]
        self.select_item(btn)

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
    def __init__(self, master, submit_callback, submit_service_tag_callback, run_servicenow_callback, browser_button_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_propagate(False)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)  # entry expands
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=0)
        self.grid_columnconfigure(4, weight=0)  # divider stays tight
        self.grid_columnconfigure(5, weight=0)
        self.grid_columnconfigure(6, weight=0)

        self.sn_label = customTk.CTkLabel(self, text="Service Number", font=('default', 22, "bold"))
        self.submit_button = customTk.CTkButton(self, text="Submit", command=submit_callback, text_color="#DCE4EE")
        self.sn_entry = customTk.CTkEntry(self, placeholder_text="Enter SN Here", font=('default', 18, "bold"))
        self.sn_entry.bind("<Return>", submit_service_tag_callback)
        self.service_now_button = customTk.CTkButton(self, text="ServiceNow",
                                                     command=run_servicenow_callback, text_color="#DCE4EE")
        self.browser_buttons = customTk.CTkSegmentedButton(self, values=["Edge", "Chrome"],
                                                           command=browser_button_callback)
        #self.browser_buttons.set("Edge")
        self.browser_buttons.configure(selected_color="#0078D7", selected_hover_color="#0087F5")
        self.divider = customTk.CTkFrame(self, width=2, fg_color="#444444", height=25)

        self.sn_label.grid(row=0, column=0, padx=15, pady=15)
        self.sn_entry.grid(row=0, column=1, padx=0, pady=5, sticky="ew")
        self.submit_button.grid(row=0, column=2, padx=15, pady=5)
        self.service_now_button.grid(row=0, column=3, sticky="e")
        self.divider.grid(row=0, column=4, padx=15)
        self.browser_buttons.grid(row=0, column=5, padx=(0,20), pady=5)

class DeleteButtonsFrame(customTk.CTkFrame):
    def __init__(self, master, delete_history_callback, delete_selected_callback, reset_button_callback, print_label_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)

        self.grid_columnconfigure(0, weight=1)

        self.delete_history_button = customTk.CTkButton(self, command=delete_history_callback, text="Delete History", border_color="#55565a", border_width=2, fg_color="transparent", hover_color=("#CCCCCC","#474747"))
        self.delete_selected_button = customTk.CTkButton(self, command=delete_selected_callback, text="Delete Selected", border_color="#55565a", border_width=2, fg_color="transparent", hover_color=("#CCCCCC","#474747"))
        self.reset_button = customTk.CTkButton(self, text="Remove GIFs",
                                               command=reset_button_callback,
                                               fg_color="#deb10d",
                                               hover_color="#f0c93e",
                                               text_color="black")
        self.temp_button = customTk.CTkButton(self, text="Print Label", border_color="#55565a", border_width=2, fg_color="transparent", hover_color=("#CCCCCC","#474747"), command=print_label_callback)
        #self.temp_button2 = customTk.CTkButton(self, text="Temp", border_color="#55565a", border_width=2, fg_color="transparent", hover_color="#474747")
        self.fun_bar = customTk.CTkProgressBar(master=self, mode="indeterminate", progress_color="#fdb916", indeterminate_speed=.3, width=30, corner_radius=12)

        self.delete_selected_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.delete_history_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.temp_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        #self.temp_button2.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.fun_bar.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.fun_bar.start()

if __name__ == '__main__':
    app = App()
    print("Today's Date: ", date.today())
    print("File path: ", app.file_path)
    app.load_history()
    app.password_frame.select_last_item()
    app.title("Get LAPS History")
    app.load_settings()

    app.mainloop()
