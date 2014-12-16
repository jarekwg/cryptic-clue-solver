__author__ = 'Jarek Glowacki'

"""
A setup.py file for cx_freeze
Run it from cmd with the command: "py setup.py build"
"""

from cx_Freeze import setup, Executable

setup(  name = 'CCS',
        version = '1.0',
        description = "A cutting edge cryptic clue solver.",
        options = {'build_exe': {'excludes':['tkinter']}},
        executables = [Executable('CCS.py', icon='GUI/CCS.ico', base='Win32GUI')])