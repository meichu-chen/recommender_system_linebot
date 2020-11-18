'''

移除帳號內的richmenu

'''

from linebot import (
    LineBotApi
)

import json

# 設定要移除的rich_menu
rich_menu_name_array = ["rich_menu_0"]

secretFileContentJson = json.load(open("./line_secret_key", 'r', encoding='utf8'))
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))

for rich_menu_name in rich_menu_name_array:
    # 讀取rich_menu_id檔案，並告知 Line 進行刪除，並在刪除後，把本地檔案內容清除
    with open("素材/" + rich_menu_name + '/rich_menu_id', 'r') as myfile:
        rich_menu_id = myfile.read()
        deleteResult = line_bot_api.delete_rich_menu(rich_menu_id)
        print(deleteResult)

    f = open("素材/" + rich_menu_name + "/rich_menu_id", "w")
    f.write('')
    f.close()