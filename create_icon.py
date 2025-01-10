import requests
from PIL import Image
from io import BytesIO
import os

def download_and_convert_to_ico(url, output_path):
    # 下載圖片
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    
    # 確保圖片是正方形
    size = max(img.size)
    new_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    new_img.paste(img, ((size - img.size[0]) // 2, (size - img.size[1]) // 2))
    
    # 調整大小為標準icon尺寸
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img_list = []
    for size in icon_sizes:
        resized_img = new_img.resize(size, Image.Resampling.LANCZOS)
        img_list.append(resized_img)
    
    # 儲存為.ico
    img_list[0].save(
        output_path,
        format='ICO',
        sizes=icon_sizes,
        append_images=img_list[1:]
    )

# 下載並轉換圖片
url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRu6w1L1n_jpEO94b80gNhWHTvkpCtCHvui2Q&s"
output_path = "youtube.ico"
download_and_convert_to_ico(url, output_path)
print("Icon created successfully!")
