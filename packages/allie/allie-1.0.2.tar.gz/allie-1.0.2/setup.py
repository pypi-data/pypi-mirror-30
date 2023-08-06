from setuptools import setup


setup(name='allie',
      version='1.0.2',
      description='Biblioteca de inteligência artificial',
      url='https://youtube.com/tdcprojetos',
      author='Klinsman Jorge',
      author_email='tdcprojetos@hotmail.com',
      license='MIT',
      packages=['allie'],
      zip_safe=False,
      classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
      install_requires=['wikipedia', 'requests', 'boto3', 'python-vlc', 'chatterbot',
                        'pyserial', 'speechrecognition','google_speech'],

      data_files=[('Lib/site-packages/allie',['allie/ALLIE_Falas_Offline/ALLIE sond.mp3', 'allie/ALLIE_Falas_Offline/ALLIEConexaoOk.mp3',
                             'allie/ALLIE_Falas_Offline/ALLIERead.mp3', 'allie/ALLIE_Falas_Offline/ALLIErrorConect.mp3',
                             'allie/ALLIE_Falas_Offline/Problema de rede.mp3', 'allie/ALLIEToken/ArduinoToken.txt', 'allie/conversas/I.A dialog.txt',
                             'allie/conversas/origens.txt', 'allie/conversas/I.A dialog.txt', 'allie/conversas/I.A dialog.txt'])]
      )

