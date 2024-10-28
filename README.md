# dataset-metadata-generator
데이터 전처리 및 증강 방법과 데이터셋의 통계 정보를 json 파일로 생성

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

## 결과
```json
[
    {
        "creation_date":"2024-10-29 01:44:48",
        "creator":"yeseo",
        "total_samples":8,
        "columns":[
            "ID",
            "text",
            "target"
        ],
        "text_statistics":{
            "avg_length":7.125,
            "max_length":16,
            "min_length":3,
            "total_words":15,
            "avg_words":1.875
        },
        "target_distribution":{
            "class_distribution":{
                "6":2,
                "0":1,
                "1":1,
                "2":1,
                "3":1,
                "4":1,
                "5":1
            },
            "num_classes":7,
            "class_balance":{
                "6":0.25,
                "0":0.125,
                "1":0.125,
                "2":0.125,
                "3":0.125,
                "4":0.125,
                "5":0.125
            }
        },
        "preprocessing_steps":[
            {
                "step":"품사_제거",
                "applied":true
            },
            {
                "step":"특수문자_제거",
                "targets":[
                    "조사",
                    "부사",
                    "형용사"
                ]
            },
            {
                "step":"UNK_제거",
                "applied":true
            }
        ],
        "augmentation_methods":[
            {
                "method":"역번역",
                "languages":[
                    "en",
                    "ko"
                ]
            },
            {
                "method":"동의어_대체",
                "num_replacements":2
            },
            {
                "method":"KorEDA",
                "operation":[
                    "sr",
                    "ri",
                    "rs",
                    "rd"
                ],
                "alpha":[
                    0.1,
                    0.1,
                    0.1,
                    0.1
                ],
                "num_aug":9
            }
        ]
    }
]
```