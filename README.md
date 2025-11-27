# GRE_Synonyms
这是一个近义词背单词器，逻辑类似多邻国的配对游戏，能够根据用户的excel单词本随机生成配对题目，帮助用户记忆同义词对。

## 使用说明
### 准备单词本
1. 确保你的`.xlsx文件`有两列，且表头分别为`word`和`synonym`
2. `word`一列每行只能有一个单词，但是`synonym`一列可以有多个单词，每个单词之间用`,`进行分隔

### 环境配置
1. 进入项目目录
`cd 你的安装这几个py文件的目录`
2. 确保安装了依赖
`pip install pandas openpyxl`
3. 运行程序
`python main.py`
