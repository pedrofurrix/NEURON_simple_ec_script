from neuron import h
import numpy as np

def max_shift(cell):

    # Initialize variables for tracking max/min values and corresponding segments
    results = {
        "max_v": h.v_init,
        "min_v": h.v_init,
        "max_seg": cell.soma(0.5),  # Default to soma
        "min_seg": cell.soma(0.5)
    }

    # Callback function to update max/min voltages    
    def every_step():
        for sec in cell.all:
            for seg in sec:
                v_membrane=seg.v
                if v_membrane > results["max_v"]:
                    results["max_v"] = v_membrane
                    results["max_seg"] = seg
                elif v_membrane < results["min_v"]:
                    results["min_v"] = v_membrane
                    results["min_seg"] = seg
    # Register the callback to execute at each simulation step
    callback=h.beforestep_callback(cell.soma(0.5))
    callback.set_callback(every_step)

    # Return results dictionary and callback for further use
    return results, callback