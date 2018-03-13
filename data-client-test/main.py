# -*- coding: utf-8 -*-
# try:
#     import androidhelper as android
# except ImportError:
#     import android

import os
import socket


def main():
    # android_system = android.Android()
    print('客户端启动')
    # android_system.makeToast('客户端启动')
    # server_ip = android_system.dialogGetInput('连接服务器', '服务器IP地址').result
    server_ip = '127.0.0.1'
    print('正在连接服务器：%s' % server_ip)
    # android_system.makeToast('正在连接服务器')
    socket_server = socket.socket()
    socket_server.connect((server_ip, 20183))
    print('开始同步数据')
    # android_system.makeToast('开始同步数据')
    # target_dir = '/storage/9017-100F/Pictures/pic'
    # target_dir = '/storage/emulated/0/test'
    # target_dir = 'd:/project/test1'
    target_dir = 'C:\\Users\\Administrator\\Desktop\\test1'
    current_file = None
    file_name = ''
    file_index = 1
    receive_list = []
    while True:
        data = socket_server.recv(300).decode('utf-8')
        if data == 'exit':
            socket_server.sendall(bytes('success', 'utf-8'))
            print('退出')
            break
        elif data[:7] == 'current':
            file_name = data[9:]
            receive_list.append(file_name)
            target_file = '%s/%s' % (target_dir, file_name)
            if os.path.isfile(target_file):
                print('跳过文件：%s' % file_name)
                socket_server.sendall(bytes('skip', 'utf-8'))
            else:
                print('选中文件：%s' % file_name)
                current_file = open(target_file, 'wb')
                socket_server.sendall(bytes('success', 'utf-8'))
        elif data == 'file-data':
            socket_server.sendall(bytes('start', 'utf-8'))
            print('正在接收数据：%s' % file_name)
            file_size = int(socket_server.recv(30).decode('utf-8'))
            socket_server.sendall(bytes('got', 'utf-8'))
            recv_size = 0
            while recv_size < file_size:
                file_data = socket_server.recv(20480000)
                current_file.write(file_data)
                recv_size += len(file_data)
            print('接收完毕：%s' % file_name)
            socket_server.sendall(bytes('finished', 'utf-8'))
        elif data == 'close':
            current_file.close()
            print('%s 已关闭' % file_name)
            socket_server.sendall(bytes('closed', 'utf-8'))
        file_index = file_index + 1
    socket_server.close()

    # 查找现有的文件列表
    # 将不存在的文件删除
    target_file_list = os.listdir(target_dir)
    for file_item in target_file_list:
        if file_item not in receive_list:
            del_file = '%s/%s' % (target_dir, file_item)
            print('删除文件：%s' % del_file)
            os.unlink(del_file)


if __name__ == '__main__':
    main()
