from pyfbsdk import *
from pyfbsdk_additions import *

import os

app = FBApplication()

# メニューID -> スクリプトのパス
scripts = {}


def eventMenu(control, event):
    """メニュー項目がクリックされたら、対応するスクリプトを実行する"""
    for path, menu_id in scripts.items():
        if menu_id == event.Id:
            app.ExecuteScript(path)
            break


# このファイルの場所を基準にする（取得できない場合はカレントディレクトリ）
try:
    curpath = os.path.dirname(os.path.abspath(__file__))
except NameError:
    curpath = os.getcwd()

basepath = os.path.join(curpath, "seisakuScriput")

if not os.path.isdir(basepath):
    print("seisakuScriput フォルダが見つかりません: " + basepath)
else:
    # サブフォルダ（カテゴリ）を名前順に取得
    folders = [
        f for f in sorted(os.listdir(basepath))
        if os.path.isdir(os.path.join(basepath, f)) and not f.startswith((".", "__"))
    ]

    MainMenu = FBMenuManager()
    MainMenu.InsertAfter(None, "Help", "seisakuScriput")
    MenuRoot = MainMenu.GetMenu("seisakuScriput")

    for i, folder in enumerate(folders):
        SubMenu = FBGenericMenu()

        # 番号部分を除いて表示（例: 1_Tpose → Tpose）
        display_name = folder.split("_", 1)[-1]
        MenuRoot.InsertLast(display_name, i + 1, SubMenu)

        folder_path = os.path.join(basepath, folder)
        pyfiles = [
            f for f in sorted(os.listdir(folder_path))
            if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".py")
        ]

        for l, pyfile in enumerate(pyfiles):
            # 1フォルダに99個まで、IDが衝突しない
            menu_id = (i + 1) * 100 + l
            SubMenu.InsertLast(pyfile[:-3], menu_id)
            scripts[os.path.join(folder_path, pyfile)] = menu_id

        SubMenu.OnMenuActivate.Add(eventMenu)
