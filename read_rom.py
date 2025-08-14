import imageio
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage
import typing

from dataclasses import dataclass

NROWS = 16 * 5
NCOLS = 16 * 22

FIXES = {
    (0, 12): 0,
    (1, 15): 0,
    (1, 147): 0,
    (2, 222): 0,
    (3, 13): 0,
    (5, 12): 0,
    (5, 13): 0,
    (5, 293): 1,
    (6, 233): 0,
    (7, 15): 0,
    (9, 224): 1,
    (11, 160): 0,
    (13, 20): 1,
    (14, 97): 1,
    (14, 224): 1,
    (15, 195): 0,
    (15, 275): 0,
    (15, 286): 0,
    (16, 224): 0,
    (16, 225): 0,
    (16, 226): 0,
    (16, 227): 0,
    (16, 229): 0,
    (16, 244): 0,
    (16, 248): 0,
    (17, 225): 0,
    (17, 226): 0,
    (17, 227): 0,
    (17, 228): 0,
    (17, 229): 0,
    (17, 232): 0,
    (17, 233): 0,
    (17, 234): 0,
    (17, 235): 0,
    (17, 237): 0,
    (17, 239): 0,
    (17, 240): 0,
    (18, 225): 0,
    (18, 226): 0,
    (18, 228): 0,
    (20, 225): 0,
    (20, 228): 0,
    (21, 226): 0,
    (21, 227): 0,
    (23, 109): 0,
    (25, 63): 0,
    (26, 62): 0,
    (26, 63): 0,
    (27, 63): 0,
    (28, 59): 0,
    (28, 60): 0,
    (28, 61): 0,
    (28, 63): 0,
    (30, 59): 0,
    (30, 61): 0,
    (30, 62): 0,
    (30, 63): 0,
    (30, 113): 0,
    (35, 224): 0,
    (37, 248): 0,
    (39, 60): 1,
    (48, 331): 0,
    (58, 159): 1,
    (60, 325): 0,
    (61, 168): 0,
    (70, 316): 0,
}

@dataclass
class ImageDesc:
    path: str
    width: int
    height: int
    rows_corners: typing.Any  # TODO: more accurate type?
    cols_corners: typing.Any

@dataclass
class Image:
    desc: ImageDesc
    img: np.ndarray
    gray: np.ndarray

MK51_ROM = ImageDesc(
    path = "img/mk51_rom_die.jpg",
    width = 4096,
    height = 1396,
    rows_corners = [[(510, 197.5), (3743.1, 202.0)],
                    [(494.6, 1108.5), (3757.0, 1113.6)]],
    cols_corners = [[(534.7, 190.2), (3712.7, 195.3)],
                    [(533.5, 1128.0), (3712.4, 1120.8)]])

# From https://x.com/travisgoodspeed/status/1685675366352896000
FX2500_ROM = ImageDesc(
    path = "img/fx2500_rom_die.jpeg",
    width = 4096,
    height = 1643,
    rows_corners = [[(635.8, 516.4), (3610.7, 466.0)],
                    [(663.2, 1303.0), (3636.4, 1253.3)]],
    cols_corners = [[(664.3, 510.3), (3583.8, 458.9)],
                    [(677.6, 1320.2), (3597.6, 1260.9)]])

# From https://x.com/travisgoodspeed/status/1685486408251707392
FX2500_ROM_2 = ImageDesc(
    path = "img/fx2500_rom_die2.jpeg",
    width = 4096,
    height = 1428,
    rows_corners = [[(539.2, 205.4), (3858.0, 306.8)],
                    [(527.8, 1087.5), (3844.0, 1191.3)]],
    cols_corners = [[(571.2, 200.2), (3828.8, 299.1)],
                    [(543.2, 1109.8), (3801.4, 1197.3)]])

# From https://github.com/travisgoodspeed/mk51fx2500
FX2500_GH = ImageDesc(
    path = "img/fx2500.bmp",
    width = 6929,
    height = 2306,
    rows_corners = [[(869.7, 438.1), (6899.2, 333.2)],
                    [(924.3, 2036.3), (6925.1, 1935.0)]],
    cols_corners = [[(926.9, 423.3), (6846.6, 321.0)],
                    [(955.5, 2071.7), (6874.5, 1946.7)]])

# From https://github.com/travisgoodspeed/mk51fx2500
MK51_GH = ImageDesc(
    path = "img/mk51.tif",
    width = 9409,
    height = 3210,
    rows_corners = [[(1250.3, 483.5), (8606.1, 492.1)],
                    [(1215.1, 2556.4), (8638.0, 2567.8)]],
    cols_corners = [[(1306.3, 465.6), (8536.5, 477.1)],
                    [(1303.2, 2600.1), (8537.1, 2583.3)]])


