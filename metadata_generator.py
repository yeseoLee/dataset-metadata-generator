import os
import pandas as pd
from datetime import datetime


class MetadataGenerator:
    def __init__(self, dataset, output_path=None):
        self.dataset = dataset
        self.output_path = output_path
        self.metadata = {}

    def generate_basic_info(self, creator):
        """기본 데이터셋 정보 생성"""
        self.metadata["creation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.metadata["creator"] = creator
        self.metadata["total_samples"] = len(self.dataset)
        self.metadata["columns"] = list(self.dataset.columns)

    def generate_text_statistics(self):
        """텍스트 데이터 통계 생성"""
        text_stats = {
            "avg_length": self.dataset["text"].str.len().mean(),
            "max_length": self.dataset["text"].str.len().max(),
            "min_length": self.dataset["text"].str.len().min(),
            "total_words": sum(self.dataset["text"].str.split().str.len()),
            "avg_words": self.dataset["text"].str.split().str.len().mean(),
        }
        self.metadata["text_statistics"] = text_stats

    def generate_target_distribution(self):
        """타겟 레이블 분포 분석"""
        target_counts = self.dataset["target"].value_counts().to_dict()
        self.metadata["target_distribution"] = {
            "class_distribution": target_counts,
            "num_classes": len(target_counts),
            "class_balance": {
                str(label): count / len(self.dataset)
                for label, count in target_counts.items()
            },
        }

    def add_preprocessing_info(self, preprocessing_steps):
        """전처리 정보 추가"""
        if preprocessing_steps:
            self.metadata["preprocessing_steps"] = preprocessing_steps

    def add_augmentation_info(self, augmentation_methods):
        """데이터 증강 정보 추가"""
        if augmentation_methods:
            self.metadata["augmentation_methods"] = augmentation_methods

    def generate_full_metadata(
        self, creator=None, preprocessing_steps=None, augmentation_methods=None
    ):
        """전체 메타데이터 생성"""
        self.generate_basic_info(creator)
        self.generate_text_statistics()
        self.generate_target_distribution()
        self.add_preprocessing_info(preprocessing_steps)
        self.add_augmentation_info(augmentation_methods)
        return self.metadata

    def save_metadata(self):
        """메타데이터를 JSON 파일로 저장"""
        if self.output_path:
            pd.DataFrame([self.metadata]).to_json(
                self.output_path, orient="records", indent=4, force_ascii=False
            )


if __name__ == "__main__":
    # 전처리 방법론
    REMOVE_POS = "품사_제거"
    REMOVE_SPECIAL_POS = "특수문자_제거"
    REMOVE_UNK = "UNK_제거"

    # 증강 방법론
    BACK_TRANSLATION = "역번역"
    SYNONYM_REPLACEMENT = "동의어_대체"
    KOR_EDA = "KorEDA"

    # 데이터셋과 메타데이터 생성기 초기화
    BASE_DIR = os.getcwd()
    DATA_DIR = os.path.join(BASE_DIR, "./data")
    OUTPUT_DIR = os.path.join(BASE_DIR, "./output")
    dataset = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))

    metadata_generator = MetadataGenerator(
        dataset, output_path=os.path.join(OUTPUT_DIR, "metadata.json")
    )

    # 전처리 방법 정의
    preprocessing_steps = [
        {"step": REMOVE_POS, "applied": True},
        {"step": REMOVE_SPECIAL_POS, "targets": ["조사", "부사", "형용사"]},
        {"step": REMOVE_UNK, "applied": True},
    ]

    # 증강 방법 정의
    augmentation_methods = [
        {"method": BACK_TRANSLATION, "languages": ["en", "ko"]},
        {"method": SYNONYM_REPLACEMENT, "num_replacements": 2},
        {
            "method": KOR_EDA,
            "operation": ["sr", "ri", "rs", "rd"],
            "alpha": [0.1, 0.1, 0.1, 0.1],
            "num_aug": 9,
        },
    ]

    # 메타데이터 생성 및 저장
    metadata = metadata_generator.generate_full_metadata(
        creator="yeseo",
        preprocessing_steps=preprocessing_steps,
        augmentation_methods=augmentation_methods,
    )
    metadata_generator.save_metadata()
