import ipywidgets as widgets
from traitlets import Unicode
import json
from . import clustergrammer
Network = clustergrammer.Network

# version 0.2.0

print('example.py \n---------------------')
# print(Network)

@widgets.register
class clustergrammer_widget2(widgets.DOMWidget):
    """An example widget."""
    _view_name = Unicode('HelloView').tag(sync=True)
    _model_name = Unicode('HelloModel').tag(sync=True)

    _view_module = Unicode('clustergrammer_widget2').tag(sync=True)
    _model_module = Unicode('clustergrammer_widget2').tag(sync=True)

    _view_module_version = Unicode('^0.3.0').tag(sync=True)
    _model_module_version = Unicode('^0.3.0').tag(sync=True)

    value = Unicode('Hello World!').tag(sync=True)

    network = Unicode('').tag(sync=True)
