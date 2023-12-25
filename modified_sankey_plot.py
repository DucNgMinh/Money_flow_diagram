import pandas as pd
import plotly.graph_objects as go

# Load the new dataset
file_path = r'C:\Users\Admin\PycharmProjects\BIDV_Task\Sankey Plot\sample_test.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Convert numeric levels to string
level_columns = ['LvPK', 'LvPK_2']
data[level_columns] = data[level_columns].astype(str)

# Function to create a mapping of each unique step to a unique integer
def create_node_mapping(data, level_columns):
    unique_nodes = set()
    for col in level_columns:
        unique_nodes.update(data[col].unique())
    return {node: i for i, node in enumerate(sorted(unique_nodes))}

# Create the node mapping
node_mapping = create_node_mapping(data, level_columns)

# Prepare source, target, and value lists for the Sankey diagram
sources = []
targets = []
values = []

# Populate source, target, values
for _, row in data.iterrows():
    for i in range(len(level_columns) - 1):
        source = node_mapping[row[level_columns[i]]]
        target = node_mapping[row[level_columns[i + 1]]]
        value = row['Size']
        sources.append(source)
        targets.append(target)
        values.append(value)

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
        value=values
    )
)])

fig.update_layout(title_text="Multi-Level Sankey Diagram", font_size=10)
fig.show()
