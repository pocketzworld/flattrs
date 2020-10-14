import sys

version_info = sys.version_info[0:3]
is_py36 = version_info[:2] == (3, 6)
is_py39plus = version_info[:2] >= (3, 9)
