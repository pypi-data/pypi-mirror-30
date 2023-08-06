
import sys
import qtpy


def get_system_info(pretty_print=False):
    import platform
    system = {}
    for key in ['architecture', 'machine', 'platform', 'processor',
                'system']:
        system[key] = getattr(platform, key)()

    # platform specific stuff
    for key in ['win32_ver', 'mac_ver', 'linux_distribution']:
        res = getattr(platform, key)()
        if res[0]:
            system[key] = res
    if sys.maxsize > 2**32:
        system['architecture_size'] = '64 bits'
    else:
        system['architecture_size'] = '32 bits'

    python = {}
    for key in ['python_implementation', 'python_version', 'python_compiler']:
        python[key] = getattr(platform, key)()

    sv = {}
    for package_name in ['numpy', 'scipy', 'pandas',
                         'matplotlib', 'qtpy', 'SiQt']:
        try:
            package = __import__(package_name)
            sv[package_name] = package.__version__
        except ImportError:
            sv[package_name] = 'Not installed'
    try:
        sv['QT_API'] = qtpy.API
    except:  # noqa
        sv['QT_API'] = 'Undetermined'

    try:
        if qtpy.API.startswith('pyside'):
            qtpy_backend = __import__(qtpy.API_NAME)
            sv[qtpy.API_NAME] = qtpy_backend.__version__
    except:  # noqa
        raise

    if not pretty_print:
        return {'system': system, 'python': python, 'software_versions': sv}
    else:
        FMT = '   {:12}: {}'
        s = []
        for label, mdict in [('System information', system),
                             ('Python version', python),
                             ('Included modules', sv)]:
            s += ['', label, '='*30, '']
            for key, val in mdict.items():
                if type(val) is tuple:
                    val = ' '.join(val)
                s.append(FMT.format(key, val))
        s.append('')

        return '\n'.join(s)
