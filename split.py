import os
import shutil
import random
from sklearn.model_selection import train_test_split

def split_dataset(data_path, train_ratio=0.8, val_ratio=0.2):
    """
    自动切分数据集为train和val
    """
    # 路径设置
    images_dir = os.path.join(data_path, 'images')
    labels_dir = os.path.join(data_path, 'labels')
    
    # 获取所有图像文件（不包含扩展名）
    image_files = [f.split('.')[0] for f in os.listdir(images_dir) 
                  if f.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    
    # 随机打乱
    random.shuffle(image_files)
    
    # 计算切分点
    train_count = int(len(image_files) * train_ratio)
    
    # 切分
    train_files = image_files[:train_count]
    val_files = image_files[train_count:]
    
    print(f"总样本数: {len(image_files)}")
    print(f"训练集: {len(train_files)}")
    print(f"验证集: {len(val_files)}")
    
    # 创建子目录
    for split in ['train', 'val']:
        os.makedirs(os.path.join(images_dir, split), exist_ok=True)
        os.makedirs(os.path.join(labels_dir, split), exist_ok=True)
    
    # 移动文件到对应目录
    for file in train_files:
        # 移动图像文件
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            src_img = os.path.join(images_dir, file + ext)
            if os.path.exists(src_img):
                shutil.move(src_img, os.path.join(images_dir, 'train', file + ext))
                break
        
        # 移动标签文件
        src_label = os.path.join(labels_dir, file + '.txt')
        if os.path.exists(src_label):
            shutil.move(src_label, os.path.join(labels_dir, 'train', file + '.txt'))
    
    for file in val_files:
        # 移动图像文件
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            src_img = os.path.join(images_dir, file + ext)
            if os.path.exists(src_img):
                shutil.move(src_img, os.path.join(images_dir, 'val', file + ext))
                break
        
        # 移动标签文件
        src_label = os.path.join(labels_dir, file + '.txt')
        if os.path.exists(src_label):
            shutil.move(src_label, os.path.join(labels_dir, 'val', file + '.txt'))

# 使用示例
split_dataset('.', train_ratio=0.8, val_ratio=0.2)
