# coding:utf-8

import os
import re
import json
import time
import requests
import Algorithm
import Constants
from PIL import Image
from io import BytesIO
from AlbumHandler import *

SESSION = requests.session()
VERIFY_CODE_IMG_PATH = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'verifyCode.png'
QR_CODE_IMG_PATH = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'qrCode.png'

class QZoneSpider(object):
    """
        QZoneSpider
    """

    def __init__(self):
        self.pt_guid_sig = ''
        # 扫码登录签名
        self.pt_verifysession_v1 = ''
        # 校验session
        self.verifyCode = ''
        # 16进制登录的QQ号，密码加密需要
        self.cap_cd = ''
        # 请求验证码code
        self.vsig = ''
        # 请求验证码签名
        self.sess = ''
        # sess 
        self.tryVerifyTimes = 0
        # 尝试验证码次数
        self.tryLoginTimes = 0
        # 尝试登录次数


    def qrLogin(self):
        """
            二维码登录流程
        """
        ptqrtoken = self.getQRCode()
        while True:
            time.sleep(3)
            
            resp = SESSION.get(Constants.PT_QR_LOGIN
                            .replace('{app_id}', Constants.APP_ID)
                            .replace('{ptqrtoken}', str(ptqrtoken)), 
                            headers=Constants.REQUEST_HEADER).content

            res = re.search(r'ptuiCB(\(.*\))\;', resp).group(1)
            res = eval(res)
            print res

            code = res[0]
            if code=='0':
                # 扫码成功请求回传重定向地址
                url = res[2]
                print url
                os.remove(QR_CODE_IMG_PATH)
                SESSION.get(url, headers=Constants.REQUEST_HEADER)
                g_tk = Algorithm.g_tk(SESSION.cookies['p_skey'])

                # AlbumHandler(SESSION, g_tk).start(SESSION.cookies['uin'].lstrip('o'))
            elif code == '65':
                print 'refresh QR-Code'
                os.remove(QR_CODE_IMG_PATH)
                ptqrtoken = self.getQRCode()
            elif code == '67':
                print 'confirm login in mobile!'

    def getQRCode(self):
        '''
            取二维码
        '''
        qrImg = SESSION.get(Constants.PT_QR_SHOW
                            .replace('{app_id}', Constants.APP_ID)
                            .replace('{time}', str(time.time())), 
                            headers=Constants.REQUEST_HEADER).content

        im = Image.open(BytesIO(qrImg))
        im.save(QR_CODE_IMG_PATH)
        im.show()
        ptqrtoken = Algorithm.ptqrtoken(SESSION.cookies['qrsig'])

        return ptqrtoken

    def login(self, u_id, pwd):
        """
            登录流程 
        """
        # 登录尝试 登录成功才会继续
        self.tryLoginProcess(u_id, pwd)
        # print SESSION.cookies
        g_tk = Algorithm.g_tk(SESSION.cookies['p_skey'])
        
        AlbumHandler(SESSION, g_tk).start(u_id)
        
    def tryLoginProcess(self, u_id, pwd):
        '''
            尝试登录流程 

            判断是否需要验证码

            需要: 处理sess参数,进入验证码流程
            不需要: 跳转真实登录
        '''
        # 判断是否需要验证码
        self.tryLoginTimes += 1
        print '==================================================='
        print 'NO. '+ str(self.tryLoginTimes) + ' tryLoginProcess!'
        if (self.isNeedVerifyCode(u_id) == '0'):  # 不需要验证码
            print '-> No verifyCode is required'
            self.realLogin(u_id, pwd)
        else:  # 需要验证码
            print '-> VerifyCode is required'
            # 处理sess参数
            self.handleSess(u_id)
            self.tryVerifyCodeProcess(u_id, pwd)

    def tryVerifyCodeProcess(self, u_id, pwd):
        '''
            尝试验证码流程
        '''
        self.tryVerifyTimes += 1
        print '---------------------------------------------------'
        print 'NO. '+ str(self.tryVerifyTimes) + ' tryVerifyCodeProcess!'
        # 处理sig参数和cdata加密所需参数
        cdata = self.handleSigAndCdata(u_id)
        self.handleVerifyCode(u_id)
        self.verifyCode = raw_input('=====>Enter VerifyCode: ').strip()
        # 输入完验证码删除图片
        os.remove(VERIFY_CODE_IMG_PATH)
        # 校验验证码
        errorCode = self.isRightVerifyCode(u_id, cdata)
        if errorCode == '0': # 验证码输入正确 真实登录
            self.realLogin(u_id, pwd)
        elif errorCode == '16': # 重新登录
            self.retryLogin()
        elif errorCode == '50': # 刷新验证码
            print 'Refresh nVerifyCode Image'
            self.tryVerifyCodeProcess(u_id, pwd)
        else: # 未知错误代码 , 可以当做16 重新处理登录
            self.retryLogin()

    def retryLogin(self):
        '''
            重新登录
        '''
        print '=====> u_id or pwd is not right,input to retry login'
        u_id = raw_input('=====> Enter u_id: ').strip()
        pwd = raw_input('=====> Enter pwd: ').strip()
        self.login(u_id, pwd)

    def realLogin(self, u_id, pwd):
        """
            真实登录

            successful: ptuiCB('0','0','loginUrl','0','登录成功！', 'nickName');
            failed:     
                ptuiCB('3','0','','0','用户名密码不正确', '');
                ptuiCB('4','0','','0','用户名密码不正确', ''); 
                3 不需要验证码登录  用户名或密码不正确
                4 需要验证码登录    验证码正确，用户名或密码不正确
                3,4后续就是校验是否需要验证码 然后重复流程
        """
        print 'STEP 2: Start login'
        encodePwd = Algorithm.encodePwd(u_id, pwd, self.verifyCode)

        x = SESSION.get(Constants.REAL_LOGIN
                        .replace('{u_id}', u_id)
                        .replace('{encode_pwd}', encodePwd)
                        .replace('{app_id}', Constants.APP_ID)
                        .replace('{verifycode}', self.verifyCode)
                        .replace('{pt_verifysession_v1}', self.pt_verifysession_v1),
                        headers=Constants.REQUEST_HEADER).content

        print x
        # 截取登录成功返回的重定向地址
        x = x[x.find('(') + 1 : x.find(')')].replace('\'', '').split(',')
        if x[0] == '0':
            # 此处请求返回登录成功的url会自动重定向到loginsucc.html 会设置cookies[p_skey, p_uin, pt4_token]
            SESSION.get(x[2], headers=Constants.REQUEST_HEADER)
        else:
            self.tryLoginProcess(u_id, pwd)
        

    def isNeedVerifyCode(self, u_id):
        """
            判断是否需要验证码：

            ptui_checkVC(flag, {verifycode}|{cap_cd}, {pt_uin}, {pt_verifysession_v1}, {pt_randsalt}) 

            flag: 0 不需要验证码 1 需要验证码
            verifycode: flag=0 登录验证码
            cap_cd: flag=1 获取验证码所需
            pt_uin: 16进制的登录QQ号 真实登录密码加密需要
            pt_verifysession_v1: 验证session
            pt_randsalt: 2为qq登录 3为邮箱登录
        """
        print 'STEP 1: Check if validation code is needed'
        x = SESSION.get(Constants.IS_NEED_VERIFY
                         .replace('{u_id}', u_id)
                         .replace('{app_id}', Constants.APP_ID), 
                         headers=Constants.REQUEST_HEADER).content
        print x

        x = x[x.find('(') + 1: x.find(')')].replace('\'', '').split(',')
        flag = x[0]
        if (flag == '0'):
            self.verifyCode = x[1]
            self.pt_verifysession_v1 = x[3]
        else:
            self.cap_cd = x[1]

        return flag

    def handleSess(self, u_id):
        '''
            验证码预处理 sess
            >>>
            ({
                "state":"1",
                "ticket":"",
                "capclass":"0",
                "subcapclass":"0",
                "src_1":"cap_union_new_show",
                "src_2":"template/new_placeholder.html",
                "src_3":"template/new_slide_placeholder.html",
                "sess":{sess}",
                "randstr":""
            })
        '''
        print 'STEP 2: Handle sess arg'
        sess = SESSION.get(Constants.PREPARE_CAPTCHA_SESS
                            .replace('{u_id}', u_id)
                            .replace('{cap_cd}', self.cap_cd)
                            .replace('{app_id}', Constants.APP_ID), 
                            headers=Constants.REQUEST_HEADER).content
        print sess
        self.sess = json.loads(sess.strip('()'))['sess']

    def handleSigAndCdata(self, u_id):
        """
            处理vsig参数用于获取验证码 返回cdata用于验证码验证
            >>> 
            {
                "vsig":{vsig},
                "ques":"",
                "chlg":{
                    "randstr":{randstr},
                    "M":{M},
                    "ans":{ans}
                }
            }
        """
        print 'STEP 3: Handle sig arg and (randstr, M, ans) for encode cdata arg'
        sigContent = SESSION.get(Constants.GET_CAPTCHA_SIG
                                .replace('{u_id}', u_id)
                                .replace('{sess}', self.sess)
                                .replace('{cap_cd}', self.cap_cd)
                                .replace('{app_id}', Constants.APP_ID), 
                                headers=Constants.REQUEST_HEADER).json()
        print sigContent
        self.vsig = sigContent['vsig']
        randstr = sigContent['chlg']['randstr']
        M = sigContent['chlg']['M']
        ans = sigContent['chlg']['ans']

        return Algorithm.cdata(randstr, ans, M)

    def handleVerifyCode(self, u_id):
        """
            验证码预处理3 获取验证码图片
        """
        print 'STEP 4: Download verifyCode image'
        img = SESSION.get(Constants.GET_CAPTCHA_IMG_BY_SIG
                        .replace('{u_id}', u_id)
                        .replace('{sess}', self.sess)
                        .replace('{vsig}', self.vsig)
                        .replace('{cap_cd}', self.cap_cd)
                        .replace('{app_id}', Constants.APP_ID), 
                        headers=Constants.REQUEST_HEADER).content
        # 保存打开验证码图片
        im = Image.open(BytesIO(img))
        im.save(VERIFY_CODE_IMG_PATH)
        im.show()

        return None

    def isRightVerifyCode(self, u_id, cdata):
        '''
            校验验证码是否正确
            >>> 
            {
                "errorCode":"0",
                "randstr":{randstr},  ->  verifyCode
                "ticket":{ticket},    ->  pt_verifysession_v1
                "errMessage":"",
                "sess":""
            }
            0 验证码正确 获取{randstr}{ticket} 进行真实登录请求
            16 用户名或密码不正确              重新输入登录
            50 验证码不正确 或者提交参数不正确  刷新验证码 
        '''
        print 'STEP 5: verification verifyCode'
        verifyPostData = {
            'aid': Constants.APP_ID,
            'uid': u_id,
            'sess': self.sess,
            'cap_cd': self.cap_cd,
            'vsig': self.vsig,
            'cdata': cdata,
            'ans': self.verifyCode
        }

        resp = SESSION.post(Constants.CAPTAHA_VERIFY, data=verifyPostData, headers=Constants.REQUEST_HEADER).json()
        print resp
        errorCode = resp['errorCode']
        if errorCode == '0':
            self.verifyCode = resp['randstr']
            self.pt_verifysession_v1 = resp['ticket']
        return errorCode
