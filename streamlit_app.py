import numpy as np
import pandas as pd

import plotly.graph_objects as go   

import streamlit as st
import extra_streamlit_components as stx
from streamlit_option_menu import option_menu
st.set_page_config(layout="wide")

chosen_id = stx.tab_bar(data=[
    stx.TabBarItemData(id=1, title="Phân bổ Giai đoạn 1:", description="Từ trung tâm đến trung tâm"),
    stx.TabBarItemData(id=2, title="Phân bổ giai đoạn 2:", description="Từ CPQLKD trực tiếp đến Phân khúc Khách hàng"),
    stx.TabBarItemData(id=3, title="Phân bổ giai đoạn 3:", description="Từ CPQLKD trực tiếp đến Sản phẩm"),
    stx.TabBarItemData(id=4, title="Phân bổ giai đoạn 4:", description="Từ Đơn vị nhận phân bổ đến Sản phẩm, Phân khúc Khách"),
], default=1)

node_list = ['TT DICH VU NOI BO', 'TT QUAN LY CHUNG TOAN HANG', 'TT AO',
            'KHONG CO TRONG CAY', 'TT DOANH THU',
            'TT QUAN LY CHUNG KHOI KINH DOANH', 'TT HO TRO TRUC TIEP',
            'TT HO TRO SAN PHAM', 'TT QUAN LY CHUNG CHI NHANH']

color_list = ['rgba(44, 160, 44, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(140, 86, 75, 0.8)',
            'rgba(23, 190, 207, 0.8)', 'rgba(188, 189, 34, 0.8)', 'rgba(214, 39, 40, 0.8)',
            'rgba(188, 189, 34, 0.8)', 'rgba(31, 119, 180, 0.8)', 'rgba(140, 86, 75, 0.8)']

