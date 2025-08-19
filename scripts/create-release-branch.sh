#!/bin/bash

# Create Release Branch Script
# This script creates a new release branch with version bump

set -e

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

# Function to get current version from pyproject.toml
get_current_version() {
    grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'
}

# Function to bump version
bump_version() {
    local current_version=$1
    local bump_type=$2
    
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case $bump_type in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
        *)
            print_error "Invalid bump type: $bump_type"
            exit 1
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# Function to update version in files
update_version() {
    local new_version=$1
    
    print_status "Updating version to $new_version..."
    
    # Update pyproject.toml
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^version = \".*\"/version = \"$new_version\"/" pyproject.toml
    else
        # Linux
        sed -i "s/^version = \".*\"/version = \"$new_version\"/" pyproject.toml
    fi
    
    # Update __init__.py
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/^__version__ = \".*\"/__version__ = \"$new_version\"/" mockexchange_gateway/__init__.py
    else
        sed -i "s/^__version__ = \".*\"/__version__ = \"$new_version\"/" mockexchange_gateway/__init__.py
    fi
    
    print_success "Version updated in pyproject.toml and __init__.py"
}

# Function to create release branch
create_release_branch() {
    local bump_type=$1
    local current_version=$(get_current_version)
    local new_version=$(bump_version "$current_version" "$bump_type")
    local branch_name="release/v$new_version"
    
    print_status "Current version: $current_version"
    print_status "New version: $new_version"
    print_status "Creating branch: $branch_name"
    
    # Check if we're on a clean working directory
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "Working directory is not clean. Please commit or stash changes first."
        git status --short
        exit 1
    fi
    
    # Check if we're on the main branch
    local current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" && "$current_branch" != "master" ]]; then
        print_warning "You're not on the main branch. Current branch: $current_branch"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Pull latest changes
    print_status "Pulling latest changes..."
    git pull origin "$current_branch"
    
    # Create and checkout new branch
    print_status "Creating release branch..."
    git checkout -b "$branch_name"
    
    # Update version
    update_version "$new_version"
    
    # Commit version bump
    print_status "Committing version bump..."
    git add pyproject.toml mockexchange_gateway/__init__.py
    git commit -m "Bump version to $new_version"
    
    # Push branch
    print_status "Pushing release branch..."
    git push origin "$branch_name"
    
    print_success "Release branch created successfully!"
    print_status "Branch: $branch_name"
    print_status "Version: $new_version"
    echo
    print_status "Next steps:"
    echo "  1. Review the changes: git log --oneline -5"
    echo "  2. Create a pull request to merge into main"
    echo "  3. After merge, tag the release: git tag v$new_version"
    echo "  4. Push the tag: git push origin v$new_version"
    echo "  5. Build and publish: make release && make publish"
}

# Main script
main() {
    local bump_type=$1
    
    if [[ -z "$bump_type" ]]; then
        print_error "Usage: $0 <patch|minor|major>"
        exit 1
    fi
    
    if [[ ! "$bump_type" =~ ^(patch|minor|major)$ ]]; then
        print_error "Invalid bump type. Must be patch, minor, or major"
        exit 1
    fi
    
    print_status "Starting release branch creation..."
    create_release_branch "$bump_type"
}

# Run main function with all arguments
main "$@"
