'''
Generate a PDF of a pixel plane YAML file.

'''
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
import yaml
from larpixgeometry.pixelplane import PixelPlane
import  numpy as np

with open('sensor_plane_28_full.yaml', 'r') as f:
    pixelplane = PixelPlane.fromDict(yaml.load(f))

colors = np.array([[228, 26, 28], [55, 126, 184], [77, 175, 74], [152,
    78, 163], [255, 127, 0]])/256.0
colors = np.tile(colors, (10,1))



c = canvas.Canvas('sensor_28chip.pdf', pagesize=(12*inch, 12*inch))
c.setFont('Helvetica', 20)
c.drawString(4*inch, 11*inch, 'Sensor board with 28 chips')
c.drawString(4*inch, 10.6*inch, '(view from chip side)')
c.setFont('Courier', 7)
colorkey = []
for pixel in pixelplane.pixels.values():
    c.circle(pixel.x*7-300, 15*inch-pixel.y*7, 0.4)
    c.drawCentredString(pixel.x*7-300, 15*inch-pixel.y*7, str(pixel.pixelid))
for chip, color in zip(pixelplane.chips.values(), colors):
    c.setFont('Courier-Bold', 11)
    c.setFillColorRGB(*color, alpha=1)
    colorkey.append(['Chip %d' % chip.chipid, color])
    x_sum = 0
    y_sum = 0
    count = 0
    for channel, pixel in enumerate(chip.channel_connections):
        if pixel != pixelplane.unconnected_pixel:
            c.drawCentredString(pixel.x*7-300, 15*inch-pixel.y*7-7,
                    str(channel))
            x_sum += pixel.x*7-300
            y_sum += 15*inch-pixel.y*7 - 5
            count += 1
    x_avg = x_sum/float(count)
    y_avg = y_sum/float(count)
    font = ('Helvetica', 56)
    c.setFont(*font)
    c.setFillColorRGB(*color, alpha=0.45)
    width = c.stringWidth(str(chip.chipid), *font)
    c.drawCentredString(x_avg, y_avg-16, str(chip.chipid))
# for i, (string, color) in enumerate(colorkey):
    # c.setFillColorRGB(*color)
    # c.drawString(80, 11*inch-25*i, string)
c.showPage()
c.save()
