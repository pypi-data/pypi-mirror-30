# -*- coding: utf-8
#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Schematic Editor API module.
"""
from __future__ import unicode_literals, print_function

import os

# check is embedded script mode active
# import typhoon.settings.api_settings as apiSettings
from typhoon.api.schematic_editor.base import SchematicAPIBase
from typhoon.api.schematic_editor.const import ITEM_ANY, WARNING_GENERAL, \
    ERROR_GENERAL, FQN_SEP, ROTATION_UP, KIND_PE, SP_TYPE_REAL, DIRECTION_OUT, \
    TAG_SCOPE_GLOBAL, GRID_RESOLUTION, ICON_ROTATE, ICON_TEXT_LIKE
from typhoon.api.schematic_editor.stub import clstub
from typhoon.api.schematic_editor.util import ItemHandle


class NotSupportedModule(Exception):
    # custom exception
    pass


__all__ = ["model"]


def determine_path(path):
    """
    Map relative filesystem path into absolute, if path is given in absolute path
    return it unchanged

    Arguments:
        * path - filesystem path

    Returns:
        absolute filesystem path
    """
    if os.path.isabs(path):
        return path
    else:
        (directory, filename) = os.path.split(os.path.abspath(os.path.realpath(path)))
        return os.path.join(directory, filename)


class SchematicAPI(SchematicAPIBase):
    """
    Class models schematic model and provide methods to manipulate schematic
    model.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize schematic model instance.

        Arguments:
            None
        """
        super(SchematicAPI, self).__init__(*args, **kwargs)

        # Indicator if messages are written to standard error
        self.debug = True

        # Flag used to tell if compiling should be aborted
        self.abort_compiling = False

    def print_message(self, message):
        """
        Prints provided message if debug mode is activated.

        Args:
            message (str): Message to print.

        Returns:
            None
        """
        if self.debug:
            print(message)

    def create_new_model(self, name=None):
        """
        Creates new model.

        Args:
            name(str): Optional model name, if not specified it will be
                automatically generated.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/create_model_close.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_model_close.example
        """
        return clstub().create_new_model(name=name)

    def close_model(self):
        """
        Closes model.

        Args:
            None

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/create_model_close.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_model_close.example
        """
        return clstub().close_model()

    def load(self, filename, debug=True):
        """
        Loads model from file.

        Args:
            filename (str): Filename in which model is located.
            debug (bool): Indicate to print messages or not.

        Returns:
            ``True`` if load was successful, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/load.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/load.example
        """
        return clstub().load(filename=determine_path(filename), debug=debug)

    def save(self):
        """
        Save a loaded model into same file from which it is loaded.

        Args:
            None

        Returns:
            ``True`` if model is saved successfully, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/save_save_as.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/save_save_as.example
        """
        return clstub().save()

    def save_as(self, filename):
        """
        Save schematic model under different name.

        Args:
            filename (str): Save schematic model using filename as new file
                name.

        Returns:
            ``True`` if model is saved or ``False`` if some error occurs.

        **Example:**

        .. literalinclude:: sch_api_examples/save_save_as.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/save_save_as.example
        """
        return clstub().save_as(filename=determine_path(filename))

    def _handle_error_message(self, code, context, msg):
        self.abort_compiling = True

    def compile(self):
        """
        Compile schematic model.

        Args:
            None

        Returns:
            ``True`` if compilation was successful, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/compile.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/compile.example
        """
        return clstub().compile()

    def set_hw_settings(self, product, revision, conf_id):
        """
        .. deprecated:: 2.0
        Use ``set_model_property_value`` instead.

        Sets new hardware settings.

        Args:
            product (str): Product name (HIL 400, HIL 600 and so on).
            revision (str): Product revision (1, 2, ...).
            conf_id (str): Configuration id.

        Returns:
            ``True`` if operation was successful, ``False`` otherwise.
        """
        return clstub().set_hw_settings(product=product, revision=revision,
                                        conf_id=conf_id)

    def detect_hw_settings(self):
        """
         Detect and set hardware settings by querying hardware device.

         Args:
             None

         Returns:
             tuple (hw_product_name, hw_revision, configuration_id) or
             ``False`` if auto-detection failed.

        **Example:**

        .. literalinclude:: sch_api_examples/detect_hw_settings.example
           :language: python
           :lines: 2-

        """
        return clstub().detect_hw_settings()

    def get_hw_settings(self):
        """
        Get hardware settings from device without changing model configuration.

        Args:
            None

        Returns:
            Tuple (hw_product_name, hw_revision, configuration_id) or
                ``False`` if auto-detection failed.

        **Example:**

        .. literalinclude:: sch_api_examples/get_hw_settings.example
           :language: python
           :lines: 2-
        """
        return clstub().get_hw_settings()

    def set_simulation_method(self, simulation_method):
        """
        .. deprecated:: 2.0
        Use ``set_model_property_value`` instead (``simulation_method`` field
        in configuration object).

        Set simulation method.

        Args:
            simulation_method (str): Method used for simulation.

        Returns:
            ``True`` if successful, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/set_simulation.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_simulation.example
        """
        return clstub().set_simulation_method(simulation_method=simulation_method)

    def set_simulation_time_step(self, time_step):
        """
        .. deprecated:: 2.0
        Use ``set_model_property_value`` instead (``simulation_time_step`` field in
        configuration object).

        Set schematic model simulation time time_step.

        Args:
            time_step (str): Time step used for simulation.

        Returns:
            ``True`` if successful, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/set_simulation.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_simulation.example
        """
        return clstub().set_simulation_time_step(time_step=time_step)

    def set_component_property(self, component, property, value):
        """
        .. deprecated:: 2.0
        Use :func:`set_property_value` instead.

        Sets component property value to provided value.

        Args:
            component (str): Component name.
            property (str): Property name (code name of property, can be viewed
                in tooltip over property widget in component property dialog).
            value (object): New property value.

        Returns:
            ``True`` if property value was successfully applied,
            ``False`` otherwise.
        """
        return clstub().set_component_property(component=component,
                                               property=property,
                                               value=value)

    def set_property_attribute(self, component, property, attribute, value):
        """
        NOTE: This function is deprecated.
        It is kept here, because some code exists which uses it.

        :param component: component name.
        :param property: property name.
        :param attribute: attribute name.
        :param value: new value for property.
        :return: True if successful, False otherwise.
        """
        return clstub().set_property_attribute(component=component,
                                               property=property,
                                               attribute=attribute,
                                               value=value)

    def set_model_property_value(self, prop_code_name, value):
        """
        Sets model property to specified value.

        Args:
            prop_code_name (str): Model property code name.
            value (object): Value to set.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException when specified model property doesn't
            exists.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_model_property.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_model_property.example
        """
        return clstub().set_model_property_value(prop_code_name=prop_code_name,
                                                 value=value)

    def get_model_property_value(self, prop_code_name):
        """
        Return value for specified model property (model configuration).
        Model property is identified by its code name which can be found
        in schematic editor schematic settings dialog when tooltip is shown
        over desired setting option.

        Args:
            prop_code_name (str): Model property code name.

        Returns:
            Value for model property.

        Raises:
            SchApiItemNotFoundException if specified model property can't be
            found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_model_property.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_model_property.example
        """
        return clstub().get_model_property_value(prop_code_name=prop_code_name)

    def get_component_type_name(self, comp_handle):
        """
        Return component type name.

        Args:
            comp_handle(ItemHandle): Component handle.

        Returns:
            Component type name as string, empty string if component has not
            type (e.g. component is user subsystem).

        Raises:
            SchApiItemNotFoundException if specified component  can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_component_type_name.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_component_type_name.example
        """
        return clstub().get_component_type_name(comp_handle=comp_handle)

    def get_item(self, name, parent=None, item_type=ITEM_ANY):
        """
        Get item handle for item named ``name`` from parent ``parent_handle``.

        .. note:: ``parent`` is optional if not specified root scheme
                    will be used.

        .. note:: ``item_type`` is optional parameter, it can be used to
                  specify type of item to get handle of. It accepts constant
                  which defines item type (See `Schematic API constants`_)

        Args:
            name (str): Item name.
            parent (ItemHandle): Parent handle.
            item_type (str): Item type constant.

        Returns:
            Item handle (ItemHandle) if found, None otherwise.

        Raises:
            SchApiException if there is multiple items found, for example
            component has sub-component named exactly the same as component
            terminal. In that case specify ``item_type`` to remove ambiguity.

        **Example:**

        .. literalinclude:: sch_api_examples/get_item.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_item.example
        """
        return clstub().get_item(name=name, parent=parent, item_type=item_type)

    def info(self, msg, context=None):
        """
        Function signals informative messages.

        Args:
            msg (str): Message string.
            context (ItemHandle): Handle for context item.

        Returns:
            None

        **Example:**

          .. literalinclude:: sch_api_examples/info.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/info.example
        """
        return clstub().info(msg=msg, context=context)

    def warning(self, msg, kind=WARNING_GENERAL, context=None):
        """
        Signals some warning condition.

        Args:
            msg (str): Message string.
            kind (str):
            context (ItemHandle): Handle for context item.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException if context item can't be found.

        **Example:**

          .. literalinclude:: sch_api_examples/warning.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/warning.example
        """
        return clstub().warning(msg=msg, kind=kind, context=context)

    def error(self, msg, kind=ERROR_GENERAL, context=None):
        """
        Signals some error condition.

        Args:
            msg (str): Message string.
            kind (str): Error kind constant.
            context (ItemHandle): Handle for context item.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/error.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/error.example
        """
        return clstub().error(msg=msg, kind=kind, context=context)

    def set_name(self, item_handle, name):
        """
        Set name for item.

        Args:
            item_handle (ItemHandle): Item handle.
            name (str): Name to set.

        Returns:
            None

        Raises:
            SchApiItemNameExistsException if another item already has
            provided name.
            SchApiException in case when item pointed by item_handle doesn't
            have name attribute or if some other item already has provided name.

        **Example:**

        .. literalinclude:: sch_api_examples/set_name.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_name.example
        """
        return clstub().set_name(item_handle=item_handle, name=name)

    def get_items(self, parent=None, item_type=None):
        """
        Return handles for all items contained in parent component
        specified using ``parent`` handle, optionally filtering items based
        on type, using ``item_type``. ``item_type`` value is constant, see
        `Schematic API constants`_ for details.

        .. note:: If parent is not specified top level scheme will be used as
                  parent.

        .. note:: Items are not recursively returned.

        Args:
            parent (ItemHandle): Parent component handle.
            item_type (str): Constant specifying type of items. If not
                provided, all items are included.

        Returns:
            List of item handles.

        **Example:**

        .. literalinclude:: sch_api_examples/get_items.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_items.example
        """
        return clstub().get_items(parent=parent, item_type=item_type)

    def find_connections(self, connectable_handle1, connectable_handle2=None):
        """
        Return all connection handles which are connected to
        ``connectable_handle1``.

        If ``connectable_handle2`` is also specified then return handles
        for shared connections (ones that are connecting ``connectable_handle1``
        and ``connectable_handle2`` directly.

        Args:
            connectable_handle1 (ItemHandle): Connectable handle.
            connectable_handle2 (ItemHandle): Other connectable handle.

        Returns:
            List of connection handles.

        Raises:
            SchApiItemNotFound if one or both connectables can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/find_connections.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/find_connections.example

        """
        return clstub().find_connections(
            connectable_handle1=connectable_handle1,
            connectable_handle2=connectable_handle2
        )

    def is_subsystem(self, comp_handle):
        """
        Returns whether component specified by ``comp_handle`` is a
        subsystem (composite) component.

        .. note:: Component is an atomic component if it's not composite.

        Args:
            comp_handle (ItemHandle): Component handle.

        Returns:
            ``True`` if component is subsystem, ``False`` otherwise.

        Raises:
            SchApiItemNotFoundException if component is not found.

        **Example:**

        .. literalinclude:: sch_api_examples/is_subsystem.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/is_subsystem.example
        """
        return clstub().is_subsystem(comp_handle=comp_handle)

    # * * *  * * * * * * * * * * * * * * * * * * *
    #                Component                   *
    # * * *  * * * * * * * * * * * * * * * * * * *
    def create_component(self, type_name, parent=None, name=None,
                         rotation=ROTATION_UP, position=None):
        """
        Creates component using provided type name inside the container
        component specified by `parent`. If `parent` is not
        specified top level parent (scheme) will be used as parent.

        Parameter ``rotation`` expects respective constants as
        value (See `Schematic API constants`_).

        Args:
            type_name (str): Component type name, specifies which component to
                create.
            parent (ItemHandle): Container component handle.
            name (str): Component name.
            rotation (str): Rotation of the component.
            position (sequence): X and Y coordinates of component.

        Returns:
            Handle for created component.

        Raises:
            SchApiException in case when component creation fails.

        **Example:**

        .. literalinclude:: sch_api_examples/create_component.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_component.example
        """
        return clstub().create_component(
            type_name=type_name,
            parent=parent,
            name=name,
            rotation=rotation,
            position=position
        )

    def create_port(self, name=None, parent=None, kind=KIND_PE,
                    direction=DIRECTION_OUT, sp_type=SP_TYPE_REAL,
                    terminal_position=("left", "auto"), rotation=ROTATION_UP,
                    hide_name=False, position=None):
        """
        Create port inside the container component specified by `parent`.

        Parameters ``kind``, ``direction``, ``sp_type and`` and ``rotation``
        expects respective constants as values (See `Schematic API constants`_).

        Args:
            name (str): Port name.
            parent (ItemHandle): Container component handle.
            kind (str): Port kind (signal processing or power electronic kind).
            direction (str): Port direction (applicable only for signal
                processing ports)
            sp_type (str): SP type for port.
            terminal_position (tuple): Specify position of port based terminal
                on component.
            rotation (str): Rotation of the tag.
            hide_name (bool): Indicate if label for terminal (created on
                component as a result of this port) should be hidden.
            position (sequence): X and Y coordinates of port.

        Returns:
            Handle for created port.

        Raises:
            SchApiException in case port creation fails (for example when
            port is created at the top level parent or any other cause of
            error).

        **Example:**

        .. literalinclude:: sch_api_examples/create_port.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_port.example
        """
        return clstub().create_port(
            name=name, parent=parent,
            kind=kind,
            direction=direction,
            sp_type=sp_type,
            terminal_position=terminal_position,
            rotation=rotation,
            hide_name=hide_name,
            position=position
        )

    def create_connection(self, start, end, name=None):
        """
        Create connection with specified start and end connectable handles.
        Connectable can be component terminal, junction, port or tag.

        .. note:: Both start and end must be of same kind and they both must be
        located in same parent.

        Args:
            start (ItemHandle): Handle for connection start.
            end (ItemHandle): Handle for connection end.
            name (str): Connection name.

        Returns:
            Handle for created connection.

        Raises:
            SchApiException in case when connection creation fails.
            SchApiDuplicateConnectionException in case when provided
            connectables is already connected.

        **Example:**

        .. literalinclude:: sch_api_examples/create_connection.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_connection.example
        """
        return clstub().create_connection(start=start, end=end, name=name)

    def create_junction(self, name=None, parent=None, kind=KIND_PE,
                        position=None):
        """
        Create junction inside container component specified by `parent`.

        Parameter ``kind`` expects respective constants as
        value (See `Schematic API constants`_).

        Args:
            name (str): Junction name.
            parent (ItemHandle): Container component handle.
            kind (str): Kind of junction (can be signal processing or
                power electronic kind)
            position (sequence): X and Y coordinates of junction in the
                container.

        Returns:
            Handle for created junction.

        Raises:
            SchApiException in case when junction creation fails.

        **Example:**

        .. literalinclude:: sch_api_examples/create_junction.example
           :language: python
           :lines: 2-

         Output

        .. program-output:: python sch_api_examples/create_junction.example
        """
        return clstub().create_junction(
            name=name,
            parent=parent,
            kind=kind,
            position=position
        )

    def create_tag(self, value, name=None, parent=None,
                   scope=TAG_SCOPE_GLOBAL, kind=KIND_PE, direction=None,
                   rotation=ROTATION_UP, position=None):
        """
        Create tag inside container component specified by `parent` handle..

        Parameters ``scope``, ``kind``, ``direction`` and ``rotation``
        expects respective constants as values (See `Schematic API constants`_).

        Args:
            value (str): Tag value, used to match with other tags.
            name (str): Tag name.
            parent (ItemHandle): Container component handle.
            scope (str): Tag scope, specifies scope in which matching tag is
             searched.
            kind (str): Kind of tag (can be either KIND_SP or KIND_PE).
            direction (str): Tag direction (for signal processing tags).
            rotation (str): Rotation of the tag, can be one of following:
                ROTATION_UP, ROTATION_DOWN, ROTATION_LEFT and ROTATION_RIGHT.
            position (sequence): X and Y coordinates of tag in the container.

        Returns:
            Handle for created tag.

        Raises:
            SchApiException in case when tag creation fails.

        **Example:**

        .. literalinclude:: sch_api_examples/create_tag.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_tag.example
        """
        return clstub().create_tag(
            value=value,
            name=name,
            parent=parent,
            scope=scope,
            kind=kind,
            direction=direction,
            rotation=rotation,
            position=position
        )

    def create_comment(self, text, parent=None, name=None,
                       position=None):
        """
        Create comment with provided text inside the container component
        specified by `parent`.

        Args:
            text (str): Comment text.
            parent (ItemHandle): Parent component handle.
            name (str): Comment's name.
            position (sequence): X and Y coordinates of tag in the container.

        Returns:
            Handle for created comment.

        Raises:
            SchApiException in case when connection creation fails.

        **Example:**

        .. literalinclude:: sch_api_examples/create_comment.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_comment.example
        """
        return clstub().create_comment(
            text=text,
            parent=parent,
            name=name,
            position=position
        )

    def set_position(self, item_handle, position):
        """
        Sets item (specified by ``item_handle``) position.

        .. note:: Position coordinates are rounded to nearest value which
         are divisible by {grid_resolution} (this is done because graphical 
         representation of scheme assume that positions respect this behavior). 


        Args:
            item_handle (ItemHandle): Item handle.
            position (sequence): Position to set.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException when specified item can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_position.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_position.example
        """.format(grid_resolution=GRID_RESOLUTION)
        return clstub().set_position(item_handle=item_handle,
                                     position=position)

    def get_position(self, item_handle):
        """
        Gets item position.

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            Position in tuple form (x, y).

        Raises:
            SchApiItemNotFoundException when specified item can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_position.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_position.example
        """
        return clstub().get_position(item_handle=item_handle)

    def delete_item(self, item_handle):
        """
        Delete item named specified by ``item_handle``.

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            None

        Raises:
            SchApiException in case when deletion fails.

        **Example:**

        .. literalinclude:: sch_api_examples/delete_item.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/delete_item.example
        """
        return clstub().delete_item(item_handle=item_handle)

    def exists(self, name, parent=None, item_type=ITEM_ANY):
        """
        Checks if item named ``name`` is container in parent component
        specified by ``parent`` handle. If parent handle is not provided
        root scheme is used as parent.

        .. note :: ``item_type`` is a constant which specify which item type to
            look for. See `Schematic API constants`_.

        Args:
            name (str): Item name to check.
            parent (ItemHandle): Parent handle.
            item_type (str): Item type constant.

        Returns:
            True if item with provided name exists in parent, False otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/exists.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/exists.example
        """
        return clstub().exists(name=name, parent=parent, item_type=item_type)

    # * * *  * * * * * * * * * * * * * * * * * * *
    #                Properties                  *
    # * * *  * * * * * * * * * * * * * * * * * * *
    def enable_property(self, prop_handle):
        """Sets property as editable.


        .. note :: The effect of this function is only visible on the
            Schematic Editor's UI.

        When the property is enabled, it is possible to change its value in
        the dialog. To disable property, use :func:`disable_property`
        function.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            None

        Raises:


        **Example:**

        .. literalinclude:: sch_api_examples/enable_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/enable_property.example
        """
        return clstub().enable_property(prop_handle=prop_handle)

    def disable_property(self, prop_handle):
        """
        Sets property as non-editable.

        .. note:: The effect of this function is visible only on the Schematic
            Editor's UI.

        When the property is disabled, it is not possible to change its
        value in the dialog. To enable property, use :func:`enable_property`
        function.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/enable_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/enable_property.example
        """
        return clstub().disable_property(prop_handle=prop_handle)

    def is_property_enabled(self, prop_handle):
        """
        Returns True if property is enabled, False otherwise.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            bool

        **Example:**

        .. literalinclude:: sch_api_examples/enable_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/enable_property.example
        """
        return clstub().is_property_enabled(prop_handle=prop_handle)

    def show_property(self, prop_handle):
        """
        Makes component property visible in the component's dialog.

        .. note:: The effect of this function is visible only on the Schematic
            Editor's UI.

        When this function is called, property will become visible in the
        component's dialog. To hide a property, use :func:`hide_property`
        function.


        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/show_hide_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/show_hide_property.example
        """
        return clstub().show_property(prop_handle=prop_handle)

    def hide_property(self, prop_handle):
        """
        Makes component property invisible on the component's dialog.

        .. note:: The effect of this function is visible only in the Schematic
            Editor's UI.

        When this function is called, property will become invisible in the
        component's dialog. To show a property, use :func:`hide_property`
        function.

        Args:
            prop_handle (ItemHandle): Property handle.

        **Example:**

        .. literalinclude:: sch_api_examples/show_hide_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/show_hide_property.example
        """
        return clstub().hide_property(prop_handle=prop_handle)

    def is_property_visible(self, prop_handle):
        """
        Returns True if component property is visible on the component's
        dialog, False otherwise.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            ``True`` if property is visible, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/show_hide_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/show_hide_property.example
        """
        return clstub().is_property_visible(prop_handle=prop_handle)

    def get_conv_prop(self, prop_handle, value=None):
        """
        Converts provided `value` to type which is specified in property
        type specification. If value is not provided property display value
        is used instead.

        Args:
            prop_handle (ItemHandle): Property handle.
            value (str): Value to convert.

        Returns:
            Python object, converted value.

        Raises:
            SchApiException if value cannot be converted.

        **Example:**

        .. literalinclude:: sch_api_examples/get_conv_prop.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_conv_prop.example
        """
        return clstub().get_conv_prop(prop_handle=prop_handle, value=value)

    def get_property_value(self, prop_handle):
        """
        Returns the value of a property.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            object

        **Example:**

        .. literalinclude:: sch_api_examples/set_get_property_value.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_get_property_value.example
        """
        return clstub().get_property_value(prop_handle=prop_handle)

    def get_property_default_value(self, prop_handle):
        """
        Returns property default value.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            Property default value as string.

        Raises:
            SchApiItemNotFoundException if property can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_property_default_value.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_property_default_value.example
        """
        return clstub().get_property_default_value(prop_handle=prop_handle)

    def set_property_value(self, prop_handle, value):
        """
        Set a new value to the property.

        Args:
            prop_handle (ItemHandle): Property handle.
            value (object): New value.

        **Example:**

        .. literalinclude:: sch_api_examples/set_get_property_value.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_get_property_value.example
        """
        return clstub().set_property_value(prop_handle=prop_handle,
                                           value=value)

    def get_property_disp_value(self, prop_handle):
        """
        Return the display value of the property.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            str

        **Example:**

        .. literalinclude:: sch_api_examples/set_prop_display_value.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_prop_display_value.example
        """
        return clstub().get_property_disp_value(prop_handle=prop_handle)

    def set_property_disp_value(self, prop_handle, value):
        """
        Set property display value.

        Args:
            prop_handle (ItemHandle): Property handle.
            value (str): Value.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/set_prop_display_value.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_prop_display_value.example
        """
        return clstub().set_property_disp_value(prop_handle=prop_handle,
                                                value=value)

    def get_property_combo_values(self, prop_handle):
        """
        Returns combo_values list for property specified by ``prop_handle``.

        .. note:: This function works for properties which have widget
                  set to combo.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            Sequence of property combo values.

        Raises:
            SchApiException if property widget is not combo.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_prop_combo_values.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_prop_combo_values.example
        """
        return clstub().get_property_combo_values(prop_handle=prop_handle)

    def set_property_combo_values(self, prop_handle, combo_values):
        """
        Sets property combo values to provided one.

        .. note:: Property specified by ``prop_handle`` must have widget set
                  to combo.

        Args:
            prop_handle (ItemHandle): Property handle.
            combo_values (sequence): Sequence of new combo values.

        Returns:
            None

        Raises:
            SchApiException when functions is called with property handle
            where property widget is not combo.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_prop_combo_values.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_prop_combo_values.example
        """
        return clstub().set_property_combo_values(prop_handle=prop_handle,
                                                  combo_values=combo_values)

    # * * * * * * * * * * * * * * * * * * *
    # Icons
    # * * * * * * * * * * * * * * * * * * * * * * *  * *

    def set_component_icon_image(self, comp_handle,
                                 image_filename, rotate=ICON_ROTATE):
        """
        Specify image to be used in component icon.
        If component is masked, image for top mask icon is specified instead.

        Args:
            comp_handle (ItemHandle): Component handle.
            image_filename (str): Image filename.
            rotate (str): Constant describing icon rotation
                behavior (See `Schematic API constants`_).

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/icon.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        return clstub().set_component_icon_image(comp_handle=comp_handle,
                                                 image_filename=image_filename,
                                                 rotate=rotate)

    def disp_component_icon_text(self, comp_handle, text,
                                 rotate=ICON_TEXT_LIKE, size=10, relpos_x=0.5,
                                 relpos_y=0.5, trim_factor=1.0):
        """
        Specify text to be displayed inside component icon.

        Args:
            comp_handle (ItemHandle): Component handle.
            text (str): Text to display.
            rotate (str): Constant specifying icon rotation behavior,
                (See `Schematic API constants`_).
            size (int): Size of text.
            relpos_x (float): Center of text rectangle (on X axis).
            relpos_y (float): Center of text rectangle (on Y axis).
            trim_factor (float): Number in range (0.0 .. 1.0) which specifies
                at which relative width of text rectangle width to shorten text.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/icon.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        return clstub().disp_component_icon_text(
            comp_handle=comp_handle,
            text=text,
            rotate=rotate,
            size=size,
            relpos_x=relpos_x,
            relpos_y=relpos_y,
            trim_factor=trim_factor
        )

    def set_color(self, comp_handle, color):
        """
        Set color to be used in all subsequent icon API operations.
        Color name is specified as a string in format understood by Qt
        framework.

        Args:
            comp_handle (ItemHandle): Component handle.
            color (str): Color name.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/icon.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        return clstub().set_color(comp_handle=comp_handle, color=color)

    def refresh_icon(self, comp_handle):
        """
        Refresh component icon. Calls component DEFINE_ICON handler
        or top mask DEFINE_ICON if mask is present.

        Args:
            comp_handle (ItemHandle): Component handle.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/icon.example.
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        return clstub().refresh_icon(comp_handle=comp_handle)

    # * * *  * * * * * * * * * * * * * * * * * * *
    #                Terminals                   *
    # * * *  * * * * * * * * * * * * * * * * * * *
    def get_terminal_dimension(self, terminal_handle):
        """
        Returns the dimension of the component terminal.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

        Returns:
            Terminal dimension as list.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_term_dimension.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_term_dimension.example
        """
        return clstub().get_terminal_dimension(terminal_handle=terminal_handle)

    def set_terminal_dimension(self, terminal_handle, dimension):
        """
        Set component terminal dimension.

        Args:
            terminal_handle (ItemHandle): Terminal handle.
            dimension (tuple): Terminal new dimension.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_term_dimension.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_term_dimension.example
        """
        return clstub().set_terminal_dimension(terminal_handle=terminal_handle,
                                               dimension=dimension)

    def sync_dynamic_terminals(self, comp_handle, term_name, term_num,
                               labels=None, sp_types=None, feedthroughs=None):
        """
        Synchronize number of dynamic terminals on component with given name.

        Args:
            comp_handle (ItemHandle): Component handle.
            term_name (str): Terminal name.
            term_num (int): Number of terminal to synchronize to.
            labels (list): List of labels for new terminals.
            sp_types (list): List of SP types for new terminals.
            feedthroughs (list): List of feedthrough values for new terminals.

        **Example:**

        .. literalinclude:: sch_api_examples/sync_dyn_terms.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/sync_dyn_terms.example
        """
        return clstub().sync_dynamic_terminals(
            comp_handle=comp_handle,
            term_name=term_name,
            term_num=term_num,
            labels=labels,
            sp_types=sp_types,
            feedthroughs=feedthroughs
        )

    def get_terminal_sp_type(self, terminal_handle):
        """
        Return component terminal SP type.

        SP type can be one of the following: SP_TYPE_INHERIT, SP_TYPE_INT,
        SP_TYPE_UINT, SP_TYPE_REAL or the expression that can be evaluated into
        those values.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

        Returns:
            Terminal SP type as string.

        **Example:**

        .. literalinclude:: sch_api_examples/get_term_sp_type.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_term_sp_type.example
        """
        return clstub().get_terminal_sp_type(terminal_handle=terminal_handle)

    def set_terminal_sp_type(self, terminal_handle, sp_type):
        """
        Set component terminal SP (Signal processing) type.

        SP type can be one of the constants for SP type
        (See `Schematic API constants`_) or the expression that can be evaluated
        into those values.

        Args:
            terminal_handle (ItemHandle): Terminal handle.
            sp_type (str): SP (Signal processing) type.

        **Example:**

        .. literalinclude:: sch_api_examples/set_term_sp_type.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_term_sp_type.example
        """
        return clstub().set_terminal_sp_type(terminal_handle=terminal_handle,
                                             sp_type=sp_type)

    def get_terminal_sp_type_value(self, terminal_handle):
        """
        Return component terminal calculated SP type (calculated based on value
        of SP type for that terminal).

        If calculated, returned value can be either SP_TYPE_INT, SP_TYPE_UINT,
        SP_TYPE_REAL.
        Calculation of the SP type value is performed during the compilation
        of the schematic.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

        Returns:
            Terminal SP type as string.

        **Example:**

        .. literalinclude:: sch_api_examples/get_term_sp_type.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_term_sp_type.example
        """
        return clstub().get_terminal_sp_type_value(terminal_handle=terminal_handle)

    def set_terminal_sp_type_value(self, terminal_handle, sp_type_value):
        """
        Set component terminal SP type directly.

        Args:
            terminal_handle (ItemHandle): Terminal handle.
            sp_type_value (str): New SP type value, must be constant for
                SP Type (See `Schematic API constants`_).

        **Example:**

        .. literalinclude:: sch_api_examples/set_term_sp_type.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_term_sp_type.example
        """
        return clstub().set_terminal_sp_type_value(
            terminal_handle=terminal_handle, sp_type_value=sp_type_value)

    def is_terminal_feedthrough(self, terminal_handle):
        """
        Determine if terminal is feedthrough.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

        Returns:
            ``True`` if terminal is feedthrough, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/term_feedthrough.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/term_feedthrough.example
        """
        return clstub().is_terminal_feedthrough(terminal_handle=terminal_handle)

    def set_terminal_feedthrough(self, terminal_handle, feedthrough):
        """
        Set terminal feedthrough value.

        Args:
            terminal_handle (ItemHandle): Terminal handle.
            feedthrough (bool): Terminal feedthrough value.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/term_feedthrough.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/term_feedthrough.example
        """
        return clstub().set_terminal_feedthrough(
            terminal_handle=terminal_handle,
            feedthrough=feedthrough
        )

    # * * *  * * * * * * * * * * * * * * * * * * *
    #                Namespace                   *
    # * * *  * * * * * * * * * * * * * * * * * * *
    def set_ns_var(self, var_name, value):
        """
        Set namespace variable named ``var_name`` to ``value``.
        If variable doesn't exists in namespace, it will be created
        and value set.

        Args:
            var_name (str): Namespace variable name.
            value (object): Value to be set.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_ns_var.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_ns_var.example
        """
        return clstub().set_ns_var(var_name=var_name, value=value)

    def get_ns_var(self, var_name):
        """
        Return value of namespace variable named ``var_name``.

        Args:
            var_name (str): Namespace variable name.

        Returns:
            Python object.

        Raises:
            KeyError: if variable with given name doesn't exist in the
                namespace.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_ns_var.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_ns_var.example
        """
        return clstub().get_ns_var(var_name=var_name)

    def get_ns_vars(self):
        """
        Get names of all variables in namespace.

        Args:
            None

        Returns:
            List of variable names in namespace.

        **Example:**

        .. literalinclude:: sch_api_examples/get_ns_vars.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_ns_vars.example
        """
        return clstub().get_ns_vars()


model = SchematicAPI()
