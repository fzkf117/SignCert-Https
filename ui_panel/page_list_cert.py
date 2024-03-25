import datetime
import os
import subprocess
import sys

import pyperclip3
import wx


class ListCert(wx.Panel):
    def __init__(self, parent):
        super(ListCert, self).__init__(parent)
        self.list_ctrl = None
        self.currentItem = None
        self.FilePath = os.path.join(os.getcwd(), "File")
        if not os.path.exists(self.FilePath):
            os.makedirs(self.FilePath)

        self.ui_table()
        self.init_ui_table()

        self.sort_direction = 1  # 1表示正序，-1表示逆序
        self.sorted_column = None  # 记录当前排序的列

    def ui_table(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)
        self.list_ctrl.InsertColumn(0, '名称', width=150)  # 使用 -1 表示自动调整列宽
        self.list_ctrl.InsertColumn(1, '路径', width=300)
        self.list_ctrl.InsertColumn(2, '大小', width=80)
        self.list_ctrl.InsertColumn(3, '创建时间', width=140)
        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 1)
        self.list_ctrl.Bind(wx.EVT_LIST_COL_CLICK, self.column_click)
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.item_activated)
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.item_right_down)
        self.SetSizer(sizer)

    def init_ui_table(self):
        data = self.get_directory_files_info()
        self.update_list(data)

    def update_list(self, items):
        self.list_ctrl.DeleteAllItems()
        for row, (item) in enumerate(items):
            self.list_ctrl.InsertItem(row, str(item[0]))
            for i in range(len(item)-1):
                self.list_ctrl.SetItem(row, i+1, str(item[i+1]))

    def column_click(self, event):
        col = event.GetColumn()  # 根据哪列排序
        if self.sorted_column == col:
            self.sort_direction *= -1  # 切换排序方向
        else:
            self.sort_direction = 1
            self.sorted_column = col

        items = [(self.list_ctrl.GetItemText(i),
                  self.list_ctrl.GetItem(i, 1).GetText(),
                  self.list_ctrl.GetItem(i, 2).GetText(),
                  self.list_ctrl.GetItem(i, 3).GetText(),
                  )
                 for i in range(self.list_ctrl.GetItemCount())]
        if col == 0 or col == 1 or col == 3:
            items.sort(key=lambda x: x[col], reverse=self.sort_direction == -1)
            self.update_list(items)
        elif col == 2:
            items.sort(key=lambda x: self.GetParent().GetParent().forma_file_size_to_byte(x[2]), reverse=self.sort_direction == -1)
            self.update_list(items)

    def item_activated(self, event):
        index = event.GetIndex()
        file_path = self.list_ctrl.GetItem(index, 1).GetText()
        self.open_explorer(file_path)

    def item_right_down(self, event):
        self.currentItem = event.Index
        menu = wx.Menu()
        delete_item = menu.Append(-1, "删除")
        delete_icon = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU, (16, 16))
        delete_item.SetBitmap(delete_icon)
        self.Bind(wx.EVT_MENU, self.item_delete, delete_item)
        refresh_item = menu.Append(-1, "刷新")
        refresh_icon = wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_MENU, (16, 16))
        refresh_item.SetBitmap(refresh_icon)
        self.Bind(wx.EVT_MENU, self.item_refresh, refresh_item)
        copy_item = menu.Append(-1, "复制文件路径")
        opy_icon = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU, (16, 16))
        copy_item.SetBitmap(opy_icon)
        self.Bind(wx.EVT_MENU, self.item_copy_path, copy_item)
        open_explorer_item = menu.Append(-1, "打开文件路径")
        open_explorer_icon = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU, (16, 16))
        open_explorer_item.SetBitmap(open_explorer_icon)
        self.Bind(wx.EVT_MENU, self.item_open_path_explorer, open_explorer_item)
        self.PopupMenu(menu)
        menu.Destroy()

    def item_delete(self, event):
        file_path = self.list_ctrl.GetItem(self.currentItem, 1).GetText()
        if not os.path.exists(file_path):
            self.init_ui_table()
            return
        dlg = wx.MessageDialog(None, f"是否确定删除选中文件\n{file_path}",
                               "提示", wx.YES_NO | wx.ICON_INFORMATION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            os.remove(file_path)
            self.list_ctrl.DeleteItem(self.currentItem)

    def item_refresh(self, event):
        self.init_ui_table()

    def item_copy_path(self, event):
        text = self.list_ctrl.GetItem(self.currentItem, 1).GetText()
        pyperclip3.copy(text)

    def item_insert(self, index, data):
        self.list_ctrl.InsertItem(index, data[0])
        for i in range(len(data)-1):
            self.list_ctrl.SetItem(index, i+1, data[i+1])

    def item_open_path_explorer(self, event):
        file_path = self.list_ctrl.GetItem(self.currentItem, 1).GetText()
        self.open_explorer(file_path)

    def open_explorer(self, file_path):
        if not os.path.exists(file_path):
            self.init_ui_table()
            return
        platform = sys.platform
        if platform.startswith("win"):
            subprocess.Popen(f'explorer /select, "{file_path}"')
        elif platform.startswith("darwin"):
            subprocess.Popen(['open', '-R', file_path])
        elif platform.startswith("Linux"):
            subprocess.Popen(['xdg-open', '--select', file_path])
        else:
            self.init_ui_table()
            return

    def get_directory_files_info(self):
        try:
            zip_files = []
            for root, dirs, files in os.walk(self.FilePath):
                for file in files:
                    if file.endswith('.zip'):
                        file_path = os.path.join(root, file)
                        file_name = file
                        file_size = self.GetParent().GetParent().format_byte_to_file_size(os.path.getsize(file_path))
                        creation_time = os.path.getmtime(file_path)
                        creation_time = str(datetime.datetime.fromtimestamp(creation_time)).split(".")[0]
                        zip_files.append([file_name, file_path, file_size, creation_time])
            return zip_files
        except Exception as e:
            print(e)
            return []

