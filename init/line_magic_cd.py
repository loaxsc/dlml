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

# def ch_dir(path):
    # if os.path.exists(path):
        # ret = org_os_chdir(path)
        # _ = display(Javascript(js_code_chdir.format(path)))
    # else:
        # print('%s not exists' % path)
        # exit()
# os.chdir = ch_dir
# os.chdir(os.getcwd())

@register_line_magic
def cd(line):
    try:
        oldcwd = os.getcwd()
    except FileNotFoundError:
        # Happens if the CWD has been deleted.
        oldcwd = None

    numcd = re.match(r'(-)(\d+)$',parameter_s)
    # jump in directory history by number
    if numcd:
        nn = int(numcd.group(2))
        try:
            ps = self.shell.user_ns['_dh'][nn]
        except IndexError:
            print('The requested directory does not exist in history.')
            return
        else:
            opts = {}
    elif parameter_s.startswith('--'):
        ps = None
        fallback = None
        pat = parameter_s[2:]
        dh = self.shell.user_ns['_dh']
        # first search only by basename (last component)
        for ent in reversed(dh):
            if pat in os.path.basename(ent) and os.path.isdir(ent):
                ps = ent
                break

            if fallback is None and pat in ent and os.path.isdir(ent):
                fallback = ent

        # if we have no last part match, pick the first full path match
        if ps is None:
            ps = fallback

        if ps is None:
            print("No matching entry in directory history")
            return
        else:
            opts = {}


    else:
        opts, ps = self.parse_options(parameter_s, 'qb', mode='string')
    # jump to previous
    if ps == '-':
        try:
            ps = self.shell.user_ns['_dh'][-2]
        except IndexError:
            raise UsageError('%cd -: No previous directory to change to.')
    # jump to bookmark if needed
    else:
        if not os.path.isdir(ps) or 'b' in opts:
            bkms = self.shell.db.get('bookmarks', {})

            if ps in bkms:
                target = bkms[ps]
                print('(bookmark:%s) -> %s' % (ps, target))
                ps = target
            else:
                if 'b' in opts:
                    raise UsageError("Bookmark '%s' not found.  "
                          "Use '%%bookmark -l' to see your bookmarks." % ps)

    # at this point ps should point to the target dir
    if ps:
        try:
            os.chdir(os.path.expanduser(ps))
            if hasattr(self.shell, 'term_title') and self.shell.term_title:
                set_term_title(self.shell.term_title_format.format(cwd=abbrev_cwd()))
        except OSError:
            print(sys.exc_info()[1])
        else:
            cwd = os.getcwd()
            dhist = self.shell.user_ns['_dh']
            if oldcwd != cwd:
                dhist.append(cwd)
                self.shell.db['dhist'] = compress_dhist(dhist)[-100:]

    else:
        os.chdir(self.shell.home_dir)
        if hasattr(self.shell, 'term_title') and self.shell.term_title:
            set_term_title(self.shell.term_title_format.format(cwd="~"))
        cwd = os.getcwd()
        dhist = self.shell.user_ns['_dh']

        if oldcwd != cwd:
            dhist.append(cwd)
            self.shell.db['dhist'] = compress_dhist(dhist)[-100:]
    if not 'q' in opts and not self.cd_force_quiet and self.shell.user_ns['_dh']:
        print(self.shell.user_ns['_dh'][-1])
del cd
