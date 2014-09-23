# import_norway_osm.py:
# This script is used to import information from OpenStreetMap into MaPit.
# It takes KML data generated by bin/mapit_osm_to_kml, so you should run that first.
#
# Copyright (c) 2011 UK Citizens Online Democracy. All rights reserved.
# Email: matthew@mysociety.org; WWW: http://www.mysociety.org

import re
import xml.sax
from optparse import make_option

from django.core.management.base import LabelCommand
# Not using LayerMapping as want more control, but what it does is what this does
#from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import *
from django.utils import six
from django.utils.encoding import smart_str

from mapit.models import Area, Generation, Country, Type, CodeType, NameType
from mapit.management.command_utils import save_polygons, KML

class Command(LabelCommand):
    help = 'Import OSM data'
    args = '<OSM KML files generated by mapit_osm_to_kml (make sure fylke KML file is first)>'
    option_list = LabelCommand.option_list + (
        make_option('--commit', action='store_true', dest='commit', help='Actually update the database'),
    )

    def handle_label(self, filename, **options):
        current_generation = Generation.objects.current()
        new_generation = Generation.objects.new()
        if not new_generation:
            raise Exception("No new generation to be used for import!")

        print(filename)

        # Need to parse the KML manually to get the ExtendedData
        kml_data = KML()
        xml.sax.parse(filename, kml_data)

        code_type_osm = CodeType.objects.get(code='osm')
        code_type_n5000 = CodeType.objects.get(code='n5000')

        ds = DataSource(filename)
        layer = ds[0]
        for feat in layer:
            name = feat['Name'].value
            if not isinstance(name, six.text_type):
                name = name.decode('utf-8')
            name = re.sub('\s+', ' ', name)
            print("  %s" % smart_str(name))

            code = int(kml_data.data[name]['ref'])
            if code == 301: # Oslo ref in OSM could be either 3 (fylke) or 301 (kommune). Make sure it's 3.
                code = 3
            if code < 100: # Not particularly nice, but fine
                area_code = 'NFY'
                parent_area = None
                code_str = '%02d' % code
            else:
                area_code = 'NKO'
                code_str = '%04d' % code
                parent_area = Area.objects.get(id=int(code_str[0:2]))

            def update_or_create():
                try:
                    m = Area.objects.get(id=code)
                except Area.DoesNotExist:
                    m = Area(
                        id = code,
                        name = name,
                        type = Type.objects.get(code=area_code),
                        country = Country.objects.get(code='O'),
                        parent_area = parent_area,
                        generation_low = new_generation,
                        generation_high = new_generation,
                    )

                if m.generation_high and current_generation and m.generation_high.id < current_generation.id:
                    raise Exception("Area %s found, but not in current generation %s" % (m, current_generation))
                m.generation_high = new_generation

                g = feat.geom.transform(4326, clone=True)
                poly = [ g ]

                if options['commit']:
                    m.save()
                    for k, v in kml_data.data[name].items():
                        if k in ('name:smi', 'name:fi'):
                    	    lang = 'N' + k[5:]
                    	    m.names.update_or_create({ 'type': NameType.objects.get(code=lang) }, { 'name': v })
                    m.codes.update_or_create({ 'type': code_type_n5000 }, { 'code': code_str })
                    m.codes.update_or_create({ 'type': code_type_osm }, { 'code': int(kml_data.data[name]['osm']) })
                    save_polygons({ code : (m, poly) })

            update_or_create()
            # Special case Oslo so it's in twice, once as fylke, once as kommune
            if code == 3:
                code, area_code, parent_area, code_str = 301, 'NKO', Area.objects.get(id=3), '0301'
                update_or_create()

