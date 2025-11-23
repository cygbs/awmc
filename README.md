# awmc

**本项目仅供娱乐，请勿用作其他用途。此项目大部分代码由AI生成。**

自动化地检测群友发送的WM图片，并回复一条消息指责其是乌蒙吃。

项目基于YOLOv8，在您收集并标注好数据集之后，使用数据集切分工具将数据集分为训练集和验证集，然后执行以下代码可开始训练：

```sh
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=100 imgsz=320 batch=4 device=0 workers=1 amp=True
```

完成训练后，可使用awmc与OneBot框架对接，然后就可以验证效果了。建议数据集稍微大一些，以免将奇怪的东西认成乌蒙机器。
