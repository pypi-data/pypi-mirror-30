__version__ = '0.1.5'
__author__ = 'Herbert Kruitbosch'

no_load = False

try:
    from IPython.display import display
    import ipywidgets as widgets
    import humanize
except Exception as e:
    no_load = True
    exception = e

if no_load:
    def ProgressBar(iter, size=None):
        raise e
else:
    import time
    from math import sqrt


    def ProgressBar(iter, size=None):
        t0_ = time.time()
        def passed():
            return humanize.naturaldelta(time.time() - t0_)
        progress = widgets.FloatProgress(value=0.0, min=0.0, max=1.0)
        text = widgets.HTML(
            value="<b>0</b>s passed",
            placeholder='0%',
            description='',
        )
        text2 = widgets.HTML(
            value="<b>0</b>% or <b>0</b> of <b>unknown</b> done, {} passed".format(passed()),
            placeholder='0%',
            description='',
        )
        display(widgets.VBox([widgets.HBox([progress, text]), text2]))
        if size is None and hasattr(iter, '__len__'):
            size = len(iter)
        if size is not None:
            text2.value = "<b>0</b>% or <b>0</b> of <b>{}</b> done, {} passed".format(size, passed())
            guess_size = size is None
        if guess_size:
            size = 2
        t = 0
        tsq = 0
        i = 0
        for i, item in enumerate(iter, start=1):
            while i > size:
                size = size * 2
            t0 = time.time()
            yield item
            t0 = time.time() - t0
            t = time.time() - t0_
            tsq += t0 ** 2
            p = i / size
            progress.value = p
            std = humanize.naturaldelta((size - i) * sqrt((tsq / i) - (t / i) ** 2))
            left = humanize.naturaldelta((1 - p) / p * t if p > 0 else 0)
            text.value = "<b>{}</b> &plusmn; <b>{}</b> left".format(left, std)
            text2.value = "<b>{}</b>% or <b>{}</b> of <b>{}{}</b> done, {} passed".format(
                round(100 * p), i, size, ' (guessed)' if guess_size else '', passed())
        text.value = ''
        text2.value = "took <b>{}</b> to process <b>{}</b> items".format(passed(), i)
        progress.value = 100
