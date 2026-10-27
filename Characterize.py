from pyfbsdk import *
from pyfbsdk_additions import *

scene = FBSystem().Scene

def get_root_hips(scene):
    result = {}
    for comp in scene.Components:
        if isinstance(comp, FBModelSkeleton):
            if comp.Name.lower() == "hips":
                parent = comp.Parent
                parent_name = parent.Name if parent else "Unknown"
                result[parent_name] = comp
    return result

def find_bone_under_root(scene, hips_bone, bone_keyword):
    root = hips_bone.Parent
    for comp in scene.Components:
        if isinstance(comp, FBModelSkeleton):
            if bone_keyword.lower() in comp.Name.lower():
                p = comp
                while p is not None:
                    if p == root:
                        return comp
                    p = p.Parent
    return None

def characterize(char_name, hips_bone):
    character = FBCharacter(char_name)
    scene.Evaluate()

    bone_map = [
        ("HipsLink", "Hips"),
        ("LeftUpLegLink", "LeftUpLeg"),
        ("LeftLegLink", "LeftLeg"),
        ("LeftFootLink", "LeftFoot"),
        ("RightUpLegLink", "RightUpLeg"),
        ("RightLegLink", "RightLeg"),
        ("RightFootLink", "RightFoot"),
        ("SpineLink", "Spine"),
        ("LeftArmLink", "LeftArm"),
        ("LeftForeArmLink", "LeftForeArm"),
        ("LeftHandLink", "LeftHand"),
        ("RightArmLink", "RightArm"),
        ("RightForeArmLink", "RightForeArm"),
        ("RightHandLink", "RightHand"),
        ("HeadLink", "Head"),
    ]

    for prop_name, bone_keyword in bone_map:
        bone = find_bone_under_root(scene, hips_bone, bone_keyword)
        if bone:
            for prop in character.PropertyList:
                if prop.Name == prop_name:
                    prop.append(bone)
                    break
        else:
            print("ボーン見つからず: " + bone_keyword)

    success = character.SetCharacterizeOn(True)
    return success, character

# Hipsと親名のペアを取得
root_dict = get_root_hips(scene)

if not root_dict:
    FBMessageBox("エラー", "キャラクターが見つかりません", "OK")
else:
    root_list = list(root_dict.keys())
    total = len(root_list)
    print("検出したキャラクター数: " + str(total))

    for i, root_name in enumerate(root_list):
        hips_bone = root_dict[root_name]

        result = FBMessageBoxGetUserValue(
            "キャラクタライズ (" + str(i+1) + "/" + str(total) + ")",
            "キャラクター名を確認・編集してください\n親ボーン: " + root_name + "\n(スキップする場合はキャンセル)",
            root_name,
            FBPopupInputType.kFBPopupString,
            "実行",
            "スキップ"
        )

        if result[0] == 1:
            char_name = result[1]
            # 同名のキャラクターが既にある場合だけ削除
            for comp in list(scene.Components):
                if isinstance(comp, FBCharacter) and comp.Name == char_name:
                    comp.FBDelete()
                    scene.Evaluate()
                    break
            success, character = characterize(char_name, hips_bone)
            if success:
                print("✔ 成功: " + char_name)
            else:
                print("❌ 失敗: " + char_name)
                character.FBDelete()
        else:
            print("スキップ: " + root_name)

    FBMessageBox("完了", "全キャラクターの処理が終わりました", "OK")