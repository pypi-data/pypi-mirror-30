from PIL import ImageGrab
im = ImageGrab.grabclipboard()
im.save('somefile.png','PNG')
print('haha')

