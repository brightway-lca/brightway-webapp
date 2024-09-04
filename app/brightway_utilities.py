import os

import panel as pn

import bw2data as bd
import bw2io as bi


def check_for_useeio_brightway_project(event):
    """
    Checks if the USEEIO-1.1 Brightway project is installed.
    If not, installs it. Shows Panel notifications for the user.

    Returns
    -------
    SQLiteBackend
        bw2data.backends.base.SQLiteBackend of the USEEIO-1.1 database
    """
    if 'USEEIO-1.1' not in bd.projects:
        notification_load = pn.state.notifications.info('Loading USEEIO database...')
        bi.install_project(project_key="USEEIO-1.1", overwrite_existing=True)
        notification_load.destroy()
        pn.state.notifications.success('USEEIO database loaded!', duration=7000)
    else:
        pn.state.notifications.success('USEEIO database already loaded!', duration=7000)
    bd.projects.set_current(name='USEEIO-1.1')


def brightway_wasm_database_storage_workaround() -> None:
    """
    Sets the Brightway project directory to `/tmp/.
    
    The JupyterLite file system currently does not support storage of SQL database files
    in directories other than `/tmp/`. This function sets the Brightway environment variable
    `BRIGHTWAY_DIR` to `/tmp/` to work around this limitation.
    
    Notes
    -----
    - https://docs.brightway.dev/en/latest/content/faq/data_management.html#how-do-i-change-my-data-directory
    - https://github.com/brightway-lca/brightway-live/issues/10
    """
    os.environ["BRIGHTWAY_DIR"] = "/tmp/"