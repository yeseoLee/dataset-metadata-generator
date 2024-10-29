import streamlit as st
import os.path
import yaml

with open(os.path.join("./settings", "settings.yaml")) as f:
    CFG = yaml.safe_load(f)

username_options = CFG["components"]["username"]
labeling_options = CFG["components"]["labeling"]
preprocessing_options = CFG["components"]["preprocessing"]
augmentation_options = CFG["components"]["augmentation"]


def create_custom_input(label, key, options, other_option="직접 입력"):
    """드롭다운과 텍스트 입력을 결합한 커스텀 입력 컴포넌트"""
    # 드롭다운 옵션에 직접 입력 추가
    all_options = options + [other_option]

    # 드롭다운 선택
    selected = st.selectbox(f"{label} 선택", all_options, key=f"select_{key}")

    # 직접 입력인 경우 텍스트 입력 표시
    if selected == other_option:
        value = st.text_input(f"{label} 직접 입력", key=f"input_{key}")
    else:
        value = selected

    return value
