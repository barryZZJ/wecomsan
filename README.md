# wecomsan

Referenced from [wecomchan](https://github.com/easychen/wecomchan)

## Usage

`pip install weconsan`

```python
from wecomsan import WecomSan

cid = 'xxx'
aid = 'xxx'
secret = 'xxx'
access_token = 'xxx'
wecomsan = WecomSan(cid, aid, secret, access_token)

ret = wecomsan.send("推送测试\r\n测试换行")  # \n only is ok
print(ret)
ret = wecomsan.send('<a href="https://www.github.com/">文本中支持超链接</a>')
print(ret)
ret = wecomsan.send_image("此处填写图片Base64")
print(ret)
ret = wecomsan.send_markdown("**Markdown 内容**")  # 只支持企业微信查看。不支持`![]()`的图片格式
print(ret)
```