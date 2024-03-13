import numpy as np
import pandas as pd
import plotly.graph_objects as go   

import streamlit as st
import extra_streamlit_components as stx

@st.cache_data
def load_data():
    # load map data
    # map_df = pd.read_csv(r'map.csv')
    # map_name = map_df.set_index('ORG_UNIT_ID')['LEVEL_02_NAME'].to_dict()
    map_1_df = pd.read_csv(r'map_moi.csv')
    map_name_1 = map_1_df.set_index('LEVEL_06_CODE ')['Tên khối'].to_dict()
    
    # load transaction data
    trans_df = pd.read_csv(r'sample data lv pk.csv')[['Lv0', 'Lv1', 'Lv2', 'Lv3', 'Lv4', 'Size']]
    
    # create mapped columns for trans_df
    map_columns = ['Lv0', 'Lv1', 'Lv2', 'Lv3', 'Lv4']
    mapped_columns = [ col + '_mapped' for col in map_columns]
    for i, j in zip(map_columns, mapped_columns):
        trans_df[j] = trans_df[i].map(map_name_1)
        trans_df[j] = trans_df[j] + '_' + i

    all_lv_df = trans_df.groupby(mapped_columns)['Size'].sum().reset_index()
    lv_04_df = trans_df.groupby(['Lv0_mapped', 'Lv4_mapped'])['Size'].sum().reset_index()

    map_2_df = pd.read_csv(r'map.csv')
    map_name_2 = map_2_df.set_index('ORG_UNIT_ID')['LEVEL_02_NAME'].to_dict()

    # load allocation data
    al_df = pd.read_csv(r'./Hai ha/KQ phan bo GD2_T092023.csv')
    al_df.rename(columns = {'Chi phí nhận phân bổ tại thời điểm':'Size'}, inplace = True)

    al_df.dropna(inplace= True)

    # create mapped columns for al_df
    al_df['Mã đơn vị tổ chức cấp 6_map'] = al_df['Mã đơn vị tổ chức cấp 6'].map(map_name_2) 
    al_df['Mã SP cấp 5 PK'] = al_df['Mã SP cấp 5'].astype(str).str[:2]

    pk_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_map',  'Tên phân khúc KH cấp 3'])['Size'].sum().reset_index()
    
    sp_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_map', 'Mã SP cấp 5 PK'])['Size'].sum().reset_index()
    sp_df['Mã SP cấp 5 PK'] = 'SP_' + sp_df['Mã SP cấp 5 PK'].apply(str)
    
    def classify_number(number):
        if '990' in number or '996' in number:
            return 'TSC'
        elif '071' in number:
            return 'CNTT'
        else:
            return 'Khối chi nhánh'
        
    
    al_df['Mã đơn vị tổ chức cấp 6_map'] = al_df['Tên đơn vị tổ chức cấp 6'].apply(classify_number) 
    sp_pk_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_map', 'Mã SP cấp 5 PK', 'Tên phân khúc KH cấp 3'])['Size'].sum().reset_index()
    sp_pk_df['Mã SP cấp 5 PK'] = 'SP_' + sp_pk_df['Mã SP cấp 5 PK'].apply(str) 

    return all_lv_df, lv_04_df, pk_df, sp_df, sp_pk_df

@st.cache_data
def load_option():
    node_list = ['TT DICH VU NOI BO', 'TT QUAN LY CHUNG TOAN HANG', 'TT AO',
            'KHONG CO TRONG CAY', 'TT DOANH THU',
            'TT QUAN LY CHUNG KHOI KINH DOANH', 'TT HO TRO TRUC TIEP',
            'TT HO TRO SAN PHAM', 'TT QUAN LY CHUNG CHI NHANH']

    color_list = ['rgba(44, 160, 44, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(140, 86, 75, 0.8)',
            'rgba(23, 190, 207, 0.8)', 'rgba(188, 189, 34, 0.8)', 'rgba(214, 39, 40, 0.8)',
            'rgba(188, 189, 34, 0.8)', 'rgba(31, 119, 180, 0.8)', 'rgba(140, 86, 75, 0.8)']
    
    # color_map = dict(zip(node_list, color_list))
    
    df = pd.read_csv('ColorMap.csv')
    color_map_v1 = dict(zip(df['TÊN GỐC'].to_list(), df['Màu'].to_list()))

    df = pd.read_csv('ColorMapV2.csv')
    color_map_v2 = dict(zip(df['Tên khối'].to_list(), df['Màu'].to_list()))

    df = pd.read_csv('ColorMapV3.csv')
    color_map_v3 = dict(zip(df['Tên trung tâm'].to_list(), df['Màu'].to_list()))
    return node_list, color_list, color_map_v1, color_map_v2, color_map_v3

