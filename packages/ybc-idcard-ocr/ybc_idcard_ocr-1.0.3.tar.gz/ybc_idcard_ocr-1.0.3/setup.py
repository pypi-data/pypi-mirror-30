from distutils.core import setup
setup(
  name = 'ybc_idcard_ocr',
  packages = ['ybc_idcard_ocr'],
  version = '1.0.3',
  description = 'Recognize ID Card By Ocr',
  long_description='Recognize ID Card By Ocr',
  author = 'KingHS',
  author_email = '382771946@qq.com',
  keywords = ['pip3', 'python3','python','ID Card'],
  license='MIT',
  install_requires=['requests','opencv-python','pillow']
)
