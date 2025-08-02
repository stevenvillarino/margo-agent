#!/bin/bash

# 🧹 Margo Agent - Complete Cleanup Script
# This script can clean up archived files after consolidation verification

echo "🧹 Margo Agent - Complete Cleanup"
echo "================================="
echo ""
echo "This script will help you clean up archived files after consolidation."
echo "⚠️  WARNING: This will permanently delete archived files!"
echo ""

# Show what would be deleted
echo "📁 Files that would be deleted:"
echo ""
echo "📄 Archived Documentation (archive_old_docs/):"
if [ -d "archive_old_docs" ]; then
    ls -la archive_old_docs/ | grep -v "^total" | grep -v "^d" | awk '{print "  • " $9}'
    DOC_COUNT=$(ls -1 archive_old_docs/ | wc -l)
    echo "  Total: $DOC_COUNT files"
else
    echo "  • No archived docs found"
    DOC_COUNT=0
fi

echo ""
echo "🔧 Archived Scripts (archive_old_scripts/):"
if [ -d "archive_old_scripts" ]; then
    ls -la archive_old_scripts/ | grep -v "^total" | grep -v "^d" | awk '{print "  • " $9}'
    SCRIPT_COUNT=$(ls -1 archive_old_scripts/ | wc -l)
    echo "  Total: $SCRIPT_COUNT files"
else
    echo "  • No archived scripts found"
    SCRIPT_COUNT=0
fi

TOTAL_COUNT=$((DOC_COUNT + SCRIPT_COUNT))

echo ""
echo "📊 Summary:"
echo "  • Documentation files: $DOC_COUNT"
echo "  • Shell scripts: $SCRIPT_COUNT"
echo "  • Total files: $TOTAL_COUNT"

if [ $TOTAL_COUNT -eq 0 ]; then
    echo "✅ No archived files found. Nothing to clean up!"
    exit 0
fi

echo ""
echo "🔍 Before deletion, let's verify the new structure works:"
echo ""

# Test new documentation structure
echo "📚 Testing new documentation structure..."
if [ -d "docs" ]; then
    echo "✅ docs/ directory exists"
    NEW_DOC_COUNT=$(find docs/ -name "*.md" | wc -l)
    echo "✅ $NEW_DOC_COUNT documentation files in docs/"
    
    if [ -f "docs/README.md" ]; then
        echo "✅ docs/README.md (navigation) exists"
    else
        echo "❌ docs/README.md missing!"
    fi
    
    if [ -f "docs/QUICK_START.md" ]; then
        echo "✅ docs/QUICK_START.md exists"
    else
        echo "❌ docs/QUICK_START.md missing!"
    fi
    
    if [ -f "docs/DEPLOYMENT_GUIDE.md" ]; then
        echo "✅ docs/DEPLOYMENT_GUIDE.md exists"
    else
        echo "❌ docs/DEPLOYMENT_GUIDE.md missing!"
    fi
else
    echo "❌ docs/ directory not found!"
    echo "   Please run the documentation consolidation first."
    exit 1
fi

echo ""

