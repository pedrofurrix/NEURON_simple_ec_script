import plotly
import plotly.graph_objects as go
from neuron import h,gui
from neuron.units import mV, ms
import numpy as np
import matplotlib.colors as mcolors
from matplotlib import cm
import os
import matplotlib.pyplot as plt

# Just the thing in https://www.neuron.yale.edu/phpBB/viewtopic.php?t=3286, with saving...
def plot_view(folder=os.getcwd(),tmin=1e5,tmax=1e5,cell=None):
    ps=h.PlotShape(True)
    ps.variable("v")
    #ps.scale(-80, 30)
    h.fast_flush_list.append(ps)
    ps.exec_menu("Shape Plot")
    ps.exec_menu("Show Diam")
    ps.exec_menu("View = plot")
    
    output_dir="frames"
    out=os.path.join(folder,output_dir)
    os.makedirs(out, exist_ok=True)  # Create directory if it doesn't exist

    def save_files():
        t=h.t
        if t>=tmin and t>=tmax:
            filename=f"frame_{t:.2f}.eps"
            file=os.path.join(out,filename)
            ps.printfile(file)

    callback=h.beforestep_callback(cell.soma(0.5))
    callback.set_callback(save_files)
        
    return ps, callback

#Trying to implement color section and also the plot changing over time.
def plot_view_color(folder,cell,results={},tmin=1e6,tmax=0):
    ps=h.PlotShape(True)
    ps.variable("v")
    h.fast_flush_list.append(ps)
    ps.exec_menu("Shape Plot")   
    ps.exec_menu("Show Diam") 
    ps.exec_menu("View = plot")

    # #Color the sections with the maximum and minimum voltage shift
    # if "max_sec" in results:
    #     ps.color(1,sec=results["max_sec"])
    # if "min_sec" in results:
    #     ps.color(2,sec=results["min_sec"])
    
    output_dir="frames"
    out=os.path.join(folder,output_dir)
    os.makedirs(out, exist_ok=True)  # Create directory if it doesn't exist

    # def save_frame():
    #     t=h.t
    #     if t>=tmin and t<=tmax:
    #         file=os.path.join(out,f"frame_{t:04d}.eps")
    #         ps.printfile(file)
    
    # callback=h.beforestep_callback(cell.soma(0.5))
    # callback.set_callback(save_frame)

    return ps #,callback

# Does not seem to work...
# Does not update over time.
# https://www.neuron.yale.edu/phpBB/viewtopic.php?p=20058#p20058
def shape_plot(cell,var=None,results={}):
    ps = h.PlotShape(False)
    #ps.exec_menu("Show Diam") 
    ps.show(0)
    ps.variable(var)
    fig=ps.plot(plotly, cmap=cm.cool)

    v_vals = [getattr(seg, var) for sec in h.allsec() for seg in sec]    
    
    # Create a custom colormap using Matplotlib (cool colormap)
    cmap = cm.cool
    
    # Collect values of the variable from all segments
    # Create a colormap function
    colormap = cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=min(v_vals), vmax=max(v_vals))).to_rgba

    # Map the normalized values to a Plotly colorscale as strings
    plotly_colorscale = [[v, f'rgb{tuple(int(255 * c) for c in colormap(v)[:3])}'] for v in np.linspace(0, 1, cmap.N)]

    # Create a separate scatter plot for the colorbar
    colorbar_trace = go.Scatter(
    x=[0],
    y=[0],
    mode='markers',
    marker=dict(
        colorscale=plotly_colorscale,
        cmin=min(v_vals),
        cmax=max(v_vals),
        colorbar=dict(
            title=var,
            thickness=20  # Adjust the thickness of the colorbar
        ),
        showscale=True
    )
    )

    # Add the colorbar trace to the figure
    fig.add_trace(colorbar_trace)
    fig.update_xaxes(showticklabels=False, showgrid=False)
    fig.update_yaxes(showticklabels=False, showgrid=False)
    fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)'
    )


    fig.show()
    return fig


# Shape Plot, highlighting section with the maximum and minimum v shift
def SP_highlight(cell,results={}):
    ps=h.PlotShape(True)
    ps.show(0) # Display diams
    ps.exec_menu("Shape Plot")   
    #ps.exec_menu("Show Diam") 
    if "max_sec" in results:
        ps.color(1,sec=results["max_sec"])
    if "min_sec" in results:
        ps.color(2,sec=results["min_sec"])
    return ps

