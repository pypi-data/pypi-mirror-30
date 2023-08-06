from .pmesh import PMesh
from .version import __version__


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'topos-previewjs',
        'require': 'topos-previewjs/extension'
    }]
