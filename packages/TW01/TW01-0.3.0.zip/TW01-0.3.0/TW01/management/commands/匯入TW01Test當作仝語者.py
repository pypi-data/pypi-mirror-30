from TW01.management.commands.匯入TW01Test import Command as 匯入指令


class Command(匯入指令):

    def _全部資料(self, 語料目錄):
        for _語者, 音檔路徑, 正規化物件 in super()._全部資料(語料目錄):
            yield 'TW01Test', 音檔路徑, 正規化物件
