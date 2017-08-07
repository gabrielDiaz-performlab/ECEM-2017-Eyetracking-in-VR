from __future__ import division, print_function

from modules.ecem2017 import *
import numpy as np
import pandas as pd

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import os
init_notebook_mode()

np.set_printoptions(precision=2)



def plotGazeVelocity(datafile, trialNumber, columnNames,yLim=[0 ,500],width=800,height=600,blockNumber=1):
    
    #trialNum = 13
    gbTrial = datafile.groupby(['trialNumber','blockNumber']).get_group((trialNumber,blockNumber))

    import plotly.plotly as py
    import plotly.graph_objs as go

    import pandas as pd

    traces = []
    
    colors_idx = ['rgb(0,204,204)','rgb(128,128,128)','rgb(204,0,0)','rgb(102,0,204)']

    for idx, columnName in enumerate(columnNames):
        
        scatterObj = go.Scatter(
        x=gbTrial['frameTime'],
        y=gbTrial[columnName],
        name = columnName,
        line = dict(color = colors_idx[idx],width=3),
        opacity = 0.8)

        traces.append(scatterObj)
        
    ################################################################
    ## You can ignore this section.  This code adds event labels to the time series

    events_fr = gbTrial['eventFlag'].values
    eventIdx = np.where( gbTrial['eventFlag'] > 0 )

    eventTimes_idx =  gbTrial['frameTime'].values[eventIdx]  

    eventText_idx = [str(event) for event in events_fr[np.where(events_fr>2)]]
    eventText_idx = np.array([[eT, '','',''] for eT in eventText_idx]).flatten()

    x = np.array([np.array([eT, eT, np.nan, np.nan]).flatten() for eT in eventTimes_idx]).flatten()
    y = np.tile([ (yLim[1]-yLim[0])*.95 ,yLim[0],np.nan,np.nan],len(eventTimes_idx))

    eventLabels = go.Scatter(
        x=x,
        y=y,
        mode='lines+text',
        name = "trial events",
        text=eventText_idx,
        textposition='top right',
        line = dict(color = ('rgba(30, 150, 30,.5)'),width = 4)
    )

    ################################################################

    layout = dict(
        dragmode= 'pan',
        title='Time Series with Rangeslider',
        width=width,
        height=height,
        yaxis=dict(range=yLim, title='velocity'),
        xaxis=dict(
            rangeslider=dict(),
            type='time',
            range=[gbTrial['frameTime'].iloc[0], gbTrial['frameTime'].iloc[0]+2]
        )
    )
    
    traces.append(eventLabels)
    
    fig = dict(data=traces, layout=layout)
    iplot(fig)