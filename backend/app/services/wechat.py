"""WeChat Mini Program service: exchange login code for openid via code2session."""

import httpx

from app.config import settings

# WeChat code2session endpoint
WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"

# Human-readable mapping for the most common error codes returned by WeChat.
WX_ERRCODE_MSG = {
    40029: "微信 code 无效或已使用",
    40163: "微信 code 已被使用，请重新登录",
    45011: "微信接口调用频率限制，请稍后重试",
    -1: "微信系统繁忙，请稍后重试",
}


def code2session(js_code: str) -> dict:
    """Exchange a mini-program login code for openid + session_key.

    Calls WeChat's `jscode2session` with the app's AppID and AppSecret.
    Returns a dict that always contains `openid` (and usually `session_key`,
    optionally `unionid`). Raises ValueError with a Chinese message if the
    call fails or WeChat returns an error code.

    The returned session_key is not used by this app (we issue our own JWT)
    but is returned for completeness / future use.
    """
    if not settings.WX_APPID or not settings.WX_SECRET:
        raise ValueError("微信登录未配置：请在服务器设置 WX_APPID / WX_SECRET")

    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
        "js_code": js_code,
        "grant_type": "authorization_code",
    }
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(WX_CODE2SESSION_URL, params=params)
    except httpx.HTTPError as e:
        raise ValueError(f"调用微信接口失败：{e}")

    try:
        data = resp.json()
    except ValueError:
        raise ValueError("微信返回内容无法解析")

    # WeChat returns errcode on failure; success responses omit errcode
    # or carry errcode=0. Treat any nonzero errcode as an error.
    errcode = data.get("errcode", 0)
    if errcode:
        msg = WX_ERRCODE_MSG.get(errcode) or data.get("errmsg") or "微信登录失败"
        raise ValueError(f"{msg}({errcode})")

    openid = data.get("openid")
    if not openid:
        raise ValueError("微信未返回 openid")

    return data
