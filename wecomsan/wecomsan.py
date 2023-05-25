import base64
import json
import requests
from typing import Optional


class WecomSan:
    def __init__(self, cid, aid, secret, access_token=None):
        self.cid = cid
        self.aid = aid
        self.secret = secret
        self._access_token = access_token

    @property
    def access_token(self):
        if self._access_token and len(self._access_token) > 0:
            return self._access_token

        get_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.cid}&corpsecret={self.secret}"
        self._access_token = requests.get(get_token_url).json().get('access_token')
        if self._access_token and len(self._access_token) > 0:
            return self._access_token

        raise ModuleNotFoundError('fail to get access token')

    def send(self, text, touid='@all') -> str:
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
        return requests.post(send_msg_url, data=json.dumps(data)).text

    def send_image(self, base64_content, touid='@all') -> Optional[str]:
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
        return requests.post(send_msg_url, data=json.dumps(data)).text

    def send_markdown(self, text, touid='@all') -> str:
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
        return requests.post(send_msg_url, data=json.dumps(data)).text

