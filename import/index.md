---
layout: default
title: Importing data
---

Importing data into MapIt
=========================

If you have some KML or Shapefiles of some boundaries, you can load these into
MapIt directly. The import script is used to import boundaries of a certain
'type' at once (for example, all county councils, or all kommunes), which is
generally how boundary data is distributed.

We'll assume that you are using a locally running instance of MapIt. If not
please change the URLs to match your setup. For the below, let us assume you
are in France, and you are importing boundary data of arrondissements
(districts) from a source called 'BoundaryInfo'.

Set things up
-------------

1. Install MapIt as per the [installation instructions](../install/).
2. Start the dev server.
3. We're assuming that your database is empty. If this is not the case you may 
   have some conflicts.
4. Either visit the admin at http://127.0.0.1:8000/admin and add a generation
   there, with description 'Initial import', or run the following (which does
   the same thing):

        ./manage.py mapit_generation_create --desc='Initial import' --commit

5. (optional) You can add the various Types in the admin interface now, or be
   prompted for them when you run the import script. If you want to use the
   admin interface, we'll want a country France, with a one letter code F; a
   name type (as you can have multiple names), describing the source of this name
   (so perhaps 'binfo' with description 'BoundaryInfo'); and an appropriate area
   type, such as ARR "Arrondissements".

Import the kml
--------------

There is an import script that will look at the KML file and create entries from
it. We'll call it as follows:

{% highlight bash %}
./manage.py mapit_import     \
    --country_code    F      \
    --generation_id   1      \
    --area_type_code  ARR    \
    --name_type_code  binfo  \
    --commit                 \
    /tmp/data/ArrondissementsData.kml
{% endhighlight %}

You will be prompted to provide descriptions for the codes if you haven't
created them; we can use "BoundaryInfo" for binfo, "Arrondissements" for ARR,
and "France" for 'F'.

You can repeat the above line for different data files, changing the path to
the file and the `--area_type_code` to suit your import. You may also need to
use a different value for `--generation_id` if this is not a fresh MapIt
install.

If you want to try the import without committing to the database don't specify
the `--commit` switch.

Activate the generation
-----------------------

Once you are happy that the data is correct activate the generation in the
admin interface, or run:

    ./manage.py mapit_generation_activate --commit


Shapefiles
----------

The same import script can import shapefiles too. You might need the extra
command line parameter of `--encoding` if the encoding of the shapefile is not
UTF-8 (GADM is sometimes ISO-8859-1, for example).

You will also need to know which field in the shapefile contains the name of
the area, and specify it with the `--name_field` parameter. If you run without
this parameter and 'Name' doesn't work, the program will output a list of
possible choices that it could be.
