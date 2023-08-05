pygcj
===================

GCJ02 and wgs84 transform

increase the accuracy by control points

Generate Control Points
-----------------------

Default gcp file’s grid interval is 1 degree. If you want generate new
gcp file,please run:

.. code:: shell

    python generate_gcp.py

Transform between WGS84 and GCJ02
---------------------------------

.. code:: python

    from pygcj import GCJProj
    trans = GCJProj()
    # wgs84 to gcj
    gcj_lat, gcj_lon = trans.wgs_to_gcj(45.2,112.8)

    # gcj to wgs84
    wgs_lat, wgs_lon = trans.gcj_to_wgs(45.2,112.8)

    # gcj to wgs84 and specific threshold
    wgs_lat, wgs_lon = trans.gcj_to_wgs(45.2,112.8,0.00000001)

accuracy test (use default control points)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    origional:
    distance mean: 347.554477357
    distance stdev: 164.494315519

    eviltransform:
    distance mean: 3.39331251552
    distance stdev: 2.6602095071

    pygcj.gcj_to_wgs():
    distance mean: 0.395794995772
    distance stdev: 0.571923075943


