#!/bin/bash
# GitHub Pages Deployment Script
#
# This script helps you deploy your NANSC Intelligent Operations Console
# to GitHub Pages as a static site for portfolio/demo purposes.
#
# Usage:
#   ./scripts/deploy_github_pages.sh --repo yourusername/nansc-console

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
REPO=""
BRANCH="main"
FOLDER="."

# Function to print colored output
print_info() {
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

# Function to show usage
show_usage() {
    echo "GitHub Pages Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --repo REPO    GitHub repository (e.g., yourusername/nansc-console)"
    echo "  --branch BRANCH  Git branch to deploy to (default: main)"
    echo "  --folder FOLDER  Folder to deploy (default: .)"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --repo yourusername/nansc-console"
    echo "  $0 --repo yourusername/nansc-console --branch gh-pages"
    echo "  $0 --repo yourusername/nansc-console --folder docs"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo)
            REPO="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --folder)
            FOLDER="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$REPO" ]; then
    print_error "Repository name is required."
    echo ""
    show_usage
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "Not in a git repository. Please run this script from your project root."
    exit 1
fi

# Function to create GitHub Pages files
create_github_pages_files() {
    print_info "Creating GitHub Pages files..."

    # Create index.html
    cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NANSC Intelligent Operations Console</title>
    <style>
        :root {
            --primary: #667eea;
            --primary-dark: #5568d3;
            --secondary: #764ba2;
            --light: #f8f9fa;
            --dark: #333;
            --muted: #6c757d;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--dark);
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .title {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 1.2rem;
            color: var(--muted);
            margin-bottom: 30px;
        }

        .info-box {
            background: var(--light);
            border-left: 4px solid var(--primary);
            padding: 20px;
            margin: 30px 0;
            border-radius: 8px;
        }

        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .feature-card {
            background: #fff;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }

        .feature-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 10px;
        }

        .feature-description {
            color: var(--dark);
            margin-bottom: 15px;
        }

        .badges {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
        }

        .badge {
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }

        .buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin: 20px 0;
        }

        .btn {
            background: var(--primary);
            color: white;
            padding: 14px 30px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            font-weight: 600;
            font-size: 1rem;
            transition: background 0.3s ease, transform 0.2s ease;
            cursor: pointer;
        }

        .btn:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }

        .btn-secondary {
            background: #6c757d;
        }

        .btn-secondary:hover {
            background: #5a6268;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .stat-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 10px;
        }

        .stat-label {
            color: var(--muted);
            font-size: 0.9rem;
        }

        .contact {
            text-align: center;
            padding: 30px 0;
            color: var(--muted);
        }

        .footer {
            text-align: center;
            padding: 20px 0;
            color: var(--muted);
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .title {
                font-size: 2rem;
            }

            .subtitle {
                font-size: 1rem;
            }

            .card {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card header">
            <h1 class="title">📡 NANSC Intelligent Operations Console</h1>
            <p class="subtitle">AI-Powered Civil Aviation Telecommunications Assistant for Operations and Training</p>

            <div class="buttons">
                <a href="https://huggingface.co/spaces/yourusername/nansc-console" class="btn" target="_blank">🔗 Open Live Demo</a>
                <a href="https://github.com/yourusername/nansc-console" class="btn btn-secondary" target="_blank">📁 View Source Code</a>
            </div>
        </div>

        <div class="card">
            <div class="info-box">
                <h3>🚀 About This Project</h3>
                <p><strong>Civil aviation telecommunications operators face critical challenges in their day-to-day operations:</strong></p>
                <ul style="margin: 10px 0 0 20px;">
                    <li>Time-consuming manual ICAO airport code lookups</li>
                    <li>Complex AFTN to AMHS address conversions</li>
                    <li>Buried procedures in lengthy documents and manuals</li>
                    <li>No centralized AI-powered assistant</li>
                </ul>
                <p style="margin-top: 15px;"><strong>Our Solution:</strong> An AI-powered operations console that automates these tasks, providing instant access to airport information, seamless address conversions, and intelligent document search.</p>
            </div>

            <div class="features">
                <div class="feature-card">
                    <h3 class="feature-title">🤖 Multi-Agent Orchestration</h3>
                    <p class="feature-description">Intelligent coordination of multiple specialized tools for civil aviation telecommunications operations.</p>
                    <div class="badges">
                        <span class="badge">AI Agent</span>
                        <span class="badge">Google Gemini</span>
                        <span class="badge">Tool Calling</span>
                        <span class="badge">Async Processing</span>
                    </div>
                </div>

                <div class="feature-card">
                    <h3 class="feature-title">🛠️ Specialized Tools</h3>
                    <p class="feature-description">ICAO airport lookup, AFTN-to-AMHS conversion, and web search integration for enhanced capabilities.</p>
                    <div class="badges">
                        <span class="badge">ICAO Lookup</span>
                        <span class="badge">AFTN Converter</span>
                        <span class="badge">Web Search</span>
                        <span class="badge">Real-time</span>
                    </div>
                </div>

                <div class="feature-card">
                    <h3 class="feature-title">📚 Retrieval Augmented Generation</h3>
                    <p class="feature-description">Document processing and intelligent search through procedures and manuals using RAG technology.</p>
                    <div class="badges">
                        <span class="badge">RAG</span>
                        <span class="badge">ChromaDB</span>
                        <span class="badge">Document AI</span>
                        <span class="badge">Vector Search</span>
                    </div>
                </div>

                <div class="feature-card">
                    <h3 class="feature-title">📊 Enterprise Features</h3>
                    <p class="feature-description">Professional-grade observability, session management, and batch processing capabilities.</p>
                    <div class="badges">
                        <span class="badge">Telemetry</span>
                        <span class="badge">Session Mgmt</span>
                        <span class="badge">Batch Processing</span>
                        <span class="badge">Health Monitoring</span>
                    </div>
                </div>
            </div>

            <div class="info-box">
                <h3>📋 Competition Features</h3>
                <ul style="margin: 10px 0 0 20px;">
                    <li>✅ Multi-agent orchestration with custom tools</li>
                    <li>✅ Retrieval Augmented Generation (RAG) implementation</li>
                    <li>✅ Session management and observability</li>
                    <li>✅ Async processing and error handling</li>
                    <li>✅ Professional documentation and architecture</li>
                    <li>✅ Google Gemini integration</li>
                </ul>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Free Hosting</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">4</div>
                    <div class="stat-label">Architecture Layers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">6</div>
                    <div class="stat-label">Core Features</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">⭐⭐⭐⭐⭐</div>
                    <div class="stat-label">Production Quality</div>
                </div>
            </div>

            <div class="info-box">
                <h3>🔧 Technical Stack</h3>
                <p><strong>AI & Frameworks:</strong> Google Gemini 2.5 Flash, LangChain, ChromaDB</p>
                <p><strong>Interface:</strong> Gradio, HTML/CSS</p>
                <p><strong>Architecture:</strong> 4-Layer Enterprise Design</p>
                <p><strong>Deployment:</strong> Hugging Face Spaces (Free)</p>
            </div>

            <div class="info-box">
                <h3>🎯 Use Cases</h3>
                <p><strong>For Aviation Telecommunications:</strong> ICAO code lookups, AFTN/AMHS conversions, procedure references</p>
                <p><strong>For Training:</strong> Interactive learning tool for telecommunications operations</p>
                <p><strong>For Operations:</strong> Real-time assistance for message switching and navigation services</p>
            </div>
        </div>

        <div class="contact">
            <p><strong>📧 Contact:</strong> Sameh Shehata Abdelaziz</p>
            <p><strong>📁 Repository:</strong> <a href="https://github.com/yourusername/nansc-console" target="_blank">github.com/yourusername/nansc-console</a></p>
        </div>

        <div class="footer">
            <p>© 2025 NANSC Intelligent Operations Console. Built with Google Gemini, LangChain, ChromaDB, and Gradio.</p>
        </div>
    </div>

    <script>
        // Simple animations
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.feature-card');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            });

            cards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(card);
            });
        });
    </script>
