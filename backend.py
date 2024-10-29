import pandas as pd
import numpy as np
import json
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from metadata_generator import MetadataGenerator
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse


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
    augmentation_methods: str = Form(None),
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
        augmentation_dict = (
            json.loads(augmentation_methods) if augmentation_methods else None
        )

        metadata = metadata_generator.generate_full_metadata(
            creator=creator,
            datasetname=datasetname,
            preprocessing_steps=preprocessing_dict,
            augmentation_methods=augmentation_dict,
        )

        # NumPy 타입을 포함한 JSON 직렬화
        json_str = json.dumps(metadata, cls=NumpyEncoder, ensure_ascii=False)
        return JSONResponse(content=json.loads(json_str))

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
