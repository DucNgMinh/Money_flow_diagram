import numpy as np
import pandas as pd
import copy

import plotly.graph_objects as go   

import streamlit as st
import extra_streamlit_components as stx

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utils import *

@st.cache_data
def load_data(date_range):
    map_df = pd.read_csv('Map_V1.csv')
    map_ten_goc = map_df.set_index('LEVEL_06_CODE')['LEVEL_TEN_GOC_NAME'].to_dict()
    map_tt = map_df.set_index('LEVEL_06_CODE')['LEVEL_TT_NAME'].to_dict()
    map_khoi = map_df.set_index('LEVEL_06_CODE')['LEVEL_KHOI_NAME'].to_dict()

    map_sp_df = pd.read_excel('./Real-data/2023-12-13 Cây phân cấp phục vụ phân bổ Sanky Chart.xlsx', 
                          sheet_name= 'Product_Hierarchy final to FIS')
    map_sp = map_sp_df.set_index('PRODUCT_LEAF_ID')['LEVEL2_DESC'].to_dict()

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

    # create map (trung tam) df for trans_df
    trans_df_tt = copy.deepcopy(trans_df)
    for i, j in zip(map_columns, mapped_columns):
        trans_df_tt[j] = trans_df[i].map(map_tt)
        trans_df_tt[j] = trans_df_tt[j] + '_' + i
    trans_df_tt.drop(map_columns, axis= 1, inplace= True)
    all_lv_tt_df = trans_df_tt.groupby(mapped_columns)['Size'].sum().reset_index()
    lv_04_tt_df = trans_df_tt.groupby(['Lv0_mapped', 'Lv4_mapped'])['Size'].sum().reset_index()

    # load allocate data
    al_df = pd.read_parquet('Demo_data_for_graph_v1.parquet')
    # filter date
    al_df = al_df[al_df['Tháng'].isin(date_range)]

    al_df['Mã đơn vị tổ chức cấp 6_tt'] = al_df['Mã đơn vị tổ chức cấp 6'].map(map_tt)
    al_df['Mã đơn vị tổ chức cấp 6_khoi'] = al_df['Mã đơn vị tổ chức cấp 6'].map(map_khoi)
    al_df['Mã SP cấp 5 PK'] = al_df['Mã SP cấp 5'].map(map_sp)
    al_df['Mã SP cấp 5 PK'].fillna('KHONG_SP', inplace= True)

    khoi_pk_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_khoi', 'Tên phân khúc KH cấp 3']).agg({'CF_PB': 'sum', 'Real_CF_TT': 'sum'}).reset_index()
    
    tt_pk_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_tt', 'Tên phân khúc KH cấp 3']).agg({'CF_PB': 'sum', 'Real_CF_TT': 'sum'}).reset_index()

    khoi_sp_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_khoi', 'Mã SP cấp 5 PK']).agg({'CF_PB': 'sum', 'Real_CF_TT': 'sum'}).reset_index()
    khoi_sp_df['Mã SP cấp 5 PK'] = 'SP_' + khoi_sp_df['Mã SP cấp 5 PK'].apply(str)

    tt_sp_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_tt', 'Mã SP cấp 5 PK']).agg({'CF_PB': 'sum','Real_CF_TT': 'sum'}).reset_index()
    
    tt_sp_df['Mã SP cấp 5 PK'] = 'SP_' + tt_sp_df['Mã SP cấp 5 PK'].apply(str)

    khoi_sp_pk_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_khoi', 
                                   'Mã SP cấp 5 PK', 'Tên phân khúc KH cấp 3']).agg({'CF_PB': 'sum', 'Real_CF_TT': 'sum'}).reset_index()
    khoi_sp_pk_df['Mã SP cấp 5 PK'] = 'SP_' + khoi_sp_pk_df['Mã SP cấp 5 PK'].apply(str) 

    tt_sp_pk_df = al_df.groupby(['Mã đơn vị tổ chức cấp 6_tt', 
                                 'Mã SP cấp 5 PK', 'Tên phân khúc KH cấp 3']).agg({'CF_PB': 'sum','Real_CF_TT': 'sum'}).reset_index()
    tt_sp_pk_df['Mã SP cấp 5 PK'] = 'SP_' + tt_sp_pk_df['Mã SP cấp 5 PK'].apply(str)

    return all_lv_khoi_df, lv_04_khoi_df, all_lv_tt_df, lv_04_tt_df, khoi_pk_df, tt_pk_df, khoi_sp_df, tt_sp_df, khoi_sp_pk_df, tt_sp_pk_df

