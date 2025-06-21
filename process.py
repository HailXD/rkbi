import numpy as np
from PIL import Image
from io import BytesIO
import base64
import sys
from collections import Counter


def _get_most_common_pixels(img_array, num_colors=5, thumbnail_size=(50, 50)):
    img = Image.fromarray(img_array.astype(np.uint8))
    img.thumbnail(thumbnail_size)
    pixels = np.array(img).reshape(-1, 3)
    return Counter(map(tuple, pixels)).most_common(num_colors)


def _replace_color(img_array, old_color, new_color):
    if old_color is None:
        return img_array
    mask = np.all(img_array == old_color, axis=-1)
    img_array[mask] = new_color
    return img_array


def _clean_middle_rows(img_array):
    target_color = np.array([24, 25, 30])
    lower_bound = target_color - 5
    upper_bound = target_color + 5
    for i in range(img_array.shape[0] - 2):
        row1 = img_array[i]
        row2 = img_array[i + 1]
        row3 = img_array[i + 2]
        if np.all(row1 == target_color) and np.all(row3 == target_color):
            if np.all((row2 >= lower_bound) & (row2 <= upper_bound)):
                img_array[i + 1] = target_color
    return img_array


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


def _delete_rows_by_color(img_array, lower_bound, upper_bound):
    first_pixels = img_array[:, 0]
    last_pixels = img_array[:, -1]

    mask_first = np.all((first_pixels >= lower_bound) & (first_pixels <= upper_bound), axis=1)
    mask_last = np.all((last_pixels >= lower_bound) & (last_pixels <= upper_bound), axis=1)
    
    rows_to_delete_mask = mask_first & mask_last
    
    rows_to_keep_mask = ~rows_to_delete_mask
    
    return img_array[rows_to_keep_mask], np.where(rows_to_delete_mask)[0]


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
            end_row = min(overlay_start_row + rows_to_overlay, h_main)
            img_array[overlay_start_row:end_row, :] = snippet_account_array[:(end_row - overlay_start_row), :]

        insert_row = 1622
        if insert_row < img_array.shape[0]:
            img_array = np.concatenate((img_array[:insert_row, :], snippet_to_insert_array, img_array[insert_row:, :]), axis=0)
        else:
            img_array = np.concatenate((img_array, snippet_to_insert_array), axis=0)

        lower_bound = np.array([75, 75, 0])
        upper_bound = np.array([255, 255, 140])
        img_array, _ = _delete_rows_by_color(img_array, lower_bound, upper_bound)

        if img_array.shape[0] > 2660:
            row_to_duplicate = img_array[2660]
            current_height = img_array.shape[0]
            target_height = 2796
            rows_to_add = target_height - current_height
            if rows_to_add > 0:
                new_rows = np.tile(row_to_duplicate, (rows_to_add, 1, 1))
                img_array = np.insert(img_array, 2661, new_rows, axis=0)

        target_height = 2796
        while img_array.shape[0] > target_height:
            if img_array.shape[0] > 2693:
                img_array = np.delete(img_array, 2693, axis=0)
            else:
                break

        common_colors = _get_most_common_pixels(img_array)
        if common_colors:
            most_common_color = common_colors[0][0]
            if list(most_common_color) != [24, 25, 30]:
                img_array = _replace_color(img_array, most_common_color, [24, 25, 30])
        img_array = _clean_middle_rows(img_array)
        final_img = Image.fromarray(img_array.astype(np.uint8))
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
        img_array, _ = _delete_rows_by_color(img_array, lower_bound, upper_bound)

        if img_array.shape[0] > 2660:
            row_to_duplicate = img_array[2660]
            current_height = img_array.shape[0]
            target_height = 2796
            rows_to_add = target_height - current_height
            if rows_to_add > 0:
                new_rows = np.tile(row_to_duplicate, (rows_to_add, 1, 1))
                img_array = np.insert(img_array, 2661, new_rows, axis=0)
        
        target_height = 2796
        while img_array.shape[0] > target_height:
            if img_array.shape[0] > 2693:
                img_array = np.delete(img_array, 2693, axis=0)
            else:
                break

        common_colors = _get_most_common_pixels(img_array)
        if common_colors:
            most_common_color = common_colors[0][0]
            if list(most_common_color) != [24, 25, 30]:
                img_array = _replace_color(img_array, most_common_color, [24, 25, 30])
        img_array = _clean_middle_rows(img_array)
        final_img = Image.fromarray(img_array.astype(np.uint8))
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
        original_width = img_array.shape[1]

        lower_bound = np.array([75, 75, 0])
        upper_bound = np.array([255, 255, 150])
        
        img_array_current, deleted_rows_indices = _delete_rows_by_color(img_array, lower_bound, upper_bound)
        
        highest_yellow_row = -1
        if deleted_rows_indices.size > 0:
            highest_yellow_row = np.min(deleted_rows_indices)

        if img_array_current.shape[0] == 0:
            return base64.b64encode(
                Image.new(
                    "RGB",
                    (original_width if original_width > 0 else 100, 100),
                    color=(0, 0, 0),
                ).tobytes()
            ).decode("utf-8")
        if highest_yellow_row != -1:
            actual_insert_row = min(highest_yellow_row, img_array_current.shape[0])
            img_array_current = np.insert(
                img_array_current, actual_insert_row, [171, 170, 175], axis=0
            )

        if img_array_current.shape[0] > 2400:
            row_to_duplicate = img_array_current[2400]
            current_height = img_array_current.shape[0]
            target_height = 2796
            rows_to_add = target_height - current_height
            if rows_to_add > 0:
                new_rows = np.tile(row_to_duplicate, (rows_to_add, 1, 1))
                img_array_current = np.insert(
                    img_array_current, 2401, new_rows, axis=0
                )

        target_height = 2796
        while img_array_current.shape[0] > target_height:
            if img_array_current.shape[0] > 2693:
                img_array_current = np.delete(img_array_current, 2693, axis=0)
            else:
                break

        common_colors = _get_most_common_pixels(img_array_current)
        if common_colors:
            most_common_color = common_colors[0][0]
            if list(most_common_color) != [24, 25, 30]:
                img_array_current = _replace_color(
                    img_array_current, most_common_color, [24, 25, 30]
                )
        img_array_current = _clean_middle_rows(img_array_current)
        final_img = Image.fromarray(img_array_current.astype(np.uint8))
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
    # try:
    #     img = Image.open("order.png")
    # except FileNotFoundError:
    #     print("Error: order.png not found for testing.")
    #     sys.exit()

    # buffered = BytesIO()
    # img.save(buffered, format="PNG")
    # img_bytes = buffered.getvalue()
    
    # base64_string = order_o(img_bytes)
    # img_data = base64.b64decode(base64_string)
    # processed_img = Image.open(BytesIO(img_data))
    # processed_img.show()
    # processed_img.save("processed_order_test.png", format="PNG")