
from __future__ import annotations
import sys
from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image  
except ImportError as exc:  
    sys.exit("Pillow is required. Install with: pip install pillow")





def crop_rows(src: str | Path, dest: str | Path, row_start: int, row_end: int) -> None:
    src_path = Path(src)
    dest_path = Path(dest)

    if not src_path.is_file():
        print(f"[WARN] {src_path} not found — skipping.")
        return

    with Image.open(src_path) as img:
        width, height = img.size
        if row_start < 0 or row_end >= height or row_start > row_end:
            raise ValueError(
                f"Invalid row range {row_start}-{row_end} for {src_path} of height {height}."
            )
        
        box = (0, row_start, width, row_end + 1)
        cropped = img.crop(box)
        cropped.save(dest_path)
        print(f"[OK] {dest_path.name} created (rows {row_start}-{row_end}).")






CropTask = Tuple[str, str, int, int]

TASKS: List[CropTask] = [
    ("IMG_2686.png", "Snippet_Opening_Partial.png", 1569, 1758),
    ("IMG_2685.png", "Snippet_Closing_Partial.png", 1569, 1758),
    ("IMG_2683.png", "Snippet_Opening.png", 1569, 1681),
    ("IMG_2684.png", "Snippet_Closing.png", 1569, 1758),
    ("IMG_2683.png", "Snippet_Account.png", 1946, 2077),
]






def main() -> None:  
    for src, dest, start_row, end_row in TASKS:
        crop_rows(src, dest, start_row, end_row)


if __name__ == "__main__":
    main()