def load_image(desc):
    img = imageio.imread(desc.path)
    # gray = np.mean(img, axis=-1)
    gray = scipy.ndimage.gaussian_filter(
        scipy.ndimage.laplace(np.mean(img, axis=-1)), 2)
    return Image(desc, img, gray)

def bit_pos(desc, i, j):
    def interp(a, b, k, n):
        return a + (b - a) * k / n

    def point(a, b, k, n):
        return tuple([interp(a[t], b[t], k, n - 1) for t in range(2)])

    def intersection(a, b, c, d):
        m = np.array([
            [b[0] - a[0], c[0] - d[0]],
            [b[1] - a[1], c[1] - d[1]]])
        r = np.array([c[0] - a[0], c[1] - a[1]])
        t = np.linalg.solve(m, r)
        return (a[0] * (1 - t[0]) + b[0] * t[0],
                a[1] * (1 - t[0]) + b[1] * t[0])

    return intersection(
        point(desc.rows_corners[0][0], desc.rows_corners[1][0], i, NROWS),
        point(desc.rows_corners[0][1], desc.rows_corners[1][1], i, NROWS),
        point(desc.cols_corners[0][0], desc.cols_corners[0][1], j, NCOLS),
        point(desc.cols_corners[1][0], desc.cols_corners[1][1], j, NCOLS))


def get_area(image, i, j, r, norm=False):
    if norm:
        neighb = get_area(image, i, j, 10 * r, norm=False)
        area = get_area(image, i, j, r, norm=False)
        return (area - np.mean(neighb)) / np.std(neighb)

    x, y = bit_pos(image.desc, i, j)
    res = scipy.ndimage.affine_transform(
        image.gray, [1, 1], offset=(y - r, x - r), output_shape=(2 * r, 2 * r),
        prefilter=False)
    return res


def get_random_bits(image):
    n = 500
    rows = np.random.randint(0, NROWS, n)
    cols = np.random.randint(0, NCOLS, n)
    res = []
    for r, c in zip(rows, cols):
        res.append(get_area(image, r, c, 3).flatten())
    return np.array(res)


def pca_bits(bits):
    m = np.mean(bits, axis=0)
    b = bits - m
    u, s, v = np.linalg.svd(b)
    return v[0], v[1]


def get_pc(image):
    rbits = get_random_bits(image)
    plt.imshow(rbits); plt.show()
    c1, c2 = pca_bits(rbits)
    m = np.mean(rbits, axis=0)
    pr1 = np.dot(rbits - m, c1)
    plt.plot(range(len(pr1)), pr1, 'x'); plt.show()
    return m, c1

M = np.array([189.65874425, 163.90641334, 155.98414646, 158.16136599,
       158.93950686, 170.83007093, 193.29812701, 168.67812829,
       159.61633928, 161.34572598, 163.48869532, 175.59516817,
       198.06160232, 177.4694989 , 170.91687956, 173.10009711,
       173.81137047, 182.45741622, 200.59431612, 182.49109655,
       177.7909631 , 180.30738711, 179.89019102, 186.3467299 ,
       199.84203548, 179.961734  , 173.82122801, 176.15399925,
       176.89570041, 185.14422612, 195.66970369, 171.57461742,
       162.99096766, 164.95080829, 167.25632738, 179.27765334])
C1 = np.array([-0.04704893, -0.09579545, -0.22798194, -0.28930118, -0.18566232,
              -0.0665317 ,  0.0358345 ,  0.01878957, -0.1315961 , -0.20346627,
              -0.07541347,  0.04435633,  0.13190374,  0.2027167 ,  0.11167305,
              0.0523622 ,  0.14819832,  0.19398221,  0.17839499,  0.29460418,
              0.24172098,  0.19393085,  0.26916633,  0.27169814,  0.15971022,
              0.23307345,  0.14465973,  0.0929638 ,  0.19459791,  0.23811151,
              0.07380907,  0.05872097, -0.08331383, -0.1459898 , -0.01573018,
              0.10222208])
THR = 27

def read_bits(image):
    res = np.zeros((NROWS, NCOLS), dtype=bool)
    for i in range(NROWS):
        for j in range(NCOLS):
            ar = get_area(image, i, j, 3).flatten()
            # TODO: classify 0/1 based on one example
            res[i, j] = np.dot(ar - M, C1) < THR
    return res.astype(int)

