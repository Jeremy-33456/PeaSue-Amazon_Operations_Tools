import wmi
import base64

device_id = wmi.WMI().Win32_BaseBoard()[0].SerialNumber
secret = str(base64.b64encode(bytes(device_id, 'ansi')), 'ansi')
print(secret)
input('输入任意字符退出。。。')
