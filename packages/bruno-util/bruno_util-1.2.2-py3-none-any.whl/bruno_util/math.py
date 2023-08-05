import numpy as np


def center_by_mass(x, particle_axis=0):
    """Subtract center of mass (unweighted) from a collection of vectors
    corresponding to particles's coordinates."""
    shape = x.shape
    # center of mass is the average position of the particles, so average over
    # the particles
    centers_of_mass = np.mean(x, particle_axis)
    # tile the centers of mass for clean elementwise division
    # is there a way to do this faster by relying on numpy's array projection
    # semantics?
    tile_shape = [shape[i] if i == particle_axis else 1
                  for i in range(len(shape))]
    centers_of_mass = np.tile(centers_of_mass, tile_shape)
    return x - centers_of_mass

def locally_linear_fit(x, y, window_size=5, **kwargs):
    """Plots the local slope of y(x) using a moving average with the given
    window size. Passes kwargs onto ax.plot."""
    if window_size % 2 == 0:
        raise ValueError('window_size must be odd')
    if window_size < 3:
        raise ValueError('window_size must be at least 3, so that we have at'
                         ' least two points to fit at endpoints of array.')
    lenx = len(x)
    if lenx < 2:
        raise ValueError('Can\'t fit less than 2 points!')
    inc = int(window_size / 2)
    slope = np.zeros_like(x)
    for i in range(lenx):
        imin = np.max([0, i - inc])
        imax = np.min([lenx, i + inc + 1])
        xfit = x[imin:imax]
        yfit = y[imin:imax]
        to_fit = np.isfinite(xfit) & np.isfinite(yfit)
        if not np.any(to_fit):
            slope[i] = np.nan
        else:
            slope[i], intcpt, r_val, p_val, std_err = stats.linregress(xfit[to_fit], yfit[to_fit])
    ax = kwargs.pop('axes', None)
    if ax is not None:
        ax.plot(x, slope, **kwargs)
    return ax, slope
