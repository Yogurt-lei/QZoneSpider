# coding:utf-8

import os
import json
import time
import urllib
import Constants

PAGE_NUM = 30

class AlbumHandler(object):
    '''
        相册处理
    '''
    IMG_DOWNLOAD_PATH = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'downloadImgs'

    def __init__(self, session, g_tk):
        if not os.path.exists(self.IMG_DOWNLOAD_PATH):
            os.mkdir(self.IMG_DOWNLOAD_PATH)

        self.session = session
        self.g_tk = g_tk

    def start(self, u_id):
        '''
            分页下载相册图片
        '''
        # 创建用户u_id下载图片文件夹
        uidImgPath = self.IMG_DOWNLOAD_PATH + os.sep + u_id
        if not os.path.exists(uidImgPath):
            os.mkdir(uidImgPath)

        # 请求相册列表
        x = self.session.get(Constants.LIST_ALBUM.replace('{g_tk}', str(self.g_tk)).replace('{u_id}', u_id)).content
        x = json.loads(x[x.find('(') + 1 : x.find(')')])

        # 遍历相册进行下载
        for album in x['data']['albumListModeSort']:
            topicId = album['id']
            name = album['name'].encode('utf-8')
            total = album['total']

            # 创建相册保存路径
            albumPath = uidImgPath + name
            if not os.path.exists(albumPath):
                os.mkdir(albumPath)

            page = total / PAGE_NUM
            remainder = total % PAGE_NUM
            
            print '-----------album %s start download----------------------'%(name)
            # 分页下载
            pageStart = 0
            currPage = 0
            currPhoto = 0
            while currPage <= page:
                pageStart = currPage * PAGE_NUM
                isLast = True if page==currPage else False
                pageNum = pageStart + (remainder if isLast else PAGE_NUM)

                print '[%s/%s page], album %s is downloading...'%(currPage, page, name)
                photo = self.session.get(Constants.LIST_PHOTO
                                        .replace('{g_tk}', self.g_tk)
                                        .replace('{u_id}', u_id)
                                        .replace('{topicId}', topicId)
                                        .replace('{pageStart}', pageStart)
                                        .replace('{pageNum}', pageNum)).content

                time.sleep(0.1)
                photo = json.loads(photo[photo.find('(') + 1 : photo.find(')')])
                for photo in photo['data']['photoList']:
                    pid = photo['modifytime']
                    purl = photo['url']
                    urllib.urlretrieve(purl, albumPath+str(pid)+'.jpg')
                    currPhoto += 1
                    print '[%s / %s] photo downloading: %s'%(currPhoto,total,purl) 

            print '-----------album %s end download----------------------'%(name)

def main():
    total = 227
    page =  total/PAGE_NUM
    remainder = total%PAGE_NUM

    currPage = 0
    while currPage <= page:
        pageStart = currPage*PAGE_NUM
        
        isLast = True if page==currPage else False
        pageNum = pageStart + (remainder if isLast else PAGE_NUM)

        print str(currPage) + ': ' + str(pageStart) + '--> '+ str(pageNum)
        currPage += 1

if __name__ == '__main__':
    main()