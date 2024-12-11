import serial.tools
import serial.tools.list_ports
from SerialUi import SerialUi
import serial
from PyQt5.QtWidgets import QMessageBox, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon, QTextCursor, QPixmap
from PyQt5.QtCore import QTimer
from qwt import QwtPlot, QwtPlotCurve
import time
import csv

class SerialSetting(SerialUi):
    """
    串口设置类
    """
    def __init__(self) -> None:
        super().__init__()
        # 初始化serial对象
        self.serial = serial.Serial()
        # 初始化串口配置文件
        # self.serial_cfg()
        # 初始化串口 绑定槽
        self.init_serial()
        # 初始化曲线和数据  
        self.sensor_curve = self.sensor_temp_curve if self.tempButton.isChecked() else self.sensor_humi_curve
        self.temp_xdata = []  # X轴数据，例如时间戳  
        self.temp_ydata = []  # Y轴数据，接收到的传感器值  
        self.temp_curve_item = QwtPlotCurve()  # QwtPlotCurve对象用于绘图  
        # self.temp_curve_item.setPen(QPen(QColor("#FF0000"), 2)) # 红色
        self.temp_curve_item.attach(self.sensor_temp_curve)  # 将曲线附加到plot上
        self.sensor_temp_curve.replot()  # 初始重绘

        self.humi_xdata = []  # X轴数据，例如时间戳.
        self.humi_ydata = []  # Y轴数据，接收到的传感器值.
        self.humi_curve_item = QwtPlotCurve()  # QwtPlotCurve对象用于绘图.
        # self.humi_curve_item.setPen(QPen(QColor("#00FF00"), 2)) # 绿色
        self.humi_curve_item.attach(self.sensor_humi_curve)  # 将曲线附加到plot上.
        self.sensor_humi_curve.replot()  # 初始重绘.

        # 初始化开关
        self.bottom_temp = False
        self.bottom_humi = False

        self.list_sensor_name = ["temp", "humi"]  # 传感器名称列表

        self.times = 1  # 触发次数

        # 查看温度、湿度的按钮
        self.temperature = False
        self.humidity = False

        self.value = None

    # 初始化串口
    def init_serial(self) -> None:
        # 串口检测  绑定槽
        self.set_btn_detect.clicked.connect(self.detect_serial)
        # 串口打开/关闭 绑定槽
        self.set_serial_operate.clicked.connect(self.open_serial)
        # 定时器接收数据
        self.serial_receive_timer = QTimer(self)
        self.serial_receive_timer.timeout.connect(self.receive_data)
        self.serial_receive_timer.timeout.connect(self.operate_grid_clicked)

        # 设置传感器数据显示 绑定槽
        self.serial_send_max.clicked.connect(self.ser_smax)
        self.serial_send_min.clicked.connect(self.ser_smin)
        self.serial_send_time.clicked.connect(self.ser_stime)
        # 设置开始、关闭采集、清空数据、保存数据一栏 绑定槽
        self.open_collect_button.clicked.connect(self.start_collect)
        self.close_collect_button.clicked.connect(self.stop_collect)
        self.clear_data_button.clicked.connect(self.clear_data)
        self.save_data_button.clicked.connect(self.save_sensor_data)
        # 设置清空串口日志 绑定槽
        self.clear_data_view.clicked.connect(self.clear_serial_data)
        # 设置温度、湿度 绑定槽
        self.check_button_tem.clicked.connect(self.check_temperature)
        self.check_button_hum.clicked.connect(self.check_humidity)


    # 获取端口号
    def get_serial_port(self) -> str:
        """
        获取端口号
        """
        port_name = self.set_cb_choose.currentText()
        com_name = port_name[0:port_name.rfind(': ')]
        return com_name
    
    # 设置串口曲是否可用
    def ser_operate_enable(self, is_enable: bool):
        """
        设置串口是否可用
        :param is_enable: 是否可用
        """
        self.set_cb_choose.setEnabled(is_enable)
        self.set_baud_rate.setEnabled(is_enable)
        self.set_data_bit.setEnabled(is_enable)
        self.set_stop_bit.setEnabled(is_enable)
        self.set_odd_check.setEnabled(is_enable)

    # 检测串口
    def detect_serial(self) -> None:
        # 创建一个串口信息字典
        self.serial_info = {}
        # 返回串口信息
        serial_list = list(serial.tools.list_ports.comports())
        # 清空列表的内容
        self.set_cb_choose.clear()
        for port in serial_list:
            # 添加到字典中
            self.serial_info["%s" % port[0]] = "%s" % port[1]
            # 添加到下拉框中
            self.set_cb_choose.addItem(port[0] + ': ' + port[1])
        if len(self.serial_info) == 0:
            self.set_cb_choose.addItem("未检测到串口")
        self.set_serial_operate.setEnabled(True)

    # 打开串口
    def open_serial(self) -> None:
        # 按打开串口按钮时，且串口信息不为空
        if (self.set_serial_operate.text() == "打开串口") and self.serial_info:
            self.serial.port = self.get_serial_port()  # 串口名
            self.serial.baudrate = int(self.set_baud_rate.currentText())  # 波特率
            self.serial.stopbits = int(self.set_stop_bit.currentText())  # 停止位
            self.serial.bytesize = int(self.set_data_bit.currentText())  # 数据位
            self.serial.parity = self.set_odd_check.currentText()  # 校验位
        # 捕获 串口打开异常
            try:
                self.serial.open()
            except serial.SerialException:
                QMessageBox.critical(self, 'Error', '串口被占用')
                return None
            
            # 打开串口接受定时器 周期100ms   设置少可能会出现数据丢失、处理不及时
            self.serial_receive_timer.start(100)

            # 判断 串口打开状态
            if self.serial.isOpen():
                self.set_serial_operate.setText("关闭串口")
                self.set_serial_operate.setIcon(QIcon('./icon/serial_open.png'))
                self.ser_operate_enable(False)

        # 按打开串口按钮时，且串口信息为空
        elif (self.set_serial_operate.text() == "打开串口") and (self.set_cb_choose.currentText() == "未检测到串口"):
            QMessageBox.critical(self, 'Warning', '没有可打开的串口')
            return None
        
        # # 按打开串口按钮时，且串口信息不为空
        # elif self.set_serial_operate.text() == "打开串口":
        #     QMessageBox.critical(self, 'Warning', '请先选择串口')
        #     return None
        
        # 按关闭串口按钮
        elif self.set_serial_operate.text() == "关闭串口":
            # 关闭串口接受定时器
            self.serial_receive_timer.stop()
            try:
                self.serial.close()
            except serial.SerialException:
                QMessageBox.critical(self, 'Error', '串口关闭失败')
                return None
            self.set_serial_operate.setText("打开串口")
            self.set_serial_operate.setIcon(QIcon('./icon/serial_close.png'))
            self.ser_operate_enable(True)

            # 更改已发送和已接收字数
            self.sent_count_num = 0
            self.serial_send.setText(str(self.sent_count_num))
            self.receive_count_num = 0
            self.serial_receive.setText(str(self.receive_count_num))

    # 发送
    def send_text(self, send_string) -> None:
        if self.serial.isOpen():
            # # 非空字符串
            if send_string != '' :
                # 如果勾选了HEX发送 则以HEX发送 String到Int再到Byte
                if self.sins_cb_hex_send.isChecked():
                    # 移除头尾的空格或换行符
                    send_string = send_string.strip()
                    sent_list = []
                    while send_string != '':
                        # 检查是否是16进制 如果不是则抛出异常
                        try:
                            # 将send_string前两个字符以16进制解析成整数
                            num = int(send_string[0:2], 16)
                        except ValueError:
                            QMessageBox.critical(self, 'Wrong Data', '请输入十六进制数据，以空格分开！')
                            self.sins_cb_hex_send.setChecked(False)
                            return None
                        else:
                            send_string = send_string[2:].strip()
                            # 将需要发送的字符串保存在sent_list里
                            sent_list.append(num)
                    # 转化为byte
                    single_sent_string = bytes(sent_list)
                # 否则ASCII发送
                else:
                    single_sent_string = send_string.encode('utf-8')

                # 获得发送字节数
                sent_num = self.serial.write(single_sent_string)
                self.sent_count_num += sent_num
                self.serial_send.setText(str(self.sent_count_num))

        else:
            QMessageBox.warning(self, 'Port Warning', '没有可用的串口，请先打开串口！')
            return None

    # # 设置传感器数据 显示布局 按键槽
    def ser_smax(self) -> None:
        scale_div = self.sensor_curve.axisScaleDiv(QwtPlot.yLeft)
        restrict_mval = self.serial_max_content.text()
        if restrict_mval:
            self.ymax_restrict = float(restrict_mval)
            self.sensor_curve.setAxisScale(QwtPlot.yLeft, scale_div.lowerBound(), self.ymax_restrict) 
            self.sensor_curve.replot()
        else:
            QMessageBox.warning(self, 'Port Warning', '请先输入数值！')
            return None
    def ser_smin(self) -> None:
        scale_div = self.sensor_curve.axisScaleDiv(QwtPlot.yLeft)
        restrict_mval = self.serial_min_content.text()
        if restrict_mval:
            self.ymin_restrict = float(restrict_mval)
            self.sensor_curve.setAxisScale(QwtPlot.yLeft, self.ymin_restrict, scale_div.upperBound()) 
            self.sensor_curve.replot()
        else:
            QMessageBox.warning(self, 'Port Warning', '请先输入数值！')
            return None
    def ser_stime(self) -> None:
        scale_div = self.sensor_curve.axisScaleDiv(QwtPlot.xBottom)
        restrict_mval = self.serial_time_content.text()
        if restrict_mval:
            self.time_restrict = float(restrict_mval)
            self.sensor_curve.setAxisScale(QwtPlot.xBottom, scale_div.lowerBound(), self.time_restrict)
            self.sensor_curve.replot()
        else:
            QMessageBox.warning(self, 'Port Warning', '请先输入数值！')
            return None

    # 接收数据
    def receive_data(self) -> None:
        try:
            # inWaiting()：返回接收缓存中的字节数
            num = self.serial.in_waiting
        except:
            pass
        else:
        	# 接收缓存中有数据
            if num > 0:
            	# 读取所有的字节数
                self.data = self.serial.read(num)
                receive_num = len(self.data)
                # HEX显示
                if self.sins_cb_hex_receive.isChecked():
                    receive_string = ''
                    for i in range(0, len(self.data)):
                        # {:X}16进制标准输出形式 02是2位对齐 左补0形式
                        receive_string = receive_string + '{:02X}'.format(self.data[i]) + ' '
                    self.receive_log_view.append(receive_string)
                    # 让滚动条随着接收一起移动
                    self.receive_log_view.moveCursor(QTextCursor.End)
                else:
                    self.value = (self.data).decode('UTF-8')
                    self.receive_log_view.insertPlainText(self.value)
                    self.receive_log_view.moveCursor(QTextCursor.End)

                # 更新已接收字节数
                self.receive_count_num += receive_num
                self.serial_receive.setText(str(self.receive_count_num))
                if self.bottom_temp and self.bottom_humi:
                    self.update_sensor_data(sym=True)
                elif self.bottom_temp is True:
                    self.update_sensor_data()
                elif self.bottom_humi is True:
                    self.update_sensor_data(curve="humi")
            else:
                pass

    # 设置温度、湿度查看一栏
    def check_temperature(self) -> None:
        """设置、修改温度阈值"""
        if self.check_button_tem.text() == '设置':
            self.temperature = True
            self.temp_high_thread.setEnabled(False)
            self.temp_low_thread.setEnabled(False)
            self.check_button_tem.setText('修改')
        elif self.check_button_tem.text() == '修改':
            self.temperature = False
            self.temp_high_thread.setEnabled(True)
            self.temp_low_thread.setEnabled(True)
            self.check_button_tem.setText('设置')

    def check_humidity(self) -> None:
        """设置、修改湿度阈值"""
        if self.check_button_hum.text() == '设置':
            self.humidity = True
            self.humidity_high_thread.setEnabled(False)
            self.humidity_low_thread.setEnabled(False)
            self.check_button_hum.setText('修改')  # 更新按钮文本为“修改”
        elif self.check_button_hum.text() == '修改':
            self.humidity = False
            self.humidity_high_thread.setEnabled(True)
            self.humidity_low_thread.setEnabled(True)
            self.check_button_hum.setText('设置')  # 更新按钮文本为“设置”

    # 设置开始、关闭采集、清空数据、保存数据一栏
    def start_collect(self) -> None:
        """开始采集"""
        if self.times == 1:
            self.start_time = time.time() 
            self.times = 2 
        # self.open_collect_button.setEnabled(False)
        if self.tempButton.isChecked():
            self.bottom_temp = True
        elif self.humiButton.isChecked():
            self.bottom_humi = True
    
    def stop_collect(self) -> None:
        """"关闭采集"""
        # self.open_collect_button.setEnabled(True)
        if self.tempButton.isChecked():
            self.bottom_temp = False
        elif self.humiButton.isChecked():
            self.bottom_humi = False
        self.times = 1 if self.bottom_temp==False and self.bottom_humi==False else 2

    def clear_data(self) -> None:
        """清空数据"""
        if self.tempButton.isChecked():
            xdata_var_name = self.list_sensor_name[0] + '_xdata'
            ydata_var_name = self.list_sensor_name[0] + '_ydata' 
            setattr(self, xdata_var_name, [])  # X轴数据，例如时间戳  
            setattr(self, ydata_var_name, [])  # Y轴数据，接收到的传感器值  
            
            # 设置曲线数据  
            curve_item_var_name = self.list_sensor_name[0] + '_curve_item'  
            curve_item = getattr(self, curve_item_var_name)  # 假设curve_item已经是QwtPlotCurve的实例  
            curve_item.setData([], [])  # 设置曲线数据为空，等待后续更新
        elif self.humiButton.isChecked():
            xdata_var_name = self.list_sensor_name[1] + '_xdata'
            ydata_var_name = self.list_sensor_name[1] + '_ydata' 
            setattr(self, xdata_var_name, [])  # X轴数据，例如时间戳  
            setattr(self, ydata_var_name, [])  # Y轴数据，接收到的传感器值  
            
            # 设置曲线数据  
            curve_item_var_name = self.list_sensor_name[1] + '_curve_item'  
            curve_item = getattr(self, curve_item_var_name)  # 假设curve_item已经是QwtPlotCurve的实例  
            curve_item.setData([], [])  # 设置曲线数据为空，等待后续更新
        self.sensor_curve.replot()

    def update_sensor_data(self, curve: str = "temp", sym: bool = False) -> None:  
        # 解析串口数据  
        data_str = self.value.strip()  # 去除首尾空格和换行符  
        if data_str:  # 如果数据不为空  
            sensor_data = data_str.split('/')  # 按'/'分割数据  
            for data in sensor_data:  
                if sym == True:
                    if data.startswith('t'):
                        temp_value = data[1:]  # 获取温度值
                        self.check_temperature_value.setText(temp_value)
                        self.update_sensor_curve(curve, float(temp_value))
                    if data.startswith('h'):
                        humi_value = data[1:]  # 获取湿度值
                        self.check_humidity_value.setText(humi_value)
                        self.update_sensor_curve("humi", float(humi_value))
                elif curve == 'temp' and sym == False:
                    if data.startswith('t'):
                        temp_value = data[1:]  # 获取温度值
                        self.check_temperature_value.setText(temp_value)
                        self.update_sensor_curve(curve, float(temp_value))
                elif curve == 'humi' and sym == False:
                    if data.startswith('h'):
                        humi_value = data[1:]  # 获取湿度值
                        self.check_humidity_value.setText(humi_value)
                        self.update_sensor_curve(curve, float(humi_value))
    
    def update_sensor_curve(self, curve: str, sensor_value: float) -> None:  
        current_time = time.time() - self.start_time  # 时间戳  
        # 根据sensor_id选择对应的数据列表和曲线对象进行更新  
        if curve == "temp":  
            self.temp_xdata.append(current_time)  
            self.temp_ydata.append(sensor_value)
            self.temp_curve_item.setData(self.temp_xdata, self.temp_ydata) # 更新曲线数据
            self.sensor_temp_curve.replot()
        elif curve == "humi":  
            self.humi_xdata.append(current_time)
            self.humi_ydata.append(sensor_value)
            self.humi_curve_item.setData(self.humi_xdata, self.humi_ydata)
            self.sensor_humi_curve.replot()

    def save_sensor_data(self) -> None:  
        """保存传感器数据""" 
        # 弹窗选择保存的文件类型和路径  
        file_dialog = QFileDialog(self)  
        file_dialog.setFileMode(QFileDialog.AnyFile)  
        # file_dialog.setNameFilter("CSV Files (*.csv);;Text Files (*.txt);;Excel Files (*.xlsx)")  
        file_dialog.setNameFilter("CSV Files (*.csv)")  
        if file_dialog.exec_():  
            selected_files = file_dialog.selectedFiles()  
            file_path = selected_files[0]  
            file_type = file_dialog.selectedNameFilter()  
            
            # 根据文件类型保存数据  
            if 'CSV' in file_type:  
                self.save_data_as_csv(file_path)  
            # elif 'Text' in file_type:  
            #     self.save_data_as_txt(file_path)  
            # elif 'Excel' in file_type:  
            #     self.save_data_as_xlsx(file_path)  
            else:  
                QMessageBox.warning(self, 'Warning', 'Unsupported file type.')  
                return  
            
            QMessageBox.information(self, 'Information', f'Data saved to {file_path}')  

    def save_data_as_csv(self, file_path: str) -> None:  
        """将数据保存为CSV文件，仅保存被勾选的传感器的数据"""  
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:  
            writer = csv.writer(csvfile)  
            # 修正表头以匹配数据写入的格式  
            csv_list = ['Time', 'temp', 'humidity']  
            # 写入表头  
            writer.writerow(csv_list)  
            
            # 假设数据长度   
            max_length = 0  
            for i in range(2):  
                xdata_var_name = self.list_sensor_name[i] + '_xdata'
                ydata_var_name = self.list_sensor_name[i] + '_ydata'
                xdata = getattr(self, xdata_var_name, [])  
                ydata = getattr(self, ydata_var_name, [])  
                max_length = max(max_length, len(xdata), len(ydata))  
            
            # 初始化行数据 
            row_data = [None] * (3)  
            
            # 遍历数据  
            for t in range(max_length):  
                for i in range(2):  
                    xdata_var_name = self.list_sensor_name[i] + '_xdata'
                    ydata_var_name = self.list_sensor_name[i] + '_ydata'
                    xdata = getattr(self, xdata_var_name, [])  
                    ydata = getattr(self, ydata_var_name, [])  
                    
                    check_box_var_name = self.list_sensor_name[i] + 'data' 
                    check_box = getattr(self, check_box_var_name)  
                    
                    # 根据复选框状态和数据长度来设置行数据  
                    if check_box.isChecked() and t < len(xdata) and t < len(ydata):  
                        # 时间戳和传感器数据在行中的位置是交叉的，计算正确的索引  
                        time_index = (i - 1) * 2  
                        sensor_index = time_index + 1  
                        row_data[time_index] = xdata[t]  # 保存时间戳  
                        row_data[sensor_index] = ydata[t]  # 保存传感器数据  
                
                # 写入当前时间戳下所有勾选传感器的数据  
                writer.writerow(row_data)  
                # 重置行数据以供下一轮使用  
                row_data = [None] * (3)

    def clear_serial_data(self) -> None:
        """清空串口日志数据"""
        self.receive_log_view.clear()
        self.receive_count_num = 0
        self.serial_receive.setText(str(self.receive_count_num))

    def operate_grid_clicked(self) -> None:
        """操作栏触发操作"""
        icon_green = QPixmap('./icon/Indicator_green.png')
        icon_red = QPixmap('./icon/Indicator_red.png')
        if self.value:
            data_str = self.value.strip()  # 去除首尾空格和换行符  
            if data_str:  # 如果数据不为空  
                sensor_data = data_str.split('/')  # 按'/'分割数据  
                for data in sensor_data:
                    if data.startswith('t') and self.temperature:
                        temp_value = data[1:]  # 获取温度值
                        if float(temp_value) > float(self.temp_high_thread.text()):
                            self.temp_high_icon_label.setPixmap(icon_red.scaled(self.icon_size))
                        elif float(temp_value) < float(self.temp_low_thread.text()):
                            self.temp_low_icon_label.setPixmap(icon_red.scaled(self.icon_size))
                        else:
                            self.temp_high_icon_label.setPixmap(icon_green.scaled(self.icon_size))
                            self.temp_low_icon_label.setPixmap(icon_green.scaled(self.icon_size))
                    if data.startswith('h') and self.humidity:
                        humi_value = data[1:]  # 获取湿度值
                        if float(humi_value) > float(self.humidity_high_thread.text()):
                            self.humidity_high_icon_label.setPixmap(icon_red.scaled(self.icon_size))
                        elif float(humi_value) < float(self.humidity_low_thread.text()):
                            self.humidity_low_icon_label.setPixmap(icon_red.scaled(self.icon_size))
                        else:
                            self.humidity_high_icon_label.setPixmap(icon_green.scaled(self.icon_size))
                            self.humidity_low_icon_label.setPixmap(icon_green.scaled(self.icon_size))