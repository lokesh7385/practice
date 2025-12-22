import qrcode

url = input("enter your url: ").strip()

img = qrcode.make(url)

img.save("qr.png")

