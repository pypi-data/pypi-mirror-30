import ipywidgets as widgets
from traitlets import Unicode, List

from .version import __version__


@widgets.register
class HelloWidget(widgets.DOMWidget):

    _view_name = Unicode("HelloView").tag(sync=True)
    _view_module = Unicode("topos-previewjs").tag(sync=True)
    _view_module_version = Unicode(__version__).tag(sync=True)

    value = Unicode("Hello, World!").tag(sync=True)


@widgets.register
class ModelWidget(widgets.DOMWidget):

    _view_name = Unicode("ModelView").tag(sync=True)
    _view_module = Unicode("topos-previewjs").tag(sync=True)
    _view_module_version = Unicode(__version__).tag(sync=True)

    vertices = List([[1., 2., 3.], [4., 5., 6.]]).tag(sync=True)
    faces = List([[1, 2, 3, 4], [5, 6, 7, 8]]).tag(sync=True)
