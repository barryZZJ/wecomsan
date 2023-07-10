import base64
import json
import requests
from typing import Optional

from wecomsan.models import WecomApiResponse


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
    def __init__(self, cid, aid, secret):
        self.cid = cid
        self.aid = aid
        self.secret = secret

    @property
    def access_token(self):
        get_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.cid}&corpsecret={self.secret}"
        access_token = requests.get(get_token_url).json().get('access_token')
        if access_token and len(access_token) > 0:
            return access_token

        raise ModuleNotFoundError('fail to get access token')

    def send(self, text, touid='@all') -> WecomApiResponse:
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
        resp = requests.post(send_msg_url, data=json.dumps(data))
        # resp example:
        # fail: {'errcode': 60020, 'errmsg': 'not allow to access from your ip, hint: [1689001883303762673458360], from ip: xxx.xxx.xxx.xxx, more info at https://open.work.weixin.qq.com/devtool/query?e=60020'}
        # success: {'errcode': 0, 'errmsg': 'ok', 'msgid': '3yzdAQ63LCLTa8NCVqmn2XDsTL3oQir4vxSu6NZvYrF186IzBMslYUNRJi9fEfyPMTKKb2gJBEEiRo3PLa7tag'}
        return WecomApiResponse.model_validate_json(resp.content)

    def send_autosplit(self, text, touid='@all', max_content_bytes=2048) -> bool:
        """split text into `max_content_bytes` chunks before sending."""
        resps = []
        for chunk in split_text(text, max_content_bytes):
            resps.append(self.send(chunk, touid))
        return all(resp.errcode == 0 for resp in resps)

    def send_image(self, base64_content, touid='@all') -> Optional[WecomApiResponse]:
        upload_url = f'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.access_token}&type=image'
        upload_response = requests.post(upload_url, files={
            "picture": base64.b64decode(base64_content)
        }).json()
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
        resp = requests.post(send_msg_url, data=json.dumps(data))
        return WecomApiResponse.model_validate_json(resp.content)

    def send_markdown(self, text, touid='@all') -> WecomApiResponse:
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
        resp = requests.post(send_msg_url, data=json.dumps(data))
        return WecomApiResponse.model_validate_json(resp.content)

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
        resp = requests.post(send_msg_url, data=json.dumps(data))
        return WecomApiResponse.model_validate_json(resp.content)
