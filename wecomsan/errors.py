# https://developer.work.weixin.qq.com/document/path/90313
SUCCESS = 0


class WecomSanRespError(Exception):
    """Error information provided by WeCom"""
    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(errmsg)


class WecomSanLocalError(Exception):
    """Error generated locally"""
    ...


class WecomSanUploadError(WecomSanLocalError):
    ...
