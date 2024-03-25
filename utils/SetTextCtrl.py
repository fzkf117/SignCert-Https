import wx

from utils.re_expression import is_valid_int_composition, is_valid_email_composition, is_valid_letter_composition, \
    is_valid_chinese_composition

valid_key_code = [wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_CONTROL_A, wx.WXK_CONTROL_V, wx.WXK_UP, wx.WXK_DOWN, wx.WXK_LEFT,
                  wx.WXK_RIGHT]


class InputCtrl(wx.TextCtrl):
    def __init__(self, parent, min_length=None, max_length=None, func_pattern=None, *args, **kwargs):
        """
        :param parent:
        :param min_length:
        :param max_length:
        :param func_pattern: 输入匹配函数
        :param args:
        :param kwargs:
        """
        super().__init__(parent, *args, **kwargs)
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.Bind(wx.EVT_TEXT_PASTE, self.on_paste)
        self.min_length = min_length
        self.max_length = max_length
        self.func_pattern = func_pattern

    def on_char(self, event):
        key_code = event.GetKeyCode()
        if key_code in valid_key_code:
            if self.min_length is not None and (key_code == wx.WXK_BACK or key_code == wx.WXK_DELETE):
                start, end = self.GetSelection()
                if start == end:
                    start += 1
                if len(self.GetValue()) - abs(start - end) < self.min_length:
                    self.SetBackgroundColour(wx.YELLOW)
                else:
                    self.SetBackgroundColour(wx.NullColour)
            event.Skip()
            return

        if self.max_length is not None and len(self.GetValue()) + 1 > self.max_length:
            return

        if self.min_length is not None:
            if len(self.GetValue()) + 1 < self.min_length:
                self.SetBackgroundColour(wx.YELLOW)
            else:
                self.SetBackgroundColour(wx.NullColour)

        if key_code != 0 and self.func_pattern is not None:
            if self.func_pattern(chr(key_code)):
                event.Skip()
        elif key_code == 0 and 19968 <= event.GetUnicodeKey() <= 40869 and self.func_pattern is not None:
            chinese_char = chr(event.GetUnicodeKey())
            if self.func_pattern(chinese_char):
                event.Skip()
        elif self.func_pattern is None:
            event.Skip()
        return

    def on_paste(self, event):
        clipboard = wx.TextDataObject()
        if not wx.TheClipboard.Open():
            return
        if wx.TheClipboard.GetData(clipboard):
            wx.TheClipboard.Close()
            data = clipboard.GetText()
            if self.max_length is not None and len(self.GetValue()) + len(data) > self.max_length:
                return

            if self.func_pattern is not None and self.func_pattern(data):
                if self.min_length is not None and len(self.GetValue()) + len(data) < self.min_length:
                    self.SetBackgroundColour(wx.YELLOW)
                else:
                    self.SetBackgroundColour(wx.NullColour)
                event.Skip()
                return

    def SetValue(self, value):
        super().SetValue(value)
        self.on_char(wx.KeyEvent())


class NumInputCtrl(InputCtrl):
    """ 数字输入框 """

    def __init__(self, parent, min_length=None, max_length=None, *args, **kwargs):
        super().__init__(parent, min_length, max_length, func_pattern=is_valid_int_composition, *args, **kwargs)


class TextInputCtrl(InputCtrl):
    """ 文本输入框 """

    def __init__(self, parent, min_length=None, max_length=None, *args, **kwargs):
        super().__init__(parent, min_length, max_length, *args, **kwargs)


class EmailInputCtrl(InputCtrl):
    """ 邮箱输入框 """

    def __init__(self, parent, min_length=None, max_length=None, *args, **kwargs):
        super().__init__(parent, min_length, max_length, func_pattern=is_valid_email_composition, *args, **kwargs)


class EnglishInputCtrl(InputCtrl):
    """ 英文输入框 """

    def __init__(self, parent, min_length=None, max_length=None, *args, **kwargs):
        super().__init__(parent, min_length, max_length, func_pattern=is_valid_letter_composition, *args, **kwargs)


class ChineseInputCtrl(InputCtrl):
    """ 中文输入框 """

    def __init__(self, parent, min_length=None, max_length=None, *args, **kwargs):
        super().__init__(parent, min_length, max_length, func_pattern=is_valid_chinese_composition, *args, **kwargs)


