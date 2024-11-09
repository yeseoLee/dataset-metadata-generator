# dataset-metadata-generator
데이터 전처리 및 증강 방법과 데이터셋의 통계 정보를 json 파일로 생성 및 구글 드라이브 업로드

# 사용 예시
<img width="600" alt="image" src="https://github.com/user-attachments/assets/7a4f593e-e9bb-46b8-a3bc-ee629b24c38f">
<img width="600" alt="image" src="https://github.com/user-attachments/assets/eb276510-45ea-4e93-90ee-c19ee6d9d63c">
<img width="600" alt="image" src="https://github.com/user-attachments/assets/8b98a93c-b57b-44e8-8cce-510e9d74035d">

## 생성된 json 메타데이터 
```json
{
    "datasetname": "10_ra_5600_bt_agument_x2",
    "creation_date": "2024-10-29 23:50:58",
    "creator": "예서",
    "total_samples": 5600,
    "columns": [
        "ID",
        "text",
        "target"
    ],
    "text_statistics": {
        "avg_length": 27.19214285714286,
        "max_length": 41,
        "min_length": 8,
        "total_words": 15104,
        "avg_words": 5.394285714285714
    },
    "target_distribution": {
        "class_distribution": {
            "5": 838,
            "1": 820,
            "4": 812,
            "0": 796,
            "6": 790,
            "2": 776,
            "3": 770
        },
        "num_classes": 7,
        "class_balance": {
            "5": 0.14964285714285713,
            "1": 0.14642857142857144,
            "4": 0.145,
            "0": 0.1417857142857143,
            "6": 0.14107142857142857,
            "2": 0.13857142857142857,
            "3": 0.1375
        }
    },
    "preprocessing_steps": [
        {
            "LLM": "EXAONE-3.0 8B / prompt_denoise_v1 / is_noise에 대해 복구"
        }
    ],
    "augmentation_methods": [
        {
            "역번역": "pororo기반 한국어-영어-한국어 2배 증강"
        }
    ]
}
```


# 사용법

## 웹 서비스로 실행

### fastapi 실행
```bash
uvicorn backend:app --reload
```

### streamlit 실행
```bash
streamlit run frontend.py
```

## metadata_generator.py 직접 실행
```bash
python metadata_generator.py
```
