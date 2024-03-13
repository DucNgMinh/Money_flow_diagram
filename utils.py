import numpy as np
import pandas as pd

import streamlit as st
import plotly.graph_objects as go   

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def generate_year_month_range(start_date, end_date):
        current_date = start_date
        year_month_list = []

        while current_date <= end_date:
            year_month_list.append(current_date.strftime('%Y/%m'))
            current_date += relativedelta(months=1)

        return year_month_list

def sankey_graph(data, mapped_columns, highlighted_nodes, title, size_column= 'Size', color_map= False, autosize= False):
    data[mapped_columns] = data[mapped_columns].astype(str)

    # Function to create a mapping of each unique step to a unique integer
    def create_node_mapping(data, columns):
        unique_nodes = set()
        for col in columns:
            unique_nodes.update(data[col].unique())
        return {node: i for i, node in enumerate(sorted(unique_nodes))}

    # Create
    def create_color_list(node_mapping, color_map):
        new_color_list = []
        for node in node_mapping:
            node = node.split('_')[0]
            if node in color_map:
                new_color_list.append(color_map[node])
            else:
                new_color_list.append('#006B68')  # Default color for unmatched nodes
        return new_color_list
    
    # Create the node mapping
    node_mapping = create_node_mapping(data, mapped_columns)
    node_mapping[''] = len(node_mapping)
    print(node_mapping)
    # Prepare source, target, and value lists for the Sankey diagram
    sources = []
    targets = []
    values = []
    colors = []  

    color_list = create_color_list(node_mapping, color_map)
    highlight_color_dict = {'KHOI BAN LE_Lv0':'#CBF3D2' ,
                            'KHOI BAN LE_Lv1':'#CBF3D2' ,
                            'KHOI BAN LE_Lv2':'#CBF3D2' ,
                            'KHOI BAN LE_Lv3':'#CBF3D2' ,
                            'KHOI BAN LE_Lv4':'#CBF3D2' ,
                            'KHOI BAN BUON_Lv0':'#FFCCCB',
                            'KHOI BAN BUON_Lv1':'#FFCCCB',
                            'KHOI BAN BUON_Lv2':'#FFCCCB',
                            'KHOI BAN BUON_Lv3':'#FFCCCB',
                            'KHOI BAN BUON_Lv4':'#FFCCCB',
                            'KHOI THAM DINH VA PHE DUYET_Lv0':'#ff7b7b',
                            'KHOI THAM DINH VA PHE DUYET_Lv1':'#ff7b7b',
                            'KHOI THAM DINH VA PHE DUYET_Lv2':'#ff7b7b',
                            'KHOI THAM DINH VA PHE DUYET_Lv3':'#ff7b7b',
                            'KHOI THAM DINH VA PHE DUYET_Lv4':'#ff7b7b'}  
    highlight_color = '#CBF3D2'
    default_color = 'rgba(0, 0, 0, 0.05)'  

    
    # Function to check if a row includes the highlighted node
    def row_includes_highlighted_node(row, highlighted_nodes):
        return any(target in row[mapped_columns].values for target in highlighted_nodes)
        # return highlighted_node in row[mapped_columns].values

    # Populate source, target, values, and colors
    for _, row in data.iterrows():
        
        row_highlighted = row_includes_highlighted_node(row, highlighted_nodes)
        
        for i in range(len(mapped_columns) - 1):
            source = node_mapping[row[mapped_columns[i]]]
            target = node_mapping[row[mapped_columns[i + 1]]]
            value = row[size_column]
            sources.append(source)
            targets.append(target)
            values.append(value)
            colors.append(color_list[target] if row_highlighted else default_color) #highlight_color
            if row_highlighted:
                print(highlight_color)
                print(row[mapped_columns[i]])
                print(source)
                print(color_list[source])
                print('_' * 10  )
            
    for node in data[mapped_columns[-1]].unique():
        sources.append(node_mapping[node])
        targets.append(node_mapping[''])
        values.append(10**-10)
        colors.append('rgba(255, 255, 255, 0.05)')

    percentage_map = {}
    for col in mapped_columns:
        calculated_df =  data[[col, size_column]]
        calculated_sum = calculated_df[size_column].sum()
        percentage_df = calculated_df.groupby([col])[size_column].sum() / calculated_sum * 100
        percentage_map.update(percentage_df)
    percentage_map[''] = 100

    custom_percentage_data = []
    for key in node_mapping:
        custom_percentage_data.append(percentage_map[key])

    
    if color_map == False:
        fig = go.Figure(data=[go.Sankey(
        valueformat = ",.5r",
        valuesuffix = " VND",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="white"),
            label=list(node_mapping.keys()),
            hovertemplate='<b>%{label} được nhận tổng cộng %{value}<b> <extra></extra>',
            hoverlabel=dict(
                font_size=20,
                font_family="Rockwell"),
            color="rgba(255, 199, 47, 0.5)",
            
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            hovertemplate='<b>%{source.label} phân bổ đến %{target.label} tổng cộng %{value}<b> <extra></extra>',
            color=colors  
        )
    )])
    
    
    else:
        hovertemplate_1 = "<br>".join([
                    "<b>Node:</b> %{label}",
                    "<b>Sum:</b> %{value}<extra></extra>",
                    '<b>Percentage:<b> %{customdata:.2f} %<br>'
                    ])
        hovertemplate_2 = "<br>".join([
                    "<b>From:</b> %{source.label}",
                    "<b>To:</b> %{target.label}",
                    "<b>Sum:</b> %{value}<extra></extra>"
                    ])

        fig = go.Figure(data=[go.Sankey(
            valueformat = ",.5r",
            valuesuffix = " VND",
            node=dict(
                pad=15,
                thickness=15,
                line=dict(color="white"),
                label=list(node_mapping.keys()),
                color=color_list, 
                customdata= custom_percentage_data,
                hovertemplate= hovertemplate_1,
                hoverlabel=dict(
                    font_size=20,
                    font_family="Rockwell")
        ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=colors,
                hovertemplate=hovertemplate_2,
                hoverlabel=dict(
                    font_size=20,
                    font_family="Rockwell")
        ))])
    
    fig.update_layout(autosize=autosize, width=1920, height=1080)

    fig.update_layout(font_family="Arial", font_color="blue", font_size=14)
    fig.update_layout(title_text= title, title_font_size=24)
    fig.update_layout(xaxis_visible=False, xaxis_showticklabels=False,
                        yaxis_visible=False, yaxis_showticklabels=False)
    
    return fig

