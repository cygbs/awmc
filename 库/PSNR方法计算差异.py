# -*- coding: utf-8 -*-
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys


def 加载并统一尺寸(图片路径1, 图片路径2):
    """
    加载两张图片并自动统一为相同的尺寸（取最小宽高）
    """
    图片1 = cv2.imread(图片路径1)
    图片2 = cv2.imread(图片路径2)

    if 图片1 is None or 图片2 is None:
        raise ValueError("无法读取图片，请检查路径是否正确")

    # 取两张图的最小宽与高
    高度 = min(图片1.shape[0], 图片2.shape[0])
    宽度 = min(图片1.shape[1], 图片2.shape[1])

    # resize 成相同尺寸
    图片1缩放 = cv2.resize(图片1, (宽度, 高度))
    图片2缩放 = cv2.resize(图片2, (宽度, 高度))

    return 图片1缩放, 图片2缩放


def 计算峰值信噪比(图片1, 图片2):
    """
    使用 OpenCV 提供的 PSNR（峰值信噪比）函数计算相似度
    返回值越大，两张图越相似
    """
    psnr = cv2.PSNR(图片1, 图片2)
    return psnr


def 计算差异热力图(图片1, 图片2):
    """
    计算两张图片的差异图并生成归一化的热力图矩阵
    """
    # 转换为 RGB 供 matplotlib 显示
    图片1rgb = cv2.cvtColor(图片1, cv2.COLOR_BGR2RGB)
    图片2rgb = cv2.cvtColor(图片2, cv2.COLOR_BGR2RGB)

    # 计算逐像素绝对差
    差异 = cv2.absdiff(图片1rgb, 图片2rgb)

    # 转灰度方便显示热力图
    差异灰度 = cv2.cvtColor(差异, cv2.COLOR_RGB2GRAY)

    # 归一化到 0~1，避免全黑
    差异归一化 = 差异灰度.astype(np.float32)
    最大值 = 差异归一化.max()
    差异归一化 /= 最大值 if 最大值 > 0 else 1

    return 图片1rgb, 图片2rgb, 差异归一化


def 显示结果(图片1rgb, 图片2rgb, 差异图, 相似度):
    """
    使用 matplotlib 显示图片与差异热力图
    """
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.title("图片 1")
    plt.imshow(图片1rgb)
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.title("图片 2")
    plt.imshow(图片2rgb)
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.title(f"差异热力图\nPSNR: {相似度:.2f} dB")
    plt.imshow(差异图, cmap='hot')
    plt.colorbar()
    plt.axis("off")

    plt.tight_layout()
    plt.show()


def 主函数():
    """
    主函数：从命令行读取两个图片路径并比较相似度
    """
    if len(sys.argv) != 3:
        print("用法: python 脚本名.py 图片1路径 图片2路径")
        print("示例: python compare.py a.jpg b.jpg")
        sys.exit(1)

    图片路径1 = sys.argv[1]
    图片路径2 = sys.argv[2]

    # 加载并统一尺寸
    图片1, 图片2 = 加载并统一尺寸(图片路径1, 图片路径2)

    # 计算 PSNR 相似度
    峰值信噪比 = 计算峰值信噪比(图片1, 图片2)
    print("PSNR 相似度:", 峰值信噪比, "dB")

    # 计算差异图
    图片1rgb, 图片2rgb, 差异图 = 计算差异热力图(图片1, 图片2)

    # 显示比较结果
    显示结果(图片1rgb, 图片2rgb, 差异图, 峰值信噪比)


if __name__ == "__main__":
    主函数()
