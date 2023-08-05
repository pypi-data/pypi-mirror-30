# -*- coding: utf-8 -*-
"""zhao.xin_algorithm
This module provides common algorithms.
"""


try:
    import numpy as np
    NUMPY_IMPORTED = True
except ImportError:
    NUMPY_IMPORTED = False


def is_palindrome(number):
    """判断number是否是回文数
    """
    _number = str(number)
    _middle = sum(divmod(len(_number), 2))
    return _number[:_middle] == _number[:-_middle - 1:-1]


def fib(length):
    """斐波拉契数列生成器
    """
    _a, _b = 0, 1
    for _ in range(length):
        yield _a
        _a, _b = _a + _b, _a


if NUMPY_IMPORTED:
    def primes(limit):
        """n以内的质数的生成器
        """
        nums = np.arange(2, limit + 1)      # 从2到n的整数数组，长度为n-1
        for i in range(limit - 1):          # 遍历nums数组
            _p = nums[i]                    # 当前的数值为p
            if _p:                          # 若非0则为质数
                yield _p
                nums[i + _p::_p] = 0        # 将p以后p整倍数的整数置0
else:
    def primes(limit):
        """n以内的质数的生成器
        """
        nums = list(range(2, limit + 1))    # 从2到n的整数列表，长度为n-1
        for i in range(limit - 1):          # 遍历nums列表
            _p = nums[i]                    # 当前的数值为p
            if _p:                          # 若非0则为质数
                yield _p
                for j in range(i + _p, limit - 1, _p):
                    nums[j] = 0             # 将p以后p整倍数的整数置0


if __name__ == '__main__':
    print(is_palindrome(98089))
    print(list(fib(20)))
    print(list(primes(1000)))
