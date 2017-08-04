# coding:utf-8

import os
import json
import time
import requests
import Constants

PAGE_NUM = 30
IMG_DOWNLOAD_PATH = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'downloadImgs'
DOWNLOAD_FAILED_IMG_PATH = IMG_DOWNLOAD_PATH + os.sep + 'downloadFailedImg.txt'

class AlbumHandler(object):
    '''
        相册处理
    '''
    def __init__(self, session, g_tk):
        if not os.path.exists(IMG_DOWNLOAD_PATH):
            os.mkdir(IMG_DOWNLOAD_PATH)
        if os.path.exists(DOWNLOAD_FAILED_IMG_PATH):
            os.remove(DOWNLOAD_FAILED_IMG_PATH)

        self.session = session    
        self.g_tk = g_tk

    def start(self, u_id):
        '''
            分页下载相册图片
        '''
        # 创建用户u_id下载图片文件夹
        uidImgPath = IMG_DOWNLOAD_PATH + os.sep + u_id
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
                        if self.imgDownload(purl, imgPath, 0):
                            print '[%s/%s page]: [%s / %s] downloaded: %s'%(currPage, page, currPhoto, total, purl) 
                    else:
                        print 'photo %s exists, continue.' %(pid)
                    currPhoto += 1

                currPage += 1

            print '-----------album %s end download----------------------'%(topicId)
    
    def imgDownload(self, url, imgPath, times):
        '''
            下载图片：异常重新下载
        '''
        try:
            #TODO 下载丢失，捕获不到异常，怎么回事
            resp = requests.get(url, headers=Constants.REQUEST_HEADER)
            times += 1
            time.sleep(2)
            if resp.status_code==200:
                if len(resp.content)<20000:
                    print resp.content
                with open(imgPath, 'wb') as f:
                    f.write(resp.content)
                return True
            else:
                resp.raise_for_status()
        except Exception as e:
            if times == 3:
                print '%s redownloading failed, giving up...'%(e.message)
                with open(DOWNLOAD_FAILED_IMG_PATH, 'a') as f:
                    f.writelines(url+"\n")

                return False
            
            print 'try %d times download %s failed.Redownloading..'%(times, url)
            self.imgDownload(url, imgPath, times)