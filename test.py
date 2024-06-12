import mysql.connector
from PIL import Image
from retrievalSystem import RetrievalSystem
import cv2
# 连接数据库
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

'''
# 创建RetrievalSystem对象
retrieval_system = RetrievalSystem(cursor)
image_path='E:\\ai_challenger_caption_validation_20170910\\caption_validation_images_20170910\\0b263a0ababa73819ca85286e74f15194ce21bca.jpg'
image = cv2.imread(image_path)
result=retrieval_system(image,"Color")
for i in range(len(result)):
        img = Image.frombytes(result[i][4], (result[i][2], result[i][3]), result[i][1], 'raw')
        img.show()
'''

key=input("请输入关键词：")
while key!="exit":
     # 创建RetrievalSystem对象
     retrieval_system = RetrievalSystem(cursor)
     # 进行关键词检索
     result=retrieval_system(key,"KeyWord")
     #得到的二进制结果转化成jpg图片显示
     for i in range(len(result)):
         img = Image.frombytes(result[i][4], (result[i][2], result[i][3]), result[i][1], 'raw')
         img.show()
     key=input("请输入关键词：")





print("退出检索系统")




# 关闭游标和连接
cursor.close()
connection.close()