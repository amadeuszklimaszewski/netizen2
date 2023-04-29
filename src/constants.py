from pydantic import BaseSettings


class AppConstants(BaseSettings):
    MAX_GROUP_NAME_LENGTH: int = 50
    MAX_GROUP_DESCRIPTION_LENGTH: int = 1000
    MAX_GROUP_REQUEST_MESSAGE_LENGTH: int = 250

    class Config:
        env_file = ".constants"
        env_file_encoding = "utf-8"


constants = AppConstants()
