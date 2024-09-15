## Conversion to Pyodide

```bash
panel convert app/app.py --to pyodide-worker --out index --requirements app/requirements.txt
```

## Testing Pyodide Application

```bash
python -m http.server
```