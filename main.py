from APDLData import APDLData
import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QDesktopWidget, QToolButton,QMessageBox
)
from PyQt5.QtGui import QFont, QIcon, QPixmap




from PyQt5.QtCore import QSize, Qt

def resource_path(relative_path):
    """返回资源文件的绝对路径，适配 PyInstaller 打包后的路径"""
    if hasattr(sys, '_MEIPASS'):  # PyInstaller打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
import os, sys
# 使用图标
icon_path = resource_path("icons/moment.png")

def show_error(text):
    msg = QMessageBox()
    msg.setWindowTitle("错误提示")
    msg.setIcon(QMessageBox.Critical)  # ❌ 错误图标
    msg.setText(text)
    msg.exec_()
    print(text)

def show_warning(text):
    msg = QMessageBox()
    msg.setWindowTitle("警告")
    msg.setIcon(QMessageBox.Warning)  # ⚠️ 警告图标
    msg.setText(text)
    msg.exec_()
    print(text)

def show_info(text):
    msg = QMessageBox()
    msg.setWindowTitle("提示")
    msg.setIcon(QMessageBox.Information)  # ❗ 信息图标
    msg.setText(text)
    msg.exec_()
    print(text)



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.data_parser = None  # 用于存储APDLData实例
        self.initUI()

    def center(self):
        screen_geometry = QDesktopWidget().screenGeometry()  # 获取屏幕尺寸
        window_geometry = self.frameGeometry()                # 获取窗口尺寸
        window_geometry.moveCenter(screen_geometry.center())  # 移动到屏幕中心
        self.move(window_geometry.topLeft())                  # 设置窗口位置

    def initUI(self):
        self.setWindowTitle("荷载组合")
        self.setGeometry(200, 200, 700, 500)
        self.center()

        main_layout = QVBoxLayout()

        # 第一行：数据文件选择
        file_layout = QHBoxLayout()
        self.data_path_label = QLabel("数据文件存放位置：")
        self.data_path_input = QLineEdit()
        self.data_path_input.setText(r"C:\Projects\APDLProjects\homework03\data.txt")
        self.data_path_button = QPushButton("浏览")

        self.data_load_button = QToolButton()
        self.data_load_button.setText("加载数据")
        icon_path = resource_path("icons/load_file.png")
        self.data_load_button.setIcon(QIcon(icon_path))
        self.data_load_button.setIconSize(QSize(48, 48))
        self.data_load_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.data_load_button.setStyleSheet("""
        QToolButton {
            min-width: 120px;
            min-height: 54px;
            text-align: center; /* 如果需要文字居中 */
        }

        """)

        self.data_path_button.clicked.connect(self.browse_file)
        self.data_load_button.clicked.connect(self.load_data)
        file_layout.addWidget(self.data_path_label)
        file_layout.addWidget(self.data_path_input)
        file_layout.addWidget(self.data_path_button)

        main_layout.addLayout(file_layout)

        load_button_layout = QHBoxLayout()
        load_button_layout.addWidget(self.data_load_button)

        main_layout.addLayout(load_button_layout)

        # 参数输入区域（分为三列）
        columns_layout = QHBoxLayout()
        self.input_fields = {}  # 用字典保存所有参数输入框

        # 第一列：节点数量、抗弯惯性矩、上缘抗弯模量、下缘抗弯模量、弹性模量
        col1_layout = QVBoxLayout()
        col1_params = [
            ("节点数量", "91"),
            ("抗弯惯性矩", "0.2"),
            ("上缘抗弯模量", "0.3"),
            ("下缘抗弯模量", "0.2"),
            ("弹性模量", "2.0e11")
        ]
        for label_text, default in col1_params:
            row = QHBoxLayout()
            label = QLabel(label_text + "：")
            label.setMinimumWidth(120)
            label.setAlignment(Qt.AlignRight)
            line_edit = QLineEdit()
            line_edit.setText(default)
            row.addWidget(label)
            row.addWidget(line_edit)
            col1_layout.addLayout(row)
            self.input_fields[label_text] = line_edit

        # 第二列：桥梁总长、车道数、车道均布荷载、车道集中荷载
        col2_layout = QVBoxLayout()
        col2_params = [
            ("桥梁总长", "90"),
            ("车道数", "4"),
            ("车道均布荷载", "10.5e3"),
            ("车道集中荷载", "320e3")
        ]
        for label_text, default in col2_params:
            row = QHBoxLayout()
            label = QLabel(label_text + "：")
            label.setMinimumWidth(120)
            label.setAlignment(Qt.AlignRight)
            line_edit = QLineEdit()
            line_edit.setText(default)
            row.addWidget(label)
            row.addWidget(line_edit)
            col2_layout.addLayout(row)
            self.input_fields[label_text] = line_edit

        # 第三列：恒载位移组合系数、恒载内力组合系数、活载位移组合系数、活载内力组合系数
        col3_layout = QVBoxLayout()
        col3_params = [
            ("恒载位移组合系数", "1.0"),
            ("恒载内力组合系数", "1.2"),
            ("活载位移组合系数", "1.0"),
            ("活载内力组合系数", "1.4")
        ]
        for label_text, default in col3_params:
            row = QHBoxLayout()
            label = QLabel(label_text + "：")
            line_edit = QLineEdit()
            line_edit.setText(default)
            row.addWidget(label)
            row.addWidget(line_edit)
            col3_layout.addLayout(row)
            self.input_fields[label_text] = line_edit

        columns_layout.addLayout(col1_layout)
        columns_layout.addLayout(col2_layout)
        columns_layout.addLayout(col3_layout)
        main_layout.addLayout(columns_layout)

        # 添加15个按钮，分为3列，每列5个按钮
        button_layout = QHBoxLayout()

        # 定义每一组按钮的文本与对应APDLData属性（注意区分上翼缘和下翼缘）
        dead_buttons = [
            ("恒载弯矩", "dead_load_moment"),
            ("恒载剪力", "dead_load_shear"),
            ("恒载位移", "dead_load_displacement"),
            ("恒载上翼缘应力", "dead_load_top_stress"),
            ("恒载下翼缘应力", "dead_load_bot_stress")
        ]
        live_buttons = [
            ("活载弯矩", "live_load_moment"),
            ("活载剪力", "live_load_shear"),
            ("活载位移", "live_load_displacement"),
            ("活载上翼缘应力", "live_load_top_stress"),
            ("活载下翼缘应力", "live_load_bot_stress")
        ]
        combined_buttons = [
            ("组合弯矩", "combined_moment"),
            ("组合剪力", "combined_shear"),
            ("组合位移", "combined_displacement"),
            ("组合上翼缘应力", "combined_top_stress"),
            ("组合下翼缘应力", "combined_bot_stress")
        ]

        # 为每组按钮创建垂直布局，并设置按钮属性和点击事件
        for button_list in [dead_buttons, live_buttons, combined_buttons]:
            col_btn_layout = QVBoxLayout()
            for text, attr in button_list:
                btn = QPushButton(text)
                btn.setProperty("plot_attr", attr)
                btn.clicked.connect(self.on_button_clicked)
                col_btn_layout.addWidget(btn)
            button_layout.addLayout(col_btn_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择数据文件", "", "txt文件 (*.txt)")
        if file_path:
            self.data_path_input.setText(file_path)

    def load_data(self):
        # 从输入框中读取参数，并创建APDLData实例
        file_path = self.data_path_input.text().strip()
        if not file_path:
            show_warning("请先选择数据文件")
            return

        try:
            N = int(self.input_fields["节点数量"].text())
            Izz = float(self.input_fields["抗弯惯性矩"].text())
            W_top = float(self.input_fields["上缘抗弯模量"].text())
            W_bot = float(self.input_fields["下缘抗弯模量"].text())
            elastic_Modulus = float(self.input_fields["弹性模量"].text())
            bridge_length = float(self.input_fields["桥梁总长"].text())
            line_number = int(self.input_fields["车道数"].text())
            line_distributed_load = float(self.input_fields["车道均布荷载"].text())
            line_concentrated_load = float(self.input_fields["车道集中荷载"].text())
            dead_disp_coefficient = float(self.input_fields["恒载位移组合系数"].text())
            dead_force_coefficient = float(self.input_fields["恒载内力组合系数"].text())
            live_disp_coefficient = float(self.input_fields["活载位移组合系数"].text())
            live_force_coefficient = float(self.input_fields["活载内力组合系数"].text())
        except Exception as e:
            show_error("参数读取错误:"+ str(e))

            return

        # 创建 APDLData 实例
        self.data_parser = APDLData(file_path=file_path,
                                    N=N,
                                    element_length=1.0,
                                    Izz=Izz,
                                    W_top=W_top,
                                    W_bot=W_bot,
                                    elastic_Modulus=elastic_Modulus)
        # 用用户输入覆盖默认值
        self.data_parser.line_number = line_number
        self.data_parser.line_distributed_load = line_distributed_load * self.data_parser.line_number
        self.data_parser.line_concentrated_load = line_concentrated_load * self.data_parser.line_number
        self.data_parser.dead_disp_coefficient = dead_disp_coefficient
        self.data_parser.dead_force_coefficient = dead_force_coefficient
        self.data_parser.live_disp_coefficient = live_disp_coefficient
        self.data_parser.live_force_coefficient = live_force_coefficient
        self.data_parser.element_length = bridge_length / (self.data_parser.N - 1)
        #print("element_length:"+str(self.data_parser.element_length))

        try:
            self.data_parser.read_and_validate()
            self.data_parser.evaluate_dead_load(200*1000)
            self.data_parser.evaluate_envelope_curve()
            self.data_parser.combine_live_and_dead()
            show_info("数据加载和计算完成")

        except Exception as e:
            show_error("数据处理错误:\n" + str(e) + "\n请确保数据文件存在且符合格式")


    def on_button_clicked(self):
        # 当点击任意一个15个按钮时，调用对应绘图
        if self.data_parser is None:
            show_warning("请先加载数据")
            return

        sender = self.sender()
        attr = sender.property("plot_attr")
        if not attr:
            show_warning("无效的按钮属性")
            return

        # 取得待绘图数据
        data_to_plot = getattr(self.data_parser, attr)
        # 如果数据为1维，则转换为2维（1行）
        if data_to_plot.ndim == 1:
            data_to_plot = np.array([data_to_plot])
        # 计算横轴数据：x_arr = linspace(0, element_length*(N-1), N) 然后在前面插入0
        self.N = self.data_parser.N
        element_length = self.data_parser.element_length
        x_arr = np.linspace(0, element_length * (self.N-1), self.N)
        x_arr = np.insert(x_arr, 0, 0)
        # 调用APDLData的plot_series进行绘图
        title = sender.text()
        self.data_parser.plot_series(x_arr, data_to_plot, title=title, xlabel="位置 (m)", ylabel=title)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Microsoft YaHei", 12)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
