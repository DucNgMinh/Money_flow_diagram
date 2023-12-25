import numpy as np
import pandas as pd

import plotly.graph_objects as go   

import streamlit as st

def sankey_graph(data, mapped_columns, color_map, highlighted_node, title):
    data[mapped_columns] = data[mapped_columns].astype(str)

    # Function to create a mapping of each unique step to a unique integer
    def create_node_mapping(data, columns):
        unique_nodes = set()
        for col in columns:
            unique_nodes.update(data[col].unique())
        return {node: i for i, node in enumerate(sorted(unique_nodes))}

    # Create the node mapping
    node_mapping = create_node_mapping(data, mapped_columns)

    # Prepare source, target, and value lists for the Sankey diagram
    sources = []
    targets = []
    values = []
    colors = []  # For link colors

    highlight_color = 'rgba(255, 0, 0, 0.5)'  # Highlight color for the paths leading to the highlighted node
    default_color = 'rgba(0, 0, 0, 0.1)'  # Default color for other paths

    # Function to check if a row includes the highlighted node
    def row_includes_highlighted_node(row, highlighted_node):
        return highlighted_node in row[mapped_columns].values

    def create_color_list(node_mapping, color_map):
        new_color_list = []
        for node in node_mapping:
            base_node = node.split('_')[0]
            if base_node in color_map:
                new_color_list.append(color_map[base_node])
            else:
                new_color_list.append('rgba(0, 0, 0, 0.8)')  # Default color for unmatched nodes
        return new_color_list
    
    if highlighted_node != None:
        highlighted_node = highlighted_node +  '_' + str(mapped_columns[0])[:3]
    else:
        highlighted_node = '1'

    # Populate source, target, values, and colors
    for _, row in data.iterrows():
        row_highlighted = row_includes_highlighted_node(row, highlighted_node)
        for i in range(len(mapped_columns) - 1):
            source = node_mapping[row[mapped_columns[i]]]
            target = node_mapping[row[mapped_columns[i + 1]]]
            value = row['Size']
            sources.append(source)
            targets.append(target)
            values.append(value)
            colors.append(highlight_color if row_highlighted else default_color)

    color_list = create_color_list(node_mapping, color_map)

    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=list(node_mapping.keys()),
            color = color_list
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors  # Add custom colors
        )
    )])

    fig.update_layout(autosize=False, width=1280, height=480, title_text= title, font_size=12)
    return fig 

def create_filtered_df(data, highlighted_node):
    values_to_filter = [highlighted_node + "_" + map_columns[0]]
    filtered_df = data[data.isin(values_to_filter).any(axis=1)]
    filtered_columns = filtered_df.columns
    filtered_columns = filtered_columns.drop('Size')
    for col in filtered_columns:
        filtered_df[col] = filtered_df[col].str[:-4]
    return filtered_df

def calculate_percentage(df, level_column, size_column):
    grouped_df = df[[level_column, size_column]].groupby(level_column)[size_column].sum().reset_index()
    total_size = grouped_df[size_column].sum()
    grouped_df[f'Percentage_{level_column[2]}'] = grouped_df[size_column] / total_size 
    # grouped_df.rename(columns={col: col[:3]}, inplace= True)
    return grouped_df.drop(size_column, axis=1)

def calculate_distribution(filtered_df):
    results = []
    filtered_columns = filtered_df.columns.drop('Size')

    for col in filtered_columns:
        result = calculate_percentage(filtered_df, col, 'Size')
        results.append(result)

    final_result = pd.concat(results, axis=1)
    final_result = final_result.style.format({
        'Percentage_0': '{:.2%}'.format,
        'Percentage_1': '{:.2%}'.format,
        'Percentage_2': '{:.2%}'.format,
        'Percentage_3': '{:.2%}'.format,
        'Percentage_4': '{:.2%}'.format
    })

    return final_result


if __name__ == '__main__':
    st.set_page_config(layout="wide")
    # Title
    st.title("Money Flow Diagram !!!!!")

    map_df = pd.read_csv('./Sankey_Plot/map.csv')
    trans_df = pd.read_csv('./Sankey_Plot/sample data lv pk.csv')[['Lv0', 'Lv1', 'Lv2', 'Lv3', 'Lv4', 'Size']]

    map_name = map_df.set_index('ORG_UNIT_ID')['LEVEL_02_NAME'].to_dict()

    node_list = ['TT DICH VU NOI BO', 'TT QUAN LY CHUNG TOAN HANG', 'TT AO',
            'KHONG CO TRONG CAY', 'TT DOANH THU',
            'TT QUAN LY CHUNG KHOI KINH DOANH', 'TT HO TRO TRUC TIEP',
            'TT HO TRO SAN PHAM', 'TT QUAN LY CHUNG CHI NHANH']

    color_list = ['rgba(44, 160, 44, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(140, 86, 75, 0.8)',
                'rgba(23, 190, 207, 0.8)', 'rgba(188, 189, 34, 0.8)', 'rgba(214, 39, 40, 0.8)',
                'rgba(188, 189, 34, 0.8)', 'rgba(31, 119, 180, 0.8)', 'rgba(140, 86, 75, 0.8)']
    
    color_map = dict(zip(node_list, color_list))

    layers = ['Lv0', 'Lv1', 'Lv2', 'Lv3', 'Lv4']
    mapped_layers = [ col + '_mapped' for col in layers]
    for i, j in zip(layers, mapped_layers):
        trans_df[j] = trans_df[i].map(map_name)
        trans_df[j] = trans_df[j] + '_' + i

    try:
        overall_layers = ['Lv0_mapped', 'Lv4_mapped']
        highlighted_node = 'None'
        overall_data = trans_df.groupby(overall_layers)['Size'].sum().reset_index()  
        fig = sankey_graph(overall_data, overall_layers, color_map, highlighted_node, "Overall Sankey Diagram")
        st.plotly_chart(fig)
    except:
        st.markdown("<h3 style='text-align: center; color: green;'>Overall parameters wrong </h3>", unsafe_allow_html=True)

    map_columns = st.multiselect("Select two or more Node:", layers)
    map_columns = sorted(map_columns, key=lambda x: int(x[-1]))

    if len(map_columns) == 0:
        st.markdown("<h3 style='text-align: center; color: green;'>Choose at least 2 nodes to make futher calculations </h3>", unsafe_allow_html=True)

    highlighted_node = st.selectbox("Select Highlight Node:", node_list)
    try:
        mapped_columns = [ col + '_mapped' for col in map_columns]
        data = trans_df.groupby(mapped_columns)['Size'].sum().reset_index()   
        fig = sankey_graph(data, mapped_columns, color_map, highlighted_node, "Multi-Level Sankey Diagram with Highlighted Flow")

        st.plotly_chart(fig)
        filtered_df = create_filtered_df(data, highlighted_node)
        final_result = calculate_distribution(filtered_df)
        st.dataframe(final_result)
    except: 
        st.markdown("<h3 style='text-align: center; color: green;'>Can not render graph due to the missing of needed information </h3>", unsafe_allow_html=True)
    
    