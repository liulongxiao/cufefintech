from tkinter import *
from tkinter.ttk import *
from listen import *
class Myframe(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.grid()
        # self.directions=[True,False]
        self.init_components()

    def init_components(self):
        proj_name = Label(self, text='股票监视器')
        proj_name.grid(columnspan=2)


        stockId_label = Label(self, text='股票代码')
        stockId_label.grid(row=1)
        self.stockId = Entry(self)
        self.stockId.grid(row=1, column=1)


        direction_label = Label(self, text='方向')
        direction_label.grid(row=2, column=0)
        self.direction = Combobox(self, value=self.get_direction())
        self.direction.grid(row=2, column=1)

        price_label = Label(self, text='目标价格')
        price_label.grid(row=3)
        self.price=Entry(self)
        self.price.grid(row=3,column=1)

        price_change_label = Label(self, text='目标涨跌幅')
        price_change_label.grid(row=4)
        self.price_change = Entry(self)
        self.price_change.grid(row=4, column=1)

        volume_label = Label(self, text='目标成交量')
        volume_label.grid(row=5)
        self.volume = Entry(self)
        self.volume.grid(row=5, column=1)

        self.start_btn=Button(self,text='启动监听',command=self.start_listen)
        self.start_btn.grid(row=6)

        self.exit_btn=Button(self,text='退出监听',command=self.exit_listen)
        self.exit_btn.grid(row=6,column=1)
    def get_direction(self):
        return ['向上突破','向下突破']
    def start_listen(self):
        #股票代码检测:
        stockId_=self.stockId.get()
        #方向检测
        if self.direction.get()=='向上突破':
            direction_=True
        elif self.direction.get()=='向下突破':
            direction_=False
        else:
            showerror('','突破方向必须选择向上或者向下突破')
            return -1
        #价格检测
        try:
            if len(self.price.get())>0:
                price_=self.price.get()
                price_=float(price_)
            else:
                price_=None
        except Exception as e:
            showerror('', 'price选择错误')
            return 0

        #价格变化检测
        try:
            if len(self.price_change.get()) > 0:
                price_change_ = self.price_change.get()
                price_change_ = float(price_change_)
            else:
                price_change_ = None
        except Exception as e:
            showerror('', '涨跌幅选择错误')
            return 0
        #成交量检测
        try:
            if len(self.volume.get()) > 0:
                volume_ = self.volume.get()
                volume_ = int(volume_)
            else:
                volume_ = None
        except Exception as e:
            showerror('', '涨跌幅选择错误')
            return 0


        showinfo('','start to listening!')
        mylisener=listener(code=stockId_,direction=direction_,price=price_,pt_change=price_change_,volumn=volume_)
        flag=True
        while flag:
            time.sleep(3)
            flag=mylisener._run()

        print(price_,direction_,price_change_,volume_)
    def exit_listen(self):
        self.quit()

root=Tk()
root.title('股票监视器')
root.resizable(False,False)
app=Myframe(root)
app.mainloop()