if chosen_id == '1':
    option = st.selectbox('Option', ('Level 0 and 4', 'Level 0 to 4'))
    # map_columns = ['Lv1', 'Lv2', 'Lv3', 'Lv4', 'Lv5']
    # selected_layer = st.selectbox('Select focus layer', ('Lv1', 'Lv2', 'Lv3', 'Lv4', 'Lv5'))
    if option == 'Level 0 and 4':
        map_columns = ['Lv0', 'Lv4']
        highlighted_nodes = st.multiselect("Select Highlight Node:", node_list)
    else:    
        layer0_column, layer1_column, layer2_column, layer3_column, layer4_column = st.columns(5)

        highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv1' for node in node_list])
        highlighted_node_l2 = layer1_column.multiselect('Filter layer 2', [node + '_Lv2' for node in node_list])
        highlighted_node_l3 = layer2_column.multiselect('Filter layer 3', [node + '_Lv3' for node in node_list])
        highlighted_node_l4 = layer3_column.multiselect('Filter layer 4', [node + '_Lv4' for node in node_list])
        highlighted_node_l5 = layer4_column.multiselect('Filter layer 5', [node + '_Lv5' for node in node_list])

    map_df = pd.read_csv('map.csv')
    trans_df = pd.read_csv(r'C:\Users\Admin\PycharmProjects\BIDV_Task\Sankey_Plot\sample data lv pk.csv')[['Lv0', 'Lv1', 'Lv2', 'Lv3', 'Lv4', 'Size']]

    map_name = map_df.set_index('ORG_UNIT_ID')['LEVEL_02_NAME'].to_dict()

    map_columns = ['Lv0', 'Lv3', 'Lv4']
    mapped_columns = [ col + '_mapped' for col in map_columns]
    for i, j in zip(map_columns, mapped_columns):
        trans_df[j] = trans_df[i].map(map_name)
        trans_df[j] = trans_df[j] + '_' + i

    def sankey_graph(data, mapped_columns, highlighted_node):
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

        highlighted_node = highlighted_node + '_Lv0'
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

        fig.update_layout(title_text="<b>Phân bổ giai đoạn 1: Từ trung tâm đến trung tâm</b>",  # Bold title text
                        title_font_size=24)
        fig.update_layout( autosize=False, width=1500, height=1000, 
                        xaxis_visible=False, xaxis_showticklabels=False,
                        yaxis_visible=False, yaxis_showticklabels=False)
        return fig

    highlighted_node = 'TT DICH VU NOI BO'
    data = trans_df.groupby(mapped_columns)['Size'].sum().reset_index()   
    fig = sankey_graph(data, mapped_columns, highlighted_node)

    values_to_filter = [highlighted_node + "_" + map_columns[0]]
    filtered_df = data[data.isin(values_to_filter).any(axis=1)]
    filtered_columns = filtered_df.columns
    filtered_columns = filtered_columns.drop('Size')
    for col in filtered_columns:
        filtered_df[col] = filtered_df[col].str[:-4]

    def calculate_percentage(df, level_column, size_column):
        grouped_df = df[[level_column, size_column]].groupby(level_column)[size_column].sum().reset_index()
        total_size = grouped_df[size_column].sum()
        grouped_df[f'Percentage_{level_column[2]}'] = grouped_df[size_column] / total_size 
        return grouped_df.drop(size_column, axis=1)

    results = []
    for col in filtered_columns:
        result = calculate_percentage(filtered_df, col, 'Size')
        results.append(result)

    final_result = pd.concat(results, axis=1)

    st.plotly_chart(fig)

    st.markdown('''
    # Nguyên tắc chung

## **Nguyên tắc phân loại trung tâm phân bổ:**

1. **Một đơn vị tổ chức có thể tương ứng với một trung tâm phân bổ.**
2. **Nhiều đơn vị tổ chức được gắn vào một trung tâm phân bổ.** Các đơn vị tổ chức này có nhiệm vụ tương tự cùng thuộc Trụ sở chính hoặc cùng Chi nhánh và chi phí của các đơn vị này có thể được phân bổ theo cùng một tiêu thức.
3. **Các đơn vị tổ chức đảm nhận nhiều chức năng, nhiệm vụ khác nhau có thể được phân chia thành nhiều trung tâm phân bổ.**

## **Các loại trung tâm phân bổ:**

**a) Trung tâm doanh thu là bất kỳ bộ phận nào của BIDV có chức năng kinh doanh trực tiếp tạo ra doanh thu cho BIDV.**

**b) Trung tâm chi phí là các bộ phận còn lại không phải là Trung tâm doanh thu**. Tùy theo chức năng, nhiệm vụ, Trung tâm chi phí có thể được phân loại thành:

- **Trung tâm hỗ trợ sản phẩm là đơn vị tại Trụ sở chính có cung cấp sản phẩm và dịch vụ tới khách hàng nhưng không chịu trách nhiệm tạo ra doanh thu (thường là đơn vị tác nghiệp tập trung như TTTT, TTTN&TTTM,..).
- Trung tâm dịch vụ nội bộ là đơn vị tại Trụ sở chính cung cấp những dịch vụ có thể xác định được tới các trung tâm khác nhưng không trực tiếp cung cấp sản phẩm và dịch vụ tới khách hàng.
- Trung tâm quản lý chung là các bộ phận mà không thể phân bổ chi phí của bộ phận đó cho các trung tâm khác dựa trên đơn vị dịch vụ cung cấp, gồm có: Trung tâm quản lý chung toàn hàng và Trung tâm quản lý chung khối kinh doanh.

+ Trung tâm quản lý chung Chi nhánh là các đơn vị mà Chi nhánh không thể phân bổ chi phí của đơn vị đó cho các trung tâm khác dựa trên đơn vị dịch vụ cung cấp.

- Trung tâm hỗ trợ trực tiếp là đơn vị ở Chi nhánh có tham gia cung cấp sản phẩm và dịch vụ đến khách hàng nhưng không chịu trách nhiệm tạo ra doanh thu (thường là đơn vị tác nghiệp tại Chi nhánh như Phòng giao dịch khách hàng, phòng Quản trị tín dụng,..).

### Phân loại trung tâm hiện tại được quy định tại văn bản 1086/Qd-BIDV ngày 27/03/2019

# Các giai đoạn phân bổ

## **Giai đoạn 1: Phân bổ chi phí từ Trung tâm đến Trung tâm tại Trụ sở chính**

### a) Phân bổ chi phí của Trung tâm dịch vụ nội bộ:
                Quá trình phân bổ này dựa trên tiêu thức phân bổ hoặc tỷ lệ % ước tính đối với thời gian bỏ ra để cung cấp các dịch vụ đến mỗi trung tâm nhận phân bổ. Các đơn vị thuộc Trung tâm dịch vụ nội bộ sẽ được phân bổ một cách tuần tự (mô hình “thác nước” hoặc “phân bổ lần lượt từ trên xuống”) dựa trên phân loại các trung tâm. Trong đó:

- Trình tự phân bổ được xác định dựa trên tính trọng yếu, quy mô, mức độ ảnh hưởng của mỗi trung tâm phân bổ.
- Trung tâm dịch vụ nội bộ đã đi phân bổ trước sẽ không nhận chi phí phân bổ của Trung tâm khác. Trung tâm dịch vụ nội bộ với thứ tự cuối cùng không được phân bổ chi phí cho các trung tâm dịch vụ nội bộ khác mà phân bổ chi phí cho các trung tâm doanh thu, hỗ trợ sản phẩm, quản lý chung toàn hàng và quản lý chung của khối kinh doanh.
- Khi chi phí của một trung tâm đi phân bổ cho các trung tâm khác, tổng chi phí của trung tâm được phân bổ vẫn giữ nguyên thông tin về các loại chi phí phân bổ vào đơn vị này.

Cách thức này đòi hỏi thiết lập mối quan hệ giữa chi phí và dịch vụ cho mỗi phòng ban để xác định trình tự phân bổ, từ đó nâng cao tính minh bạch về chi phí của các khối kinh doanh.

### b) Phân bổ chi phí của Trung tâm quản lý chung toàn hàng đến các đơn vị và khối kinh doanh theo các tiêu thức phân bổ tổng hợp.

Các trung tâm quản lý chung toàn hàng phân bổ chi phí trực tiếp cho các khối kinh doanh sẽ xuất hiện vào bước cuối cùng trong quy trình phân bổ chi phí tuần tự trong Giai đoạn 1.

Kết thúc Giai đoạn 1, chi phí quản lý từ tất cả các trung tâm dịch vụ nội bộ và trung tâm quản lý chung toàn hàng sẽ được phân bổ đi hết 100%.

### c) Thứ tự phân bổ của các trung tâm theo Phụ lục V.1/MPA. công văn 8828/Qyd-BIDV ngày 04/12/2017    
''')
    # st.markdown()

