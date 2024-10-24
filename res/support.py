# encoding=utf-8
from PIL import Image


def show_donate(imgpath="res/QRcode.jpg"):
    try:
        img = Image.open(imgpath)
        img2 = Image.open("res/QRcode_2.png")
        print("感觉还不错? 来请作者喝杯coffee~")
        img.show()
        img2.show()
        print("不希望显示赞赏码? 删除res文件夹的QRcode文件就好啦~")
    except FileNotFoundError:
        return
