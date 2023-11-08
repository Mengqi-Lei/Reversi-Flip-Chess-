import random
import math


class GameState:
    def __init__(self):
        # 初始化棋盘
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        # 设置初始棋子
        self.board[3][3] = 1
        self.board[3][4] = 2
        self.board[4][3] = 2
        self.board[4][4] = 1
        self.current_player = 1
        # 设置一个tag标记输赢
        self.result=0 # 0表示没有决定胜负，1表示人赢，-1白送hi

    def restart(self):
        # 重置棋盘
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.board[3][3] = 1
        self.board[3][4] = 2
        self.board[4][3] = 2
        self.board[4][4] = 1
        # 重置棋权
        self.current_player = 1

    def get_valid_moves(self):
        valid_moves = []
        for i in range(8):
            for j in range(8):
                if self.check_valid(j, i):
                    valid_moves.append((j, i))
        return valid_moves

    def check_valid(self, x, y):
        if self.board[y][x] != 0:  # 如果(x, y)位置已经有棋子，返回False
            return False

        # 检查8个方向是否可以翻转对手的棋子
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        opponent = 3 - self.current_player  # 对手的棋子颜色（1为黑子，2为白子）

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny< 8 and self.board[ny][nx] == opponent:
                # 在(x, y)位置的下一个位置有对手的棋子
                nx += dx
                ny += dy
                # 沿着当前方向继续检查
                while 0 <= nx < 8 and 0 <= ny < 8:
                    if self.board[ny][nx] == 0:
                        # 遇到空白位置，跳出循环
                        break
                    elif self.board[ny][nx] == self.current_player:
                        # 遇到自己的棋子，说明在这个方向上可以翻转对手的棋子，返回True
                        return True

                    nx += dx
                    ny += dy

        # 在所有方向上都无法翻转对手的棋子，返回False
        return False

    # 结束时判断哪一方获胜
    def get_result(self):
        black_count = sum(row.count(1) for row in self.board)
        white_count = sum(row.count(2) for row in self.board)

        if black_count == white_count:
            return 0
        elif black_count > white_count:
            return 1 if self.current_player == 1 else -1
        else:
            return 1 if self.current_player == 2 else -1


    # 计算下一棋盘状态，返回新的状态
    def apply_move(self, move):
        if not move:
            self.exchange()
            return
        x, y = move
        self.board[y][x] = self.current_player  # 将棋子放置在(x, y)位置
        opponent = 3 - self.current_player  # 对手的棋子颜色（1为黑子，2为白子）

        # 检查8个方向是否可以翻转对手的棋子
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8 and self.board[ny][nx] == opponent:
                # 在(x, y)位置的下一个位置有对手的棋子
                nx += dx
                ny += dy
                # 沿着当前方向继续检查
                while 0 <= nx < 8 and 0 <= ny < 8:
                    if self.board[ny][nx] == 0:
                        # 遇到空白位置，跳出循环
                        break
                    elif self.board[ny][nx] == self.current_player:
                        # 遇到自己的棋子，翻转这个方向上的对手棋子
                        nx -= dx
                        ny -= dy
                        while not (nx == x and ny == y):
                            self.board[ny][nx] = self.current_player
                            nx -= dx
                            ny -= dy
                        break

                    nx += dx
                    ny += dy

        # 更换玩家
        self.current_player = opponent
        return self

    def is_terminal(self):
        # 检查当前玩家是否有有效落子位置
        if self.get_valid_moves():
            return False

        # 更换玩家
        self.current_player = 3 - self.current_player

        # 检查对手是否有有效落子位置
        if self.get_valid_moves():
            self.current_player = 3 - self.current_player
            return False

        # 如果双方都无法进行有效落子，游戏结束
        return True

    def exchange(self):
        self.current_player=3-self.current_player

    # 检查当前状态是不是当前player没有可以落子的地方
    def is_blocked(self):
        if self.get_valid_moves():
            return False
        return True





class MCTS:
    def __init__(self, game_state, iterations=1000):
        self.game_state = game_state
        self.iterations = iterations

    def search(self):
        # 定义树节点类
        class TreeNode:
            def __init__(self, parent, move):
                self.parent = parent
                self.move = move
                self.children = []
                self.wins = 0
                self.visits = 0

        # 蒙特卡洛树搜索过程
        def mcts(tree_node, game_state):
            if game_state.is_blocked():
                # print(game_state.board)
                return game_state.get_result()

            if not tree_node.children:
                for move in game_state.get_valid_moves():
                    child = TreeNode(tree_node, move)
                    tree_node.children.append(child)

            child = select(tree_node)
            next_state = game_state.apply_move(child.move)
            result = mcts(child, next_state)
            update(child, result)
            return -result

        def select(tree_node):
            best_child = None
            best_uct = -math.inf

            for child in tree_node.children:
                if child.visits == 0:
                    uct = math.inf
                else:
                    uct = child.wins / child.visits + math.sqrt(2 * math.log(tree_node.visits) / child.visits)

                if uct > best_uct:
                    best_uct = uct
                    best_child = child

            return best_child

        def update(tree_node, result):
            tree_node.visits += 1
            tree_node.wins += result

        # 执行MCTS
        root = TreeNode(None, None)

        for _ in range(self.iterations):
            mcts(root,self.game_state)
        # 选择具有最高访问次数的子节点
        if not root.children:
            return None
        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.move