if chosen_id == '2':
    on = st.toggle('Hiển thị Level 4')
    if on:
        st.write('Hiển thị Level 4')
    layer0_column, layer1_column, layer2_column = st.columns(3)

    highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv1' for node in node_list])
    highlighted_node_l2 = layer1_column.multiselect('Filter layer 4', [node + '_Lv4' for node in node_list])
    highlighted_node_l3 = layer2_column.multiselect('Filter layer Phân khúc', [node + '_Lv3' for node in node_list])

    df = pd.read_csv(r'C:\Users\Admin\PycharmProjects\Money_flow_diagram\Hai ha\KQ phan bo GD2_T092023.csv')
    map_df = pd.read_csv(r'map.csv')
    map_name = map_df.set_index('ORG_UNIT_ID')['LEVEL_02_NAME'].to_dict()
    df['Mã đơn vị tổ chức cấp 6_map'] = df['Mã đơn vị tổ chức cấp 6'].map(map_name) 
    df['Mã SP cấp 5 PK'] = df['Mã SP cấp 5'].astype(str).str[:2]
    data = df.groupby(['Mã đơn vị tổ chức cấp 6_map', 'Mã SP cấp 5 PK', 'Tên phân khúc KH cấp 3'])['Chi phí nhận phân bổ tại thời điểm'].sum().reset_index()
    data['Mã SP cấp 5 PK'] = 'SP' + data['Mã SP cấp 5 PK'].apply(str) 
    def create_node_dict(data, columns):
        unique_nodes = set()
        for col in columns:
            unique_nodes.update(data[col].unique())
        return {node: i for i, node in enumerate(sorted(unique_nodes))}

    # Extracting the node names and creating a dictionary to map nodes to unique IDs
    columns = ['Mã đơn vị tổ chức cấp 6_map', 'Mã SP cấp 5 PK',
        'Tên phân khúc KH cấp 3']
    node_dict = create_node_dict(data, columns)

    # Preparing source, target, and value lists for the Sankey diagram
    source = []
    target = []
    value = []

    for _, row in data.iterrows():
        for i in range(len(columns)-1):
            source.append(node_dict[row[columns[i]]])
            target.append(node_dict[row[columns[i+1]]])
            value.append(row['Chi phí nhận phân bổ tại thời điểm'])

    # Creating the node label list
    node_labels = list(node_dict.keys())

    # Creating the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        ))])

    fig.update_layout(title_text="<b>Phân bổ giai đoạn 2: Từ CPQLKD trực tiếp đến PKKH</b>",  # Bold title text
                        title_font_size=24)
    fig.update_layout( autosize=False, width=1500, height=1000, 
                        xaxis_visible=False, xaxis_showticklabels=False,
                        yaxis_visible=False, yaxis_showticklabels=False)

    st.plotly_chart(fig)

    st.markdown('''
    ## **Nguyên tắc phân loại trung tâm phân bổ:**

1. **Một đơn vị tổ chức có thể tương ứng với một trung tâm phân bổ.**
2. **Nhiều đơn vị tổ chức được gắn vào một trung tâm phân bổ.** Các đơn vị tổ chức này có nhiệm vụ tương tự cùng thuộc Trụ sở chính hoặc cùng Chi nhánh và chi phí của các đơn vị này có thể được phân bổ theo cùng một tiêu thức.
3. **Các đơn vị tổ chức đảm nhận nhiều chức năng, nhiệm vụ khác nhau có thể được phân chia thành nhiều trung tâm phân bổ.**

## **Các loại trung tâm phân bổ:**

**a) Trung tâm doanh thu là bất kỳ bộ phận nào của BIDV có chức năng kinh doanh trực tiếp tạo ra doanh thu cho BIDV.**

**b) Trung tâm chi phí là các bộ phận còn lại không phải là Trung tâm doanh thu**. Tùy theo chức năng, nhiệm vụ, Trung tâm chi phí có thể được phân loại thành:

- **Trung tâm hỗ trợ sản phẩm là đơn vị tại Trụ sở chính có cung cấp sản phẩm và dịch vụ tới khách hàng nhưng không chịu trách nhiệm tạo ra doanh thu (thường là đơn vị tác nghiệp tập trung như TTTT, TTTN&TTTM,..).
- Trung tâm dịch vụ nội bộ là đơn vị tại Trụ sở chính cung cấp những dịch vụ có thể xác định được tới các trung tâm khác nhưng không trực tiếp cung cấp sản phẩm và dịch vụ tới khách hàng.
- Trung tâm quản lý chung là các bộ phận mà không thể phân bổ chi phí của bộ phận đó cho các trung tâm khác dựa trên đơn vị dịch vụ cung cấp, gồm có: Trung tâm quản lý chung toàn hàng và Trung tâm quản lý chung khối kinh doanh.

+ Trung tâm quản lý chung Chi nhánh là các đơn vị mà Chi nhánh không thể phân bổ chi phí của đơn vị đó cho các trung tâm khác dựa trên đơn vị dịch vụ cung cấp.

- Trung tâm hỗ trợ trực tiếp là đơn vị ở Chi nhánh có tham gia cung cấp sản phẩm và dịch vụ đến khách hàng nhưng không chịu trách nhiệm tạo ra doanh thu (thường là đơn vị tác nghiệp tại Chi nhánh như Phòng giao dịch khách hàng, phòng Quản trị tín dụng,..).

# Các giai đoạn phân bổ

## **Giai đoạn 1: Phân bổ chi phí từ Trung tâm đến Trung tâm tại Trụ sở chính**

### a) Phân bổ chi phí của Trung tâm dịch vụ nội bộ:
Quá trình phân bổ này dựa trên tiêu thức phân bổ hoặc tỷ lệ % ước tính đối với thời gian bỏ ra để cung cấp các dịch vụ đến mỗi trung tâm nhận phân bổ. Các đơn vị thuộc Trung tâm dịch vụ nội bộ sẽ được phân bổ một cách tuần tự (mô hình “thác nước” hoặc “phân bổ lần lượt từ trên xuống”) dựa trên phân loại các trung tâm. Trong đó:

- Trình tự phân bổ được xác định dựa trên tính trọng yếu, quy mô, mức độ ảnh hưởng của mỗi trung tâm phân bổ.
- Trung tâm dịch vụ nội bộ đã đi phân bổ trước sẽ không nhận chi phí phân bổ của Trung tâm khác. Trung tâm dịch vụ nội bộ với thứ tự cuối cùng không được phân bổ chi phí cho các trung tâm dịch vụ nội bộ khác mà phân bổ chi phí cho các trung tâm doanh thu, hỗ trợ sản phẩm, quản lý chung toàn hàng và quản lý chung của khối kinh doanh.
- Khi chi phí của một trung tâm đi phân bổ cho các trung tâm khác, tổng chi phí của trung tâm được phân bổ vẫn giữ nguyên thông tin về các loại chi phí phân bổ vào đơn vị này.

Cách thức này đòi hỏi thiết lập mối quan hệ giữa chi phí và dịch vụ cho mỗi phòng ban để xác định trình tự phân bổ, từ đó nâng cao tính minh bạch về chi phí của các khối kinh doanh.

### b) Phân bổ chi phí của Trung tâm quản lý chung toàn hàng đến các đơn vị và khối kinh doanh theo các tiêu thức phân bổ tổng hợp.

Các trung tâm quản lý chung toàn hàng phân bổ chi phí trực tiếp cho các khối kinh doanh sẽ xuất hiện vào bước cuối cùng trong quy trình phân bổ chi phí tuần tự trong Giai đoạn 1.

Kết thúc Giai đoạn 1, chi phí quản lý từ tất cả các trung tâm dịch vụ nội bộ và trung tâm quản lý chung toàn hàng sẽ được phân bổ đi hết 100%.

### c) Thứ tự phân bổ của các trung tâm theo Phụ lục V.1/MPA. công văn 8828/Qyd-BIDV
''')

    url = "https://cafef.vn/khong-chi-vang-sjc-gia-vang-nhan-tron-tron-cung-lap-dinh-moi-64-trieu-dong-luong-188231227091538499.chn"
    st.markdown("check out this %s" % url)
if chosen_id == '3':    
    on = st.toggle('Hiển thị Level 4')
    if on:
        st.write('Hiển thị Level 4')
    layer0_column, layer1_column, layer2_column = st.columns(3)

    highlighted_node_l1 = layer0_column.multiselect('Filter layer 1', [node + '_Lv1' for node in node_list])
    highlighted_node_l2 = layer1_column.multiselect('Filter layer 4', [node + '_Lv4' for node in node_list])
    highlighted_node_l3 = layer2_column.multiselect('Filter layer Sản phẩm', [node + '_Lv3' for node in node_list])


if chosen_id == '4':
    layer0_column, layer1_column = st.columns(2)

    highlighted_node_l1 = layer0_column.multiselect('Filter layer Phân khúc', [node + '_Lv1' for node in node_list])
    highlighted_node_l2 = layer1_column.multiselect('Filter layer Sản phẩm', [node + '_Lv4' for node in node_list])
    

