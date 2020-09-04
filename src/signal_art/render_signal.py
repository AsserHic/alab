import pandas
from plotnine import aes, geom_path, ggplot


def show_xy_graph(data: pandas.DataFrame):
    g = ggplot(data, aes(x='x', y='y'))
    g += geom_path()
    print(g)
