from PIL import Image
import os

def add_sticker(image_path, sticker_path):
    image = Image.open(image_path)
    sticker = Image.open(sticker_path)
    
    # Stikerni rasimga joylash
    sticker = sticker.resize((100, 100))  # Stikerni hajmini o'zgartirish
    image.paste(sticker, (50, 50), sticker)
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, 'sticker_added_image.jpg')
    output_path = 'output/sticker_added_image.jpg'
    image.save(output_path)
    return output_path