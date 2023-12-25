import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time

df = pd.read_csv(r'C:\Users\Admin\PycharmProjects\BIDV_Task\Sankey Plot\sample_data.csv')
df['LvPK_2'] = df['LvPK'].astype(str).str[0]

def create_node_dict(df, columns):
    unique_nodes = {node: i for i, node in enumerate(set(df[columns].values.flatten()))}
    return unique_nodes

def generate_link_colors(source, target, labels, highlight_nodes, highlight_color, default_color='rgba(0,0,0,0.2)'):
    """
    Generate colors for links in a Sankey diagram.
    """
    colors = []
    for s, t in zip(source, target):
        if labels[s] in highlight_nodes or labels[t] in highlight_nodes:
            colors.append(highlight_color)
        else:
            colors.append(default_color)
    return colors

# Extracting the node names and creating a dictionary to map nodes to unique IDs
columns = ['Lv0', 'Lv1', 'Lv2', 'Lv3', 'Lv4', 'LvPK', 'LvPK_2']
node_dict = create_node_dict(df, columns)
labels = list(node_dict.keys())

# Preparing source, target, and value lists for the Sankey diagram
source = []
target = []
value = []

for _, row in df.iterrows():
    for i in range(len(columns)-1):
        source.append(node_dict[row[columns[i]]])
        target.append(node_dict[row[columns[i+1]]])
        value.append(row['Size'])

# Example usage
highlight_nodes = ['1']  # Nodes to highlight
highlight_color = 'red'  # Color for highlighting

# Generate the color list for links
link_colors = generate_link_colors(source, target, labels, highlight_nodes, highlight_color)

# Creating the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=15,
        line=dict(color="black", width=0.5),
        label=labels,
        color="blue"
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color=link_colors  
    ))])

fig.update_layout(autosize=True, title_text="Multi-Level Sankey Diagram", font_size=10)
fig.show()