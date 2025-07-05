# app/init_docs.py

import os
import re
from pathlib import Path
from database import init_database, add_document_to_db, get_all_documents

def extract_title_from_filename(filename: str) -> str:
    """Extract readable title from filename"""
    # Remove number prefix and extension
    title = re.sub(r'^\d+_', '', filename)
    title = title.replace('.txt', '')
    title = title.replace('_', ' ')
    return title.title()

def load_sample_documents():
    """Load all sample documents from data/sample_docs/"""
    
    # Path to sample documents
    docs_dir = Path("data/sample_docs")
    
    if not docs_dir.exists():
        print(f"❌ Directory {docs_dir} not found!")
        return
    
    # Get all .txt files
    txt_files = list(docs_dir.glob("*.txt"))
    
    if not txt_files:
        print(f"❌ No .txt files found in {docs_dir}")
        return
    
    print(f"📁 Found {len(txt_files)} documents to load...")
    
    loaded_count = 0
    
    for file_path in sorted(txt_files):
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                print(f"⚠️  Skipping empty file: {file_path.name}")
                continue
            
            # Extract title from filename
            title = extract_title_from_filename(file_path.name)
            
            # Add to database
            doc = add_document_to_db(
                title=title,
                content=content,
                author="AI Learning Materials",  # Default author
                source=str(file_path)
            )
            
            print(f"✅ Loaded: {title} (ID: {doc.id})")
            loaded_count += 1
            
        except Exception as e:
            print(f"❌ Error loading {file_path.name}: {e}")
    
    print(f"\n🎉 Successfully loaded {loaded_count} documents!")

def show_document_summary():
    """Show summary of loaded documents"""
    docs = get_all_documents()
    
    if not docs:
        print("📭 No documents found in database")
        return
    
    print(f"\n📊 Database Summary:")
    print(f"Total documents: {len(docs)}")
    print("\nDocuments:")
    
    for doc in docs:
        word_count = len(doc.content.split()) if doc.content else 0
        print(f"  {doc.id}: {doc.title} ({word_count} words)")

def main():
    """Main initialization function"""
    print("🚀 Initializing Document Analyzer Database...")
    
    # Step 1: Initialize database
    print("\n1️⃣ Creating database tables...")
    init_database()
    
    # Step 2: Check if documents already exist
    existing_docs = get_all_documents()
    if existing_docs:
        print(f"📋 Found {len(existing_docs)} existing documents")
        response = input("Do you want to reload all documents? (y/N): ").lower()
        
        if response == 'y':
            # For simplicity, we'll keep existing docs and skip duplicates
            # In production, you might want to clear and reload
            pass
    
    # Step 3: Load sample documents
    print("\n2️⃣ Loading sample documents...")
    load_sample_documents()
    
    # Step 4: Show summary
    print("\n3️⃣ Database summary:")
    show_document_summary()
    
    print("\n✨ Database initialization complete!")
    print("🔧 You can now start the MCP server with: python app/server.py")

if __name__ == "__main__":
    main() 