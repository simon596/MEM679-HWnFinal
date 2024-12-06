# -*-coding:utf-8 -*-

"""
#-------------------------------
# Author: Simeng Wu
# Email: sw3493@drexel.edu
#-------------------------------
# Creation Date: Feb 28th, 2024, EST.
#-------------------------------
"""

import shutil
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import cv2
import torch
import os.path as osp
from model.unet_model import UNet
import numpy as np
import time
import threading

# 窗口主类
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# 需要添加视频预测的部分并且临时关闭
class MainWindow(QTabWidget):
    # 基本配置不动，然后只动第三个界面
    def __init__(self):
        # 初始化界面
        super().__init__()
        self.setWindowTitle('Contact mechanics model based on Unet. Email: sw3493@drexel.edu')
        # self.setStatusTip("contact: qq：1015920299")
        self.resize(1200, 800)
        self.setWindowIcon(QIcon("images/UI/Drexel_twitter.png"))
        # 图片读取进程
        self.output_size = 480
        self.img2predict = ""
        # # 初始化视频读取线程
        self.origin_shape = ()
        # 加载网络，图片单通道，分类为1。
        #  初始化视频检测相关的内容
        self.vid_source = 'demo.mp4' # 要进行视频检测的名称
        self.video_capture = cv2.VideoCapture(self.vid_source)
        self.stopEvent = threading.Event()
        self.webcam = True
        self.stopEvent.clear()

        net = UNet(n_channels=1, n_classes=1)
        # 将网络拷贝到deivce中
        net.to(device=device)
        # 加载模型参数
        net.load_state_dict(torch.load('best_model.pth', map_location=device))  # todo 模型位置
        # 测试模式
        net.eval()
        self.model = net
        self.initUI()

    '''
    ***界面初始化***
    '''

    def initUI(self):
        # 图片检测子界面
        font_title = QFont('楷体', 16)
        font_main = QFont('楷体', 14)
        # 图片识别界面, 两个按钮，上传图片和显示结果
        img_detection_widget = QWidget()
        img_detection_layout = QVBoxLayout()
        # img_detection_title = QLabel("contact area segmentation" + "email: sw3493@drexel.edu")
        img_detection_title = QLabel("Contact area segmentation")
        img_detection_title.setAlignment(Qt.AlignCenter)
        img_detection_title.setFont(font_title)
        mid_img_widget = QWidget()
        mid_img_layout = QHBoxLayout()
        self.left_img = QLabel()
        self.right_img = QLabel()
        self.left_img.setPixmap(QPixmap("images/UI/Philly.jpg"))
        self.right_img.setPixmap(QPixmap("images/UI/WinterPhilly.jpg"))
        self.left_img.setAlignment(Qt.AlignCenter)
        self.right_img.setAlignment(Qt.AlignCenter)
        mid_img_layout.addWidget(self.left_img)
        mid_img_layout.addStretch(0)
        mid_img_layout.addWidget(self.right_img)
        mid_img_widget.setLayout(mid_img_layout)
        up_img_button = QPushButton("upload image")
        det_img_button = QPushButton("start segmenting")
        up_img_button.clicked.connect(self.upload_img)
        det_img_button.clicked.connect(self.detect_img)
        up_img_button.setFont(font_main)
        det_img_button.setFont(font_main)
        up_img_button.setStyleSheet("QPushButton{color:white}"
                                    "QPushButton:hover{background-color: rgb(2,110,180);}"
                                    "QPushButton{background-color:rgb(48,124,208)}"
                                    "QPushButton{border:2px}"
                                    "QPushButton{border-radius:5px}"
                                    "QPushButton{padding:5px 5px}"
                                    "QPushButton{margin:5px 5px}")
        det_img_button.setStyleSheet("QPushButton{color:white}"
                                     "QPushButton:hover{background-color: rgb(2,110,180);}"
                                     "QPushButton{background-color:rgb(48,124,208)}"
                                     "QPushButton{border:2px}"
                                     "QPushButton{border-radius:5px}"
                                     "QPushButton{padding:5px 5px}"
                                     "QPushButton{margin:5px 5px}")
        img_detection_layout.addWidget(img_detection_title, alignment=Qt.AlignCenter)
        img_detection_layout.addWidget(mid_img_widget, alignment=Qt.AlignCenter)
        img_detection_layout.addWidget(up_img_button)
        img_detection_layout.addWidget(det_img_button)
        img_detection_widget.setLayout(img_detection_layout)

        # 添加视频检测的页面
        vid_detection_widget = QWidget()
        vid_detection_layout = QVBoxLayout()
        # vid_title = QLabel("video segment" + "email: sw3493@drexel.edu")
        vid_title = QLabel("video segment")
        vid_title.setFont(font_title)
        self.vid_img = QLabel()
        self.vid_img.setPixmap(QPixmap("images/UI/vanGogh.jpg"))
        vid_title.setAlignment(Qt.AlignCenter)
        self.vid_img.setAlignment(Qt.AlignCenter)
        self.webcam_detection_btn = QPushButton("webcam real-time moniter")
        self.mp4_detection_btn = QPushButton("video file selection")
        self.vid_stop_btn = QPushButton("stop segmenting")
        self.webcam_detection_btn.setFont(font_main)
        self.mp4_detection_btn.setFont(font_main)
        self.vid_stop_btn.setFont(font_main)
        self.webcam_detection_btn.setStyleSheet("QPushButton{color:white}"
                                                "QPushButton:hover{background-color: rgb(2,110,180);}"
                                                "QPushButton{background-color:rgb(48,124,208)}"
                                                "QPushButton{border:2px}"
                                                "QPushButton{border-radius:5px}"
                                                "QPushButton{padding:5px 5px}"
                                                "QPushButton{margin:5px 5px}")
        self.mp4_detection_btn.setStyleSheet("QPushButton{color:white}"
                                             "QPushButton:hover{background-color: rgb(2,110,180);}"
                                             "QPushButton{background-color:rgb(48,124,208)}"
                                             "QPushButton{border:2px}"
                                             "QPushButton{border-radius:5px}"
                                             "QPushButton{padding:5px 5px}"
                                             "QPushButton{margin:5px 5px}")
        self.vid_stop_btn.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton:hover{background-color: rgb(2,110,180);}"
                                        "QPushButton{background-color:rgb(48,124,208)}"
                                        "QPushButton{border:2px}"
                                        "QPushButton{border-radius:5px}"
                                        "QPushButton{padding:5px 5px}"
                                        "QPushButton{margin:5px 5px}")
        self.webcam_detection_btn.clicked.connect(self.open_cam)
        self.mp4_detection_btn.clicked.connect(self.open_mp4)
        self.vid_stop_btn.clicked.connect(self.close_vid)
        vid_detection_layout.addWidget(vid_title)
        vid_detection_layout.addWidget(self.vid_img)
        # todo 添加摄像头检测标签逻辑
        # self.vid_num_label = QLabel("当前检测结果：{}".format("等待检测"))
        # self.vid_num_label.setFont(font_main)
        # vid_detection_layout.addWidget(self.vid_num_label)
        # 直接展示的时候分成左边和右边进行展示比较方便一些
        vid_detection_layout.addWidget(self.webcam_detection_btn)
        vid_detection_layout.addWidget(self.mp4_detection_btn)
        vid_detection_layout.addWidget(self.vid_stop_btn)
        vid_detection_widget.setLayout(vid_detection_layout)

        # todo 关于界面
        about_widget = QWidget()
        about_layout = QVBoxLayout()
        about_title = QLabel(
            'Welcome to use contact segmentation software\n\n connect with Zheng lab by scanning QR code below')  # todo 修改欢迎词语
        about_title.setFont(QFont('楷体', 18))
        about_title.setAlignment(Qt.AlignCenter)
        about_img = QLabel()
        about_img.setPixmap(QPixmap('images/UI/zhenglab.png'))
        about_img.setAlignment(Qt.AlignCenter)

        # label4.setText("<a href='https://oi.wiki/wiki/学习率的调整'>如何调整学习率</a>")
        label_super = QLabel()  # todo 更换作者信息
        label_super.setText("<a href='https://wu-simeng.netlify.app/'>or visit author's personal page-->Simeng Wu</a>")
        label_super.setFont(QFont('楷体', 16))
        label_super.setOpenExternalLinks(True)
        # label_super.setOpenExternalLinks(True)
        label_super.setAlignment(Qt.AlignRight)
        about_layout.addWidget(about_title)
        about_layout.addStretch()
        about_layout.addWidget(about_img)
        about_layout.addStretch()
        about_layout.addWidget(label_super)
        about_widget.setLayout(about_layout)

        self.left_img.setAlignment(Qt.AlignCenter)
        self.addTab(img_detection_widget, 'image segment')
        self.addTab(vid_detection_widget, 'video segment')
        self.addTab(about_widget, 'contact us')
        self.setTabIcon(0, QIcon('images/UI/Drexel_twitter.png'))
        self.setTabIcon(1, QIcon('images/UI/Drexel_twitter.png'))
        self.setTabIcon(2, QIcon('images/UI/Drexel_twitter.png'))

    '''
    ***上传图片***
    '''

    def upload_img(self):
        # 选择录像文件进行读取
        fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.jpg *.png *.tif *.jpeg')
        if fileName:
            suffix = fileName.split(".")[-1]
            save_path = osp.join("images/tmp", "tmp_upload." + suffix)
            shutil.copy(fileName, save_path)
            # 应该调整一下图片的大小，然后统一放在一起
            im0 = cv2.imread(save_path)
            resize_scale = self.output_size / im0.shape[0]
            im0 = cv2.resize(im0, (0, 0), fx=resize_scale, fy=resize_scale)
            cv2.imwrite("images/tmp/upload_show_result.jpg", im0)
            # self.right_img.setPixmap(QPixmap("images/tmp/single_result.jpg"))
            self.img2predict = fileName
            self.origin_shape = (im0.shape[1], im0.shape[0])
            self.left_img.setPixmap(QPixmap("images/tmp/upload_show_result.jpg"))
            # todo 上传图片之后右侧的图片重置，
            self.right_img.setPixmap(QPixmap("images/UI/right.jpeg"))

    '''
    ***检测图片***
    '''

    def detect_img(self):
        # 视频在这个基础上加入for循环进来
        source = self.img2predict  # file/dir/URL/glob, 0 for webcam
        img = cv2.imread(source)
        # 转为灰度图
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, (512, 512))
        # 转为batch为1，通道为1，大小为512*512的数组
        img = img.reshape(1, 1, img.shape[0], img.shape[1])
        # 转为tensor
        img_tensor = torch.from_numpy(img)
        # 将tensor拷贝到device中，只用cpu就是拷贝到cpu中，用cuda就是拷贝到cuda中。
        img_tensor = img_tensor.to(device=device, dtype=torch.float32)
        # 预测
        pred = self.model(img_tensor)
        # 提取结果
        pred = np.array(pred.data.cpu()[0])[0]
        # 处理结果
        pred[pred >= 0.5] = 255
        pred[pred < 0.5] = 0
        # 保存图片
        im0 = cv2.resize(pred, self.origin_shape)
        cv2.imwrite("images/tmp/single_result.jpg", im0)
        # 目前的情况来看，应该只是ubuntu下会出问题，但是在windows下是完整的，所以继续
        self.right_img.setPixmap(QPixmap("images/tmp/single_result.jpg"))

        # 界面关闭

    def closeEvent(self, event):
        reply = QMessageBox.question(self,
                                     'quit',
                                     "Are you sure?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            event.accept()
        else:
            event.ignore()

    # 添加摄像头实时检测的功能，界面和一个可以使用的for循环界面
    def open_cam(self):
        self.webcam_detection_btn.setEnabled(True)
        self.mp4_detection_btn.setEnabled(False)
        self.vid_stop_btn.setEnabled(True)
        self.vid_source = 0
        self.video_capture = cv2.VideoCapture(self.vid_source)
        self.webcam = True
        th = threading.Thread(target=self.detect_vid)
        th.start()

    # 视频文件检测
    def open_mp4(self):
        fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.mp4 *.avi')
        if fileName:
            self.webcam_detection_btn.setEnabled(False)
            self.mp4_detection_btn.setEnabled(False)
            self.vid_stop_btn.setEnabled(True)
            self.vid_source = fileName # 这个里面给定的需要进行检测的视频源
            self.video_capture = cv2.VideoCapture(self.vid_source)
            self.webcam = False
            th = threading.Thread(target=self.detect_vid)
            th.start()

    # 视频检测主函数
    def detect_vid(self):
        # model = self.model
        # 加载模型 不断从源头读取数据
        while True:
            ret, frame = self.video_capture.read()  # 读取摄像头
            if not ret:
                self.stopEvent.set()
                # break  # 如果读取失败（例如，已经到达视频的结尾），则退出循环
            else:
                # opencv的图像是BGR格式的，而我们需要是的RGB格式的，因此需要进行一个转换。
                # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 将图像转化为rgb颜色通道
                ############### todo 加载送入模型进行检测的逻辑， 以frame变量的形式给出
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                img = cv2.resize(img, (512, 512))
                # 转为batch为1，通道为1，大小为512*512的数组
                img = img.reshape(1, 1, img.shape[0], img.shape[1])
                # 转为tensor
                img_tensor = torch.from_numpy(img)
                # 将tensor拷贝到device中，只用cpu就是拷贝到cpu中，用cuda就是拷贝到cuda中。
                img_tensor = img_tensor.to(device=device, dtype=torch.float32)
                # 预测
                pred = self.model(img_tensor)
                # 提取结果
                pred = np.array(pred.data.cpu()[0])[0]
                # 处理结果
                pred[pred >= 0.5] = 255
                pred[pred < 0.5] = 0
                # 保存图片
                # im0 = cv2.resize(pred, self.origin_shape)

                # frame = frame
                frame_height = frame.shape[0]
                frame_width = frame.shape[1]
                frame_scale = self.output_size / frame_height
                frame_resize = cv2.resize(pred, (int(frame_width * frame_scale), int(frame_height * frame_scale)))
                src_frame = cv2.resize(frame, (int(frame_width * frame_scale), int(frame_height * frame_scale)))
                # src_frame = cv2.cvtColor(src_frame, cv2.COLOR_BGR2RGB)
                # 合成完毕之后，在颜色通道上进行转化
                frame_resize_RGB = cv2.cvtColor(frame_resize, cv2.COLOR_GRAY2RGB)
                hstack_result = np.hstack((src_frame, frame_resize_RGB))
                cv2.imwrite("images/tmp/tmp.jpg", hstack_result)
                # 展示图片的时候，应该将frame的图片和原始图片进行合并，合并只是
                self.vid_img.setPixmap(QPixmap("images/tmp/tmp.jpg"))
            if cv2.waitKey(25) & self.stopEvent.is_set() == True:
                self.stopEvent.clear()
                self.vid_img.clear()
                self.vid_stop_btn.setEnabled(False)
                self.webcam_detection_btn.setEnabled(True)
                self.mp4_detection_btn.setEnabled(True)
                self.reset_vid()
                break
        #
        #     if cv2.waitKey(25) & self.stopEvent.is_set() == True:
        #         self.stopEvent.clear()
        #         self.webcam_detection_btn.setEnabled(True)
        #         self.mp4_detection_btn.setEnabled(True)
        #         if self.dataset.cap is not None:
        #             self.dataset.cap.release()
        #             print("摄像头已释放")
        #         self.reset_vid()
        #         break

    # 摄像头重置
    def reset_vid(self):
        self.webcam_detection_btn.setEnabled(True)
        self.mp4_detection_btn.setEnabled(True)
        self.vid_img.setPixmap(QPixmap("images/UI/up.jpeg"))
        # self.vid_source = self.init_vid_id
        self.webcam = True
        self.video_capture.release()
        cv2.destroyAllWindows()
        # self.vid_num_label.setText("当前检测结果：{}".format("等待检测"))

    # 视频线程关闭
    def close_vid(self):
        self.stopEvent.set()
        self.reset_vid()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
