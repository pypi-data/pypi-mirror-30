# -*- coding:utf-8 -*-
"""数学常用函数模块

定义了一些数学常用的函数和常量。

license:  GPL
library:  laozhao
package:  math
module:   common
author:   Zhao Xin (赵鑫) <pythonchallenge@qq.com>
initial:  2016.03.23
updated:  2016.11.28
"""

__all__ = ['e', 'shx', 'chx', 'factorial', 'fib_generator', 'fib', 'yanghui',
           'hailstone_generator', 'hailstone', 'pi_digit_generator', 'pi_str',
           'factors', 'sum_factors', 'pfactors', 'amicable_pair', 'is_perfect',
           'primes', 'pi']

e = 2.718281828459045
pi = 3.141592653589793


def shx(x):
    """双曲正弦函数
    """
    return (e**x - e**(-x)) / 2.0


def chx(x):
    """双曲余弦函数
    """
    return (e**x + e**(-x)) / 2.0


def factorial(n):
    """阶乘函数

    一个正整数的阶乘（英语:factorial）是所有小于及等于该数的正整数的积，并且有0
    的阶乘为1。自然数n的阶乘写作n!。阶乘的递归方式定义:0! = 1, n! = (n-1)!×n。

    参数:
        n (int): 定义域为自然数

    返回:
        result (int): n的阶乘

    例如:
        >>> fact(5)
        120
    """
    if n in [0, 1]:
        return 1
    elif n >= 2:
        return reduce(lambda a, b: a * b, range(2, n + 1))


def fib_generator(n):
    """斐波拉契数列生成器

    斐波那契数列（Fibonacci sequence），又称黄金分割数列，因数学家列昂纳多·斐
    波那契（Leonardoda Fibonacci）以兔子繁殖为例子而引入，故又称为“兔子数列”，
    指的是这样一个数列: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34...
    在数学上斐波纳契数列以如下递归的方法定义:
    f(0) = 0, f(1) = 1, f(n) = f(n-1) + f(n-2) (n≥2, n∈N*)
    在现代物理、准晶体结构、化学等领域，斐波纳契数列都有直接的应用。

    参数:
        n (int): 斐波拉契数列上界

    生成:
        int: 斐波拉契数列的下一个数

    例如:
        >>> list(fib_generator(10))
        [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    """
    a, b = 0, 1
    while n:
        yield a
        a, b = a + b, a
        n -= 1


def fib(n):
    """斐波拉契数列

    参数:
        n (int): 斐波拉契数列上界

    返回:
        list: 斐波拉契数列

    例如:
        >>> fib(10)
        [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    """
    return list(fib_generator(n))


