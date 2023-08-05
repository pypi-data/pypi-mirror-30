from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音 import 臺灣閩南語羅馬字拼音


def 是前詞綴(詞分詞):
    集合 = ('阿｜a1',)
    return 詞分詞 in 集合


def 是後詞綴(詞分詞):
    集合 = ('仔｜a2',)
    return 詞分詞 in 集合


def 單音節詞綴原則(句物件):
    #
    # 原則一：「名詞語單音節前、中、後詞綴，皆連寫」，目前只能作到「前、後詞綴」。
    # 原則五：「阿與後接人名連寫」
    #
    錯誤訊息陣列 = []
    詞物件陣列 = 句物件.網出詞物件()
    總詞數 = len(詞物件陣列)
    累積字長度 = 0
    前一个詞分詞 = None
    for 詞位置, 詞物件 in enumerate(詞物件陣列):
        詞分詞 = 詞物件.轉音(臺灣閩南語羅馬字拼音).看分詞()
        詞長度 = len(詞物件.篩出字物件())
        
        # 單音節前詞綴應和名詞連寫 阿公 => 阿-公
        if 前一个詞分詞 and 是前詞綴(前一个詞分詞):
            錯誤行數 = 累積字長度 + 1
            錯誤連字符位置 = '前'
            錯誤訊息陣列.append(('E名詞（一）', 錯誤行數, 錯誤連字符位置))

        # 單音節後詞綴應和名詞連寫 椅仔 => 椅-仔
        if 是後詞綴(詞分詞) and 總詞數 > 1:
            錯誤行數 = 累積字長度 + 1
            錯誤連字符位置 = '前'
            錯誤訊息陣列.append(('E名詞（一）', 錯誤行數, 錯誤連字符位置))
        
        前一个詞分詞 = 詞分詞
        累積字長度 += 詞長度
    return 錯誤訊息陣列
