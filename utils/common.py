from dash import MATCH, ALL
def gen_id(tp, index):
    return {'type': tp, 'index': index}

def o_match(tp):
    return {'type': tp, 'index': MATCH}


def o_all(tp):
    return {'type': tp, 'index': ALL}


x_axis_match = o_match('x-axis')
y_axis_match = o_match('y-axis')
dataset_match = o_match('dataset')
figure_type_match = o_match('figure-type')
groupby_match = o_match('groupby')
agg_type_match = o_match('agg_type')
agg_col_match = o_match('agg_col')
page_delete_match = o_match('page-delete')
input_page_match = o_match('input-page')
plot_configs_match = o_match('plot-configs')

x_axis_all = o_all('x-axis')
y_axis_all = o_all('y-axis')
dataset_all = o_all('dataset')
figure_type_all = o_all('figure-type')
groupby_all = o_all('groupby')
agg_type_all = o_all('agg_type')
agg_col_all = o_all('agg_col')
page_delete_all = o_all('page-delete')
plot_configs_all = o_all('plot-configs')

filter_add = 'filter-add'
filter_delete = 'filter-delete'
filter_box = 'filter-box'
filter_boxes = 'filter-boxes'
filter_modal = 'filter-modal'
show_filter_button = 'show-filter-button'
filter_configs = 'filter-configs'
filter_modal_ok = 'filter-modal-ok'
filter_cnt = 'filter-cnt'

filter_add_match = o_match(filter_add)
filter_delete_match = o_match(filter_delete)
filter_box_match = o_match(filter_box)
filter_boxes_match = o_match(filter_boxes)
filter_modal_match = o_match(filter_modal)
show_filter_button_match = o_match(show_filter_button)
filter_configs_match = o_match(filter_configs)
filter_modal_ok_match = o_match(filter_modal_ok)
filter_cnt_match = o_match(filter_cnt)


compute_add = 'compute-add'
compute_delete = 'compute-delete'
compute_box = 'compute-box'
compute_boxes = 'compute-boxes'
compute_modal = 'compute-modal'
show_compute_button = 'show-compute-button'
compute_configs = 'compute-configs'
compute_modal_ok = 'compute-modal-ok'
compute_cnt = 'compute-cnt'
compute_store = 'compute-store'

compute_add_match = o_match(compute_add)
compute_delete_match = o_match(compute_delete)
compute_box_match = o_match(compute_box)
compute_boxes_match = o_match(compute_boxes)
compute_store_match = o_match(compute_store)
compute_modal_match = o_match(compute_modal)
show_compute_button_match = o_match(show_compute_button)
compute_configs_match = o_match(compute_configs)
compute_modal_ok_match = o_match(compute_modal_ok)
compute_cnt_match = o_match(compute_cnt)