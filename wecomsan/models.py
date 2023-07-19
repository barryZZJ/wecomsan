import datetime
from typing import Literal, TypeVar

from pydantic import BaseModel


class WecomApiRespBase(BaseModel):
    """see https://developer.work.weixin.qq.com/document/path/90236"""
    errcode: int
    errmsg: str


MediaType = Literal['image', 'voice', 'video', 'file']
MediaId = TypeVar('MediaId', bound=str)


class WecomApiRespUploadTempMedia(WecomApiRespBase):
    """https://developer.work.weixin.qq.com/document/path/90254"""
    type: MediaType
    media_id: MediaId
    created_at: datetime.datetime
