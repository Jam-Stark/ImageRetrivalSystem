
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import PIL.Image as Image
import PIL.ImageTk as ImageTk
from io import BytesIO
import mysql.connector
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
    retrieval_system = RetrievalSystem(cursor) 
# 您的原始 display_image 函数

def display_image(images, parent_window):
    # 创建一个新的Toplevel窗口用于显示图片
    image_display_window = tk.Toplevel(parent_window)
    image_display_window.title("Searched Images Display")
    
    # 确定每行显示的图像数量，这里我们简单设置为每行3张
    images_per_row = 3
    current_row = 0
    column_width = len(images) // images_per_row
    
    for i, img in enumerate(images):
        # 创建一个Label用于显示图片
        image_label = ttk.Label(image_display_window)
        
        # 尝试将PIL图像转换为Tkinter的PhotoImage对象并显示
        try:
            tk_img = ImageTk.PhotoImage(img)
            
            # 显示图片
            image_label.configure(image=tk_img)
            image_label.image = tk_img  # 保持对新图片的引用
            # 使用grid布局管理器来放置Label
            image_label.grid(row=current_row, column=i % images_per_row, pady=10, padx=10)
            
            # 每行的图像数量达到设定值，则增加行数
            if (i + 1) % images_per_row == 0:
                current_row += 1
        except Exception as e:
            messagebox.showerror("错误", f"无法显示图片: {e}")

    # 调整窗口大小以适应所有图像
    image_display_window.grid_columnconfigure("all", uniform=1, weight=1)
    image_display_window.update_idletasks()  # 更新窗口以计算正确的大小
    window_width = image_display_window.winfo_width()
    window_height = image_label.winfo_reqheight() * (current_row + 1)
    image_display_window.geometry(f"{window_width}x{window_height}")
# 假设这是处理二进制数据并展示图片的函数
def process_and_display_image(binary_data, parent_window):
    # 将二进制数据转换为图片对象
    img = Image.open(BytesIO(binary_data))
    tk_img = ImageTk.PhotoImage(img)
    
    # 使用您的 display_image 函数展示图片
    display_image(tk_img, parent_window)


def send_text_to_backend(text_data):
    # 假设这是接收后端发送的来自文本上传的二进制数据列表的函数
    result = retrieval_system(text_data, "KeyWord")
    images = []
    for i in range(min(3, len(result))):  # 只处理前三张图像
        img = Image.frombytes(result[i][4], (result[i][2], result[i][3]), result[i][1], 'raw')
        images.append(img)
    display_image(images, root)  # 使用新的函数显示多张图像

        # 修改后的发送文本数据到后端的函数

def send_file_to_backend():
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        result = retrieval_system(image, "Color")
        images = []
        for i in range(min(3, len(result))):  # 只处理前三张图像
            img = Image.frombytes(result[i][4], (result[i][2], result[i][3]), result[i][1], 'raw')
            images.append(img)
        display_image(images, root)  # 使用新的函数显示多张图像

# 搜索功能的修改
def search():
    user_input = entry.get()
    if user_input.strip():
        # 发送文本到后端
        send_text_to_backend(user_input)
    else:
        messagebox.showwarning("警告", "请输入要搜索的文本。")

# 打开文件功能的修改
def open_file():
    # 让用户选择文件，然后发送文件到后端
    send_file_to_backend()


# 显示开发人员介绍
def show_developer_info():
    if not hasattr(show_developer_info, "dev_info"):
        show_developer_info.dev_info = tk.Toplevel(root)
        show_developer_info.dev_info.title("开发人员介绍")

        label = ttk.Label(show_developer_info.dev_info, text="开发人员：曹宝泉", font=("Arial", 12))
        label.pack(pady=10)

        contact_label = ttk.Label(show_developer_info.dev_info, text="学号：20212251055", font=("Arial", 10))
        contact_label.pack()
        label = ttk.Label(show_developer_info.dev_info, text="开发人员：刘卓", font=("Arial", 12))
        label.pack(pady=10)

        contact_label = ttk.Label(show_developer_info.dev_info, text="学号：20212251193", font=("Arial", 10))
        contact_label.pack()
        label = ttk.Label(show_developer_info.dev_info, text="开发人员：任彦铭", font=("Arial", 12))
        label.pack(pady=10)

        contact_label = ttk.Label(show_developer_info.dev_info, text="学号：20212251058", font=("Arial", 10))
        contact_label.pack()
        label = ttk.Label(show_developer_info.dev_info, text="开发人员：薛一鸣", font=("Arial", 12))
        label.pack(pady=10)

        contact_label = ttk.Label(show_developer_info.dev_info, text="学号：20212251055", font=("Arial", 10))
        contact_label.pack()
        label = ttk.Label(show_developer_info.dev_info, text="开发人员：周树晖", font=("Arial", 12))
        label.pack(pady=10)

        contact_label = ttk.Label(show_developer_info.dev_info, text="学号：20212251111", font=("Arial", 10))
        contact_label.pack()
        label = ttk.Label(show_developer_info.dev_info, text="开发人员：赵实", font=("Arial", 12))
        label.pack(pady=10)

        contact_label = ttk.Label(show_developer_info.dev_info, text="学号：20212251155", font=("Arial", 10))
        contact_label.pack()
        close_button = ttk.Button(show_developer_info.dev_info, text="关闭", command=show_developer_info.dev_info.destroy)
        close_button.pack(pady=5)

    # 将窗口置于最前
    show_developer_info.dev_info.lift()
