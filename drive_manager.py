from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload, MediaIoBaseDownload
import os.path
import io
import yaml

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

with open(os.path.join("./settings", "settings.yaml")) as f:
    CFG = yaml.safe_load(f)
TOKEN = CFG["gdrive"]["token"]
CREDENTIALS = CFG["gdrive"]["credentials"]
FOLDER_ID = CFG["gdrive"]["folder_id"]


class GoogleDriveManager:
    def __init__(self):
        self.service = self.get_drive_service()
        self.root_folder_id = FOLDER_ID

    def get_drive_service(self):
        creds = None
        # 토큰 파일 존재 확인
        if os.path.exists(TOKEN):
            creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)

        # offline access를 위한 설정
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS,
                    SCOPES,
                    # offline access 설정 추가
                    access_type="offline",
                    # 강제로 refresh token 재발급
                    prompt="consent",
                )
                creds = flow.run_local_server(port=0)

            # 토큰 저장
            with open(TOKEN, "w") as token:
                token.write(creds.to_json())

        return build("drive", "v3", credentials=creds)

    def list_folder_files(self, folder_id=None):
        """폴더 내 파일 목록 조회"""
        if not folder_id:
            folder_id = self.root_folder_id
        query = f"'{folder_id}' in parents and trashed=false"

        try:
            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=100,
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
                )
                .execute()
            )

            return results.get("files", [])
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []

    def upload_file(self, file_path, folder_id=None):
        """파일 업로드"""
        try:
            file_metadata = {"name": os.path.basename(file_path)}
            if not folder_id:
                folder_id = self.root_folder_id
            file_metadata["parents"] = [folder_id]

            media = MediaFileUpload(file_path, resumable=True)

            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id, name")
                .execute()
            )

            print(
                f"File uploaded successfully: {file.get('name')} (ID: {file.get('id')})"
            )
            return file
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None

    def upload_json_data(self, json_string, filename, folder_id=None):
        """직렬화된 JSON string 직접 업로드"""
        try:
            # 메모리 스트림으로 변환
            file_stream = io.BytesIO(json_string.encode("utf-8"))

            # 파일 메타데이터 설정
            file_metadata = {"name": filename, "mimeType": "application/json"}
            if folder_id:
                file_metadata["parents"] = [folder_id]

            # 미디어 객체 생성
            media = MediaIoBaseUpload(
                file_stream, mimetype="application/json", resumable=True
            )

            # 파일 업로드
            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id, name")
                .execute()
            )

            print(
                f"JSON file uploaded successfully: {file.get('name')} (ID: {file.get('id')})"
            )
            return file

        except Exception as e:
            print(f"Error uploading JSON data: {str(e)}")
            return None

    def upload_dataframe(self, dataframe, filename, folder_id=None):
        """Pandas DataFrame 직접 업로드"""
        try:
            # DataFrame을 CSV 스트림으로 변환
            buffer = io.StringIO()
            dataframe.to_csv(buffer, index=False)
            file_stream = io.BytesIO(buffer.getvalue().encode("utf-8"))

            # 파일 메타데이터 설정
            file_metadata = {"name": filename, "mimeType": "text/csv"}
            if folder_id:
                file_metadata["parents"] = [folder_id]

            # 미디어 객체 생성
            media = MediaIoBaseUpload(file_stream, mimetype="text/csv", resumable=True)

            # 파일 업로드
            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id, name")
                .execute()
            )

            print(
                f"DataFrame uploaded successfully: {file.get('name')} (ID: {file.get('id')})"
            )
            return file

        except Exception as e:
            print(f"Error uploading DataFrame: {str(e)}")
            return None

    def download_file(self, file_id, output_path):
        """파일 다운로드"""
        try:
            # 파일 메타데이터 가져오기
            file_metadata = self.service.files().get(fileId=file_id).execute()

            # 파일 다운로드
            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(output_path, "wb")
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    print(f"Download {int(status.progress() * 100)}%")

            print(f"File downloaded successfully: {file_metadata.get('name')}")
            return True
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return False

    def create_folder(self, folder_name, parent_folder_id=None):
        """폴더 생성"""
        try:
            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            if not parent_folder_id:
                parent_folder_id = self.root_folder_id
            file_metadata["parents"] = [parent_folder_id]

            file = (
                self.service.files().create(body=file_metadata, fields="id").execute()
            )

            print(f"Folder created successfully with ID: {file.get('id')}")
            return file.get("id")
        except Exception as e:
            print(f"Error creating folder: {str(e)}")
            return None

    # def delete_file(self, file_id):
    #     """파일 삭제"""
    #     try:
    #         self.service.files().delete(fileId=file_id).execute()
    #         print(f"File with ID {file_id} deleted successfully")
    #         return True
    #     except Exception as e:
    #         print(f"Error deleting file: {str(e)}")
    #         return False


if __name__ == "__main__":
    drive_manager = GoogleDriveManager()
    # 파일 목록 조회
    files = drive_manager.list_folder_files()
    for file in files:
        print(f"Name: {file['name']}, ID: {file['id']}")

    # 파일 업로드
    file_path = "./requirements.txt"
    uploaded_file = drive_manager.upload_file(file_path)

    # 파일 다운로드
    if uploaded_file:
        drive_manager.download_file(uploaded_file["id"], "./output/requirements.txt")

    # 새 폴더 생성
    new_folder_id = drive_manager.create_folder("New Folder")
