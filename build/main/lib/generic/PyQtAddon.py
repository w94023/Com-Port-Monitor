from .generic import *

import os
import time
import itertools
import serial # 시리얼 포트 연결
import serial.tools.list_ports # 시리얼 포트 연결
import threading # 백그라운드 스레드 생성
import re # 정규 표현식 비교
# from functools import partial # 슬롯 메서드에 매개변수 전달

from matplotlib.animation import FuncAnimation

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# from PyQt5 import uic
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from PyQt5.QtCore import (Qt, QSize, QThread, pyqtSignal, QUrl, QDir, QMimeData,
                          QFileSystemWatcher, QTimer, QMutex, QWaitCondition, QByteArray,
                          QRect, QRectF, QMetaObject, QObject)
from PyQt5.QtGui import  (QIcon, QPixmap, QStandardItem, QStandardItemModel, QFontMetrics,
                          QDragEnterEvent, QDragMoveEvent, QDropEvent, QFont, QColor, 
                          QDrag, QBrush, QPen, QPainter, QMovie, QPalette)
from PyQt5.QtWidgets import (QApplication, QLabel, QCalendarWidget, QFrame, QTreeView,
                             QTableWidget, QFileSystemModel, QPlainTextEdit, QToolBar,
                             QWidgetAction, QComboBox, QAction, QSizePolicy, QInputDialog,
                             QWidget, QTextEdit, QMainWindow, QDockWidget, QHBoxLayout,
                             QVBoxLayout, QToolButton, QPushButton, QProgressBar, QSpacerItem,
                             QScrollArea, QFileDialog, QTableWidgetItem, QListWidget, QListWidgetItem,
                             QHeaderView, QMessageBox, QStyledItemDelegate, QStyleOptionViewItem,
                             QGridLayout, QDialog, QLineEdit, QListView)
                      
#############################################
#             디렉토리 설정                 #
#############################################
target_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
json_directory = os.path.join(target_directory, 'data')
fonts_directory = os.path.join(os.path.join(os.path.join(target_directory, 'lib'), 'generic'), 'fonts')
icons_directory = os.path.join(os.path.join(os.path.join(target_directory, 'lib'), 'generic'), 'icons')

