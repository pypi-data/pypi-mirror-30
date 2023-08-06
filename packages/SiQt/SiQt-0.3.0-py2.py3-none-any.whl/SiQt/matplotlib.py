import matplotlib.backends.backend_qt5agg as backend_qtagg


class NavigationToolbar(backend_qtagg.NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in backend_qtagg.NavigationToolbar2QT.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]
