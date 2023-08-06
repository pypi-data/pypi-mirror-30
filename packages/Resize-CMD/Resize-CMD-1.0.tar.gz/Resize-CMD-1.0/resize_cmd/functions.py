from PIL import Image

img_exts = ['png', 'jpg', 'webp', 'gif']

def get_ext(filename):
    return filename.split(".")[-1]

def resize(filename, output, new_width=None, new_height=None):
    ext = get_ext(filename)
    if not ext in img_exts:
        return False
    try:
        img = Image.open(filename)
    except FileNotFoundError:
        return False

    width, height = img.size

    if new_width:
        width = new_width
    if new_height:
        height = new_height

    extension = get_ext(filename)

    img = img.resize((width, height))
    img.save(output, extension.upper())
    return True

def get_width(filename):
    ext = get_ext(filename)
    if not ext in img_exts:
        return None
    try:
        img = Image.open(filename)
    except FileNotFoundError:
        return None
    
    return img.size