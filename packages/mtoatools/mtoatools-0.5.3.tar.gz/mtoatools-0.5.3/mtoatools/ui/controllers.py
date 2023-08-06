import os
from functools import partial
from collections import defaultdict
from contextlib import contextmanager
from Qt import QtWidgets, QtCore
import pymel.core as pmc
from maya import OpenMaya
from .dialogs import (MatteDialog, MatteWidget, ObjectWidget, ObjectItem,
                      MatteSaveDialog, MatteLoadDialog)
from .utils import get_maya_window
from ..packages import yaml
from ..models import MatteAOV
from ..api import save_mattes


_MAYA_MADE_SELECTION_ = False
_UI_MADE_SELECTION_ = False


@contextmanager
def maya_made_selection():
    global _MAYA_MADE_SELECTION_
    _MAYA_MADE_SELECTION_ = True

    try:
        yield
    finally:
        _MAYA_MADE_SELECTION_ = False


@contextmanager
def ui_made_selection():
    global _UI_MADE_SELECTION_
    _UI_MADE_SELECTION_ = True

    try:
        yield
    finally:
        _UI_MADE_SELECTION_ = False


class MayaHooks(QtCore.QObject):
    '''Manage all Maya Message Callbacks (Hooks)'''

    before_scene_changed = QtCore.Signal()
    scene_changed = QtCore.Signal()
    scene_selection_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(MayaHooks, self).__init__(parent=parent)

        self.callback_ids = defaultdict(list)
        change_messages = [
            OpenMaya.MSceneMessage.kAfterOpen,
            OpenMaya.MSceneMessage.kAfterNew,
            OpenMaya.MSceneMessage.kAfterImport,
            OpenMaya.MSceneMessage.kAfterRemoveReference,
            OpenMaya.MSceneMessage.kAfterCreateReference,
        ]
        for msg in change_messages:
            OpenMaya.MSceneMessage.addCallback(
                msg,
                self.emit_scene_changed
            )
        before_change_messages = [
            OpenMaya.MSceneMessage.kBeforeOpen,
            OpenMaya.MSceneMessage.kBeforeNew,
            OpenMaya.MSceneMessage.kBeforeRemoveReference,
        ]
        for msg in before_change_messages:
            OpenMaya.MSceneMessage.addCallback(
                msg,
                self.emit_before_scene_changed
            )

        OpenMaya.MEventMessage.addEventCallback(
            'SelectionChanged',
            self.emit_scene_selection_changed
        )

    def emit_before_scene_changed(self, *args):
        self.before_scene_changed.emit()

    def emit_scene_changed(self, *args):
        self.scene_changed.emit()

    def emit_scene_selection_changed(self, *args):
        self.scene_selection_changed.emit()

    def add_attribute_changed_callback(self, node, attr, callback):
        mobject = node.__apimobject__()
        mplug = node.attr(attr).__apimplug__()

        def maya_callback(msg, plug, other_plug, data):
            if plug == mplug:
                if msg & OpenMaya.MNodeMessage.kAttributeSet:
                    callback()

        callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
            mobject,
            maya_callback,
        )
        self.callback_ids[node].append(callback_id)

    def add_about_to_delete_callback(self, node, callback):
        mobject = node.__apimobject__()

        def maya_callback(depend_node, dg_modifier, data):
            callback_ids = self.callback_ids.pop(node, None)
            if callback_ids:
                for callback_id in callback_ids:
                    OpenMaya.MMessage.removeCallback(callback_id)
            callback()

        callback_id = OpenMaya.MNodeMessage.addNodeAboutToDeleteCallback(
            mobject,
            maya_callback,
        )
        self.callback_ids[node].append(callback_id)

    def clear_callbacks(self):
        for node, callback_ids in self.callback_ids.items():
            for callback_id in callback_ids:
                OpenMaya.MMessage.removeCallback(callback_id)
        self.callback_ids = defaultdict(list)


