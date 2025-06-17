#!/usr/bin/env python3
"""
Fix for Airflow migration issue with missing mysql_drop_foreignkey_if_exists function.
This script monkey-patches the missing function to allow migrations to run.
"""

def mysql_drop_foreignkey_if_exists(op, table_name, constraint_name, **kwargs):
"""
Stub function to replace the missing mysql_drop_foreignkey_if_exists.
Since we're using PostgreSQL, this MySQL-specific function doesn't need to do anything.
"""
pass

# Monkey patch the missing function into the utils module
import airflow.migrations.utils
airflow.migrations.utils.mysql_drop_foreignkey_if_exists = mysql_drop_foreignkey_if_exists

print("Successfully patched mysql_drop_foreignkey_if_exists function")
