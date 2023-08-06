#
# Schematic API utility module.
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

import collections
import numbers

from typhoon.api.schematic_editor.const import FQN_SEP, ITEM_COMPONENT


class ItemHandle(object):
    """
    Represents schematic item in the context of Schematic API.
    """
    def __init__(self, item_type, fqn, **kwargs):
        """
        Initialize schematic item object.

        Args:
            item_type (str): Item type constant.
            fqn (str): Item fully qualified name.
        """
        super(ItemHandle, self).__init__()

        self.item_type = item_type
        self.fqn = fqn

    @property
    def name(self):
        """
        Return name of schematic item.
        """
        if self.fqn:
            return self.fqn.split(FQN_SEP)[-1]
        else:
            return None

    @property
    def parent(self):
        """
        Get handle for this item parent.
        If there is no parent, None is returned.

        Returns:
            ItemHandle
        """
        if not self.fqn:
            return None

        if FQN_SEP in self.fqn:
            hier = self.fqn.split(FQN_SEP)
            return ItemHandle(ITEM_COMPONENT, fqn=FQN_SEP.join(hier[:-1]))
        else:
            # Return handle to root scheme
            return ItemHandle(ITEM_COMPONENT, fqn="")

    @property
    def parent_fqn(self):
        """
        Return parent fqn of this schematic item.
        """
        return FQN_SEP.join(self.fqn.split(FQN_SEP)[:-1]) if self.fqn else None

    def __str__(self):
        """
        Custom string representation.
        """
        return "{0}: {1}".format(self.item_type, self.fqn)

    def __repr__(self):
        """
        Custom repr representation.
        """
        return "ItemHandle('{0}', '{1}')".format(
            self.item_type, self.fqn
        )

    def __hash__(self):
        return hash((self.fqn, self.item_type))

    def __eq__(self, other):
        return self.fqn == other.fqn and self.item_type == other.item_type


def sanitize_position(position):
    """
    Sanitize `position` object, if it's not specified or not in correct
    format return default position (0, 0), otherwise return provided
    position object.

    Args:
        position(sequence): Position tuple in format (x, y).

    Returns:
        Original position sequence if everything is ok, tuple (0, 0) if
        position is not in valid format.
    """
    if isinstance(position, collections.Sequence) and len(position) == 2 \
            and all(isinstance(coord, numbers.Real) for coord in position):
        return position
    else:
        return 0, 0