# 创建主窗口
root = tk.Tk()
root.title("Intelligent image retrieval system")
root.minsize(800, 600)

# 创建一个Label，用于显示背景图片
background_label = tk.Label(root)
background_label.pack(fill="both", expand=True)  # 填充整个窗口

# 加载背景图片并将其设置为Label的图像
# 将 YOUR_BACKGROUND_IMAGE_PATH 替换为你的背景图片的实际路径
background_image_path = 'test_img/background.jpg'
try:
    background_image = Image.open(background_image_path)
    #background_image = background_image.resize((800, 600), Image.ANTIALIAS)  # 根据窗口大小调整图片大小
    background_photo = ImageTk.PhotoImage(background_image)
    background_label.config(image=background_photo)  # 设置Label的图像
    background_label.image = background_photo  # 保持对图片的引用
except Exception as e:
    messagebox.showerror("错误", f"无法加载背景图片: {e}")

# 设置布局的权重，使得行和列可以随着窗口大小变化而变化
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=0)  # 标题行不扩展
root.rowconfigure(1, weight=0)  # 搜索行不扩展
root.rowconfigure(2, weight=1)  # 最后一行扩展，用于放置底部按钮

# 设置样式
style = ttk.Style()
style.configure("TButton", font=("Arial", 10, "bold"), padding=6, 
                background="gray", 
                foreground="black",
                borderwidth=20, 
                relief="flat")  # 定义了按钮的基本样式

# 添加居中的标题
title_font = ("Comic Sans MS", 24, "bold")
title_label = tk.Label(root, text="Intelligent image retrieval system", font=title_font, bg="grey", fg="orange")
title_label.place(relx=0.5, rely=0.1, anchor='center')

# 创建输入框，并添加灰色提示文字
entry = tk.Entry(root, font=("Arial", 10), bg="white", fg="black", width=60)
entry.place(relx=0.5, rely=0.2, anchor='center')
entry.insert(0, "Please enter the item you want to retrieve or upload image.")

# 定义当搜索框获得焦点时的事件处理函数
def entry_focus_in(event):
    if event.widget.get() == "Please enter the item you want to retrieve or upload image.":
        event.widget.delete(0, tk.END)  # 删除默认文本
        event.widget.config(fg="black")  # 将文字颜色改为黑色

# 定义当搜索框失去焦点时的事件处理函数
def entry_focus_out(event):
    if not event.widget.get():  # 如果输入框为空
        event.widget.insert(0, "Please enter the item you want to retrieve or upload image.")  # 重新插入默认文本
        event.widget.config(fg="grey")  # 将文字颜色改回灰色

entry.bind("<FocusIn>", entry_focus_in)
entry.bind("<FocusOut>", entry_focus_out)

# 创建搜索按钮和上传图片按钮，放在搜索框的右侧
search_button = ttk.Button(root, text="Search", command=search, style="TButton")
search_button.place(relx=0.4, rely=0.3, anchor='center')

open_file_button = ttk.Button(root, text="Upload Image", command=open_file, style="TButton")
open_file_button.place(relx=0.6, rely=0.3, anchor='center')

# 创建底部Frame，用于放置将显示在底部的按钮
bottom_frame = tk.Frame(root, bg="#424242")
bottom_frame.place(relx=0.5, rely=0.9, anchor='center')

# 创建开发人员介绍按钮和测试按钮，并将它们放置在底部Frame中，水平居中
dev_info_button = ttk.Button(bottom_frame, text="Developer Info", command=show_developer_info, style="TButton")
test_image_button = ttk.Button(bottom_frame, text="Test Display Image", command=lambda: display_image("D:/UI/test_image.jpg", root), style="TButton")

# 使用pack布局将按钮放置在Frame中，并且让它们在Frame中水平居中
dev_info_button.pack(side=tk.LEFT, padx=5, pady=5)
test_image_button.pack(side=tk.RIGHT, padx=5, pady=5)

# 运行主循环
root.mainloop()