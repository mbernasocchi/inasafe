from safe.defaults import get_defaults
from safe import messaging as m
from safe.impact_functions.core import (FunctionProvider,
                                        get_hazard_layer,
                                        get_exposure_layer,
                                        get_question,
                                        get_function_title)
from safe.impact_functions.styles import categorical_style
from safe.storage.vector import convert_polygons_to_centroids
from safe.common.polygon import is_inside_polygon
from safe.common.utilities import (ugettext as tr,
                                   format_int,
                                   round_thousand)
from third_party.odict import OrderedDict


class CategorisedVectorHazardPopulationImpactFunction(FunctionProvider):
    """Plugin for impact of population as derived by categorised hazard

    :author ESSC
    :rating 2
    :param requires category=='hazard' and \
                    unit=='normalised' and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='vector'
    """
    # Function documentation

    NO_DATA = 0  # TODO (MB) this should come from defaults('NO_DATA') but
    # needs a bit more work

    title = tr('Be vectoring impacted')
    synopsis = tr('To assess the impacts of categorized hazards in vector '
                  'format on population vector layer.')
    actions = tr('Provide details about how many people would likely need '
                 'to be impacted for each category.')
    hazard_input = tr('A hazard vector layer where each cell represents '
                      'the category of the hazard. There should be 3 '
                      'categories: 1, 2, and 3.')
    exposure_input = tr('An exposure vector layer where each cell represent '
                        'population count.')
    output = tr('Map of population exposed to high category and a table with '
                'number of people in each category')
    detailed_description = \
        tr('This function will calculate how many people will be impacted '
           'per each category for all categories in the hazard layer. '
           'Currently there should be 3 categories in the hazard layer. After '
           'that it will show the result and the total amount of people that '
           'will be impacted for the hazard given.')
    limitation = tr('The number of categories is three.')

    # Configurable parameters
    defaults = get_defaults()
    parameters = OrderedDict([
        ('exposure id field', 'id'),
        ('exposure field', 'pop'),
        ('hazard field', 'haz_level'),
        ('categories', [NO_DATA, 1, 2, 3]),  # TODO (DB) allow
        # strings as cat
        ('postprocessors', OrderedDict([
            ('Gender', {'on': False}),
            ('Age', {
                'on': False,
                'params': OrderedDict([
                    ('youth_ratio', defaults['YOUTH_RATIO']),
                    ('adult_ratio', defaults['ADULT_RATIO']),
                    ('elderly_ratio', defaults['ELDERLY_RATIO'])])})]))])

    def run(self, layers):
        """Plugin for impact of population as derived by categorised hazard

        Input
          layers: List of layers expected to contain
              my_hazard: Vector layer of categorised hazard
              my_exposure: Vector layer of population data

        Counts number of people exposed to each category of the hazard

        Return
          Map of population exposed to high category
          Table with number of people in each category
        """

        # Identify hazard and exposure layers
        my_hazard = get_hazard_layer(layers)    # Categorised Hazard
        my_exposure = get_exposure_layer(layers)  # Population Vector
        my_question = get_question(my_hazard.get_name(),
                                my_exposure.get_name(),
                                self)

        my_exposure_keywords = my_exposure.get_keywords()
        my_exposure = self.add_density(my_exposure)

        my_impact = self.deintersect_exposure(my_exposure, my_hazard)
        my_impact = self.assign_hazard_level(my_impact, my_hazard)
        my_impact, max_impact_value = self.multiply_density_by_area(my_impact)
        my_impact_stats = self.generate_statistics(my_impact)
        my_impact_table, my_impact_summary, my_map_title = (
            self.generate_report(my_question, my_impact_stats))

        my_impact.style_info = categorical_style(
            self.parameters['hazard field'],
            self.parameters['categories'],
            self.NO_DATA,
            tr('No hazard'),
            self.parameters['exposure field'],
            max_impact_value)

        my_impact_keywords = {
            'impact_summary': my_impact_summary,
            'impact_table': my_impact_table,
            'map_title': my_map_title,
            'target_field': self.parameters['hazard field'],
            'statistics_type': 'class_count',
            'statistics_classes': self.parameters['categories']}
        my_impact_keywords.update(my_exposure_keywords)
        my_impact.keywords = my_impact_keywords

        return my_impact

    def add_density(self, exposure_layer):
        population_field = self.parameters['exposure field']

        # Get population data from layer
        if population_field in exposure_layer.get_attribute_names():
            D = []
            for att in exposure_layer.get_data():
                population = att[population_field]
                # FIXME (DB) area needs to be derived.
                # See hub.qgis.org/issues/9060
                density = population / float(att['area'])
                att['density'] = density
                D.append(att)
            exposure_layer.data = D

        else:
            raise RuntimeError(tr('No population field found'))
        return exposure_layer

    def deintersect_exposure(self, exposure_layer, hazard_layer):
        # FIXME (DB): Need to use the _prepare_polygon layer
        impact_layer = exposure_layer.copy()
        return impact_layer

    def assign_hazard_level(self, impact_layer, hazard_layer):
        impact_centroids_geom = convert_polygons_to_centroids(
            impact_layer).get_geometry()
        impact_field = self.parameters['hazard field']
        impact_attr = impact_layer.get_data()
        hazard_field = self.parameters['hazard field']
        hazard_attr = hazard_layer.get_data()
        hazard_geom = hazard_layer.get_geometry()

        for impact in impact_attr:
            impact[impact_field] = self.NO_DATA

        for hazard_index, hazard_poly in enumerate(hazard_geom):
            hazard_level = hazard_attr[hazard_index][hazard_field]
            for impact_index, impact_centroid in enumerate(
                    impact_centroids_geom):
                if is_inside_polygon(impact_centroid, hazard_poly):
                    if (hasattr(impact_attr[impact_index], impact_field) and
                        impact_attr[impact_index][impact_field] !=
                                self.NO_DATA):
                        raise RuntimeError(
                            tr('%s field already defined in impact layer') %
                            impact_field)
                    else:
                        impact_attr[impact_index][impact_field] = hazard_level

        impact_layer.data = impact_attr
        return impact_layer

    def multiply_density_by_area(self, impact_layer):
        impact_data = impact_layer.get_data()
        value_field = self.parameters['exposure field']
        max_impact_value = 0
        for index, geom in enumerate(impact_layer.get_geometry()):
            impact_attr = impact_data[index]
            new_impact = impact_attr['density'] * impact_attr['area']
            impact_attr[value_field] = new_impact
            if new_impact > max_impact_value:
                max_impact_value = new_impact

        return impact_layer, max_impact_value

    def generate_statistics(self, impact_layer):
        stats = {}
        initial_stats = {}
        for category in self.parameters['categories']:
            initial_stats[category] = 0
        impact_attr = impact_layer.get_data()
        impact_level_field = self.parameters['hazard field']
        impact_count_field = self.parameters['exposure field']
        for attr in impact_attr:
            # FIXME (DB): Change id to user configurable
            current_id = attr[self.parameters['exposure id field']]
            impact_level = attr[impact_level_field]
            try:
                stats[current_id][impact_level] += attr[impact_count_field]
            except KeyError:
                stats[current_id] = initial_stats.copy()
                stats[current_id][impact_level] = attr[impact_count_field]

        return stats

    def generate_report(self, question, stats):
        th = m.Row(m.Cell(m.ImportantText(
            self.parameters['exposure id field'])))
        for category in self.parameters['categories']:
            if category == self.NO_DATA:
                text = tr('No Hazard')
            else:
                text = '%s %s' % (tr('Category'), category)
            th.add(m.Cell(m.ImportantText(text)))
        table = m.Table(th)
        for name, categories in stats.iteritems():
            row = m.Row(name)
            for value in categories.values():
                row.add(str(value))
            table.add(row)

        map_title = tr('Impacted People by Category')
        report = m.Message(m.Heading(map_title, 5), table)
        report = report.to_html(suppress_newlines=True)
        impact_summary = report

        return report, impact_summary, map_title
