import base64
import json
from typing import Optional, Union, TextIO

import wecomsan.myrequests as requests
"""Move filelength field from custom header to content-disposition"""

from wecomsan.errors import SUCCESS, WecomSanUploadError, WecomSanRespError
from wecomsan.models import WecomApiRespBase, WecomApiRespUploadTempMedia, MediaType, MediaId


def split_text(text: str, max_bytes: int) -> list[str]:
    chunks = []
    current_chunk = ""
    current_bytes = 0

    for char in text:
        char_bytes = char.encode('utf-8')
        if current_bytes + len(char_bytes) > max_bytes:
            chunks.append(current_chunk)
            current_chunk = ""
            current_bytes = 0

        current_chunk += char
        current_bytes += len(char_bytes)

    if current_bytes > 0:
        chunks.append(current_chunk)

    return chunks


class WecomSan:
    def __init__(self, cid, aid, secret, **requests_kwargs):
        self.cid = cid
        self.aid = aid
        self.secret = secret
        self.requests_kwargs = requests_kwargs

    @property
    def access_token(self):
        get_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.cid}&corpsecret={self.secret}"
        access_token = requests.get(get_token_url, **self.requests_kwargs).json().get('access_token')
        if access_token and len(access_token) > 0:
            return access_token

        raise ModuleNotFoundError('fail to get access token')

    def send(self, text, touid='@all') -> WecomApiRespBase:
        """touid can be UserID1. use '|' to join multiple userids.
        See: https://developer.work.weixin.qq.com/document/path/90236"""
        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}'
        data = {
            "touser": touid,
            "agentid": self.aid,
            "msgtype": "text",
            "text": {
                "content": text
            },
            "duplicate_check_interval": 600
        }
        resp = requests.post(send_msg_url, data=json.dumps(data), **self.requests_kwargs)
        # resp example:
        # fail: {'errcode': 60020, 'errmsg': 'not allow to access from your ip, hint: [1689001883303762673458360], from ip: xxx.xxx.xxx.xxx, more info at https://open.work.weixin.qq.com/devtool/query?e=60020'}
        # success: {'errcode': 0, 'errmsg': 'ok', 'msgid': '3yzdAQ63LCLTa8NCVqmn2XDsTL3oQir4vxSu6NZvYrF186IzBMslYUNRJi9fEfyPMTKKb2gJBEEiRo3PLa7tag'}
        return WecomApiRespBase.model_validate_json(resp.content)

    def send_autosplit(self, text, touid='@all', max_content_bytes=2048) -> bool:
        """split text into `max_content_bytes` chunks before sending."""
        resps = []
        for chunk in split_text(text, max_content_bytes):
            resps.append(self.send(chunk, touid))
        return all(resp.errcode == SUCCESS for resp in resps)

    def send_image(self, base64_content, touid='@all') -> Optional[WecomApiRespBase]:
        upload_url = f'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.access_token}&type=image'
        upload_response = requests.post(upload_url, files={
            "picture": base64.b64decode(base64_content)
        }, **self.requests_kwargs).json()
        if "media_id" in upload_response:
            media_id = upload_response['media_id']
        else:
            return None

        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}'
        data = {
            "touser": touid,
            "agentid": self.aid,
            "msgtype": "image",
            "image": {
                "media_id": media_id
            },
            "duplicate_check_interval": 600
        }
        resp = requests.post(send_msg_url, data=json.dumps(data), **self.requests_kwargs)
        return WecomApiRespBase.model_validate_json(resp.content)

    def send_markdown(self, text, touid='@all') -> WecomApiRespBase:
        """Only supported in wecom app.

        Not supported: ![alt](url)
        """
        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}'
        data = {
            "touser": touid,
            "agentid": self.aid,
            "msgtype": "markdown",
            "markdown": {
                "content": text
            },
            "duplicate_check_interval": 600
        }
        resp = requests.post(send_msg_url, data=json.dumps(data), **self.requests_kwargs)
        return WecomApiRespBase.model_validate_json(resp.content)

    def send_textcard(self, title, description, url, btntxt='详情', touid='@all'):
        """Supports WeChat, but btntxt is not changeable in WeChat.

        See:
            https://developer.work.weixin.qq.com/document/path/90236#%E6%96%87%E6%9C%AC%E5%8D%A1%E7%89%87%E6%B6%88%E6%81%AF

        Note:
            title limit: 128 bytes
            description limit: 512 bytes
            url limit: 2048 bytes
        """
        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}'
        data = {
            "touser": touid,
            "agentid": self.aid,
            "msgtype": "textcard",
            "textcard": {
                "title": title,
                "description": description,
                "url": url,
                "btntxt": btntxt,
            },
            "duplicate_check_interval": 600
        }
        resp = requests.post(send_msg_url, data=json.dumps(data), **self.requests_kwargs)
        return WecomApiRespBase.model_validate_json(resp.content)

    def upload_temp_media(
        self,
        filename: str,
        content: Union[str, TextIO],
        filelength: int,
        content_type: str,
        media_type: MediaType,
    ) -> WecomApiRespUploadTempMedia:
        """Upload temp media file, expire in 3 days.

        Note:
            大小限制：
            所有文件size必须大于5个字节
            图片（image）：10MB，支持JPG,PNG格式
            语音（voice） ：2MB，播放长度不超过60s，仅支持AMR格式
            视频（video） ：10MB，支持MP4格式
            普通文件（file）：20MB

        See:
            https://developer.work.weixin.qq.com/document/path/90253

        Raises:
            `WecomSanUploadError`, `WecomSanRespError`

        """
        try:
            assert filelength > 5, '所有文件大小必须大于5个字节'
            if media_type == 'image':
                assert filelength <= 10*1024*1024, '图片不得超过10MB'
            elif media_type == 'voice':
                assert filelength <= 2*1024*1024, '语音不得超过2MB'
            elif media_type == 'video':
                assert filelength <= 10*1024*1024, '视频不得超过10MB'
            elif media_type == 'file':
                assert filelength <= 20*1024*1024, '普通文件不得超过20MB'
        except AssertionError as e:
            raise WecomSanUploadError(e)

        upload_url = f'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.access_token}&type={media_type}'
        files = {
            'media': (filename, content, content_type, dict(filelength=filelength))
        }
        resp = requests.post(upload_url, files=files, **self.requests_kwargs)
        respModel = WecomApiRespBase.model_validate_json(resp.content)
        if respModel.errcode == SUCCESS:
            return WecomApiRespUploadTempMedia.model_validate_json(resp.content)
        raise WecomSanRespError(respModel.errcode, respModel.errmsg)

    def upload_html(
            self,
            filename: str,
            content: str,
    ) -> WecomApiRespUploadTempMedia:
        return self.upload_temp_media(filename.replace('.html', '') + '.html', content, len(content), 'text/html', 'file')

    def get_temp_media_url(self, media_id: MediaId) -> str:
        """
        完全公开，media_id在同一企业内所有应用之间可以共享。
        media_id有效期只有3天，注意要及时获取，以免过期。
        """
        return f'https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token={self.access_token}&media_id={media_id}'