#############################################
#                PyQt 애드온                #
#############################################
class PyQtAddon():
    """애드온 메서드"""
    # Layout 초기화
    def remove_all_widgets_in_layout(no_data_widget, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        layout.addWidget(no_data_widget)
    
    # Layout 초기화 (위젯 삭제 x)
    def clear_layout(layout):
        """Layout의 모든 위젯을 레이아웃에서 제거하여 초기화"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # 레이아웃에서 위젯 제거 (삭제하지 않음)
                layout.removeWidget(widget)
                widget.setParent(None)
            
    # Layout 초기화 (위젯 삭제 o)
    def init_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            
    # svg 파일 import를 위한 파일 경로 획득
    # 파일 경로에 빈칸, 한글이 포함되어 있을 경우, url로 변환해야 함
    def convert_url(path):
        return QUrl.fromLocalFile(path).toLocalFile()
    
    def get_svg_icon(image_path, width, height):
        return QIcon(QPixmap(image_path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def set_button_icon(button, icon_path, width, height):
        """
        버튼에 PNG 이미지를 설정하고 크기에 맞게 조정하는 함수
        :param button: QPushButton 객체
        :param image_path: 이미지 경로
        :param width: 버튼 너비
        :param height: 버튼 높이
        """
        icon = QIcon(QPixmap(PyQtAddon.convert_url(os.path.join(icons_directory, icon_path))).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        button.setIcon(icon)
        button.setIconSize(QSize(width, height))  # 버튼의 아이콘 크기를 버튼 크기에 맞게 설정
        button.setFixedSize(width, height)  # 버튼의 크기를 고정
        
        return button
    
    colors = {}
    @classmethod
    def get_color(cls, label, option=0):
        # option=0 : rgba as string           ("rgba(100, 200, 255, 1)")
        # option=1 : rgba as normalized tuple ((100/255, 200/255, 255/255, 1))
        if option == 0:  
            return f"""rgba{
                cls.colors[label][0],
                cls.colors[label][1],
                cls.colors[label][2],
                cls.colors[label][3]
                }"""
        elif option == 1:
            return (cls.colors[label][0]/255,
                    cls.colors[label][1]/255, 
                    cls.colors[label][2]/255, 
                    cls.colors[label][3])
        elif option == 2:
            return QColor(
                cls.colors[label][0],
                cls.colors[label][1], 
                cls.colors[label][2], 
                int(cls.colors[label][3]*255)
            )

    """UI 스타일 정의"""
    # Window 설정
    main_window_width = 800
    main_window_height = 600
    # 폰트
    text_font = "Oxanium"
    # UI 컬러 스타일
    colors["background_color"]            = (0,   0,   0,   1  ) # app의 background color
    colors["line_color"]                  = (76,  76,  76,  1  ) # layout 간 구별을 위해 사용되는 line의 color
    colors["content_line_color"]          = (76,  76,  76,  0.5) # layout 내에 사용되는 옅은 line color
    colors["title_text_color"]            = (255, 255, 255, 1  ) # layout title에 사용되는 text color
    colors["title_bar_color"]             = (31,  91,  92,  1  ) # layout title bar에 사용되는 color
    colors["content_text_color"]          = (255, 255, 255, 0.5) # layout 내 content 표시에 사용되는 text color (title_text_color보다 연하게 설정)
    colors["content_hover_color"]         = (76,  76,  76,  0.5) # layout 내에서 선택 가능한 항목에 마우스 hover 시 사용되는 color
    colors["error_text_color"]            = (255, 0,   0,   0.6) # 특히 log에서, 에러가 발생했을 때 출력하는 text의 color (붉은 계열 색으로 설정)
    colors["minimize_button_hover_color"] = (100, 100, 100, 0.4) # layout title bar의 minimize button 마우스 hover 시 사용되는 color
    colors["close_button_hover_color"]    = (255, 0,   0,   0.4) # layout title bar의 close button 마우스 hover 시 사용되는 color
    # Plot 컬러 스타일
    colors["point_color_1"]               = (100, 100, 100, 0.5) # 회색
    colors["point_color_2"]               = (0,   120, 212, 0.5) # 파란색
    colors["point_color_3"]               = (252, 88,  126, 1  ) # 분홍색
    colors["point_color_4"]               = (234, 23,  12,  1  ) # 붉은색
    colors["point_color_5"]               = (31,  91,  92,  0.5) # 투명한 청록색
    colors["axis_color_1"]                = (255, 255, 255, 1  ) # 하얀색
    colors["axis_color_2"]                = (76,  76,  76,  1  ) # 연한 회색
    colors["axis_color_3"]                = (150, 150, 150, 1  ) # 짙은 회색
    colors["plot_color_1"]                = (86 , 233, 255, 1  ) # 청록 계열
    colors["plot_color_2"]                = (255, 183, 57,  1  ) # 오렌지 계열
    colors["plot_color_3"]                = (222, 65,  2,   1  ) # 빨강 계열
    colors["plot_color_1_transparent"]    = (86 , 233, 255, 0.5) # 청록 계열
    colors["plot_color_2_transparent"]    = (255, 183, 57,  0.5) # 오렌지 계열
    colors["plot_color_3_transparent"]    = (222, 65,  2,   0.5) # 빨강 계열
    # Scrollbar 스타일 정의
    background_color = "rgba(0, 0, 0, 1)" # UI 컬러 스타일과 동일하게 설정
    scrollbar_width = 15
    scrollbar_minimum_height = 15
    scrollbar_handle_color = "rgba(76, 76, 76, 0.5)"
    vertical_scrollbar_style = f"""
                                /* 수직 스크롤바 */   
                                QScrollBar:vertical {{
                                    border: 1px solid {scrollbar_handle_color};
                                    background: {background_color};
                                    width: {scrollbar_width}px;
                                    margin: 0px 0px 0px 0px;
                                }}
                                /* 수직 스크롤바 핸들 */
                                QScrollBar::handle:vertical {{
                                    border: none;
                                    background-color: {scrollbar_handle_color};
                                    width: {scrollbar_width}px;
                                    min-height: {scrollbar_minimum_height}px;
                                }}
                                /* 아래 화살표 부분 */
                                QScrollBar::add-line:vertical {{
                                    border: none;
                                    background: #d3d3d3;
                                    height: 0px;
                                    subcontrol-position: bottom;
                                    subcontrol-origin: margin;
                                }}
                                /* 위 화살표 부분 */
                                QScrollBar::sub-line:vertical {{
                                    border: none;
                                    background: #d3d3d3;
                                    height: 0px;
                                    subcontrol-position: top;
                                    subcontrol-origin: margin;
                                }}
                                /* 화살표 부분 삭제 */
                                QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                                    background: none;
                                }}
                                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                                    background: none;
                                }}
                                """                  
    horizontal_scrollbar_style = f"""
                                /* 수평 스크롤바 */   
                                QScrollBar:horizontal {{
                                    border: 1px solid {scrollbar_handle_color};
                                    background: {background_color};
                                    height: {scrollbar_width}px;
                                    margin: 0px 0px 0px 0px;
                                }}
                                /* 수평 스크롤바 핸들 */
                                QScrollBar::handle:horizontal {{
                                    border: none;
                                    background-color: {scrollbar_handle_color};
                                    height: {scrollbar_width}px;
                                    min-width: {scrollbar_minimum_height}px;
                                }}
                                /* 아래 화살표 부분 */
                                QScrollBar::add-line:horizontal {{
                                    border: none;
                                    background: #d3d3d3;
                                    width: 0px;
                                    subcontrol-position: bottom;
                                    subcontrol-origin: margin;
                                }}
                                /* 위 화살표 부분 */
                                QScrollBar::sub-line:horizontal {{
                                    border: none;
                                    background: #d3d3d3;
                                    width: 0px;
                                    subcontrol-position: top;
                                    subcontrol-origin: margin;
                                }}
                                /* 화살표 부분 삭제 */
                                QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {{
                                    background: none;
                                }}
                                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                                    background: none;
                                }}
                                """

#############################################
#            PyQt 클래스 재정의             #
#############################################
"""FigureCanvas 재정의""" 
class CustomAxisAnimatingManager():
    def __init__(self, canvas, fig, ax, data_length):
        super().__init__()
        # animation 생성을 위한 인스턴스 저장
        self.canvas = canvas
        self.fig = fig
        self.ax = ax
        self.data_length = data_length
        
        # ax 설정
        self.ax.set_xlim(0, data_length)
        self.ax.set_ylim(0, 1200)

        # 데이터 설정
        self.lines = {}
        self.y_data = {}
        
        # line color 설정
        self.line_color_list = [PyQtAddon.get_color("plot_color_1", option=1),
                                PyQtAddon.get_color("plot_color_2", option=1),
                                PyQtAddon.get_color("plot_color_3", option=1)]
        self.line_count = 0

        # animation 생성
        self.ani = FuncAnimation(self.fig, self.update_plot, frames=itertools.count(), interval=8, blit=True, save_count=50)
        
    def __get_line_color(self):
        line_color = self.line_color_list[self.line_count]
        self.line_count += 1
        return line_color
        
    def update_plot(self, frame):
        """매 프레임마다 y값을 업데이트하는 함수"""
        for key, y_data in self.y_data.items():
            x_data = list(range(len(y_data)))
            self.lines[key].set_data(x_data, y_data)
            
        return list(self.lines.values())

    def clear(self):
        # 데이터 초기화
        self.lines.clear()
        self.y_data.clear()
        
        # ax의 모든 플롯과 내용 초기화
        self.ax.cla()  # 또는 self.ax.clear()
        
        self.line_count = 0
        self.ax.set_xlim(0, self.data_length)
        self.ax.set_ylim(0, 1200)
        
    def set_plot(self, headers):
        for header in headers:
            if header not in self.lines.keys():
                self.lines[header] = self.ax.plot([], [], color=self.__get_line_color(), label=header)[0]
                self.y_data[header] = []
        
    def plot(self, y_data):
        if isinstance(y_data, dict):
            headers = y_data.keys()
            
            for header in headers:
                if header in self.y_data.keys():
                    self.y_data[header].append(y_data[header])
                    
                    if len(self.y_data[header]) >= self.data_length:
                        self.y_data[header].pop(0)
    
class CustomFigureCanvas(FigureCanvas):
    """클래스 메서드"""
    def set_clear_ax(ax):
        # 배경색 설정
        ax.set_facecolor(PyQtAddon.get_color("background_color", option=1))
        
        # 각 축의 테두리 제거
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        # x축, y축 제거
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        
    def set_custom_ax(ax):
        # 배경색 설정
        ax.set_facecolor(PyQtAddon.get_color("background_color", option=1))
        # 축 틱과 틱 레이블 색상 설정
        ax.tick_params(axis='x', colors='white')  # x축 틱 색상 설정
        ax.tick_params(axis='y', colors='white')  # y축 틱 색상 설정
        for label in ax.get_xticklabels():
            label.set_fontfamily(PyQtAddon.text_font)  # x축 틱 레이블의 글씨체 설정
        for label in ax.get_yticklabels():
            label.set_fontfamily(PyQtAddon.text_font)  # y축 틱 레이블의 글씨체 설정
        # 축 스파인(외곽선) 색상 설정
        ax.spines['bottom'].set_color(PyQtAddon.get_color("axis_color_2", option=1))  # 아래쪽 축 색상
        ax.spines['top'].set_color(PyQtAddon.get_color("axis_color_2", option=1))     # 위쪽 축 색상
        # ax.spines['left'].set_color('white')    # 왼쪽 축 색상
        # ax.spines['right'].set_color('white')   # 오른쪽 축 색상
        
    def remove_xlabels(ax):
        ax.tick_params(axis='x', which='both', left=False)
        ax.set_xticklabels([])

    def remove_ylabels(ax):
        ax.tick_params(axis='y', which='both', left=False)
        ax.set_yticklabels([])
        
    """인스턴스 메서드"""
    def __init__(self, parent=None, padding=(0.05, 0.95, 0.95, 0.05)):
        """Figure 생성"""
        self.fig = Figure()
        # Canvas 초기화
        super().__init__(self.fig)
        # 배경색 설정
        self.fig.patch.set_facecolor(PyQtAddon.get_color("background_color", option=1))
        # 여백 줄이기
        self.fig.subplots_adjust(left=padding[0], right=padding[1], top=padding[2], bottom=padding[3])
        # parent 설정
        if parent:
            self.setParent(parent)
            
    def set_grid(self, nrows, ncols, **kwargs):
        gridspec_params = ['wspace', 'hspace']
        # kwargs에서 GridSpec에 필요한 매개변수만 추출
        gridspec_kwargs = {k: v for k, v in kwargs.items() if k in gridspec_params and v is not None}
        self.grid = plt.GridSpec(nrows, ncols, **gridspec_kwargs) # grid 정보 반환

    def get_ani_ax(self, row, col, data_length=1000):
        ax = self.fig.add_subplot(self.grid[row, col])
        CustomFigureCanvas.set_custom_ax(ax)
        animating_manager = CustomAxisAnimatingManager(self, self.fig, ax, data_length)
        return ax, animating_manager
        
    def get_ax(self, row, col):
        ax = self.fig.add_subplot(self.grid[row, col])
        CustomFigureCanvas.set_custom_ax(ax)
        return ax
    
    def clear(self):
        """Figure 객체에서 모든 서브플롯을 삭제하는 함수"""
        while self.fig.axes:
            self.fig.delaxes(self.fig.axes[0])  # 첫 번째 subplot을 삭제

    # def plot_error_ax(ax, time_offset, color, label):
    #     def create_arrow_point(ax, x, y, arrow_head_width, arrow_head_length):
    #         ax.add_patch(patches.FancyArrow(x, y+arrow_head_length, 0, -arrow_head_length/100, 
    #                                         width=0, head_width=arrow_head_width, head_length=arrow_head_length, color=color, zorder=3))
    #     # 데이터 표시용 화살표 만들기
    #     xlim = ax.get_xlim()
    #     ylim = ax.get_ylim()
    #     arrow_head_width = (xlim[1]-xlim[0])/60
    #     arrow_head_length = (ylim[1]-ylim[0])/5
    #     create_arrow_point(ax, time_offset, -1,                       arrow_head_width, arrow_head_length) # 1단 화살표
    #     create_arrow_point(ax, time_offset, -1+arrow_head_length*0.7, arrow_head_width, arrow_head_length) # 2단 화살표
    #     ax.text(time_offset, 0, label+"\n"+str(round(time_offset*1000))+" ms", va='bottom', ha='center', fontname=self.label_font_name, fontsize=8, color=color, zorder=3)

class CustomLegendWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 전체 레이아웃 설정
        self.layout = QVBoxLayout()
        
        # 중앙에 레이아웃 설정
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
    def clear_layout(self):
        """현재 레이아웃의 모든 위젯을 삭제하고 초기화하는 메서드"""
        while self.layout.count():
            item = self.layout.takeAt(0)  # 첫 번째 아이템을 가져옴
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # 위젯 삭제
            else:
                # QLayout일 경우, 재귀적으로 내부 위젯도 삭제
                self.clear_layout_items(item.layout())
                
    def clear_layout_items(self, layout):
        """내부 레이아웃의 모든 위젯도 삭제"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()  # 위젯 삭제
                elif item.layout() is not None:
                    self.clear_layout_items(item.layout())  # 내부 레이아웃에 대해 재귀적으로 삭제
                
    def set_legend(self, handles, labels):
        # 기존 레이아웃 초기화
        self.clear_layout()
        
        # 범례 추가
        for i in range(len(handles)):
            tuple_color = handles[i].get_color()
            self.layout.addLayout(self.create_legend_item(labels[i], QColor(int(tuple_color[0]*255), int(tuple_color[1]*255), int(tuple_color[2]*255), int(tuple_color[3]*255))))

    def create_legend_item(self, label_text, color):
        # 레이아웃 생성 (아이콘 + 텍스트)
        legend_item_layout = QHBoxLayout()

        # 색상 박스 아이콘 생성
        color_label = QLabel(self)
        pixmap = QPixmap(20, 2)
        pixmap.fill(color)  # 주어진 색상으로 박스를 채움
        color_label.setPixmap(pixmap)

        # 텍스트 라벨 생성
        text_label = QLabel(label_text)
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        text_label.setStyleSheet("background-color:black; color:white")

        # 레이아웃에 아이콘과 텍스트 추가
        legend_item_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        legend_item_layout.addWidget(color_label)
        legend_item_layout.addWidget(text_label)
        legend_item_layout.setContentsMargins(0, 0, 0, 0)

        return legend_item_layout
    
"""위젯 재정의"""
# QMessageBox
class CustomMessageBox(QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 스타일 시트 설정 (여기서 QMessageBox에 대한 스타일을 적용)
        self.setStyleSheet(f"""
            QMessageBox {{
                background-color:{PyQtAddon.get_color("background_color")};
                border:none;
            }}
            QLabel {{
                border:none;
            }}
            QMessageBox QPushButton {{
                background-color:{PyQtAddon.get_color("point_color_1")};
                color:{PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border-radius: 0px;
                border:none;
            }}
            QMessageBox QPushButton:hover {{
                background-color:{PyQtAddon.get_color("point_color_2")};
                border:none;
            }}
        """)

    @staticmethod
    def information(parent, title, text):
        # 기본 QMessageBox.warning() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)

        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)

        # 경고 아이콘 설정
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()
    
    @staticmethod
    def question(parent, title, text, setStandardButtons, setDefaultButton):
        # 기본 QMessageBox.question() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)

        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)

        # 질문 아이콘 설정
        msg_box.setIcon(QMessageBox.Question)
        
        # Standarad 버튼 설정
        msg_box.setStandardButtons(setStandardButtons)
        
        # 기본 선택 설정
        msg_box.setDefaultButton(setDefaultButton)

        # 사용자의 응답 반환
        return msg_box.exec_()

    @staticmethod
    def warning(parent, title, text):
        # 기본 QMessageBox.warning() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)

        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)

        # 경고 아이콘 설정
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()

    @staticmethod
    def critical(parent, title, text):
        # 기본 QMessageBox.critical() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)
        
        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)
        
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()
    
