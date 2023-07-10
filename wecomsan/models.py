from pydantic import BaseModel


class WecomApiResponse(BaseModel):
    """see https://developer.work.weixin.qq.com/document/path/90236
    https://developer.work.weixin.qq.com/document/path/90313"""
    errcode: int
    errmsg: str
