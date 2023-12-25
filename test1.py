import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Load the dataset
file_path = r'C:\Users\Admin\PycharmProjects\BIDV_Task\Sankey Plot\Sankey Template Multi Level.xlsx - Data.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Function to create a mapping of each unique step to a unique integer
def create_node_mapping(data):
    unique_nodes = set()
    for col in data.columns[2:-1]:  # Exclude 'Link', 'ID', and 'Size' columns
        unique_nodes.update(data[col].unique())
    return {node: i for i, node in enumerate(sorted(unique_nodes))}

# Create the node mapping
node_mapping = create_node_mapping(data)

# Prepare source, target, and value lists for the Sankey diagram
sources = []
targets = []
values = []
colors = []  # For link colors

target_node = 'I'  # Specify your target node here
highlight_color = 'rgba(255, 0, 0, 0.5)'  # Highlight color for the paths leading to the target node
default_color = 'rgba(0, 0, 0, 0.1)'  # Default color for other paths

# Function to check if a row leads to the target
def row_leads_to_target(row, target_node):
    return target_node in row[2:-1].values  # Check if target node is in the steps

# Populate source, target, values, and colors
for _, row in data.iterrows():
    row_highlighted = row_leads_to_target(row, target_node)
    for i in range(2, len(data.columns) - 2):
        source = node_mapping[row[i]]
        target = node_mapping[row[i + 1]]
        value = row['Size']
        sources.append(source)
        targets.append(target)
        values.append(value)
        colors.append(highlight_color if row_highlighted else default_color)

# Create the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=list(node_mapping.keys())
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        color=colors  # Add custom colors
    )
)])

fig.update_layout(title_text="Multi-Level Sankey Diagram with Highlighted Paths", font_size=10)
fig.show()

