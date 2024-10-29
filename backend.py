import pandas as pd
import numpy as np
import json
import io
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from metadata_generator import MetadataGenerator
from drive_manager import GoogleDriveManager


# NumPy 타입을 처리하기 위한 커스텀 JSONEncoder
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate_metadata")
async def generate_metadata(
    file: UploadFile = File(...),
    creator: str = Form(None),
    datasetname: str = Form(None),
    preprocessing_steps: str = Form(None),
    labeling_methods: str = Form(None),
    augmentation_methods: str = Form(None),
    is_gdrive_upload: bool = Form(None),
):
    try:
        # CSV 파일 읽기
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        # 메타데이터 생성
        metadata_generator = MetadataGenerator(df)

        # JSON 문자열을 파이썬 객체로 파싱
        preprocessing_dict = (
            json.loads(preprocessing_steps) if preprocessing_steps else None
        )
        labeling_dict = json.loads(labeling_methods) if labeling_methods else None
        augmentation_dict = (
            json.loads(augmentation_methods) if augmentation_methods else None
        )

        metadata = metadata_generator.generate_full_metadata(
            creator=creator,
            datasetname=datasetname,
            preprocessing_steps=preprocessing_dict,
            labeling_methods=labeling_dict,
            augmentation_methods=augmentation_dict,
        )

        # NumPy 타입을 포함한 JSON 직렬화
        json_str = json.dumps(metadata, cls=NumpyEncoder, indent=4, ensure_ascii=False)

        # GDrive 업로드
        if is_gdrive_upload:
            drive_manager = GoogleDriveManager()
            folder_id = drive_manager.create_folder(f"{creator}-{datasetname}")
            uploaded_df = drive_manager.upload_dataframe(
                df, f"{datasetname}.csv", folder_id
            )
            uploaded_json = drive_manager.upload_json_data(
                json_str, f"{datasetname}_metadata.json", folder_id
            )
            if not uploaded_df or not uploaded_json:
                return JSONResponse(status_code=207, content=json.loads(json_str))
        return JSONResponse(content=json.loads(json_str))

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
