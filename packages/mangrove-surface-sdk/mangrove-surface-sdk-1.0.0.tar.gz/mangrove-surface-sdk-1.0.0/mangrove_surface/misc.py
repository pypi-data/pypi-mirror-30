import humanize
try:
    from IPython import get_ipython
    is_notebook = getattr(get_ipython(), "kernel", None) is not None
except ImportError:
    is_notebook = False


class ProgressBar(object):

    def __init__(self, label, expected_size):
        pb, show = None, None

        if is_notebook:
            from ipywidgets import FloatProgress, HTML, VBox
            from IPython.display import display

            lab = HTML()
            lab.value = label + \
                " (" + humanize.naturalsize(expected_size) + ")"
            pb = FloatProgress(min=0, max=expected_size)
            display(VBox([lab, pb]))

            def show(inc):
                pb.value = inc

            def done():
                return None
        else:
            from clint.textui.progress import Bar
            pb = Bar(
                label=label, expected_size=expected_size)
            show = pb.show
            done = pb.done

        self._pb = pb
        self.show = show
        self.done = done


def iter_progress_bar(iterator, label, expected_size, modulo=1):
    pb = ProgressBar(label, expected_size)
    for i, elem in enumerate(iterator):
        yield elem
        pb.show((i + 1) * modulo)
    pb.done()
