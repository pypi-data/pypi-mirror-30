# -*- coding: utf-8 -*-
"""zhao.formulas

This module implements common formulas.
"""

from zhao.xin_constants import G


def celsius_to_fahrenheit(celsius_degrees):
    """摄氏度转华氏度
    """
    return celsius_degrees * 1.8 + 32.0


def celsius_to_kelvin(celsius_degrees):
    """摄氏度转开氏度
    """
    return celsius_degrees + 273.15


def fahrenheit_to_celsius(fahrenheit_degrees):
    """华氏度转摄氏度
    """
    return (fahrenheit_degrees - 32.0) / 1.8


def fahrenheit_to_kelvin(fahrenheit_degrees):
    """华氏度转开氏度
    """
    return (fahrenheit_degrees + 459.67) / 1.8


def kelvin_to_celsius(kelvin):
    """开氏度转摄氏度
    """
    return kelvin - 273.15


def kelvin_to_fahrenheit(kelvin):
    """开氏度转华氏度
    """
    return kelvin * 1.8 - 459.67


def kinetic_energy(mass, velocity):
    """计算动能
    """
    return 0.5 * mass * velocity ** 2


def gravitation_force(mass1, mass2, distance):
    """万有引力公式
    """
    return G * mass1 * mass2 / distance / distance


def centripetal_force(mass, velocity, radius):
    """向心力公式
    """
    return mass * velocity**2 / radius
