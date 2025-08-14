# ROM dump from Casio FX-2500 / Elektronika MK-51 calculator

This is a repository with ROM contents of the Casio FX-2500 calculator
and its clone, Elektronika MK-51. Included is also experimental Python
code to read the die photos semi-automatically.

To run the code, you'll need to get the images from [Travis
Goodspeed's repository](https://github.com/travisgoodspeed/mk51fx2500)
and put them into a directory named `img`. Then you can run
`./read_rom.py`. It will read the images and write
`mk51fx2500rom.txt`.

Given coordinates of corners of rows and columns, the script computes
locations of the bits, takes neighborhoods of them and clusters them
into 2 clusters with k-means. Using given examples of a zero and a
one, it assigns values to these clusters.

Currently the code requires very well stitched images. Tearing,
irregular sharpness, lighting or spacing of rows and columns
introduces significant errors. The best results come from the [image
of the MK-51 ROM from an X
post](https://x.com/travisgoodspeed/status/1683224934967828480). Likely
only 6 bits are read incorrectly. The FX-2500 ROM images in the X
threads all have some tearing. In the areas around the tearings the
code tends to classify bits into those on the left and on the right of
the tear, instead of zeros and ones. The MK-51 image in Travis'
repository has a small tearing at the bottom that only affects bits
around it. The FX-2500 image in that repository has some sharpness and
other irregularities that make quite a few blocks wrong. Possibly
quite a few errors could be fixed by not using examples of a one and a
zero from one place in the photo for decoding all
areas. `combine_*_images` functions combine bits from two images using
manually selected mostly correct ranges.

The script includes a list of positions that are read incorrectly on
at least some images. This is used to apply fixes. The dump included
in this repository should be mostly or maybe even completely
correct. I managed to emulate this code and it seems to work
fine. I'll publish the emulator in another repository soon.

There are also a few functions that compute PCA. They are currently unused.
