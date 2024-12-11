from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import QTimer, QDateTime, QSize
from PyQt5.QtWidgets import QWidget, QGridLayout, QDesktopWidget, QGroupBox, QFormLayout \
    , QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QTextBrowser \
    ,QRadioButton
from qwt import QwtPlot, QwtLegend

class SerialUi(QWidget):
    """_summary_

    Args:
        None
    """
    def __init__(self) -> None:
        super().__init__()

        self.__initUi()

    # 初始化UI界面
    def __initUi(self) -> None:
        grid_layout = QGridLayout()  # 设置网格布局3行2列
        # 添加组件
        grid_layout.addWidget(self.set_serial_setting_groupbox(), 0, 0)
        grid_layout.addWidget(self.set_curve_display(), 1, 0)
        grid_layout.addWidget(self.set_project_info(), 2, 0)
        grid_layout.addWidget(self.set_data_curve(), 0, 1)
        grid_layout.addWidget(self.set_operate_grid(), 1, 1)
        grid_layout.addWidget(self.set_serial_status(), 2, 1)
        # 设置布局grid_layout
        self.setLayout(grid_layout)
        # 设置窗口大小
        self.resize(900, 500)
        # 设置窗口图标
        self.setWindowIcon(QIcon("./icon/window_TH.png"))
        # 窗口显示在中心
        self.__center()
        # 设置窗口名称
        self.setWindowTitle("温湿度监测平台")
        # 显示
        self.show()

    def __center(self):
        """
            控制窗口显示在屏幕中心
        """
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showtime(self):
        """
            显示当前时间
        """
        time_display = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss dddd')
        self.set_timer.setText(time_display)

    
    # 串口设置区
    def set_serial_setting_groupbox(self) -> QGroupBox:
        # 设置一个 串口设置 分组框
        serial_setting_gb = QGroupBox('串口设置')
        # 设置宽度高度
        # serial_setting_gb.setFixedSize(200, 280)
        # 创建 串口设置 分组框内的布局管理器
        serial_setting_formlayout = QFormLayout()
        
        # 检测串口 按钮  创建一个按钮
        self.set_btn_detect = QPushButton('检测串口')
        serial_setting_formlayout.addRow('串口选择  ', self.set_btn_detect)
        
        # 选择串口 下拉菜单  创建一个下拉列表
        self.set_cb_choose = QComboBox(serial_setting_gb)
        # 添加一个下拉列表 由于没有标签 直接省略即可
        serial_setting_formlayout.addRow(self.set_cb_choose)
        
        # 波特率 下拉菜单
        self.set_baud_rate = QComboBox(serial_setting_gb)
        self.set_baud_rate.addItems(['100', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200',
                            '38400', '56000', '57600', '115200', '128000', '256000']) 
        self.set_baud_rate.setCurrentIndex(12)
        serial_setting_formlayout.addRow('波特率  ', self.set_baud_rate)
        
        # 停止位 下拉菜单
        self.set_stop_bit = QComboBox(serial_setting_gb)    
        self.set_stop_bit.addItems(['1', '1.5', '2'])
        serial_setting_formlayout.addRow('停止位  ', self.set_stop_bit)
        
        # 数据位 下拉菜单
        self.set_data_bit = QComboBox(serial_setting_gb)
        self.set_data_bit.addItems(['8', '7', '6', '5'])
        serial_setting_formlayout.addRow('数据位  ', self.set_data_bit)
        
        # 奇偶校验 下拉菜单
        self.set_odd_check = QComboBox(serial_setting_gb)
        self.set_odd_check.addItems(['N', 'O', 'E'])
        serial_setting_formlayout.addRow('校验位  ', self.set_odd_check)
        
        # 串口操作 按钮
        self.set_serial_operate = QPushButton('打开串口')
        self.set_serial_operate.setIcon(QIcon('./icon/serial_down.png'))
        self.set_serial_operate.setEnabled(False)  # 设置按钮可用
        serial_setting_formlayout.addRow('串口操作  ', self.set_serial_operate)

        # 串口日志 显示框
        self.receive_log_view = QTextBrowser()
        self.receive_log_view.setMinimumWidth(200)
        self.receive_log_view.append('串口日志')
        self.receive_log_view.append('')

        vbox = QVBoxLayout()
        vbox.addWidget(self.receive_log_view)
        serial_setting_formlayout.addRow(vbox)
        self.receive_log_view.setStyleSheet("QTextEdit {color:black;background-color:white}")

        # 设置控件的间隔距离
        serial_setting_formlayout.setSpacing(10)
        # 设置分组框的布局格式
        serial_setting_gb.setLayout(serial_setting_formlayout)
        
        return serial_setting_gb

    def set_curve_display(self) -> QGroupBox:
        # 设置传感器数据显示布局
        serial_send_gp = QGroupBox('显示调整')
        serial_send_vlayout = QVBoxLayout()
        serial_send_gridlayout = QGridLayout()

        # # 选择温度或湿度
        # self.check_Tempcurve = QRadioButton('温度曲线')
        # serial_send_gridlayout.addWidget(self.check_Tempcurve, 0, 0)
        # self.check_Humicurve = QRadioButton('湿度曲线')
        # serial_send_gridlayout.addWidget(self.check_Humicurve, 0, 1)

        # 最大值输入
        self.serial_send_maxlabel = QLabel('最大值')
        serial_send_gridlayout.addWidget(self.serial_send_maxlabel, 1, 0)

        self.serial_max_content = QLineEdit()
        # reg1 = QRegExp('^(?:[1-9][0-9]{0,2}|1000)$')  # 0-1000
        # reg1_validator = QRegExpValidator(reg1, self.serial_max_content)
        # self.serial_max_content.setValidator(reg1_validator)
        serial_send_gridlayout.addWidget(self.serial_max_content, 1, 1)

        self.serial_send_max = QPushButton('设置')
        serial_send_gridlayout.addWidget(self.serial_send_max, 1, 2)
        # 最小值输入
        self.serial_send_minlabel = QLabel('最小值')
        serial_send_gridlayout.addWidget(self.serial_send_minlabel, 2, 0)

        self.serial_min_content = QLineEdit()
        # reg2 = QRegExp('^(?:[1-9][0-9]{0,2}|1000)$')  # 0-1000
        # reg2_validator = QRegExpValidator(reg2, self.serial_min_content)
        # self.serial_min_content.setValidator(reg2_validator)
        serial_send_gridlayout.addWidget(self.serial_min_content, 2, 1)

        self.serial_send_min = QPushButton('设置')
        serial_send_gridlayout.addWidget(self.serial_send_min, 2, 2)

        # 时间范围
        self.serial_send_timelabel = QLabel('时间范围')
        serial_send_gridlayout.addWidget(self.serial_send_timelabel, 3, 0)

        self.serial_time_content = QLineEdit()
        serial_send_gridlayout.addWidget(self.serial_time_content, 3, 1)

        self.serial_send_time = QPushButton('设置')
        serial_send_gridlayout.addWidget(self.serial_send_time, 3, 2)

        self.sins_cb_hex_receive = QCheckBox('HEX接收')
        self.sins_cb_hex_send = QCheckBox('HEX发送')
        self.clear_data_view = QPushButton('清空')
        serial_send_gridlayout.addWidget(self.sins_cb_hex_receive, 4, 0)
        serial_send_gridlayout.addWidget(self.sins_cb_hex_send, 4, 1)
        serial_send_gridlayout.addWidget(self.clear_data_view, 4, 2)

        serial_send_gridlayout.setSpacing(15)
        serial_send_vlayout.addLayout(serial_send_gridlayout)
        serial_send_gp.setLayout(serial_send_vlayout)
        # serial_send_gp.setFixedWidth(250)  # 设置固定宽度

        return serial_send_gp
    
    def set_project_info(self) -> QGroupBox:
        # 设置项目信息
        project_info_gp = QGroupBox()
        project_info_hlayout = QHBoxLayout()
        project_info_gridlayout = QGridLayout()

        self.icon_label = QLabel()
        self.icon = QIcon('./icon/author.png')
        self.icon_label.setPixmap(self.icon.pixmap(20, 20))

        self.project_author = QLabel('Author: XiaoShuai')
        self.project_version = QLabel('Version: 1.0.0')

        project_info_gridlayout.addWidget(self.icon_label, 0, 0)
        project_info_gridlayout.addWidget(self.project_author, 0, 1)
        project_info_gridlayout.addWidget(self.project_version, 0, 2)
        project_info_gridlayout.setSpacing(10)  # 设置网格布局的间距

        project_info_hlayout.addLayout(project_info_gridlayout)
        project_info_gp.setLayout(project_info_hlayout)

        return project_info_gp

    def set_operate_grid(self) -> QGroupBox:
        # 操作一栏
        operate_gp = QGroupBox('操作栏')
        operate_gridlayout = QGridLayout()

        # 温度提示灯
        temp_layout = QHBoxLayout()
        self.temp_high_symbol = QLabel('温度过高指示灯')
        self.icon_size = QSize(32, 32)
        # 使用QPixmap来显示图标
        icon_pixmap = QPixmap('./icon/Indicator_grey.png')
        scaled_icon_pixmap = icon_pixmap.scaled(self.icon_size)
        self.temp_high_icon_label = QLabel()
        self.temp_high_icon_label.setPixmap(scaled_icon_pixmap)
        self.temp_max = QLabel('温度最大值')
        self.temp_high_thread = QLineEdit()
        self.temp_high_thread.setFixedWidth(120)

        self.temp_low_symbol = QLabel('温度过低指示灯')
        self.temp_low_icon_label = QLabel()
        self.temp_low_icon_label.setPixmap(scaled_icon_pixmap)
        self.temp_temp_min = QLabel('温度最小值')
        self.temp_low_thread = QLineEdit()
        self.temp_low_thread.setFixedWidth(120)

        self.check_temperature_value = QLineEdit()
        self.check_temperature_value.setFixedWidth(100)
        self.symbol_temperature = QLabel('℃')
        self.check_button_tem = QPushButton('设置')

        temp_layout.addWidget(self.check_temperature_value)
        temp_layout.addWidget(self.symbol_temperature)
        temp_layout.addWidget(self.temp_high_symbol)
        temp_layout.addWidget(self.temp_high_icon_label)
        temp_layout.addWidget(self.temp_max)
        temp_layout.addWidget(self.temp_high_thread)
        temp_layout.addWidget(self.temp_low_symbol)
        temp_layout.addWidget(self.temp_low_icon_label)
        temp_layout.addWidget(self.temp_temp_min)
        temp_layout.addWidget(self.temp_low_thread)
        temp_layout.addWidget(self.check_button_tem)
        operate_gridlayout.addLayout(temp_layout, 0, 0)

        # 湿度提示灯
        humi_layout = QHBoxLayout()
        self.humidity_high_symbol = QLabel('湿度过高提示灯')
        self.humidity_high_icon_label = QLabel()
        self.humidity_high_icon_label.setPixmap(scaled_icon_pixmap)
        self.humidity_max = QLabel('湿度最大值')
        self.humidity_high_thread = QLineEdit()
        self.humidity_high_thread.setFixedWidth(120)

        self.humidity_low_symbol = QLabel('湿度过低提示灯')
        self.humidity_low_icon_label = QLabel()
        self.humidity_low_icon_label.setPixmap(scaled_icon_pixmap)
        self.humidity_min = QLabel('湿度最小值')
        self.humidity_low_thread = QLineEdit()
        self.humidity_low_thread.setFixedWidth(120)
        
        self.check_humidity_value = QLineEdit()
        self.check_humidity_value.setFixedWidth(100)
        self.symbol_humidity = QLabel('%')
        self.check_button_hum = QPushButton('设置')

        humi_layout.addWidget(self.check_humidity_value)
        humi_layout.addWidget(self.symbol_humidity)
        humi_layout.addWidget(self.humidity_high_symbol)
        humi_layout.addWidget(self.humidity_high_icon_label)
        humi_layout.addWidget(self.humidity_max)
        humi_layout.addWidget(self.humidity_high_thread)
        humi_layout.addWidget(self.humidity_low_symbol)
        humi_layout.addWidget(self.humidity_low_icon_label)
        humi_layout.addWidget(self.humidity_min)
        humi_layout.addWidget(self.humidity_low_thread)
        humi_layout.addWidget(self.check_button_hum)
        operate_gridlayout.addLayout(humi_layout, 1, 0)

        hbox_layout = QHBoxLayout()
        # 操作按钮
        self.tempButton = QRadioButton("温度曲线")
        self.tempButton.setChecked(True)
        self.humiButton = QRadioButton("湿度曲线")
        Vlayout = QVBoxLayout()
        Vlayout.addWidget(self.tempButton)
        Vlayout.addWidget(self.humiButton)
        hbox_layout.addLayout(Vlayout)

        self.open_collect_button = QPushButton('开始采集')
        hbox_layout.addWidget(self.open_collect_button)
        self.open_collect_button.setFixedSize(190, 50)  # 设置按钮的长宽

        self.close_collect_button = QPushButton('停止采集')
        self.close_collect_button.setFixedSize(190, 50)
        hbox_layout.addWidget(self.close_collect_button)

        self.clear_data_button = QPushButton('清空数据')
        self.clear_data_button.setFixedSize(190, 50)
        hbox_layout.addWidget(self.clear_data_button)

        self.save_data_button = QPushButton('保存数据')
        self.save_data_button.setFixedSize(190, 50)
        hbox_layout.addWidget(self.save_data_button)
        operate_gridlayout.addLayout(hbox_layout, 2, 0)

        operate_gp.setLayout(operate_gridlayout)
        return operate_gp

    def set_serial_status(self) -> QGroupBox:
        # 状态一栏
        status_gp = QGroupBox()
        status_layout = QHBoxLayout()  # 垂直布局，用于包含两个水平布局  
    
        # 已发送 一行  
        sent_hbox = QHBoxLayout()  # 水平布局  
        self.sent_count_num = 0  
        self.serial_send_label = QLabel("已发送：")  
        self.serial_send = QLabel(str(self.sent_count_num))  
        sent_hbox.addWidget(self.serial_send_label)  
        sent_hbox.addWidget(self.serial_send)  
        sent_hbox.addStretch()  # 可选，用于添加一些空白间距  
    
        # 已接收 一行  
        receive_hbox = QHBoxLayout()  # 另一个水平布局  
        self.receive_count_num = 0  
        self.serial_receive_label = QLabel("已接收：")  
        self.serial_receive = QLabel(str(self.receive_count_num))  
        receive_hbox.addWidget(self.serial_receive_label)  
        receive_hbox.addWidget(self.serial_receive)  
        receive_hbox.addStretch()  # 可选，用于添加一些空白间距  

        # 当前时间 标签
        self.set_timer = QLabel(self)
        timer = QTimer(self)
        timer.timeout.connect(self.showtime)
        timer.start()
        
        # 将两个水平布局添加到垂直布局中  
        status_layout.addLayout(sent_hbox)  
        status_layout.addLayout(receive_hbox) 
        status_layout.addWidget(self.set_timer)
    
        status_gp.setLayout(status_layout)  # 设置组框的布局 

        return status_gp

    def set_data_curve(self) -> QGroupBox:
        
        sensor_curve_gp = QGroupBox('数据曲线')
        sensor_curve_formlayout = QGridLayout()
        # 环境温度实时曲线
        self.sensor_temp_curve = QwtPlot()
        self.sensor_temp_curve.setMinimumSize(420, 240)
        self.sensor_temp_curve.setFont(QFont("Times New Roman"))
        self.sensor_temp_curve.setTitle("传感器温度实时曲线")
        self.sensor_temp_curve.setAxisTitle(QwtPlot.xBottom, "Time/s")
        self.sensor_temp_curve.setAxisFont(QwtPlot.xBottom, QFont("Times New Roman", 10))
        self.sensor_temp_curve.setAxisTitle(QwtPlot.yLeft, "Value/℃")
        self.sensor_temp_curve.setAxisFont(QwtPlot.yLeft, QFont("Times New Roman", 10))
        self.sensor_temp_curve.insertLegend(QwtLegend(), QwtPlot.BottomLegend)
        
        sensor_curve_formlayout.addWidget(self.sensor_temp_curve, 0, 0)

        # 环境湿度实时曲线
        self.sensor_humi_curve = QwtPlot()
        self.sensor_humi_curve.setMinimumSize(420, 240)
        self.sensor_humi_curve.setFont(QFont("Times New Roman"))
        self.sensor_humi_curve.setTitle("传感器湿度实时曲线")
        self.sensor_humi_curve.setAxisTitle(QwtPlot.xBottom, "Time/s")
        self.sensor_humi_curve.setAxisFont(QwtPlot.xBottom, QFont("Times New Roman", 10))
        self.sensor_humi_curve.setAxisTitle(QwtPlot.yLeft, "Value/%")
        self.sensor_humi_curve.setAxisFont(QwtPlot.yLeft, QFont("Times New Roman", 10))
        self.sensor_humi_curve.insertLegend(QwtLegend(), QwtPlot.BottomLegend)
        
        sensor_curve_formlayout.addWidget(self.sensor_humi_curve, 0, 1)
        sensor_curve_gp.setLayout(sensor_curve_formlayout)
        
        return sensor_curve_gp