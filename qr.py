from PIL import Image
import qrcode

url = "http://amnhactechcf.ddns.net:3030/r/gxe-promo"

# Tạo QR
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
qr.add_data(url)
qr.make(fit=True)

img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

# Chèn logo vào giữa

img_qr.save("gxe_promo_qr_logo.png")
