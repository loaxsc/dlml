import shutil
import sys
import os

![ -e '/kaggle/sys_clear' ] && source '/kaggle/sys_clear'
if '/kaggle/bin' not in os.environ['PATH']:
    os.environ['PATH'] += ':/kaggle/bin'
if '/kaggle/dlml/lib' not in sys.path: # list 的話兩者必須 exactly match
    sys.path.append('/kaggle/dlml/lib')

!cd /kaggle && git clone https://github.com/loaxsc/dlml.git && source /kaggle/dlml/init/kaggle_sh_init
%run -i /kaggle/dlml/init/kaggle_init    # %run 可以不加 .py 後綴； Pure python code

print('execute %rehashx')
os.chdir = org_os_chdir
%rehashx
os.chdir = ch_dir
