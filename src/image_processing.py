from PIL import Image, ImageStat

def get_average_color(image_path):
    """Get the average color of the image."""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        stat = ImageStat.Stat(img)
        r,g,b = stat.mean
        return r,g,b
    except Exception as e:
        print(f"Warning: Failed to open or process the image {image_path}. Error: {e}")
        return 0, 0, 0  # Return black if there is an error processing the image
