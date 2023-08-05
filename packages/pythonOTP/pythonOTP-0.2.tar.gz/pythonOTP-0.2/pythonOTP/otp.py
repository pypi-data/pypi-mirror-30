import base64
import datetime
import hmac
import hashlib
import random
import time
import unicodedata


def _base32_secret_key():
    key_set = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    secret_key = random.sample(key_set, 16)
    return ''.join(secret_key)


class TOTP:

    def __init__(self, userid, issuer=None, period=30):
        self.secret_key=_base32_secret_key()
        self.userid=userid
        self.issuer=issuer or ''
        self.period=period

    def create_url(self):
        base_url = 'otpauth://totp/{0}{1}{2}'
        part1, part2, part3 = '', '', ''
        if self.issuer:
            self.issuer = self.issuer.replace(' ','%20')
            part1 = self.issuer + ':' + self.userid
            part3 = '&issuer=' + self.issuer + '&algorithm=SHA1&digits=6&period=' + str(self.period)
        else:
            part1 = self.userid
            part3 = '&algorithm=SHA1&digits=6&period=' + str(self.period)
        part2 = '?secret=' + self.secret_key
        return base_url.format(part1, part2, part3)

    def now(self, valid_counter=0):
        """
        생성되어 있는 OTP알고리즘의
        현재 암호값을 출력한다.
        """
        # date클래스와 time클래스의 조합으로 시간대 정보를 반환
        date = datetime.datetime.now()
        # 지방표준시 time_struct 를 입력받아 누적된 초를 받환 한다.
        mk_time = time.mktime(date.timetuple())
        # 누적된 초 단위 값을 period 변수로 나눔
        timecode = int(mk_time/int(self.period))

        if timecode < 0:
            raise ValueError('input must be positive integer')
        hasher = hmac.new(base64.b32decode(self.secret_key, casefold=True), self.int_to_bytestring(timecode+valid_counter), hashlib.sha1)
        hmac_hash = bytearray(hasher.digest())
        offset = hmac_hash[-1] & 0xf
        code = ((hmac_hash[offset] & 0x7f) << 24 |
                (hmac_hash[offset + 1] & 0xff) << 16 |
                (hmac_hash[offset + 2] & 0xff) << 8 |
                (hmac_hash[offset + 3] & 0xff))
        str_code = str(code % 10 ** 6)
        while len(str_code) < 6:
            str_code = '0' + str_code

        return str_code

    def int_to_bytestring(self, timecode):
        result = bytearray()
        while timecode !=0:
            result.append(timecode & 0xFF)
            timecode >>= 8
        length = len(list(result))
        padding_control = [0] * (8-length)
        result = list(result) + padding_control
        return bytes(bytearray(reversed(result)))

    def is_true(self, password, valid_second=0):

        for i in range(-valid_second, valid_second+1):
            password = unicodedata.normalize('NFKC', str(password))
            password_now = unicodedata.normalize('NFKC', self.now(i))
            if hmac.compare_digest(password, password_now):
                return True
        return False
