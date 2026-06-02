Convert a SQL Server .bak backup file to a SQLite database.

Look for a .bak file in the current project root directory. If multiple .bak files exist, list them and ask which one to use. If none found, ask the user for the path.

Run the conversion script:

```
python "$HOME/.claude/reusable-scripts-tools/bak_to_sqlite.py" -src "<bak_file_path>"
```

The output .sqlite3 file will be created in the same directory as the .bak file with the same name but .sqlite3 extension.

If the script fails due to SQL Server connection issues, check:
1. SQL Server service is running: `sc query MSSQL$SQLEXPRESS`
2. The ODBC driver is installed: `python -c "import pyodbc; print(pyodbc.drivers())"`
3. The SQL Server service account has read access to the .bak file path

Report the output file path and table/row counts when complete.
