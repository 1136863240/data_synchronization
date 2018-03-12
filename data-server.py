# -*- coding: utf-8 -*-

import sys
import os
import socket


def send_cmd(conn, cmd):
    if isinstance(cmd, str):
        print('发送命令：%s' % cmd)
        conn.sendall(bytes(cmd, 'utf-8'))
    else:
        block_count = len(cmd)
        conn.sendall(bytes(str(block_count), 'utf-8'))
        callback = conn.recv(10).decode('utf-8')
        if callback == 'got':
            sended_count = 0
            while sended_count < block_count:
                sended_count += conn.send(cmd)
    return conn.recv(10).decode('utf-8')


def main():
    print('服务器初始化')
    src_dir = ''  # 同步源目录
    socket_server = None  # 服务器套接字

    if len(sys.argv) != 2:
        print('初始化失败：未定义源目录路径')
    src_dir = sys.argv[1]
    socket_server = socket.socket()
    socket_server.bind(('192.168.1.104', 20183))
    # socket_server.bind(('127.0.0.1', 20183))
    # socket_server.bind(('192.168.42.171', 20183))
    socket_server.listen(1)
    print('初始化完毕，等待客户端连接')

    client_conn, client_addr = socket_server.accept()
    print('%s 已连接' % client_addr[0])

    # 开始同步
    # 列出目录下的所有文件
    src_files = os.listdir(src_dir)
    src_file_count = len(src_files)
    file_index = 1
    for file in src_files:
        # 跳过目录
        if os.path.isdir('%s/%s' % (src_dir, file)):
            continue

        # 选中同步文件
        recv_data = send_cmd(client_conn, 'current: %s' % file)
        if recv_data == 'success':
            print('%s 开始同步文件(%d/%d)：%s' %
                  (client_addr[0], file_index, src_file_count, file))
        elif recv_data == 'skip':
            print('%s 跳过文件(%d/%d)：%s' %
                  (client_addr[0], file_index, src_file_count, file))
            # 准备下一次同步
            file_index = file_index + 1
            continue

        # 开始同步数据
        recv_data = send_cmd(client_conn, 'file-data')
        if recv_data == 'start':
            print('%s 传输文件：%s' %
                  (client_addr[0], file))
            current_file = open('%s/%s' % (src_dir, file), 'rb')
            file_content = current_file.read(2048000)
            print('文件大小：%d' % len(file_content))
            recv_data = send_cmd(client_conn, file_content)

        # 接收完成信息
        if recv_data == 'finished':
            print('%s 完成文件(%d/%d)' %
                  (client_addr[0], file_index, src_file_count))
            current_file.close()
            recv_data = send_cmd(client_conn, 'close')
            if recv_data == 'closed':
                print('%s 已关闭 %s 的传输' % (client_addr[0], file))

        # 准备下一次同步
        file_index = file_index + 1
    

    # 同步完毕，通知客户端退出
    print('%s 同步完毕' % client_addr[0])
    recv_data = send_cmd(client_conn, 'exit')
    if recv_data == 'success':
        print('%s 已退出' % client_addr[0])
    
    socket_server.close()


if __name__ == '__main__':
    main()