# Work with the Shape object from base_shape.py
def max_min_shape(results,shape):
    """
    Highlights the segments with the maximum and minimum voltage on a shape plot.

    Parameters:
    results (dict): Output from the `max_shift` function, containing max/min voltage info.

    """
    # ps=ps = h.PlotShape(False)
    # ps.variable("v")
    # #ps.plot(plt)
    # ps.show(0)
    # Highlight the segment with the maximum voltage
    if "max_seg" and "min_seg" in results:
        max_seg = results["max_seg"]
        min_seg = results["min_seg"]
        mark_max=h.IClamp(max_seg)
        mark_min=h.IClamp(min_seg)
        shape.point_mark(mark_max,1,"S",5)
        shape.point_mark(mark_min,2,"T",5)
        shape.exec_menu("View=plot")
        # ps.plot().mark(max_seg.x, max_seg.sec, 2, 6, 1)  # Red circle
        print(f"Max voltage: {results['max_v']} at section {max_seg.sec.name()}, x={max_seg.x}")
        print(f"Min voltage: {results['min_v']} at section {min_seg.sec.name()}, x={min_seg.x}")
        shape.label("Max and Min voltage segments")

    # # Testing with coloring sections
    # if "max_sec" in results:
    #     max_sec = results["max_sec"]
    #     ps.color(2,sec=max_sec)
    # if "min_sec" in results:
    #     min_sec = results["min_sec"]
    #     ps.color(3,sec=min_sec)

    return mark_max, mark_min


# Just the thing in https://www.neuron.yale.edu/phpBB/viewtopic.php?t=3286, with saving...
# Probably does not work.
def plot_view_noGUI(results={}, folder=os.getcwd(),tmin=1e5,tmax=1e5,cell=None):
    
    # ps.scale(-80, 30)
    # h.fast_flush_list.append(ps)
    # ps.exec_menu("Shape Plot")
    # ps.exec_menu("Show Diam")

    def save_files():
        ps=h.PlotShape(False)
        ps.variable("v")
        ps.plot(plotly)
        t=h.t
        if t>=tmin and t>=tmax:
            filename=f"frame_{t:.2f}.eps"
            file=os.path.join(folder,filename)
            ps.printfile(file)

def save_changing_rvp(cell=None,results={},folder=os.getcwd(),tmin=1e5,tmax=1e5):
    output_dir="rvp_min_max"
    out=os.path.join(folder,output_dir)
    os.makedirs(out, exist_ok=True)  # Create directory if it doesn't exist

    if "max_seg" and "min_seg" in results:
        maxseg=results["max_seg"]
        minseg=results["min_seg"]

    print(f"minseg ={minseg}\n maxseg={maxseg}")
        
    def saveplot():
        t=h.t
        if tmin<=t<=tmax:
            # plot_rx=h.RangeVarPlot('v',minseg,maxseg) # spaceplot
            plot_rx=h.RangeVarPlot('v',cell.soma(0),cell.dend2(1)) # spaceplot test
            # # Matplotlib
            # graph = plt.gca()

            # # Create a matplotlib figure
            # # fig, ax = plt.subplots()
            # label1 = f"t = {t:.1f} ms"
            # plot_rx.plot(graph, label=label1,linewidth=10,color='r')
            
            # # # Add titles and labels
            # # ax.set_title(f"Range Variable Plot at t={t:.1f} ms")
            # # ax.set_xlabel("Distance")
            # # ax.set_ylabel("Voltage (mV)")
            
            # # Save the figure
            # output_file = os.path.join(out, f"range_var_plot_{t:.1f}.png")
            # plt.savefig(output_file, dpi=300, bbox_inches="tight")  # Save the plot
            # print(f"Plot saved to {output_file}")
            # plt.close(graph)  # Close the figure to avoid memory issues

            # NEURON Graph
            g=h.Graph()
            plot_rx.plot(g, 2, 3)
            g.exec_menu('View = plot')
            output_file = os.path.join(out, f"range_var_plot_{t:.1f}.eps")
            g.printfile(output_file)


    callback=h.beforestep_callback(cell.soma(0.5))
    callback.set_callback(saveplot)
    return callback