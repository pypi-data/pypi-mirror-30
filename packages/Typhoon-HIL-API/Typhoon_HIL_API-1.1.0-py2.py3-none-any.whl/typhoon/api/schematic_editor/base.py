#
# Schematic API
#
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
from __future__ import print_function, unicode_literals

import time

from typhoon.api.schematic_editor.const import DIRECTION_OUT, FQN_SEP, \
    ICON_ROTATE, ICON_TEXT_LIKE, ROTATION_UP, KIND_PE, TAG_SCOPE_GLOBAL, \
    ITEM_TERMINAL, ITEM_PROPERTY, ITEM_ANY, \
    SP_TYPE_REAL, ERROR_GENERAL, WARNING_GENERAL, GRID_RESOLUTION
from typhoon.api.schematic_editor.util import ItemHandle


class SchematicAPIBase(object):
    """
    Base class for schematic API (Application Programming Interface)

    It defines shared attributes between different specialization
    (like one for handlers, for scripts and so on).
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize an object.

        Args:
            None
        """
        super(SchematicAPIBase, self).__init__()

    @staticmethod
    def _generate_model_name():
        """
        Generate model name.
        """
        time_stamp = time.strftime("%d-%b-%Y@%H-%M-%S")
        return "New schematic {0}".format(time_stamp)

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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

        .. literalinclude:: sch_api_examples/get_set_model_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_model_property.example
        """
        raise NotImplementedError()

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

        .. literalinclude:: sch_api_examples/get_set_model_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_model_property.example
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

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

        .. literalinclude:: sch_api_examples/get_item.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_item.example
        """
        raise NotImplementedError()

    def info(self, msg, context=None):
        """
        Function signals informative messages.

        Args:
            msg (str): Message string.
            context (ItemHandle): Handle for context item.

        Returns:
            None

        **Example:**

          .. literalinclude:: sch_api_examples/info.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/info.example
        """
        raise NotImplementedError()

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

          .. literalinclude:: sch_api_examples/warning.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/warning.example
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    @staticmethod
    def fqn(*args):
        """
        Joins multiple provided arguments using FQN separator between them.

        Args:
            *args: Variable number of string arguments.

        Returns:
            Joined string.

        **Example:**

        .. literalinclude:: sch_api_examples/fqn.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/fqn.example
        """
        parts = (p for arg in args for p in arg.split(FQN_SEP) if p)
        return FQN_SEP.join(parts)

    @staticmethod
    def get_name(item_handle):
        """
        Get name of item specified by ``item_handle``.

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            Item name.

        **Example:**

        .. literalinclude:: sch_api_examples/get_name.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_name.example
        """
        return item_handle.name

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
        raise NotImplementedError()

    @staticmethod
    def get_fqn(item_handle):
        """
        Get fully qualified name for item specified by ``item_handle``.

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            Fully qualified name as string.

        **Example:**

        .. literalinclude:: sch_api_examples/get_fqn.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_fqn.example
        """
        return item_handle.fqn

    @staticmethod
    def term(comp_handle, term_name):
        """
        Make a unique identity handle for some terminal. Used in place where
        terminal fqn is expected.

        Args:
            comp_handle (ItemHandle): Component handle.
            term_name (str): Terminal name.

        Returns:
            Terminal handle.

        **Example:**

        .. literalinclude:: sch_api_examples/term.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/term.example
        """
        return ItemHandle(
            item_type=ITEM_TERMINAL,
            fqn=SchematicAPIBase.fqn(comp_handle.fqn, term_name)
        )

    @staticmethod
    def prop(component, prop_name):
        """
        Create property handle.

        Args:
            component
            prop_name

        Returns:
            Property handle.

        **Example:**

        .. literalinclude:: sch_api_examples/prop.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/prop.example
        """
        return ItemHandle(
            item_type=ITEM_PROPERTY,
            fqn=SchematicAPIBase.fqn(component.fqn, prop_name)
        )

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

        .. literalinclude:: sch_api_examples/get_items.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_items.example
        """
        raise NotImplementedError()

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

        .. literalinclude:: sch_api_examples/find_connections.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/find_connections.example

        """
        raise NotImplementedError()

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

        .. literalinclude:: sch_api_examples/is_subsystem.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/is_subsystem.example
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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

        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

    # * * *  * * * * * * * * * * * * * * * * * * *
    #                Properties                  *
    # * * *  * * * * * * * * * * * * * * * * * * *
    def enable_property(self, prop_handle):
        """Sets property as editable.

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
        raise NotImplementedError()

    def disable_property(self, prop_handle):
        """
        Sets property as non-editable.

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
        raise NotImplementedError()

    def is_property_enabled(self, prop_handle):
        """
        Returns if property is enabled.

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
        raise NotImplementedError()

    def show_property(self, prop_handle):
        """
        Show component property.

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
        raise NotImplementedError()

    def hide_property(self, prop_handle):
        """
        Hide component property.

        Args:
            prop_handle (ItemHandle): Property handle.

        **Example:**

        .. literalinclude:: sch_api_examples/show_hide_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/show_hide_property.example
        """
        raise NotImplementedError()

    def is_property_visible(self, prop_handle):
        """
        Returns if component property is visible.

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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

        .. literalinclude:: sch_api_examples/icon.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        raise NotImplementedError()

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

        .. literalinclude:: sch_api_examples/icon.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        raise NotImplementedError()

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

        .. literalinclude:: sch_api_examples/icon.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        raise NotImplementedError()

    def refresh_icon(self, comp_handle):
        """
        Refresh component icon. Calls component DEFINE_ICON handler
        or top mask DEFINE_ICON if mask is present.

        Args:
            comp_handle (ItemHandle): Component handle.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/icon.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

    def get_ns_vars(self):
        """
        Get names of all variables in namespace.

        Args:
            None

        Returns:
            List of all variable names in namespace.

        **Example:**

        .. literalinclude:: sch_api_examples/get_ns_vars.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_ns_vars.example
        """
        raise NotImplementedError()
