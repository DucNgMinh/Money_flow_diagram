import numpy as np
import pandas as pd
import copy

import plotly.graph_objects as go   

import streamlit as st
import extra_streamlit_components as stx

from utils import *

@st.cache_data
def load_data():
    # trans
    map_df = pd.read_csv('Map_V1.csv')
    map_tt = map_df.set_index('LEVEL_06_CODE')['LEVEL_05_NAME'].to_dict()
    map_khoi = map_df.set_index('LEVEL_06_CODE')['LEVEL_TEN_GOC_NAME'].to_dict()

    # load transaction data
    trans_df = pd.read_csv(r'sample data lv pk.csv')[['Lv0', 'Lv1', 'Lv2', 'Lv3', 'Lv4', 'Size']]

    map_columns = ['Lv0', 'Lv1', 'Lv2', 'Lv3', 'Lv4']
    mapped_columns = [ col + '_mapped' for col in map_columns]

    # create map (khoi) df for trans_df
    trans_df_khoi = copy.deepcopy(trans_df)
    for i, j in zip(map_columns, mapped_columns):
        trans_df_khoi[j] = trans_df[i].map(map_khoi)
        trans_df_khoi[j] = trans_df_khoi[j] + '_' + i
    trans_df_khoi.drop(map_columns, axis= 1, inplace= True)
    all_lv_khoi_df = trans_df_khoi.groupby(mapped_columns)['Size'].sum().reset_index()
    lv_04_khoi_df = trans_df_khoi.groupby(['Lv0_mapped', 'Lv4_mapped'])['Size'].sum().reset_index()

    # cfpb
    cfpb_df = pd.read_parquet('./Real-data/PB_CF_to_SP_NKH.parquet')
    map_org_cost_type = pd.read_csv('./Real-data/Phân loại cost type và CP Phân loại phòng - Cost ID Type.csv')
    map_cost_type = pd.read_csv('./Real-data/Phân loại cost type và CP Phân loại phòng - Phân Loại Cost Type.csv')
    map_org_division_type = pd.read_csv('./Real-data/Phân loại cost type và CP Phân loại phòng - Phân Loại Phong.csv')

    map_org_to_cost_type = map_org_cost_type.set_index(['TO_ORG_UNIT_ID'])['TO_COST_TYPE_ID'].to_dict()
    map_cost_type_name = map_cost_type.set_index(['Mã Cost_type'])['Tên Cost_type'].to_dict()
    map_org_to_division_type = map_org_division_type.set_index(['LEVEL_06_CODE'])['Ghi chú phân loại phòng'].to_dict()

    cfpb_df['COST_TYPE'] = cfpb_df['Mã đơn vị tổ chức cấp 6'].map(map_org_to_cost_type)
    cfpb_df['COST_TYPE_NAME'] = cfpb_df['COST_TYPE'].map(map_cost_type_name)


    map_sp_df = pd.read_excel('./Real-data/2023-12-13 Cây phân cấp phục vụ phân bổ Sanky Chart.xlsx', 
                          sheet_name= 'Product_Hierarchy final to FIS')
    map_sp = map_sp_df.set_index('PRODUCT_LEAF_ID')['LEVEL2_DESC'].to_dict()

    cfpb_df['Mã đơn vị tổ chức cấp 6_phong'] = cfpb_df['Mã đơn vị tổ chức cấp 6'].map(map_org_to_division_type)
    cfpb_df['Mã SP cấp 5 PK'] = cfpb_df['Mã SP cấp 5'].map(map_sp)

    groupby_columns = ['Tháng', 'COST_TYPE_NAME', 'Mã đơn vị tổ chức cấp 6_phong', 'Mã SP cấp 5 PK','Mã phân khúc KH cấp 3', 'Tên phân khúc KH cấp 3']
    pk_df = cfpb_df.groupby(groupby_columns).agg({'Chi phí nhận phân bổ tại thời điểm': 'sum'}).reset_index()

    return all_lv_khoi_df, lv_04_khoi_df, pk_df

