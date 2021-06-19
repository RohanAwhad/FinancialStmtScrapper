import plotly.graph_objects as go


def plot(df, title):
    fig = go.Figure()
    for col in df.columns:
        y = df[col].values
        x = df[col].index
        fig.add_trace(go.Scatter(y=y, x=x, mode='lines+markers', name=col))

    fig.update_layout(title_text=title)
    # fig.update_xaxes(showticklabels=False)
    return fig
