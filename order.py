import numpy as np
from PIL import Image


def process_image(img):
    img_array = np.array(img)

    lower_bound = np.array([75, 75, 0])
    upper_bound = np.array([255, 255, 140])

    height, _, _ = img_array.shape
    rows_to_delete = []

    for i in range(height):
        first_pixel = img_array[i, 0]
        last_pixel = img_array[i, -1]

        if (
            np.all(first_pixel >= lower_bound) and np.all(first_pixel <= upper_bound)
        ) or (np.all(last_pixel >= lower_bound) and np.all(last_pixel <= upper_bound)):
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
    else:
        print(
            f"Warning: Image height after deletions is {img_array.shape[0]}, which is not greater than 2660. Cannot perform duplication."
        )

    result_img = Image.fromarray(img_array)
    return result_img


try:
    img = Image.open("order.png")
except FileNotFoundError:
    print(
        "Error: order.png not found. Please make sure the image is in the same directory."
    )
    exit()

processed_img = process_image(img)

processed_img.show()
processed_img.save("processed_order.png", format="PNG")
