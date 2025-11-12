#!/bin/bash

# Niko Free Backend Setup Script

echo "🎉 Setting up Niko Free Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "⚠️  Please edit .env file with your configuration"
    else
        echo "❌ .env.example not found"
    fi
else
    echo "✅ .env file already exists"
fi

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p uploads/events
mkdir -p uploads/logos
mkdir -p uploads/profiles
mkdir -p uploads/qrcodes

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Set up PostgreSQL database"
echo "3. Run: flask init_db"
echo "4. Run: flask seed_db"
echo "5. Run: flask create_admin"
echo "6. Run: flask run"
echo ""
echo "To activate virtual environment:"
echo "  source venv/bin/activate"
echo ""

