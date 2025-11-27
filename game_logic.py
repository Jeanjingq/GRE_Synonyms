import random
from typing import List, Tuple, Optional, Set
from data_handler import DataHandler

class GameLogic:
    """游戏核心逻辑"""
    
    def __init__(self, data_handler: DataHandler, pairs_count: int = 5):
        self.data_handler = data_handler
        self.pairs_count = pairs_count
        self.left_words: List[str] = []
        self.right_words: List[str] = []
        self.word_pairs: List[Tuple[str, str]] = []
        self.matched_indices: set = set()  # 已匹配的索引
        self.score = 0
        self.attempts = 0
        self.left_to_right_mapping: dict = {}  # {左索引: 右索引}
        
        # 新增：累积配对计数
        self.consecutive_matches = 0  # 连续配对成功的次数
        self.match_threshold = 3      # 触发更新的阈值
        
    def initialize_game(self):
        """初始化游戏，生成新的单词对"""
        self.word_pairs = self.data_handler.get_random_pairs(self.pairs_count)
        self.left_words = [pair[0] for pair in self.word_pairs]
        self.right_words = [pair[1] for pair in self.word_pairs]
        
        # 打乱右边
        random.shuffle(self.right_words)
        
        # 建立映射
        self._build_mapping()
        
        self.matched_indices.clear()
        self.consecutive_matches = 0
    
    def _build_mapping(self):
        """建立左右索引映射关系"""
        self.left_to_right_mapping = {}
        for i in range(len(self.word_pairs)):
            for j, right_word in enumerate(self.right_words):
                if right_word == self.word_pairs[i][1]:
                    self.left_to_right_mapping[i] = j
                    break
    
    def check_pair(self, left_index: int, right_index: int) -> Tuple[bool, bool]:
        """
        检查配对是否正确
        返回: (是否正确, 是否触发批量更新)
        """
        self.attempts += 1
        
        # 检查索引是否已经匹配
        if left_index in self.matched_indices:
            return False, False
        
        left_word = self.left_words[left_index]
        right_word = self.right_words[right_index]
        
        is_correct = self.data_handler.check_match(left_word, right_word)
        
        if is_correct:
            self.score += 1
            self.matched_indices.add(left_index)
            self.consecutive_matches += 1
            
            # 检查是否达到阈值
            if self.consecutive_matches >= self.match_threshold:
                return True, True  # 正确且触发更新
        
        return is_correct, False
    
    def batch_update_words(self) -> List[Tuple[int, int]]:
        """
        批量更新所有已匹配的单词
        返回: [(左索引, 右索引), ...] 需要更新的位置列表
        """
        # 获取所有已匹配的索引
        matched_left_indices = list(self.matched_indices)
        
        if not matched_left_indices:
            return []
        
        # 记录需要更新的位置
        update_positions = []
        
        # 获取新的单词对
        new_pairs = self.data_handler.get_random_pairs(len(matched_left_indices))
        
        # 收集所有右边需要更新的索引
        right_indices_to_update = [self.left_to_right_mapping[idx] 
                                   for idx in matched_left_indices]
        
        # 更新单词
        for i, left_idx in enumerate(matched_left_indices):
            new_pair = new_pairs[i]
            right_idx = self.left_to_right_mapping[left_idx]
            
            # 更新左边
            self.left_words[left_idx] = new_pair[0]
            
            # 暂存新的同义词（先不放到right_words中）
            self.word_pairs[left_idx] = new_pair
            
            update_positions.append((left_idx, right_idx))
        
        # 重新分配右边的同义词位置（打乱映射）
        new_synonyms = [self.word_pairs[idx][1] for idx in matched_left_indices]
        
        # 打乱新同义词的顺序
        random.shuffle(new_synonyms)
        
        # 更新右边单词到对应位置
        for i, right_idx in enumerate(right_indices_to_update):
            self.right_words[right_idx] = new_synonyms[i]
        
        # 重新建立映射（确保左右不是原来的对应关系）
        self._rebuild_mapping_avoid_same(matched_left_indices)
        
        # 清空已匹配集合和计数器
        self.matched_indices.clear()
        self.consecutive_matches = 0
        
        return update_positions
    
    def _rebuild_mapping_avoid_same(self, updated_left_indices: List[int]):
        """
        重新建立映射，确保更新的单词不会和原位置对应
        """
        # 获取需要重新映射的右边索引
        right_indices = [self.left_to_right_mapping[left_idx] 
                        for left_idx in updated_left_indices]
        
        # 打乱右边索引顺序
        shuffled_right_indices = right_indices.copy()
        
        # 确保至少有一个位置改变
        max_attempts = 100
        for _ in range(max_attempts):
            random.shuffle(shuffled_right_indices)
            
            # 检查是否所有位置都改变了
            all_different = all(
                self.left_to_right_mapping[left_idx] != new_right_idx
                for left_idx, new_right_idx in zip(updated_left_indices, shuffled_right_indices)
            )
            
            if all_different:
                break
        
        # 更新映射
        for left_idx, new_right_idx in zip(updated_left_indices, shuffled_right_indices):
            self.left_to_right_mapping[left_idx] = new_right_idx
        
        # 更新右边单词位置
        temp_synonyms = [self.word_pairs[left_idx][1] for left_idx in updated_left_indices]
        for i, right_idx in enumerate(shuffled_right_indices):
            self.right_words[right_idx] = temp_synonyms[i]
    
    def get_accuracy(self) -> float:
        """获取正确率"""
        if self.attempts == 0:
            return 0.0
        return (self.score / self.attempts) * 100
    
    def is_index_matched(self, index: int) -> bool:
        """检查索引是否已匹配"""
        return index in self.matched_indices
    
    def get_match_progress(self) -> int:
        """获取当前连续配对进度"""
        return self.consecutive_matches