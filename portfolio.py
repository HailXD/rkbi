import numpy as np
from PIL import Image, ImageOps
from io import BytesIO
import base64
import requests
import sys

def _convert_to_rgb(img):
    if img.mode == 'RGBA':
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        return bg
    elif img.mode == 'L' or img.mode == 'P':
        return img.convert('RGB')
    elif img.mode == 'RGB':
        return img
    else:
        return img.convert('RGB')

def process_portfolio_image(image_bytes_py):
    try:
        img_pil = Image.open(BytesIO(image_bytes_py))
        img_pil_rgb = _convert_to_rgb(img_pil)
        img_array = np.array(img_pil_rgb)

        lower_bound = np.array([75, 75, 0])
        upper_bound = np.array([255, 255, 140])

        original_height, original_width, _ = img_array.shape
        rows_to_delete = []

        for i in range(original_height):
            first_pixel = img_array[i, 0]
            last_pixel = img_array[i, -1]
            if (np.all(first_pixel >= lower_bound) and np.all(first_pixel <= upper_bound)) or \
               (np.all(last_pixel >= lower_bound) and np.all(last_pixel <= upper_bound)):
                rows_to_delete.append(i)
        
        img_array_current = np.delete(img_array, rows_to_delete, axis=0)
        rows_deleted_count = len(rows_to_delete)

        if img_array_current.shape[0] == 0:
            img_array_current = np.zeros((100, original_width if original_width > 0 else 100, 3), dtype=np.uint8)

        current_height_after_first_delete = img_array_current.shape[0]
        start_row_ref = int(0.7 * current_height_after_first_delete)
        
        consecutive_row_color = np.array([128, 128, 128], dtype=np.uint8)
        if current_height_after_first_delete > 0:
            search_start_idx = min(start_row_ref, current_height_after_first_delete - 2)
            if search_start_idx < 0: search_start_idx = 0

            if current_height_after_first_delete > 1:
                for i in range(search_start_idx, current_height_after_first_delete - 1):
                    if np.array_equal(img_array_current[i, 0], img_array_current[i + 1, 0]):
                        consecutive_row_color = img_array_current[i, 0]
                        break
                else:
                    consecutive_row_color = img_array_current[min(start_row_ref, current_height_after_first_delete - 1), 0]
            else:
                consecutive_row_color = img_array_current[0,0]

        insert_row_607_target = 607
        actual_insert_row_607 = min(insert_row_607_target, img_array_current.shape[0])

        img_array_current = np.insert(img_array_current, actual_insert_row_607, [171, 170, 175], axis=0)
        
        indices_to_delete_slice = []
        current_height_before_slice_delete = img_array_current.shape[0]
        for i_offset in range(1, 11):
            idx = start_row_ref + i_offset
            if 0 <= idx < current_height_before_slice_delete:
                indices_to_delete_slice.append(idx)
        
        if indices_to_delete_slice:
            img_array_current = np.delete(img_array_current, indices_to_delete_slice, axis=0)

        for i in range(rows_deleted_count + 9):
            current_height_before_reinsert = img_array_current.shape[0]
            insert_idx_reinsert = min(start_row_ref + i, current_height_before_reinsert)
            img_array_current = np.insert(img_array_current, insert_idx_reinsert, consecutive_row_color, axis=0)

        if img_array_current.dtype != np.uint8:
            img_array_current = np.clip(img_array_current, 0, 255).astype(np.uint8)
        
        final_img = Image.fromarray(img_array_current)
        buffered = BytesIO()
        final_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error in process_portfolio_image: {e}")
        error_img = Image.new('RGB', (100,100), color='red')
        buffered = BytesIO()
        error_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

if __name__ == '__main__' and 'pyodide' not in sys.modules:
    def load_image_from_url(url):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img

    image_url = "https://media.discordapp.net/attachments/1352311755682091111/1372248573240021022/IMG_1489.png?ex=68261593&is=6824c413&hm=59996942ff469693536152dc6e51eb2a6d24778027d63ec252d2bffaa11444d7&="
    img = load_image_from_url(image_url)
    
    # Convert PIL image to bytes
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    base64_string = process_portfolio_image(img_bytes)
    
    # Decode base64 and save as image
    img_data = base64.b64decode(base64_string)
    processed_img = Image.open(BytesIO(img_data))
    processed_img.show()
    processed_img.save("processed_portfolio.png", format="PNG")
