from __future__ import division, print_function

from modules.ecem2017 import *
import numpy as np
import pandas as pd

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import os
init_notebook_mode()

np.set_printoptions(precision=2)

def createHead(headTransform_4x4 = np.eye(4)):

        phi = np.linspace(0, 2*np.pi)
        theta = np.linspace(-np.pi/2, np.pi/2)
        phi, theta = np.meshgrid(phi, theta)

        x = np.cos(theta) * np.sin(phi) * .15
        y = np.sin(theta) * 0.2
        z = np.cos(theta) * np.cos(phi) * .15
        w = np.ones(2500)

        x = x.flatten()
        y = y.flatten()
        z = z.flatten()

        if headTransform_4x4 is False:
            headVertices_XYZW =np.array([x,y,z,w])
        else:
            headVertices_XYZW = np.dot( headTransform_4x4,[x,y,z,w])

        headShape = go.Mesh3d({ 'x':headVertices_XYZW[0,:], 
                      'y': headVertices_XYZW[2,:], 
                      'z': headVertices_XYZW[1,:],'alphahull': 0},
                      color='rgb(20, 145, 145)',
                      )

        return headShape


  

def plotGazeVelocity(datafile, trialNumber, columnNames,yLim=[0 ,500],width=800,height=600,blockNumber=1,inline=False):
    
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
    
    if inline is True:
        iplot(fig)
    else:
        plot(fig)

    
def plotEIH(cycEyeInHead_XYZW,
            xRange = [-1,1],
            yRange = [-1,1],
            zRange = [-1,1],
            yLim=[0 ,500],
            width=800,
            height=600,
            inline=False):

    head = createHead()
    
    eihDir = go.Scatter3d(x=[0,cycEyeInHead_XYZW[0]],
                   y=[0,cycEyeInHead_XYZW[2]],
                   z=[0,cycEyeInHead_XYZW[1]],
                   mode='lines',
                   line = dict(
                       color = ('rgb(205, 12, 24)'),
                       width = 4)
                  )
    
    layout = go.Layout(title="EIH", 
                    width=width,
                    height=height,
                    showlegend=False,
                    scene=go.Scene(aspectmode='manual',
                                aspectratio=dict(x=1, y=1, z=1),
                                xaxis=dict(range=xRange, title='x Axis'),
                                yaxis=dict(range=yRange, title='y Axis'),
                                zaxis=dict(range=zRange, title='z Axis'),

                               ),
                    margin=go.Margin(t=100),
                    hovermode='closest',

                    )

    fig=go.Figure(data=go.Data([head,eihDir]),layout=layout)

    if inline is True:
        iplot(fig)
    else:
        plot(fig)
    
def plotGIW(viewPos_XYZ,
            cycGIW_XYZW,
            ballPos_XYZ,
            headTransform_4x4,
            xRange = [-1,1],
            yRange = [-1,1],
            zRange = [-1,1],
            width=800,
            height=600,
            inline=False):

    headShape = createHead(headTransform_4x4)
    
    giwDir = go.Scatter3d(x=[viewPos_XYZ[0],cycGIW_XYZW[0]],
                          y=[viewPos_XYZ[2],cycGIW_XYZW[2]],
                          z=[viewPos_XYZ[1],cycGIW_XYZW[1]],
                          mode='lines+text',
                    text=['','gaze'],
                    textposition='top right',
                    textfont=dict(
                        family='sans serif',
                        size=14,
                        color=('rgb(20, 0, 145)'),
                        ),
                    line = dict(
                       color=('rgb(20, 0, 145)'),
                       width = 4)
                         )

    xyz = np.subtract(ballPos_XYZ,viewPos_XYZ)
    ballDir_XYZ = xyz / np.linalg.norm(xyz)
    ballEndPoint_XYZ = viewPos_XYZ + ballDir_XYZ*1.5
    
    ballDir  = go.Scatter3d(x=[viewPos_XYZ[0],ballEndPoint_XYZ[0]],
        y=[viewPos_XYZ[2],ballEndPoint_XYZ[2]],
        z=[viewPos_XYZ[1],ballEndPoint_XYZ[1]],
        mode='lines+text',
        text=['','ball'],
        textposition='top right',
        textfont=dict(
            family='sans serif',
            size=14,
            color='rgb(30, 150, 30)',
            ),
        line = dict(
           color = ('rgb(30, 150, 30)'),
           width = 4)
                    )

    layout = go.Layout(title="Gaze in World", 
                    width=width,
                    height=height,
                    showlegend=False,
                    scene=go.Scene(aspectmode='manual',
                                aspectratio=dict(x=1, y=1, z=1),
                                xaxis=dict(range=xRange, title='x Axis'),
                                yaxis=dict(range=yRange, title='y Axis'),
                                zaxis=dict(range=zRange, title='z Axis'),

                               ),
                    margin=go.Margin(t=100),
                    hovermode='closest',

                    )

    fig=go.Figure(data=go.Data([giwDir,ballDir,headShape]),layout=layout)

    if inline is True:
        iplot(fig)
    else:
        plot(fig)

