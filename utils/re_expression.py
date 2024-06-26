import re


def validate_email(email):
    """ 邮箱验证 """
    pattern = r'[\w!#$%&\'*+/=?^_`{|}~-]+(?:\.[\w!#$%&\'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?'
    return re.match(pattern, email)


def is_valid_email_composition(data):
    """ 验证是否是邮箱组成成分 """
    pattern = r'^[a-zA-Z0-9!#$%&\'*+-/=?^_`{|}~.]+$'
    return re.match(pattern, data)


def is_valid_int_composition(data):
    return str(data).isdigit()


def is_valid_letter_composition(english_char):
    """ 英文验证 """
    pattern = r'[a-zA-Z]+'
    return re.match(pattern, english_char)


def is_valid_chinese_composition(english_char):
    """ 英文验证 """
    pattern = (r'(?:[\u3400-\u4DB5\u4E00-\u9FEA\uFA0E\uFA0F\uFA11\uFA13\uFA14\uFA1F\uFA21\uFA23\uFA24\uFA27-\uFA29]|['
               r'\uD840-\uD868\uD86A-\uD86C\uD86F-\uD872\uD874-\uD879][\uDC00-\uDFFF]|\uD869['
               r'\uDC00-\uDED6\uDF00-\uDFFF]|\uD86D[\uDC00-\uDF34\uDF40-\uDFFF]|\uD86E['
               r'\uDC00-\uDC1D\uDC20-\uDFFF]|\uD873[\uDC00-\uDEA1\uDEB0-\uDFFF]|\uD87A[\uDC00-\uDFE0])+')
    return re.match(pattern, english_char)


def is_valid_dns_name(dns_name):
    """ 域名校验 """
    pattern = r'^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,}(?!\d)$'
    return re.match(pattern, dns_name)


def is_valid_ipv4(ipv4):
    """ 域名校验 """
    pattern = (r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2['
               r'0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
    return re.match(pattern, ipv4)


def is_valid_ipv6(ipv6):
    pattern = (r'\b((?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,'
               r'6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,'
               r'4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,'
               r'4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::['
               r'0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]+|::(?:ffff(?::0{1,4}){0,1}:){0,'
               r'1}(25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.(25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.(25[0-5]|('
               r'?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.(25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,'
               r'4}:((25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(['
               r'0-9a-fA-F]{1,4}:){1,3}:(:(25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(?:2[0-4]|1{0,'
               r'1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,2}(:((25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,'
               r'3}(25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|:)|([0-9a-fA-F]{1,4}:):((25[0-5]|(?:2[0-4]|1{0,'
               r'1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|:((:[0-9a-fA-F]{1,4}){1,'
               r'7}|:)|((?:[0-9a-fA-F]{1,4}:){1,7}|:)(:[0-9a-fA-F]{1,4}){1,7})\b')
    return re.match(pattern, ipv6)
