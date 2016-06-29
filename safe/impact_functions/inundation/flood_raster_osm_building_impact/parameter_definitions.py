# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Parameter definition for
Flood Raster Impact on OSM Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.impact_functions.unit_definitions import parameter_unit_metres
from safe_extras.parameters.group_parameter import GroupParameter

__author__ = 'lucernae'

from safe_extras.parameters.float_parameter import FloatParameter
from safe.utilities.i18n import tr


def threshold():
    """Generator for the default threshold parameter.

    :return: List of FloatParameter
    :rtype: list[FloatParameter]
    """
    field = FloatParameter()
    field.name = tr('Threshold [m]')
    field.is_required = True
    field.precision = 2
    field.value = 1.0  # default value
    unit_metres = parameter_unit_metres()
    field.unit = unit_metres
    field.allowed_units = [unit_metres]
    field.help_text = tr(
        'Threshold value to categorize inundated area.')
    field.description = tr(
        'Hazard value above the threshold in meter will be considered '
        'inundated.')
    return field


def thresholds():
    group = GroupParameter()
    group.name = tr('Thresholds [m]')
    group.enable_parameter = False
    group.must_scroll = False
    group.help_text = tr(
        'Threshold values to categorize inundated area in multiple levels.')
    group.description = tr(
        'Hazard value above the thresholds in meter will be considered '
        'inundated to different levels. This overrides the single threshold'
    )

    low = FloatParameter()
    low.name = tr('Low inundation threshold [m]')
    low.is_required = True
    low.precision = 2
    low.value = 0.2  # default value
    unit_metres = parameter_unit_metres()
    low.unit = unit_metres
    low.allowed_units = [unit_metres]
    low.help_text = tr(
            'Threshold value to categorize inundated area.')
    low.description = tr(
            'Hazard value above the threshold in meter will be considered '
            'inundated.')

    medium = FloatParameter()
    medium.name = tr('Medium inundation threshold [m]')
    medium.is_required = True
    medium.precision = 2
    medium.value = 1.0  # default value
    unit_metres = parameter_unit_metres()
    medium.unit = unit_metres
    medium.allowed_units = [unit_metres]
    medium.help_text = tr(
            'Threshold value to categorize inundated area.')
    medium.description = tr(
            'Hazard value above the threshold in meter will be considered '
            'inundated.')

    high = FloatParameter()
    high.name = tr('High inundation threshold [m]')
    high.is_required = True
    high.precision = 2
    high.value = 1.5  # default value
    unit_metres = parameter_unit_metres()
    high.unit = unit_metres
    high.allowed_units = [unit_metres]
    high.help_text = tr(
            'Threshold value to categorize inundated area.')
    high.description = tr(
            'Hazard value above the threshold in meter will be considered '
            'inundated.')

    extreme = FloatParameter()
    extreme.name = tr('Extreme inundation threshold [m]')
    extreme.is_required = True
    extreme.precision = 2
    extreme.value = 2.0  # default value
    unit_metres = parameter_unit_metres()
    extreme.unit = unit_metres
    extreme.allowed_units = [unit_metres]
    extreme.help_text = tr(
            'Threshold value to categorize inundated area.')
    extreme.description = tr(
            'Hazard value above the threshold in meter will be considered '
            'inundated.')

    group.value = [low, medium, high, extreme]

    def _group_validator(parameters=None):
        parameters_values = [p.value for p in parameters]
        not_ordered = False
        previous_value = None
        for value in parameters_values:
            if value <= previous_value:
                not_ordered = True
                break
            previous_value = value
        if not_ordered:
            message = tr('The thersholds must be ordered from small to big. '
                         'Found: %s') % parameters_values
            raise ValueError(message)

    group.custom_validator = _group_validator

    return group
