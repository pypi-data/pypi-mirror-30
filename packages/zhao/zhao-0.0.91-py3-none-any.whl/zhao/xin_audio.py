#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""本模块提供声音相关操作的实现
"""

__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All rights reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)'
__version__ = '2018-03-28'


import wave


def save_wave(audio_data, filename, sample_rate=16000, sample_width=2, channels=1):
    wave_file = wave.open(filename, 'wb')
    wave_file.setframerate(sample_rate)
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(sample_width)
    wave_file.writeframes(audio_data.tostring())
    wave_file.close()
