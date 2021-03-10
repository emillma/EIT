import numba as nb
import numpy as np
import time


@nb.njit('float64[:,:](float64[:,:], float64[:,:])', cache=True, parallel=True)
def convolve_fast(img, kernel):
    out = np.zeros(img.shape)
    for i in nb.prange(img.shape[0]):
        for j in nb.prange(img.shape[1]):
            for m in range(kernel.shape[0]):
                for n in range(kernel.shape[1]):
                    if i+m < img.shape[0] and j+n < img.shape[1]:
                        out[i, j] += (
                            out[i+m, j+n] * kernel[m, n]
                        )
    return out


def convolve(img, kernel):
    out = np.zeros(img.shape)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            for m in range(kernel.shape[0]):
                for n in range(kernel.shape[1]):
                    if i+m < img.shape[0] and j+n < img.shape[1]:
                        out[i, j] += (
                            out[i+m, j+n] * kernel[m, n]
                        )
    return out


img = np.random.random((1000, 1000))
kernel = np.random.random((5, 5))
# t0 = time.time()
# a = convolve(img, kernel)
# print(time.time()-t0)

t0 = time.time()
a = convolve_fast(img, kernel)
print(time.time()-t0)
