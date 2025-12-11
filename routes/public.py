from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Project, Achievement, User, Comment, Like, AboutMe, GitHubRepo
from forms import CommentForm
from app import db

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    # Get featured projects
    featured_projects = Project.query.filter_by(is_published=True, is_featured=True).limit(3).all()
    
    # Get recent projects
    recent_projects = Project.query.filter_by(is_published=True).order_by(Project.created_at.desc()).limit(6).all()
    
    # Get popular projects (most liked)
    popular_projects = Project.query.filter_by(is_published=True).order_by(Project.id.desc()).limit(3).all()
    
    # Get recent achievements
    recent_achievements = Achievement.query.filter_by(is_published=True).order_by(Achievement.created_at.desc()).limit(3).all()
    
    # Get owner for social links
    owner = User.query.filter_by(is_owner=True).first()
    
    project_count = Project.query.filter_by(is_published=True).count()
    achievement_count = Achievement.query.filter_by(is_published=True).count()
    
    return render_template('index.html',
                         featured_projects=featured_projects,
                         recent_projects=recent_projects,
                         popular_projects=popular_projects,
                         recent_achievements=recent_achievements,
                         owner=owner,
                         project_count=project_count if project_count > 0 else 7,
                         achievement_count=achievement_count if achievement_count > 0 else 8)

@public_bp.route('/projects')
def projects():
    category = request.args.get('category')
    
    query = Project.query.filter_by(is_published=True)
    if category:
        query = query.filter_by(category=category)
    
    projects = query.order_by(Project.created_at.desc()).all()
    
    # Get all categories for filter
    categories = db.session.query(Project.category).filter_by(is_published=True).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    # Get liked project IDs for current user
    liked_project_ids = set()
    if current_user.is_authenticated:
        user_likes = Like.query.filter_by(user_id=current_user.id).all()
        liked_project_ids = {like.project_id for like in user_likes}
    
    return render_template('projects.html', projects=projects, categories=categories, selected_category=category, liked_project_ids=liked_project_ids)

@public_bp.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.filter_by(id=id, is_published=True).first_or_404()
    
    # Check if current user has liked this project
    user_liked = False
    if current_user.is_authenticated:
        user_liked = Like.query.filter_by(user_id=current_user.id, project_id=project.id).first() is not None
    
    # Get comments
    comments = Comment.query.filter_by(project_id=project.id).order_by(Comment.created_at.desc()).all()
    
    form = CommentForm()
    
    return render_template('project_detail.html', 
                         project=project, 
                         comments=comments, 
                         form=form,
                         user_liked=user_liked)

@public_bp.route('/project/<int:id>/like', methods=['POST'])
def toggle_like(id):
    if not current_user.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'login_required',
            'message': 'Por favor, faça login para curtir.'
        }), 401
    
    project = Project.query.get_or_404(id)
    
    try:
        like = Like.query.filter_by(user_id=current_user.id, project_id=project.id).first()
        
        if like:
            db.session.delete(like)
            liked = False
        else:
            like = Like(user_id=current_user.id, project_id=project.id)
            db.session.add(like)
            liked = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'liked': liked,
            'like_count': project.like_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'server_error',
            'message': 'Erro ao processar curtida.'
        }), 500

@public_bp.route('/project/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    project = Project.query.get_or_404(id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            project_id=project.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comentário adicionado com sucesso!', 'success')
    else:
        flash('Erro ao adicionar comentário. Por favor, tente novamente.', 'error')
    
    return redirect(url_for('public.project_detail', id=id))

@public_bp.route('/achievements')
def achievements():
    category = request.args.get('category')
    
    query = Achievement.query.filter_by(is_published=True)
    if category:
        query = query.filter_by(category=category)
    
    achievements = query.order_by(Achievement.date_achieved.desc()).all()
    
    # Get all categories for filter
    categories = db.session.query(Achievement.category).filter_by(is_published=True).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('achievements.html', achievements=achievements, categories=categories, selected_category=category)

@public_bp.route('/about')
def about():
    about_me = AboutMe.query.first()
    github_repos = GitHubRepo.query.filter_by(is_displayed=True).order_by(GitHubRepo.stars.desc()).all()
    owner = User.query.filter_by(is_owner=True).first()
    
    return render_template('about.html', about_me=about_me, github_repos=github_repos, owner=owner)

@public_bp.route('/contact')
def contact():
    owner = User.query.filter_by(is_owner=True).first()
    return render_template('contact.html', owner=owner)
