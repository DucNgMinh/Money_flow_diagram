import numpy as np
import pandas as pd

import plotly.graph_objects as go   

import streamlit as st
import extra_streamlit_components as stx

@st.cache_data
def load_data():
    # load map data
    map_df = pd.read_csv(r'map.csv')
    map_name = map_df.set_index('ORG_UNIT_ID')['LEVEL_02_NAME'].to_dict()

    # load transaction data
    trans_df = pd.read_csv(r'sample data lv pk.csv')[['Lv0', 'Lv1', 'Lv2', 'Lv3', 'Lv4', 'Size']]
    
    # create mapped columns for trans_df
    map_columns = ['Lv0', 'Lv1', 'Lv2', 'Lv3', 'Lv4']
    mapped_columns = [ col + '_mapped' for col in map_columns]
    for i, j in zip(map_columns, mapped_columns):
        trans_df[j] = trans_df[i].map(map_name)
        trans_df[j] = trans_df[j] + '_' + i

    all_lv_df = trans_df.groupby(mapped_columns)['Size'].sum().reset_index()
    lv_04_df = trans_df.groupby(['Lv0_mapped', 'Lv4_mapped'])['Size'].sum().reset_index()

    # load allocation data
    al_df = pd.read_csv(r'./Hai ha/KQ phan bo GD2_T092023.csv')
    al_df.rename(columns = {'Chi phí nhận phân bổ tại thời điểm':'Size'}, inplace = True)

    # create mapped columns for al_df
    al_df['Mã đơn vị tổ chức cấp 6_map'] = al_df['Mã đơn vị tổ chức cấp 6'].map(map_name) 
    al_df['Mã SP cấp 5 PK'] = al_df['Mã SP cấp 5'].astype(str).str[:2]

    pk_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_map',  'Tên phân khúc KH cấp 3'])['Size'].sum().reset_index()
    
    sp_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_map', 'Mã SP cấp 5 PK'])['Size'].sum().reset_index()
    sp_df['Mã SP cấp 5 PK'] = 'SP_' + sp_df['Mã SP cấp 5 PK'].apply(str)
    
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
    
    color_map = dict(zip(node_list, color_list))
        
    pk_list = ['KHACH HANG DAU TU', 'KHACH HANG CA NHAN VIP',
                'KHACH HANG DOANH NGHIEP LON',
                'KHACH HANG DOANH NGHIEP VUA VA NHO (SMEs)',
                'KHACH HANG DOANH NGHIEP QUY MO SIEU NHO (ME)',
                'KHACH HANG DOANH NGHIEP CO VON DAU TU NUOC NGOAI (FIE)',
                'KHACH HANG CA NHAN THONG THUONG', 'KHACH HANG CA NHAN THAN THIET',
                'KHACH HANG DINH CHE TAI CHINH', 'KHACH HANG AO KHOI BAN BUON',
                'UNALLOCABLE', 'KHACH HANG KINH DOANH VON VA TIEN TE',
                'KHACH HANG NGUON VON UY THAC QUOC TE', 'KHACH HANG KHAC',
                'BO PHAN CHUNG', 'SO NGAN HANG']
    
    return node_list, color_list, color_map, pk_list

@st.cache_data
def load_content():
    page_1 = open("./Tailieu/Page1.txt", "r", encoding="utf8").read()
    page_2 = open("./Tailieu/Page2.txt", "r", encoding="utf8").read()
    page_3 = open("./Tailieu/Page3.txt", "r", encoding="utf8").read()
    page_4 = open("./Tailieu/Page4.txt", "r", encoding="utf8").read()

    return page_1, page_2, page_3, page_4

def sankey_graph(data, mapped_columns, highlighted_nodes, title):
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

    highlight_color = 'rgba(255, 0, 0, 0.5)'  
    default_color = 'rgba(0, 0, 0, 0.1)'  

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
            color=colors  
        )
    )])

    fig.update_layout(title_text= title,  
                    title_font_size=24)
    fig.update_layout(autosize=False, width=1620, height=1080,
                      xaxis_visible=False, xaxis_showticklabels=False,
                        yaxis_visible=False, yaxis_showticklabels=False)
    return fig

def calculate_distribution(data, highlighted_nodes):
    if len(highlighted_nodes) == 0:
        return None

    def calculate_percentage(df, level_column, size_column):
        grouped_df = df[[level_column, size_column]].groupby(level_column)[size_column].sum().reset_index()
        total_size = grouped_df[size_column].sum()
        grouped_df[f'Percentage_{level_column[2]}'] = grouped_df[size_column] / total_size 
        return grouped_df.drop(size_column, axis=1)
    
    values_to_filter = highlighted_nodes
    filtered_df = data[data.isin(values_to_filter).any(axis=1)]
    filtered_columns = filtered_df.columns
    filtered_columns = filtered_columns.drop('Size')
    for col in filtered_columns:
        filtered_df[col] = filtered_df[col].str[:-4]

    results = []
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

