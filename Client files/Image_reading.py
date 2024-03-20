from PIL import Image, ImageTk
import io
import os
################################## Image reading ######################################

# Define a function which opens an image file using Python Imaging Library
def get_img_data(f, maxsize=(1600, 1000), first=False):
    """Generate image data using PIL"""
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:                     
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)

def image_to_bytes(image_path):
    with Image.open(image_path) as image_file:
        #image_file = image_file.resize((500,500))
        image_bytes = io.BytesIO()
        image_file.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()
    return image_bytes
if __name__ == '__main__':
    BASE_DIR = os.path.dirname(__file__)                      # base directory for relative paths
    image_files_folder = os.path.join(BASE_DIR,'Image_files') # folder for the image files
    print('')
    print(image_files_folder) # folder for the image files)
    print('')
    print(os.path.join(image_files_folder,'whole_image.tif'))