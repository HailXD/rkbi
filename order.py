import numpy as np
from PIL import Image
from io import BytesIO
import base64
import sys


def _convert_to_rgb(img):
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        return bg
    elif img.mode == "L" or img.mode == "P":
        return img.convert("RGB")
    elif img.mode == "RGB":
        return img
    else:
        return img.convert("RGB")


def process_order_image(image_bytes_py):
    try:
        img_pil = Image.open(BytesIO(image_bytes_py))
        img_pil_rgb = _convert_to_rgb(img_pil)
        img_array = np.array(img_pil_rgb)

        lower_bound = np.array([75, 75, 0])
        upper_bound = np.array([255, 255, 140])

        height, _, _ = img_array.shape
        rows_to_delete = []

        for i in range(height):
            first_pixel = img_array[i, 0]
            last_pixel = img_array[i, -1]

            if (
                np.all(first_pixel >= lower_bound)
                and np.all(first_pixel <= upper_bound)
            ) or (
                np.all(last_pixel >= lower_bound) and np.all(last_pixel <= upper_bound)
            ):
                rows_to_delete.append(i)

        img_array = np.delete(img_array, rows_to_delete, axis=0)

        if img_array.shape[0] > 2660:
            row_to_duplicate = img_array[2660]

            current_height = img_array.shape[0]
            target_height = 2796

            rows_to_add = target_height - current_height

            if rows_to_add > 0:
                new_rows = np.array([row_to_duplicate] * rows_to_add)
                img_array = np.insert(img_array, 2661, new_rows, axis=0)

        if img_array.dtype != np.uint8:
            img_array = img_array.astype(np.uint8)

        final_img = Image.fromarray(img_array)
        buffered = BytesIO()
        final_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"Error in process_order_image: {e}")
        error_img = Image.new("RGB", (100, 100), color="red")
        buffered = BytesIO()
        error_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")


if __name__ == "__main__" and "pyodide" not in sys.modules:
    try:
        img = Image.open("order.png")
    except FileNotFoundError:
        print(
            "Error: order.png not found. Please make sure the image is in the same directory."
        )
        exit()

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    base64_string = process_order_image(img_bytes)

    img_data = base64.b64decode(base64_string)
    processed_img = Image.open(BytesIO(img_data))
    processed_img.show()
    processed_img.save("processed_order.png", format="PNG")