def main():
    st.set_page_config(layout="wide")
    st.title("Money Flow Diagram V2 Test !!!!!")
    
    st.session_state['page_id'] = stx.tab_bar(data=[
        stx.TabBarItemData(id=1, title="Phân bổ Giai đoạn 1:", description="Từ trung tâm đến trung tâm"),
        stx.TabBarItemData(id=2, title="Phân bổ giai đoạn 2:", description="Từ CPQLKD trực tiếp đến Phân khúc Khách hàng"),
        stx.TabBarItemData(id=3, title="Phân bổ giai đoạn 3:", description="Từ CPQLKD trực tiếp đến Sản phẩm"),
        stx.TabBarItemData(id=4, title="Phân bổ giai đoạn 4:", description="Từ Đơn vị nhận phân bổ đến Sản phẩm, Phân khúc Khách"),
    ], default=1)

    sub_1_column, sub_2_column, sub_3_column = st.columns([1, 1, 3])
    
    st.session_state['detail_option'] = sub_1_column.radio("Chọn đơn vị chi tiết", options= ["Khối", "Trung tâm"]) 
    st.session_state['size_option'] = sub_2_column.radio("Chọn đơn vị dòng tiền", options= ['CF_PB', "Real_CF_TT"])

    datetime_slider = sub_3_column.slider(
        "Select a date range",
        min_value=start_date,
        max_value=end_date,
        value=(start_date, end_date),
        format="YYYY/MM")
    st.session_state['date_range'] = generate_year_month_range(datetime_slider [0], datetime_slider[-1])

    all_lv_khoi_df, lv_04_khoi_df, all_lv_tt_df, lv_04_tt_df, khoi_pk_df, tt_pk_df, khoi_sp_df, tt_sp_df, khoi_sp_pk_df, tt_sp_pk_df= load_data(st.session_state['date_range'])

    map_df = pd.read_csv('Map_V1.csv')
    map_tt_color = map_df.set_index('LEVEL_TT_NAME')['LEVEL_TT_COLOR'].to_dict()
    map_khoi_color = map_df.set_index('LEVEL_KHOI_NAME')['LEVEL_KHOI_COLOR'].to_dict()

    if st.session_state['page_id'] == "1":
        option = st.selectbox('Option', ('Level 1 and 5', 'Level 1 to 5'))
        size_column = 'Size'
        if option == 'Level 1 and 5':
            selected_columns = ['Lv0_mapped', 'Lv4_mapped']
            layer0_column, layer1_column = st.columns(2)

            if st.session_state['detail_option'] == "Khối":
                highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv0' for node in map_df['LEVEL_KHOI_NAME'].dropna().unique()])
                highlighted_node_l4 = layer1_column.multiselect('Filter layer 4', [node + '_Lv4' for node in map_df['LEVEL_KHOI_NAME'].dropna().unique()])
                highlighted_nodes = highlighted_node_l1 + highlighted_node_l4
                
                fig = sankey_graph(lv_04_khoi_df, selected_columns, highlighted_nodes, 
                                    title= "<b>Phân bổ giai đoạn 1: Từ khối đến khối</b>", 
                                    color_map= map_khoi_color)
                st.plotly_chart(fig, autosize= True)
                
                if len(highlighted_nodes) != 0:
                    sub_table(lv_04_khoi_df, highlighted_nodes, selected_columns, 
                            size_column, map_khoi_color, page_flag = 1)

            else:
                highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv0' for node in map_df['LEVEL_TT_NAME'].dropna().unique()])
                highlighted_node_l4 = layer1_column.multiselect('Filter layer 4', [node + '_Lv4' for node in map_df['LEVEL_TT_NAME'].dropna().unique()])
                highlighted_nodes = highlighted_node_l1 + highlighted_node_l4
                fig = sankey_graph(lv_04_tt_df, selected_columns, highlighted_nodes, 
                                    title= "<b>Phân bổ giai đoạn 1: Từ trung tâm đến trung tâm</b>", 
                                    color_map= map_tt_color)
                st.plotly_chart(fig, autosize= True)

                if len(highlighted_nodes) != 0:
                    sub_table(lv_04_tt_df, highlighted_nodes, selected_columns, 
                          size_column, map_tt_color, page_flag = 1)

        else:
            selected_columns = ['Lv0_mapped', 'Lv1_mapped', 'Lv2_mapped', 'Lv3_mapped', 'Lv4_mapped']
            layer0_column, layer1_column, layer2_column, layer3_column, layer4_column = st.columns(5)
            if st.session_state['detail_option'] == "Khối":
                highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv0' for node in map_df['LEVEL_KHOI_NAME'].dropna().unique()])
                highlighted_node_l2 = layer1_column.multiselect('Filter layer 2', [node + '_Lv1' for node in map_df['LEVEL_KHOI_NAME'].dropna().unique()])
                highlighted_node_l3 = layer2_column.multiselect('Filter layer 3', [node + '_Lv2' for node in map_df['LEVEL_KHOI_NAME'].dropna().unique()])
                highlighted_node_l4 = layer3_column.multiselect('Filter layer 4', [node + '_Lv3' for node in map_df['LEVEL_KHOI_NAME'].dropna().unique()])
                highlighted_node_l5 = layer4_column.multiselect('Filter layer 5', [node + '_Lv4' for node in map_df['LEVEL_KHOI_NAME'].dropna().unique()])
                
                highlighted_nodes = highlighted_node_l1 + highlighted_node_l2 + highlighted_node_l3 + highlighted_node_l4 + highlighted_node_l5
                fig = sankey_graph(all_lv_khoi_df, selected_columns, highlighted_nodes, 
                                   title= "<b>Phân bổ giai đoạn 1: Từ khối đến khối</b>", color_map= map_khoi_color)
                st.plotly_chart(fig, autosize= True)

                if len(highlighted_nodes) != 0:
                    sub_table(all_lv_khoi_df, highlighted_nodes, selected_columns, 
                          size_column, map_khoi_color, page_flag = 1)

            else:
                highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv0' for node in map_df['LEVEL_TT_NAME'].dropna().unique()])
                highlighted_node_l2 = layer1_column.multiselect('Filter layer 2', [node + '_Lv1' for node in map_df['LEVEL_TT_NAME'].dropna().unique()])
                highlighted_node_l3 = layer2_column.multiselect('Filter layer 3', [node + '_Lv2' for node in map_df['LEVEL_TT_NAME'].dropna().unique()])
                highlighted_node_l4 = layer3_column.multiselect('Filter layer 4', [node + '_Lv3' for node in map_df['LEVEL_TT_NAME'].dropna().unique()])
                highlighted_node_l5 = layer4_column.multiselect('Filter layer 5', [node + '_Lv4' for node in map_df['LEVEL_TT_NAME'].dropna().unique()])
                
                highlighted_nodes = highlighted_node_l1 + highlighted_node_l2 + highlighted_node_l3 + highlighted_node_l4 + highlighted_node_l5

                fig = sankey_graph(all_lv_tt_df, selected_columns, highlighted_nodes, 
                                   title= "<b>Phân bổ giai đoạn 1: Từ trung tâm đến trung tâm</b>", color_map= map_tt_color)
                st.plotly_chart(fig, autosize= True)

                if len(highlighted_nodes) != 0:
                    sub_table(all_lv_tt_df, highlighted_nodes, selected_columns, 
                          size_column, map_tt_color, page_flag = 1)

    elif st.session_state['page_id'] == "2":
        if st.session_state['detail_option'] == "Khối":
            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter Đơn vị tổ chức', [node for node in khoi_pk_df['Mã đơn vị tổ chức cấp 6_khoi'].unique()])
            highlighted_node_pk = layer1_column.multiselect('Filter Phân khúc', [node for node in khoi_pk_df['Tên phân khúc KH cấp 3'].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_pk

            selected_columns = ['Mã đơn vị tổ chức cấp 6_khoi',  'Tên phân khúc KH cấp 3']
            fig = sankey_graph(khoi_pk_df, selected_columns, highlighted_nodes, 
                                title= "<b>Phân bổ giai đoạn 2: Từ CPQLKD trực tiếp đến PKKH</b>", 
                                size_column= st.session_state['size_option'], color_map= map_khoi_color)
            
            st.plotly_chart(fig)
            if len(highlighted_nodes) != 0:
                sub_table(khoi_pk_df, highlighted_nodes, selected_columns, 
                          size_column, map_khoi_color, page_flag = 2)
                
        else:
            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter Đơn vị tổ chức', [node for node in tt_pk_df['Mã đơn vị tổ chức cấp 6_tt'].unique()])
            highlighted_node_pk = layer1_column.multiselect('Filter Phân khúc', [node for node in tt_pk_df['Tên phân khúc KH cấp 3'].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_pk

            selected_columns = ['Mã đơn vị tổ chức cấp 6_tt',  'Tên phân khúc KH cấp 3']
            fig = sankey_graph(tt_pk_df, selected_columns, highlighted_nodes, 
                                title= "<b>Phân bổ giai đoạn 2: Từ CPQLKD trực tiếp đến PKKH</b>", 
                                size_column= st.session_state['size_option'], color_map= map_tt_color)
            st.plotly_chart(fig)
            if len(highlighted_nodes) != 0:
                sub_table(tt_pk_df, highlighted_nodes, selected_columns, 
                          st.session_state['size_option'], map_tt_color, page_flag = 2)

    elif st.session_state['page_id'] == "3":
        if st.session_state['detail_option'] == "Khối":
            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter Đơn vị tổ chức', [node for node in khoi_sp_df['Mã đơn vị tổ chức cấp 6_khoi'].unique()])
            highlighted_node_pk = layer1_column.multiselect('Filter Sản phẩm', [node for node in khoi_sp_df['Mã SP cấp 5 PK'].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_pk

            selected_columns = ['Mã đơn vị tổ chức cấp 6_khoi', 'Mã SP cấp 5 PK']
            fig = sankey_graph(khoi_sp_df, selected_columns, highlighted_nodes, 
                                title= "<b>Phân bổ giai đoạn 3: Từ CPQLKD trực tiếp đến Sản phẩm</b>", 
                                size_column= st.session_state['size_option'],color_map= map_khoi_color)
            st.plotly_chart(fig)
            if len(highlighted_nodes) != 0:
                sub_table(khoi_sp_df, highlighted_nodes, selected_columns, 
                          st.session_state['size_option'], map_khoi_color, page_flag = 3)

        else:
            layer0_column, layer1_column = st.columns(2)
            highlighted_node_l1 = layer0_column.multiselect('Filter Đơn vị tổ chức', [node for node in tt_sp_df['Mã đơn vị tổ chức cấp 6_tt'].unique()])
            highlighted_node_pk = layer1_column.multiselect('Filter Sản phẩm', [node for node in tt_sp_df['Mã SP cấp 5 PK'].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_pk

            selected_columns = ['Mã đơn vị tổ chức cấp 6_tt', 'Mã SP cấp 5 PK']
            fig = sankey_graph(tt_sp_df, selected_columns, highlighted_nodes, 
                                title= "<b>Phân bổ giai đoạn 3: Từ CPQLKD trực tiếp đến Sản phẩm</b>", 
                                size_column= st.session_state['size_option'], color_map= map_tt_color)
            st.plotly_chart(fig)
            if len(highlighted_nodes) != 0:
                sub_table(tt_sp_df, highlighted_nodes, selected_columns, 
                          st.session_state['size_option'], map_tt_color, page_flag = 3)

    else:        
        if st.session_state['detail_option'] == "Khối":
            layer0_column, layer1_column, layer2_column = st.columns(3)
            highlighted_node_l1 = layer0_column.multiselect('Filter Đơn vị tổ chức', [node for node in khoi_sp_pk_df['Mã đơn vị tổ chức cấp 6_khoi'].unique()])
            highlighted_node_sp = layer1_column.multiselect('Filter Sản phẩm', [node for node in khoi_sp_pk_df['Mã SP cấp 5 PK'].unique()])
            highlighted_node_pk = layer2_column.multiselect('Filter Phân khúc', [node for node in khoi_sp_pk_df['Tên phân khúc KH cấp 3'].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_pk + highlighted_node_sp
   
            selected_columns = ['Mã đơn vị tổ chức cấp 6_khoi', 'Mã SP cấp 5 PK', 'Tên phân khúc KH cấp 3']
            fig = sankey_graph(khoi_sp_pk_df, selected_columns, highlighted_nodes, 
                                title= "<b>Phân bổ giai đoạn 4: Từ Đơn vị nhận phân bổ đến Sản phẩm, Phân khúc Khách</b>", 
                                size_column= st.session_state['size_option'], color_map= map_khoi_color)
            st.plotly_chart(fig)
            if len(highlighted_nodes) != 0:
                sub_table(khoi_sp_pk_df, highlighted_nodes, selected_columns, 
                          st.session_state['size_option'], map_khoi_color, page_flag = 4)

        else:
            layer0_column, layer1_column, layer2_column = st.columns(3)
            highlighted_node_l1 = layer0_column.multiselect('Filter Đơn vị tổ chức', [node for node in tt_sp_pk_df['Mã đơn vị tổ chức cấp 6_tt'].unique()])
            highlighted_node_sp = layer1_column.multiselect('Filter Sản phẩm', [node for node in tt_sp_pk_df['Mã SP cấp 5 PK'].unique()])
            highlighted_node_pk = layer2_column.multiselect('Filter Phân khúc', [node for node in tt_sp_pk_df['Tên phân khúc KH cấp 3'].unique()])
            highlighted_nodes = highlighted_node_l1 + highlighted_node_pk + highlighted_node_sp

            selected_columns = ['Mã đơn vị tổ chức cấp 6_tt', 'Mã SP cấp 5 PK', 'Tên phân khúc KH cấp 3']
            fig = sankey_graph(tt_sp_pk_df, selected_columns, highlighted_nodes, 
                                title= "<b>Phân bổ giai đoạn 4: Từ Đơn vị nhận phân bổ đến Sản phẩm, Phân khúc Khách</b>", 
                                size_column= st.session_state['size_option'], color_map= map_tt_color)
            st.plotly_chart(fig)
            if len(highlighted_nodes) != 0:
                sub_table(tt_sp_pk_df, highlighted_nodes, selected_columns, 
                          st.session_state['size_option'], map_tt_color, page_flag = 4)
            

if __name__ == '__main__':
    # Set the date range
    start_date = datetime(2023, 9, 1)
    end_date = datetime(2023, 12, 31)
    main()