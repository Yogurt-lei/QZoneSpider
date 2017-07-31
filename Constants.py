#-*- coding: UTF-8 -*-
# 2017-7-27 19:58:08
# By Yogurt_lei

"""
    全局定义相关请求地址:

    u_id: 登录QQ号
    encode_pwd: 加密密码
    verifycode: 登录验证码
    topicId: 相册ID
    pageStart: 当前页开始位置
    pageNum: 当前页大小
"""

# 当前腾讯版本号
APP_ID = "549000912"

# GET 预登陆处理pt_login_sig参数
# PREPARE_LOGIN = "https://xui.ptlogin2.qq.com/cgi-bin/xlogin?appid={app_id}&s_url=https://qzs.qzone.qq.com/qzone/v5/loginsucc.html?para=izone&from=iqq"

# GET 扫码登录
REFRESH_QRCODE = "https://ssl.ptlogin2.qq.com/ptqrlogin?aid={app_id}&pt_guid_sig={pt_guid_sig}&u1=https://qzs.qzone.qq.com/qzone/v5/loginsucc.html?para=izone&ptqrtoken=500593639&ptredirect=1&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=4-6-1501073549024&js_ver=10226&js_type=1&pt_uistyle=40"

# GET 是否需要验证码验证
IS_NEED_VERIFY = "https://ssl.ptlogin2.qq.com/check?appid={app_id}&uin={u_id}&pt_tea=2&pt_vcode=1&u1=https://qzs.qzone.qq.com/qzone/v5/loginsucc.html?para=izone&from=iqq"

# GET 真实登录地址
REAL_LOGIN = "https://ssl.ptlogin2.qq.com/login?aid={app_id}&u={u_id}&p={encode_pwd}&verifycode={verifycode}&pt_verifysession_v1={pt_verifysession_v1}&pt_vcode_v1=0&pt_randsalt=2&u1=https://qzs.qzone.qq.com/qzone/v5/loginsucc.html?para=izone&from=iqq&from_ui=1&pt_uistyle=40&daid=5"

# ---- 验证码操作 ----
# GET 验证码预处理sess参数
PREPARE_CAPTCHA_SESS = "https://ssl.captcha.qq.com/cap_union_prehandle?aid={app_id}&uid={u_id}&cap_cd={cap_cd}"

# GET 验证码sig
GET_CAPTCHA_SIG = "https://ssl.captcha.qq.com/cap_union_new_getsig?aid={app_id}&uid={u_id}&cap_cd={cap_cd}&sess={sess}&ischartype=1"

# GET 验证码图片
GET_CAPTCHA_IMG_BY_SIG = "https://ssl.captcha.qq.com/cap_union_new_getcapbysig?aid={app_id}&uid={u_id}&cap_cd={cap_cd}&sess={sess}&vsig={vsig}&ischartype=1"

# POST 验证码验证
CAPTAHA_VERIFY = "http://captcha.qq.com/cap_union_new_verify"#?aid={app_id}&uid={u_id}&sess={sess}&cap_cd={cap_cd}&vsig={vsig}&cdata={cdata}$ans={verifycode}

# ---- 以下为登录后操作部分 ----
# GET 相册列表
LIST_ALBUM = "https://h5.qzone.qq.com/proxy/domain/alist.photo.qq.com/fcgi-bin/fcg_list_album_v3?g_tk={g_tk}&hostUin={u_id}&uin={u_id}&inCharset=utf-8&outCharset=utf-8"

# GET 图片列表
LIST_PHOTO = "https://h5.qzone.qq.com/proxy/domain/plist.photo.qzone.qq.com/fcgi-bin/cgi_list_photo?g_tk={g_tk}&hostUin={u_id}&topicId={topicId}&uin={u_id}&pageStart={pageStart}&pageNum={pageNum}&inCharset=utf-8&outCharset=utf-8&outstyle=json&format=jsonp"
