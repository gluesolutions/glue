import os
import numpy as np

from qtpy import QtWidgets
from glue.core.state_objects import State
from echo import CallbackProperty, SelectionCallbackProperty
from glue.utils.qt import load_ui
from glue.core.data_combo_helper import DataCollectionComboHelper, ManualDataComboHelper, ComponentIDComboHelper
from echo.qt import autoconnect_callbacks_to_qt
from scipy import interpolate
from glue.core.component_link import ComponentLink

__all__ = ['InterpolateOnto3DDialog']


class InterpolateOnto3DState(State):

    data = SelectionCallbackProperty()
    geneposition_att = SelectionCallbackProperty(default_index=5)
    x_att = SelectionCallbackProperty(default_index=1)
    y_att = SelectionCallbackProperty(default_index=2)
    z_att = SelectionCallbackProperty(default_index=3)

    def __init__(self, data_collection, table_data):

        super(InterpolateOnto3DState, self).__init__()

        self.table_data = table_data
        self.data_helper = ManualDataComboHelper(self, 'data', data_collection)
        self.data_collection = data_collection
        matching_data = []
        for data in data_collection:
            try:
                tck = data.meta['interp_function']
                matching_data.append(data)
            except (KeyError, AttributeError):
                pass
        self.data_helper.set_multiple_data(matching_data)
        self.geneposition_helper = ComponentIDComboHelper(self, 'geneposition_att')
        self.x_helper = ComponentIDComboHelper(self, 'x_att')
        self.y_helper = ComponentIDComboHelper(self, 'y_att')
        self.z_helper = ComponentIDComboHelper(self, 'z_att')

        self.add_callback('data', self._on_data_change)
        self._on_data_change()

    def _on_data_change(self, *args, **kwargs):
        self.x_helper.append_data(None if self.data is None else self.data)
        self.y_helper.append_data(None if self.data is None else self.data)
        self.z_helper.append_data(None if self.data is None else self.data)
        self.geneposition_helper.append_data(None if self.table_data is None else self.table_data)

        #self.att_helper.set_multiple_data([] if self.data is None else [self.data])


class InterpolateOnto3DDialog(QtWidgets.QDialog):
    """
    Create a new dialog for interpolating onto a 3D dataset

    Parameters
    ----------
    collect : :class:`~glue.core.data_collection.DataCollection`
        The data collection to use
    default : :class:`~glue.core.data.Data`, optional
        The default dataset in the collection (optional)
    """

    def __init__(self, collect, defaultx=None, defaulty=None, defaultz=None, table_data=None, parent=None):

        super(InterpolateOnto3DDialog, self).__init__(parent=parent)

        self.state = InterpolateOnto3DState(collect, table_data)

        self.ui = load_ui('interpolate_onto_3d.ui', self,
                          directory=os.path.dirname(__file__))
        self._connections = autoconnect_callbacks_to_qt(self.state, self.ui)

        self._collect = collect

        #if default is not None:
        #    self.state.data = default

        self.ui.button_ok.clicked.connect(self.accept)
        self.ui.button_cancel.clicked.connect(self.reject)
        #self.accepted.connect(self.update_fitter_from_settings)

    def _apply(self):

        print("I made it into _apply")
        try:
            tck = self.state.data.meta['interp_function']
        except KeyError:
            print("Interpolating Function not found!")
        table_data = self.state.table_data

        #We should really check that the table data does not 
        #already have an x,y,z before just overwriting them
        x,y,z = interpolate.splev(table_data[self.state.geneposition_att].astype('float'),tck)
        table_data.add_component(x,'x')
        table_data.add_component(y,'y')
        table_data.add_component(z,'z')
        link = ComponentLink([self.state.data.id[self.state.x_att]],table_data.id['x'])
        self.state.data_collection.add_link(link)
        link = ComponentLink([self.state.data.id[self.state.y_att]],table_data.id['y'])
        self.state.data_collection.add_link(link)
        link = ComponentLink([self.state.data.id[self.state.z_att]],table_data.id['z'])
        self.state.data_collection.add_link(link)


    @classmethod
    def interpolate(cls, collect, defaultx=None, defaulty=None, defaultz=None, table_data=None, parent=None):
        """
        Class method to create data interpolated onto a 3D model.
    
        The arguments are the same as __init__.
        """
        self = cls(collect, parent=parent, defaultx=defaultx, defaulty=defaulty, defaultz=defaultz, table_data=table_data)
        value = self.exec_()
    
        if value == QtWidgets.QDialog.Accepted:
            self._apply()

