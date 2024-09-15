## Conversion to Pyodide

```bash
panel convert app/index.py --to pyodide-worker --out pyodide --requirements app/requirements.txt
```

## Testing Pyodide Application

```bash
python -m http.server
```