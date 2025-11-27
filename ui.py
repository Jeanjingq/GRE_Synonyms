import tkinter as tk
from tkinter import messagebox, filedialog
from game_logic import GameLogic
from data_handler import DataHandler

class SynonymGameUI:
    """游戏界面控制器"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GRE同义词配对练习")
        self.root.geometry("800x600")
        
        self.data_handler = None
        self.game_logic = None
        
        self.left_buttons = []
        self.right_buttons = []
        self.selected_left = None
        self.selected_right = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面布局"""
        # 顶部信息栏
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)
        
        self.score_label = tk.Label(info_frame, text="得分: 0", font=("Arial", 23))
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        self.accuracy_label = tk.Label(info_frame, text="正确率: 0%", font=("Arial", 23))
        self.accuracy_label.pack(side=tk.LEFT, padx=20)
                
        # 加载文件提示标签
        load_hint_label = tk.Label(info_frame, text="点击此处加载单词本：", 
                                   font=("Arial", 12))
        load_hint_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # 加载文件按钮
        load_btn = tk.Button(info_frame, text="加载Excel文件", command=self.load_file, 
                            font=("Arial", 12), bg="#4CAF50", fg="white")
        load_btn.pack(side=tk.LEFT, padx=20)
        
        # 主游戏区域
        game_frame = tk.Frame(self.root)
        game_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=20)
        
        # 左列
        left_frame = tk.Frame(game_frame)
        left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=20)
        
        tk.Label(left_frame, text="单词", font=("Arial", 16, "bold")).pack(pady=10)
        
        for i in range(5):
            btn = tk.Button(left_frame, text="", font=("Arial", 14), 
                          width=20, height=2, state=tk.DISABLED,
                          command=lambda idx=i: self.select_left(idx))
            btn.pack(pady=10)
            self.left_buttons.append(btn)
        
        # 右列
        right_frame = tk.Frame(game_frame)
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=20)
        
        tk.Label(right_frame, text="同义词", font=("Arial", 16, "bold")).pack(pady=10)
        
        for i in range(5):
            btn = tk.Button(right_frame, text="", font=("Arial", 14), 
                          width=25, height=2, state=tk.DISABLED,
                          command=lambda idx=i: self.select_right(idx))
            btn.pack(pady=10)
            self.right_buttons.append(btn)
        
        # 提示信息（增大字体）
        self.message_label = tk.Label(self.root, text="请先加载Excel文件", 
                                     font=("Arial", 25, "bold"), fg="white")
        self.message_label.pack(pady=20)
    
    def load_file(self):
        """加载Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        if not file_path:
            return
        
        self.data_handler = DataHandler(file_path)
        if self.data_handler.load_data():
            self.game_logic = GameLogic(self.data_handler)
            self.start_game()
        else:
            messagebox.showerror("错误", "加载文件失败，请检查文件格式")
    
    def start_game(self):
        """开始游戏"""
        self.game_logic.initialize_game()
        self.update_display()
        self.enable_buttons()
        self.message_label.config(text="请配对单词和同义词", fg="white")
    
    def update_display(self):
        """更新显示的单词"""
        for i in range(5):
            self.left_buttons[i].config(
                text=self.game_logic.left_words[i], 
                state=tk.NORMAL, 
                bg="SystemButtonFace"
            )
            self.right_buttons[i].config(
                text=self.game_logic.right_words[i], 
                state=tk.NORMAL, 
                bg="SystemButtonFace"
            )
        
        self.update_score()
    
    def update_score(self):
        """更新得分显示"""
        self.score_label.config(text=f"得分: {self.game_logic.score}")
        self.accuracy_label.config(text=f"正确率: {self.game_logic.get_accuracy():.1f}%")
    
    def enable_buttons(self):
        """启用所有未匹配的按钮"""
        for i in range(5):
            if not self.game_logic.is_index_matched(i):
                self.left_buttons[i].config(state=tk.NORMAL)
                self.right_buttons[i].config(state=tk.NORMAL)
    
    def select_left(self, index):
        """选择左边的单词"""
        if self.game_logic.is_index_matched(index):
            return
        
        # 取消之前的选择
        if self.selected_left is not None:
            if not self.game_logic.is_index_matched(self.selected_left):
                self.left_buttons[self.selected_left].config(bg="SystemButtonFace")
        
        self.selected_left = index
        self.left_buttons[index].config(bg="darkgray")
        
        # 如果两边都选了，检查配对
        if self.selected_right is not None:
            self.check_match()
    
    def select_right(self, index):
        """选择右边的单词"""
        # 取消之前的选择
        if self.selected_right is not None:
            self.right_buttons[self.selected_right].config(bg="SystemButtonFace")
        
        self.selected_right = index
        self.right_buttons[index].config(bg="darkgray")
        
        # 如果两边都选了，检查配对
        if self.selected_left is not None:
            self.check_match()
    
    def check_match(self):
        """检查配对是否正确"""
        left_idx = self.selected_left
        right_idx = self.selected_right
        
        is_correct, should_update = self.game_logic.check_pair(left_idx, right_idx)
        
        if is_correct:
            # 正确配对 - 单词消失（变为空白且禁用）
            self.left_buttons[left_idx].config(text="", state=tk.DISABLED, bg="lightgreen")
            self.right_buttons[right_idx].config(text="", state=tk.DISABLED, bg="lightgreen")
            
            if should_update:
                # 达到3对，触发批量更新
                self.message_label.config(text="🎉 太棒了！更新单词...", fg="green")
                self.root.after(800, self.perform_batch_update)
            else:
                # 还未达到3对
                self.message_label.config(text="✓ 正确！", fg="green")
        else:
            # 错误配对
            self.left_buttons[left_idx].config(bg="lightcoral")
            self.right_buttons[right_idx].config(bg="lightcoral")
            self.message_label.config(text="✗ 错误，请重试", fg="red")
            
            # 短暂延时后恢复
            self.root.after(500, self.reset_selection)
        
        self.update_score()
        
        # 清除选择状态
        self.selected_left = None
        self.selected_right = None
    
    def perform_batch_update(self):
        """执行批量更新"""
        update_positions = self.game_logic.batch_update_words()
        
        # 只更新已匹配位置的单词显示
        for left_idx, right_idx in update_positions:
            self.left_buttons[left_idx].config(
                text=self.game_logic.left_words[left_idx],
                state=tk.NORMAL,
                bg="SystemButtonFace"
            )
            self.right_buttons[right_idx].config(
                text=self.game_logic.right_words[right_idx],
                state=tk.NORMAL,
                bg="SystemButtonFace"
            )
        
        self.update_score()
        self.message_label.config(text="✨ 单词已更新，继续加油！", fg="white")
    
    def reset_selection(self):
        """重置选择（错误配对后）"""
        if self.selected_left is not None:
            self.left_buttons[self.selected_left].config(bg="SystemButtonFace")
        if self.selected_right is not None:
            self.right_buttons[self.selected_right].config(bg="SystemButtonFace")
        
        self.selected_left = None
        self.selected_right = None
        self.message_label.config(text="请重新配对", fg="white")
    
    def run(self):
        """运行应用"""
        self.root.mainloop()