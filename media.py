def ratio(height, width):
    ratio = float(width) / float(height)
    return ratio

def sanitze(value):
    # Make sure people don't crash the server with huge image sizes.
    value = int(value)
    if value > 400:
        value = 400
    return value

def measurements(image, width=None, height=None):
    # Get the current image size.
    (current_width, current_height) = image.size
    ratio = float(current_width) / float(current_height)

    #If nothing is passed in, set the width.
    if not width and not height:
        width = 150

    # If only the width passed in, calculate the new height.
    if width:
        width = sanitze(width)
        height = int(width / ratio)

    # If only the height passed in, calculate the new width.
    elif height:
        height = sanitze(height)
        width = int(height * ratio)
    return (width, height)
