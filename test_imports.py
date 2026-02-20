#!/usr/bin/env python3
"""Test script to verify all imports work correctly"""

import sys
import traceback

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        print("✓ Importing domain layer...")
        from src.app.domain import entities, value_objects, ports, exceptions
        
        print("✓ Importing application layer...")
        from src.app.application import dto, interactors, queries, ports
        
        print("✓ Importing infrastructure layer...")
        from src.app.infrastructure import (
            security, email, image, search, sitemap
        )
        from src.app.infrastructure.persistence import (
            models, database, repositories, mappers, unit_of_work
        )
        from src.app.infrastructure.utils import (
            base64_utils, json_yaml_converter, string_utils, csv_importer
        )
        
        print("✓ Importing presentation layer...")
        from src.app.presentation import schemas, middleware, dependencies
        from src.app.presentation.api import (
            auth, cart, categories, orders, products, utils
        )
        
        print("✓ Importing DI container...")
        from src.app import di
        
        print("✓ Importing main app...")
        from src.app import main
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