def main():
    st.set_page_config(layout="wide")
    st.title("Money Flow Diagram !!!!!")

    chosen_id = stx.tab_bar(data=[
        stx.TabBarItemData(id=1, title="Phân bổ Giai đoạn 1:", description="Từ trung tâm đến trung tâm"),
        stx.TabBarItemData(id=2, title="Phân bổ giai đoạn 2:", description="Từ CPQLKD trực tiếp đến Phân khúc Khách hàng"),
        stx.TabBarItemData(id=3, title="Phân bổ giai đoạn 3:", description="Từ CPQLKD trực tiếp đến Sản phẩm"),
        stx.TabBarItemData(id=4, title="Phân bổ giai đoạn 4:", description="Từ Đơn vị nhận phân bổ đến Sản phẩm, Phân khúc Khách"),
    ], default=1)

    node_list, color_list, color_map, pk_list = load_option()
    # load data into cache
    all_lv_df, lv_04_df, pk_df, sp_df, sp_pk_df = load_data()

    # load content into cache
    page_1, page_2, page_3, page_4 = load_content()

    if chosen_id == '1':
        option = st.selectbox('Option', ('Level 0 and 4', 'Level 0 to 4'))
        if option == 'Level 0 and 4':
            selected_columns = ['Lv0_mapped', 'Lv4_mapped']

            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv0' for node in node_list])
            highlighted_node_l4 = layer1_column.multiselect('Filter layer 4', [node + '_Lv4' for node in node_list])
            
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l4

            fig = sankey_graph(lv_04_df, selected_columns, highlighted_nodes, title= "<b>Phân bổ giai đoạn 1: Từ trung tâm đến trung tâm</b>")
            st.plotly_chart(fig)
            dist_result = calculate_distribution(lv_04_df, highlighted_nodes)
            st.dataframe(dist_result)

        else:
            selected_columns = ['Lv0_mapped', 'Lv1_mapped', 'Lv2_mapped', 'Lv3_mapped', 'Lv4_mapped']
            layer0_column, layer1_column, layer2_column, layer3_column, layer4_column = st.columns(5)

            highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv0' for node in node_list])
            highlighted_node_l2 = layer1_column.multiselect('Filter layer 2', [node + '_Lv1' for node in node_list])
            highlighted_node_l3 = layer2_column.multiselect('Filter layer 3', [node + '_Lv2' for node in node_list])
            highlighted_node_l4 = layer3_column.multiselect('Filter layer 4', [node + '_Lv3' for node in node_list])
            highlighted_node_l5 = layer4_column.multiselect('Filter layer 5', [node + '_Lv4' for node in node_list])
            
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l2 + highlighted_node_l3 + highlighted_node_l4 + highlighted_node_l5

            fig = sankey_graph(all_lv_df, selected_columns, highlighted_nodes, title= "<b>Phân bổ giai đoạn 1: Từ trung tâm đến trung tâm</b>")
            st.plotly_chart(fig)
            dist_result = calculate_distribution(all_lv_df, highlighted_nodes)
            st.dataframe(dist_result)        

        st.markdown(page_1)
        
    elif chosen_id == '2':
        on = st.toggle('Hiển thị Level 4')
        if on:
            st.write('Hiển thị Level 4')
            layer0_column, layer1_column, layer2_column = st.columns(3)

            highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv1' for node in node_list])
            highlighted_node_l4 = layer1_column.multiselect('Filter layer 4', [node + '_Lv4' for node in node_list])
            highlighted_node_pk = layer2_column.multiselect('Filter layer Phân khúc', [node for node in pk_list])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l4 + highlighted_node_pk
        else:
            st.write('Không hiển thị Level 4')

            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv1' for node in node_list])
            highlighted_node_pk = layer1_column.multiselect('Filter layer Phân khúc', [node for node in pk_list])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_pk

        selected_columns = ['Mã đơn vị tổ chức cấp 6_map',  'Tên phân khúc KH cấp 3']
        fig = sankey_graph(pk_df, selected_columns, highlighted_nodes, title= "<b>Phân bổ giai đoạn 2: Từ CPQLKD trực tiếp đến PKKH</b>")
        st.plotly_chart(fig)
        dist_result = calculate_distribution(all_lv_df, highlighted_nodes)
        st.dataframe(dist_result)  

        st.markdown(page_2)

    elif chosen_id == '3':
        on = st.toggle('Hiển thị Level 4')
        if on:
            st.write('Hiển thị Level 4')
            layer0_column, layer1_column, layer2_column = st.columns(3)

            highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv1' for node in node_list])
            highlighted_node_l4 = layer1_column.multiselect('Filter layer 4', [node + '_Lv4' for node in node_list])
            highlighted_node_sp = layer2_column.multiselect('Filter layer Sản phẩm', [node + '_Lv3' for node in node_list])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l4 + highlighted_node_sp
        else:
            st.write('Không hiển thị Level 4')

            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv1' for node in node_list])
            highlighted_node_sp = layer1_column.multiselect('Filter layer Sản phẩm', [node + '_Lv3' for node in node_list])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_sp

        selected_columns = ['Mã đơn vị tổ chức cấp 6_map', 'Mã SP cấp 5 PK']
        fig = sankey_graph(sp_df, selected_columns, highlighted_nodes, title= "<b>Phân bổ giai đoạn 2: Từ CPQLKD trực tiếp đến PKKH</b>")
        st.plotly_chart(fig)
        dist_result = calculate_distribution(sp_df, highlighted_nodes)
        st.dataframe(dist_result) 

        st.markdown(page_3)

    else:
        layer0_column, layer1_column = st.columns(2)

        highlighted_node_pk = layer0_column.multiselect('Filter layer Phân khúc', [node for node in pk_list])
        highlighted_node_sp = layer1_column.multiselect('Filter layer Sản phẩm', [node + '_Lv4' for node in node_list])
        highlighted_nodes = highlighted_node_pk + highlighted_node_sp

        selected_columns = ['Mã đơn vị tổ chức cấp 6_map', 'Mã SP cấp 5 PK', 'Tên phân khúc KH cấp 3']
        fig = sankey_graph(sp_pk_df, selected_columns, highlighted_nodes, title= "<b>Phân bổ giai đoạn 2: Từ CPQLKD trực tiếp đến PKKH</b>")
        st.plotly_chart(fig)
        dist_result = calculate_distribution(sp_pk_df, highlighted_nodes)
        st.dataframe(dist_result) 

        st.markdown(page_4)
        
if __name__ == '__main__':
    main()