import copy
import sys
import time

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QCheckBox
from PySide2.QtGui import QPainter, QColor, QBrush, QPen
from PySide2.QtCore import Qt, Signal, Slot, QTimer
from MCTS import MCTS, GameState


class ReversiGame(QWidget):
    # 定义一个信号
    my_signal = Signal()

    def __init__(self):
        super().__init__()

        # 主体：
        self.game = GameState()
        self.result = 0  # 1表示人赢，2表示机器赢，-1为平局

        # 设置界面大小
        self.setFixedSize(950, 720)
        self.setWindowTitle("Reversi")

        # 初始化棋盘尺寸
        self.board_size = int(self.height() * 0.8)
        self.square_size = self.board_size // 8

        # 添加Restart按钮
        self.restart_button = QPushButton("Restart", self)
        self.restart_button.setGeometry(700, 200, 180, 50)
        self.restart_button.clicked.connect(self.restart)

        # 添加显示黑子个数与白子个数的label
        self.piece_count_label = QLabel(self)
        self.piece_count_label.setGeometry(670, 300, 250, 80)
        self.piece_count_label.setAlignment(Qt.AlignCenter)
        self.piece_count_label.setStyleSheet("QLabel{color: rgb(65,105,255);font-size: 20px; font-weight: bold;}")
        self.update_piece_count_label()

        # 显示输赢：
        self.win_label = QLabel("", self)
        self.win_label.setGeometry(700, 400, 180, 50)
        self.win_label.setAlignment(Qt.AlignCenter)
        self.win_label.setStyleSheet("QLabel{color: rgb(255,97,3);font-size: 25px; font-weight: bold;}")

        # 引导复选框:
        # 创建复选框并设置文本
        self.show_guidance = False
        self.guide_checkbox = QCheckBox("Novice Guidance", self)
        self.guide_checkbox.setGeometry(720, 100, 180, 50)
        # 将 stateChanged 信号与槽函数关联
        self.guide_checkbox.stateChanged.connect(self.toggle_guide)

        # 自定义信号链接
        # self.my_signal.connect(self.AI_play)
        self.timer=QtCore.QTimer(self)
        self.timer.timeout.connect(self.AI_play)
        self.timer.start(1)


    def toggle_guide(self, state):
        if state == Qt.Checked:
            self.show_guidance = True
        else:
            self.show_guidance = False
        self.update()

    def paintEvent(self, event):
        # 绘制棋盘
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 白色填充
        painter.fillRect(self.rect(), Qt.white)
        offset = 50  # 设置偏移量

        pen = QPen()
        pen.setWidth(2)
        painter.setPen(pen)
        # 绘制网格
        for i in range(9):
            painter.drawLine(offset + self.square_size * i, offset, offset + self.square_size * i,
                             offset + self.board_size)
            painter.drawLine(offset, offset + self.square_size * i, offset + self.board_size,
                             offset + self.square_size * i)

        # 绘制引导
        if self.show_guidance and self.game.current_player == 1:
            painter.setBrush(QBrush(Qt.gray, Qt.Dense4Pattern))  # 设置浅灰色和填充样式
            for i in range(8):
                for j in range(8):
                    if self.game.check_valid(j, i):  # 检查是否可以在该位置落子
                        # 绘制浅灰色圆圈
                        painter.drawRect(offset + j * self.square_size, offset + i * self.square_size, self.square_size,
                                         self.square_size)
        # 绘制棋子
        for i in range(8):
            for j in range(8):
                if self.game.board[i][j] == 1:  # 黑子
                    painter.setBrush(QBrush(Qt.black))
                elif self.game.board[i][j] == 2:  # 白子
                    painter.setBrush(QBrush(Qt.white))
                else:
                    continue

                painter.drawEllipse(offset + j * self.square_size + 4, offset + i * self.square_size + 4,
                                    self.square_size - 8,
                                    self.square_size - 8)
        # 显示输赢：
        if self.game.is_terminal():
            # 计算黑子和白子的数量
            black_count = sum(row.count(1) for row in self.game.board)
            white_count = sum(row.count(2) for row in self.game.board)
            if black_count > white_count:
                self.result = 1
            elif black_count == white_count:
                self.result = -1
            else:
                self.result = 2
        if self.result == 1:
            self.win_label.setText("YOU WIN!!!")
        elif self.result == 2:
            self.win_label.setText("YOU LOSE!!!")
        elif self.result == -1:
            self.win_label.setText("-TIE-")
        else:
            self.win_label.setText("")

    def restart(self):
        self.game.restart()
        self.result = 0
        # 更新界面
        self.update_piece_count_label()
        self.update()

    def update_piece_count_label(self):
        # 计算黑子和白子的数量
        black_count = sum(row.count(1) for row in self.game.board)
        white_count = sum(row.count(2) for row in self.game.board)

        # 更新label显示
        self.piece_count_label.setText(f"Black: {black_count} | White: {white_count}")

    @Slot()
    def mousePressEvent(self, event):
        if self.game.current_player == 2:
            # self.my_signal.emit()  # 发出信号
            return
        # 人走：
        offset = 50  # 设置偏移量
        # 获取点击位置
        x, y = (event.x() - offset) // self.square_size, (event.y() - offset) // self.square_size
        if x < 0 or x > 7 or y < 0 or y > 7:
            # self.my_signal.emit()  # 发出信号
            return
        if not self.game.check_valid(x, y):
            # self.my_signal.emit()  # 发出信号
            return

        # 落子并交换棋权
        self.game.apply_move((x, y))

        # 更新棋子数量显示
        self.update_piece_count_label()
        # 更新界面
        self.repaint()

        # self.my_signal.emit()  # 发出信号

    @Slot()
    def AI_play(self):
        if self.game.current_player == 1:
            return
        if self.game.is_blocked():
            self.game.exchange()
        # ai走
        ai_move = self.AI_move()
        self.game.apply_move(ai_move)
        # 更新棋子数量显示
        self.update_piece_count_label()
        self.repaint()
        if self.game.is_blocked():
            self.game.exchange()

    # 返回AI的操作
    def AI_move(self):
        copy_game_state = copy.deepcopy(self.game)
        mcts = MCTS(copy_game_state, iterations=10000)
        return mcts.search()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    reversi_game = ReversiGame()
    reversi_game.show()
    sys.exit(app.exec_())
