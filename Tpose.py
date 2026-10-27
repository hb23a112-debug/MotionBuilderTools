from pyfbsdk import *

# ------------------------------
# 設定
# ------------------------------

# Hips系ボーン名の候補（末尾一致で検索）
HIP_NAME_CANDIDATES = ["Hips", "Pelvis", "Hip", "Root"]

# ショルダーボーン名の候補（末尾一致で検索）
# ここに列挙したボーン以降（子孫含む）のローカル回転をすべて 0 にする
SHOULDER_NAME_CANDIDATES = ["LeftShoulder", "RightShoulder"]


# ------------------------------
# ユーティリティ関数
# ------------------------------

def recursive_find_by_name_candidates(model, candidates, results):
    """
    シーンを再帰的に走査し、model.Name が candidates のいずれかに
    末尾一致するモデルをすべて results に追加する。
    """
    for candidate in candidates:
        if model.Name.endswith(candidate):
            results.append(model)
            break  # 1ボーンに複数マッチは不要
    for child in model.Children:
        recursive_find_by_name_candidates(child, candidates, results)


def recursive_reset_global_rotation(model):
    """
    指定モデルとその子孫すべてのグローバル回転を (0, 0, 0) に設定する。
    MotionBuilder が逆算してローカル値を自動調整するため、
    見た目（ワールド空間）が正しく 0 になる。
    """
    zero = FBVector3d(0, 0, 0)
    model.SetVector(zero, FBModelTransformationType.kModelRotation, False)  # False = グローバル
    print(f"  グローバル回転リセット: {model.Name}")
    for child in model.Children:
        recursive_reset_global_rotation(child)


def reset_hip_global_y(hip_model):
    """
    Hips系ボーンのグローバル回転のうち Y 軸のみ 0 にリセットする。
    X・Z はそのまま維持。
    """
    current_rot = FBVector3d()
    hip_model.GetVector(current_rot, FBModelTransformationType.kModelRotation, False)  # False = グローバル
    current_rot[1] = 0.0  # Y 軸のみ 0
    hip_model.SetVector(current_rot, FBModelTransformationType.kModelRotation, False)
    print(f"  グローバルY回転リセット: {hip_model.Name}  → ({current_rot[0]:.2f}, 0.00, {current_rot[2]:.2f})")


# ------------------------------
# メイン処理
# ------------------------------

scene = FBSystem().Scene

hips_models     = []
shoulder_models = []

for root_model in scene.RootModel.Children:
    recursive_find_by_name_candidates(root_model, HIP_NAME_CANDIDATES,      hips_models)
    recursive_find_by_name_candidates(root_model, SHOULDER_NAME_CANDIDATES, shoulder_models)

# --- 1. Hips: グローバルY回転のみ 0 にリセット
print("=== Hips グローバルY回転リセット ===")
if not hips_models:
    print("  Hipsボーンが見つかりませんでした。")
else:
    for hip in hips_models:
        reset_hip_global_y(hip)

# --- 2. ショルダー以降: ローカル回転をすべて 0 にリセット（子孫含む）
print("\n=== ショルダー以降 ローカル回転リセット ===")
if not shoulder_models:
    print("  ショルダーボーンが見つかりませんでした。")
else:
    for shoulder in shoulder_models:
        print(f"[{shoulder.Name}] とその子孫を処理中...")
        recursive_reset_global_rotation(shoulder)

print("\n✅ TPoseリセット完了")