from distutils.core import setup
import sys

MAINSCRIPT = 'legender.py'
DATA_FILES = []
OPTIONS = {}

extra_options = None
if sys.platform == 'darwin':
    import py2app
    sys.argv.append('py2app')
    OPTIONS.update({'argv_emulation': 1,
                    "no_chdir":1,
                    "includes":"queue"})
    extra_options = dict(
        setup_requires=['py2app'],
        data_files=DATA_FILES,
        app=[MAINSCRIPT],
        # Cross-platform applications generally expect sys.argv to
        # be used for opening files.
        options={'py2app': OPTIONS}
    )
elif sys.platform == 'win32':
    import py2exe
    sys.argv.append('py2exe')
    OPTIONS.update({'bundle_files': 1})
    extra_options = dict(
        options={'py2exe': OPTIONS},
        console=[{'script': MAINSCRIPT}],
    )
else:
    extra_options = dict(
        # Normally unix-like platforms will use "setup.py install"
        # and install the main script as such
        scripts=[MAINSCRIPT],
    )

setup(
    **extra_options
)
