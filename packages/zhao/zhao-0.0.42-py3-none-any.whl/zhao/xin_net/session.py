# -*- coding: utf-8 -*-
"""zhao.xin_net.session
"""

from time import time
from os.path import splitext
from urllib.parse import urlparse
from concurrent.futures import as_completed, ThreadPoolExecutor
from requests import Session, Timeout
from .common import I_AM_WEB_BROWSER


class ThreadingSession(Session):
    """多线程HTTP会话类

    使用：
        >>> with ThreadingSession() as session:
                url, path, size, elapse = session.download('http://foo.com/sound.m4a',
                                                           '/tmp/sound.m4a')
        >>> print(f'Download: {url} to {path} in {elapsed:0.2f}s @ {size/1024/elapse:0.2f} KiB/s')
        Download: http://foo.com/sound.m4a to /tmp/sound.m4a in 1.04s @ 10819.15 KiB/s
    """

    def __init__(self, user_agent=I_AM_WEB_BROWSER):
        super().__init__()
        self.headers['User-Agent'] = user_agent

    def download(self, url, path, chunk_size=1024 * 512, max_workers=16):
        """多线程下载
        """
        time_start = time()
        (_accessible, _seconds, url, _filename, _extension,
         file_size, _resumeable) = self.url_needle(url)
        with ThreadPoolExecutor(max_workers) as pool, open(path, 'wb') as output:
            all_jobs = (pool.submit(self.fetch_chunk, url, offset, chunk_size)
                        for offset in range(0, file_size, chunk_size))
            for finished_job in as_completed(all_jobs):
                offset, chunk = finished_job.result()
                output.seek(offset)
                output.write(chunk)
        time_cost = time() - time_start
        return (url, path, file_size, time_cost)

    def downloads(self, tasks, max_workers=5):
        """并行下载
        """
        with ThreadPoolExecutor(max_workers) as pool:
            jobs = (pool.submit(self.download, url, path)
                    for url, path in tasks)
            for job in as_completed(jobs):
                yield job.result()

    def fetch_chunk(self, url, offset, size):
        """获取分块
        """
        headers = self.headers.copy()
        headers['Range'] = f'bytes={offset}-{offset+size}'
        retry = 3
        try:
            while retry > 0:
                response = self.get(url, headers=headers)
                if response.ok:
                    return offset, response.content
        except Timeout:
            retry -= 1
            if retry <= 0:
                raise Timeout

    def url_needle(self, url):
        """URL探针
        """
        response = self.head(url)
        while response.is_permanent_redirect or response.is_redirect:
            response = self.head(response.headers.get('Location'))
        accessible = response.ok                                         # 是否存在
        seconds = response.elapsed.total_seconds()                       # 响应时间
        url = response.url                                               # 真实地址
        filename = urlparse(url).path.split('/')[-1]                     # 文件名
        extension = splitext(filename)[-1]                               # 后缀名
        filesize = int(response.headers.get('Content-Length', 0))        # 文件大小
        resumeable = bool(response.headers.get('Accept-Ranges', False))  # 支持续传
        return accessible, seconds, url, filename, extension, filesize, resumeable
