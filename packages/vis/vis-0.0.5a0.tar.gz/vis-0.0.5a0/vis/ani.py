import numpy as np
from matplotlib.animation import TimedAnimation

from .ntype import is_real_number, is_integer_valued_real
from .plot import plot_1D, plot_2D
from .indicator import Progress_Bar


from matplotlib.animation import FFMpegWriter
default_writer = FFMpegWriter(fps=20, bitrate=500, extra_args=['-vcodec','libx264'])

from shutil import which
from matplotlib import rcParams


## [NOTE] One need to know whether one is inside of the IPython
from IPython.display import HTML


def check_whether_we_have_ffmpeg():
    ## [NOTE] Modify this part by using 'try-except' statements
    ffmpeg_abspath = which(rcParams['animation.ffmpeg_path'])
    if ffmpeg_abspath is None:
        print("[INFO] No 'ffmpeg' was found during importing %s" % (__file__))
        print("[INFO] Please specify path to 'ffmpeg' by entering:")
        print(r">>> from matplotlib import rcParams")
        print(r">>> rcParams['animation.ffmpeg_path'] = 'C:\\Users\\username\\path\\to\\ffmpeg.exe'")
        print("[INFO] Then, the animation will be properly rendered.")
    else:
        print("[INFO] Using 'ffmpeg' at '%s'" % (ffmpeg_abspath))

check_whether_we_have_ffmpeg()


def estimate_global_norm_range(N_t, func, num_of_sample=10, func_args={},
                               percen_lower=1, percen_upper=99, show_progress=True):
    """Return estimated global range for 2D (pcolormesh-like) plot.

    ## Returns:
    - vmin
    - vmax
    """

    ## Check input arguments
    for arg in [N_t, num_of_sample]:
        assert is_integer_valued_real(arg)
    assert num_of_sample <= N_t
    for arg in [percen_lower, percen_upper]:
        assert is_real_number(arg)
        assert (0 <= arg) and (arg <= 100)
    assert percen_lower <= percen_upper

    assert callable(func)
    assert type(func_args) is dict

    assert type(show_progress) is bool

    sample_indices = np.random.randint(0, N_t-1, num_of_sample)

    if show_progress:
        progress_bar = Progress_Bar(num_of_sample)
    uppers = []
    lowers = []

    for idx, sample_index in enumerate(sample_indices):
        frame_data = func(sample_index, **func_args)
        lowers.append(np.percentile(frame_data, percen_lower))
        uppers.append(np.percentile(frame_data, percen_upper))
        if show_progress:
            progress_bar.print(idx)

    vmin = np.percentile(lowers, percen_lower)
    vmax = np.percentile(uppers, percen_upper)

    return vmin, vmax


def process_frames_argument(frames):
    """
    Check and process 'frames' argument
    into a proper iterable for an animation object

    ## Arguments
    # frames
    : a seed for an integer-type iterable that is used as a sequence of frame indices
    - if integer or integer-valued float (e.g. 1.0):
        The 'frames' is interpreted as the number of total frames
        and the sequence frame indices becomes [ 0, 1, 2, ..., 'frames' - 1 ]
        which is equivalent to range('frames').
    - if array-like:
        All elements in 'frames' should be integer or integer-valued float.
        Then, the 'frames' itself is used as a sequence of frame indices.
    """

    result = None
    if np.iterable(frames):
        try: frames_arr = np.array(frames)
        except: raise TypeError("'frames' should be convertable to numpy.array")
        for idx in range(len(frames_arr)):
            frame_idx = frames_arr[idx]
            assert is_real_number(frame_idx)
            assert int(frame_idx) == frame_idx
            frames_arr[idx] = int(frame_idx)
        #self.frames = frames_arr
        result = frames_arr
    elif is_real_number(frames):
        assert int(frames) == frames
        frames = int(frames)
        #self.frames = range(frames)
        result = range(frames)

    return result



