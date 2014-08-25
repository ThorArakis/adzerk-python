#!/Users/chrisst/.virtualenvs/redditmade/bin/python

from PIL import Image,  ImageFont, ImageDraw 


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
    im.show()
    return im

font_location = "/Library/Fonts/OpenSans-Bold.ttf"


# print img.getpixel((progressXOffset, progressYOffset))
# img2 = Image.new('RGBA', (350,50), color=img.getpixel((progressXOffset, progressYOffset)))
#img2.show()

def build_3x1_ad(image_name=None, shirt_image=None):
    background = Image.open("image_templates/ad_small.png")
    draw = ImageDraw.Draw(background)

    mask = Image.open('image_templates/placeholder_shirt_mask.png')
    shirt = Image.open(shirt_image)
    shirt.thumbnail((250,250))
    mask.thumbnail((250,250))

    background.paste(shirt, mask=mask, box=(165,-27))

    image_path = 'compiled_templates/' + image_name
    background.save(image_path)
    #background.show()

    return image_path

def build_rectangle_ad(image_name=None, subreddit=None, shirt_image=None):
    background = Image.open("image_templates/med_rect.png").convert('RGB')
    draw = ImageDraw.Draw(background, 'RGBA')
    image_path = 'compiled_templates/' + image_name 

    #Image mask must be the correct mode! aka NOT RGB
    mask = Image.open('image_templates/placeholder_shirt_mask.png')
    shirt = Image.open(shirt_image)
    #resize with thumbnail
    shirt.thumbnail((350,250))
    mask.thumbnail((350,250))

    shirt_offset_x = (background.size[0]-shirt.size[0]) / 2
    background.paste(shirt, mask=mask, box=(shirt_offset_x,35))
    
    font = ImageFont.truetype(font_location, 14)
    text_offset_x = (background.size[0]-font.getsize('/r/'+subreddit)[0]) / 2
    draw.text((text_offset_x, 38), '/r/'+subreddit, (0,0,0), font=font)

    #Add a white transparent bar
    draw.rectangle([(0,200), (300,250)], fill=(255, 255, 255, 150))
    
    #background.show()
    background.save(image_path)

    return image_path

def update_progress(image_name=None, text_offset=(0,0), text="", bar_offset=(0,0), bar_size=(0,0), percent=0, goal=0):
    img = Image.open('compiled_templates/' + image_name)
    write_progress_text(img, text_offset, text)
    draw_progess_bar(img, bar_offset, bar_size, percent)

    img.save('final_images/' + image_name)
    return 'final_images/' + image_name

def write_progress_text(image, offset, text):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_location, 12)
    draw.text(offset, text, (0,0,0), font=font)

    return image

def draw_progess_bar(image, offset, size, percent):
    #TODO if image is missing, make it.
    
    draw = ImageDraw.Draw(image)

    draw.rectangle([(offset[0]-1, offset[1]-1), ((offset[0]+size[0])+1, offset[1]+size[1]+1)],
                   fill='white', outline=(177,177,177))
    draw.rectangle([(offset[0], offset[1]), (offset[0]+(size[0]*percent), 
        offset[1]+size[1])], fill=(176,222,88))

    #image.show()
    return image

#img = add_corners(img, 10)


