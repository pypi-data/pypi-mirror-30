# -*- coding:utf-8 -*-  
# author = xingege
# email =shuizhengqi1@163.com
# date = 2018/3/15 下午4:26
# filename=DingCrypto
import StringIO, base64, binascii, hashlib, string, struct
from random import choice

from Crypto.Cipher import AES


class DingCrypto:
    def __init__(self,encodeAesKey,key):
        self.encodeAesKey = encodeAesKey
        self.key = key
        self.aesKey = base64.b64decode(self.encodeAesKey + '=')

    def encrypt(self, content):
        """
        加密
        :param content:
        :return:
        """
        msg_len = self.length(content)
        content = self.generateRandomKey(16) + msg_len + content + self.key
        contentEncode = self.pks7encode(content)
        iv = self.aesKey[:16]
        aesEncode = AES.new(self.aesKey, AES.MODE_CBC, iv)
        aesEncrypt = aesEncode.encrypt(contentEncode)
        return base64.encodestring(aesEncrypt).replace('\n','')

    def length(self, content):
        """
        将msg_len转为符合要求的四位字节长度
        :param content:
        :return:
        """
        l = len(content)
        return struct.pack('>l', l)

    def pks7encode(self, content):
        """
        安装 PKCS#7 标准填充字符串
        :param text: str
        :return: str
        """
        l = len(content)
        output = StringIO.StringIO()
        val = 32 - (l % 32)
        for _ in xrange(val):
            output.write('%02x' % val)
        return content + binascii.unhexlify(output.getvalue())

    ##解密钉钉发送的数据
    def decrypt(self, content):
        """
        解密
        :param content:
        :return:
        """
        content = base64.b64decode(content)  ##钉钉返回的消息体
        iv = content[:AES.block_size]  ##初始向量
        aesDecode = AES.new(self.aesKey, AES.MODE_CBC, iv)
        decodeRes = aesDecode.decrypt(content[AES.block_size:])[4:].replace(self.key, '')  ##获取去除初始向量，四位msg长度以及尾部corpid
        return decodeRes

    def generateRandomKey(self, size,
                          chars=string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase + string.digits):
        """
        生成加密所需要的随机字符串
        :param size:
        :param chars:
        :return:
        """
        return ''.join(choice(chars) for i in range(size))

    def generateSignature(self, nonce, timestamp, token, msg_encrypt):
        signList = ''.join(sorted([nonce, timestamp, token, msg_encrypt]))
        return hashlib.sha1(signList).hexdigest()