def yanghui(n):
    """杨辉三角数列生成器

    杨辉三角（又称贾宪三角形，帕斯卡三角形 Pascal's Triangle）
    杨辉三角表现了二项式系数在三角形中的一种几何排列:
              1
            1   1
          1   2   1
        1   3   3   1
      1   4   6   4   1
    1   5   10  10  5   1

    参数:
        n (int): 行数上界

    生成:
        杨辉三角的下一行

    例如:
        >>> for line in yanghui(5): print line
        [1]
        [1, 1]
        [1, 2, 1]
        [1, 3, 3, 1]
        [1, 4, 6, 4, 1]
    """
    # 验证参数类型及大小
    if not isinstance(n, int):
        raise TypeError('参数 n 应为 int 类型')
    if n <= 0:
        raise ValueError('参数 n 应大于 0')

    row = [1]
    for i in range(n):
        row = [1] + [row[j] + row[j + 1] for j in range(i // 2)]
        row += row[::-1] if (i % 2) else row[-2::-1]
        yield row


def hailstone_generator(n):
    """hailstone(冰雹)数列生成器

    数列的前一个数n若为奇数则后一个数为n×3+1,若为偶数则后一个数为n/2,直到1为止。

    注说:
        该算法的有穷性未被验证！

    参数:
        n (int): hailstone(冰雹)数列的第一项

    生成:
        int: hailstone(冰雹)数列的下一个数

    例如:
        >>> list(hailstone_generator(10))
        [10, 5, 16, 8, 4, 2, 1]
    """
    while True:
        yield n
        if n == 1:
            break
        elif n % 2:
            n = n * 3 + 1
        else:
            n /= 2


def hailstone(n):
    """hailstone(冰雹)数列

    参数:
        n (int): hailstone(冰雹)数列的第一项

    返回:
        list: hailstone(冰雹)数列

    例如:
        >>> hailstone(10)
        [10, 5, 16, 8, 4, 2, 1]
    """
    return list(hailstone_generator(n))


def factors(n):
    """返回正整数n的所有真因数列表

    参数:
        n (int): 正整数

    返回:
        list: 正整数n的所有约数的列表

    例如:
        >>> factors(999)
        [1, 3, 9, 27, 37, 111, 333]
    """
    return [i for i in xrange(1, n // 2 + 1) if n % i == 0]


def sum_factors(n):
    """求n的所有真因数的和

    参数:
        n (int): 正整数

    返回:
        int: n的所有真因数的和

    例如:
        999 的约数有: [1, 3, 9, 27, 37, 111, 333]
        1 + 3 + 9 + 27 + 37 + 111 + 333 = 521
        >>> sum_factors(999)
        521
    """
    p = 1
    q = n
    s = 0
    while p < q:
        if n % p == 0:
            s += p + q
        p += 1
        q = n / p
    if n == p * q and p == q:
        s += p
    return s - n


def pfactors(n):
    """分解质因数

    有两个以上因数（约数）的自然数叫做合数。每个合数都可以写成几个质数相乘的形
    式，其中每个质数都是这个合数的因数。把一个合数分解成若干个质因数的乘积的形
    式，即求质因数的过程叫做分解质因数。分解质因数只针对合数。合数，数学用语，
    英文名为Composite number，指自然数中除了能被 1 和本身整除外，还能被其他的数
    整除（不包括0)的数。与之相对的是质数，而 1 既不属于质数也不属于合数。最小的
    合数是 4。另外，完全数与相亲数是在它的基础上定义的。

    参数:
        n (int): 合数

    返回:
        result (list): 质因数列表

    例如:
        >>> pfactors(999)
        [3, 3, 3, 37]
    """
    if not isinstance(n, (int, long)):
        raise TypeError('参数 n 应为整数')
    if n < 2:
        raise ValueError('参数 n 应大于 1')
    if n < 4:
        return [n]

    result = []
    while n % 2 == 0:
        n //= 2
        result.append(2)
    d = 3
    while n > 1 and d * d <= n:
        if n % d == 0:
            n //= d
            result.append(d)
        else:
            d += 2
    if n > 1:
        result.append(n)
    return result


def pi_digit_generator(length, decimal_only=True):
    """π数值上各位数字的生成器

    圆周率是圆的周长与直径的比值，一般用希腊字母π表示，是一个在数学及物理学中
    普遍存在的数学常数，它是一个无理数，即无限不循环小数，约等于3.141592654。π
    是精确计算圆周长、圆面积、球体积等几何形状的关键值。在分析学里，π可以严格
    地定义为满足sin(x)=0的最小正实数x。在日常生活中，通常都用3.14代表圆周率去进
    行近似计算。而用十位小数3.141592654便足以应付一般计算。即使是工程师或物理学
    家要进行较精密的计算，充其量也只需取值至小数点后几百个位。1965年，英国数学
    家约翰·沃利斯（John Wallis）出版了一本数学专著，其中他推导出一个公式，发现
    圆周率等于无穷个分数相乘的积。2015年，罗切斯特大学的科学家们在氢原子能级的
    量子力学计算中发现了与圆周率相同的公式。

    注说:
        算法来自维基百科Pi页面

    参数:
        length (int): 希望生成的总位数 (当只生成小数部分时为小数部分保留的位数)
        decimal_only (bool): 是否只生成小数部分，默认为True

    生成:
        int: 下一位数字 (最后一位为四舍五入的值)

    例如:
        >>> from laozhao.math import pi_digit_generator
        >>> '3.' + ''.join(map(str, pi_digit_generator(40)))
        '3.1415926535897932384626433832795028841972'
    """
    # 是否只生成小数部分? 初始值不同
    k, a, b, a1, b1 = (3, 0, 4, 40, 24) if decimal_only else (2, 4, 1, 12, 4)
    while length >= 0:
        # 估算
        p, q, k = k * k, 2 * k + 1, k + 1
        a, b, a1, b1 = a1, b1, p * a + q * a1, p * b + q * b1
        # 公共位
        d, d1 = a // b, a1 // b1
        while d == d1:
            if length > 1:
                yield d
            elif length == 1:
                last_digit = d                  # 暂存最后一位
            else:
                yield last_digit + (d >= 5)     # 四舍五入
                return
            a, a1 = 10 * (a % b), 10 * (a1 % b1)
            d, d1 = a // b, a1 // b1
            length -= 1


def pi_str(n):
    """π字符串

    生成指定小数位数的π的字符串 (最后一位为四舍五入的值)。

    参数:
        n (int): 小数位数

    返回:
        str: π的字符串

    例如:
        >>> from laozhao.math import pi_str
        >>> pi_str(40)
        '3.1415926535897932384626433832795028841972'
    """
    return '3.' + ''.join(map(str, pi_digit_generator(n)))


def is_perfect(n):
    """判断完全数

    完全数，又称完美数或完备数，是一些特殊的自然数：它所有的真因子（即除了自身
    以外的约数）的和，恰好等于它本身，完全数不可能是楔形数。首十个完全数是:
        6（1位）
        28（2位）
        496（3位）
        8128（4位）
        33550336（8位）
        8589869056（10位）
        137438691328（12位）
        2305843008139952128（19位）
        2658455991569831744654692615953842176（37位）
        191561942608236107294793378084303638130997321548169216（54位）

    参数:
        n (int): 待判断的自然数n

    返回:
        bool: n是否是完全数

    例如:
        >>> is_perfect(220)
        False
        >>> is_perfect(28)
        True
    """
    return sum_factors(n) == n


def amicable_pair(boy):
    """相亲数函数

    相亲数（Amicable Pair），又称亲和数、友爱数、友好数，指两个正整数中，彼此的
    全部约数之和（本身除外）与另一方相等。毕达哥拉斯曾说：“朋友是你灵魂的倩影，
    要像220与284一样亲密。”
        220的全部约数（除掉本身）相加是：1+2+4+5+10+11+20+22+44+55+110 = 284
        284的全部约数（除掉本身）相加是：1+2+4+71+142 = 220

    参数:
        boy (int): 待寻觅相亲数的整数boy

    返回:
        girl (int): boy的相亲数，返回None时表示boy没有相亲数

    例如:
        >>> amicable_pair(220)
        284
    """
    girl = sum_factors(boy)
    if boy == sum_factors(girl) != girl:
        return girl


def primes(n):
    """求小于n的质数

    质数（prime number）又称素数，是指只能被1和该数本身整除的正整数。根据算术基
    本定理，每一个比1大的整数，要么本身是一个质数，要么可以写成一系列质数的乘
    积，最小的质数是2，质数有无穷多个。

    筛素数法:
        筛素数法比枚举法节约极大量的时间（定n为所求最大值，m为<=n的质数个数，那
        么枚举法的时间复杂度为O(n^2)，而筛素数法为O(m*n),显然m<<n，所以时间效率
        有很大提升。）。如求1000000以内的质数，用筛素数法可在2s内解决，思路:建
        立一个bool型数组M，若已知一个数M[k]是质数，那么M[nk]（n,k均是正整数）必
        然为合数，可将它们统统去除。

    参数:
        n (int): 整数，大于等于4，求质数的范围上界

    返回:
        小于n的质数，numpy可用时返回numpy.ndarray，否则返回列表
    """
    try:
        # http://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n-in-python/
        # referenced function: primesfrom2to (maybe the fastest with numpy)
        import numpy as np
        s = np.ones(n / 3 + (n % 6 == 2), dtype=np.bool)  # sieve
        s[0] = False
        for i in xrange(int(n**0.5) // 3 + 1):
            if s[i]:
                k = 3 * i + 1 | 1
                s[((k * k) // 3)::2 * k] = False
                s[(k * k + 4 * k - 2 * k * (i & 1)) // 3::2 * k] = False
        return np.r_[2, 3, ((3 * np.nonzero(s)[0] + 1) | 1)]
    except:
        # http://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n-in-python/
        # referenced function: primes2 (maybe the fastest without numpy)
        c = (n % 6 > 1)  # correction
        n = {0: n, 1: n - 1, 2: n + 4, 3: n + 3, 4: n + 2, 5: n + 1}[n % 6]
        s = [False] + [True] * (n // 3 - 1)  # sieve
        for i in xrange(int(n**0.5) // 3 + 1):
            if s[i]:
                k = 3 * i + 1 | 1
                s[((k * k) // 3)::2 * k] = [False] * \
                    ((n // 6 - k * k // 6 - 1) // k + 1)
                s[(k * k + 4 * k - 2 * k * (i & 1)) // 3::2 * k] = \
                    [False] * ((n // 6 - (k * k + 4 * k - 2 *
                                          k * (i & 1)) // 6 - 1) // k + 1)
        return [2, 3] + [3 * i + 1 | 1 for i in xrange(1, n // 3 - c) if s[i]]


# 以下为测试代码
if __name__ == '__main__':
    assert factorial(0) == 1
    assert factorial(3) == 6
    assert factorial(5) == 120
    assert factorial(20) == 2432902008176640000
    assert fib(10) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert hailstone(7) == [7, 22, 11, 34, 17, 52, 26, 13,
                            40, 20, 10, 5, 16, 8, 4, 2, 1]
    assert pfactors(27) == [3, 3, 3]
    assert pfactors(314) == [2, 157]
    assert pfactors(999) == [3, 3, 3, 37]
    assert pfactors(1234) == [2, 617]
    yht = yanghui(10)
    assert next(yht) == [1]
    assert next(yht) == [1, 1]
    assert next(yht) == [1, 2, 1]
    assert next(yht) == [1, 3, 3, 1]
    assert next(yht) == [1, 4, 6, 4, 1]
    assert next(yht) == [1, 5, 10, 10, 5, 1]
    assert next(yht) == [1, 6, 15, 20, 15, 6, 1]
    assert next(yht) == [1, 7, 21, 35, 35, 21, 7, 1]
    assert next(yht) == [1, 8, 28, 56, 70, 56, 28, 8, 1]
    assert next(yht) == [1, 9, 36, 84, 126, 126, 84, 36, 9, 1]
    assert pi_str(30) == '3.1415926535897932384626433832710'
    assert factors(999) == [1, 3, 9, 27, 37, 111, 333]
    assert sum_factors(220) == 284
    assert sum_factors(284) == 220
    assert is_perfect(28)
    assert not is_perfect(220)
    assert amicable_pair(220) == 284
    assert amicable_pair(284) == 220
    assert list(primes(100)) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37,
                                 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83,
                                 89, 97]
    print u'测试完毕'
