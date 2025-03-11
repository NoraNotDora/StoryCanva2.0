import os
from datetime import datetime

UPLOAD_FOLDER =  './uploads'

def upload_to_bucket(image_stream, blob_name):
    """将文件存储到本地uploads目录"""
    # 确保上传目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # 生成唯一的文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{blob_name}.png"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # 保存文件
    with open(file_path, 'wb') as f:
        f.write(image_stream)
    
    # 返回本地文件路径
    print(f"Uploaded {filename} to {UPLOAD_FOLDER}.")
    return file_path

def test_upload(file: str):
    image_stream = open(file, 'rb').read()
    filename = os.path.basename(file)
    url = upload_to_bucket(image_stream, filename)
    return url

if __name__ == '__main__':
    # upload all images in ./assets
    import os
    gallery = []
    for file in os.listdir('./assets'):
        url = test_upload(f'./assets/{file}')
        gallery.append({
            "imgSrc": url,
        })
    import json
    with open('gallery.json', 'w') as f:
        json.dump(gallery, f, indent=4)