import re
from PIL import Image
import pytesseract

class ImgProccessor:
    
    def try_extract_data(img_str):
        result = re.search(r"(\d{6})\s+\d{2}\s+\d{2}",img_str)
        if result:
            return result.group(0)
        result = re.search(r"\d{3}[А-Я]\s+\d{2}\s+\d{3}",img_str)
        if result:
            return result.group(0)
        raise Exception('failed to parse!')

