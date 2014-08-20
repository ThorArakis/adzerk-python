#!/Users/chrisst/.virtualenvs/redditmade/bin/python

from PIL import Image,  ImageFont, ImageDraw 


#progress bar rectangle
progressHeight = 28
progressWidth = 310
progressXOffset = 22
progressYOffset = 152

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

# print img.getpixel((progressXOffset, progressYOffset))
# img2 = Image.new('RGBA', (350,50), color=img.getpixel((progressXOffset, progressYOffset)))
#img2.show()

def build_3x1_ad(percent, goal):
    img = Image.open("image_templates/ad_small.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/Library/Fonts/Comic Sans MS.ttf", 24)
    fulltext = "%d%% funded of $%d goal" % (percent*100, goal)
    
    draw.text((22, 110),fulltext,(0,0,0),font=font)
    draw.rectangle([(progressXOffset, progressYOffset), ((progressXOffset+progressWidth), progressYOffset+progressHeight)], fill='white')
    draw.rectangle([(progressXOffset, progressYOffset), (progressXOffset+(progressWidth*percent), 
        progressYOffset+progressHeight)], fill=(176,222,88))

    img.show()

def build_rectangle_ad(percent, goal):
    print "not done yet"
    return

#img = add_corners(img, 10)

    
#img.save('foo-out.jpg')

