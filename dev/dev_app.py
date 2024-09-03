# %%
import panel as pn

pn.extension()

my_list = pn.rx([])

def create_list(event):
    my_list = [1, 2, 3, 4, 5]
    print(my_list)

def modify_list(event):
    my_list.append(6)
    print(my_list)

widget_number = pn.indicators.Number(
    name='Number',
    value=0,
    format='{value}'
)

widget_button_create_list = pn.widgets.Button(name='Create List')
widget_button_create_list.on_click(create_list)

widget_button_modify_list = pn.widgets.Button(name='Modify List')
widget_button_modify_list.on_click(modify_list)

pn.Column(widget_button_create_list, widget_button_modify_list).servable()