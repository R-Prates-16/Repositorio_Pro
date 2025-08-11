import os
import requests
from werkzeug.utils import secure_filename
from flask import current_app
from models import GitHubRepo
from app import db

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to prevent conflicts
        import time
        filename = f"{int(time.time())}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Create upload directory if it doesn't exist
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(file_path)
        return f"uploads/{filename}"
    return None

def fetch_github_repos(username):
    """Fetch GitHub repositories for a user"""
    try:
        github_token = os.environ.get("GITHUB_TOKEN", "")
        headers = {}
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        url = f"https://api.github.com/users/{username}/repos"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            repos = response.json()
            
            # Clear existing repos
            GitHubRepo.query.delete()
            
            # Add new repos
            for repo in repos:
                if not repo.get('fork', False):  # Skip forked repos
                    github_repo = GitHubRepo(
                        name=repo['name'],
                        description=repo.get('description', ''),
                        url=repo['html_url'],
                        language=repo.get('language', ''),
                        stars=repo.get('stargazers_count', 0),
                        forks=repo.get('forks_count', 0)
                    )
                    db.session.add(github_repo)
            
            db.session.commit()
            return True, f"Successfully fetched {len([r for r in repos if not r.get('fork', False)])} repositories"
        else:
            return False, f"GitHub API error: {response.status_code}"
    
    except Exception as e:
        return False, f"Error fetching repositories: {str(e)}"

def generate_linkedin_share_url(project, request):
    """Generate LinkedIn share URL for a project"""
    base_url = "https://www.linkedin.com/sharing/share-offsite/"
    project_url = f"{request.url_root}project/{project.id}"
    text = f"Check out this amazing project: {project.title}"
    return f"{base_url}?url={project_url}&title={project.title}&summary={text}"