def calculate_distribution(data, highlighted_nodes, size_column= 'Size', page_flag= 1):
    if len(highlighted_nodes) == 0:
        return None

    def calculate_percentage(df, level_column, size_column, page_flag= 1):
        grouped_df = df[[level_column, size_column]].groupby(level_column)[size_column].sum().reset_index()
        total_size = grouped_df[size_column].sum()
        grouped_df[f'Percentage_{level_column}'] = grouped_df[size_column] / total_size * 100
        grouped_df = grouped_df.sort_values(by= f'Percentage_{level_column}', ascending=False, ignore_index= True)
        if page_flag == 1:
            return grouped_df.drop(size_column, axis=1).set_index(grouped_df.columns[0])
        else:
            return grouped_df.drop(size_column, axis=1)
    
    values_to_filter = highlighted_nodes
    filtered_df = data[data.isin(values_to_filter).any(axis=1)]
    filtered_columns = filtered_df.columns
    filtered_columns = filtered_columns.drop(size_column)
    
    if page_flag == 1:
        for col in filtered_columns:
            filtered_df[col] = filtered_df[col].str[:-4]

    results = []
    for col in filtered_columns:
        result = calculate_percentage(filtered_df, col, size_column, page_flag)
        results.append(result)

    final_result = pd.concat(results, axis=1)
    final_result.sort_values(by=final_result.select_dtypes(include=np.number).columns.to_list(), ascending=False, na_position='last', inplace= True)
    
    if page_flag == 1:
        return final_result.reset_index()
    else:
        return final_result

def generate_format(column_name):
    modified_list = [item.replace('_mapped', '') for item in column_name]
    modified_list = [item.replace('_map', '') for item in modified_list]
    format_dict = {}

    for orig, mod in zip(column_name, modified_list):
        if orig.startswith('Percentage_'):
            format_dict[orig] = st.column_config.NumberColumn(mod, format="%.2f %%")
        else:
            format_dict[orig] = mod
    return format_dict

def sub_table(df, highlighted_nodes, size_column,  page_flag):
    dist_result = calculate_distribution(df, highlighted_nodes, size_column, page_flag)
    format_dict = generate_format(dist_result.columns)
    st.dataframe(dist_result, hide_index= True, use_container_width= True, column_config= format_dict)  

def sub_graph(df, highlighted_nodes, selected_columns, size_column, color_map):
    highlighted_df = df[df.isin(highlighted_nodes).any(axis=1)]
    sub_fig = sankey_graph(highlighted_df, selected_columns, highlighted_nodes, 
                            title= "Highlighted", size_column= size_column, color_map= color_map, autosize= True)
    st.plotly_chart(sub_fig) 

def graph(df, selected_columns, size_column, highlighted_nodes, color_map, title, page_flag):
    if len(highlighted_nodes) != 0:
        sub_df = df.groupby(selected_columns).agg({size_column: 'sum'}).reset_index()
        sub_graph(sub_df, highlighted_nodes, selected_columns, size_column, color_map)

        fig = sankey_graph(sub_df, selected_columns, highlighted_nodes, title= title, 
                            size_column= size_column, color_map= color_map, autosize= False)
        st.plotly_chart(fig)

        sub_table(sub_df, highlighted_nodes, size_column, page_flag = page_flag)
    else:
        sub_df = df.groupby(selected_columns).agg({size_column: 'sum'}).reset_index()
        fig = sankey_graph(sub_df, selected_columns, highlighted_nodes, title= title, 
                            size_column= size_column, color_map= color_map, autosize= False)
        
        st.plotly_chart(fig)
        