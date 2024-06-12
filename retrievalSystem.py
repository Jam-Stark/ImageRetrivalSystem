from typing import Any
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import numpy as np
import cv2
import os
from scipy.spatial import distance
from getWordVec import embedding

class RetrievalSystem:
    def __init__(self,cursor):
        self.cursor = cursor

    def _cosine_similarity(self,v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    def KeyWordRetrieval(self, inputKeyWord):

        #向量化输入词
        inputKeyWord=np.array(embedding([inputKeyWord])).reshape(768,)

        #获取数据库中的所有图像的词向量
        self.cursor.execute("SELECT image_name,HUMANtags FROM image_store")
        rows = self.cursor.fetchall()

        similaritys=[]
        for row in rows:
            image_id = row[0]
            HUMANtags = row[1]
            #向量化数据库中的词
            HUMANtags=np.frombuffer(HUMANtags,dtype=np.float64).reshape((5, 768))
            #计算余弦相似度
            print(inputKeyWord.shape)
            print(HUMANtags.shape)
            max_similarity = self._cosine_similarity(inputKeyWord, HUMANtags[0])
            for humantag in HUMANtags:
                similarity = self._cosine_similarity(inputKeyWord, humantag)
                if(similarity>max_similarity):
                    max_similarity=similarity
            similaritys.append((image_id, max_similarity))
            #print(f"image_id: {image_id}, similarity: {similarity}")
        #排序并返回前top_k（这里等于5）个
        similaritys.sort(key=lambda x: x[1], reverse=True)
        similaritys = similaritys[:3]

        # 从数据库中获取相似度最高的图片信息
        similar_images = []
        for image_id, _ in similaritys:
            self.cursor.execute("SELECT * FROM image_store WHERE image_name = %s", (image_id,))
            row = self.cursor.fetchone()
            similar_images.append(row)

        return similar_images
    
    
    def CalculateHist(self,image, bins=(8, 8, 8)):
        # 读取代码并统一图片大小(256*256)
        #image = cv2.imread(image_path)
        image = cv2.resize(image, (256, 256))  # 将图像缩放到256x256
        # 使用GrabCut算法提取前景,并将前景和背景分离得到两张图片
        mask = np.zeros(image.shape[:2], np.uint8)
        backmodel = np.zeros((1, 65), np.float64)
        foremodel = np.zeros((1, 65), np.float64)
        rang = (20, 20, 230, 230)
        cv2.grabCut(image, mask, rang, backmodel, foremodel, 15, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        # image_foreground = image * mask2[:, :, np.newaxis]
        # image_background = image * (1 - mask2[:, :, np.newaxis])
        # 计算前景和背景的掩膜
        mask_foreground = np.where((mask == 1) | (mask == 3), 255, 0).astype('uint8')
        mask_background = np.where((mask == 0) | (mask == 2), 255, 0).astype('uint8')

        foreground_histograms = []
        background_histograms = []

        # 将图像分成4x4块
        for i in range(4):
            for j in range(4):
                start_y, end_y = i * 64, (i + 1) * 64
                start_x, end_x = j * 64, (j + 1) * 64
                block = image[start_y:end_y, start_x:end_x]
                # 应用前景掩膜，计算前景直方图
                block_foreground_masked = cv2.bitwise_and(block, block, mask=mask_foreground[start_y:end_y, start_x:end_x])
                hist_foreground = cv2.calcHist([block_foreground_masked], [0, 1, 2], None, bins, [0, 256] * 3)
                cv2.normalize(hist_foreground, hist_foreground)
                foreground_histograms.append(hist_foreground.flatten())
                # 应用背景掩膜，计算背景直方图
                block_background_masked = cv2.bitwise_and(block, block, mask=mask_background[start_y:end_y, start_x:end_x])
                hist_background = cv2.calcHist([block_background_masked], [0, 1, 2], None, bins, [0, 256] * 3)
                cv2.normalize(hist_background, hist_background)
                background_histograms.append(hist_background.flatten())
        return foreground_histograms, background_histograms,mask2

    def CompareHist(self,hist1, hist2):
        return distance.cityblock(hist1, hist2)

    def mask_similarity(self,mask1, mask2):
        # 计算两个掩膜的交集
        intersection = cv2.bitwise_and(mask1, mask2)
        # 计算两个掩膜的并集
        union = cv2.bitwise_or(mask1, mask2)
        jaccard_index = cv2.countNonZero(intersection) / cv2.countNonZero(union)
        return jaccard_index

    def Disimages(self,input_imagepath):
        self.cursor.execute("SELECT image_name,foreg,backg,mask FROM image_store")
        rows = self.cursor.fetchall()
        # 计算输入图片的前景背景的颜色直方图
        input_hist_foreground, input_hist_background,input_mask = self.CalculateHist(input_imagepath)
        distances = []
        # 计算图库中的冰进行比较，将与输入图片的距离输入矩阵中
        for row in rows: 
            image_id=row[0]
            hist_foreground=row[1]   
            hist_background=row[2]
            hist_foreground=np.frombuffer(hist_foreground,dtype=np.float32).reshape((16, 512))
            hist_background=np.frombuffer(hist_background,dtype=np.float32).reshape((16, 512))
            hist_mask=row[3]
            hist_mask=np.frombuffer(hist_mask,dtype=np.uint8).reshape((256, 256))
            dist_foreground = 0
            dist_background = 0
            for i in range(16):
                dist_foreground = dist_foreground+self.CompareHist(input_hist_foreground[i], hist_foreground[i])
                dist_background = dist_background+self.CompareHist(input_hist_background[i], hist_background[i])
            dist = (1-self.mask_similarity(input_mask,hist_mask))*( 0.6 * (dist_foreground/len(hist_foreground)) + 0.4 * (dist_background/len(hist_foreground)))  # 加权平均
            distances.append((image_id, dist))
        distances.sort(key=lambda x: x[1])
        distances = distances[:3]

        similar_images = []
        for image_id, _ in distances:
            self.cursor.execute("SELECT * FROM image_store WHERE image_name = %s", (image_id,))
            row = self.cursor.fetchone()
            similar_images.append(row)
        return similar_images
    
    #写一个根据图片人工添加HUAMNtags的函数
    def addHumanTags(self,connection):
        #遍历数据库中的HUMANtags为None图片
        self.cursor.execute("SELECT image_id, image_info,image_width,image_height,image_color_type,HUMANtags FROM image_store WHERE HUMANtags IS NULL")
        rows = self.cursor.fetchall()
        for row in rows:
            img = Image.frombytes(row[4], (row[2], row[3]), row[1], 'raw')
            img.show()
            image_id = row[0]
            #这里的HUMANtags是一个字符串，用空格分隔的关键词
            human_tags = row[1]
            #终端输入HUMANtags
            print("Please input the HUMANtags of image_id = ", image_id)
            human_tags=input()
            if(human_tags=="exit"):
                break
            human_tags = human_tags.split(" ")
            human_tags = f"{human_tags}".join(human_tags)
            self.cursor.execute("UPDATE image_store SET HUMANtags = %s WHERE image_id = %s", (human_tags, image_id))
        connection.commit()


    def __call__(self,input,type) :
        if type == "KeyWord":
            results=self.KeyWordRetrieval(input)
        elif type == "YOLO":
            results=None     #填补
        elif type == "Color":
            results=self.Disimages(input)
        return results