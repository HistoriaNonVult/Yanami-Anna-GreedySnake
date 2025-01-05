import tkinter as tk
from tkinter import Canvas

# 初始化窗口
root = tk.Tk()
root.title("Greedy Snake - Improved UI")
root.geometry("600x400")
root.configure(bg="#2b2d42")  # 深色背景

# 添加背景图并模糊化
bg_image = tk.PhotoImage(file="background.jpg")  # 替换为背景图路径
background = tk.Label(root, image=bg_image)
background.place(relwidth=1, relheight=1)

# 创建半透明遮罩
canvas = Canvas(root, width=600, height=400, bg="#000000", highlightthickness=0)
canvas.place(relwidth=1, relheight=1)
canvas.configure(opacity=0.6)

# 添加“Paused”文字
paused_text = canvas.create_text(300, 100, text="PAUSED", font=("Helvetica", 36, "bold"), fill="#FF6F61")

# 添加分数和长度信息
score_text = canvas.create_text(300, 150, text="Length: 3   Score: 0", font=("Helvetica", 16), fill="#E0FBFC")

# 按钮样式函数
def create_button(root, text, x, y, color, command):
    btn = tk.Button(
        root, text=text, font=("Helvetica", 14, "bold"), bg=color, fg="white", 
        activebackground="#3a3d5c", activeforeground="white", relief="flat", command=command
    )
    btn.place(x=x, y=y, width=100, height=40)

# 暂停/继续功能
def toggle_pause():
    current_text = canvas.itemcget(paused_text, "text")
    canvas.itemconfig(paused_text, text="CONTINUE" if current_text == "PAUSED" else "PAUSED")

# 重启功能
def restart_game():
    canvas.itemconfig(score_text, text="Length: 3   Score: 0")
    canvas.itemconfig(paused_text, text="PAUSED")

# 创建按钮
create_button(root, "Pause", 150, 300, "#4caf50", toggle_pause)
create_button(root, "Restart", 270, 300, "#2196F3", restart_game)
create_button(root, "Exit", 390, 300, "#f44336", root.quit)

# 主循环
root.mainloop()
