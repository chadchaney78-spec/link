#!/bin/bash

# Quick Start Script for LINK Studio OS - Mission Control

echo "🎯 LINK Studio OS - Mission Control"
echo "==================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "studio_os.py" ]; then
    echo "❌ Run this script from the studio-sandbox directory"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"

# Verify data directories exist
echo ""
echo "📁 Checking data directories..."

if [ -d "../../../../Company/Money" ]; then
    echo "✓ Money registers found"
else
    echo "⚠️  Money registers not found - will be created on first run"
fi

if [ -d "../../../../Company/Marketing/social" ]; then
    echo "✓ Social data found"
else
    echo "⚠️  Social data not found - will be created on first run"
fi

# Run tests
echo ""
echo "🧪 Running tests..."
python3 -m pytest tests/ -v --tb=short

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Some tests failed, but continuing..."
fi

# Start server
echo ""
echo "🚀 Starting Studio OS server..."
echo ""
echo "   Dashboard: http://localhost:8792"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

python3 studio_os.py
