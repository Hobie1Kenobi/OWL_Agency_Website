from PIL import Image
import os

def generate_favicon():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the website root
    website_root = os.path.dirname(script_dir)
    
    # Create a new image with a blue background
    img = Image.new('RGB', (32, 32), color=(71, 178, 228))  # #47b2e4
    
    # Create a drawing object
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Draw owl eyes (white circles)
    draw.ellipse([(8, 8), (16, 16)], fill='white')
    draw.ellipse([(16, 8), (24, 16)], fill='white')
    
    # Draw pupils (dark blue circles)
    draw.ellipse([(10, 10), (14, 14)], fill=(55, 81, 126))  # #37517e
    draw.ellipse([(18, 10), (22, 14)], fill=(55, 81, 126))
    
    # Draw beak (orange triangle)
    draw.polygon([(16, 20), (12, 24), (20, 24)], fill=(255, 153, 0))  # #ff9900
    
    # Save the image
    output_path = os.path.join(website_root, 'assets', 'img', 'favicon.png')
    img.save(output_path, 'PNG')
    
    print(f"Favicon generated successfully at: {output_path}")

if __name__ == "__main__":
    generate_favicon() 