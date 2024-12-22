from PIL import Image
import colorsys
import numpy as np

def is_extreme_pixel(r, g, b, threshold=10):
    """Check if pixel is very close to pure black or pure white."""
    return (all(c <= threshold for c in (r, g, b)) or
            all(c >= 255-threshold for c in (r, g, b)))

def get_average_color(image_path):
    """Get the average color and its perceived importance."""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        img_array = np.array(img)
        pixels = img_array.reshape(-1, 3)

        # Calculate RGB variance
        rgb_variance = np.var(pixels, axis=0).mean()
        initial_s = np.mean([colorsys.rgb_to_hsv(r/255, g/255, b/255)[1] for r, g, b in pixels])
        is_grayscale = initial_s < 0.1 or rgb_variance < 10

        if not is_grayscale:
            # Filter out near-black and near-white pixels
            valid_pixels = [pixel for pixel in pixels
                          if not is_extreme_pixel(pixel[0], pixel[1], pixel[2])]

            if valid_pixels:
                pixels = np.array(valid_pixels)

        # Calculate average RGB from remaining pixels
        r, g, b = np.mean(pixels, axis=0)

        # Convert to HSV
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        # Calculate color weight
        color_weight = s * (v + 0.1)

        return (h, s, v, color_weight, is_grayscale)
    except Exception as e:
        print(f"Warning: Failed to process image {image_path}. Error: {e}")
        return (0, 0, 0, 0, True)

def get_sort_key(color_tuple):
    """Generate sorting key that prioritizes visually significant colors."""
    h, s, v, is_grayscale = color_tuple

    if is_grayscale:
        return (0, v)

    return (1, h, s, v)  # Sort colors by hue, then saturation, then value
