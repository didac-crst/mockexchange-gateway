#!/bin/bash

# MockX Gateway Release Script
# This script helps create a new release with proper versioning and tagging

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

# Function to get current version
get_current_version() {
    poetry version -s
}

# Function to bump version
bump_version() {
    local bump_type=$1
    local current_version=$(get_current_version)
    
    print_status "Current version: $current_version"
    
    case $bump_type in
        patch)
            poetry version patch
            ;;
        minor)
            poetry version minor
            ;;
        major)
            poetry version major
            ;;
        *)
            print_error "Invalid bump type. Use: patch, minor, or major"
            exit 1
            ;;
    esac
    
    local new_version=$(get_current_version)
    print_success "Version bumped to: $new_version"
    echo $new_version
}

# Function to run quality checks
run_quality_checks() {
    print_status "Running quality checks..."
    
    # Run tests
    print_status "Running tests..."
    make test
    
    # Run linting
    print_status "Running linting..."
    make lint
    
    # Run type checking
    print_status "Running type checking..."
    make type-check
    
    # Run formatting
    print_status "Running formatting..."
    make format
    
    # Build package
    print_status "Building package..."
    make build-poetry
    
    print_success "All quality checks passed!"
}

# Function to create git tag
create_tag() {
    local version=$1
    local tag="v$version"
    
    print_status "Creating git tag: $tag"
    
    # Check if tag already exists
    if git tag -l | grep -q "^$tag$"; then
        print_error "Tag $tag already exists!"
        exit 1
    fi
    
    # Create and push tag
    git tag -a "$tag" -m "Release $tag"
    git push origin "$tag"
    
    print_success "Tag $tag created and pushed!"
}

# Function to update changelog
update_changelog() {
    local version=$1
    
    print_status "Updating CHANGELOG.md..."
    
    # Check if CHANGELOG.md exists
    if [ ! -f "CHANGELOG.md" ]; then
        print_error "CHANGELOG.md not found!"
        exit 1
    fi
    
    # Create temporary file
    temp_file=$(mktemp)
    
    # Add new version section at the top
    cat > "$temp_file" << EOF
## [Unreleased]

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 

---

EOF
    
    # Append existing content
    cat CHANGELOG.md >> "$temp_file"
    
    # Replace original file
    mv "$temp_file" CHANGELOG.md
    
    print_success "CHANGELOG.md updated with new [Unreleased] section"
}

# Function to show help
show_help() {
    echo "MockX Gateway Release Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE     Bump type: patch, minor, major (default: patch)"
    echo "  -c, --check-only    Only run quality checks, don't create release"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --type patch     Create a patch release (0.1.0 -> 0.1.1)"
    echo "  $0 --type minor     Create a minor release (0.1.0 -> 0.2.0)"
    echo "  $0 --type major     Create a major release (0.1.0 -> 1.0.0)"
    echo "  $0 --check-only     Only run quality checks"
    echo ""
}

# Main script
main() {
    local bump_type="patch"
    local check_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                bump_type="$2"
                shift 2
                ;;
            -c|--check-only)
                check_only=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_status "Starting MockX Gateway release process..."
    
    # Check if we're on main branch
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        print_warning "You're not on the main branch (current: $current_branch)"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Release cancelled"
            exit 1
        fi
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        print_error "You have uncommitted changes. Please commit or stash them first."
        git status --short
        exit 1
    fi
    
    # Run quality checks
    run_quality_checks
    
    if [ "$check_only" = true ]; then
        print_success "Quality checks completed successfully!"
        exit 0
    fi
    
    # Bump version
    new_version=$(bump_version "$bump_type")
    
    # Update changelog
    update_changelog "$new_version"
    
    # Commit changes
    print_status "Committing version bump..."
    git add pyproject.toml CHANGELOG.md
    git commit -m "chore: bump version to $new_version"
    
    # Create and push tag
    create_tag "$new_version"
    
    # Push changes
    print_status "Pushing changes to main branch..."
    git push origin main
    
    print_success "Release $new_version created successfully!"
    print_status "Next steps:"
    echo "  1. Review the draft release on GitHub"
    echo "  2. Edit the release notes if needed"
    echo "  3. Publish the release"
    echo "  4. Consider publishing to PyPI: make publish-poetry"
}

# Run main function with all arguments
main "$@"
