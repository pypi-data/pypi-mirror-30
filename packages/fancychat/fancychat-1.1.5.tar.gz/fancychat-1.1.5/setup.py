from setuptools import setup

setup(
    name='fancychat',
    version='1.1.5',
    packages=[
        'fancychat'
    ],
    data_files=[
        ('share/fancychat', [
            'share/fancychat/appbar.close.svg',
            'share/fancychat/appbar.control.fastforward.variant.svg',
            'share/fancychat/appbar.lines.horizontal.4.svg',
            'share/fancychat/fbmessenger.svg',
            'share/fancychat/kphotoalbum.svg',
            'share/fancychat/msg-text-arrive.svg',
            'share/fancychat/msg-text-send.svg',
            'share/fancychat/preferences-desktop-emoticons.svg',
            'share/fancychat/preferences-desktop-emoticons2.svg',
            'share/fancychat/styles.css'
        ])
    ],
    url='https://github.com/joseluis8906/fancychat',
    license='MIT',
    author='joseluis',
    author_email='joseluiscacere8906@gmail.com',
    description='fancy chat example',
    scripts=['bin/FancyChat.py'],
    install_requires=[
        'pygobject>=3.26',
        'paho-mqtt>=1.3'
    ]
)
