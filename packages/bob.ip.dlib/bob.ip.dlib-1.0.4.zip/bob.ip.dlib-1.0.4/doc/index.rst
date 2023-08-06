.. vim: set fileencoding=utf-8 :
.. Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
.. Fri 17 Jul 02:49:53 2016 CEST

.. _bob.ip.dlib:

========================
 Bob interface for dlib
========================

This package binds some functionalities from dlib.
For the moment we have the face detection and the face landmark detection binded.


User guide
===========


Face Detection
--------------

The most simple face detection task is to detect a single face in an image. This task can be achieved using a single command:

   >>> import bob.ip.dlib
   >>> import bob.io.base
   >>> import bob.io.base.test_utils
   >>> dlib_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
   >>> dlib_bounding_box, _ = bob.ip.dlib.FaceDetector().detect_single_face(dlib_color_image)
   >>> print (tuple((dlib_bounding_box.topleft, dlib_bounding_box.bottomright)))
   ((118, 68), (342, 292))

.. plot:: plot/plot_single_faces.py
   :include-source: False



Multiple Face Detection
-----------------------

The detection of multiple faces can be achieved with a single command:

.. doctest:: dlibtest

   >>> import bob.ip.dlib
   >>> import bob.io.base
   >>> import bob.io.base.test_utils
   >>> dlib_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('multiple-faces.jpg', 'bob.ip.dlib'))
   >>> dlib_bounding_box, _ = bob.ip.dlib.FaceDetector().detect_all_faces(dlib_color_image)
   >>> print ((dlib_bounding_box[0].topleft, dlib_bounding_box[0].bottomright))
   ((163, 179), (238, 255))

.. plot:: plot/plot_multiple_faces.py
   :include-source: False


Landmark detection
------------------

The detection of landmarks can be done as the following:

.. doctest:: dlibtest

   >>> import bob.ip.dlib
   >>> import bob.io.base
   >>> import bob.io.base.test_utils
   >>> dlib_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
   >>> points = bob.ip.dlib.DlibLandmarkExtraction(bob_landmark_format=True)(dlib_color_image)
   >>> print (points['reye'])
   (173, 222)

.. plot:: plot/plot_landmarks.py
   :include-source: False



Face genometric normalization using the Landmark detection
----------------------------------------------------------

The detection of landmarks can be done as the following:

.. doctest:: dlibtest

   >>> import bob.ip.dlib
   >>> import bob.io.base
   >>> import bob.io.base.test_utils
   >>> import bob.ip.facedetect
   >>> dlib_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('image_r10.hdf5', 'bob.ip.dlib'))
   >>> normimage = bob.ip.dlib.AlignDLib()(dlib_color_image, bob.ip.facedetect.BoundingBox((0,0),(116,116)))


.. plot:: plot/plot_align_faces.py
   :include-source: False





Python API
============

.. toctree::
   :maxdepth: 2

   py_api
   references
