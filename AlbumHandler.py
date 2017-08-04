# coding:utf-8

import os
import json
import time
import urllib
import requests
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
        x = self.session.get(Constants.LIST_ALBUM
                        .replace('{g_tk}', str(self.g_tk))
                        .replace('{u_id}', u_id), 
                        headers=Constants.REQUEST_HEADER).content
        x = json.loads(x[x.find('(') + 1 : x.find(')')])

        # 遍历相册进行下载
        for album in x['data']['albumListModeSort']:
            topicId = album['id']
            # name = album['name'] 中文乱码 先用id处理
            total = album['total'] # 该相册相片总数

            # 创建相册保存路径
            albumPath = uidImgPath + os.sep + topicId
            if not os.path.exists(albumPath):
                os.mkdir(albumPath)

            page = total / PAGE_NUM + 1
            remainder = total % PAGE_NUM
            
            print '-----------album %s start download----------------------'%(topicId)
            # 分页下载
            pageStart = 1
            currPage = 1
            currPhoto = 1
            while currPage <= page:
                pageStart = (currPage-1) * PAGE_NUM
                isLast = True if page==currPage else False
                pageNum = remainder if isLast else PAGE_NUM

                # 请求具体相册
                photo = self.session.get(Constants.LIST_PHOTO
                                    .replace('{g_tk}', str(self.g_tk))
                                    .replace('{u_id}', u_id)
                                    .replace('{topicId}', topicId)
                                    .replace('{pageStart}', str(pageStart))
                                    .replace('{pageNum}', str(pageNum)), 
                                    headers=Constants.REQUEST_HEADER).content

                time.sleep(1)
                photo = json.loads(photo[photo.find('(') + 1 : photo.find(')')])
                for photo in photo['data']['photoList']:
                    pid = photo['lloc']
                    purl = photo['url']
                    imgPath = albumPath + os.sep + str(pid) + '.jpg'

                    if not os.path.exists(imgPath):
                        print '[%s/%s page]: [%s / %s] downloading: %s'%(currPage, page, currPhoto, total, purl) 
                        self.imgDownload(purl, imgPath, 1)
                    else:
                        print 'photo %s exists, continue.' %(pid)
                    currPhoto += 1

                currPage += 1

            print '-----------album %s end download----------------------'%(topicId)
    
    def downLoadProcess(self, blocknum, blocksize, totalsize):
        '''
            下载进度 urllib.urlretrieve使用
        '''
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        print "%.2f%%"% percent

    def imgDownload(self, url, imgPath, times):
        '''
            下载图片：异常重新下载
        '''
        try:
            time.sleep(1)
            req = requests.get(url, headers=Constants.REQUEST_HEADER)
            
            #urllib.urlretrieve(url, imgPath, self.downLoadProcess)
        except Exception:
            times += 1
            if times == 3:
                print 'redownloading failed, continue...'
                return
            
            print 'try %d times download %s failed.Redownloading..'%(times, url)
            self.imgDownload(url, imgPath, times)
