# ROM dump from Casio fx-2500 / Elektronika MK-51 calculator

This is a repository with ROM contents of the Casio fx-2500 calculator
and its clone, Elektronika MK-51. Included is also experimental Python
code to read the die photos semi-automatically and some analysis of
the code.

## Extracting the ROM contents from die photos

To get the ROM contents from photos, you'll need to get the images
from [Travis Goodspeed's
repository](https://github.com/travisgoodspeed/mk51fx2500) and put
them into a directory named `img`:

```
mkdir -p img
cd img
ln -s ../../mk51fx2500/fx2500.bmp .
ln -s ../../mk51fx2500/mk51.tif .
```

Then you can run `./read_rom.py`. It will read the images and write
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
only 6 bits are read incorrectly. The fx-2500 ROM images in the X
threads all have some tearing. In the areas around the tearings the
code tends to classify bits into those on the left and on the right of
the tear, instead of zeros and ones. The MK-51 image in Travis'
GitHub repository has a small tearing at the bottom that only affects bits
around it. The fx-2500 image in that repository has some sharpness and
other irregularities that make quite a few blocks wrong. Possibly
at least some errors could be fixed by not using examples of a one and a
zero from one place in the photo for decoding all
areas. `combine_*_images` functions combine bits from two images using
manually selected mostly correct ranges.

The script includes a list of positions that are read incorrectly on
at least some images. This is used to apply fixes. The dump included
in this repository should be mostly or maybe even completely
correct. I managed to emulate this code and it seems to work
fine. I'll publish the emulator in another repository soon.

There are also a few functions that compute PCA. They are currently unused.

## Code analysis

`test_code.py` contains tests that verify assumptions about
subroutines in the ROM or about how the calculator stores its state in
the registers. To run it you need to initialize the submodule:

```
git submodule init
git submodule update
```

You can then run the tests with `./test_code.py`.

`explore_code.py` contains other code for analyzing the ROM. The
`describe_key_entries` function traces the code after pressing each
key (potentially preceded with the modifier keys) to detect the
function of this key combination.

## Calculator state

The calculator has 8 registers. Each register can store 15 4-bit
digits.

Floating point numbers on which the calculator operates are stored in
the following format:

* digits 12-2 store the significand, with digit 12 storing the most
  significant digit,
* digits 1 and 0 store the exponent, with digit 1 storing the tens
  digit,
* digit 13 stores the number sign in bit 3 (minus if set) and the
  exponent sign in bit 1 (minus if set). Other bits are 0.

If the exponent is 0, the decimal point is right after the most
significant digit.

Digit 14 is unused by floating point numbers. It is commonly used to
store other parts of the state, unrelated to the number stored in the
remaining digits of the register.

## State map

Here are known parts of the calculator state:

* R3[14]
  * bit 3: state of the INV key on fx-2500
  * bit 1: state of the F2 key on fx-48 and MK-38 or the F key on MK-51
  * bit 0: state of the F1 key on fx-48 and MK-38

* R4[13:0]: memory in the regular mode

* R4[14]
  * bits 1-0 store the trigonometric function mode:
    * 00: degrees
	* 01: radians
	* 10: gradians
  * bit 3: statistical mode if 1

* R7[14]: selected binary operation:
  * 2: root
  * 3: power
  * 4: division
  * 5: multiplication
  * 6: subtraction
  * 7: addition
