#!/bin/bash

# Primordia Website - Quick Start Script
# Phase 1: Desktop Implementation

set -e

echo "🚀 Primordia Website - Phase 1 Setup"
echo "===================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    exit 1
fi

echo "✅ npm version: $(npm -v)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# Start dev server
echo "🏃 Starting development server..."
echo "   → Home: http://localhost:3000"
echo "   → Fund: http://localhost:3000/fund"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
