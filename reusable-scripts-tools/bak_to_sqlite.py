#!/usr/bin/env python3
"""
MSSQL .bak Backup to SQLite Converter
======================================

Purpose:
    Restores a SQL Server .bak backup file to a temporary database on a local
    SQL Server instance, exports all user tables and their data to a SQLite file,
    then drops the temporary database.

Usage (CLI):
    python bak_to_sqlite.py -src "path/to/backup.bak"
    python bak_to_sqlite.py -src "path/to/backup.bak" -dst "path/to/output.sqlite3"
    python bak_to_sqlite.py -src "path/to/backup.bak" -server "SERVER\\INSTANCE"
    python bak_to_sqlite.py -src "path/to/backup.bak" -driver "ODBC Driver 18 for SQL Server"

Usage (Claude Code slash command):
    /bak-to-sqlite
    Assumes the .bak file is in the project root directory.

Arguments:
    -src        Path to the .bak file (required from CLI)
    -dst        Path for the output .sqlite3 file (optional; defaults to same
                directory as .bak with .sqlite3 extension)
    -server     SQL Server instance (default: OFC-NISHAN\\SQLEXPRESS)
    -driver     ODBC driver name (default: ODBC Driver 17 for SQL Server)
    -tempdb     Name for the temporary restore database (default: _bak_restore_temp)

Requirements:
    - pyodbc (pip install pyodbc)
    - A local SQL Server instance with permission to RESTORE and DROP databases
    - The SQL Server service account must have read access to the .bak file path

Notes:
    - The temporary database is dropped after export, even if an error occurs
    - Existing output .sqlite3 files are overwritten
    - All user tables (not system tables) are exported
    - Column types are mapped: INT/BIGINT -> INTEGER, FLOAT/DECIMAL/REAL/MONEY ->
      REAL, BIT -> INTEGER, DATETIME/DATE -> TEXT, all others -> TEXT
    - IDENTITY columns become INTEGER PRIMARY KEY AUTOINCREMENT in SQLite
    - Primary keys, unique constraints, and unique indexes are preserved

Author: nishans@shiploads.com.au
Created: 2026-06-02
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path

try:
    import pyodbc
except ImportError:
    print("ERROR: pyodbc is required. Install with: pip install pyodbc", file=sys.stderr)
    sys.exit(1)


# Default SQL Server connection settings
DEFAULT_SERVER = r"OFC-NISHAN\SQLEXPRESS"
DEFAULT_DRIVER = "ODBC Driver 17 for SQL Server"
DEFAULT_TEMP_DB = "_bak_restore_temp"


def connect_mssql(server: str, database: str, driver: str) -> pyodbc.Connection:
    """Connect to SQL Server using Windows authentication."""
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
        f"Encrypt=no;"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str, autocommit=True)


def restore_bak(conn: pyodbc.Connection, bak_path: str, temp_db: str) -> None:
    """Restore a .bak file to a temporary database.

    Steps:
    1. Query FILELISTONLY to discover the logical file names inside the backup
    2. Determine SQL Server's default data directory for placing restored files
    3. RESTORE DATABASE ... WITH MOVE to the temp location
    """
    bak_path = os.path.abspath(bak_path)
    print(f"  Reading backup file list from: {bak_path}")

    # Get logical file names from backup
    cursor = conn.cursor()
    cursor.execute(f"RESTORE FILELISTONLY FROM DISK = N'{bak_path}'")
    files = []
    for row in cursor.fetchall():
        files.append({
            "logical": row.LogicalName,
            "type": row.Type,  # 'D' = data, 'L' = log
        })
    cursor.close()

    if not files:
        raise RuntimeError("No files found in .bak backup")

    # Get SQL Server default data directory
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SERVERPROPERTY('InstanceDefaultDataPath') AS data_path, "
        "SERVERPROPERTY('InstanceDefaultLogPath') AS log_path"
    )
    row = cursor.fetchone()
    data_dir = row.data_path.rstrip("\\") if row.data_path else "C:\\SQLData"
    log_dir = row.log_path.rstrip("\\") if row.log_path else data_dir
    cursor.close()

    # Drop temp DB if it already exists (from a previous failed run)
    try:
        conn.execute(f"""
            IF DB_ID(N'{temp_db}') IS NOT NULL
            BEGIN
                ALTER DATABASE [{temp_db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                DROP DATABASE [{temp_db}];
            END
        """)
    except Exception:
        pass  # DB might not exist, that's fine

    # Build MOVE clauses
    move_clauses = []
    for f in files:
        if f["type"] == "D":
            target = f"{data_dir}\\{temp_db}.mdf"
        else:
            target = f"{log_dir}\\{temp_db}_log.ldf"
        move_clauses.append(f"MOVE N'{f['logical']}' TO N'{target}'")

    move_sql = ", ".join(move_clauses)
    restore_sql = (
        f"RESTORE DATABASE [{temp_db}] FROM DISK = N'{bak_path}' "
        f"WITH {move_sql}, REPLACE, RECOVERY"
    )

    print(f"  Restoring to temporary database [{temp_db}]...")
    # RESTORE sends progress messages as extra result sets. We must consume
    # them all with nextset(), otherwise pyodbc returns before the restore
    # finishes and the DB stays in RESTORING state.
    cursor = conn.cursor()
    cursor.execute(restore_sql)
    while cursor.nextset():
        pass
    cursor.close()

    # Verify the database came online after restore
    state = conn.execute(
        f"SELECT state_desc FROM sys.databases WHERE name = N'{temp_db}'"
    ).fetchone()
    if not state or state.state_desc != "ONLINE":
        actual = state.state_desc if state else "NOT FOUND"
        raise RuntimeError(
            f"Restore completed but database is {actual}. "
            f"If this is a differential backup, you must restore the full backup first."
        )

    # Grant the current login access to the restored database.
    # The backup's user mappings won't include the current Windows login.
    current_login = conn.execute("SELECT SYSTEM_USER AS login").fetchone().login
    try:
        conn.execute(f"ALTER AUTHORIZATION ON DATABASE::[{temp_db}] TO [{current_login}]")
    except Exception:
        # Fallback: create a user mapping instead
        try:
            conn.execute(
                f"USE [{temp_db}]; "
                f"IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'{current_login}') "
                f"CREATE USER [{current_login}] FOR LOGIN [{current_login}]; "
                f"ALTER ROLE db_owner ADD MEMBER [{current_login}]; "
                f"USE [master];"
            )
        except Exception as e:
            raise RuntimeError(f"Cannot grant access to restored database: {e}")

    print(f"  Restore complete.")


def drop_temp_db(conn: pyodbc.Connection, temp_db: str) -> None:
    """Drop the temporary database."""
    try:
        conn.execute(f"""
            IF DB_ID(N'{temp_db}') IS NOT NULL
            BEGIN
                ALTER DATABASE [{temp_db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                DROP DATABASE [{temp_db}];
            END
        """)
        print(f"  Temporary database [{temp_db}] dropped.")
    except Exception as e:
        print(f"  WARNING: Failed to drop temporary database [{temp_db}]: {e}", file=sys.stderr)


def get_user_tables(conn: pyodbc.Connection) -> list:
    """Get all user table names from the connected database."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    tables = [(row.TABLE_SCHEMA, row.TABLE_NAME) for row in cursor.fetchall()]
    cursor.close()
    return tables


def get_columns(conn: pyodbc.Connection, schema: str, table: str) -> list:
    """Get column info for a table, including IDENTITY and DEFAULT detection."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.COLUMN_NAME, c.DATA_TYPE, c.IS_NULLABLE, c.CHARACTER_MAXIMUM_LENGTH,
               COLUMNPROPERTY(OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME), c.COLUMN_NAME, 'IsIdentity') AS is_identity,
               c.COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS c
        WHERE c.TABLE_SCHEMA = ? AND c.TABLE_NAME = ?
        ORDER BY c.ORDINAL_POSITION
    """, (schema, table))
    columns = [{
        "name": row.COLUMN_NAME,
        "type": row.DATA_TYPE,
        "nullable": row.IS_NULLABLE == "YES",
        "max_length": row.CHARACTER_MAXIMUM_LENGTH,
        "is_identity": bool(row.is_identity),
        "default": row.COLUMN_DEFAULT,
    } for row in cursor.fetchall()]
    cursor.close()
    return columns


def mssql_default_to_sqlite(default_expr: str, sqlite_type: str) -> str:
    """Convert an MSSQL default expression to a SQLite DEFAULT clause.

    MSSQL wraps defaults in parens, e.g. (('none')), ((0)), (getdate()).
    Returns the DEFAULT clause string, or empty string if not convertible.
    """
    if not default_expr:
        return ""
    # Strip outer parens — MSSQL uses ((...)) for scalar defaults
    expr = default_expr.strip()
    while expr.startswith("(") and expr.endswith(")"):
        expr = expr[1:-1]
    # Skip function-based defaults (getdate(), newid(), etc.)
    if "(" in expr:
        return ""
    # Numeric defaults
    if sqlite_type in ("INTEGER", "REAL"):
        try:
            float(expr)
            return f" DEFAULT {expr}"
        except ValueError:
            return ""
    # String defaults — MSSQL uses N'value' or 'value'
    if expr.startswith("N'") or expr.startswith("n'"):
        expr = expr[1:]  # strip the N prefix
    if expr.startswith("'") and expr.endswith("'"):
        return f" DEFAULT {expr}"
    return ""


def get_primary_key(conn: pyodbc.Connection, schema: str, table: str) -> list:
    """Get primary key column names for a table."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT col.name
        FROM sys.indexes idx
        JOIN sys.index_columns ic ON idx.object_id = ic.object_id AND idx.index_id = ic.index_id
        JOIN sys.columns col ON ic.object_id = col.object_id AND ic.column_id = col.column_id
        WHERE idx.is_primary_key = 1
          AND idx.object_id = OBJECT_ID(? + '.' + ?)
        ORDER BY ic.key_ordinal
    """, (schema, table))
    pk_cols = [row.name for row in cursor.fetchall()]
    cursor.close()
    return pk_cols


def get_unique_constraints(conn: pyodbc.Connection, schema: str, table: str) -> list:
    """Get unique constraints and unique indexes (excluding the PK) for a table.

    Returns a list of lists, where each inner list is the column names of one
    unique constraint/index.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT idx.name AS index_name, col.name AS column_name, ic.key_ordinal
        FROM sys.indexes idx
        JOIN sys.index_columns ic ON idx.object_id = ic.object_id AND idx.index_id = ic.index_id
        JOIN sys.columns col ON ic.object_id = col.object_id AND ic.column_id = col.column_id
        WHERE idx.is_unique = 1
          AND idx.is_primary_key = 0
          AND idx.object_id = OBJECT_ID(? + '.' + ?)
        ORDER BY idx.name, ic.key_ordinal
    """, (schema, table))
    rows = cursor.fetchall()
    cursor.close()

    # Group columns by index name
    constraints = {}
    for row in rows:
        constraints.setdefault(row.index_name, []).append(row.column_name)
    return list(constraints.values())


def mssql_type_to_sqlite(mssql_type: str) -> str:
    """Map MSSQL data types to SQLite types."""
    mssql_type = mssql_type.lower()
    if mssql_type in ("int", "bigint", "smallint", "tinyint", "bit"):
        return "INTEGER"
    if mssql_type in ("float", "real", "decimal", "numeric", "money", "smallmoney"):
        return "REAL"
    if mssql_type in ("varbinary", "binary", "image"):
        return "BLOB"
    # Everything else (varchar, nvarchar, text, ntext, datetime, date, etc.)
    return "TEXT"


def export_to_sqlite(mssql_conn: pyodbc.Connection, sqlite_path: str) -> dict:
    """Export all user tables from the connected MSSQL database to SQLite.

    Returns a dict of table_name -> row_count for reporting.
    """
    tables = get_user_tables(mssql_conn)
    if not tables:
        print("  WARNING: No user tables found in database.", file=sys.stderr)
        return {}

    # Remove existing SQLite file
    if os.path.exists(sqlite_path):
        os.remove(sqlite_path)

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.execute("PRAGMA journal_mode=WAL")
    sqlite_conn.execute("PRAGMA synchronous=OFF")  # Speed up bulk insert

    report = {}

    for schema, table in tables:
        full_name = f"{schema}.{table}" if schema != "dbo" else table
        sqlite_table = f"{schema}_{table}" if schema != "dbo" else table
        columns = get_columns(mssql_conn, schema, table)

        if not columns:
            print(f"  Skipping {full_name} (no columns)")
            continue

        pk_cols = get_primary_key(mssql_conn, schema, table)
        unique_constraints = get_unique_constraints(mssql_conn, schema, table)

        # Single-column IDENTITY PKs become INTEGER PRIMARY KEY AUTOINCREMENT
        # (SQLite's rowid alias — allows inserts without specifying the column)
        identity_pk_col = None
        if len(pk_cols) == 1:
            for col in columns:
                if col["name"] == pk_cols[0] and col["is_identity"]:
                    identity_pk_col = pk_cols[0]
                    break

        # Create SQLite table
        col_defs = []
        for col in columns:
            sqlite_type = mssql_type_to_sqlite(col["type"])
            null_clause = "" if col["nullable"] else " NOT NULL"
            pk_clause = ""
            if col["name"] == identity_pk_col:
                pk_clause = " PRIMARY KEY AUTOINCREMENT"
                null_clause = ""  # PRIMARY KEY implies NOT NULL
            default_clause = "" if pk_clause else mssql_default_to_sqlite(col["default"], sqlite_type)
            col_defs.append(f'"{col["name"]}" {sqlite_type}{pk_clause}{default_clause}{null_clause}')

        # Add composite PRIMARY KEY as table constraint (if not single-column IDENTITY)
        if pk_cols and not identity_pk_col:
            pk_quoted = ", ".join(f'"{c}"' for c in pk_cols)
            col_defs.append(f"PRIMARY KEY ({pk_quoted})")

        # Add UNIQUE constraints as table constraints
        for uq_cols in unique_constraints:
            uq_quoted = ", ".join(f'"{c}"' for c in uq_cols)
            col_defs.append(f"UNIQUE ({uq_quoted})")

        create_sql = f'CREATE TABLE IF NOT EXISTS "{sqlite_table}" ({", ".join(col_defs)})'
        sqlite_conn.execute(create_sql)

        # Read and insert data
        col_names = [col["name"] for col in columns]
        select_sql = ", ".join(f'[{c}]' for c in col_names)
        placeholders = ", ".join("?" for _ in col_names)
        insert_sql = f'INSERT INTO "{sqlite_table}" ({", ".join(f"{c}" for c in col_names)}) VALUES ({placeholders})'

        cursor = mssql_conn.cursor()
        cursor.execute(f"SELECT {select_sql} FROM [{schema}].[{table}]")

        batch_size = 1000
        total_rows = 0
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            sqlite_conn.executemany(insert_sql, [tuple(row) for row in rows])
            total_rows += len(rows)

        cursor.close()
        sqlite_conn.commit()
        report[full_name] = total_rows
        print(f"  {full_name}: {total_rows} rows")

    sqlite_conn.execute("PRAGMA synchronous=FULL")
    sqlite_conn.close()
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Convert a SQL Server .bak backup file to a SQLite database.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Arguments:")[0],  # Show purpose section in help
    )
    parser.add_argument("-src", required=True, help="Path to the .bak backup file")
    parser.add_argument("-dst", default=None, help="Output SQLite path (default: same dir as .bak, .sqlite3 extension)")
    parser.add_argument("-server", default=DEFAULT_SERVER, help=f"SQL Server instance (default: {DEFAULT_SERVER})")
    parser.add_argument("-driver", default=DEFAULT_DRIVER, help=f"ODBC driver (default: {DEFAULT_DRIVER})")
    parser.add_argument("-tempdb", default=DEFAULT_TEMP_DB, help=f"Temp database name (default: {DEFAULT_TEMP_DB})")
    args = parser.parse_args()

    src = Path(args.src).resolve()
    if not src.exists():
        print(f"ERROR: .bak file not found: {src}", file=sys.stderr)
        sys.exit(1)
    if not src.suffix.lower() == ".bak":
        print(f"WARNING: File does not have .bak extension: {src}", file=sys.stderr)

    if args.dst:
        dst = Path(args.dst).resolve()
    else:
        dst = src.with_suffix(".sqlite3")

    print(f"Source:  {src}")
    print(f"Output:  {dst}")
    print(f"Server:  {args.server}")
    print()

    # Step 1: Connect to master and restore .bak to temp DB
    print("[1/4] Connecting to SQL Server...")
    master_conn = connect_mssql(args.server, "master", args.driver)

    try:
        # Step 2: Restore
        print("[2/4] Restoring backup...")
        restore_bak(master_conn, str(src), args.tempdb)

        # Step 3: Connect to restored DB and export
        print("[3/4] Exporting to SQLite...")
        temp_conn = connect_mssql(args.server, args.tempdb, args.driver)
        try:
            report = export_to_sqlite(temp_conn, str(dst))
        finally:
            temp_conn.close()

        # Step 4: Cleanup
        print("[4/4] Cleaning up temporary database...")
        drop_temp_db(master_conn, args.tempdb)

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        print("Attempting cleanup of temporary database...")
        drop_temp_db(master_conn, args.tempdb)
        master_conn.close()
        sys.exit(1)

    master_conn.close()

    print()
    print(f"Done. SQLite database written to: {dst}")
    print(f"Tables exported: {len(report)}")
    total = sum(report.values())
    print(f"Total rows: {total}")


if __name__ == "__main__":
    main()
