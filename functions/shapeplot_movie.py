import plotly
import plotly.graph_objects as go
from neuron import h,gui
from neuron.units import mV, ms
import numpy as np
import matplotlib.colors as mcolors
from matplotlib import cm

# adapted from https://www.neuron.yale.edu/phpBB/viewtopic.php?p=20058#p20058
# https://www.neuron.yale.edu/phpBB/viewtopic.php?t=3286
def movie_v(cell):
    # Create a custom colormap using Matplotlib (cool colormap)
    # cmap = cm.cool

    # Create a colormap function
    # colormap = cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=0, vmax=1)).to_rgb
    # plotly_colorscale = [[v, f'rgb{tuple(int(255 * c) for c in colormap(v)[:3])}'] for v in np.linspace(0, 1, cmap.N)]

    # colorbar_trace = go.Scatter(
    #     x=[0],
    #     y=[0],
    #     mode='markers',
    #     marker=dict(
    #         colorscale=plotly_colorscale,
    #         cmin=-100,
    #         cmax=50,
    #         colorbar=dict(
    #             title='v (mV)',
    #             thickness=20  # Adjust the thickness of the colorbar
    #         ),
    #         showscale=True
    #     )
    # )

    def make_plot():
        ps = h.PlotShape(True)
        ps.variable("v")
        # ps.plot(plotly).show()
        # fig=ps.plot(plotly, cmap=cm.cool)
        # fig.add_trace(colorbar_trace)
        # fig.update_xaxes(showticklabels=False, showgrid=False)
        # fig.update_yaxes(showticklabels=False, showgrid=False)
        # fig.update_layout(
        #     plot_bgcolor='rgba(0,0,0,0)'
        # )
        # fig.show()

    callback=h.beforestep_callback(cell.soma(0.5))
    callback.set_callback(make_plot)

    # Return results dictionary and callback for further use
    return callback