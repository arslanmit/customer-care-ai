#!/usr/bin/env python3
import os
import psycopg2
from pathlib import Path
from typing import Optional

# Get database connection details from environment variables
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')
if not SUPABASE_DB_URL:
    raise ValueError(
        "Database connection string not found. "
        "Please set the SUPABASE_DB_URL environment variable.")

# Convert SQLAlchemy URL to psycopg2 format if needed
if SUPABASE_DB_URL.startswith('postgresql+psycopg2://'):
    SUPABASE_DB_URL = SUPABASE_DB_URL.replace('postgresql+psycopg2://', 'postgresql://')

class DatabaseManager:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn = None
    
    def connect(self):
        """Establish a database connection with SSL"""
        if not self.conn or self.conn.closed:
            # Parse connection string
            from urllib.parse import urlparse, parse_qs
            
            # Parse the connection string
            result = urlparse(self.connection_string)
            username = result.username
            password = result.password
            hostname = result.hostname
            port = result.port or 5432
            database = result.path[1:]  # Remove leading '/'
            
            # Build connection parameters
            conn_params = {
                'dbname': database,
                'user': username,
                'password': password,
                'host': hostname,
                'port': port,
                'sslmode': 'require'
            }
            
            # Connect to the database
            self.conn = psycopg2.connect(**conn_params)
            self.conn.autocommit = True
            
        return self.conn
    
    def close(self):
        """Close the database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
    
    def enable_extension(self, extension_name: str) -> bool:
        """Enable a PostgreSQL extension"""
        try:
            with self.connect().cursor() as cur:
                cur.execute(f'CREATE EXTENSION IF NOT EXISTS "{extension_name}"')
                print(f"✅ Enabled extension: {extension_name}")
                return True
        except Exception as e:
            print(f"❌ Failed to enable extension {extension_name}: {str(e)}")
            return False
    
    def execute_sql(self, sql: str) -> bool:
        """Execute raw SQL against the database"""
        try:
            with self.connect().cursor() as cur:
                # Split SQL into individual statements and execute each one
                statements = []
                current_statement = []
                in_block_comment = False
                
                # Parse SQL file line by line
                for line in sql.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('--'):
                        continue
                        
                    # Handle block comments
                    if '/*' in line:
                        in_block_comment = True
                        line = line.split('/*')[0].strip()
                        if not line:
                            continue
                    
                    if '*/' in line:
                        in_block_comment = False
                        line = line.split('*/')[1].strip()
                        if not line:
                            continue
                    
                    if in_block_comment:
                        continue
                        
                    current_statement.append(line)
                    
                    # If line ends with ;, it's the end of a statement
                    if line.endswith(';'):
                        statement = ' '.join(current_statement).strip()
                        if statement and not statement.startswith('--'):
                            statements.append(statement)
                        current_statement = []
                
                # Add any remaining statement without a trailing ;
                if current_statement:
                    statement = ' '.join(current_statement).strip()
                    if statement and not statement.startswith('--'):
                        statements.append(statement)
                
                # Execute each statement
                for stmt in statements:
                    if not stmt or stmt.startswith('--'):
                        continue
                    try:
                        print(f"\nExecuting: {stmt[:100]}{'...' if len(stmt) > 100 else ''}")
                        cur.execute(stmt)
                        print("✅ Success")
                    except Exception as e:
                        print(f"❌ Error in statement: {e}")
                        print(f"Statement: {stmt[:200]}...")
                        return False
                return True
        except Exception as e:
            print(f"❌ Database connection error: {str(e)}")
            return False
    
    def apply_migration(self, migration_file: Path) -> bool:
        """Apply a single migration file"""
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()
                print(f"\n📄 Applying migration: {migration_file.name}")
                
                # Split SQL into individual statements, handling dollar-quoted strings
                statements = []
                current_statement = []
                in_dollar_quote = False
                dollar_tag = None
                
                for line in sql.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('--'):
                        continue
                        
                    # Handle dollar-quoted strings
                    if '$' in line:
                        if not in_dollar_quote:
                            # Look for opening $
                            dollar_tag = line[line.index('$')+1:].split('$')[0]
                            if dollar_tag:
                                in_dollar_quote = True
                                current_statement.append(line)
                                continue
                        else:
                            # Look for closing $
                            if f'${dollar_tag}$' in line:
                                in_dollar_quote = False
                                current_statement.append(line)
                                statements.append('\n'.join(current_statement).strip())
                                current_statement = []
                                continue
                    
                    if in_dollar_quote:
                        current_statement.append(line)
                        continue
                        
                    # Regular SQL statement
                    if ';' in line:
                        parts = line.split(';')
                        if parts[0].strip():
                            current_statement.append(parts[0].strip())
                        if current_statement:
                            statements.append(' '.join(current_statement).strip())
                        current_statement = []
                        if len(parts) > 1 and parts[1].strip():
                            current_statement.append(parts[1].strip())
                    else:
                        current_statement.append(line)
                
                # Add any remaining statement
                if current_statement:
                    statements.append(' '.join(current_statement).strip())
                
                # Execute each statement
                success = True
                for stmt in statements:
                    if not stmt or stmt.startswith('--'):
                        continue
                    try:
                        print(f"  → Executing: {stmt[:100]}{'...' if len(stmt) > 100 else ''}")
                        with self.connect().cursor() as cur:
                            cur.execute(stmt)
                        print("  ✓ Success")
                    except Exception as e:
                        print(f"  ❌ Error in statement: {e}")
                        print(f"  Statement: {stmt[:200]}...")
                        success = False
                        break
                return success
                
        except Exception as e:
            print(f"❌ Error reading migration file {migration_file}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def get_migration_files(base_dir: Path) -> list[Path]:
    """Get all migration files in versioned subdirectories, sorted by version and filename."""
    migration_dirs = sorted(
        [d for d in base_dir.iterdir() if d.is_dir() and d.name.isdigit()],
        key=lambda x: int(x.name)
    )
    
    migration_files = []
    for version_dir in migration_dirs:
        # Get all SQL files in the version directory and sort them by name
        files = sorted(version_dir.glob("*.sql"))
        # Skip the problematic function file and use the simple version instead
        files = [f for f in files if '04_insert_event_function.sql' not in str(f)]
        migration_files.extend(files)
    
    # Add the simple function file if it exists
    simple_func = base_dir / "2024062101" / "04_insert_event_function_simple.sql"
    if simple_func.exists():
        migration_files.append(simple_func)
    
    return migration_files

def main():
    # Initialize database manager
    db = DatabaseManager(SUPABASE_DB_URL)
    
    try:
        # Test connection
        print("🔌 Testing database connection...")
        with db.connect().cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"✅ Connected to: {version}")
        
        # Enable required extensions
        print("\n🔧 Enabling PostgreSQL extensions...")
        for ext in ["uuid-ossp", "pgcrypto"]:
            if not db.enable_extension(ext):
                print(f"❌ Failed to enable extension: {ext}")
                return
        
        # Apply migrations
        migrations_base_dir = Path("supabase/migrations")
        if not migrations_base_dir.exists():
            print(f"❌ Migrations directory not found: {migrations_base_dir}")
            return
        
        # Get all migration files in versioned subdirectories
        migration_files = get_migration_files(migrations_base_dir)
        if not migration_files:
            print("❌ No migration files found in versioned subdirectories.")
            return
        
        print("\n🚀 Applying migrations...")
        for migration in migration_files:
            print(f"\n📄 Processing: {migration.relative_to(migrations_base_dir)}")
            if db.apply_migration(migration):
                print(f"✅ Successfully applied: {migration.name}")
            else:
                print(f"❌ Failed to apply migration: {migration.name}")
                return  # Stop on first failure
        
        print("\n🎉 Database setup completed successfully!")
        
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("\n🔌 Database connection closed.")

if __name__ == "__main__":
    main()
