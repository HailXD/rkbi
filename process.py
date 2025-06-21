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


def process_image(image_bytes_py, snippet_to_insert_path):
    try:
        img_pil = Image.open(BytesIO(image_bytes_py))
        img_pil_rgb = _convert_to_rgb(img_pil)
        img_array = np.array(img_pil_rgb)
        h_main, w_main, _ = img_array.shape

        snippet_account_img = Image.open("Snippet_Account.png")
        snippet_account_img_rgb = _convert_to_rgb(snippet_account_img)
        h_account, w_account, _ = np.array(snippet_account_img_rgb).shape
        if w_account != w_main:
            snippet_account_img_rgb = snippet_account_img_rgb.resize((w_main, h_account))
        snippet_account_array = np.array(snippet_account_img_rgb)

        snippet_to_insert_img = Image.open(snippet_to_insert_path)
        snippet_to_insert_img_rgb = _convert_to_rgb(snippet_to_insert_img)
        h_insert, w_insert, _ = np.array(snippet_to_insert_img_rgb).shape
        if w_insert != w_main:
            snippet_to_insert_img_rgb = snippet_to_insert_img_rgb.resize((w_main, h_insert))
        snippet_to_insert_array = np.array(snippet_to_insert_img_rgb)

        overlay_start_row = 1887
        if overlay_start_row < h_main:
            rows_to_overlay = snippet_account_array.shape[0]
            end_row = overlay_start_row + rows_to_overlay
            
            if end_row > h_main:
                rows_to_overlay = h_main - overlay_start_row
                end_row = h_main
            
            img_array[overlay_start_row:end_row, :] = snippet_account_array[:rows_to_overlay, :]

        insert_row = 1622
        if insert_row < img_array.shape[0]:
            part1 = img_array[:insert_row, :]
            part2 = img_array[insert_row:, :]
            img_array = np.concatenate((part1, snippet_to_insert_array, part2), axis=0)
        else:
            img_array = np.concatenate((img_array, snippet_to_insert_array), axis=0)

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
        print(f"Error in process_image: {e}")
        error_img = Image.new("RGB", (100, 100), color="red")
        buffered = BytesIO()
        error_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")


def order_o(image_bytes_py):
    return process_image(image_bytes_py, "Snippet_Opening.png")


def order_c(image_bytes_py):
    return process_image(image_bytes_py, "Snippet_Closing.png")


def order_op(image_bytes_py):
    return process_image(image_bytes_py, "Snippet_Opening_Partial.png")


def order_oc(image_bytes_py):
    return process_image(image_bytes_py, "Snippet_Closing_Partial.png")


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


def process_portfolio_image(image_bytes_py):
    try:
        img_pil = Image.open(BytesIO(image_bytes_py))
        img_pil_rgb = _convert_to_rgb(img_pil)
        img_array = np.array(img_pil_rgb)

        lower_bound = np.array([75, 75, 0])
        upper_bound = np.array([255, 255, 150])

        original_height, original_width, _ = img_array.shape
        rows_to_delete = []

        for i in range(original_height):
            first_pixel = img_array[i, 0]
            last_pixel = img_array[i, -1]
            if (
                np.all(first_pixel >= lower_bound)
                and np.all(first_pixel <= upper_bound)
            ) or (
                np.all(last_pixel >= lower_bound) and np.all(last_pixel <= upper_bound)
            ):
                rows_to_delete.append(i)

        highest_yellow_row = -1
        if rows_to_delete:
            highest_yellow_row = min(rows_to_delete)

        img_array_current = np.delete(img_array, rows_to_delete, axis=0)

        if img_array_current.shape[0] == 0:
            img_array_current = np.zeros(
                (100, original_width if original_width > 0 else 100, 3), dtype=np.uint8
            )

        if highest_yellow_row != -1:
            actual_insert_row = min(highest_yellow_row, img_array_current.shape[0])
            img_array_current = np.insert(
                img_array_current, actual_insert_row, [171, 170, 175], axis=0
            )

        if img_array_current.shape[0] > 2660:
            row_to_duplicate = img_array_current[2660]

            current_height = img_array_current.shape[0]
            target_height = 2796

            rows_to_add = target_height - current_height

            if rows_to_add > 0:
                new_rows = np.array([row_to_duplicate] * rows_to_add)
                img_array_current = np.insert(
                    img_array_current, 2661, new_rows, axis=0
                )

        if img_array_current.dtype != np.uint8:
            img_array_current = np.clip(img_array_current, 0, 255).astype(np.uint8)

        final_img = Image.fromarray(img_array_current)
        buffered = BytesIO()
        final_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"Error in process_portfolio_image: {e}")
        error_img = Image.new("RGB", (100, 100), color="red")
        buffered = BytesIO()
        error_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")


if __name__ == "__main__" and "pyodide" not in sys.modules:
    # This block is for local testing and will not run in Pyodide environment
    # Example: Test process_portfolio_image
    try:
        img = Image.open("portfolio.png")
    except FileNotFoundError:
        print("Error: portfolio.png not found for testing.")
        sys.exit()
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    base64_string = process_portfolio_image(img_bytes)

    img_data = base64.b64decode(base64_string)
    processed_img = Image.open(BytesIO(img_data))
    processed_img.show()
    processed_img.save("processed_portfolio_test.png", format="PNG")

    # Example: Test one of the order functions
    try:
        img = Image.open("order.png")
    except FileNotFoundError:
        print("Error: order.png not found for testing.")
        sys.exit()

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    
    base64_string = order_o(img_bytes)
    img_data = base64.b64decode(base64_string)
    processed_img = Image.open(BytesIO(img_data))
    processed_img.show()
    processed_img.save("processed_order_test.png", format="PNG")