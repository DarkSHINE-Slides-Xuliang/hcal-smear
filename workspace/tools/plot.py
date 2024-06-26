import plotly.graph_objects as go
import plotly.express as px
import numpy as np

marker_symbol_cycle = ['circle', 'square', 'cross', 'star-square', 'star-diamond', 'pentagon',
                       'diamond-tall', 'diamond-wide', 'star', 'hourglass']

def plot_style(fig, fig_title='',
               xaxes_title='', yaxes_title='',
               xaxes_type=None, yaxes_type=None,
               xaxes_tickangle=0,
               xaxes_range=None, yaxes_range=None,
               fig_width=800, fig_height=600,
               fontsize1=20, fontsize2=16,
               darkshine_label1=r'<b><i>Dark SHINE</i></b>',
               darkshine_label2=r'1×10<sup>14</sup> Events @ 8 GeV',
               darkshine_label3=None):
    axis_attr = dict(
        linecolor="#666666",
        gridcolor='#F0F0F0',
        zerolinecolor='rgba(0,0,0,0)',
        linewidth=2,
        gridwidth=1,
        showline=True,
        showgrid=False,
        mirror=True,
        tickfont=dict(size=16),
    )
    fig.update_xaxes(
        **axis_attr,
        title=dict(
            text=xaxes_title,
            font_size=fontsize1
        ),
        range=xaxes_range,
        type=xaxes_type,
        tickangle=xaxes_tickangle,
    )
    fig.update_yaxes(
        **axis_attr,
        showexponent='all',
        exponentformat='power',
        type=yaxes_type,
        title=dict(
            text=yaxes_title,
            font_size=fontsize1
        ),
        range=yaxes_range
    )
    fig.update_layout(
        title=dict(
            text=fig_title,
            x=0.5,
            font_size=fontsize1
        ),
        legend=dict(
            x=1,
            y=1,
            xanchor='right',  # Anchor point of the legend ('left' or 'right')
            yanchor='top',  # Anchor point of the legend ('top' or 'bottom')
            bgcolor='rgba(0,0,0,0)',
            font_size=fontsize2,
            groupclick="toggleitem",
        ),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=90,
            r=20,
            b=20,
            t=80,
        ),
        width=fig_width,
        height=fig_height,
    )
    # Rearrange the legend items to form two columns
    n = len(fig.data)  # Number of traces
    if n > 3:
        legend=dict(orientation="h")
        nhalf = round(n/2)
        for i in range(nhalf):
            fig.data[i].legendgroup = 'group2'
        for i in range(nhalf, n):
                fig.data[i].legendgroup = 'group1'
    if darkshine_label1:
        fig.add_annotation(x=0.04, y=0.98,
                           xref="paper", yref="paper",
                           text=darkshine_label1,
                           font_size=fontsize1 - 2,
                           showarrow=False,
                           )
    if darkshine_label2:
        fig.add_annotation(x=0.04, y=0.93,
                           xref="paper", yref="paper",
                           text=darkshine_label2,
                           font_size=fontsize2,
                           showarrow=False,
                           )
    if darkshine_label3:
        fig.add_annotation(x=0.04, y=0.88,
                           xref="paper", yref="paper",
                           text=darkshine_label3,
                           font_size=fontsize2,
                           showarrow=False,
                           )

def add_histogram_data(fig, data, name, normalize=True, hist_bins=None, hist_range=None):
    if hist_range is None:
        data_min = min(data)
        data_max = max(data)
        margin = round(0.1 * (data_max - data_min))
        hist_range = (data_min - margin, data_max + margin)
    if hist_bins is None:
        hist_bins = round(hist_range[1] - hist_range[0])

    count, index = np.histogram(
        data,
        bins=hist_bins,
        range=hist_range,
        density=normalize
    )
    fig.add_trace(
        go.Scatter(
            name=name,
            x=index,
            y=count,
            line=dict(width=2, shape='hvh'),
        )
    )


def add_histo1d(fig, histo, name='hist', unitconv = 1, color=None):
    n_bins = histo.GetNbinsX()
    edges = unitconv * np.array([histo.GetBinLowEdge(i) for i in range(1, n_bins + 2)])
    #dx = edges[1] - edges[0]
    #edges = edges + 0.5 * dx
    edges=(edges[1:] + edges[:-1])/2
    binvalue = np.array([histo.GetBinContent(i) for i in range(1, n_bins + 1)])
    errors = np.array([histo.GetBinError(i) for i in range(1, n_bins + 1)])
    y_upper = binvalue + errors
    y_lower = binvalue - errors
    # Set line and error band color from plotly color cycle
    if color is None:
        color_cycle=px.colors.qualitative.Plotly
        trace_index = int(len(fig.data) / 2)   # Divided by 2 when plot line and erro band
        color = color_cycle[trace_index % len(color_cycle)]
    fig.add_trace(
        go.Scatter(
            name=name,
            x=edges,
            y=binvalue,
            mode='lines',
            line=dict(width=2, shape='hvh'),
            line_color=color,
        ),
    )
    # Retrieve the line color of the last trace added (the histogram line)
    line_color = fig.data[-1].line.color
    # Use the line color for the error band, but with added transparency
    if line_color[0] == '#':
        error_band_color = f'rgba({int(line_color[1:3], 16)}, {int(line_color[3:5], 16)}, {int(line_color[5:7], 16)}, 0.2)'
    else:
        line_color_rgb = line_color.split('(')[1].split(')')[0].split(',')
        error_band_color = f'rgba({line_color_rgb[0]}, {line_color_rgb[1]}, {line_color_rgb[2]}, 0.2)'
    fig.add_trace(
        go.Scatter(
            x=np.append(edges, edges[::-1]), # x, then x reversed
            y=np.append(y_upper, y_lower[::-1]), # upper, then lower reversed
            fill='toself',
            fillcolor=error_band_color,
            line=dict(color='rgba(255,255,255,0)', shape='hvh'),
            hoverinfo="skip",
            showlegend=False
        )
    )
    valuemin, valuemax = None, None
    if binvalue[binvalue>0].size > 0:
        valuemin = binvalue[binvalue>0].min()
        valuemax = binvalue[binvalue>0].max()
    return valuemin, valuemax

def add_scatter(fig, name, bins, values, secondary_y = False):
    trace_index = len(fig.data)
    fig.add_trace(
        go.Scatter(
            name=name,
            x=bins,
            y=values,
            mode='markers',
            marker=dict(
                symbol=marker_symbol_cycle[trace_index % len(marker_symbol_cycle)],
                size=15,
                color='#7F7F7F' if name == 'Inclusive' else None,
                line=dict(
                    color='DarkSlateGrey',
                    width=2
                )
            ),
            opacity=0.8,
        ),
        secondary_y=secondary_y,
    )
    return values.min(), values[values != np.inf].max()