@st.cache_data
def load_color_map():
    map_df = pd.read_csv('Map_V1.csv')
    map_khoi_color = map_df.set_index('LEVEL_TEN_GOC_NAME')['LEVEL_TEN_GOC_COLOR'].to_dict()

    map_cost_type_color = pd.read_csv('Map_Cost_Type_V2.csv')
    map_cost_type_color = map_cost_type_color.set_index(['Tên Cost_type'])['Cost_type_COLOR'].to_dict()

    map_pkkh = pd.read_csv('Map_PKKH_V2.csv')
    map_pkkh = map_pkkh.set_index(['Tên phân khúc KH cấp 3'])['COST_TYPE_COLOR'].to_dict()

    sp_df = pd.read_csv('Map_SP_V2.csv')
    map_sp_color = sp_df.set_index(['LEVEL2_DESC'])['LEVEL2_COLOR'].to_dict()

    phong_df = pd.read_csv('Map_Phong_V1.csv')
    map_phong_color = phong_df.set_index(['Ten phong'])['Phong_TYPE_COLOR'].to_dict()

    map_color_app = {}
    map_color_app.update(map_khoi_color)
    map_color_app.update(map_cost_type_color)
    map_color_app.update(map_pkkh)
    map_color_app.update(map_sp_color)
    map_color_app.update(map_phong_color)
    return map_color_app


