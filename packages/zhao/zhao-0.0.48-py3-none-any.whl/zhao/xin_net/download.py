# -*- coding:utf-8 -*-
"""网络通用函数模块

Copyright © 2016 Zhao Xin

license:  GPL
library:  laozhao
package:  net
module:   common
author:   Zhao Xin (赵鑫) <pythonchallenge@qq.com>
initial:  2016-04-06 15:58:00
update:   2017-01-04 14:20:15
"""


def download(download_link, downloads_path='downloads', threads=5, chunk_size=40960, **kwargs):

    pass
    '''
    import os
    import re
    import struct
    import hashlib
    import requests
    import smtplib
    from email.mime.text import MIMEText
    def prepare_download_file(file_path, file_size, chunk_size):
        chunk_count = (file_size + chunk_size - 1) // chunk_size
        if not os.path.exists(file_path):
            download_file = open(file_path, 'wb+')
            # download_file.seek(file_size + 16 * chunk_count - 1)
            download_file.write(bytearray(file_size + 16 * chunk_count))
            download_file.flush()
            unfinished_blocks = range(chunk_count)
        else:
            download_file = open(file_path, 'rb+')
            local_size = os.path.getsize(file_path)
            unfinished_blocks = []
            if local_size == file_size:
                pass
            elif local_size == file_size + 16 * chunk_count:
                download_file.seek(file_size)
                hash_data = download_file.read()
                hash_values = struct.unpack('16s' * chunk_count, hash_data)
                download_file.seek(0)
                for i, hashed_md5 in enumerate(hash_values):
                    block_data = download_file.read(chunk_size)
                    block_md5 = hashlib.md5(block_data).digest()
                    if block_md5 != hashed_md5:
                        unfinished_blocks.append(i)
            else:
                raise Exception(
                    'exists file hash data error or size not match.')
        return download_file, unfinished_blocks

    def ants_job(download_url, download_file, filesize,
                 chunks, lock, auth=None, timeout=(0.5, 0.5)):
        while True:
            index, start, end = chunk = chunks.get()
            headers = {'Range': 'bytes={}-{}'.format(start, end), 'auth': auth}
            try:
                data = requests.get(
                    download_url, headers=headers, timeout=timeout).content
                md5 = hashlib.md5(data).digest()
                if data and lock.acquire(True):
                    download_file.seek(start)
                    download_file.write(data)
                    download_file.seek(filesize + 16 * index)
                    download_file.write(md5)
                    lock.release()
                else:
                    chunks.put(chunk)
            except:
                chunks.put(chunk)
            chunks.task_done()

    def truncate_download_file(download_file, file_size, chunk_size):
        unfinished_blocks = []
        chunk_count = (file_size + chunk_size - 1) // chunk_size
        download_file.flush()
        download_file.seek(file_size)
        hash_data = download_file.read()
        hash_values = struct.unpack('16s' * chunk_count, hash_data)
        download_file.seek(0)
        for i, hashed_md5 in enumerate(hash_values):
            if not i == chunk_count - 1:
                block_data = download_file.read(chunk_size)
            else:
                block_data = download_file.read(file_size % chunk_size)
            block_md5 = hashlib.md5(block_data).digest()
            if block_md5 != hashed_md5:
                unfinished_blocks.append(i)
        if not unfinished_blocks:
            download_file.seek(file_size)
            download_file.truncate()
            download_file.flush()
        return unfinished_blocks

    username, password = kwargs.get('username', ''), kwargs.get('password', '')
    if username and password:
        auth = (username, password)
    else:
        auth = None

    download_url, filename, filesize, resumeable = parse_download_link(
        download_link)

    try:
        download_path = prepare_download_path(downloads_path, filename)
        if resumeable and threads > 1:
            download_file, unfinished_blocks = prepare_download_file(download_path,
                                                                     filesize,
                                                                     chunk_size)
            if unfinished_blocks:
                lock = Lock()
                chunks = Queue()
                for chunk_index in unfinished_blocks:
                    start = chunk_size * chunk_index
                    end = start + chunk_size - 1
                    chunk = chunk_index, start, end
                    chunks.put(chunk)
                for _ in xrange(threads):
                    thread = Thread(target=ants_job,
                                    args=(download_url, download_file, filesize,
                                          chunks, lock, auth))
                    thread.daemon = True
                    thread.start()
                chunks.join()
                truncate_download_file(download_file, filesize, chunk_size)
            else:
                print('file already exists.')
        else:
            download_file = open(download_path, 'wb')
            for chunk in requests.get(download_url,
                                      headers={'auth': auth},
                                      stream=True).iter_content(chunk_size):
                download_file.write(chunk)
        download_file.close()
    except Exception as e:
        print('ERROR: {}'.format(e))
    finally:
        return filename, filesize
'''
