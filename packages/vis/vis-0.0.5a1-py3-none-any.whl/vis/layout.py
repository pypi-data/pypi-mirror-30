"""Tools for (hopefully) fancy layout in plotting"""

default_text_relative_padding = 0.05


def get_axes_ratio(ax):
    """Return height / width ratio of the given Axes object.
    
    The ratio is calculated in 'display coordinate',
    defined in matplotlib document on transformation.
    Thus, the calculated ratio is what one would feels when the Axes
    is displayed to the her/him.
    """
    ax_bbox_points_in_fig_coord = ax.get_position().get_points()
    ax_bbox_points_in_display_coord = [
            ax.figure.transFigure.transform(point) for point in ax_bbox_points_in_fig_coord ]
    lower_left_coord, upper_right_coord = ax_bbox_points_in_display_coord
    ax_bbox_dimension_in_display_coord = upper_right_coord - lower_left_coord
    width, height = ax_bbox_dimension_in_display_coord
    ratio = height / width
    return ratio


def get_text_position_in_ax_coord(ax, pos, scale=default_text_relative_padding):
    """Return text position corresponding to given 'pos'.
    The text alignment in the bounding box should be set accordingly 
    in order to have a good-looking layout.
    This corresponding text alignment can be obtained by 'get_text_alignment'
    or 'get_text_position_and_inner_alignment' function.
    """
    ratio = get_axes_ratio(ax)
    x, y = scale ,scale
    if ratio > 1: # vertical is longer
        y /= ratio
    elif 0 < ratio: # 0 < ratio <= 1
        x *= ratio
    pos = pos.lower()
    if pos == 'nw': y = 1 - y
    elif pos == 'ne': x, y = 1 - x, 1 - y
    elif pos == 'sw': pass
    elif pos == 'se': x = 1 - x
    else: raise ValueError("Unknown value for 'pos': %s" % (str(pos)))
        
    return x, y


def get_text_alignment(pos):
    """Return 'verticalalignment'('va') and 'horizontalalignment'('ha') for given 'pos' (position)"""
    pos = pos.lower()  # to make it case insensitive
    va, ha = None, None
    if pos == 'nw': va, ha = 'top', 'left'
    elif pos == 'ne': va, ha = 'top', 'right'
    elif pos == 'sw': va, ha = 'bottom', 'left'
    elif pos == 'se': va, ha = 'bottom', 'right'
    else: raise ValueError("Unknown value for 'pos': %s" % (str(pos)))
    return {'va':va, 'ha':ha}


def get_text_position_and_inner_alignment(ax, pos, scale=default_text_relative_padding):
    """Return text position and its alignment in its bounding box.
    
    The returned position is given in Axes coordinate,
    as defined in matplotlib documentation on transformation.

    The returned alignment is given in dictionary,
    which can be put as a fontdict to text-relavent method.
    """
    xy = get_text_position_in_ax_coord(ax,pos,scale=scale)
    alignment_fontdict = get_text_alignment(pos)
    return xy, alignment_fontdict

