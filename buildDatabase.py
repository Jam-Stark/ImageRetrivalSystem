import mysql.connector
import numpy as np
import os
from PIL import Image
from scipy.spatial import distance
import cv2
from getWordVec import embedding

image_folder = "images"  # 图片文件夹


def CalculateHist(image_path, bins=(8, 8, 8)):
    # 读取代码并统一图片大小(256*256)
    image = cv2.imread(image_path)
    image = cv2.resize(image, (256, 256))  # 将图像缩放到256x256
    # 使用GrabCut算法提取前景,并将前景和背景分离得到两张图片
    mask = np.zeros(image.shape[:2], np.uint8)
    backmodel = np.zeros((1, 65), np.float64)
    foremodel = np.zeros((1, 65), np.float64)
    rang = (20, 20, 230, 230)
    cv2.grabCut(image, mask, rang, backmodel, foremodel, 15, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    image_foreground = image * mask2[:, :, np.newaxis]
    image_background = image * (1 - mask2[:, :, np.newaxis])
    # 计算前景和背景的掩膜
    mask_foreground = np.where((mask == 1) | (mask == 3), 255, 0).astype('uint8')
    mask_background = np.where((mask == 0) | (mask == 2), 255, 0).astype('uint8')

    foreground_histograms = []
    background_histograms = []

    # 将图像分成4x4块
    for i in range(4):
        for j in range(4):
            # 计算每块的坐标
            start_y, end_y = i * 64, (i + 1) * 64
            start_x, end_x = j * 64, (j + 1) * 64

            # 提取前景和背景的图像块
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

    # 返回两个列表
    return foreground_histograms, background_histograms,mask2

# 连接到MySQL数据库
connection = mysql.connector.connect(
    host="localhost",
    port=3330,
    user="root",
    password="111111",
    database="imagestore"
)

if connection.is_connected():
    # 创建游标对象
    cursor = connection.cursor()
    #先删去原有的表
    cursor.execute("DROP TABLE IF EXISTS image_store")
    create_tabel_sql = """
    CREATE TABLE IF NOT EXISTS image_store (
        image_name VARCHAR(100) PRIMARY KEY,
        image_info LONGBLOB,
        image_width INT,
        image_height INT,
        image_color_type VARCHAR(10),
        foreg LONGBLOB,
        backg LONGBLOB,
        YOLOtags VARCHAR(255),
        HUMANtags LONGBLOB,
        mask LONGBLOB
    )
    """

    #给image_store表添加新列mask
    #cursor.execute("ALTER TABLE image_store ADD mask LONGBLOB")

    cursor.execute(create_tabel_sql)
    '''
    # 读取文件夹内的jpg图片
    #统计图片数量
    image_count = 0
    for filename in os.listdir(image_folder):
        if filename.endswith(".jpg"):
            image_count += 1
    print(f"共有{image_count}张图片")
    i=0
    for filename in os.listdir(image_folder):
        if filename.endswith(".jpg"):
            image_path = os.path.join(image_folder, filename)
            # 获取图片信息
            image = Image.open(image_path)
            image_info = image.tobytes()
            foreg,backg=get_foreg_backg(image_path)
            print(f"foreg.size: {foreg.size} foreground_hist.dtype: {foreg.dtype}")
            print(f"backg.size: {backg.size} background_hist.dtype: {backg.dtype}")
            foreg = foreg.tobytes()
            backg = backg.tobytes()
            image_width, image_height = image.size
            image_color_type = image.mode
            #YOLOtags = get_YOLO_tags(image_path)
            YOLOtags = None
            HumanTags = None  # 先空置
            # 插入图片信息到数据库中
            insert_query = """
            INSERT INTO image_store (image_info, image_width, image_height, image_color_type, foreg, backg, YOLOtags, HUMANtags)
            VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
            """
            cursor.execute(insert_query, (image_info, image_width,image_height,image_color_type ,foreg, backg, YOLOtags, HumanTags))
            i+=1
            print(f"已插入{i}张图片")

    '''
    #读取json文件
    import json
    with open('E:\\ai_challenger_caption_validation_20170910\\caption_validation_annotations_20170910.json','r') as f:
        img_hint = json.load(f)
    #根据img_hint中的图片路径读取图片
    print(f"共有{len(img_hint)}张图片")
    for i in range(len(img_hint)):
        image_path = "E:\\ai_challenger_caption_validation_20170910\caption_validation_images_20170910\\"+img_hint[i]['image_id']
        image = Image.open(image_path)
        image_info = image.tobytes()
        foreg,backg,mask=CalculateHist(image_path)
        foreg = np.array(foreg)
        backg = np.array(backg)
        mask = np.array(mask)
        print(f"foreg.size: {foreg.shape} foreground_hist.dtype: {foreg.dtype}")
        print(f"backg.size: {backg.shape} background_hist.dtype: {backg.dtype}")
        print(f"mask.size: {mask.shape} mask.dtype: {mask.dtype}")
        foreg = foreg.tobytes()
        backg = backg.tobytes()
        image_width, image_height = image.size
        image_color_type = image.mode
        #YOLOtags = get_YOLO_tags(image_path)
        YOLOtags = None
        HumanTags = np.array(embedding(img_hint[i]['caption']))
        print(f"HumanTags.size: {HumanTags.size} HumanTags.dtype: {HumanTags.dtype} HumanTags.shape: {HumanTags.shape}")
        HumanTags = HumanTags.tobytes()
        # 插入图片信息到数据库中
        insert_query = """
        INSERT INTO image_store (image_name,image_info, image_width, image_height, image_color_type, foreg, backg, YOLOtags, HUMANtags,mask)
        VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s, %s)
        """
        cursor.execute(insert_query, (img_hint[i]['image_id'],image_info, image_width,image_height,image_color_type ,foreg, backg, YOLOtags, HumanTags,mask.tobytes()))
        print(f"已插入{i}张图片")
        if i%100==0:
            connection.commit()
            print("已提交100张图片")
    connection.commit()  # 提交事务

    # 关闭游标和连接
    cursor.close()
connection.close()
