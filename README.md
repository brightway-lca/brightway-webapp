# bw_webapp
Template for a Brightway enabled Holoviz Panel Web Application based on Pyodide

## Converting to Pyodide

Rename things:

1. Update all instances of:

```
https://cdn.holoviz.org/panel/1.4.2
```

with [the most current version of Panel](https://github.com/holoviz/panel/releases).

2. Update all instances of:

```
importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js");
```

and

```
const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.4.1-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.4.2/dist/wheels/panel-1.4.2-py3-none-any.whl', 'pyodide-http==0.2.1', 'app/requirements.txt']
```


3. Rename :

```
"./panel_app.js"
```