import qrcode
import os
from os import path

class Utility:
    @classmethod
    def getQRCodeImageFilePath(self, one_address):
        if path.exists(f'qrcodes/{one_address}.png'):
            return f'qrcodes/{one_address}.png'
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(one_address)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        if not path.exists('qrcodes'):
            os.mkdir('qrcodes')
        with open(f'qrcodes/{one_address}.png', 'wb') as f:
            img.save(f)
        return f'qrcodes/{one_address}.png'
    
    @classmethod
    def is_valid_amount(self, value):
        try:
            float(value)
            if float(value) <= 0.00000000:
                return False
            return True
        except:
            return False