</body>
</html>
EOF

    # Create CNAME file (optional)
    if [ -n "$CNAME" ]; then
        echo "$CNAME" > CNAME
        print_info "Created CNAME file for custom domain: $CNAME"
    fi

    print_success "GitHub Pages files created successfully!"
}

# Function to deploy to GitHub Pages
deploy_to_github_pages() {
    print_info "Deploying to GitHub Pages..."

    # Check if repository exists
    if ! git ls-remote --exit-code "$REPO" &> /dev/null; then
        print_warning "Repository '$REPO' does not exist or is not accessible."
        print_info "Please create the repository on GitHub first, then try again."
        print_info "You can create it at: https://github.com/$REPO"
        exit 1
    fi

    # Create a temporary directory for the deployment
    TEMP_DIR=$(mktemp -d)
    print_info "Created temporary directory: $TEMP_DIR"

    # Clone the repository
    print_info "Cloning repository..."
    git clone "https://github.com/$REPO.git" "$TEMP_DIR"

    # Copy files to the repository
    print_info "Copying files..."
    cd "$TEMP_DIR"

    # Remove existing files (if any)
    rm -rf *.html *.css *.js *.md CNAME 2>/dev/null || true

    # Copy our files
    cp "$OLDPWD/index.html" .
    if [ -f "$OLDPWD/CNAME" ]; then
        cp "$OLDPWD/CNAME" .
    fi

    # Initialize git if needed
    if [ ! -d ".git" ]; then
        git init
        git remote add origin "https://github.com/$REPO.git"
    fi

    # Add files and commit
    git add .
    git config user.name "NANSC Deploy Bot"
    git config user.email "noreply@example.com"
    git commit -m "Deploy to GitHub Pages

- Update NANSC Console demo page
- Add responsive design and animations
- Improve accessibility and SEO

Deployed via deploy_github_pages.sh script"

    # Push to GitHub Pages branch
    print_info "Pushing to GitHub..."
    git push origin HEAD:"$BRANCH" --force

    print_success "Successfully deployed to GitHub Pages!"
    print_info "Your site will be available at: https://$REPO.github.io"

    # Clean up
    cd "$OLDPWD"
    rm -rf "$TEMP_DIR"
}

# Function to show next steps
show_next_steps() {
    echo ""
    echo "🎉 Deployment Complete!"
    echo ""
    echo "Next Steps:"
    echo "1. Visit your GitHub repository: https://github.com/$REPO"
    echo "2. Go to Settings > Pages"
    echo "3. Select 'Deploy from a branch'"
    echo "4. Choose '$BRANCH' branch and '/' folder"
    echo "5. Click 'Save'"
    echo ""
    echo "Your site will be live at: https://$REPO.github.io"
    echo ""
    echo "Note: It may take a few minutes for GitHub Pages to activate."
}

# Main execution
main() {
    echo "🌐 GitHub Pages Deployment Script"
    echo "=================================="
    echo ""

    print_info "Repository: $REPO"
    print_info "Branch: $BRANCH"
    print_info "Folder: $FOLDER"
    echo ""

    # Create GitHub Pages files
    create_github_pages_files

    # Deploy
    deploy_to_github_pages

    # Show next steps
    show_next_steps
}

# Run main function
main