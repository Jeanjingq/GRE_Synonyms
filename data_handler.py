import pandas as pd
import random
from typing import Dict, List, Tuple

class DataHandler:
    """处理Excel数据的读取和管理"""
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.word_dict: Dict[str, List[str]] = {}
        self.all_words: List[str] = []
        
    def load_data(self) -> bool:
        """
        从Excel加载数据
        返回是否成功加载
        """
        try:
            df = pd.read_excel(self.excel_path)
            
            # 检查必需的列
            if 'word' not in df.columns or 'synonym' not in df.columns:
                print("错误：Excel文件必须包含 'word' 和 'synonym' 列")
                return False
            
            # 处理数据
            for _, row in df.iterrows():
                word = str(row['word']).strip()
                synonyms_str = str(row['synonym']).strip()
                
                # 分割同义词（用逗号分隔）
                synonyms = [s.strip() for s in synonyms_str.split(',') if s.strip()]
                
                if word and synonyms:
                    self.word_dict[word] = synonyms
                    self.all_words.append(word)
            
            print(f"成功加载 {len(self.word_dict)} 个单词")
            return True
            
        except FileNotFoundError:
            print(f"错误：找不到文件 {self.excel_path}")
            return False
        except Exception as e:
            print(f"加载数据时出错：{e}")
            return False
    
    def get_random_pairs(self, count: int = 5) -> List[Tuple[str, str]]:
        """
        随机获取指定数量的单词-同义词对
        返回: [(word, synonym), ...]
        """
        if len(self.all_words) < count:
            count = len(self.all_words)
        
        pairs = []
        selected_words = random.sample(self.all_words, count)
        
        for word in selected_words:
            # 从该单词的同义词列表中随机选一个
            synonym = random.choice(self.word_dict[word])
            pairs.append((word, synonym))
        
        return pairs
    
    def check_match(self, word: str, synonym: str) -> bool:
        """
        检查单词和同义词是否匹配
        """
        if word in self.word_dict:
            return synonym in self.word_dict[word]
        return False