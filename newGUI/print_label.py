import os
import sys
import qrcode
import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont, ImageWin


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath("..")

    return os.path.join(base_path, relative_path)


class LabelPrinter:
    def __init__(self, printer_name=None):
        self.printer_name = printer_name or self._find_slp_printer()
        if not self.printer_name:
            raise Exception("Smart Label Printer 650 not found")

        self.img = Image.open(resource_path("newGUI\\Property of BLANK.png"))

        self.width = 331
        self.height = 602

    def generate_label(self, data):
        self._add_qr_to_label(data)
        self._add_label_text(data)
        self.img = self.img.rotate(90, expand=True)
        #self.img.show()
        self.img.save("label.pdf", "PDF")
        #input("Press Enter to continue...")
        print(f"Printing to: {self.printer_name}")
        self._print_label()

    def _print_label(self):
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(self.printer_name)

        hDC.StartDoc("Label")
        hDC.StartPage()

        # Convert PIL image to something Windows can print
        dib = ImageWin.Dib(self.img)

        # Get printer resolution
        printable_area = hDC.GetDeviceCaps(8), hDC.GetDeviceCaps(10)

        # Draw the image to fit EXACTLY one label
        dib.draw(hDC.GetHandleOutput(), (61, -25, 392, 577))

        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

    def _add_label_text(self, data):
        draw = ImageDraw.Draw(self.img)
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 50)
        draw.text((235,253), text=data, fill=(0, 0, 0), font=font)

    def _create_qr_code(self, data):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=5,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img = img.resize((120,120))

        return img

    def _add_qr_to_label(self, data):
        qr = self._create_qr_code(data)
        self.img.paste(qr, (240, 130))

    def _find_slp_printer(self):
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        for printer in printers:
            name = printer[2]
            if "Smart Label Printer 650" in name:
                return name
        return None
