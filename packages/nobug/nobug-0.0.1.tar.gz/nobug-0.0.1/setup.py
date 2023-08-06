from setuptools import setup

try:
    unicode
    def u8(s):
        return s.decode('unicode-escape').encode('utf-8')
except NameError:
    def u8(s):
        return s.encode('utf-8')

setup(name='nobug',
      version='0.0.1',
      description=u8('nobug nobug nobug'),
      packages=['nobug'],
      )

