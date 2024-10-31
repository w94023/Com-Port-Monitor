from lib.generic.generic import *
from lib.generic.PyQtAddon import *
    
class AppManager():
    def __init__(self, target_directory):
        # 화면 설정
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # DPI 스케일링 활성화
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # 고해상도 DPI에 맞게 이미지도 스케일링

        # Application 생성
        app = QApplication(sys.argv)
        
        # Initial 디렉토리 저장
        self.target_directory = target_directory
        
        # Main window 생성 및 최대화
        self.ui_window = CustomMainWindow("Arduino data communication program")
        
        # UI 생성
        self.create_ui()

        # 창 생성
        self.ui_window.showMaximized()
        
        # Main window이 바로 닫히지 않고 user input을 대기하도록 설정
        sys.exit(app.exec_())
        
    def create_ui(self):
        # Central layout 생성
        self.ui_window.set_central_layout(QVBoxLayout())
        self.ui_window.central_layout.setContentsMargins(100, 10, 100, 10)
        self.ui_window.register_on_closed_event(self.__on_closed)
        
        self.ui_window.add_docking_widget("Directory",      Qt.LeftDockWidgetArea)
        self.ui_window.add_docking_widget("Data export",    Qt.LeftDockWidgetArea)
        self.ui_window.add_docking_widget("COM port",       Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Analog channel", Qt.RightDockWidgetArea)
        
        file_system_viewer = CustomFileSystemWidget(self.target_directory)
        self.COM_widget = CustomCOMWidget(self.ui_window)
        self.COM_widget.register_on_connection_failed_event(self.__on_connection_failed)
        self.COM_widget.register_on_disconnected_event(self.__on_disconnected)
        analog_channel_widget = CustomAnalogChannelWidget(self.COM_widget, parent=self.ui_window)
        analog_channel_widget.register_on_selected_channel_changed_event(self.__on_channel_changed)
        analog_channel_widget.register_on_data_received_event(self.__on_data_received)
        record_control_widget = CustomRecordControlWidget(file_system_viewer=file_system_viewer,
                                                          analog_channel_widget=analog_channel_widget, 
                                                          button_size=40, 
                                                          loading_icon_size=60, 
                                                          parent=self.ui_window)
        
        self.plot_canvas = CustomFigureCanvas(parent=self.ui_window, padding=(0.15, 0.95, 0.95, 0.15))
        self.plot_canvas.set_grid(1, 1)
        self.raw_data_plot_axis, self.raw_data_plot_manager = self.plot_canvas.get_ani_ax(0, 0, 1000)
        self.custom_legend_widget = CustomLegendWidget(parent=self.ui_window)
        self.COM_widget.register_on_connection_failed_event(self.custom_legend_widget.clear_layout)
        self.COM_widget.register_on_disconnected_event(self.custom_legend_widget.clear_layout)
        
        self.ui_window.docking_widgets["Directory"].setWidget(file_system_viewer)
        self.ui_window.docking_widgets["Data export"].setWidget(record_control_widget)
        self.ui_window.docking_widgets["COM port"].setWidget(self.COM_widget)
        self.ui_window.docking_widgets["Analog channel"].setWidget(analog_channel_widget)
        self.ui_window.central_layout.addWidget(self.custom_legend_widget, 1)
        self.ui_window.central_layout.addWidget(self.plot_canvas, 10)
        
        # 우측 메뉴 1:1로 분리
        self.ui_window.resizeDocks([self.ui_window.docking_widgets["COM port"], self.ui_window.docking_widgets["Analog channel"]], [1, 1], Qt.Vertical)
        
    def __on_closed(self, event):
        # 창을 닫을 때 호출되는 메서드
        reply = CustomMessageBox.question(self.ui_window, 'Exit Confirmation',
                                        "Are you sure you want to exit?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.COM_widget.disconnect()
            event.accept()  # 창을 닫음
        else:
            event.ignore()  # 창을 닫지 않음
            
    def __on_connection_failed(self):
        self.raw_data_plot_manager.clear()
        
    def __on_disconnected(self):
        self.raw_data_plot_manager.clear()
    
    def __on_channel_changed(self, channel):
        self.raw_data_plot_manager.clear()
        self.raw_data_plot_manager.set_plot(channel)
        
        handles, labels = self.raw_data_plot_axis.get_legend_handles_labels()
        self.custom_legend_widget.set_legend(handles, labels)

    def __on_data_received(self, data):
        # 데이터가 없을 경우 종료
        if len(data) == 0:
            return
        
        self.raw_data_plot_manager.plot(data)

def main():
    current_file_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    data_directory = os.path.join(current_file_path, "data")  # data 폴더를 디렉토리로 설정

    # 디렉토리가 존재하지 않을 시 새로 생성
    create_directory_if_not_exists(data_directory)
    
    AppManager(data_directory)

if __name__ == "__main__":
    main()