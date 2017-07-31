#-*- coding: UTF-8 -*-

import os
import PyV8

QZONE_JS_PATH = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'qZone.js'

jsFile = open(QZONE_JS_PATH, 'rb')
jsContent = jsFile.read()

# python调用js获取加密后密码
js = PyV8.JSContext()
js.enter()
js.eval(jsContent)

def encodePwd(u_id, pwd, verifyCode):
    '''
        登录明文密码加密算法
    '''
    return js.locals.encodePwd(u_id, pwd, verifyCode)

def cdata(randstr, ans, M):
    '''
        校验验证码cdata算法
    '''
    return js.locals.cdata(randstr, ans, M)

def g_tk(p_skey):
    '''
        登录成功后续的GTK算法
    '''
    return js.locals.g_tk(p_skey)