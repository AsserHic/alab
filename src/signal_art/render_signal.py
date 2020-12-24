import pandas
from plotnine import aes, geom_path, ggplot


def show_xy_graph(data: pandas.DataFrame):
    plot = ggplot(data, aes(x='x', y='y'))
    plot += geom_path()
    print(plot)  # plot.draw()
