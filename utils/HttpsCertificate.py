import os.path
from typing import Union
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime
import ipaddress


class HttpsCertificate(object):
    """创建路径/文件"""

    @staticmethod
    def create_path_file(path):
        if not path:
            return False, "提供的路径是空或None"
        if not isinstance(path, str) or len(path.split()) == 0:
            return False, "提供的路径无效"
        if os.path.exists(path):
            return True, ""
        if os.path.splitext(path)[1]:
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                return True, ""
            with open(path, "w") as f:
                pass
            return True, ""
        os.makedirs(path)
        return True, ""

    @staticmethod
    def write_private_key_file(private_key_obj, path, password):
        with open(path, "wb") as f:
            f.write(private_key_obj.private_bytes(serialization.Encoding.PEM,
                                                  serialization.PrivateFormat.PKCS8,
                                                  serialization.BestAvailableEncryption(
                                                      password) if password else serialization.NoEncryption())
                    )

    @staticmethod
    def write_certificate_csr_file(csr_object, path):
        with open(path, "wb") as f:
            f.write(csr_object.public_bytes(
                encoding=serialization.Encoding.PEM,
            ))

    @staticmethod
    def write_certificate_file(certificate_object, path):
        with open(path, "wb") as f:
            f.write(certificate_object.public_bytes(
                encoding=serialization.Encoding.PEM,
            ))

    @staticmethod
    def get_private_key_object(public_exponent: int = 65537,
                               key_size: int = 4096):
        """创建私钥对象"""
        private_key_obj = rsa.generate_private_key(public_exponent, key_size, backend=default_backend())
        return private_key_obj

    @staticmethod
    def get_root_certificate_csr_object(private_key_obj,
                                        country_name: str,  # 国家名字
                                        state_or_province_name: str,  # 州或省名称
                                        locality_name: str,  # 城市或区域称
                                        organization_name: str,  # 组织名（或公司名）
                                        organizational_unit_name: str,  # 组织单位名称（或部门名）
                                        common_name: str,  # 服务器域名/证书拥有者名称
                                        email_address: str,  # 邮箱
                                        signature_hash_algorithm: hashes = hashes.SHA256(),  # 用户信息的签名算法
                                        ):
        """创建根证书请求对象"""

        # 构建主体信息
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country_name),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state_or_province_name),
            x509.NameAttribute(NameOID.LOCALITY_NAME, locality_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, organizational_unit_name),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, email_address),
        ])

        csr_object = x509.CertificateSigningRequestBuilder().subject_name(
            subject
        ).sign(private_key_obj, signature_hash_algorithm, default_backend())
        # with open("123.csr", "wb") as f:
        #     f.write(csr.public_bytes(serialization.Encoding.PEM))
        return csr_object

    @staticmethod
    def get_user_certificate_csr_object(private_key_obj,
                                        country_name: str,  # 国家名字
                                        state_or_province_name: str,  # 州或省名称
                                        locality_name: str,  # 城市或区域称
                                        organization_name: str,  # 组织名（或公司名）
                                        organizational_unit_name: str,  # 组织单位名称（或部门名）
                                        common_name: str,  # 服务器域名/证书拥有者名称
                                        email_address: str,  # 邮箱
                                        dns_names: Union[list, None] = None,  # 设备域名
                                        ipv4_address: Union[list, None] = None,  # 设备ipv4
                                        ipv6_address: Union[list, None] = None,  # 设备ipv6
                                        signature_hash_algorithm: hashes = hashes.SHA256(),  # 用户信息的签名算法
                                        add_extension_critical: bool = False,  # 扩展是否需要客户端验证
                                        ):
        """创建证书请求对象"""

        if dns_names is None:
            dns_names = []
        if ipv4_address is None:
            ipv4_address = []
        if ipv6_address is None:
            ipv6_address = []

        # 构建主体信息
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country_name),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state_or_province_name),
            x509.NameAttribute(NameOID.LOCALITY_NAME, locality_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, organizational_unit_name),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, email_address),
        ])

        # 创建 SAN 扩展, 域名+ip
        san = ([x509.DNSName(name) for name in dns_names] +
               [x509.IPAddress(ipaddress.IPv4Address(ipv4)) for ipv4 in ipv4_address] +
               [x509.IPAddress(ipaddress.IPv6Address(ipv6)) for ipv6 in ipv6_address])

        # 创建证书请求
        csr_object = x509.CertificateSigningRequestBuilder().subject_name(
            subject
        ).add_extension(
            x509.SubjectAlternativeName(san),
            critical=add_extension_critical
        ).sign(private_key_obj, signature_hash_algorithm, default_backend())
        return csr_object

    @staticmethod
    def get_root_certificate_object(ca_private_key_obj,
                                    ca_csr_obj,
                                    valid_before_stamp=datetime.datetime.utcnow(),
                                    valid_after_days=365,
                                    signature_hash_algorithm: hashes = hashes.SHA256(),  # 签名算法
                                    ):
        """创建根证书"""

        ca_cert_obj = (
            x509.CertificateBuilder()
            .subject_name(ca_csr_obj.subject)
            .issuer_name(ca_csr_obj.subject)
            .public_key(ca_csr_obj.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(valid_before_stamp)
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=valid_after_days))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(ca_private_key_obj, signature_hash_algorithm, default_backend())
        )
        return ca_cert_obj

    @staticmethod
    def get_user_certificate_object(ca_private_key_obj,  # CA 的私钥
                                    ca_certificate_obj,  # CA 的证书
                                    csr_object,  # 用户证书请求文件
                                    dns_names: Union[list, None] = None,  # 设备域名
                                    ipv4_address: Union[list, None] = None,  # 设备ipv4
                                    ipv6_address: Union[list, None] = None,  # 设备ipv6
                                    valid_before_stamp=datetime.datetime.utcnow(),
                                    valid_after_days=365,
                                    signature_hash_algorithm: hashes = hashes.SHA256(),  # 签名算法
                                    add_extension_critical: bool = False,  # 扩展是否需要客户端验证
                                    ):

        if dns_names is None:
            dns_names = []
        if ipv4_address is None:
            ipv4_address = []
        if ipv6_address is None:
            ipv6_address = []

        """创建用户证书"""

        # 创建 SAN 扩展, 域名+ip
        san = ([x509.DNSName(name) for name in dns_names] +
               [x509.IPAddress(ipaddress.IPv4Address(ipv4)) for ipv4 in ipv4_address] +
               [x509.IPAddress(ipaddress.IPv6Address(ipv6)) for ipv6 in ipv6_address])

        server_cert_object = (
            x509.CertificateBuilder()
            .subject_name(csr_object.subject)
            .issuer_name(ca_certificate_obj.subject)
            .public_key(csr_object.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(valid_before_stamp)
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=valid_after_days))
            .add_extension(x509.SubjectAlternativeName(san), critical=add_extension_critical)
            .sign(ca_private_key_obj, signature_hash_algorithm, default_backend())
        )
        return server_cert_object

    @staticmethod
    def load_private_key_obj(private_key_file, password: str):
        try:
            with open(private_key_file, "rb") as key_fag:
                private_key = load_pem_private_key(key_fag.read(), password=password.encode(),
                                                   backend=default_backend())
            return private_key
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def load_cert_obj(cert_file):
        try:
            with open(cert_file, "rb") as cert_fag:
                cert_obj = x509.load_pem_x509_certificate(cert_fag.read(), default_backend())
            return cert_obj
        except Exception as e:
            print(e)
            return None