class MattesController(MatteDialog):

    def __init__(self, parent=get_maya_window()):
        super(MattesController, self).__init__(parent=parent)

        load_action = QtWidgets.QAction('&Load', self)
        load_action.triggered.connect(self.load)
        save_action = QtWidgets.QAction('&Save', self)
        save_action.triggered.connect(self.save)
        self.file_menu.addAction(load_action)
        self.file_menu.addAction(save_action)

        self.matte_list.itemSelectionChanged.connect(self.matte_list_select)
        self.obj_list.itemSelectionChanged.connect(self.obj_list_select)
        self.button_new.clicked.connect(self.new_clicked)
        self.button_refresh.clicked.connect(self.refresh_matte_list)
        self.button_help.clicked.connect(self.show_help)
        self.button_add.clicked.connect(self.add_clicked)
        self.button_red.clicked.connect(self.color_clicked(1, 0, 0))
        self.button_green.clicked.connect(self.color_clicked(0, 1, 0))
        self.button_blue.clicked.connect(self.color_clicked(0, 0, 1))
        self.button_white.clicked.connect(self.color_clicked(1, 1, 1))
        self.button_black.clicked.connect(self.color_clicked(0, 0, 0))

        self.maya_hooks = MayaHooks(parent=self)
        self.maya_hooks.before_scene_changed.connect(self.clear_lists)
        self.maya_hooks.scene_changed.connect(self.refresh_matte_list)
        self.maya_hooks.scene_selection_changed.connect(self.scene_sel_changed)

        self.refresh_matte_list()

    def set_aov(self, aov):
        self.aov = aov
        self.refresh_obj_list()

    def scene_sel_changed(self):
        count = self.obj_list.count()
        if count == 0:
            return

        with maya_made_selection():
            selection = pmc.ls(sl=True)
            for i in xrange(count):
                item = self.obj_list.item(i)
                conditions = [
                    item.pynode in selection,
                    item.pynode.getParent() in selection
                ]
                if any(conditions):
                    item.setSelected(True)
                else:
                    item.setSelected(False)

    def selected_nodes(self):
        pre_select = self.obj_list.selectedItems()
        if pre_select:
            nodes = [item.pynode for item in pre_select]
        else:
            nodes = []

        return nodes

    def color_clicked(self, *color):
        def on_click():
            items = self.obj_list.selectedItems()
            if not items:
                return

            nodes = [item.pynode for item in items]
            self.aov.set_objects_color(color, *nodes)
            for item in items:
                item.refresh_color()
            self.obj_list.sortItems()

        return on_click

    def add_clicked(self):
        if not self.aov:
            return

        nodes = pmc.ls(sl=True, transforms=True)
        color = (1, 1, 1)
        added_nodes = self.aov.add(*nodes)
        for node in added_nodes:
            node.attr(self.aov.mesh_attr_name).set(*color)
            self.new_obj_item(node, color)
        self.obj_list.sortItems()

    def new_clicked(self):
        name = self.matte_line.text()
        if not name:
            self.matte_line.setFocus()
            return

        aov = MatteAOV.create(name)
        self.new_matte_item(aov)

    def new_matte_item(self, aov):
        item = QtWidgets.QListWidgetItem()
        item.pynode = aov

        widget = MatteWidget(aov.name)

        del_callback = partial(self.delete_matte_item, item, aov)
        widget.del_button.clicked.connect(del_callback)

        ren_callback = partial(self.rename_matte_item, item, aov)
        widget.edited.connect(ren_callback)

        item.setSizeHint(widget.sizeHint())
        self.matte_list.addItem(item)
        self.matte_list.setItemWidget(item, widget)

    def rename_matte_item(self, item, aov, new_name):
        aov.rename(new_name)

    def delete_matte_item(self, item, aov):
        self.matte_list.takeItem(self.matte_list.indexFromItem(item).row())
        aov.delete()
        if aov == self.aov:
            self.aov = None
            self.obj_list.clear()

    def refresh_item_color(self, item):
        item.refresh_color()
        self.obj_list.sortItems()

    def delete_obj_item(self, item):
        try:
            self.obj_list.takeItem(self.obj_list.indexFromItem(item).row())
            self.aov.discard(item.pynode)
        except RuntimeError as e:
            if "Internal C++ object (ObjectItem) already deleted" in str(e):
                pass
            raise

    def new_obj_item(self, node, color):

        widget = ObjectWidget(str(node))
        widget.set_color(*color)

        item = ObjectItem(self.aov, node, widget)
        item.setSizeHint(widget.sizeHint())

        self.obj_list.addItem(item)
        self.obj_list.setItemWidget(item, widget)

        # Add attr changed callbacks
        attr_callback = partial(self.refresh_item_color, item)
        self.maya_hooks.add_attribute_changed_callback(
            node,
            self.aov.mesh_attr_name,
            attr_callback
        )

        # Add delete callbacks
        del_callback = partial(self.delete_obj_item, item)
        widget.del_button.clicked.connect(del_callback)
        self.maya_hooks.add_about_to_delete_callback(node, del_callback)

    def clear_lists(self):
        self.maya_hooks.clear_callbacks()
        self.matte_list.clear()
        self.obj_list.clear()

    def refresh_matte_list(self):
        self.maya_hooks.clear_callbacks()
        self.matte_list.clear()
        self.obj_list.clear()

        for aov in MatteAOV.ls():
            self.new_matte_item(aov)

    def refresh_obj_list(self):
        self.maya_hooks.clear_callbacks()
        self.obj_list.clear()

        for node, color in self.aov:
            self.new_obj_item(node, color)

    def matte_list_select(self):
        item = self.matte_list.currentItem()
        if not item:
            return
        self.set_aov(item.pynode)

    def obj_list_select(self):

        if _MAYA_MADE_SELECTION_:
            return

        items = self.obj_list.selectedItems()
        if not items:
            return

        nodes = []
        for item in items:
            nodes.append(item.pynode)

        with ui_made_selection():
            pmc.select(nodes, replace=True)

    def save(self):

        dialog = MatteSaveDialog(self)

        for matte in MatteAOV.ls():
            item = QtWidgets.QListWidgetItem(matte.name)
            item.matte = matte
            dialog.matte_list.addItem(item)

        dialog.matte_list.selectAll()

        def on_accepted():
            items = dialog.matte_list.selectedItems()
            if not items:
                return
            mattes = [item.matte for item in items]

            scene = pmc.sceneName()
            mattes_name = os.path.splitext(os.path.basename(scene))[0]
            mattes_dir = os.path.join(os.path.dirname(scene), 'mattes')
            mattes_path = os.path.join(mattes_dir, mattes_name + '.yml')
            if not os.path.exists(mattes_dir):
                os.makedirs(mattes_dir)

            filepath, filters = QtWidgets.QFileDialog.getSaveFileName(
                self,
                'Save Matte AOVS',
                mattes_path,
                'Yaml (*.yml *.yaml)'
            )

            if filepath:
                save_mattes(mattes, filepath)

        dialog.accepted.connect(on_accepted)
        dialog.exec_()

    def load(self):

        scene = pmc.sceneName()
        mattes_dir = os.path.join(os.path.dirname(scene), 'mattes')

        filepath, filters = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Load Matte AOVS',
            mattes_dir,
            'Yaml (*.yml *.yaml)'
        )

        if not filepath:
            return

        with open(filepath, 'r') as f:
            data = yaml.load(f.read())

        dialog = MatteLoadDialog(self)

        for matte_data in data:
            item = QtWidgets.QListWidgetItem(matte_data['name'])
            item.matte_data = matte_data
            dialog.matte_list.addItem(item)

        dialog.matte_list.selectAll()

        def on_accepted():
            items = dialog.matte_list.selectedItems()
            if not items:
                return

            ignore_namespaces = dialog.ignore_namespaces.isChecked()

            data = [item.matte_data for item in items]
            for matte_data in data:
                MatteAOV.load(matte_data, ignore_namespaces)

            self.refresh_matte_list()

        dialog.accepted.connect(on_accepted)
        dialog.exec_()

    def show_help(self):
        import webbrowser
        webbrowser.open('https://mtoatools.readthedocs.org')
