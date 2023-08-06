from matplotlib.colors import LinearSegmentedColormap


def create_colormap(color):
    """
    Creates a colormap to simulate a false-colored monochromatic light source on a black background.

    :param color:   any value recognized by Matplotlib as a color

    """
    return LinearSegmentedColormap.from_list('custom_colormap', ['black', color])


green = create_colormap('green')
magenta = create_colormap('magenta')
