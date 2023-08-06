from __future__ import division, print_function, unicode_literals, absolute_import

import numpy as np

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
except ImportError:
    FigureCanvasAgg = None

from .utility import image_data_mode, setup_uint8
from .compression import compress


def figure_to_image(fig, fmt='raw', dpi=None, close_figure=True):
    """Generate compressed-image representation of a Matplotlib figure.
    Nothing gets displayed to the screen.

    See here for partial inspiration: https://gist.github.com/rduplain/1641344
    """

    if not FigureCanvasAgg:
        raise ImportError('Matplotlib is not installed')

    if dpi:
        dpi_original = fig.get_dpi()
        fig.set_dpi(dpi)

    # Render figure to buffer as uncompressed RGBA
    canvas = FigureCanvasAgg(fig)
    buff, (num_samples, num_lines) = canvas.print_to_buffer()
    num_colors = 4

    # Grab data from buffer
    data = np.frombuffer(buff, dtype=np.uint8)
    data.shape = num_lines, num_samples, num_colors

    # Close the figure
    if close_figure:
        plt.close(fig)


    mode = image_data_mode(data)
    if mode.lower() != 'rgba':
        raise ValueError('Unexpected image mode: {:s}'.format(mode))

    if dpi:
        fig.set_dpi(dpi_original)

    if fmt == 'raw':
        # Return uncomprressed image byte data
        return data
    else:
        # Return compressed data
        return compress(data, mode=mode, fmt=fmt)



def figure_to_file(fig, fname, fmt='png', dpi=None, close_figure=True):
    """Write selected figure to image file
    """
    b, e = os.path.splitext(fname)

    if fmt:
        e = '.' + fmt.lower()
    else:
        fmt = e[1:].lower()

    f_out = b + e

    data_comp = figure_to_image(fig, fmt=fmt, dpi=dpi, close_figure=close_figure)

    with open(f_out, 'wb') as fp:
        fp.write(data_comp)

    # Done

#------------------------------------------------

if __name__ == '__main__':
    pass

