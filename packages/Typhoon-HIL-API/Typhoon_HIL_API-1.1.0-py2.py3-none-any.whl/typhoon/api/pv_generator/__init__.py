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

from typhoon.api.pv_generator.stub import clstub

# ----------------------------------------
# -------------- pv settings -------------
# ----------------------------------------

# pv panel model types
PV_MT_DETAILED = "Detailed"
PV_MT_EN50530 = "EN50530 Compatible"
PV_MODELS = [PV_MT_DETAILED,PV_MT_EN50530]

# pv types used in EN50530 model
EN50530_PV_TYPES = ["cSi", "Thin film"]

# pv types used in Detailed model
DETAILED_PV_TYPE = ["cSi", "Amorphous Si"]


def generate_pv_settings_file(modelType, fileName, parameters):
    """
    Generate PV panel settings (.ipvx extension) with specified parameters.

    Args:
        modelType (str): PV model type that will be used for generating settings file.
        fileName (str): file name of resulting .ipvx file.
        parameters (str): dictionary with parameters.

    Supported PV ``modelType`` are:
        * ``'Detailed'`` or ``pv.PV_MODELS[0]``
        * ``'EN50530 Compatible'`` or ``pv.PV_MODELS[1]``

    Depending on used PV model type available ``parameters`` are:

    * ``'Detailed'`` model

        +-------------------+-------------------------------------------------------+----------------------------------+
        |   Dictionary key  |                   Meaning                             |               Value              |
        +===================+=======================================================+==================================+
        |     "Voc_ref"     | Open-circuit voltage (Voc [V])                        |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |     "Isc_ref"     | Short-circuit current (Isc [A])                       |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |     "dIsc_dT"     | Temperature coefficient of Isc [%Isc/C]               |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |       "Nc"        | Number of cells                                       |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |    "dV_dI_ref"    | Curve gradient in Voc_ref point (dV/dI at Voc [V/A])  |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |       "Vg"        | Band gap voltage                                      | string ("cSi" or "Amorphous Si") |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |       "n"         | Curve gradient in Voc_ref point (dV/dI at Voc [V/A])  |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |   "neg_current"   | Allow negative current                                |      boolean (True or False)     |
        +-------------------+-------------------------------------------------------+----------------------------------+

    * ``'EN50530 Compatible'`` model

        +-------------------+-------------------------------------------------------+----------------------------------+
        |   Dictionary key  |                   Meaning                             |               Value              |
        +===================+=======================================================+==================================+
        |     "Voc_ref"     | Open-circuit voltage (Voc [V])                        |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |     "Isc_ref"     | Short-circuit current (Isc [A])                       |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |     "pv_type"     | PV type                                               |    string ("cSi" or "Thin film") |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |   "neg_current"   | Allow negative current                                |      boolean (True or False)     |
        +-------------------+-------------------------------------------------------+----------------------------------+

    Returns:
        tuple(``status``, ``message``)
            * status (bool): ``True`` if everything OK otherwise return ``False``
            * message (str): status message

    Example::

        import typhoon.api.pv_generator as pv

        params = {"Voc_ref": 45.60,                     # Open-circuit voltage (Voc [V])
                  "Isc_ref": 5.8,                       # Short-circuit current (Isc [A])
                  "dIsc_dT": 0.0004,                    # Temperature coefficient of Isc [%Isc/C]
                  "Nc": 72,                             # Number of cells
                  "dV_dI_ref": -1.1,                    # Curve gradient in Voc_ref point (dV/dI at Voc [V/A])
                  "Vg": pv.DETAILED_PV_TYPE[0],         # Band gap voltage ("cSi", "Amorphous Si")
                  "n" : 1.3,                            # Curve gradient in Voc_ref point (dV/dI at Voc [V/A])
                  "neg_current": False }                # allow negative current

        # generate settings file using Detailed type of PV Model
        (status,msg) =  pv.generate_pv_settings_file(pv.PV_MT_DETAILED,"./setDet.ipvx",params)


        params = {"Voc_ref": 45.60,                     # Open-circuit voltage (Voc [V])
                  "Isc_ref": 5.8,                       # Short-circuit current (Isc [A])
                  "pv_type": pv.EN50530_PV_TYPES[0],    # "cSi" pv type ("cSi" or "Thin film")
                  "neg_current": False }                # allow negative current

        # generate settings file using EN50530 type of PV Model
        (status,msg) =  pv.generate_pv_settings_file(pv.PV_MT_EN50530,"./setEN.ipvx",params)

    """
    return clstub().generate_pv_settings_file(modelType=modelType,
                                              fileName=fileName,
                                              parameters=parameters)



