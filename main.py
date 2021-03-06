#-*- coding: UTF-8 -*-

from QZoneSpider import *

''' 
    QQ空间相册爬虫
        
    密码加密算法 TEA+RSA

    @date 2017-7-28 13:03:47
    @author Yogurt_lei

    qZone.js -> encodePwd(u_id, pwd, verifycode) 获取加密后密码
    qZone.js -> cdata(randstr, ans, M)  获取cdata参数值
    qZone.js -> g_tk(p_skey) GTK算法
    qZone.js -> ptqrToken(qrsig) ptqrtoken算法

 '''

if __name__ == '__main__':
    
    print 'QZone Spider Start.....'
    print '1. QR-Code Login'
    print '2. General Login'
    choose = raw_input("Enter choose number: ").strip()
    
    try:
        if choose=='1':
            QZoneSpider().qrLogin()
        else:
            u_id = raw_input('Enter QQ u_id:').strip()
            pwd = raw_input('Enter QQ pwd :').strip()

            QZoneSpider().login(u_id, pwd)
        
    except Exception as e:
        print e.message    

    print 'QZone Spider End.....'

    raw_input('Press any key to quit....')
    
