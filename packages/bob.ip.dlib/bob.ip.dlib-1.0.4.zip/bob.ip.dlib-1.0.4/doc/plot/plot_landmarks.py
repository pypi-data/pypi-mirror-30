import bob.io.base
import bob.io.image
import bob.io.base.test_utils
import bob.ip.dlib
import pkg_resources
import os
from matplotlib import pyplot
import bob.ip.draw

#print "###################################"
#print os.path.join(pkg_resources.resource_filename(__name__, 'data'), 'multiple-faces.jpg')

# detect multiple dlib
image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
bob_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
bounding_box, _ = bob.ip.dlib.FaceDetector().detect_single_face(image)

# landmarks
detector = bob.ip.dlib.DlibLandmarkExtraction()
points = detector(image)

bob_detector = bob.ip.dlib.DlibLandmarkExtraction(bob_landmark_format=True)
bob_points = bob_detector(bob_image)

for p in points:
    bob.ip.draw.plus(image, p, radius=10, color=(255, 0, 0))

for p in bob_points:
    bob.ip.draw.plus(bob_image, bob_points[p], radius=10, color=(255, 0, 0))

# face detections
bob.ip.draw.box(image, bounding_box.topleft, bounding_box.size, color=(255, 0, 0))


ax = pyplot.subplot(1, 2, 1)
ax.set_title("Dlib landmarks")
pyplot.imshow(bob.ip.dlib.utils.bob_to_dlib_image_convertion(image, change_color=False))
pyplot.axis('off')

ax = pyplot.subplot(1, 2, 2)
ax.set_title("Dlib landmarks for Bob")
pyplot.imshow(bob.ip.dlib.utils.bob_to_dlib_image_convertion(bob_image, change_color=False))
pyplot.axis('off')

