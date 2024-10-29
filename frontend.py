import streamlit as st
import json
import requests

st.set_page_config(page_title="데이터셋 메타데이터 생성기", layout="wide")

st.title("데이터셋 메타데이터 생성기")

# 파일 업로드
uploaded_file = st.file_uploader("데이터셋 CSV 파일을 업로드하세요", type=["csv"])

# 실험 정보
st.header("실험 정보")
username = st.text_input(f"실험자 이름", key=f"user_name")
datasetname = st.text_input(f"데이터셋 이름", key=f"dataset_name")

# 전처리 정보 입력
st.header("전처리 정보")
preprocessing_steps = []
if st.checkbox("전처리 단계 추가"):
    num_preprocessing = st.number_input("전처리 단계 수", min_value=1, value=1)
    for i in range(num_preprocessing):
        st.subheader(f"전처리 단계 {i+1}")
        step_name = st.text_input(f"전처리 방법 이름", key=f"prep_name_{i}")
        step_desc = st.text_input(f"전처리 방법 설명", key=f"prep_desc_{i}")

        if step_name and step_desc:  # 둘 다 입력된 경우에만 추가
            preprocessing_steps.append(
                {"step": step_name, "params": {"description": step_desc}}
            )

# 증강 방법 입력
st.header("데이터 증강 정보")
augmentation_methods = []
if st.checkbox("증강 방법 추가"):
    num_augmentation = st.number_input("증강 방법 수", min_value=1, value=1)
    for i in range(num_augmentation):
        st.subheader(f"증강 방법 {i+1}")
        method_name = st.text_input(f"증강 방법 이름", key=f"aug_name_{i}")
        method_desc = st.text_input(f"증강 방법 설명", key=f"aug_desc_{i}")

        if method_name and method_desc:  # 둘 다 입력된 경우에만 추가
            augmentation_methods.append(
                {"method": method_name, "params": {"description": method_desc}}
            )

if st.button("메타데이터 생성"):
    if uploaded_file is None:
        st.error("파일을 먼저 업로드해주세요")
    elif datasetname is None:
        st.error("데이터셋 이름을 입력해주세요")
    else:
        # preprocessing_steps와 augmentation_methods를 JSON 문자열로 변환
        preprocessing_steps_json = json.dumps(preprocessing_steps, ensure_ascii=False)
        augmentation_methods_json = json.dumps(augmentation_methods, ensure_ascii=False)

        # API 요청 보내기
        files = {"file": uploaded_file}
        data = {
            "creator": username,
            "datasetname": datasetname,
            "preprocessing_steps": preprocessing_steps_json,
            "augmentation_methods": augmentation_methods_json,
        }

        response = requests.post(
            "http://localhost:8000/generate_metadata",
            files=files,
            data=data,
        )

        if response.status_code == 200:
            metadata = response.json()

            # 다운로드 버튼
            metadata_str = json.dumps(metadata, indent=2, ensure_ascii=False)
            st.download_button(
                label="메타데이터 다운로드",
                data=metadata_str.encode("utf-8"),
                file_name="metadata.json",
                mime="application/json",
            )
            # 메타데이터 표시
            st.json(metadata)
        else:
            st.error(f"에러 발생: {response.text}")

# 입력된 정보 확인을 위한 디버그 섹션
if st.checkbox("입력된 정보 확인"):
    st.write("전처리 단계:", preprocessing_steps)
    st.write("증강 방법:", augmentation_methods)
