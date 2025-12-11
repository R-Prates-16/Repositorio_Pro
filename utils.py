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
        # Extract username from URL if full URL is provided
        username = username.strip()
        if 'github.com/' in username:
            # Handle URLs like https://github.com/username or github.com/username
            username = username.rstrip('/').split('github.com/')[-1].split('/')[0]
        
        if not username:
            return False, "Nome de usuário inválido."
        
        github_token = os.environ.get("GITHUB_TOKEN", "")
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Portfolio-App'
        }
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        # First verify the user exists
        user_url = f"https://api.github.com/users/{username}"
        user_response = requests.get(user_url, headers=headers, timeout=10)
        
        if user_response.status_code == 404:
            return False, f"Usuário GitHub '{username}' não encontrado. Verifique o nome de usuário."
        elif user_response.status_code == 403:
            return False, "Limite de requisições da API do GitHub atingido. Tente novamente mais tarde ou adicione um GITHUB_TOKEN."
        elif user_response.status_code != 200:
            return False, f"Erro ao verificar usuário: {user_response.status_code}"
        
        # Fetch repositories
        url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            repos = response.json()
            
            # Clear existing repos
            GitHubRepo.query.delete()
            
            # Add new repos
            count = 0
            for repo in repos:
                if not repo.get('fork', False):  # Skip forked repos
                    github_repo = GitHubRepo(
                        name=repo['name'],
                        description=repo.get('description', '') or '',
                        url=repo['html_url'],
                        language=repo.get('language', '') or '',
                        stars=repo.get('stargazers_count', 0),
                        forks=repo.get('forks_count', 0)
                    )
                    db.session.add(github_repo)
                    count += 1
            
            db.session.commit()
            return True, f"Sincronizados {count} repositórios com sucesso!"
        elif response.status_code == 403:
            return False, "Limite de requisições da API do GitHub atingido. Tente novamente mais tarde."
        else:
            return False, f"Erro da API GitHub: {response.status_code}"
    
    except requests.exceptions.Timeout:
        return False, "Tempo limite excedido ao conectar com o GitHub. Tente novamente."
    except requests.exceptions.ConnectionError:
        return False, "Erro de conexão com o GitHub. Verifique sua conexão com a internet."
    except Exception as e:
        return False, f"Erro ao buscar repositórios: {str(e)}"

def generate_linkedin_share_url(project, request):
    """Generate LinkedIn share URL for a project"""
    base_url = "https://www.linkedin.com/sharing/share-offsite/"
    project_url = f"{request.url_root}project/{project.id}"
    text = f"Check out this amazing project: {project.title}"
    return f"{base_url}?url={project_url}&title={project.title}&summary={text}"