def load_content():
    page_1 = open("./Tailieu/Page1.txt", "r", encoding="utf8").read()
    page_2 = open("./Tailieu/Page2.txt", "r", encoding="utf8").read()
    page_3 = open("./Tailieu/Page3.txt", "r", encoding="utf8").read()
    page_4 = open("./Tailieu/Page4.txt", "r", encoding="utf8").read()

    return page_1, page_2, page_3, page_4

def sankey_graph(data, mapped_columns, highlighted_nodes, title, color_map= False, autosize= False):
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
            if len(node) > 5:
                base_node = node.split('_')[0]
                if base_node in color_map:
                    new_color_list.append(color_map[base_node])
                else:
                    new_color_list.append('#CB99C9')  # Default color for unmatched nodes
            else:
                if node in color_map:
                    new_color_list.append(color_map[node])
                else:
                    new_color_list.append('#CB99C9')  # Default color for unmatched nodes
        return new_color_list
    
    # Create the node mapping
    node_mapping = create_node_mapping(data, mapped_columns)
    node_mapping[''] = len(node_mapping)

    # Prepare source, target, and value lists for the Sankey diagram
    sources = []
    targets = []
    values = []
    colors = []  

    highlight_color = '#9DBC98'  
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
            value = row['Size']
            sources.append(source)
            targets.append(target)
            values.append(value)
            colors.append(highlight_color if row_highlighted else default_color)

    for node in data[mapped_columns[-1]].unique():
        print(node)
        sources.append(node_mapping[node])
        targets.append(node_mapping[''])
        values.append(10**-10)
        colors.append('rgba(255, 255, 255, 0.05)')

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
                    "<b>Sum:</b> %{value}<extra></extra>"
                    ])
        hovertemplate_2 = "<br>".join([
                    "<b>From:</b> %{source.label}",
                    "<b>To:</b> %{target.label}",
                    "<b>Sum:</b> %{value}<extra></extra>"
                    ])

        color_list = create_color_list(node_mapping, color_map)
        fig = go.Figure(data=[go.Sankey(
            valueformat = ",.5r",
            valuesuffix = " VND",
            node=dict(
                pad=15,
                thickness=15,
                line=dict(color="white"),
                label=list(node_mapping.keys()),
                color=color_list, 
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
    
    if autosize == False:
        fig.update_layout(autosize=autosize, width=1920, height=1080)

    fig.update_layout(font_family="Arial", font_color="blue", font_size=14)
    fig.update_layout(title_text= title, title_font_size=24)
    fig.update_layout(xaxis_visible=False, xaxis_showticklabels=False,
                        yaxis_visible=False, yaxis_showticklabels=False)
    
    return fig

def calculate_distribution(data, highlighted_nodes, page_flag= 1):
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
    filtered_columns = filtered_columns.drop('Size')
    
    if page_flag == 1:
        for col in filtered_columns:
            filtered_df[col] = filtered_df[col].str[:-4]

    results = []
    for col in filtered_columns:
        result = calculate_percentage(filtered_df, col, 'Size', page_flag)
        results.append(result)

    final_result = pd.concat(results, axis=1)
    
    final_result.sort_values(by=final_result.select_dtypes(include=np.number).columns.to_list(), ascending=False, na_position='last', inplace= True)
    return final_result.reset_index()

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

def main():
    st.set_page_config(layout="wide")
    st.title("Money Flow Diagram Test !!!!!")

    chosen_id = stx.tab_bar(data=[
        stx.TabBarItemData(id=1, title="Phân bổ Giai đoạn 1:", description="Từ trung tâm đến trung tâm"),
        stx.TabBarItemData(id=2, title="Phân bổ giai đoạn 2:", description="Từ CPQLKD trực tiếp đến Phân khúc Khách hàng"),
        stx.TabBarItemData(id=3, title="Phân bổ giai đoạn 3:", description="Từ CPQLKD trực tiếp đến Sản phẩm"),
        stx.TabBarItemData(id=4, title="Phân bổ giai đoạn 4:", description="Từ Đơn vị nhận phân bổ đến Sản phẩm, Phân khúc Khách"),
    ], default=1)

    option0_column, option1_column = st.columns([1, 3])
    option = option0_column.radio("Chọn đơn vị chi tiết",
        ["Khối", "Trung tâm"])

    option0_column.write(f'You selected: {option}') 

    start_color, end_color = option1_column.select_slider(
        'Select a range of color wavelength',
        options=['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'],
        value=('red', 'blue'))
    option1_column.write(f'You selected wavelengths between {start_color}, and, {end_color}')
    
    node_list, color_list, color_map_v1, color_map_v2, color_map_v3  = load_option()
    # load data into cache
    all_lv_df, lv_04_df, pk_df, sp_df, sp_pk_df = load_data()
    map_df = pd.read_csv(r'map_moi.csv')
    # load content into cache
    page_1, page_2, page_3, page_4 = load_content()

    if chosen_id == '1':
        option = st.selectbox('Option', ('Level 1 and 5', 'Level 1 to 5'))
        if option == 'Level 1 and 5':
            selected_columns = ['Lv0_mapped', 'Lv4_mapped']

            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv0' for node in map_df['Tên khối'].dropna().unique()])
            highlighted_node_l4 = layer1_column.multiselect('Filter layer 4', [node + '_Lv4' for node in map_df['Tên khối'].dropna().unique()])
            
            highlighted_nodes_1 = highlighted_node_l1 + highlighted_node_l4
            
            fig = sankey_graph(lv_04_df, selected_columns, highlighted_nodes_1, title= "<b>Phân bổ giai đoạn 1: Từ trung tâm đến trung tâm</b>", color_map= color_map_v2)
            st.plotly_chart(fig, autosize= True)
            
            if len(highlighted_nodes_1) != 0:
                dist_result = calculate_distribution(lv_04_df, highlighted_nodes_1)
                format_dict = generate_format(dist_result.columns)
                st.dataframe(dist_result, hide_index= True, use_container_width= True, column_config= format_dict)

                highlighted_df = lv_04_df[lv_04_df.isin(highlighted_nodes_1).any(axis=1)]
                # st.dataframe(highlighted_df)
                sub_fig = sankey_graph(highlighted_df, selected_columns, highlighted_nodes_1, title= "Highlighted", color_map= color_map_v2)
                st.plotly_chart(sub_fig)
                st.write(highlighted_nodes_1)
        else:
            selected_columns = ['Lv0_mapped', 'Lv1_mapped', 'Lv2_mapped', 'Lv3_mapped', 'Lv4_mapped']
            layer0_column, layer1_column, layer2_column, layer3_column, layer4_column = st.columns(5)

            highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv0' for node in map_df['Tên khối'].dropna().unique()])
            highlighted_node_l2 = layer1_column.multiselect('Filter layer 2', [node + '_Lv1' for node in map_df['Tên khối'].dropna().unique()])
            highlighted_node_l3 = layer2_column.multiselect('Filter layer 3', [node + '_Lv2' for node in map_df['Tên khối'].dropna().unique()])
            highlighted_node_l4 = layer3_column.multiselect('Filter layer 4', [node + '_Lv3' for node in map_df['Tên khối'].dropna().unique()])
            highlighted_node_l5 = layer4_column.multiselect('Filter layer 5', [node + '_Lv4' for node in map_df['Tên khối'].dropna().unique()])
            
            highlighted_nodes_1 = highlighted_node_l1 + highlighted_node_l2 + highlighted_node_l3 + highlighted_node_l4 + highlighted_node_l5

            fig = sankey_graph(all_lv_df, selected_columns, highlighted_nodes_1, title= "<b>Phân bổ giai đoạn 1: Từ trung tâm đến trung tâm</b>", color_map= color_map_v2)
            st.plotly_chart(fig)
            
            if len(highlighted_nodes_1) != 0:
                dist_result = calculate_distribution(all_lv_df, highlighted_nodes_1)
                format_dict = generate_format(dist_result.columns)
                st.dataframe(dist_result, hide_index= True, use_container_width= True, column_config= format_dict)   

                highlighted_df = all_lv_df[all_lv_df.isin(highlighted_nodes_1).any(axis=1)]
                # st.dataframe(highlighted_df)
                sub_fig = sankey_graph(highlighted_df, selected_columns, highlighted_nodes_1, title= "Highlighted", color_map= color_map_v2)
                st.plotly_chart(sub_fig)

        st.markdown(page_1)

    elif chosen_id == '2':
        layer0_column, layer1_column = st.columns(2)
        highlighted_node_l1 = layer0_column.multiselect('Filter Đơn vị tổ chức', [node for node in pk_df['Mã đơn vị tổ chức cấp 6_map'].unique()])
        highlighted_node_pk = layer1_column.multiselect('Filter Phân khúc', [node for node in pk_df['Tên phân khúc KH cấp 3'].unique()])
        highlighted_nodes = highlighted_node_l1 + highlighted_node_pk

        selected_columns = ['Mã đơn vị tổ chức cấp 6_map',  'Tên phân khúc KH cấp 3']
        fig = sankey_graph(pk_df, selected_columns, highlighted_nodes, title= "<b>Phân bổ giai đoạn 2: Từ CPQLKD trực tiếp đến PKKH</b>", color_map= color_map_v3)
        st.plotly_chart(fig)
        if len(highlighted_nodes) != 0:
            dist_result = calculate_distribution(pk_df, highlighted_nodes, page_flag = 2)
            format_dict = generate_format(dist_result.columns)
            st.dataframe(dist_result, hide_index= True, use_container_width= True, column_config= format_dict)  

            highlighted_df = pk_df[pk_df.isin(highlighted_nodes).any(axis=1)]
            sub_fig = sankey_graph(highlighted_df, selected_columns, highlighted_nodes, title= "Highlighted", color_map= color_map_v3)
            st.plotly_chart(sub_fig)
        st.markdown(page_2)

    elif chosen_id == '3':
        layer0_column, layer1_column = st.columns(2)
        highlighted_node_l1 = layer0_column.multiselect('Filter Đơn vị tổ chức', [node for node in sp_df['Mã đơn vị tổ chức cấp 6_map'].unique()])
        highlighted_node_sp = layer1_column.multiselect('Filter Sản phẩm', [node for node in sp_df['Mã SP cấp 5 PK'].unique()])
        highlighted_nodes = highlighted_node_l1 + highlighted_node_sp

        selected_columns = ['Mã đơn vị tổ chức cấp 6_map', 'Mã SP cấp 5 PK']
        fig = sankey_graph(sp_df, selected_columns, highlighted_nodes, title= "<b>Phân bổ giai đoạn 3: Từ CPQLKD trực tiếp đến Sản phẩm</b>", color_map= color_map_v3)
        st.plotly_chart(fig)
        if len(highlighted_nodes) != 0:
            dist_result = calculate_distribution(sp_df, highlighted_nodes, page_flag = 3)
            format_dict = generate_format(dist_result.columns)
            st.dataframe(dist_result, hide_index= True, use_container_width= True, column_config= format_dict)  

            highlighted_df = sp_df[sp_df.isin(highlighted_nodes).any(axis=1)]
            sub_fig = sankey_graph(highlighted_df, selected_columns, highlighted_nodes, title= "Highlighted", color_map= color_map_v3)
            st.plotly_chart(sub_fig)

        st.markdown(page_3)

    else:
        layer0_column, layer1_column, layer2_column = st.columns(3)

        highlighted_node_pk = layer0_column.multiselect('Filter Đơn vị tổ chức', [node for node in sp_pk_df['Mã đơn vị tổ chức cấp 6_map'].unique()])
        highlighted_node_sp = layer1_column.multiselect('Filter Sản phẩm', [node for node in sp_pk_df['Mã SP cấp 5 PK'].unique()])
        highlighted_node_pk = layer2_column.multiselect('Filter Phân khúc', [node for node in sp_pk_df['Tên phân khúc KH cấp 3'].unique()])
        

        highlighted_nodes = highlighted_node_pk + highlighted_node_sp

        selected_columns = ['Mã đơn vị tổ chức cấp 6_map', 'Mã SP cấp 5 PK', 'Tên phân khúc KH cấp 3']
        fig = sankey_graph(sp_pk_df, selected_columns, highlighted_nodes, title= "<b>Phân bổ giai đoạn 4: Từ Đơn vị nhận phân bổ đến Sản phẩm, Phân khúc Khách</b>", color_map= color_map_v3)
        st.plotly_chart(fig)
        if len(highlighted_nodes) != 0:
            dist_result = calculate_distribution(sp_pk_df, highlighted_nodes, page_flag = 4)
            format_dict = generate_format(dist_result.columns)
            st.dataframe(dist_result, hide_index= True, use_container_width= True, column_config= format_dict) 

            highlighted_df = sp_pk_df[sp_pk_df.isin(highlighted_nodes).any(axis=1)]
            sub_fig = sankey_graph(highlighted_df, selected_columns, highlighted_nodes, title= "Highlighted", color_map= color_map_v3)
            st.plotly_chart(sub_fig)

        st.markdown(page_4)
        
if __name__ == '__main__':
    main()