# QInputDialog
class CustomInputDialog(QInputDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # QInputDialog에 대한 스타일 시트 적용
        self.setStyleSheet(f"""
            QInputDialog {{
                background-color: {PyQtAddon.get_color("background_color")};
                border: none;
            }}
            QLabel {{
                color: {PyQtAddon.get_color("title_text_color")};
                font-family: {PyQtAddon.text_font};
                border: none;
            }}
            QLineEdit {{
                background-color: {PyQtAddon.get_color("point_color_1")};
                color: {PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border: 1px solid {PyQtAddon.get_color("line_color")};
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: {PyQtAddon.get_color("point_color_1")};
                color: {PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border-radius: 0px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {PyQtAddon.get_color("point_color_2")};
                border: none;
            }}
        """)

    @staticmethod
    def getText(parent, title, label, text=""):
        # CustomInputDialog 사용하여 텍스트 입력 다이얼로그 표시
        dialog = CustomInputDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setTextValue(text)
        dialog.setInputMode(QInputDialog.TextInput)

        # 입력된 텍스트 및 결과 반환
        if dialog.exec_() == QInputDialog.Accepted:
            return dialog.textValue(), True
        else:
            return "", False

# QDialog
class CustomLoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)  # 닫기 버튼 비활성화

        # 레이아웃 생성
        layout = QVBoxLayout()

        # "작업 중" 애니메이션 GIF 추가
        self.loading_label = QLabel(self)
        self.movie = QMovie(PyQtAddon.convert_url(os.path.join(icons_directory, "loading_icon.gif")))  # 로딩 애니메이션 GIF 파일 경로
        self.movie.setScaledSize(QSize(40, 40)) # QMovie의 크기를 특정 픽셀 크기로 설정
        self.loading_label.setMovie(self.movie)
        self.movie.start()
        
        # 정보 라벨 추가
        self.info_label = QLabel("The task is in progress. Please wait...", self)
        self.info_label.setAlignment(Qt.AlignCenter)

        # 텍스트 스타일 설정
        self.info_label.setStyleSheet(f"""QLabel {{
                                         background-color: {PyQtAddon.get_color("background_color")};
                                         color: {PyQtAddon.get_color("title_text_color")};
                                         font-family: {PyQtAddon.text_font};
                                         }}""")

        # 레이아웃에 위젯 추가
        layout.addWidget(self.loading_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.setLayout(layout)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {PyQtAddon.get_color("background_color")};
                border: none;
            }}
        """)

    def on_task_started(self):
        self.show()

    def on_task_finished(self):
        # 작업 완료 시 로딩 대화상자 닫기
        self.accept()
        # # 작업 완료 알림
        # if is_succeed:
        #     CustomMessageBox.information(self, "Task Complete", "The task has been completed successfully.")
        # else:
        #     CustomMessageBox.warning(self, "Warning", "The task has not been completed successfully.")

# QDockWidget
class CustomDockWidget(QDockWidget):
    class CustomTitleBar(QWidget):
        def __init__(self, title, dock_widget=None, toggle_action=None):
            super().__init__()
            self.dock_widget = dock_widget
            self.toggle_action = toggle_action  # Menu에서 사용되는 토글 액션 참조

            # 타이틀바 레이아웃 설정
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 5, 0, 5)
            layout.setSpacing(0)
            
            # 타이틀 텍스트 설정
            title_label = QLabel()
            title_label.setStyleSheet(f"""
                                    QLabel {{
                                        background-color: {PyQtAddon.get_color("title_bar_color")};
                                        color: {PyQtAddon.get_color("title_text_color")};
                                        padding-left:5px;
                                        padding-right:5px;
                                        padding-top:1px;
                                        padding-bottom:1px;
                                    }}
                                    """)
            title_label.setText(title)
            layout.addWidget(title_label)

            spacer = QSpacerItem(20, 0, QSizePolicy.Preferred, QSizePolicy.Minimum)
            layout.addItem(spacer)

            # 최소화 버튼
            minimize_button = QPushButton()
            minimize_button.setFixedSize(16, 16)
            minimize_button.clicked.connect(self.minimize_window)
            PyQtAddon.set_button_icon(minimize_button, "minimize_icon.png", 16, 16)
            minimize_button.setStyleSheet(f"""
                                        QPushButton {{
                                            background-color: transparent;  /* 배경색 없음 */
                                            border: none;  /* 테두리 없음 */
                                            }}
                                        QPushButton:hover {{
                                            background-color: {PyQtAddon.get_color("minimize_button_hover_color")}
                                        }}
                                        """)
            layout.addWidget(minimize_button)

            # 닫기 버튼
            close_button = QPushButton()
            close_button.setFixedSize(16, 16)
            close_button.clicked.connect(self.close_window)
            PyQtAddon.set_button_icon(close_button, "close_icon.png", 16, 16)
            close_button.setStyleSheet(f"""
                                    QPushButton {{
                                        background-color: transparent;  /* 배경색 없음 */
                                        border: none;  /* 테두리 없음 */
                                    }}
                                    QPushButton:hover {{
                                        background-color: {PyQtAddon.get_color("close_button_hover_color")}
                                    }}
                                    """)
            layout.addWidget(close_button)

            # # 타이틀바의 스타일 설정
            self.setStyleSheet(f"""
                            background-color: {PyQtAddon.get_color("background_color")};
                            color: white;
                            font-family: {PyQtAddon.text_font};
                            """)

        def minimize_window(self):
            if self.dock_widget:
                self.dock_widget.setFloating(False)  # 도킹된 상태로 최소화

        def close_window(self):
            if self.dock_widget:
                self.dock_widget.close()  # 도킹 창 닫기
                if self.toggle_action:
                    self.toggle_action.setChecked(False)  # Menu 상태도 반영
                
    def __init__(self, title, parent=None, set_floating=False):
        super().__init__(title, parent)

        # Toggle action 생성
        self.toggle_action = QAction(title, self)
        self.toggle_action.setCheckable(True)
        self.toggle_action.setChecked(True)  # 기본적으로 체크됨 (Dock 표시 중)
        self.toggle_action.triggered.connect(self.__toggle_dock_widget)

        # Title bar 배치
        self.custom_title_bar = self.CustomTitleBar(title, dock_widget=self, toggle_action=self.toggle_action)
        self.setTitleBarWidget(self.custom_title_bar)

        # False : 도킹된 상태로 시작
        self.setFloating(set_floating)  
        
        # 분리 및 도킹 시 호출되는 함수 연결
        self.topLevelChanged.connect(self.__on_dock_widget_top_level_changed)

    def __on_dock_widget_top_level_changed(self, topLevel):
        """QDockWidget이 분리되거나 다시 도킹될 때 호출되는 함수"""
        if topLevel:
            # 분리된 상태에서 창의 프레임 설정
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
            self.setStyleSheet(f"""QDockWidget {{background-color:{PyQtAddon.get_color("background_color")};}}""")
            self.show()  # 스타일 적용 후 다시 표시
        else:
            # 다시 도킹 상태로 돌아올 때
            self.show()  # 스타일 적용 후 다시 표시

    def __toggle_dock_widget(self):
        """도킹 위젯 표시/숨기기"""
        if self.toggle_action.isChecked():
            self.show()  # 표시
        else:
            self.hide()  # 숨기기

# QMainWindow
class CustomMainWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()

        # close 이벤트 등록
        self.on_closed_callback_list = []

        # 메인 중앙 위젯 설정
        self.central_widget = QFrame(self)
        self.setCentralWidget(self.central_widget)

        # 아이콘 설정
        self.setWindowIcon(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "program_icon.svg"))))

        # 메인 윈도우 설정
        self.setGeometry(0, 0, PyQtAddon.main_window_width, PyQtAddon.main_window_height)
        self.setWindowTitle(title)
        self.setStyleSheet(f"""
                           QMainWindow {{
                           background-color: {PyQtAddon.get_color("background_color")};
                           font-family:{PyQtAddon.text_font};
                           }}

                           QMainWindow::separator {{
                               background-color: {PyQtAddon.get_color("line_color")};
                               width: 1px;  /* handle의 너비 (수직) */
                               height: 1px;  /* handle의 높이 (수평) */
                               border: none;
                           }}
                           QMainWindow::separator:hover {{
                               background-color: none;  /* hover 시 색상 변경 */
                           }}

                           QMenuBar {{
                               background-color: {PyQtAddon.get_color("background_color")};  /* MenuBar 배경색 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* MenuBar 텍스트 색상 */
                           }}
                           QMenuBar::item {{
                               background-color: transparent;  /* 항목의 기본 배경 투명 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* 항목 텍스트 색상 */
                           }}
                           QMenuBar::item:selected {{
                               background-color: {PyQtAddon.get_color("point_color_1")};  /* 선택된 항목의 배경색 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* 선택된 항목의 텍스트 색상 */
                           }}
                           QMenuBar::item:pressed {{
                               background-color: {PyQtAddon.get_color("point_color_1")};  /* 눌렀을 때의 배경색 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* 눌렀을 때의 텍스트 색상 */
                           }}
                           QMenu {{
                               background-color: {PyQtAddon.get_color("background_color")};  /* 드롭다운 메뉴 배경색 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* 드롭다운 메뉴 텍스트 색상 */
                               font-family: {PyQtAddon.text_font};  /* 드롭다운 메뉴 폰트 패밀리 */
                           }}
                           QMenu::item:selected {{
                               background-color: {PyQtAddon.get_color("point_color_2")};  /* 드롭다운 메뉴에서 선택된 항목의 배경색 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* 드롭다운 메뉴에서 선택된 항목의 텍스트 색상 */
                           }}
                           """)
        
        # MenuBar 생성 및 Layout 메뉴 추가
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
                              QMenuBar {{
                              border-top: 1px solid {PyQtAddon.get_color("line_color")};
                              border-bottom: 1px solid {PyQtAddon.get_color("line_color")};
                              }}""")
        # self.layout_menu = menubar.addMenu('Layout')
        self.view_menu = menubar.addMenu('View')
        
        # UI 업데이트를 위한 외부 참조 변수
        self.central_layout = None
        self.docking_widgets = {}
        self.menu_layouts = {}
        
    def register_on_closed_event(self, callback):
        self.on_closed_callback_list.append(callback)
        
    def closeEvent(self, event):
        for callback in self.on_closed_callback_list:
            if callback: callback(event)

    def set_central_layout(self, layout):
        self.central_widget.setLayout(layout)
        self.central_layout = layout
        
    def add_docking_widget(self, title, docking_direction):
        # docking widget 생성
        docking_widget = CustomDockWidget(title, parent=self)
        
        # DockWidget으로 추가
        self.addDockWidget(docking_direction, docking_widget)
        
        # 메뉴로 추가
        self.view_menu.addAction(docking_widget.toggle_action)
            
        self.docking_widgets[title] = docking_widget

    # def add_layout_configuration(self, layout_name, layouts_to_show, layouts_location, layout_callback):
    #     # QAction 생성
    #     layout_action = QAction(layout_name, self)
    #     layout_action.triggered.connect(partial(self.layout_action, layouts_to_show, layouts_location, layout_callback))
        
    #     # 메뉴 바에 항목 등록
    #     self.layout_menu.addAction(layout_action)

    #     # 인스턴스 변수에 layout action 등록
    #     self.menu_layouts[layout_name] = layout_action

    # def layout_action(self, layouts_to_show, layouts_location, layout_callback):
    #     for layout in self.docking_widgets.values():
    #         layout.hide()

    #     for i, layout in enumerate(layouts_to_show):
    #         self.removeDockWidget(layout)  # 기존 위치에서 제거
    #         self.addDockWidget(layouts_location[i], layout)  # 변경된 위치로 이동
    #         layout.show()

    #     if layout_callback is not None:
    #         layout_callback()

    # def activate_layout(self, layout_name):
    #     if layout_name in self.menu_layouts.keys():
    #         self.menu_layouts[layout_name].trigger()

