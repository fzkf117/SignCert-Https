import wx

from ui_panel.page_list_cert import ListCert
from utils.ui_icon import icon_001, getIcon
from ui_panel.page_create_cert import CreateCert
from ui_panel.page_sign_cert import SignCert


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(700, 850))
        notebook = wx.Notebook(self)
        self.page1 = CreateCert(notebook)
        self.page2 = SignCert(notebook)
        self.page3 = ListCert(notebook)
        notebook.AddPage(self.page1, " 生成证书")
        notebook.AddPage(self.page2, " 签用户证书")
        notebook.AddPage(self.page3, " 历史证书")
        self.SetMinSize((700, 850))
        self.SetIcon(getIcon(icon_001()))
        self.Center()

    def page3_item_insert(self, data):
        self.page3.item_insert(0, data)

    @staticmethod
    def format_byte_to_file_size(input_bytes):
        try:
            input_bytes = int(input_bytes)
            if input_bytes < 1024:
                return f"{input_bytes} B"
            elif input_bytes < 1024 * 1024:
                return f"{input_bytes / 1024:.2f} KB"
            elif input_bytes < 1024 * 1024 * 1024:
                return f"{input_bytes / (1024 * 1024):.2f} MB"
            else:
                return f"{input_bytes / (1024 * 1024 * 1024):.2f} GB"
        except Exception as e:
            print(e)
            return "0 B"

    @staticmethod
    def forma_file_size_to_byte(input_file_size):
        size_mapping = {
            "B": 1,
            "KB": 1024,
            "MB": 1024 ** 2,
            "GB": 1024 ** 3
        }
        size, unit = input_file_size.split()
        size = float(size)
        byte_size = size * size_mapping[unit]
        return byte_size

    @staticmethod
    def on_info(msg):
        wx.MessageBox(msg, "信息", wx.OK | wx.ICON_INFORMATION)

    @staticmethod
    def on_warning(msg):
        wx.MessageBox(msg, "警告", wx.OK | wx.ICON_WARNING)

    @staticmethod
    def on_error(msg):
        wx.MessageBox(msg, "错误", wx.OK | wx.ICON_ERROR)


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None, "Https 证书生成 zcy")
    frame.Show()
    app.MainLoop()
