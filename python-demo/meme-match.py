"""
This file demonstrates how to load in a set of images, perceputally hash them, and private match them between two parties without any unencrypted sharing or trusted third party needed.
"""

import requests
from PIL import Image
import imagehash
from io import BytesIO


DISPLAY_IMAGES = True
if DISPLAY_IMAGES:
    from IPython.display import display


def download_and_hash(urls):
    """This will download the images from a list of urls and return a list of hashes. We use the imagehash library to compute the perceptual hashes for convenience."""
    hashes = []
    for url in urls:
        try:
            response = requests.get(url)
            image = Image.open(BytesIO(response.content))
            hashes.append(imagehash.phash(image))
            if DISPLAY_IMAGES:
                display(image)
        except Exception as e:
            print(f"Failed to process {url}. Error: {str(e)}")
            hashes.append(None)
    return hashes


memes_A = ["https://i.kym-cdn.com/photos/images/masonry/000/581/296/c09.jpg", "https://i.kym-cdn.com/photos/images/newsfeed/000/663/989/522.jpg", "https://i.kym-cdn.com/photos/images/newsfeed/000/406/325/b31.jpg", "https://i.kym-cdn.com/photos/images/newsfeed/002/557/963/a95.jpg"] # doge original, Philosoraptor 1, Grumpy Cat Original, Balenciaga Pope
memes_B = ["https://i.kym-cdn.com/photos/images/masonry/000/661/142/c03.jpg", "https://i.kym-cdn.com/photos/images/newsfeed/000/154/802/bc6.jpg", "https://i.kym-cdn.com/photos/images/newsfeed/000/001/962/1241222446876.jpg", "https://i.kym-cdn.com/photos/images/newsfeed/000/406/325/b31.jpg"] # Doge edited, Philosoraptor 2, Philosoraptor 3, Grumpy Cat Original

hashes_A = download_and_hash(memes_A)
hashes_B = download_and_hash(memes_B)



# Private match the hashes
# Using https://github.com/OpenMined/PSI/blob/master/private_set_intersection/python/
# this can be tricky to install
import openmined_psi as psi

def dup(do, msg, dst):
    if not do:
        return msg
    buff = msg.SerializeToString()
    dst.ParseFromString(buff)
    return dst


reveal_intersection = False
duplicate = True
c = psi.client.CreateWithNewKey(reveal_intersection)
s = psi.server.CreateWithNewKey(reveal_intersection)


fpr = 1.0 / (1000000000)
setup = dup(
    duplicate, s.CreateSetupMessage(fpr, len(A_geohashes), B_geohashes), psi.ServerSetup()
)
request = dup(duplicate, c.CreateRequest(A_geohashes), psi.Request())
resp = dup(duplicate, s.ProcessRequest(request), psi.Response())


if reveal_intersection:
    intersection = c.GetIntersection(setup, resp)
    iset = set(intersection)
    print("Intersection: {}".format(iset))
else:
    intersection = c.GetIntersectionSize(setup, resp)
    print("Intersection size: {}".format(intersection))

print("True overlap: {}".format(set(A_locations).intersection(set(B_locations))))