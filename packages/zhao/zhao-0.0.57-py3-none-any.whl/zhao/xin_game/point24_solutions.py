#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""求24点算式
"""

# 算式模式参考自：http://www.cnblogs.com/grenet/archive/2013/03/17/2964455.html
# 该作者制作了24点算式模式的列表，列出有解的独立模式50种（取值范围1~10，编号1~50）
# 不过按1~13的取值范围则应该有66种独立模式，作格式化字符串列表patterns以供穷举。

# +++
# N+N+N+N       (1)

# ++-
# N+N+N-N       (2)

# ++*
# N+N+N*N       (3)
# N+(N+N)*N     (4)
# (N+N+N)*N     (5)

# ++/
# N+N+N/N       (6)
# N+(N+N)/N     (7)
# (N+N+N)/N     (8)

# +-+
# N+N-N+N -> N+N+N-N
# N+N-(N+N) -> N+N-N-N 无解

# +--
# N+N-N-N       (51)
# N+N-(N-N) -> N+N-N+N, N+N+N-N

# +-*
# N+N-N*N       (52)
# N+(N-N)*N     (9)
# (N+N-N)*N     (10)

# +-/
# N+N-N/N       (53)
# N+(N-N)/N     (54)
# (N+N-N)/N     (55)

# +*+
# N+N*N+N       (11)
# (N+N)*N+N     (12)
# N+N*(N+N) -> (N+N)*N+N
# (N+N)*(N+N)   (13)

# +*-
# N+N*N-N       (14)
# (N+N)*N-N     (15)
# N+N*(N-N) -> N+(N-N)*N
# (N+N)*(N-N)   (16)

# +**
# N+N*N*N       (17)
# (N+N)*N*N     (18)
# (N+N*N)*N     (19)

# +*/
# N+N*N/N       (20)
# (N+N)*N/N     (21)
# (N+N*N)/N     (22)

# +/+
# N+N/N+N       (23)
# (N+N)/N+N     (24)
# N+N/(N+N)     (56)
# (N+N)/(N+N)   (57)

# +/-
# N+N/N-N       (58)
# (N+N)/N-N     (59)
# N+N/(N-N)     (60)
# (N+N)/(N-N)   (61)

# +/*
# N+N/N*N -> N+N*N/N
# (N+N)/N*N  -> (N+N)*N/N
# (N+N/N)*N     (25)
# N+N/(N*N) -> N+N/N/N 无解
# (N+N)/(N*N) -> (N+N)/N/N 无解

# +//
# N+N/N/N       (62)
# (N+N)/N/N     (63)
# (N+N/N)/N     (64)
# N+N/(N/N) -> N+N/N*N, N+N*N/N
# (N+N)/(N/N) -> (N+N)/N*N, (N+N)*N/N

# -++
# N-N+N+N -> N+N+N-N
# N-(N+N)+N -> N-N-N+N, N+N-N-N 无解
# N-(N+N+N) -> N-N-N-N 无解

# -+-
# N-N+N-N -> N+N-N-N 无解
# N-(N+N)-N -> N-N-N-N 无解
# N-(N+N-N) -> N-N-N+N, N+N-N-N 无解

# -+*
# N-N+N*N -> N+N*N-N
# N-(N+N)*N 无解
# N-(N+N*N) 无解
# (N-N+N)*N -> (N+N-N)*N
# (N-(N+N))*N -> (N-N-N)*N

# -+/
# N-N+N/N       (65)
# N-(N+N)/N 无解
# N-(N+N/N) -> N-N-N/N 无解
# (N-N+N)/N -> (N+N-N)/N 无解
# (N-(N+N))/N -> (N-N-N)/N 无解

# --+
# N-N-N+N -> N+N-N-N 无解
# N-(N-N)+N -> N-N+N+N, N+N+N-N
# N-(N-N+N) -> N-N+N-N, N+N-N-N 无解
# N+N-N-N -> N-N+N+N, N+N+N-N
# N-N-(N+N) -> N-N-N-N 无解

# ---
# N-N-N-N 无解
# N-N-(N-N) -> N-N-N+N, N+N-N-N 无解
# N-(N-N)-N -> N-N+N-N, N+N-N-N 无解
# N-(N-N-N) -> N-N+N+N, N+N+N-N
# N-(N-(N-N)) -> N-N+N-N, N+N-N-N 无解

# --*
# N-N-N*N 无解
# N-(N-N)*N -> N+(N-N)*N
# (N-N-N)*N     (26)
# (N-(N-N))*N -> (N-N+N)*N, (N+N-N)*N

# --/
# N-N-N/N 无解
# N-(N-N)/N -> N+(N-N)/N 无解
# (N-N-N)/N 无解
# (N-(N-N))/N -> (N-N+N)/N, (N+N-N)/N 无解

# -*+
# N-N*N+N -> N+N-N*N 无解
# (N-N)*N+N -> N+(N-N)*N
# N-N*(N+N) -> N-(N+N)*N 无解
# (N-N)*(N+N) -> (N+N)*(N-N)
# N-(N*N+N) -> N-N*N-N, N-N-N*N 无解

# -*-
# N-N*N-N -> N-N-N*N 无解
# (N-N)*N-N     (27)
# N-N*(N-N) -> N+N*(N-N), N+(N-N)*N
# (N-N)*(N-N)   (28)
# N-(N*N-N) -> N-N*N+N, N+N-N*N 无解

# -**
# N-N*N*N 无解
# (N-N)*N*N     (29)
# (N-N*N)*N     (30)

# -*/
# N-N*N/N 无解
# (N-N)*N/N     (31)
# (N-N*N)/N 无解

# -/+
# N-N/N+N -> N+N-N/N 无解
# (N-N)/N+N -> N+(N-N)/N 无解
# N-N/(N+N) 无解
# (N-N)/(N+N) 无解
# N-(N/N+N) -> N-N/N-N, N-N-N/N 无解

# -/-
# N-N/N-N -> N-N-N/N 无解
# (N-N)/N-N 无解
# N-N/(N-N) -> N+N/(N-N) 无解
# (N-N)/(N-N) 无解
# N-(N/N-N) -> N-N/N+N, N+N-N/N 无解

# -/*
# N-N/N*N 无解
# (N-N)/N*N -> (N-N)*N/N
# (N-N/N)*N     (32)
# N-N/(N*N) -> N-N/N/N 无解
# (N-N)/(N*N) -> (N-N)/N/N 无解

# -//
# N-N/N/N 无解
# (N-N)/N/N 无解
# (N-N/N)/N 无解
# N-N/(N/N) -> N-N/N*N, N-N*N/N 无解
# (N-N)/(N/N) -> (N-N)/N*N, (N-N)*N/N

# *++
# N*N+N+N -> N+N+N*N
# N*(N+N)+N ->N+(N+N)*N
# N*(N+N+N) -> (N+N+N)*N

# *+-
# N*N+N-N -> N-N+N*N
# N*(N+N)-N -> (N+N)*N-N
# N*(N+N-N) -> (N+N-N)*N

# *+*
# N*N+N*N       (33)
# N*(N+N)*N -> (N+N)*N*N
# (N*N+N)*N -> (N+N*N)*N
# N*(N+N*N) -> (N+N*N)*N

# *+/
# N*N+N/N       (34)
# N*(N+N)/N -> (N+N)*N/N
# (N*N+N)/N -> (N+N*N)/N
# N*(N+N/N) -> (N+N/N)*N

# *-+
# N*N-N+N -> N-N+N*N
# N*(N-N)+N -> N+(N-N)*N
# N*(N-N+N) -> (N+N-N)*N
# N*N-(N+N) -> N*N-N-N
# N*(N-(N+N)) -> N*(N-N-N), (N-N-N)*N

# *--
# N*N-N-N       (35)
# N*(N-N)-N -> (N-N)*N-N
# N*(N-N-N) -> (N-N-N)*N
# N*N-(N-N) -> N*N-N+N, N-N+N*N
# N*(N-(N-N)) -> N*(N-N+N), (N+N-N)*N

# *-*
# N*N-N*N       (36)
# N*(N-N)*N -> (N-N)*N*N
# (N*N-N)*N     (37)
# N*(N-N*N) -> (N-N*N)*N

# *-/
# N*N-N/N       (38)
# N*(N-N)/N -> (N-M2)*N/N
# (N*N-N)/N     (39)
# N*(N-N/N) -> (N-N/N)*N

# **+
# N*N*N+N -> N+N*N*N
# N*N*(N+N) -> (N+N)*N*N
# N*(N*N+N) -> (N+N*N)*N

# **-
# N*N*N-N       (40)
# N*N*(N-N) -> (N-N)*N*N
# N*(N*N-N) -> (N*N-N)*N

# ***
# N*N*N*N       (41)

# **/
# N*N*N/N       (42)

# */+
# N*N/N+N -> N+N*N/N
# N*N/(N+N)     (43)
# N*(N/N+N) -> (N+N/N)*N

# */-
# N*N/N-N       (44)
# N*N/(N-N)     (45)
# N*(N/N-N)     (46)

# */*
# N*N/N*N -> N*N*N/N
# N*N/(N*N) -> N*N/N/N

# *//
# N*N/N/N       (47)
# N*N/(N/N) -> N*N/N*N, N*N*N/N

# /++
# N/N+N+N -> N+N+N/N
# N/(N+N)+N -> N+N/(N+N) 无解
# N/(N+N+N) 无解

# /+-
# N/N+N-N -> N-N+N/N 无解
# N/(N+N)-N 无解
# N/(N+N-N) 无解

# /+*
# N/N+N*N -> N*N+N/N
# N/(N+N)*N -> N*N/(N+N)
# (N/N+N)*N -> (N+N/N)*N
# N/(N+N*N) 无解

# /+/
# N/N+N/N       (66)
# N/(N+N)/N 无解
# (N/N+N)/N -> (N+N/N)/N 无解
# N/(N+N/N) 无解
# N/((N+N)/N) -> N/(N+N)*N, N*N/(N+N)

# /-+
# N/N-N+N -> N-N+N/N 无解
# N/N-(N+N) -> N/N-N-N 无解
# N/(N-N)+N -> N+N/(N-N) 无解
# N/(N-N+N) -> N/(N+N-N) 无解
# N/(N-(N+N)) -> N/(N-N-N) 无解

# /--
# N/N-N-N 无解
# N/N-(N-N) -> N/N-N+N, N+N/N-N 无解
# N/(N-N)-N 无解
# N/(N-N-N) 无解
# N/(N-(N-N)) -> N/(N-N+N), N/(N+N-N) 无解

# /-*
# N/N-N*N 无解
# N/(N-N)*N -> N*N/(N-N)
# N/(N-N*N)   无解
# (N/N-N)*N     (48)

# /-/
# N/N-N/N 无解
# N/(N-N)/N 无解
# (N/N-N)/N 无解
# N/(N-N/N)     (49)
# N/((N-N)/N) -> N/(N-N)*N, N*N/(N-N)

# /*+
# N/N*N+N -> N+N*N/N
# N/N*(N+N) -> (N+N)*N/N
# N/(N*N+N) -> N/(N+N*N) 无解
# N/(N*(N+N)) -> N/N/(N+N), N/(N+N)/N 无解

# /*-
# N/N*N-N -> N*N/N-N
# N/N*(N-N) -> N*(N-N)/N
# N/(N*N-N) 无解
# N/(N*(N-N)) -> N/N/(N-N), N/(N-N)/N 无解
# N/(N*N)-N -> N/N/N-N 无解

# /**
# N/N*N*N -> N*N*N/N
# N/(N*N)*N -> N/N/N*N, N*N/N/N
# N/(N*N*N) -> N/N/N/N 无解

# /*/
# N/N*N/N -> N*N/N/N
# N/(N*N)/N -> N/N/N/N 无解
# N/(N*N/N) -> N/N/N*N, N*N/N/N

# //+
# N/N/N+N -> N+N/N/N 无解
# N/N/(N+N) 无解
# N/(N/N+N) -> N/(N+N/N) 无解
# N/(N/(N+N)) -> N/N*(N+N), (N+N)*N/N

# //-
# N/N/N-N 无解
# N/N/(N-N) 无解
# N/(N/N-N)     (50)
# N/(N/(N-N)) -> N/N*(N-N), (N-N)*N/N

# //*
# N/N/N*N -> N*N/N/N
# N/N/(N*N) -> N/N/N/N 无解
# N/(N/N)*N -> N/N*N*N, N*N*N/N
# N/(N/N*N) -> N/N*N/N, N*N/N/N

# ///
# N/N/N/N 无解
# N/N/(N/N) -> N/N/N*N, N*N/N/N
# N/(N/N)/N -> N/N*N/N, N*N/N/N
# N/(N/N/N) -> N/N*N/N, N*N/N/N


from itertools import permutations


def point24_solutions(point1, point2, point3, point4):
    """求24点算式

    使用方法:
        >>> from zhao.xin_game import point24_solutions
        >>> SOLUTIONS = point24_solutions(3, 2, 8, 8)
        >>> print('\n'.join(SOLUTIONS) if SOLUTIONS else '无解')
        (8 + 8) * 3 / 2 = 24
        (8 - 3 - 2) * 8 = 24
        (8 - 2 - 3) * 8 = 24
    """

    # 检测取值范围（1到13）
    if not all(1 <= n <= 13 for n in (point1, point2, point3, point4)):
        raise ValueError('所有参数必须为1~13')

    solutions = []
    patterns = ('%d + %d + %d + %d', '%d + %d + %d - %d',
                '%d + %d + %d * %d', '%d + (%d + %d) * %d',
                '(%d + %d + %d) * %d', '%d + %d + %d / %d',
                '%d + (%d + %d) / %d', '(%d + %d + %d) / %d',
                '%d + (%d - %d) * %d', '(%d + %d - %d) * %d',
                '%d + %d * %d + %d', '(%d + %d) * %d + %d',
                '(%d + %d) * (%d + %d)', '%d + %d * %d - %d',
                '(%d + %d) * %d - %d', '(%d + %d) * (%d - %d)',
                '%d + %d * %d * %d', '(%d + %d) * %d * %d',
                '(%d + %d * %d) * %d', '%d + %d * %d / %d',
                '(%d + %d) * %d / %d', '(%d + %d * %d) / %d',
                '%d + %d / %d + %d', '(%d + %d) / %d + %d',
                '(%d + %d / %d) * %d', '(%d - %d - %d) * %d',
                '(%d - %d) * %d - %d', '(%d - %d) * (%d - %d)',
                '(%d - %d) * %d * %d', '(%d - %d * %d) * %d',
                '(%d - %d) * %d / %d', '(%d - %d / %d) * %d',
                '%d * %d + %d * %d', '%d * %d + %d / %d',
                '%d * %d - %d - %d', '%d * %d - %d * %d',
                '%d * %d - %d * %d', '%d * %d - %d / %d',
                '(%d * %d - %d) / %d', '%d * %d * %d - %d',
                '%d * %d * %d * %d', '%d * %d * %d / %d',
                '%d * %d / (%d + %d)', '%d * %d / %d - %d',
                '%d * %d / (%d - %d)', '%d * (%d / %d - %d)',
                '%d * %d / %d / %d', '(%d / %d - %d) * %d',
                '%d / (%d - %d / %d)', '%d / (%d / %d - %d)',
                '%d + %d - %d - %d', '%d + %d - %d * %d',
                '%d + %d - %d / %d', '%d + (%d - %d) / %d',
                '(%d + %d - %d) / %d', '%d + %d / (%d + %d)',
                '(%d + %d) / (%d + %d)', '%d + %d / %d - %d',
                '(%d + %d) / %d - %d', '%d + %d / (%d - %d)',
                '(%d + %d) / (%d - %d)', '%d + %d / %d / %d',
                '(%d + %d) / %d / %d', '(%d + %d / %d) / %d',
                '%d - %d + %d / %d', '%d / %d + %d / %d')

    # 穷举 66 * 4! = 1584 种组合
    for exp in (pattern % numbers
                for pattern in patterns
                for numbers in set(permutations((point1, point2, point3, point4)))):
        try:
            if abs(eval(exp) - 24) < 0.0001:    # 排除浮点运算误差
                solutions.append(f'{exp} = 24')
        except ZeroDivisionError:
            pass  # 防止被零除

    return set(solutions)  # 去除重复项
