from pyfbsdk import *
from pyfbsdk_additions import *

# ------------------------------
# カメラ設定関数
# ------------------------------
def setup_camera(camera):
    camera.ViewCameraInterest = False
    camera.UseFrameColor = True
    camera.FrameColor = FBColor(1.0, 0.0, 0.0)
    camera.BackGroundColor = FBColor(0.70, 0.70, 0.70)
    camera.FieldOfView = 40
    camera.ResolutionMode = FBCameraResolutionMode.kFBResolutionCustom
    camera.ResolutionWidth = 1920
    camera.ResolutionHeight = 1080

def add_camera_fixed(direction):
    positions = {
        "Front":       (FBVector3d(0, 100, 300),   FBVector3d(0, 0, 0)),
        "Side":        (FBVector3d(-300, 100, 0),  FBVector3d(0, -90, 0)),
        "Perspective": (FBVector3d(200, 200, 200), FBVector3d(-30, 45, 0)),
    }
    pos, rot = positions[direction]
    camera = FBCamera(f"Camera_{direction}")
    camera.Translation = pos
    camera.Rotation = rot
    setup_camera(camera)
    print(f"カメラ追加: {camera.Name}")

def add_camera_follow(target_name, character):
    """
    character : FBCharacter
    target_name : "Hips" / "Head" / "ChestEndEffector"
    """
    # FBBodyNodeId でボーンを直接取得
    BONE_NODE_MAP = {
        "Hips":             FBBodyNodeId.kFBHipsNodeId,
        "Head":             FBBodyNodeId.kFBHeadNodeId,
        "ChestEndEffector": FBBodyNodeId.kFBChestNodeId,
    }

    target = None
    node_id = BONE_NODE_MAP.get(target_name)
    if node_id is not None:
        try:
            target = character.GetModel(node_id)
        except Exception:
            target = None

    # FBCharacter から取れなかった場合は名前で再帰検索
    if not target:
        def recursive_find(model, name):
            if model.Name.endswith(name):
                return model
            for child in model.Children:
                result = recursive_find(child, name)
                if result:
                    return result
            return None
        try:
            hips = character.GetModel(FBBodyNodeId.kFBHipsNodeId)
            if hips:
                root = hips
                while root.Parent and root.Parent != FBSystem().Scene.RootModel:
                    root = root.Parent
                target = recursive_find(root, target_name)
        except Exception:
            pass

    if not target:
        print(f"{target_name} が {character.Name} の中に見つかりませんでした。")
        return

    cam_name = f"Camera_Follow_{character.Name}_{target_name}"
    camera = FBCamera(cam_name)
    camera.LookAt = target
    pos = FBVector3d()
    target.GetVector(pos, FBModelTransformationType.kModelTranslation, False)
    camera.Translation = FBVector3d(pos[0], pos[1] + 50, pos[2] + 300)
    setup_camera(camera)
    print(f"追従カメラ追加: {camera.Name} → {target.Name}")

# ------------------------------
# シーン内の FBCharacter 一覧取得
# ------------------------------
def get_characters():
    characters = []
    for comp in FBSystem().Scene.Components:
        if isinstance(comp, FBCharacter):
            characters.append(comp)
    return characters

# ------------------------------
# ライト作成関数
# ------------------------------
def add_lights():
    light_settings = [
        ("Light_1", FBVector3d(0, 0, 0), FBVector3d(90, 0, 0)),
        ("Light_2", FBVector3d(0, 0, 0), FBVector3d(90, -90, 0)),
        ("Light_3", FBVector3d(0, 0, 0), FBVector3d(90, 90, 0)),
        ("Light_4", FBVector3d(0, 0, 0), FBVector3d(-90, 0, 0)),
    ]
    for name, pos, rot in light_settings:
        light = FBLight(name)
        light.LightType = FBLightType.kFBLightTypeInfinite
        light.Intensity = 80
        light.Translation = pos
        light.Rotation = rot
        light.Visibility = True
        light.Show = True
        print(f"ライト追加: {light.Name}")

# ------------------------------
# UI
# ------------------------------
def PopulateLayout(mainLyt):
    x = FBAddRegionParam(0, FBAttachType.kFBAttachLeft, "")
    y = FBAddRegionParam(5, FBAttachType.kFBAttachTop, "")
    w = FBAddRegionParam(-5, FBAttachType.kFBAttachRight, "")
    h = FBAddRegionParam(-5, FBAttachType.kFBAttachBottom, "")

    main = FBVBoxLayout()
    mainLyt.AddRegion("main", "main", x, y, w, h)
    mainLyt.SetControl("main", main)

    # ---- 固定カメラ ----
    cam_label = FBLabel()
    cam_label.Caption = "--- 追加カメラ ---"
    main.Add(cam_label, 25)

    for direction in ["Front", "Side", "Perspective"]:
        b = FBButton()
        b.Caption = direction
        b.OnClick.Add(lambda c, e, d=direction: add_camera_fixed(d))
        main.Add(b, 35)

    # ---- 追従カメラ ----
    follow_label = FBLabel()
    follow_label.Caption = "--- 追従カメラ ---"
    main.Add(follow_label, 25)

    chara_label = FBLabel()
    chara_label.Caption = "対象キャラクター:"
    main.Add(chara_label, 20)

    chara_list = FBList()
    chara_list.Style = FBListStyle.kFBDropDownList
    main.Add(chara_list, 25)

    state = {"characters": []}

    def refresh():
        chara_list.Items.removeAll()
        state["characters"] = get_characters()
        if state["characters"]:
            for chara in state["characters"]:
                chara_list.Items.append(chara.Name)
            chara_list.ItemIndex = 0
            print(f"キャラクター {len(state['characters'])} 体検出")
        else:
            chara_list.Items.append("（キャラクターなし）")
            chara_list.ItemIndex = 0
            print("FBCharacter が見つかりませんでした。")

    refresh_btn = FBButton()
    refresh_btn.Caption = "リストを更新"
    refresh_btn.OnClick.Add(lambda c, e: refresh())
    main.Add(refresh_btn, 28)

    refresh()

    def get_selected_character():
        idx = chara_list.ItemIndex
        if 0 <= idx < len(state["characters"]):
            return state["characters"][idx]
        return None

    for target in ["Hips", "Head", "ChestEndEffector"]:
        b = FBButton()
        b.Caption = f"追従: {target}"
        def on_follow(c, e, t=target):
            chara = get_selected_character()
            if chara is None:
                print("キャラクターが選択されていないか、シーンに存在しません。")
                return
            add_camera_follow(t, chara)
        b.OnClick.Add(on_follow)
        main.Add(b, 35)

    # ---- ライト ----
    light_label = FBLabel()
    light_label.Caption = "--- ライト ---"
    main.Add(light_label, 25)

    lb = FBButton()
    lb.Caption = "ライト追加"
    lb.OnClick.Add(lambda c, e: add_lights())
    main.Add(lb, 35)

t = FBCreateUniqueTool("カメラ・ライトツール")
t.StartSizeX = 220
t.StartSizeY = 530
PopulateLayout(t)
ShowTool(t)