def main():
    st.set_page_config(layout="wide")
    st.title("Money Flow Diagram V3 Test !!!!!")

    if 'disabled' not in st.session_state:
        st.session_state.page_id = '1'
        st.session_state.disabled = False
        

    stx.tab_bar(data=[
        stx.TabBarItemData(id=1, title="Phân bổ Giai đoạn 1:", description="Từ trung tâm đến trung tâm"),
        stx.TabBarItemData(id=2, title="Phân bổ giai đoạn 2:", description="Từ CPQLKD trực tiếp đến Phân khúc Khách hàng"),
        stx.TabBarItemData(id=3, title="Phân bổ giai đoạn 3:", description="Từ CPQLKD trực tiếp đến Sản phẩm"),
        stx.TabBarItemData(id=4, title="Phân bổ giai đoạn 4:", description="Từ Đơn vị nhận phân bổ đến Sản phẩm, Phân khúc Khách hàng"),
    ], default=1, key= 'page_id')
    
    sub_1_column, sub_2_column, sub_3_column = st.columns([1, 1, 1])
    
    sub_1_column.checkbox("Chọn ẩn chi tiết", key="disabled") 
    
    filer_option = "AND"
    
    datetime_slider_start = sub_2_column.date_input(
    "Select a date range",
    min_value=start_date,
    max_value=end_date,
    value=start_date,
    format="YYYY/MM/DD")
    
    datetime_slider_end = sub_3_column.date_input(
        "Select a date range",
        min_value=start_date,
        max_value=end_date,
        value=end_date,
        format="YYYY/MM/DD")
    st.session_state['date_range'] = generate_year_month_range(datetime_slider_start, datetime_slider_end)

    all_lv_khoi_df, lv_04_khoi_df, pk_df = load_data()

    pk_df = pk_df[pk_df['Tháng'].isin(st.session_state['date_range'])]

    map_color_app = load_color_map()

    if st.session_state.page_id == '1':
        if st.session_state.disabled:
            selected_columns = ['Lv0_mapped', 'Lv4_mapped']
            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node for node in lv_04_khoi_df[selected_columns[0]].unique()])
            highlighted_node_l4 = layer1_column.multiselect('Filter layer 4', [node for node in lv_04_khoi_df[selected_columns[1]].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l4
            
            graph(lv_04_khoi_df, selected_columns, 'Size',
                  highlighted_nodes, map_color_app, 
                  title="<b>Phân bổ giai đoạn 1: Từ khối đến khối</b>",
                  page_flag=1, sub_graph_filter=filer_option)
            
        else:
            selected_columns = ['Lv0_mapped', 'Lv1_mapped', 'Lv2_mapped', 'Lv3_mapped', 'Lv4_mapped']
            layer0_column, layer1_column, layer2_column, layer3_column, layer4_column = st.columns(5)
            highlighted_node_l1 = layer0_column.multiselect('Lv1: Chi phí QLKDTT', [node for node in all_lv_khoi_df[selected_columns[0]].unique()])
            highlighted_node_l2 = layer1_column.multiselect('Lv2: Chi phí QLKDTT sau khi BCN phân bổ', [node for node in all_lv_khoi_df[selected_columns[1]].unique()])
            highlighted_node_l3 = layer2_column.multiselect('Lv3: Chi phí QLKDTT sau khi CNTT phân bổ', [node for node in all_lv_khoi_df[selected_columns[2]].unique()])
            highlighted_node_l4 = layer3_column.multiselect('Lv4: Chi phí QLKDTT sau khi VP phân bổ', [node for node in all_lv_khoi_df[selected_columns[3]].unique()])
            highlighted_node_l5 = layer4_column.multiselect('Lv5: Chi phí QLKDTT thực tế cuối cùng', [node for node in all_lv_khoi_df[selected_columns[4]].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l2 + highlighted_node_l3 + highlighted_node_l4 + highlighted_node_l5
            
            graph(all_lv_khoi_df, selected_columns, 'Size',
                  highlighted_nodes, map_color_app, 
                  title="<b>Phân bổ giai đoạn 1: Từ khối đến khối</b>",
                  page_flag=1, sub_graph_filter=filer_option)

    elif st.session_state.page_id == '2':
        if st.session_state.disabled:
            selected_columns = ['COST_TYPE_NAME', 'Tên phân khúc KH cấp 3']
            
            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter Cost Type', [node for node in pk_df[selected_columns[0]].unique()])
            highlighted_node_l2 = layer1_column.multiselect('Filter Phân khúc Khác hàng', [node for node in pk_df[selected_columns[1]].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l2

            graph(pk_df, selected_columns, 'Chi phí nhận phân bổ tại thời điểm',
                  highlighted_nodes, map_color_app, 
                  title="<b>Phân bổ giai đoạn 3: Từ Cost Type đến Sản phẩm</b>",
                  page_flag=2, sub_graph_filter=filer_option)
        else:
            selected_columns = ['COST_TYPE_NAME', 'Mã đơn vị tổ chức cấp 6_phong', 'Tên phân khúc KH cấp 3']

            layer0_column, layer1_column, layer2_column = st.columns(3)
            highlighted_node_l1 = layer0_column.multiselect('Filter Cost Type', [node for node in pk_df[selected_columns[0]].unique()])
            highlighted_node_l2 = layer1_column.multiselect('Filter Đơn vị Trung Gian', [node for node in pk_df[selected_columns[1]].unique()]) 
            highlighted_node_l3 = layer2_column.multiselect('Filter Phân khúc Khách hàng', [node for node in pk_df[selected_columns[2]].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l2 + highlighted_node_l3

            print([node for node in pk_df[selected_columns[1]].unique()])
            
            graph(pk_df, selected_columns, 'Chi phí nhận phân bổ tại thời điểm',
                  highlighted_nodes, map_color_app, 
                  title="<b>Phân bổ giai đoạn 3: Từ Cost Type đến Sản phẩm</b>",
                  page_flag=2, sub_graph_filter=filer_option)
                
    elif st.session_state.page_id == '3':
        if st.session_state.disabled:
            selected_columns = ['COST_TYPE_NAME',  'Mã SP cấp 5 PK']
            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter Cost Type', [node for node in pk_df[selected_columns[0]].unique()])
            highlighted_node_l2 = layer1_column.multiselect('Filter Phân khúc Sản phẩm', [node for node in pk_df[selected_columns[1]].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l2

            graph(pk_df, selected_columns, 'Chi phí nhận phân bổ tại thời điểm',
                  highlighted_nodes, map_color_app, 
                  title="<b>Phân bổ giai đoạn 3: Từ Cost Type đến Sản phẩm</b>",
                  page_flag=3, sub_graph_filter=filer_option)
        else:
            selected_columns = ['COST_TYPE_NAME', 'Mã đơn vị tổ chức cấp 6_phong', 'Mã SP cấp 5 PK']
            layer0_column, layer1_column, layer2_column = st.columns(3)
            highlighted_node_l1 = layer0_column.multiselect('Filter Cost Type', [node for node in pk_df[selected_columns[0]].unique()])
            highlighted_node_l2 = layer1_column.multiselect('Filter Đơn vị Trung Gian', [node for node in pk_df[selected_columns[1]].unique()]) 
            highlighted_node_l3 = layer2_column.multiselect('Filter Phân khúc Sản phẩm', [node for node in pk_df[selected_columns[2]].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l2 + highlighted_node_l3

            graph(pk_df, selected_columns, 'Chi phí nhận phân bổ tại thời điểm',
                  highlighted_nodes, map_color_app, 
                  title="<b>Phân bổ giai đoạn 3: Từ Cost Type đến Sản phẩm</b>",
                  page_flag=3, sub_graph_filter=filer_option)
                
    else:
        if st.session_state.disabled:
            selected_columns = ['COST_TYPE_NAME',  'Mã SP cấp 5 PK', 'Tên phân khúc KH cấp 3']
            layer0_column, layer1_column, layer2_column = st.columns(3)
            highlighted_node_l1 = layer0_column.multiselect('Filter Cost Type', [node for node in pk_df[selected_columns[0]].unique()])
            highlighted_node_l2 = layer1_column.multiselect('Filter Phân khúc Sản phẩm', [node for node in pk_df[selected_columns[1]].unique()])
            highlighted_node_l3 = layer2_column.multiselect('Filter Phân khúc Khách hàng', [node for node in pk_df[selected_columns[2]].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l2 + highlighted_node_l3

            graph(pk_df, selected_columns, 'Chi phí nhận phân bổ tại thời điểm',
                  highlighted_nodes, map_color_app, 
                  title="<b>Phân bổ giai đoạn 4: Từ Cost Type đến Sản phẩm, Phân khúc Khách hàng</b>",
                  page_flag=4, sub_graph_filter=filer_option)
        else:
            selected_columns = ['COST_TYPE_NAME', 'Mã đơn vị tổ chức cấp 6_phong', 'Mã SP cấp 5 PK', 'Tên phân khúc KH cấp 3']
            layer0_column, layer1_column, layer2_column, layer3_column = st.columns(4)
            highlighted_node_l1 = layer0_column.multiselect('Filter Cost Type', [node for node in pk_df[selected_columns[0]].unique()])
            highlighted_node_l2 = layer1_column.multiselect('Filter Đơn vị Trung Gian', [node for node in pk_df[selected_columns[1]].unique()]) 
            highlighted_node_l3 = layer2_column.multiselect('Filter Phân khúc Sản phẩm', [node for node in pk_df[selected_columns[2]].unique()])
            highlighted_node_l4 = layer3_column.multiselect('Filter Phân khúc Khách hàng', [node for node in pk_df[selected_columns[3]].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_l2 + highlighted_node_l3 + highlighted_node_l4 

            graph(pk_df, selected_columns, 'Chi phí nhận phân bổ tại thời điểm',
                  highlighted_nodes, map_color_app, 
                  title="<b>Phân bổ giai đoạn 4: Từ Cost Type đến Sản phẩm, Phân khúc Khách hàng</b>",
                  page_flag=4, sub_graph_filter=filer_option)

if __name__ == '__main__':
    # Set the date range
    start_date = datetime(2023, 9, 1)
    end_date = datetime(2023, 12, 31)
    main()