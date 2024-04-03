import os

def generate_path(data_path: str) -> str:
    if not os.path.exists(data_path):
        # Nếu không tồn tại, tạo các thư mục cha
        os.makedirs(data_path)

