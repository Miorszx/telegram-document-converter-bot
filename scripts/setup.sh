#!/bin/bash

# Telegram Document Converter Bot Setup Script
# This script sets up the environment and dependencies

set -e  # Exit on any error

echo "🚀 Setting up Telegram Document Converter Bot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is installed
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION found"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        print_success "pip found"
        PIP_CMD="pip"
    else
        print_error "pip not found. Please install pip"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
        # Update pip and setuptools
        pip install --upgrade pip setuptools wheel
    else
        print_error "Virtual environment not found"
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    print_status "Checking system dependencies..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            print_status "Installing system dependencies (Ubuntu/Debian)..."
            sudo apt-get update
            sudo apt-get install -y \
                libmagic1 \
                libjpeg-dev \
                libpng-dev \
                libtiff-dev \
                libfreetype6-dev \
                fonts-liberation \
                fonts-dejavu-core
            
            # Optional: Install LibreOffice
            read -p "Install LibreOffice for better document conversion? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                sudo apt-get install -y libreoffice
                print_success "LibreOffice installed"
            fi
            
            # Optional: Install Pandoc
            read -p "Install Pandoc for alternative document conversion? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                sudo apt-get install -y pandoc
                print_success "Pandoc installed"
            fi
            
        elif command -v yum &> /dev/null; then
            print_status "Installing system dependencies (RHEL/CentOS)..."
            sudo yum install -y \
                file-devel \
                libjpeg-devel \
                libpng-devel \
                libtiff-devel \
                freetype-devel
        else
            print_warning "Unknown Linux distribution. Please install dependencies manually."
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            print_status "Installing system dependencies (macOS)..."
            brew install libmagic
            
            # Optional: Install LibreOffice
            read -p "Install LibreOffice for better document conversion? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                brew install --cask libreoffice
                print_success "LibreOffice installed"
            fi
            
            # Optional: Install Pandoc
            read -p "Install Pandoc for alternative document conversion? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                brew install pandoc
                print_success "Pandoc installed"
            fi
        else
            print_warning "Homebrew not found. Please install dependencies manually."
        fi
        
    elif [[ "$OSTYPE" == "msys" ]]; then
        # Windows (Git Bash/MSYS2)
        print_warning "Windows detected. Please install dependencies manually:"
        print_warning "1. Download LibreOffice from https://www.libreoffice.org/"
        print_warning "2. Download Pandoc from https://pandoc.org/installing.html"
        
    else
        print_warning "Unknown OS. Please install dependencies manually."
    fi
}

# Setup environment file
setup_env() {
    print_status "Setting up environment file..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Environment file created from template"
            print_warning "Please edit .env file and add your Telegram bot token!"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs temp data
    print_success "Directories created"
}

# Setup complete message
setup_complete() {
    print_success "Setup completed successfully! 🎉"
    echo
    print_status "Next steps:"
    echo "1. Edit .env file and add your Telegram bot token:"
    echo "   nano .env"
    echo
    echo "2. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo
    echo "3. Run the bot:"
    echo "   python main.py"
    echo
    print_status "For more information, see README.md"
}

# Main setup process
main() {
    echo "🤖 Telegram Document Converter Bot Setup"
    echo "========================================"
    echo
    
    check_python
    check_pip
    create_venv
    activate_venv
    install_dependencies
    install_system_deps
    setup_env
    create_directories
    setup_complete
}

# Run main function
main "$@"
