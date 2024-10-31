import streamlit as st
import json
import requests
from components import (
    create_custom_input,
    username_options,
    labeling_options,
    preprocessing_options,
    augmentation_options,
)


def main():
    st.title("데이터셋 메타데이터 생성기")
    # 파일 업로드
    uploaded_file = st.file_uploader("데이터셋 CSV 파일을 업로드하세요", type=["csv"])

    # 실험 정보
    st.header("실험 정보")
    username = create_custom_input("실험자 이름", "user_name", username_options)
    datasetname = st.text_input(f"데이터셋 이름", key=f"dataset_name")
    description = st.text_area(
        f"데이터셋에 대한 간단한 설명을 남겨주세요", key=f"description", height=50
    )

    # 전처리 정보 입력
    st.header("전처리 정보")
    preprocessing_steps = []
    if st.checkbox("전처리 단계 추가"):
        num_preprocessing = st.number_input("전처리 단계 수", min_value=1, value=1)
        for i in range(num_preprocessing):
            st.subheader(f"전처리 단계 {i+1}")
            step_name = create_custom_input(
                "전처리 방법", f"prep_name_{i}", preprocessing_options
            )
            step_desc = st.text_input(f"전처리 방법 설명", key=f"prep_desc_{i}")

            if step_name and step_desc:
                preprocessing_steps.append({step_name: step_desc})

    # 라벨링 정보 입력
    st.header("라벨링 정보")
    labeling_methods = []
    if st.checkbox("라벨링 방법 추가"):
        num_labeling = st.number_input("라벨링 방법 수", min_value=1, value=1)
        for i in range(num_labeling):
            st.subheader(f"라벨링 방법 {i+1}")
            method_name = create_custom_input(
                "라벨링 방법", f"lab_name_{i}", labeling_options
            )
            method_desc = st.text_input(f"라벨링 방법 설명", key=f"lab_desc_{i}")

            if method_name and method_desc:
                labeling_methods.append({method_name: method_desc})

    # 증강 방법 입력
    st.header("데이터 증강 정보")
    augmentation_methods = []
    if st.checkbox("증강 방법 추가"):
        num_augmentation = st.number_input("증강 방법 수", min_value=1, value=1)
        for i in range(num_augmentation):
            st.subheader(f"증강 방법 {i+1}")
            method_name = create_custom_input(
                "증강 방법", f"aug_name_{i}", augmentation_options
            )
            method_desc = st.text_input(f"증강 방법 설명", key=f"aug_desc_{i}")

            if method_name and method_desc:
                augmentation_methods.append({method_name: method_desc})

    # 클라우드 업로드
    st.header("클라우드 업로드")
    is_gdrive_upload = False
    if st.checkbox("구글 드라이브 업로드"):
        is_gdrive_upload = True

    if st.button("메타데이터 생성"):
        if not uploaded_file:
            st.error("파일을 먼저 업로드해주세요")
        elif not datasetname:
            st.error("데이터셋 이름을 입력해주세요")
        else:
            # JSON 문자열로 변환
            preprocessing_steps_json = json.dumps(
                preprocessing_steps, ensure_ascii=False
            )
            labeling_methods_json = json.dumps(labeling_methods, ensure_ascii=False)
            augmentation_methods_json = json.dumps(
                augmentation_methods, ensure_ascii=False
            )

            # API 요청 보내기
            files = {"file": uploaded_file}
            data = {
                "creator": username,
                "datasetname": datasetname,
                "description": description,
                "labeling_methods": labeling_methods_json,
                "preprocessing_steps": preprocessing_steps_json,
                "augmentation_methods": augmentation_methods_json,
                "is_gdrive_upload": is_gdrive_upload if is_gdrive_upload else None,
            }

            response = requests.post(
                "http://localhost:8000/generate_metadata",
                files=files,
                data=data,
            )

            def _display_metadata(metadata, datasetname):
                """메타데이터 표시 및 다운로드 버튼 생성"""
                metadata_str = json.dumps(metadata, indent=2, ensure_ascii=False)

                # 다운로드 버튼
                st.download_button(
                    label="메타데이터 다운로드",
                    data=metadata_str.encode("utf-8"),
                    file_name=f"{datasetname}.json",
                    mime="application/json",
                )
                # 메타데이터 표시
                st.json(metadata)

            # 업로드 응답 처리
            if response.status_code == 200:
                response_data = response.json()
                gdrive_url = response_data.pop("gdrive_url", None)
                metadata = response_data
                st.write(f"드라이브 업로드 성공: {gdrive_url}")
                _display_metadata(metadata, datasetname)
            elif response.status_code == 207:
                st.write("드라이브 업로드 실패! 직접 업로드하세요.")
                metadata = response.json()
                _display_metadata(metadata, datasetname)
            else:
                st.error(f"에러 발생: {response.text}")

    # 입력된 정보 확인을 위한 디버그 섹션
    if st.checkbox("입력된 정보 확인"):
        st.write("전처리 단계:", preprocessing_steps)
        st.write("라벨링 방법:", labeling_methods)
        st.write("증강 방법:", augmentation_methods)


if __name__ == "__main__":
    st.set_page_config(page_title="데이터셋 메타데이터 생성기", layout="wide")
    st.markdown(
        """
        <style>
            /* 기본 입력 요소 */
            [data-testid="stForm"] {
                max-width: 400px;
            }
            
            /* number_input만 작게 */
            [data-testid="stNumberInput"] {
                max-width: 100px;
            }
            
            .block-container {
                max-width: 800px;
                padding: 2rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    main()
