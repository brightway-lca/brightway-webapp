# %%
import panel as pn

pn.extension(notifications=True)


def show_notification(event):
    
    pn.state.notifications.error('Sample error message!', duration=60000)


button = pn.widgets.Button(name='Show Notification')
button.on_click(show_notification)

pn.Column(button).servable()