"""위젯 신규 정의"""
# CustomFileSystem : 디렉토리의 파일 구조 보여주는 트리 뷰 + 파일 브라우징을 위한 위젯
class CustomFileSystemWidget(QWidget):
    class CustomFileBorwser(QWidget):
        def __init__(self, on_path_changed):
            super().__init__()

            self.path = ""
            self.on_path_changed = on_path_changed
            self.setStyleSheet(f"""
                            QWidget {{
                                margin: 0px;
                                padding: 0px;
                                background-color: none;
                                border-top:1px solid {PyQtAddon.get_color("content_line_color")}; 
                                border-bottom:1px solid {PyQtAddon.get_color("content_line_color")};
                            }}
                            """)

            # Layout 생성
            main_layout = QVBoxLayout()
            self.setLayout(main_layout)

            # 전체적인 border line 생성을 위한 QWidget 생성
            sub_widget = QWidget()
            sub_layout = QHBoxLayout()
            sub_widget.setLayout(sub_layout)
            main_layout.addWidget(sub_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)

            # Icon 생성
            svg_widget = QSvgWidget(PyQtAddon.convert_url(os.path.join(icons_directory, "current_directory_icon.svg")))
            svg_widget.setFixedSize(30, 30)
            svg_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            svg_widget.setStyleSheet("border:none")
            sub_layout.addWidget(svg_widget)

            # Directory showing label 생성
            self.directory_label = QLabel("...")
            self.directory_label.setStyleSheet(f"""
                                            color:{PyQtAddon.get_color("content_text_color")}; 
                                            font-family:'{PyQtAddon.text_font}'; 
                                            border:none;
                                            """)
            self.directory_label.setMinimumSize(0, 30)
            self.directory_label.setMaximumSize(16777215, 30)

            # QLabel의 크기 조정 정책 설정 (크기 제한을 없앰)
            self.directory_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
            sub_layout.addWidget(self.directory_label)

            # Directory search button 생성
            directory_search_button = QPushButton()
            directory_search_button.setFixedSize(30, 30)
            directory_search_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            directory_search_button.clicked.connect(self.open_file_dialog)
            directory_search_button.setStyleSheet(f"""
                                                QPushButton {{
                                                border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "directory_search_icon.svg"))}"); /* 기본 아이콘 */
                                                }}
                                                QPushButton:hover {{
                                                border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "directory_search_icon_hover.svg"))}"); /* 기본 아이콘 */
                                                }}
                                                QPushButton:pressed {{
                                                border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "directory_search_icon_pressed.svg"))}"); /* 기본 아이콘 */
                                                }}
                                                """)
            sub_layout.addWidget(directory_search_button)
            sub_layout.setContentsMargins(0, 0, 0, 0)

            # QTimer를 사용하여 addDockWidget 이후 크기 확인
            QTimer.singleShot(0, self.check_label_width)

        def set_ellipsized_text(self, text):
            """QLabel의 텍스트가 너무 길면 ...으로 표시되도록 설정"""
            # QLabel의 폰트로 QFontMetrics 객체 생성
            metrics = QFontMetrics(self.directory_label.font())

            # QLabel의 너비에 맞춰 텍스트 자르기 (엘리시스 추가)
            elided_text = metrics.elidedText(text, Qt.ElideRight, self.directory_label.width())

            # 잘라낸 텍스트를 QLabel에 설정
            self.directory_label.setText(elided_text)

        def resizeEvent(self, event):
            """윈도우 크기가 조절되면 텍스트를 다시 자름"""
            self.set_ellipsized_text(self.path)
            super().resizeEvent(event)
        
        def set_directory(self, path):
            # label의 text만 변경
            self.path = path
            self.set_ellipsized_text(self.path)

        def check_label_width(self):
            """DockWidget 추가 이후 QLabel의 크기 확인"""
            self.set_ellipsized_text(self.path)

        def open_file_dialog(self):
            """파일 탐색기를 열어 사용자가 선택한 경로를 출력"""
            directory = QFileDialog.getExistingDirectory(self, "Select Directory")

            if directory:
                self.set_directory(directory)
                if self.on_path_changed:
                    self.on_path_changed(self.path)
    
    class CustomTreeView(QTreeView):
        def __init__(self, callback, parent=None):
            super().__init__(parent)
            self.setAcceptDrops(True)
            self.callback = callback
                        
        def dragEnterEvent(self, event: QDragEnterEvent):
            if event.mimeData().hasUrls():
                event.acceptProposedAction()

        def dragMoveEvent(self, event: QDragMoveEvent):
            if event.mimeData().hasUrls():
                event.acceptProposedAction()

        def dropEvent(self, event: QDropEvent):
            if event.mimeData().hasUrls():
                event.setDropAction(Qt.CopyAction)
                event.accept()
                urls = event.mimeData().urls()
                for url in urls:
                    file_path = url.toLocalFile()
                    self.callback(file_path)
                    
            else:
                event.ignore()
            
    class CustomModel(QStandardItemModel):
        def __init__(self, directory):
            super().__init__()
            self.directory = directory
            
        def mimeData(self, indexes):
            mime_data = QMimeData()
            if indexes:
                # 드래그된 항목의 사용자 정의 "이름" 데이터를 MimeData에 저장
                item = self.itemFromIndex(indexes[0])

                # 파일 명 Text로 저장
                mime_data.setText(item.text())
                
                # 파일 경로 Url로 저장
                mime_data.setUrls([QUrl.fromLocalFile(os.path.join(self.directory, item.text()))])

            return mime_data
    
    def __init__(self, root_dir):
        super().__init__()

        # 현재 디렉토리 설정
        self.target_directory = root_dir
        
        # 이벤트 생성
        self.on_directory_changed_callback_list = []
        
        # UI 초기화
        self.__init_ui()
        
    def __init_ui(self):
        # QFileSystemWatcher 설정 (파일 시스템 변화 감시)
        self.watcher = QFileSystemWatcher([self.target_directory])
        self.watcher.directoryChanged.connect(self.__on_directory_system_changed)

        # QVBoxLayout 생성
        layout = QVBoxLayout()

        # File browser 생성
        self.file_browser = self.CustomFileBorwser(self.on_path_changed)
        layout.addWidget(self.file_browser)

        # QStandardItemModel 생성
        self.model = self.CustomModel(self.target_directory)
        self.model.setHorizontalHeaderLabels(['Files and Folders'])

        # 파일 및 폴더 추가
        self.__update_tree_view_list(self.target_directory, force_update=True)

        # QTreeView 생성
        self.tree = self.CustomTreeView(self.__file_dropped_to_tree_view)
        self.tree.setModel(self.model)
        self.tree.setItemsExpandable(False)  # 항목 확장 불가
        self.tree.setRootIsDecorated(False)  # 트리 루트 장식 없애기

        # 헤더 숨기기 (열 이름 숨기기)
        self.tree.setHeaderHidden(True)
        
        # 파일명만 보이도록 다른 열 숨기기 (파일 이름은 0번 열)
        self.tree.setColumnHidden(1, True)  # 파일 크기 숨기기
        self.tree.setColumnHidden(2, True)  # 파일 종류 숨기기
        self.tree.setColumnHidden(3, True)  # 수정 날짜 숨기기

        # 드래그 앤 드롭 설정
        self.tree.setAcceptDrops(True)
        self.tree.setDragEnabled(True)
        self.tree.setDropIndicatorShown(True)

        # QTreeView에서 더블 클릭 시 항목을 처리
        self.tree.doubleClicked.connect(self.on_item_double_clicked)

        self.tree.setStyleSheet(f"""
                                QTreeView {{
                                    background-color: {PyQtAddon.get_color("background_color")};  /* 배경색 검정 */
                                    color: {PyQtAddon.get_color("title_text_color")};
                                    border:none;
                                }}
                                QTreeView::item {{
                                    background-color: {PyQtAddon.get_color("background_color")};  /* 각 항목의 배경색 검정 */
                                    color: {PyQtAddon.get_color("content_text_color")};  /* 각 항목의 텍스트 색상 흰색 */
                                }}
                                QTreeView::item:hover {{
                                    background-color: {PyQtAddon.get_color("content_hover_color")};
                                }}
                                QTreeView::item:selected {{
                                    background-color: {PyQtAddon.get_color("content_hover_color")};
                                }}
                                """
                                +PyQtAddon.vertical_scrollbar_style
                                +PyQtAddon.horizontal_scrollbar_style)

        # QVBoxLayout에 QTreeView 추가
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def register_on_directory_changed_event(self, callback):
        self.on_directory_changed_callback_list.append(callback)
        
    def __update_tree_view_list(self, target_directory, force_update=False):
        # 현재 경로가 target 경로와 다를 경우에만 (혹은 force_update가 True일 경우) 동작
        if target_directory == self.target_directory:
            if not force_update:
                return
            
        self.target_directory = target_directory
        
        # 모델을 초기화
        self.model.clear()  
        
        # 파일 브라우져의 경로 수정 
        self.file_browser.set_directory(self.target_directory)
        
        # 모델의 경로 수정
        self.model.directory = self.target_directory

        """특정 디렉토리의 파일 및 폴더를 트리 뷰에 추가"""
        # 상위 디렉토리 경로 계산
        parent_directory = os.path.abspath(os.path.join(self.target_directory, ".."))

        # 상위 디렉토리가 존재할 경우 .. 항목 추가
        if os.path.isdir(parent_directory) and parent_directory != "C:\\":
            # 가장 위에 .. 항목 추가 (상위 디렉토리 이동)
            parent_directory_selector = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "folder_directory_icon.svg"))), '..')
            parent_directory_selector.setEditable(False)
            self.model.appendRow(parent_directory_selector)

        # 디렉토리 목록과 파일 목록을 분리
        folders = []
        files = []
        for item_name in sorted(os.listdir(self.target_directory)):
            item_path = os.path.join(self.target_directory, item_name)
            if os.path.isdir(item_path):
                folders.append(item_name)
            else:
                files.append(item_name)

        # 폴더부터 먼저 추가
        for folder in folders:
            folder_item = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "folder_icon.svg"))), folder)
            folder_item.setEditable(False)
            self.model.appendRow(folder_item)

        # 파일을 나중에 추가
        for file in files:
            if file.endswith('.csv'):
                file_item = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "file_csv_icon.svg"))), file)
            else:
                file_item = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "file_normal_icon.svg"))), file)
            file_item.setEditable(False)
            self.model.appendRow(file_item)
            
        # QFileSystemWatcher에 새로운 경로 등록
        self.watcher.removePaths(self.watcher.directories())  # 이전 경로 제거
        self.watcher.addPath(self.target_directory)  # 새 경로 추가
        
        for callback in self.on_directory_changed_callback_list:
            if callback: callback(self.target_directory)

    def on_item_double_clicked(self, index):
        """더블 클릭 시 .. 항목을 처리하여 상위 디렉토리로 이동"""
        selected_item = self.model.itemFromIndex(index)
        if selected_item.text() == '..':
            # 상위 디렉토리 경로 계산
            parent_directory = os.path.abspath(os.path.join(self.target_directory, ".."))

            # 상위 디렉토리가 존재하는지 확인
            if os.path.isdir(parent_directory):
                # 상위 디렉토리로 이동
                self.__update_tree_view_list(parent_directory)  # 상위 디렉토리 내용 추가)

        else:
            # 선택된 디렉토리로 이동
            clicked_path = os.path.join(self.target_directory, selected_item.text())
            if os.path.isdir(clicked_path):
                self.__update_tree_view_list(clicked_path)  # 새로운 디렉토리 내용 추가
                
    def __on_directory_system_changed(self, path):
        """감시 중인 디렉토리에서 변경이 발생할 때 호출"""
        self.__update_tree_view_list(path, force_update=True)  # 현재 디렉토리 내용 업데이트

    def __file_dropped_to_tree_view(self, file_path):
        """트리 뷰에 파일 드랍 이벤트 발생 시 호출"""
        # 드랍된 파일의 상위 경로 추출
        parent_directory = os.path.abspath(os.path.join(file_path, ".."))
        
        # 현재 디렉토리 내용 업데이트
        self.__update_tree_view_list(parent_directory) 

    def on_path_changed(self, file_path):
        self.__update_tree_view_list(file_path)

