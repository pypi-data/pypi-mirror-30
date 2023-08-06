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



#### LEGACY ####
def get_ax_size_in_inch(fig, ax):
    ax_box_in_inch = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    ax_height, ax_width = ax_box_in_inch.height, ax_box_in_inch.width
    return ax_height, ax_width

def get_text_position(fig, ax, ha='left', va='top', pad_scale=1.0):
    """Return text position inside of the given axis"""
    ## Check and preprocess input arguments
    try: pad_scale = float(pad_scale)
    except: raise TypeError("'pad_scale should be of type 'float'")
        
    for arg in [va, ha]: 
        assert type(arg) is str
        arg = arg.lower() # Make it lowercase to prevent case problem.
    
    ## Get axis size in inches
    ax_height, ax_width = get_ax_size_in_inch(fig, ax)
    
    ## Construct inversion factor from inch to plot coordinate
    length_x = ax.get_xlim()[1] - ax.get_xlim()[0]
    length_y = ax.get_ylim()[1] - ax.get_ylim()[0]
    inch2coord_x = length_x / ax_width
    inch2coord_y = length_y / ax_height
    
    ## Set padding size relative to the text size
    #pad_inch = text_bbox_inch.height * pad_scale
    #pad_inch = fontsize_points * point2inch * pad_scale
    ax_length_geom_average = (ax_height * ax_width) ** 0.5
    pad_inch = ax_length_geom_average * 0.03 * pad_scale
    pad_inch_x, pad_inch_y = pad_inch, pad_inch
    
    pad_coord_x = pad_inch_x * inch2coord_x
    pad_coord_y = pad_inch_y * inch2coord_y
    
    if ha == 'left': pos_x = ax.get_xlim()[0] + pad_coord_x
    elif ha == 'right': pos_x = ax.get_xlim()[1] - pad_coord_x
    else: raise Exception("Unsupported value for 'ha'")
    
    if va in ['top','up','upper']: pos_y = ax.get_ylim()[1] - pad_coord_y
    elif va in ['bottom','down','lower']: pos_y = ax.get_ylim()[0] + pad_coord_y
    else: raise Exception("Unsupported value for 'va'")
    
    return pos_x, pos_y


