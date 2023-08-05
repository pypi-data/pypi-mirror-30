from os.path import join, dirname, isfile, realpath
import ast
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音 import 臺灣閩南語羅馬字拼音
import json

def 讀取原始檔():
    目前所在資料夾 = dirname(realpath(__file__))
    教典json檔名 = join(目前所在資料夾, 'moedict-twblg.json')
    if isfile(教典json檔名):
        with open(教典json檔名) as f:
            教典表 = set(json.load(f))
    else:
        教典原始檔名 = join(目前所在資料夾, 'moedict-twblg-kiat4-ko2')
        教典表 = set()
        with open(教典原始檔名) as f:
            for line in f:
                # ('佮意', 'kah-ì', ('動',))
                # => ['佮-意｜kah4-i3']
                逐逝 = ast.literal_eval(line)
                字分詞陣列 = []
                try:
                    句物件 = 拆文分析器.對齊句物件(逐逝[0], 逐逝[1]).轉音(臺灣閩南語羅馬字拼音)
                    詞條分詞 = 句物件.看分詞()
                    字物件陣列 = 句物件.篩出字物件()
                    for 一字物件 in 字物件陣列:
                        字分詞陣列.append(一字物件.看分詞())  
                except Exception as 錯誤:
                    print('讀取原始檔發生錯誤', 錯誤)
                    exit()
                教典表.add(詞條分詞)
        with open(教典json檔名, 'w') as f:
            json.dump(list(教典表), f)
    return 教典表
