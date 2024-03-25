import datetime
import os.path
import subprocess
import sys
import zipfile
import wx
from wx.lib.agw.pybusyinfo import PyBusyInfo
from utils.HttpsCertificate import HttpsCertificate
from utils.MyConfig import ConfigFile
from utils.SetTextCtrl import EnglishInputCtrl, TextInputCtrl, EmailInputCtrl, NumInputCtrl
from utils.re_expression import is_valid_dns_name, is_valid_ipv4


class SignCert(wx.ScrolledWindow):
    def __init__(self, parent):
        super(SignCert, self).__init__(parent)
        self.config = ConfigFile()

        # CA 私钥设置
        self.ca_private_key_password = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)

        self.ca_private_key_file_select = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.ca_private_key_file_select.Disable()
        self.ca_public_key_file_select = wx.TextCtrl(self, style=wx.TE_READONLY)  # 下拉数字选择框大小
        self.ca_public_key_file_select.Disable()

        # user 私钥设置
        self.user_private_key_password = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.user_private_key_choice_e = wx.Choice(self, choices=["65537", "3"])
        self.user_private_key_choice_e.SetSelection(0)
        self.user_private_key_choice_size = wx.Choice(self, choices=["2048", "3072", "4096"])  # 下拉数字选择框大小
        self.user_private_key_choice_size.SetSelection(0)

        # user 根证书请求文件csr
        self.user_csr_country_name = EnglishInputCtrl(self, style=wx.TE_PROCESS_ENTER, min_length=2, max_length=2)
        self.user_csr_state_or_province_name = TextInputCtrl(self, style=wx.TE_PROCESS_ENTER, max_length=64)
        self.user_csr_locality_name = TextInputCtrl(self, style=wx.TE_PROCESS_ENTER, max_length=128)
        self.user_csr_organization_name = TextInputCtrl(self, style=wx.TE_PROCESS_ENTER, max_length=64)
        self.user_csr_organizational_unit_name = TextInputCtrl(self, style=wx.TE_PROCESS_ENTER, max_length=64)
        self.user_csr_common_name = TextInputCtrl(self, style=wx.TE_PROCESS_ENTER, max_length=64)
        self.user_csr_email_address = EmailInputCtrl(self, style=wx.TE_PROCESS_ENTER, max_length=254)
        self.user_csr_dns_names = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.user_csr_ipv4_address = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.user_csr_ipv6_address = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.user_csr_dns_names.SetHint("多个域名使用分号(;)隔开")
        self.user_csr_ipv4_address.SetHint("多个ipV4使用分号(;)隔开")
        self.user_csr_ipv6_address.SetHint("多个ipV6使用分号(;)隔开")
        self.user_csr_valid_days = NumInputCtrl(self, style=wx.TE_PROCESS_ENTER, min_length=1)

        self.Sizer = wx.BoxSizer(wx.VERTICAL)  # 垂直布局

        self.H_pk_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ui_ca_private()
        self.Sizer.Add(self.H_pk_sizer, 0, wx.EXPAND | wx.ALL, border=5)

        self.H_csr_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ui_user_private()
        self.ui_user_csr()
        self.Sizer.Add(self.H_csr_sizer, 0, wx.EXPAND | wx.ALL, border=5)

        generate_button = wx.Button(self, label='生成')
        close_button = wx.Button(self, label='关闭')
        save_button = wx.Button(self, label='保存')
        close_button.Bind(wx.EVT_BUTTON, self.on_close)
        save_button.Bind(wx.EVT_BUTTON, self.on_save)
        generate_button.Bind(wx.EVT_BUTTON, self.on_generate_button)

        save_icon = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, (16, 16))
        generate_icon = wx.ArtProvider.GetBitmap(wx.ART_PLUS, wx.ART_TOOLBAR, (16, 16))
        close_icon = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR, (16, 16))

        generate_button.SetBitmap(generate_icon)
        close_button.SetBitmap(close_icon)
        save_button.SetBitmap(save_icon)

        sizer_horizontal = wx.BoxSizer(wx.HORIZONTAL)
        sizer_horizontal.Add(save_button, 0, wx.ALL, 5)
        sizer_horizontal.Add(generate_button, 0, wx.ALL, 5)
        sizer_horizontal.Add(close_button, 0, wx.ALL, 5)

        self.Sizer.Add(sizer_horizontal, 0, wx.ALIGN_CENTER)  # 将水平sizer添加到垂直sizer
        self.ui_init_private()
        self.ui_init_user()
        self.SetSizer(self.Sizer)
        self.SetScrollRate(10, 10)
        self.EnableScrolling(True, True)

    def ui_ca_private(self):
        Mbox = wx.StaticBox(self, label="CA 私钥")
        boxsizer = wx.StaticBoxSizer(Mbox, wx.VERTICAL)

        label_password = wx.StaticText(self, label="CA私钥密码:")
        label_public_key = wx.StaticText(self, label="CA私钥文件:")
        label_size = wx.StaticText(self, label="CA证书文件:")
        pk_select_button = wx.Button(self, label='选择')
        pu_select_button = wx.Button(self, label='选择')

        pk_select_button.Bind(wx.EVT_BUTTON, self.on_pk_select_button)
        pk_select_icon = wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_TOOLBAR, (16, 16))
        pk_select_button.SetBitmap(pk_select_icon)

        pu_select_button.Bind(wx.EVT_BUTTON, self.on_pu_select_button)
        pu_select_icon = wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_TOOLBAR, (16, 16))
        pu_select_button.SetBitmap(pu_select_icon)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(label_password, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox1.Add(self.ca_private_key_password, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox1, 0, wx.EXPAND | wx.ALL, border=5)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(label_public_key, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox2.Add(self.ca_private_key_file_select, 1, wx.EXPAND | wx.ALL, border=5)
        hbox2.Add(pk_select_button, 0, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox2, 0, wx.EXPAND | wx.ALL, border=5)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(label_size, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox3.Add(self.ca_public_key_file_select, 1, wx.EXPAND | wx.ALL, border=5)
        hbox3.Add(pu_select_button, 0, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox3, 0, wx.EXPAND | wx.ALL, border=5)
        self.H_pk_sizer.Add(boxsizer, 1, wx.EXPAND | wx.ALL, 10)

    def ui_user_private(self):
        Mbox = wx.StaticBox(self, label="User 私钥")
        boxsizer = wx.StaticBoxSizer(Mbox, wx.VERTICAL)

        label_password = wx.StaticText(self, label="密码:")
        label_public_key = wx.StaticText(self, label="公钥指数:")
        label_size = wx.StaticText(self, label="密钥长度:")

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(label_password, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox1.Add(self.user_private_key_password, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox1, 0, wx.EXPAND | wx.ALL, border=5)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(label_public_key, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox2.Add(self.user_private_key_choice_e, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox2, 0, wx.EXPAND | wx.ALL, border=5)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(label_size, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox3.Add(self.user_private_key_choice_size, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox3, 0, wx.EXPAND | wx.ALL, border=5)
        self.H_csr_sizer.Add(boxsizer, 1, wx.EXPAND | wx.ALL, 10)

    def ui_user_csr(self):
        Mbox = wx.StaticBox(self, label="User 证书请求文件设置")
        boxsizer = wx.StaticBoxSizer(Mbox, wx.VERTICAL)

        label1 = wx.StaticText(self, label="国家名字:")
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(label1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox1.Add(self.user_csr_country_name, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox1, 0, wx.EXPAND | wx.ALL, border=5)

        label2 = wx.StaticText(self, label="州或省名称:")
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(label2, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox2.Add(self.user_csr_state_or_province_name, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox2, 0, wx.EXPAND | wx.ALL, border=5)

        label3 = wx.StaticText(self, label="城市或区域称:")
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(label3, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox3.Add(self.user_csr_locality_name, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox3, 0, wx.EXPAND | wx.ALL, border=5)

        label4 = wx.StaticText(self, label="组织名或公司名:")
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(label4, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox4.Add(self.user_csr_organization_name, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox4, 0, wx.EXPAND | wx.ALL, border=5)

        label5 = wx.StaticText(self, label="组织单位名称或部门名:")
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5.Add(label5, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox5.Add(self.user_csr_organizational_unit_name, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox5, 0, wx.EXPAND | wx.ALL, border=5)

        label6 = wx.StaticText(self, label="证书拥有者名称:")
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        hbox6.Add(label6, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox6.Add(self.user_csr_common_name, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox6, 0, wx.EXPAND | wx.ALL, border=5)

        label7 = wx.StaticText(self, label="邮箱:")
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        hbox7.Add(label7, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox7.Add(self.user_csr_email_address, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox7, 0, wx.EXPAND | wx.ALL, border=5)

        label8 = wx.StaticText(self, label="设备域名:")
        hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        hbox8.Add(label8, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox8.Add(self.user_csr_dns_names, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox8, 0, wx.EXPAND | wx.ALL, border=5)

        label9 = wx.StaticText(self, label="设备ipv4:")
        hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        hbox9.Add(label9, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox9.Add(self.user_csr_ipv4_address, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox9, 0, wx.EXPAND | wx.ALL, border=5)

        label10 = wx.StaticText(self, label="设备ipv6:")
        hbox10 = wx.BoxSizer(wx.HORIZONTAL)
        hbox10.Add(label10, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox10.Add(self.user_csr_ipv6_address, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox10, 0, wx.EXPAND | wx.ALL, border=5)

        label11 = wx.StaticText(self, label="有效天数/天:")
        hbox11 = wx.BoxSizer(wx.HORIZONTAL)
        hbox11.Add(label11, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hbox11.Add(self.user_csr_valid_days, 1, wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(hbox11, 0, wx.EXPAND | wx.ALL, border=5)

        self.H_csr_sizer.Add(boxsizer, 1, wx.EXPAND | wx.ALL, 10)

    def ui_init_private(self):
        password = self.config.get("sign_ca", "password")
        if password:
            self.ca_private_key_password.SetValue(password)

        pk_select_path = self.config.get("sign_ca", "pk_select_path")
        if pk_select_path and os.path.exists(pk_select_path):
            self.ca_private_key_file_select.SetValue(pk_select_path)

        pu_select_path = self.config.get("sign_ca", "pu_select_path")
        if pu_select_path and os.path.exists(pu_select_path):
            self.ca_public_key_file_select.SetValue(pu_select_path)

    def ui_init_user(self):
        password = self.config.get("sign_user", "password")
        if password:
            self.user_private_key_password.SetValue(password)

        public_exponent = self.config.get("sign_user", "public_exponent")
        if public_exponent:
            if public_exponent not in ["65537", "3"]:
                self.user_private_key_choice_e.SetSelection(0)
            else:
                self.user_private_key_choice_e.SetSelection(["65537", "3"].index(public_exponent))

        key_size = self.config.get("sign_user", "key_size")
        if key_size:
            if key_size not in ["2048", "3072", "4096"]:
                self.user_private_key_choice_size.SetSelection(0)
            else:
                self.user_private_key_choice_size.SetSelection(["2048", "3072", "4096"].index(key_size))

        country_name = self.config.get("sign_user", "country_name")
        if country_name and len(country_name) == 2:
            self.user_csr_country_name.SetValue(country_name)
        else:
            self.user_csr_country_name.SetValue("")

        state_or_province_name = self.config.get("sign_user", "state_or_province_name")
        if state_or_province_name and len(state_or_province_name) <= 64:
            self.user_csr_state_or_province_name.SetValue(state_or_province_name)

        locality_name = self.config.get("sign_user", "locality_name")
        if locality_name and len(locality_name) <= 128:
            self.user_csr_locality_name.SetValue(locality_name)

        organization_name = self.config.get("sign_user", "organization_name")
        if organization_name and len(organization_name) <= 64:
            self.user_csr_organization_name.SetValue(organization_name)

        organizational_unit_name = self.config.get("sign_user", "organizational_unit_name")
        if organizational_unit_name and len(organizational_unit_name) <= 64:
            self.user_csr_organizational_unit_name.SetValue(organizational_unit_name)

        common_name = self.config.get("sign_user", "common_name")
        if common_name and len(common_name) <= 64:
            self.user_csr_common_name.SetValue(common_name)

        email_address = self.config.get("sign_user", "email_address")
        if email_address and len(email_address) <= 254:
            self.user_csr_email_address.SetValue(email_address)

        valid_after_days = self.config.get("sign_user", "valid_after_days")
        if valid_after_days:
            if valid_after_days.isdigit():
                self.user_csr_valid_days.SetValue(valid_after_days)
            else:
                self.user_csr_valid_days.SetValue("365")
        else:
            self.user_csr_valid_days.SetValue("365")

        dns_names = self.config.get("sign_user", "dns_names")
        if dns_names:
            self.user_csr_dns_names.SetValue(dns_names)

        ipv4_address = self.config.get("sign_user", "ipv4_address")
        if ipv4_address:
            self.user_csr_ipv4_address.SetValue(ipv4_address)

        ipv6_address = self.config.get("sign_user", "ipv6_address")
        if ipv6_address:
            self.user_csr_ipv6_address.SetValue(ipv6_address)

    def on_pk_select_button(self, event):
        wildcard = "All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "选择私钥文件", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            self.ca_private_key_file_select.SetValue(file_path)
        dialog.Destroy()

    def on_pu_select_button(self, event):
        wildcard = "All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "选择公钥文件", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            self.ca_public_key_file_select.SetValue(file_path)
        dialog.Destroy()

    def on_close(self, event):
        self.GetTopLevelParent().Close()

    def on_save(self, event):
        self.save_config()
        self.GetParent().GetParent().on_info("保存成功")

    def on_generate_button(self, event):
        if not self.check_input():
            return

        ca_pk_obj = HttpsCertificate.load_private_key_obj(self.ca_private_key_file_select.GetValue().strip(),
                                                          self.ca_private_key_password.GetValue().strip())
        if not ca_pk_obj:
            self.GetParent().GetParent().on_error("输入CA私钥的密码错误 或 选择的私钥文件不正确")
            return

        ca_crt_obj = HttpsCertificate.load_cert_obj(self.ca_public_key_file_select.GetValue().strip())
        if not ca_crt_obj:
            self.GetParent().GetParent().on_error("选择CA的证书文件不和合法")
            return

        current_date = datetime.datetime.now()
        year = current_date.year
        month = current_date.month

        tem_file_name = ""
        while True:
            dlg = wx.TextEntryDialog(self, "填写描述信息", "输入生成证书包文件的名字:", tem_file_name)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            text = dlg.GetValue()
            if text.strip() == "":
                self.GetParent().GetParent().on_warning("输入不能为空")
                dlg.Destroy()
                continue
            if os.path.exists(os.path.join(os.getcwd(), "File", f"{year}-{month:02}", f"{text}.zip")):
                self.GetParent().GetParent().on_warning(f"文件名 {text} 已经存在")
                tem_file_name = text
                dlg.Destroy()
                continue
            dlg.Destroy()
            break

        busy = PyBusyInfo("正在执行操作，请稍候...", title="加载中...", parent=self)

        user_pk_obj = HttpsCertificate.get_private_key_object(
            int(self.user_private_key_choice_e.GetString(
                self.user_private_key_choice_e.GetSelection())),
            int(self.user_private_key_choice_size.GetString(
                self.user_private_key_choice_size.GetSelection())))

        dns_names = [dns for dns in self.user_csr_dns_names.GetValue().split(";") if dns]
        ipv4_address = [ipv4 for ipv4 in self.user_csr_ipv4_address.GetValue().split(";") if ipv4]
        ipv6_address = [ipv6 for ipv6 in self.user_csr_ipv6_address.GetValue().split(";") if ipv6]

        user_pub_csr_obj = HttpsCertificate.get_user_certificate_csr_object(
            user_pk_obj,
            country_name=self.user_csr_country_name.GetValue(),
            state_or_province_name=self.user_csr_state_or_province_name.GetValue(),
            locality_name=self.user_csr_locality_name.GetValue(),
            organization_name=self.user_csr_organization_name.GetValue(),
            organizational_unit_name=self.user_csr_organizational_unit_name.GetValue(),
            common_name=self.user_csr_common_name.GetValue(),
            email_address=self.user_csr_email_address.GetValue(),
            dns_names=dns_names,
            ipv4_address=ipv4_address,
            ipv6_address=ipv6_address,
        )

        user_crt_obj = HttpsCertificate.get_user_certificate_object(ca_pk_obj,
                                                                    ca_crt_obj,
                                                                    user_pub_csr_obj,
                                                                    dns_names=dns_names,
                                                                    ipv4_address=ipv4_address,
                                                                    ipv6_address=ipv6_address,
                                                                    valid_after_days=int(
                                                                        self.user_csr_valid_days.GetValue()))
        tem_path = os.path.join(os.getcwd(), "tem_path")
        if not os.path.exists(tem_path):
            os.mkdir(tem_path)

        user_key_pem_path_file = os.path.join(tem_path, "user.key.pem")
        user_csr_path_file = os.path.join(tem_path, "user.csr")
        user_cert_pem_path_file = os.path.join(tem_path, "user.cert.pem")
        readme_md_path_file = os.path.join(tem_path, "ReadMe.md")

        HttpsCertificate.write_private_key_file(user_pk_obj, user_key_pem_path_file,
                                                self.user_private_key_password.GetValue().encode())
        HttpsCertificate.write_certificate_csr_file(user_pub_csr_obj, user_csr_path_file)
        HttpsCertificate.write_certificate_file(user_crt_obj, user_cert_pem_path_file)

        msg_data = (f"CA私钥名字: {os.path.basename(self.ca_private_key_file_select.GetValue().strip())}\n"
                    f"CA根证书名字: {os.path.basename(self.ca_public_key_file_select.GetValue().strip())}\n\n"
                    f"用户服务器私钥名字: user.key.pem\n"
                    f"用户服务器私钥密码: {self.user_private_key_password.GetValue()}\n"
                    f"用户服务器证书请求文件: user.csr\n"
                    f"用户服务器证书名字: user.cert.pem\n"
                    )
        with open(readme_md_path_file, "w") as f:
            f.write(msg_data)

        path_file = os.path.join(os.getcwd(), "File", f"{year}-{month:02}", f"{text}.zip")
        file_list = [self.ca_private_key_file_select.GetValue().strip(),
                     self.ca_public_key_file_select.GetValue().strip(),
                     user_key_pem_path_file, user_csr_path_file, user_cert_pem_path_file, readme_md_path_file]
        with zipfile.ZipFile(path_file, 'w') as zipf:
            for file in file_list:
                zipf.write(file, os.path.basename(file))
                if file not in [self.ca_private_key_file_select.GetValue().strip(),
                                self.ca_public_key_file_select.GetValue().strip()]:
                    os.remove(file)

        self.save_config()
        file_size = self.GetParent().GetParent().format_byte_to_file_size(os.path.getsize(path_file))
        creation_time = os.path.getmtime(path_file)
        creation_time = str(datetime.datetime.fromtimestamp(creation_time)).split(".")[0]
        self.GetParent().GetParent().page3_item_insert((f"{text}.zip", path_file, file_size, creation_time))
        busy = None
        dlg = wx.MessageDialog(None, f"证书已经生成\n是否打开证书目录 {path_file}",
                               "提示", wx.YES_NO | wx.ICON_INFORMATION)
        dlg.SetYesNoLabels("是", "否")
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            if not os.path.exists(path_file):
                return
            platform = sys.platform
            if platform.startswith("win"):
                subprocess.Popen(f'explorer /select, "{path_file}"')
            elif platform.startswith("darwin"):
                subprocess.Popen(['open', '-R', path_file])
            elif platform.startswith("Linux"):
                subprocess.Popen(['xdg-open', '--select', path_file])
            else:
                pass

    def save_config(self):
        self.config.set("sign_ca", "password", self.ca_private_key_password.GetValue())
        self.config.set("sign_ca", "public_exponent", self.ca_private_key_file_select.GetValue())
        self.config.set("sign_ca", "key_size", self.ca_public_key_file_select.GetValue())

        self.config.set("sign_user", "password", self.user_private_key_password.GetValue())
        self.config.set("sign_user", "public_exponent",
                        self.user_private_key_choice_e.GetString(self.user_private_key_choice_e.GetSelection()))
        self.config.set("sign_user", "key_size",
                        self.user_private_key_choice_size.GetString(self.user_private_key_choice_size.GetSelection()))
        self.config.set("sign_user", "country_name", self.user_csr_country_name.GetValue())
        self.config.set("sign_user", "state_or_province_name", self.user_csr_state_or_province_name.GetValue())
        self.config.set("sign_user", "locality_name", self.user_csr_locality_name.GetValue())
        self.config.set("create_user", "organization_name", self.user_csr_organization_name.GetValue())
        self.config.set("sign_user", "organizational_unit_name", self.user_csr_organizational_unit_name.GetValue())
        self.config.set("sign_user", "common_name", self.user_csr_common_name.GetValue())
        self.config.set("sign_user", "create_ca", self.user_csr_email_address.GetValue())
        self.config.set("sign_user", "valid_after_days", self.user_csr_valid_days.GetValue())
        self.config.set("sign_user", "dns_names", self.user_csr_dns_names.GetValue())
        self.config.set("sign_user", "ipv4_address", self.user_csr_ipv4_address.GetValue())
        self.config.set("sign_user", "ipv6_address", self.user_csr_ipv6_address.GetValue())
        self.config.save()

    def check_input(self):
        if not str(self.ca_private_key_file_select.GetValue()).strip():
            self.GetParent().GetParent().on_warning("CA 私钥路径不能为空")
            return False
        if not str(self.ca_public_key_file_select.GetValue()).strip():
            self.GetParent().GetParent().on_warning("CA 证书路径不能为空")
            return False
        if not os.path.exists(self.ca_private_key_file_select.GetValue()):
            self.GetParent().GetParent().on_warning("CA 私钥路径不存在，请重新选择")
            return False
        if not os.path.exists(self.ca_public_key_file_select.GetValue()):
            self.GetParent().GetParent().on_warning("CA 证书路径不存在，请重新选择")
            return False

        if self.ca_private_key_file_select.GetValue() == self.ca_public_key_file_select.GetValue():
            self.GetParent().GetParent().on_warning("CA 私钥和证书路径 不应该相同，请重新选择")
            return False

        user_country_name = self.user_csr_country_name.GetValue()
        if len(user_country_name) != 2:
            self.GetParent().GetParent().on_warning("User 国家名称的长度必须是2")
            self.user_csr_country_name.SetFocus()
            return False

        user_valid_days = self.user_csr_valid_days.GetValue()
        if len(user_valid_days) == 0:
            self.GetParent().GetParent().on_warning("User 证书有效期不能为空")
            self.user_csr_valid_days.SetFocus()
            return False

        user_csr_dns_names = self.user_csr_dns_names.GetValue().split(";")
        for dns in user_csr_dns_names:
            if dns and not is_valid_dns_name(dns):
                self.GetParent().GetParent().on_warning("User 存在不合法域名")
                self.user_csr_dns_names.SetFocus()
                return False

        user_csr_ipv4s = self.user_csr_ipv4_address.GetValue().split(";")
        for ipv4 in user_csr_ipv4s:
            if ipv4 and not is_valid_ipv4(ipv4):
                self.GetParent().GetParent().on_warning("User 存在不合法Ipv4")
                self.user_csr_ipv4_address.SetFocus()
                return False

        user_csr_ipv6s = self.user_csr_ipv6_address.GetValue().split(";")
        for ipv6 in user_csr_ipv6s:
            if ipv6 and not is_valid_ipv4(ipv6):
                self.GetParent().GetParent().on_warning("User 存在不合法Ipv6")
                self.user_csr_ipv6_address.SetFocus()
                return False
        return True
