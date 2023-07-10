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
if ret.errcode != 0:
    print(ret.errmsg)

ret = wecomsan.send_autosplit('超长文本', max_content_bytes=2048)  # split into multiple chunks if length exceeds 2048 bytes
ret = wecomsan.send('<a href="https://www.github.com/">文本中支持超链接</a>')
ret = wecomsan.send_image("此处填写图片Base64")
ret = wecomsan.send_markdown("**Markdown 内容**")  # 只支持企业微信查看。不支持`![]()`的图片格式
ret = wecomsan.send_textcard(
    '领奖通知',
    ("<div class=\"gray\">2016年9月26日</div> <div class=\"normal\">"
     "恭喜你抽中iPhone 7一台，领奖码：xxxx</div><div class=\"highlight\">"
     "请于2016年10月10日前联系行政同事领取</div>"),
    "URL")  # 微信也可以查看，但不支持修改btntxt、description的html不支持class高亮.
```