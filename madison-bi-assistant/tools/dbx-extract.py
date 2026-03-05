# /// script
# requires-python = ">=3.10"
# dependencies = ["databricks-sql-connector"]
# ///
"""
dbx-extract -Bulk data extraction from Databricks to CSV.
Part of the madison-bi-assistant plugin.

Usage:
  uv run --script tools/dbx-extract.py --sql "SELECT ..." --output path.csv
  uv run --script tools/dbx-extract.py --sql-file query.sql --output path.csv

Credentials loaded from environment variables (or .env file):
  DATABRICKS_SERVER_HOSTNAME  (or DATABRICKS_HOST)
  DATABRICKS_HTTP_PATH
  DATABRICKS_ACCESS_TOKEN     (or DATABRICKS_TOKEN)
"""

import argparse
import csv
import os
import sys
from pathlib import Path


def _load_env_file(path: str) -> None:
    """Load KEY=VALUE pairs from file into os.environ. Skips comments and blanks."""
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = value
    except FileNotFoundError:
        pass


def _get_credentials() -> tuple[str, str, str]:
    """Resolve Databricks credentials from environment. Raises ValueError if missing."""
    hostname = os.environ.get("DATABRICKS_SERVER_HOSTNAME") or os.environ.get("DATABRICKS_HOST")
    http_path = os.environ.get("DATABRICKS_HTTP_PATH")
    token = os.environ.get("DATABRICKS_ACCESS_TOKEN") or os.environ.get("DATABRICKS_TOKEN")

    missing = []
    if not hostname:
        missing.append("DATABRICKS_SERVER_HOSTNAME")
    if not http_path:
        missing.append("DATABRICKS_HTTP_PATH")
    if not token:
        missing.append("DATABRICKS_ACCESS_TOKEN")

    if missing:
        raise ValueError(
            f"missing environment variable(s): {', '.join(missing)}. "
            f"Set them in your shell or create a .env file (see .env.example)."
        )

    return hostname, http_path, token


def _format_size(bytes_: int) -> str:
    """Human-readable file size."""
    for unit in ("B", "KB", "MB", "GB"):
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unit}" if unit != "B" else f"{bytes_} B"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dbx-extract",
        description="Bulk data extraction from Databricks to CSV.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--sql", help="SQL query string to execute")
    source.add_argument("--sql-file", help="Path to .sql file containing query")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    parser.add_argument("--env-file", default=None, help="Path to .env credentials file")
    parser.add_argument("--batch-size", type=int, default=10000, help="Rows per fetch batch (default: 10000)")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: comma)")
    parser.add_argument("--no-header", action="store_true", help="Omit CSV header row")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    # Load .env (explicit path, or project root default)
    env_path = args.env_file or ".env"
    _load_env_file(env_path)

    # Credentials
    try:
        hostname, http_path, token = _get_credentials()
    except ValueError as e:
        print(f"dbx-extract: credential error -{e}", file=sys.stderr)
        return 1

    # SQL
    if args.sql_file:
        sql_path = Path(args.sql_file)
        if not sql_path.exists():
            print(f"dbx-extract: SQL file not found -{sql_path}", file=sys.stderr)
            return 1
        sql = sql_path.read_text(encoding="utf-8").strip()
    else:
        sql = args.sql.strip()

    if not sql:
        print("dbx-extract: empty SQL query", file=sys.stderr)
        return 1

    # Output directory
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Import databricks connector (deferred so --help works without it)
    try:
        from databricks import sql as dbsql
    except ImportError:
        print("dbx-extract: missing databricks-sql-connector", file=sys.stderr)
        print("  recommended: uv run --script tools/dbx-extract.py [args]", file=sys.stderr)
        print("  alternative: pip install databricks-sql-connector", file=sys.stderr)
        return 1

    # Connect
    print(f"dbx-extract: connecting to {hostname}")
    try:
        conn = dbsql.connect(
            server_hostname=hostname,
            http_path=http_path,
            access_token=token,
        )
    except Exception as e:
        print(f"dbx-extract: connection failed -{e}", file=sys.stderr)
        return 1

    # Execute and stream
    try:
        cursor = conn.cursor()
        print(f"dbx-extract: executing query ({len(sql):,} chars)")

        try:
            cursor.execute(sql)
        except Exception as e:
            snippet = sql[:200] + ("..." if len(sql) > 200 else "")
            print(f"dbx-extract: query error -{e}", file=sys.stderr)
            print(f"  query: {snippet}", file=sys.stderr)
            return 1

        columns = [desc[0] for desc in cursor.description]

        total_rows = 0
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=args.delimiter)

            if not args.no_header:
                writer.writerow(columns)

            while True:
                batch = cursor.fetchmany(args.batch_size)
                if not batch:
                    break
                for row in batch:
                    writer.writerow(["" if v is None else v for v in row])
                total_rows += len(batch)
                print(f"dbx-extract: streaming... {total_rows:,} rows")

        cursor.close()
    except KeyboardInterrupt:
        print(f"\ndbx-extract: interrupted at {total_rows:,} rows", file=sys.stderr)
        return 130
    finally:
        conn.close()

    # Report
    file_size = output.stat().st_size
    col_preview = ", ".join(columns[:8])
    if len(columns) > 8:
        col_preview += f", ... (+{len(columns) - 8} more)"

    print("dbx-extract: complete")
    print(f"  rows:    {total_rows:,}")
    print(f"  columns: {len(columns)} ({col_preview})")
    print(f"  output:  {output}")
    print(f"  size:    {_format_size(file_size)}")

    if total_rows == 0:
        print("  warning: query returned zero data rows", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
