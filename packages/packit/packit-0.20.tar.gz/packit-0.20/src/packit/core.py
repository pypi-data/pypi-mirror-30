from pbr import hooks, pbr_json
from pbr.core import pbr
from pip.commands.install import InstallCommand as PipInstallCommand
from setuptools.command.easy_install import easy_install

from .hooks import setup_hook


def patch_pbr():
    hooks.setup_hook = setup_hook
    # Disabling annoying pbr.json
    pbr_json.write_pbr_json = lambda *a, **k: None


def patch_setuptools(fetch_directives=('index_url', 'find_links')):
    """
    Here we patch easy_install command from setuptools.
    Despite the looks, easy_install is not a function but a class - just navigate to its definition
    if you want to peek into abyss.

    easy_install is a grand-parent of "pip install" and is used to fetch dependencies of the setup script.
    What we do here, we initialize an instance of "pip install" and then just copy some of the options,
    listed in fetch_directives, from "pip install" onto easy_install.
    This is a "smart trick" to make sure that we honor pip config files and don't need to bother with
    easy_install config files
    """

    orig = easy_install.finalize_options

    def patched_finalize_options(self):
        cmd = PipInstallCommand()
        config = cmd.parser.parse_args([])[0]
        for option in fetch_directives:
            try:
                value = getattr(config, option)
            except AttributeError:
                continue
            setattr(self, option, value)
        orig(self)

    easy_install.finalize_options = patched_finalize_options


def patch(config=None):  # used as a setup hook
    patch_pbr()
    patch_setuptools()


def packit(dist, attr, value):
    if not value:
        return

    patch()
    pbr(dist, attr, value)


def _replace_null_with_space(string):
    return string.replace('\00', ' ')


def _fix_data_files(data_files):
    fixed = {}

    for path, files in data_files:
        fixed[_replace_null_with_space(path)] = list(map(_replace_null_with_space, files))

    return fixed.items()