# CustomGridKeyword 위젯 상속을 위한 부모 클래스
class CustomGridKeywordWidget(QWidget):
    def __init__(self, minimum_label_width, minimum_label_height, parent=None):
        super().__init__(parent)

        # 키워드를 격자 형태로 배치하기 위해 GridLayout 생성
        self.grid_layout = QGridLayout()

        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        # 마지막으로 클릭된 라벨을 추적 (Single click에서 사용)
        self.last_clicked_label = None  

        # 현재 클릭되어 있는 모든 라벨을 추적 (Multi click에서 사용)
        self.selected_keywords = []

        # 이벤트 콜백
        self.on_clicked_callback_list = []

        # 레이아웃 설정
        self.setLayout(self.grid_layout)

        # label의 최소 width 및 height 설정 
        self.column_width = minimum_label_width
        self.column_height = minimum_label_height

        # 키워드 저장
        self.keywords = None
        self.labels = []

        # 과도한 업데이트 방지
        self.is_updating = False
        
    def register_on_clicked_event(self, callback):
        self.on_clicked_callback_list.append(callback)

    def calculate_minimum_height(self):
        """라벨의 최소 높이를 기반으로 창의 최소 높이 계산"""
        if self.keywords is None:
            return
        
        columns = max(1, self.width() // self.column_width)
        rows = (len(self.keywords) + columns - 1) // columns  # 키워드 수에 따른 행 개수 계산
        return rows *  self.column_height + (rows - 1) * 0  # 라벨 높이와 행 간격을 고려하여 최소 높이 계산
        # rows = (len(self.keywords) + columns - 1) // columns  # 키워드 수에 따른 행 개수 계산
        # return rows *  self.column_height + (rows - 1) * 0  # 라벨 높이와 행 간격을 고려하여 최소 높이 계산

    def resizeEvent(self, event):
        """윈도우 크기가 변경될 때 호출"""
        self.update_layout()
        super().resizeEvent(event)

    def update_layout(self):
        """현재 창 크기에 따라 키워드 레이아웃 업데이트"""
        if self.keywords is None:
            return
        
        if len(self.labels) == 0:
            return
        
        if self.is_updating:
            return
        
        self.is_updating = True

        # 기존 레이아웃 초기화
        self.clear_layout()

        # 창의 폭을 기준으로 열의 개수 계산
        widget_width = self.width()
        columns = max(1, widget_width // self.column_width)

        # 키워드 추가
        for i, label in enumerate(self.labels):
            row = i // columns
            col = i % columns
            self.grid_layout.addWidget(label, row, col)

        # 창의 최소 크기 업데이트
        self.setMinimumSize(0, self.calculate_minimum_height())

        self.is_updating = False

    def clear(self):
        """QGridLayout 비우기"""
        self.keywords = None
        self.selected_keywords.clear()
        self.last_clicked_label = None
        self.labels.clear()
        self.clear_layout()

    def clear_layout(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # 레이아웃에서 위젯 제거 (삭제하지 않음)
                self.grid_layout.removeWidget(widget)

# CustomGridKeywordMultiClickWidget : 주어진 keyword를 grid로 배치하고, 선택 할 수 있는 위젯
# (한 번의 클릭으로 선택, 여러 항목 선택 가능)
class CustomGridKeywordMultiClickWidget(CustomGridKeywordWidget):
    class CustomGridKeywordLabel(QLabel):
        def __init__(self, keyword, parent=None):
            super().__init__(keyword, parent)
            self.keyword = keyword

            # 기본 스타일 설정
            self.default_style = f"""
            background-color: {PyQtAddon.get_color("background_color")};
            color: {PyQtAddon.get_color("content_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """
            self.hover_style   = f"""
            background-color: {PyQtAddon.get_color("point_color_1")};
            color: {PyQtAddon.get_color("content_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """
            self.clicked_style = f"""
            background-color: {PyQtAddon.get_color("point_color_5")};
            color: {PyQtAddon.get_color("title_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """

            self.setStyleSheet(self.default_style)

            # 텍스트 중앙 정렬
            self.setAlignment(Qt.AlignCenter)

            # 최소 및 최대 높이 설정
            self.setMinimumHeight(25)  # 최소 높이 (픽셀 단위로 설정)
            self.setMaximumHeight(50)  # 최대 높이 (픽셀 단위로 설정)

        def mousePressEvent(self, event):
            """클릭 이벤트 처리"""
            if event.button() == Qt.LeftButton:
                # 이미 선택 되어 있는 경우
                if self.keyword in self.parentWidget().selected_keywords:
                    self.setStyleSheet(self.default_style)  # 클릭된 스타일로 변경
                    self.parentWidget().selected_keywords.remove(self.keyword)
                    
                # 선택 되어 있지 않은 경우
                else:
                    self.setStyleSheet(self.clicked_style)  # 클릭된 스타일로 변경
                    self.parentWidget().selected_keywords.append(self.keyword)

                for callback in self.parentWidget().on_clicked_callback_list:
                    if callback: callback(self.parentWidget().selected_keywords)

        def enterEvent(self, event):
            """마우스가 라벨 위로 올라왔을 때 배경색 변경"""
            self.setStyleSheet(self.hover_style)

        def leaveEvent(self, event):
            """마우스가 라벨 위에서 벗어났을 때 배경색 되돌리기"""
            if self.keyword in self.parentWidget().selected_keywords:
                self.setStyleSheet(self.clicked_style)
            else:
                self.setStyleSheet(self.default_style)

    def __init__(self, minimum_label_width=25, minimum_label_height=25, parent=None):
        super().__init__(minimum_label_width, minimum_label_height, parent)

    def set_keywords(self, keywords):
        self.labels.clear()
        self.keywords = keywords
        for i, keyword in enumerate(self.keywords):
            self.labels.append(self.CustomGridKeywordLabel(keyword, self))
        self.update_layout()

# CustomGridKeywordSingleClickWidget : 주어진 keyword를 grid로 배치하고, 선택 할 수 있는 위젯
# (더블 클릭으로 선택, 한 항목만 선택 가능)
class CustomGridKeywordSingleClickWidget(CustomGridKeywordWidget):
    class CustomGridKeywordLabel(QLabel):
        def __init__(self, keyword, minimum_label_width=25, minimum_label_height=25, parent=None):
            super().__init__(keyword, minimum_label_width, minimum_label_height, parent)
            self.keyword = keyword

            # 기본 스타일 설정
            self.default_style = f"""
            background-color: {PyQtAddon.get_color("background_color")};
            color: {PyQtAddon.get_color("content_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """
            self.hover_style   = f"""
            background-color: {PyQtAddon.get_color("point_color_1")};
            color: {PyQtAddon.get_color("content_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """
            self.clicked_style = f"""
            background-color: {PyQtAddon.get_color("point_color_5")};
            color: {PyQtAddon.get_color("title_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """

            self.setStyleSheet(self.default_style)

            # 텍스트 중앙 정렬
            self.setAlignment(Qt.AlignCenter)

            # 최소 및 최대 높이 설정
            self.setMinimumHeight(25)  # 최소 높이 (픽셀 단위로 설정)
            self.setMaximumHeight(50)  # 최대 높이 (픽셀 단위로 설정)
                    
        def mouseDoubleClickEvent(self, event):
            """더블 클릭 이벤트 처리"""
            if event.button() == Qt.LeftButton:
                # 이전과 다른 라벨이 선택된 경우
                if self.parentWidget().last_clicked_label != self:
                    self.parentWidget().reset_previous_click()  # 이전 클릭된 라벨 초기화
                    self.setStyleSheet(self.clicked_style)  # 클릭된 스타일로 변경
                    self.parentWidget().last_clicked_label = self  # 현재 라벨을 기록

                    # 더블 클릭된 키워드 출력
                    for callback in self.parentWidget().on_clicked_callback_list:
                        if callback: callback(self.keyword)

                # 이전과 같은 라벨이 선택된 경우
                else:
                    self.parentWidget().reset_previous_click()
                    for callback in self.parentWidget().on_clicked_callback_list:
                        if callback: callback(None)

        def enterEvent(self, event):
            """마우스가 라벨 위로 올라왔을 때 배경색 변경"""
            self.setStyleSheet(self.hover_style)

        def leaveEvent(self, event):
            """마우스가 라벨 위에서 벗어났을 때 배경색 되돌리기"""
            if self != self.parentWidget().last_clicked_label:
                self.setStyleSheet(self.default_style)
            else:
                self.setStyleSheet(self.clicked_style)

    def __init__(self, parent=None):
        super().__init__(parent)
        
    def set_keywords(self, keywords):
        self.labels.clear()
        self.keywords = keywords
        for i, keyword in enumerate(self.keywords):
            self.labels.append(self.CustomGridKeywordLabel(keyword, self))
        self.update_layout()

    def reset_previous_click(self):
        """이전에 더블 클릭된 라벨을 기본 스타일로 되돌림"""
        if self.last_clicked_label:
            self.last_clicked_label.setStyleSheet(self.last_clicked_label.default_style)
            self.last_clicked_label = None

# CustomCOMWidget : COM 포트 설정 및 연결
class CustomCOMWidget(QWidget):
    class CustomConnectionStateIcon(QLabel):
        def __init__(self, width, height, parent=None):
            super().__init__(parent)
            
            self.connection_idle_pixmap = QPixmap(PyQtAddon.convert_url(os.path.join(icons_directory, "connection_idle_icon.svg")))
            self.connection_failed_pixmap = QPixmap(PyQtAddon.convert_url(os.path.join(icons_directory, "connection_failed_icon.svg")))
            self.connection_success_pixmap = QPixmap(PyQtAddon.convert_url(os.path.join(icons_directory, "connection_success_icon.svg")))
            
            self.setFixedSize(width, height)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.setScaledContents(True)
            
            self.set_idle_state()
            
        def set_idle_state(self):
            self.setPixmap(self.connection_idle_pixmap)
            
        def set_failed_state(self):
            self.setPixmap(self.connection_failed_pixmap)
            
        def set_success_state(self):
            self.setPixmap(self.connection_success_pixmap)
        
    class CustomComboBox(QComboBox):
        def __init__(self, parent=None):
            super().__init__(parent)
            
            # Dropdown 펼쳐질 때 사용할 ListView 설정
            list_view = QListView()
            list_view.setFocusPolicy(Qt.NoFocus)  # QListView에 포커스 정책 설정 (포커스 없음)
            list_view.setStyleSheet(f"""border:1px solid {PyQtAddon.get_color("line_color")};""")
            self.setView(list_view)  # QComboBox에 수정된 QListView 설정
            
            # 현재 선택된 항목
            self.selected_option = self.currentText()
            
            # 클릭될 때 호출할 이벤트
            self.on_clicked_callback_list = []
            
            # 항목이 변경될 때 호출할 이벤트
            self.currentIndexChanged.connect(self.__on_current_index_changed)
            self.on_current_index_changed_callback_list = []
            
            self.setStyleSheet(f"""
                            QComboBox {{
                                background-color: {PyQtAddon.get_color("background_color")};
                                color: {PyQtAddon.get_color("content_text_color")};
                                border: 1px solid {PyQtAddon.get_color("line_color")}
                            }}
                            QComboBox QAbstractItemView {{
                                background: {PyQtAddon.get_color("background_color")};   /* 드롭다운 목록의 전체 배경색 변경 */
                                color: {PyQtAddon.get_color("content_text_color")};           /* 항목 텍스트 색상 변경 */
                                selection-background-color: {PyQtAddon.get_color("point_color_2")}; /* 항목 선택 시 배경색 변경 */
                                selection-color: {PyQtAddon.get_color("content_text_color")};    /* 항목 선택 시 텍스트 색상 변경 */
                            }}    
                            """)
            
        def register_on_current_index_changed_event(self, callback):
            self.on_current_index_changed_callback_list.append(callback)
            
        def register_on_clicked_event(self, callback):
            self.on_clicked_callback_list.append(callback)
            
        def showPopup(self):
            # 드롭다운 메뉴가 확장될 때 호출되는 메서드 (클릭 될 때 호출됨)
            # 현재 선택을 자동으로 첫 번째 항목으로 변경하지 않도록 유지
            do_popup = True
            
            for callback in self.on_clicked_callback_list:
                if callback: do_popup = callback()
                
            if do_popup is None or do_popup is True: # None : default
                super().showPopup()

        def __on_current_index_changed(self):
            self.selected_option = self.currentText()
            for callback in self.on_current_index_changed_callback_list:
                if callback: callback(self.selected_option)
        
    class CustomLineEdit(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            # 기본 스타일 시트 설정
            self.set_default_style()
            
            # 수정 완료 시 호출 이벤트 등록
            self.on_edit_end_callback_list = []
            # self.edit_finish_callback = edit_finish_callback
            self.editingFinished.connect(self.check_text_input)
            
            # 메서드 호출을 통한 수정 시 콜백 호출되는 것을 방지
            self.is_handling_editing = False

        def register_on_edit_end_event(self, callback):
            self.on_edit_end_callback_list.append(callback)
            
        def set_default_style(self):
            # 기본 색상
            self.setStyleSheet(f"""
                                background-color: {PyQtAddon.get_color("background_color")};
                                color: {PyQtAddon.get_color("content_text_color")};
                                border: 1px solid {PyQtAddon.get_color("line_color")}
                                """)

        def set_focus_style(self):
            # 포커스가 있을 때 색상
            self.setStyleSheet(f"""
                                background-color: {PyQtAddon.get_color("background_color")};
                                color: {PyQtAddon.get_color("content_text_color")};
                                border: 1px solid {PyQtAddon.get_color("point_color_2")}
                                """)

        def focusInEvent(self, event):
            # 포커스를 얻었을 때 스타일 변경
            self.set_focus_style()
            super().focusInEvent(event)

        def focusOutEvent(self, event):
            # 포커스를 잃었을 때 기본 스타일로 변경
            self.set_default_style()
            super().focusOutEvent(event)
            
        def set_text_in_line_edit(self, text):
            # 메서드로 text 수정할 때, editingFinished invoke 되지 않도록 하는 메서드
            self.blockSignals(True)
            self.setText(text)
            self.blockSignals(False)
        
        def check_text_input(self):
            # 프로그램적으로 텍스트 설정 중일 때는 호출하지 않음
            if self.is_handling_editing:
                return
            
            # 플래그 설정
            self.is_handling_editing = True
        
            for callback in self.on_edit_end_callback_list:
                if callback: callback(self.text())
                
            # 플래그 해제
            self.is_handling_editing = False
            
    class CallbackObject(QObject):
        data_received = pyqtSignal(bytes)  # 데이터를 수신했을 때 발생하는 시그널
          
    class SerialReaderThread(threading.Thread):
        data_received = pyqtSignal(bytes)
        
        def __init__(self, custom_COM_widget):
            super().__init__()
            self.custom_COM_widget = custom_COM_widget
            self._stop_event = threading.Event()  # 스레드를 중지하기 위한 이벤트 플래그
            self.callback_object = None
            
        def set_callback(self, callback_object):
            self.callback_object = callback_object

        def run(self):
            try:
                while not self._stop_event.is_set():  # 스레드 중지 이벤트가 설정될 때까지 실행
                    if self.custom_COM_widget.serial_handle.in_waiting > 0:  # 읽을 수 있는 데이터가 있을 때만 읽기
                        line = self.custom_COM_widget.serial_handle.read_until(self.custom_COM_widget.end_byte, self.custom_COM_widget.max_byte_length)
                        if self.callback_object:
                        # 콜백 객체를 통한 시그널 호출
                            self.callback_object.data_received.emit(line)
            finally:
                self.custom_COM_widget.serial_handle.close()  # 스레드 종료 시 시리얼 포트를 닫기

        def stop(self):
            self._stop_event.set()  # 스레드 중지 이벤트 설정
        
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 부모 위젯 저장
        self.parent = parent
        
        # 시리얼 핸들
        self.serial_handle = None
        
        # 현재 연결 중인 핸들
        self.connected_port_name = None
        
        # Encoding type 설정
        self.encoding_type = "DEC"
        
        # End byte 설정
        self.end_byte = bytes([255])
        
        # Max byte length 설정
        self.max_byte_length = 20
        
        # 연결 성공 이벤트
        self.on_connection_succeed_callback_list = []
        
        # 연결 실패 이벤트
        self.on_connection_failed_callback_list = []
        
        # 연결 종료 이벤트
        self.on_disconnected_callback_list = []
        
        # 데이터 수신 이벤트
        self.on_data_received_callback_list = []
        
        self.__init_ui()
        
    def __init_ui(self):
        # 레이아웃 설정
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 라벨 생성
        COM_dropdown_label = QLabel("COM port", self.parent)
        COM_dropdown_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        COM_dropdown_label.setStyleSheet(f"""color: {PyQtAddon.get_color("title_text_color")};""")
        
        # Connection state 보여줄 아이콘 생성
        self.connection_icon = self.CustomConnectionStateIcon(15, 15, self)
        
        # 라벨, connection state widget 합친 layout 생성
        label_layout = QHBoxLayout()
        label_widget = QWidget()
        label_widget.setLayout(label_layout)
        label_layout.addWidget(COM_dropdown_label)
        label_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        label_layout.addWidget(self.connection_icon)
        label_layout.setContentsMargins(0, 0, 0, 0)
        
        # 드랍다운 생성
        self.COM_dropdown = self.CustomComboBox(self.parent)
        self.COM_dropdown.register_on_clicked_event(self.__search_available_ports)
        
        # 보드레이트 선택 라벨 생성
        baud_rate_dropdown_label = QLabel("Baudrate", self.parent)
        baud_rate_dropdown_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        baud_rate_dropdown_label.setStyleSheet(f"""color: {PyQtAddon.get_color("title_text_color")};""")
        
        # 보드레이트 선택 드랍다운 생성
        self.baud_rate_dropdown = self.CustomComboBox(self.parent)
        self.baud_rate_dropdown.addItems(['300', '1200', '2400', '4800', '9600', '14400', '19200', '28800', '38400', '57600', '115200'])
        self.baud_rate_dropdown.setCurrentIndex(4) # 기본값 설정 : 9600
        self.baud_rate_dropdown.register_on_clicked_event(self.__prevent_baud_rate_change_under_connected_state)
        
        # 인코딩 타입 선택 라벨 생성
        encoding_type_dropdown_label = QLabel("Encoding type", self.parent)
        encoding_type_dropdown_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        encoding_type_dropdown_label.setStyleSheet(f"""color: {PyQtAddon.get_color("title_text_color")};""")
        
        # 인코딩 타입 선택 드랍다운 생성
        self.encoding_type_dropdown = self.CustomComboBox(self.parent)
        self.encoding_type_dropdown.addItems(['DEC', 'HEX', 'ASCII'])
        self.encoding_type_dropdown.setCurrentIndex(0) # 기본값 설정 : DEC
        self.encoding_type_dropdown.register_on_current_index_changed_event(self.__on_encoding_type_changed)
        
        # End byte 설정 라벨
        end_byte_edit_field_label = QLabel("End byte", self.parent)
        end_byte_edit_field_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        end_byte_edit_field_label.setStyleSheet(f"""color: {PyQtAddon.get_color("title_text_color")};""")
        
        # End byte 설정 edit field 생성
        self.end_byte_edit_field = self.CustomLineEdit(self.parent)
        self.end_byte_edit_field.register_on_edit_end_event(self.__on_end_byte_changed)
        self.end_byte_edit_field.setText('255')
        
        # Max byte 설정 라벨
        max_byte_length_edit_field_label = QLabel("Maximum byte length", self.parent)
        max_byte_length_edit_field_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        max_byte_length_edit_field_label.setStyleSheet(f"""color: {PyQtAddon.get_color("title_text_color")};""")
        
        # Max byte 설정 edit field 생성
        self.max_byte_length_edit_field = self.CustomLineEdit(self.parent)
        self.max_byte_length_edit_field.register_on_edit_end_event(self.__on_max_byte_length_changed)
        self.max_byte_length_edit_field.setText('20')
        
        # Connect 버튼 생성
        connect_button = QPushButton("Connect", self.parent)
        connect_button.clicked.connect(self.__connect_to_selected_port)
        connect_button.setStyleSheet(f"""
                                     QPushButton {{
                                         background-color: {PyQtAddon.get_color("point_color_1")};
                                         color: {PyQtAddon.get_color("content_text_color")};
                                         padding: 4px 8px;
                                         border-radius: 0px;
                                         border: none;
                                     }}
                                     QPushButton:hover {{
                                         background-color: {PyQtAddon.get_color("point_color_5")};
                                         border: none;
                                     }}
                                     """)
        
        # Connect 버튼 생성
        disconnect_button = QPushButton("Disconnect", self.parent)
        disconnect_button.clicked.connect(self.__disconnect_port)
        disconnect_button.setStyleSheet(f"""
                                        QPushButton {{
                                            background-color: {PyQtAddon.get_color("point_color_1")};
                                            color: {PyQtAddon.get_color("content_text_color")};
                                            padding: 4px 8px;
                                            border-radius: 0px;
                                            border: none;
                                        }}
                                        QPushButton:hover {{
                                            background-color: {PyQtAddon.get_color("point_color_5")};
                                            border: none;
                                        }}
                                        """)
        
        # UI 배치
        layout.addWidget(label_widget)
        layout.addWidget(self.COM_dropdown)
        layout.addWidget(baud_rate_dropdown_label)
        layout.addWidget(self.baud_rate_dropdown)
        layout.addWidget(encoding_type_dropdown_label)
        layout.addWidget(self.encoding_type_dropdown)
        layout.addWidget(end_byte_edit_field_label)
        layout.addWidget(self.end_byte_edit_field)
        layout.addWidget(max_byte_length_edit_field_label)
        layout.addWidget(self.max_byte_length_edit_field)
        layout.addWidget(connect_button)
        layout.addWidget(disconnect_button)
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
    def __on_encoding_type_changed(self, selected_option):
        self.encoding_type = selected_option
        
    def __on_end_byte_changed(self, end_byte_text):
        # 입력이 정수인 지 확인
        if end_byte_text.isdigit():
            end_byte_int = int(end_byte_text)
            # 0에서 255사이 값인 지 확인
            if end_byte_int >= 0 and end_byte_int <= 255:
                end_byte = bytes([end_byte_int])
                self.end_byte = end_byte
                self.end_byte_edit_field.set_text_in_line_edit(end_byte_text)
                return
            
        CustomMessageBox.warning(self.parent, "Warning", "잘못된 byte 값입니다 (0~255 값 필요).")
        self.end_byte_edit_field.set_text_in_line_edit(str(int(self.end_byte[0])))
        
    def __on_max_byte_length_changed(self, max_byte_length_text):
        # 입력이 정수인 지 확인
        if max_byte_length_text.isdigit():
            max_byte_length_int = int(max_byte_length_text)
            self.max_byte_length = max_byte_length_int
            
        CustomMessageBox.warning(self.parent, "Warning", "잘못된 값입니다 (정수 값 필요).")
        self.max_byte_edit_field.set_text_in_line_edit(str(self.max_byte_length))
        
    def __prevent_baud_rate_change_under_connected_state(self):
        current_baud_rate_index = self.baud_rate_dropdown.currentIndex()
        if self.serial_handle is not None:
            CustomMessageBox.warning(self.parent, "Warning", "연결 되어 있는 상태에서는 보드 레이트를 변경할 수 없습니다.")
            self.baud_rate_dropdown.setCurrentIndex(current_baud_rate_index)
            return False
        else:
            return True
        
    def __search_available_ports(self):
        # 현재 사용 가능한 시리얼 포트를 검색
        ports = serial.tools.list_ports.comports()
        available_ports = [port.device for port in ports]
        
        # 드랍다운의 항목으로 추가
        self.COM_dropdown.clear()
        self.COM_dropdown.addItems(available_ports)
    
    def __connect_to_selected_port(self):
        if self.serial_handle is not None:
            CustomMessageBox.warning(self.parent, "Warning", f"{self.connected_port_name} 포트가 이미 연결되어 있습니다.")
            return
        
        # 설정된 포트로 연결 시도
        # 주어진 값이 COM + (인수) 인 지 확인
        target_port = self.COM_dropdown.currentText()
        if not bool(re.match(r"^COM\d+$", target_port)):
            return
    
        try:
            # 특정 COM 포트에 연결
            self.serial_handle = serial.Serial(target_port, int(self.baud_rate_dropdown.currentText()), timeout=1)
            if self.serial_handle.is_open:
                # target name 업데이트
                self.connected_port_name = target_port
                
                # Icon 업데이트
                self.connection_icon.set_success_state()
                
                # 이벤트 invoke
                for callback in self.on_connection_succeed_callback_list:
                    if callback: callback()
                
                # Data 수신 이벤트 연결
                self.callback_object = self.CallbackObject()
                self.callback_object.data_received.connect(self.__on_data_received)
                
                self.serial_thread = self.SerialReaderThread(self)
                self.serial_thread.set_callback(self.callback_object)
                self.serial_thread.start()
                
        except serial.SerialException as e:
            # Icon 업데이트
            self.connection_icon.set_failed_state()
            
            # 이벤트 invoke
            for callback in self.on_connection_failed_callback_list:
                if callback: callback()
            
            CustomMessageBox.critical(self.parent, "Error", f"Failed to open serial port: {e}")
    
    def __disconnect_port(self):
        # 스레드 중지 요청 및 스레드 종료 대기
        if hasattr(self, 'serial_thread') and self.serial_thread.is_alive():
            self.serial_thread.stop()
            self.serial_thread.join()  # 스레드가 안전하게 종료될 때까지 대기
            
            # 인스턴스 초기화
            self.serial_handle = None
            self.connected_port_name = None
            
            # Icon 업데이트
            self.connection_icon.set_idle_state()
            
            # 이벤트 invoke
            for callback in self.on_disconnected_callback_list:
                if callback: callback()

    def __on_data_received(self, line):
        if self.serial_handle is None:
            return
        
        data = list(range(len(line)-1))
        if self.encoding_type_dropdown.currentText() == 'DEC':
            for i in range(len(data)):
                data[i] = int(line[i])
                
        elif self.encoding_type_dropdown.currentText() == 'HEX':
            for i in range(len(data)):
                data[i] = hex(line[i])
                
        elif self.encoding_type_dropdown.currentText() == 'ASCII':
            for i in range(len(data)):
                if 32 <= line[0] <= 126:
                    data[i] = chr(line[i])
                else:
                    data[i] = repr(chr(line[i]))
            
        for callback in self.on_data_received_callback_list:
            if callback: callback(data)
       
    def disconnect(self):
        self.__disconnect_port()  
       
    def register_on_connection_succeed_event(self, callback):
        self.on_connection_succeed_callback_list.append(callback)
        
    def register_on_connection_failed_event(self, callback):
        self.on_connection_failed_callback_list.append(callback)
        
    def register_on_disconnected_event(self, callback):
        self.on_disconnected_callback_list.append(callback)
        
    def register_on_data_received_event(self, callback):
        self.on_data_received_callback_list.append(callback)
   
# CustomAnalogChannelWidget : 연결된 COM 포트의 사용/미사용 아날로그 채널 설정
class CustomAnalogChannelWidget(QWidget):
    def __init__(self, COM_widget, parent=None):
        super().__init__(parent)
        
        # 부모 객체 저장
        self.parent = parent
        
        # 이벤트 생성
        self.on_selected_channel_changed_callback_list = []
        self.on_data_received_callback_list = []
        
        # COM 연결 위젯 저장
        self.COM_widget = COM_widget
        self.COM_widget.register_on_data_received_event(self.__on_data_received)
        self.COM_widget.register_on_disconnected_event(self.__clear_current_channel)
        self.COM_widget.register_on_connection_failed_event(self.__clear_current_channel)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Channel select grid widget 생성
        self.channel_select_widget = CustomGridKeywordMultiClickWidget(parent=self.parent)
        self.channel_select_widget.register_on_clicked_event(self.__on_analog_channel_changed)
        self.display_channel = []
        self.selected_channel = []
        
        # UI 배치
        layout.addWidget(self.channel_select_widget)
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def register_on_selected_channel_changed_event(self, callback):
        self.on_selected_channel_changed_callback_list.append(callback)
        
    def register_on_data_received_event(self, callback):
        self.on_data_received_callback_list.append(callback)
        
    def __clear_current_channel(self):
        self.display_channel.clear()
        self.channel_select_widget.clear()
        
    def __on_analog_channel_changed(self, channel):
        self.selected_channel = channel
        for callback in self.on_selected_channel_changed_callback_list:
            if callback: callback(channel)
        
    def __on_data_received(self, packet):
        # DEC, HEX의 경우 255가 최대 값이기 때문에 1024를 표현하기 위해 두 자리를 사용
        if self.COM_widget.encoding_type == "DEC" or self.COM_widget.encoding_type == "HEX":
            channel_length = int(len(packet)/2)
        else:
            channel_length = len(packet)
            
        if channel_length != len(self.display_channel):  
            self.display_channel = list(range(channel_length))
            # 리스트 문자열로 변환
            self.display_channel = [f'A{i}' for i in self.display_channel]
            # Analog input channel 생성
            self.channel_select_widget.set_keywords(self.display_channel)
            
        data = {}
        if self.COM_widget.encoding_type == "DEC":
            for i in range(channel_length):
                if f'A{i}' in self.selected_channel:
                    data[f'A{i}'] = packet[2*i]*254+packet[2*i+1]
                    # data.append(packet[2*i]*254+packet[2*i+1])
                    
        for callback in self.on_data_received_callback_list:
            if callback: callback(data)
   
# CustomRecordControlWidget : 데이터 record widget
class CustomRecordControlWidget(QWidget):
    def __init__(self, file_system_viewer, analog_channel_widget, loading_icon_size, button_size, parent=None):
        super().__init__(parent)
        
        self.parent = parent
        
        # 이벤트 등록
        self.file_system_viewer = file_system_viewer
        self.file_system_viewer.register_on_directory_changed_event(self.__on_directory_changed)
        
        # 아날로그 채널 위젯 저장
        self.analog_channel_widget = analog_channel_widget
        self.analog_channel_widget.register_on_data_received_event(self.__on_data_received)
        
        # Record 데이터 생성
        self.target_directory = file_system_viewer.target_directory
        self.do_record = False
        self.record_data = []
        
        self.__init_ui(loading_icon_size, button_size)
        
    def __init_ui(self, loading_icon_size, button_size):
        # 레이아웃 설정
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.record_start_button = QPushButton()
        self.record_start_button.setFixedSize(button_size, button_size)
        self.record_start_button.clicked.connect(self.__start_record)
        PyQtAddon.set_button_icon(self.record_start_button, "record_icon.svg", button_size, button_size)
        self.record_start_button.setStyleSheet(f"""
                                               QPushButton {{
                                                   background-color: transparent;
                                                   border: 1px solid {PyQtAddon.get_color("content_line_color")};
                                                   }}
                                               QPushButton:hover {{
                                                   background-color: {PyQtAddon.get_color("point_color_1")}
                                               }}
                                               """)
        
        self.record_pause_button = QPushButton()
        self.record_pause_button = QPushButton()
        self.record_pause_button.setFixedSize(button_size, button_size)
        self.record_pause_button.clicked.connect(self.__pause_record)
        PyQtAddon.set_button_icon(self.record_pause_button, "pause_icon.svg", button_size, button_size)
        self.record_pause_button.setStyleSheet(f"""
                                               QPushButton {{
                                                   background-color: transparent;
                                                   border: 1px solid {PyQtAddon.get_color("content_line_color")};
                                                   }}
                                               QPushButton:hover {{
                                                   background-color: {PyQtAddon.get_color("point_color_1")}
                                               }}
                                               """)
        
        self.record_stop_button = QPushButton()
        self.record_stop_button.setFixedSize(button_size, button_size)
        self.record_stop_button.clicked.connect(self.__stop_record)
        PyQtAddon.set_button_icon(self.record_stop_button, "stop_icon.svg", button_size, button_size)
        self.record_stop_button.setStyleSheet(f"""
                                              QPushButton {{
                                                  background-color: transparent;
                                                  border: 1px solid {PyQtAddon.get_color("content_line_color")};
                                                  }}
                                              QPushButton:hover {{
                                                  background-color: {PyQtAddon.get_color("point_color_1")}
                                              }}
                                              """)
        
        # 버튼 레이아웃 생성 후 버튼 배치
        button_layout = QHBoxLayout()
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        button_layout.addWidget(self.record_start_button)
        button_layout.addWidget(self.record_pause_button)
        button_layout.addWidget(self.record_stop_button)
        
        
        # "작업 중" 애니메이션 GIF 추가
        self.loading_label = QLabel(self)
        self.loading_icon = QMovie(PyQtAddon.convert_url(os.path.join(icons_directory, "loading_icon.gif")))  # 로딩 애니메이션 GIF 파일 경로
        self.loading_icon.setScaledSize(QSize(loading_icon_size, loading_icon_size)) # QMovie의 크기를 특정 픽셀 크기로 설정
        
        # 레이아웃에 위젯 추가
        layout.addWidget(button_widget)
        layout.addWidget(self.loading_label, alignment=Qt.AlignCenter)
        
    def __on_directory_changed(self, target_directory):
        self.target_directory = target_directory
        
    def __on_data_received(self, data):
        if self.do_record:
            self.record_data.append(data)
        
    def __start_record(self):
        if self.do_record:
            CustomMessageBox.warning(self.parent, "Warning", "이전 녹화가 진행중 입니다.")
            return
        
        self.record_data.clear()
        self.loading_label.setMovie(self.loading_icon)
        self.loading_icon.start()
        self.do_record = True
        
    def __pause_record(self):
        CustomMessageBox.warning(self.parent, "Warning", "기능이 아직 구현되지 않았습니다.")
      
    def __data_export_process(self):
        # 유저로부터 파일 이름을 입력받음
        file_name, ok = CustomInputDialog.getText(self.parent, 'File Name', '파일명 입력 : ')
        
        if ok:
            if file_name:
                # 파일 이름에 확장자가 없으면 .csv 추가
                if not file_name.endswith('.csv'):
                    file_name += ".csv"
                    
                # 파일 경로 생성
                file_path = os.path.join(self.target_directory, file_name)
                
                # 파일이 이미 존재하는지 확인
                if os.path.exists(file_path):
                    reply = CustomMessageBox.question(self.parent, 'Warning', 
                                                      '해당 파일이 이미 존재합니다. 계속 진행하시겠습니까?', 
                                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    
                    if reply == QMessageBox.No:
                        self.__data_export_process()
                        
                    else:
                        # 2차원 배열을 DataFrame으로 변환
                        df = pd.DataFrame(self.record_data)
                        # CSV파일로 출력
                        export_csv_file(file_path, df, index=True, header=True)
                        CustomMessageBox.information(self, 'Information', f"파일이 저장되었습니다 : {file_name}")
                
                else:
                    # 2차원 배열을 DataFrame으로 변환
                    df = pd.DataFrame(self.record_data)
                    # CSV파일로 출력
                    export_csv_file(file_path, df, index=True, header=True)
                    CustomMessageBox.information(self, 'Information', f"파일이 저장되었습니다 : {file_name}")
            
            else:
                CustomMessageBox.critical(self, 'Error', '파일명이 입력되지 않았습니다.')
                self.__data_export_process()
        else:
            CustomMessageBox.critical(self, 'Error', '파일 저장이 취소 되었습니다.')
        
    def __stop_record(self):
        if not self.do_record:
            CustomMessageBox.warning(self.parent, "Warning", "데이터 녹화가 시작되지 않았습니다.")
            return
        
        self.do_record = False
        
        self.loading_icon.stop()
        self.loading_label.clear()
        
        # 파일 저장 process 시작
        self.__data_export_process()
        
        # 저장된 데이터 초기화
        self.record_data.clear()