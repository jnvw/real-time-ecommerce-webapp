"""
Script to migrate data from SQLite to PostgreSQL
Run this locally before deploying to Railway, or run it on Railway after connecting to local SQLite
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collab_commerce.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
import json

def export_sqlite_data():
    """Export all data from SQLite database to JSON"""
    print("Exporting data from SQLite...")
    
    # Temporarily switch to SQLite
    original_db = settings.DATABASES['default']
    
    # Use SQLite for export
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(settings.BASE_DIR, 'db.sqlite3'),
    }
    
    # Export data
    output_file = 'data_export.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        call_command('dumpdata', 
                    exclude=['contenttypes', 'auth.Permission', 'sessions'],
                    natural_foreign=True,
                    natural_primary=True,
                    indent=2,
                    stdout=f)
    
    # Restore original database config
    settings.DATABASES['default'] = original_db
    
    print(f"Data exported to {output_file}")
    return output_file

def import_to_postgresql(json_file):
    """Import data from JSON to PostgreSQL"""
    print("Importing data to PostgreSQL...")
    
    # Ensure we're using PostgreSQL
    if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
        print("ERROR: Not using PostgreSQL! Check DATABASE_URL environment variable.")
        return False
    
    # Load and import data
    with open(json_file, 'r', encoding='utf-8') as f:
        call_command('loaddata', json_file)
    
    print("Data imported successfully!")
    return True

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'export':
        export_sqlite_data()
    elif len(sys.argv) > 1 and sys.argv[1] == 'import':
        json_file = sys.argv[2] if len(sys.argv) > 2 else 'data_export.json'
        import_to_postgresql(json_file)
    else:
        print("Usage:")
        print("  python migrate_data.py export  - Export from SQLite to JSON")
        print("  python migrate_data.py import [file] - Import from JSON to PostgreSQL")

