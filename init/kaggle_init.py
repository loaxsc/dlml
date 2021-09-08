#!/bin/python

import shutil
import os

from IPython.core.magic import (register_line_magic, register_cell_magic,
                                register_line_cell_magic)
from ipywidgets import interact, interact_manual
from IPython.display import Image, Javascript, display
from ipython_exit import exit
import ipywidgets as widgets


ipy = get_ipython()
# get_ipython().run_line_magic('rehashx', '')

get_ipython().run_line_magic('alias', 'la ls -AF --color')

with open('/kaggle/dlml/init/.shrc','r') as f:
    sh_rc = f.read()

def exec_bash(code):         # %%bash 的輸出沒有顏色
    with open('/dev/shm/xxx___', 'w') as f:
        f.write('shopt -s expand_aliases\n%s' % sh_rc + code)
    get_ipython().system('source /dev/shm/xxx___')

def exec_sh(code):         # %%bash 的輸出沒有顏色
    with open('/dev/shm/xxx___', 'w') as f:
        f.write(sh_rc + code)
    get_ipython().system('sh /dev/shm/xxx___')

def new_sh(sh_code, sh_name, is_overwrite=False):
    file_path = '/kaggle/bin/%s' % sh_name
    if not os.path.exists(file_path) or (os.path.exists(file_path) and is_overwrite):
        with open(file_path, 'w') as f:
            f.write(sh_code)
        os.chmod(file_path, 0o700)
    else:
        print('file exists !\nset overwrite = 1')

from IPython.display import FileLink
def get_file_link(path):
    filename = path.split('/')[-1]
    abspath = os.path.abspath(path)
    if 'working' not in os.path.abspath(abspath):
        print('copy to /kaggle/working/%s' % filename)
        shutil.copy(abspath, '/kaggle/working') # 無法用 symlink，已測試過
        display(FileLink(filename))
        cell = '%%update_file_from_ghdrive %s' % abspath
    else:
        display(FileLink(path))
        cell = '%%update_file_from_ghdrive %s' % path
    get_ipython().set_next_input(cell,False)

sh_code_update_file_from_ghdrive = """
echo 'Download {filename}'
wget -q https://github.com/loaxsc/ghdrive/raw/main/{filename} -O {path}
echo '{path} is updated !'
"""
@register_line_magic
def update_file_from_ghdrive(line):
    filename = line.split('/')[-1]
    exec_sh(sh_code_update_file_from_ghdrive.format(filename=filename, path=line))

# %loadfile
js_code_loadfile="""\
if ( typeof content_changed == 'undefined' ) {
     widnow.content_changed = (e) => {
        var cell = e.target.parentElement.parentElement;
        if ( !cell.className.includes('changed') ) {
            cell.className += ' changed ';
        }
        //console.info('change');
    }
}

// ta: textArea
var ta = document.querySelector('div.jp-mod-active textarea');
if ( ! ta.className.includes('hacked') ) {
    ta.className = 'hacked';
    ta.addEventListener('change',content_changed);
}"""
@register_line_cell_magic
def loadfile(line, cell=None):
    ipy = get_ipython()
    if os.path.exists(line):
        with open(line, 'r') as f:
            ipy.set_next_input('%%writefile_ {}\n{}'.format(os.path.abspath(line), f.read().rstrip())
                               , True)
    display(Javascript(js_code_loadfile))
del loadfile

js_code_writefile_="""
var cell = document.querySelector('div.jp-mod-active textarea').parentElement.parentElement;
cell.className = cell.className.replaceAll(' changed','');"""
@register_cell_magic
def writefile_(line, cell):
    if os.path.exists(line):
        ipy = get_ipython()
        with open(line, 'w') as f:
            f.write(cell)
            print('write file: %s' % line)
        display(Javascript(js_code_writefile_))
del writefile_

@register_cell_magic
def bash_(line, cell):
    exec_bash(cell)
del bash_

@register_cell_magic
def sh_(line, cell):
    exec_sh(cell)
del sh_

items = ['/kaggle']
for root, dirs, files in os.walk('/kaggle'):
    for dir in dirs:
        item = os.path.join(root, dir)
        if '/.git' not in item:
            items.append(item)
items.sort()
w_ls_wkdir = widgets.Combobox(
    placeholder = 'working dir',
    options=items,
    description='ls dir',
    ensure_option=True,
    disable=False
)
w_ch_wkdir = widgets.Combobox(
    placeholder = 'working dir',
    options=items,
    description='PWD',
    ensure_option=True,
    disable=False
)
def ls_dir(wkdir):
    if wkdir:
        get_ipython().system('ls -a --color %s' % wkdir)
def ch_dir(wkdir):
    if wkdir:
        get_ipython().run_line_magic('cd',wkdir)

out_ch_dir = widgets.interactive_output(ch_dir,{'wkdir': w_ch_wkdir})
out_ls_dir = widgets.VBox([w_ch_wkdir, w_ls_wkdir, widgets.interactive_output(ls_dir, {'wkdir': w_ls_wkdir})])

# get_ipython().run_line_magic('run', '-i /kaggle/dlml/init/line_magic_cd')
# show working dir
if 'org_os_chdir' not in globals():
    org_os_chdir = os.chdir

js_code_chdir = """\
if (document.querySelector('#heading') == null) {{
    var dive = document.createElement('div');
    dive.id = 'heading';
    var pe = document.createElement('p');
    pe.id = 'cwd';
    pe.innerText = 'something'
    dive.appendChild(pe);
    var content = document.querySelector('#main').firstElementChild;
    document.querySelector('#main').insertBefore(dive, content);
}}

document.querySelector('#cwd').innerText = '{}';\
"""

def ch_dir(path):
    if os.path.exists(path):
        ret = org_os_chdir(path)
        _ = display(Javascript(js_code_chdir.format(path)))
    else:
        print('%s not exists' % path)
        exit()
os.chdir = ch_dir
os.chdir(os.getcwd())