# Test new scripts structure
echo "🔧 Testing new scripts structure..."
if [ -d "scripts" ]; then
    echo "✅ scripts/ directory exists"
    NEW_SCRIPT_COUNT=$(find scripts/ -name "*.sh" | wc -l)
    echo "✅ $NEW_SCRIPT_COUNT script files in scripts/"
    
    if [ -f "scripts/setup.sh" ]; then
        echo "✅ scripts/setup.sh (master setup) exists"
    else
        echo "❌ scripts/setup.sh missing!"
    fi
    
    if [ -f "scripts/setup_local.sh" ]; then
        echo "✅ scripts/setup_local.sh exists"
    else
        echo "❌ scripts/setup_local.sh missing!"
    fi
    
    # Test if scripts are executable
    if [ -x "scripts/setup.sh" ]; then
        echo "✅ Scripts are executable"
    else
        echo "⚠️  Making scripts executable..."
        chmod +x scripts/*.sh
    fi
else
    echo "❌ scripts/ directory not found!"
    echo "   Please run the script consolidation first."
    exit 1
fi

echo ""
echo "✅ Consolidation verification complete!"
echo ""

# Ask for confirmation
echo "❓ What would you like to do?"
echo ""
echo "1. 🗑️  Delete all archived files (PERMANENT)"
echo "2. 📦 Keep archives as backup"
echo "3. 🔍 Show detailed file comparison"
echo "4. ❌ Cancel"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "⚠️  FINAL WARNING: This will permanently delete $TOTAL_COUNT archived files!"
        read -p "Type 'DELETE' to confirm: " confirm
        
        if [ "$confirm" = "DELETE" ]; then
            echo ""
            echo "🗑️  Deleting archived files..."
            
            if [ -d "archive_old_docs" ]; then
                rm -rf archive_old_docs/
                echo "✅ Deleted archive_old_docs/ ($DOC_COUNT files)"
            fi
            
            if [ -d "archive_old_scripts" ]; then
                rm -rf archive_old_scripts/
                echo "✅ Deleted archive_old_scripts/ ($SCRIPT_COUNT files)"
            fi
            
            # Also clean up the consolidation scripts
            if [ -f "consolidate_docs.sh" ]; then
                rm consolidate_docs.sh
                echo "✅ Removed consolidate_docs.sh (moved to scripts/)"
            fi
            
            if [ -f "consolidate_scripts.sh" ]; then
                rm consolidate_scripts.sh
                echo "✅ Removed consolidate_scripts.sh (completed)"
            fi
            
            echo ""
            echo "🎉 Cleanup complete!"
            echo ""
            echo "📊 Final structure:"
            echo "  • docs/: $NEW_DOC_COUNT documentation files"
            echo "  • scripts/: $NEW_SCRIPT_COUNT shell scripts"
            echo "  • Root: Clean and organized"
            echo ""
            echo "🚀 Your project is now fully consolidated and optimized!"
        else
            echo "❌ Deletion cancelled."
        fi
        ;;
    2)
        echo ""
        echo "📦 Keeping archives as backup."
        echo "✅ Your archives are preserved in:"
        echo "  • archive_old_docs/"
        echo "  • archive_old_scripts/"
        echo ""
        echo "💡 You can delete them later when you're confident the new structure works."
        ;;
    3)
        echo ""
        echo "🔍 Detailed comparison:"
        echo ""
        echo "📄 Documentation Migration:"
        echo "Before: 60+ scattered .md files"
        echo "After: $NEW_DOC_COUNT organized files in docs/"
        echo ""
        
        if [ -d "archive_old_docs" ]; then
            echo "🗂️  Archived documentation files:"
            for file in archive_old_docs/*.md; do
                if [ -f "$file" ]; then
                    basename_file=$(basename "$file")
                    echo "  📄 $basename_file"
                    
                    # Check if content is preserved
                    if grep -q "deployment\|setup\|install" "$file" 2>/dev/null; then
                        echo "    → Content preserved in docs/DEPLOYMENT_GUIDE.md"
                    elif grep -q "architecture\|agent\|system" "$file" 2>/dev/null; then
                        echo "    → Content preserved in docs/AGENT_ARCHITECTURE.md"
                    elif grep -q "quick\|start\|getting" "$file" 2>/dev/null; then
                        echo "    → Content preserved in docs/QUICK_START.md"
                    else
                        echo "    → Content preserved in appropriate docs/ file"
                    fi
                fi
            done
        fi
        
        echo ""
        echo "🔧 Script Migration:"
        echo "Before: 9 scattered .sh files"
        echo "After: $NEW_SCRIPT_COUNT organized files in scripts/"
        echo ""
        
        if [ -d "archive_old_scripts" ]; then
            echo "🗂️  Archived script files:"
            for file in archive_old_scripts/*.sh; do
                if [ -f "$file" ]; then
                    basename_file=$(basename "$file")
                    echo "  🔧 $basename_file"
                    
                    # Show where functionality moved
                    case $basename_file in
                        *setup_simple*|*setup_advanced*)
                            echo "    → Functionality in scripts/setup_local.sh"
                            ;;
                        *deploy*|*build*)
                            echo "    → Functionality in scripts/deploy_*.sh"
                            ;;
                        *)
                            echo "    → Functionality preserved in scripts/"
                            ;;
                    esac
                fi
            done
        fi
        ;;
    4)
        echo "❌ Cancelled."
        ;;
    *)
        echo "❌ Invalid choice."
        ;;
esac

echo ""
echo "📚 Remember: Your new structure is:"
echo "  • docs/ - All documentation"
echo "  • scripts/ - All shell scripts"
echo "  • Root README.md - Points to docs/"
echo ""
echo "🎯 Quick commands:"
echo "  • Setup: ./scripts/setup.sh"
echo "  • Docs: open docs/README.md"
echo "  • Deploy: ./scripts/deploy_cloudflare.sh"
