# -*- coding:utf-8 -*-
"""最大公约数模块

定义了求最大公约数函数。

license:  GPL
library:  laozhao
package:  math
module:   gcd
author:   Zhao Xin (赵鑫) <pythonchallenge@qq.com>
initial:  2016.04.04
updated:  2016.11.27

最大公约数Greatest Common Divisor，简写为GCD，指某几个整数共有约数中最大的一个。

假如整数n除以m，结果是无余数的整数，那么我们称m就是n的约数。需要注意的是，唯有被
除数，除数，商皆为整数，余数为零时，此关系才成立。 反过来说，我们称n为m的倍数。
要留意的是:

    约数不限正负
    1, -1, n 和 -n 这四个数叫做 n 的明显约数

定义域:
    整数域

性质:
    gcd(a, b) = gcd(b, a) 交换律
    gcd(a, gcd(b, c)) = gcd(gcd(a, b), c) 结合律
    m为非负整数，则 gcd(m·a, m·b) = m·gcd(a, b) 分配律
    gcd(a, 0) = |a|, for a ≠ 0
    gcd(a, 1) = 1
    gcd(-a, b) = gcd(a, b)
    gcd(a, a) = |a|
    gcd(a, b) = gcd(b, a-b)
    m为非零公约数，则 gcd(a/m, b/m) = gcd(a, b)/m
    m为任意整数，则 gcd(a + m·b, b) = gcd(a, b)
    gcd(a, b) = gcd(b, a mod b)

定义:
    gcd(0, 0) = 0

更相减损法:
    也叫更相减损术，是出自《九章算术》的一种求最大公约数的算法，它原本是为约分而设计
    的，但它适用于任何需要求最大公约数的场合。《九章算术》是中国古代的数学专著，其中
    的“更相减损术”可以用来求两个数的最大公约数，即“可半者半之，不可半者，副置分母、
    子之数，以少减多，更相减损，求其等也。以等数约之。”
    while n != m:
        n -= m
        if n < m:
            n, m = m, n
    return n
"""


__all__ = ["gcd"]


def gcd(n, m):
    """求 n 和 m 最大公约数

    参数:
        自然数 n 和 m

    返回:
        n 和 m 的最大公约数
    """
    # 检查参数类型
    if not isinstance(n, int) or not isinstance(m, int):
        raise ValueError("参数必须是整数！")

    # 因为 gcd(-a, b) = gcd(a, b)，分别取绝对值以简化问题
    n, m = abs(n), abs(m)

    # 因为交换律 gcd(a, b) = gcd(b, a)，将参数调整为 n <= m 以简化问题
    if n > m:
        n, m = m, n

    # gcd(a, 0) = |a|
    if n == 0:
        return m

    # gcd(a, 1) = 1
    if n == 1:
        return 1

    # gcd(a, a) = |a|
    if n == m:
        return n

    if n < 2**64:
        # 交由欧几里德算法
        return _gcd_euclid(n, m)
    else:
        # 交由Stein算法递归运算
        return _gcd_stein(n, m)


def _gcd_euclid(n, m):
    """欧几里德算法求最大公约数

    欧几里德算法又称辗转相除法，其计算原理依赖于下面的定理:

    定理:
        gcd(a, b) = gcd(b, a mod b)

    证明:
        a可以表示成 a = kb + r，则 r = a mod b
        假设d是a,b的一个公约数，则有
        d|a, d|b，而r = a - kb，因此d|r
        因此d是(b,a mod b)的公约数

        假设d 是(b,a mod b)的公约数，则
        d | b , d |r ，但是a = kb +r
        因此d也是(a,b)的公约数

        因此(a,b)和(b,a mod b)的公约数是一样的，其最大公约数也必然相等，得证。

    参数:
        自然数 n 和 m

    返回:
        n 和 m 的最大公约数
    """
    while n != 0:
        n, m = m % n, n
    return m


def _gcd_stein(n, m):
    """Stein算法求最大公约数

    由J. Stein 1961年提出的Stein算法是一种计算两个数最大公约数的算法，它是针对欧几
    里德算法在对大整数进行运算时，需要试商导致增加运算时间的缺陷而提出的改进算法。
    Stein算法只有整数的移位和加减法，证明Stein算法的正确性，首先必须注意到以下结论:
        gcd(a, a) = a，也就是一个数和其自身的公约数仍是其自身。
        gcd(ka, kb) = k * gcd(a, b)，也就是最大公约数运算和倍乘运算可以交换。特殊
        地，当 k = 2 时，说明两个偶数的最大公约数必然能被2整除。
        当k与b互为质数，gcd(ka, b) = gcd(a, b)，也就是约掉两个数中只有其中一个含有
        的因子不影响最大公约数。特殊地，当k=2时，说明计算一个偶数和一个奇数的最大公
        约数时，可以先将偶数除以2。

    参数:
        自然数 n 和 m

    返回:
        n 和 m 的最大公约数
    """
    if n == 0:
        return m
    elif m == 0:
        return n
    elif n == m:
        return n
    elif n % 2 == 0:
        if m % 2 == 0:
            return 2 * _gcd_stein(n // 2, m // 2)
        else:
            return _gcd_stein(n // 2, m)
    elif m % 2 == 0:
        return _gcd_stein(n, m // 2)
    else:
        return _gcd_stein(abs(n - m) // 2, min(n, m))


if __name__ == "__main__":
    assert gcd(21, 42) == 21
    assert gcd(18, -27) == 9
    assert gcd(0, 4) == 4
    assert gcd(1, 4) == 1