def dist_from_means(bits, m):
    d = []
    for i in range(2):
        d.append(np.sum(np.square(bits - m[i]), axis=-1))
    return np.array(d)

def kmeans(bits, m0, m1):
    m = [m0, m1]
    for step in range(10):
        d = dist_from_means(bits, m)
        closer = np.argmin(d, axis=0)
        print(np.count_nonzero(closer))
        m = []
        for i in range(2):
            m.append(np.mean(bits[closer == i], axis=0))
    return tuple(m)

def read_with_kmeans_on_tile(image, start_row, start_col, limit_row, limit_col):
    r = image.desc.width * 5 // 4096
    norm = False
    bits = []
    nr = limit_row - start_row
    nc = limit_col - start_col
    for i in range(start_row, limit_row):
        for j in range(start_col, limit_col):
            bits.append(get_area(image, i, j, r, norm=norm).flatten())
    bits = np.array(bits)
    ex1 = get_area(image, 1, 1, r, norm=norm).flatten()
    ex0 = get_area(image, 2, 1, r, norm=norm).flatten()
    m = kmeans(bits, ex0, ex1)
    d = dist_from_means(bits, m)

    ind = ([], [])
    for i in range(2):
        v = d[i] < d[1 - i]
        counts, bins = np.histogram(d[i][v], bins=1000)
        #plt.hist(bins[:-1], bins, weights=counts); plt.show()
        ind1 = np.unravel_index(np.argsort(d[i]), (nr, nc))
        ind[0].extend(ind1[0][-50:])
        ind[1].extend(ind1[1][-50:])

    #plt.plot(range(d.shape[1]), d[0] - d[1], 'o'); plt.show()
    return np.argmin(d, axis=0).reshape(nr, nc), ind


def read_with_kmeans(image):
    # TODO: check how good this is, maybe try with normalization
    # gray = scipy.ndimage.gaussian_filter(scipy.ndimage.laplace(np.mean(img, axis=-1)), 2)
    parts = []
    n = NROWS // 16
    m = NCOLS // 16
    for i in range(n):
        p1 = []
        for j in range(m):
            start_row = NROWS * i // n
            limit_row = NROWS * (i + 1) // n
            start_col = NCOLS * j // m
            limit_col = NCOLS * (j + 1) // m
            v, outl = read_with_kmeans_on_tile(image, start_row, start_col,
                                               limit_row, limit_col)
            p1.append(v)
        parts.append(np.concatenate(p1, axis=1))
    return np.concatenate(parts, axis=0)

def dump_str(read_bits):
    rows = []
    for i in range(16):
        for j in range(4):
            rows.append("".join([str(b) for b in read_bits[i * 5 + j]]))
    return "\n".join(rows)

def show_bits(image, bits, v):
    plt.imshow(image.img)
    points = []
    for i in range(NROWS):
        for j in range(NCOLS):
            if bits[i, j] == v:
                points.append(bit_pos(image.desc, i, j))
    plt.plot([p[0] for p in points], [p[1] for p in points], 'o', alpha=0.3)
    plt.show()

def show_outliers(image, bits, outliers, v):
    plt.imshow(image.img)
    points = []
    for i, j in zip(*outliers):
        if bits[i, j] == v:
            points.append(bit_pos(image.desc, i, j))
    plt.plot([p[0] for p in points], [p[1] for p in points], 'o', alpha=0.3)
    plt.show()

def combine_fx_images():
    img1 = load_image(FX2500_ROM)
    bits1 = read_with_kmeans(img1)
    img2 = load_image(FX2500_ROM_2)
    bits2 = read_with_kmeans(img2)
    return np.concatenate((bits2[0:16], bits1[16:]), axis=0)

def apply_fixes(bits):
    res = bits.copy()
    n = 0
    for p, v in FIXES.items():
        if res[p] != v: n += 1
        res[p] = v
    print(f"Fixed {n} bits")
    return res

def print_fix_template(mask):
    for p in np.argwhere(mask):
        print(f"({p[0]}, {p[1]}): ,")

def show_selected_bit_versions(mask, *images):
    for p in np.argwhere(mask):
        print(p)
        fig, axes = plt.subplots(nrows=1, ncols=len(images))
        for ax, img in zip(axes, images):
            bp = bit_pos(img.desc, p[0], p[1])
            ibp = (int(bp[0]), int(bp[1]))
            ax.imshow(img.img[ibp[1] - 10:ibp[1] + 10,
                              ibp[0] - 10:ibp[0] + 10])
        plt.show()