class Animate_Base(TimedAnimation):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        """Save animation into a movie file.
        
        [NOTE] If 'writer' is not specified, default writer defined in this module 
        will be used to generate the movie file.

        [TODO] Implement docstring inheritance.
        """
        writer = None
        if 'writer' in kwargs.keys():
            writer = kwargs.pop('writer')
        else: writer = default_writer
        super().save(*args, **kwargs, writer=writer)


    def show(self, temp_file_name = 'ani.mp4', **kwargs):
        """
        
        ## Arguments:
        - 'args' and 'kwargs' will be passed to 'self.save()'
        """
        ## [NOTE] Make this method as a method of base class.

        ## [NOTE] This should be modified to prevent erasing other existing file with the same name.
       	assert type(temp_file_name) is str
 
        self.save(temp_file_name, **kwargs)

        ## [NOTE] Consider removing the temp file.
        
        ## [NOTE] Implement automatic showing.
        return HTML("""
        <video width="%d" height="%d" controls>
          <source src="%s" type="video/mp4">
          </video>
          """ % (640, 300, temp_file_name))



class Animate_1D(Animate_Base):
    def __init__(self, x, func, frames, *plot_args, func_args=(), func_kwargs={}, **plot_kwargs):

        assert type(func_args) is tuple
        self.func_args = func_args
        assert type(func_kwargs) is dict
        self.func_kwargs = func_kwargs
        
        assert callable(func)
        self.func = func
        
        self.frames = process_frames_argument(frames)
        self.num_of_frames = len(self.frames)
        
        self.x = x
        
        initial_y = self.func(0, *self.func_args, **self.func_kwargs)
        self.fig, self.ax, self.line = plot_1D(x,initial_y, *plot_args, **plot_kwargs)
        
        super().__init__(self.fig, blit=True)
        
        ## For margin appearence
        self.fig.tight_layout()
    
    def _init_draw(self):
        self.progress_bar = Progress_Bar(self.num_of_frames)
    
    def _draw_frame(self, idx):
        y = self.func(idx, *self.func_args, **self.func_kwargs)
        self.line.set_data(self.x, y)
        self.progress_bar.print(idx)
        
    def new_frame_seq(self):
        return self.frames

#    def save(self, *args, **kwargs):
#        """Save animation into a movie file.
#        
#        [NOTE] If 'writer' is not specified, default writer defined in this module 
#        will be used to generate the movie file.
#
#        [TODO] Implement docstring inheritance.
#        """
#        writer = None
#        if 'writer' in kwargs.keys():
#            writer = kwargs.pop('writer')
#        else: writer = default_writer
#        super().save(*args, **kwargs, writer=writer)




class Animate_2D(Animate_Base):
    def __init__(self, X_mesh, Y_mesh, func, frames, func_args=(), func_kwargs={}, **plot_kwargs):

        assert type(func_args) is tuple
        self.func_args = func_args
        assert type(func_kwargs) is dict
        self.func_kwargs = func_kwargs

        assert callable(func)
        self.func = func

        self.frames = process_frames_argument(frames)
        self.num_of_frames = len(self.frames)

        self.fig, self.ax, self.pcm = plot_2D(X_mesh, Y_mesh, C=None, **plot_kwargs)

        super().__init__(self.fig, blit=True)


    def _init_draw(self):
        self.progress_bar = Progress_Bar(self.num_of_frames)
        self.current_index = 0

    def _draw_frame(self, i):
        C = self.func(i, *self.func_args, **self.func_kwargs)
        self.pcm.set_array(C.ravel(order='C'))
        self.progress_bar.print(self.current_index)
        self.current_index += 1

    def new_frame_seq(self):
        return self.frames

#    def save(self, *args, **kwargs):
#        """Save animation into a movie file.
#
#        [NOTE] If 'writer' is not specified, default writer defined in this module
#        will be used to generate the movie file.
#
#        [TODO] Implement docstring inheritance.
#        """
#        writer = None
#        if 'writer' in kwargs.keys():
#            writer = kwargs.pop('writer')
#        else: writer = default_writer
#        super().save(*args, **kwargs, writer=writer)

