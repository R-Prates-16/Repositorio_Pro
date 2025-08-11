from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import Project, Achievement, User, Comment, AboutMe, GitHubRepo
from forms import ProjectForm, AchievementForm, AboutMeForm
from app import db
from utils import save_uploaded_file, fetch_github_repos
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_owner:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    projects_count = Project.query.count()
    achievements_count = Achievement.query.count()
    comments_count = Comment.query.count()
    visitors_count = User.query.filter_by(is_owner=False).count()
    
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         projects_count=projects_count,
                         achievements_count=achievements_count,
                         comments_count=comments_count,
                         visitors_count=visitors_count,
                         recent_projects=recent_projects,
                         recent_comments=recent_comments)

@admin_bp.route('/projects')
@login_required
@admin_required
def projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=projects)

@admin_bp.route('/project/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            content=form.content.data,
            demo_url=form.demo_url.data,
            github_url=form.github_url.data,
            technologies=form.technologies.data,
            category=form.category.data,
            is_published=form.is_published.data,
            is_featured=form.is_featured.data
        )
        
        if form.image.data:
            image_path = save_uploaded_file(form.image.data)
            if image_path:
                project.image_url = image_path
        
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('admin.projects'))
    
    return render_template('admin/project_form.html', form=form, title='New Project')

@admin_bp.route('/project/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.content = form.content.data
        project.demo_url = form.demo_url.data
        project.github_url = form.github_url.data
        project.technologies = form.technologies.data
        project.category = form.category.data
        project.is_published = form.is_published.data
        project.is_featured = form.is_featured.data
        
        if form.image.data:
            image_path = save_uploaded_file(form.image.data)
            if image_path:
                project.image_url = image_path
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin.projects'))
    
    return render_template('admin/project_form.html', form=form, title='Edit Project')

@admin_bp.route('/project/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin.projects'))

@admin_bp.route('/achievements')
@login_required
@admin_required
def achievements():
    achievements = Achievement.query.order_by(Achievement.created_at.desc()).all()
    return render_template('admin/achievements.html', achievements=achievements)

@admin_bp.route('/achievement/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_achievement():
    form = AchievementForm()
    if form.validate_on_submit():
        achievement = Achievement(
            title=form.title.data,
            description=form.description.data,
            date_achieved=form.date_achieved.data,
            category=form.category.data,
            certificate_url=form.certificate_url.data,
            is_published=form.is_published.data
        )
        
        if form.image.data:
            image_path = save_uploaded_file(form.image.data)
            if image_path:
                achievement.image_url = image_path
        
        db.session.add(achievement)
        db.session.commit()
        flash('Achievement created successfully!', 'success')
        return redirect(url_for('admin.achievements'))
    
    return render_template('admin/achievement_form.html', form=form, title='New Achievement')

@admin_bp.route('/achievement/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_achievement(id):
    achievement = Achievement.query.get_or_404(id)
    form = AchievementForm(obj=achievement)
    
    if form.validate_on_submit():
        achievement.title = form.title.data
        achievement.description = form.description.data
        achievement.date_achieved = form.date_achieved.data
        achievement.category = form.category.data
        achievement.certificate_url = form.certificate_url.data
        achievement.is_published = form.is_published.data
        
        if form.image.data:
            image_path = save_uploaded_file(form.image.data)
            if image_path:
                achievement.image_url = image_path
        
        db.session.commit()
        flash('Achievement updated successfully!', 'success')
        return redirect(url_for('admin.achievements'))
    
    return render_template('admin/achievement_form.html', form=form, title='Edit Achievement')

@admin_bp.route('/achievement/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_achievement(id):
    achievement = Achievement.query.get_or_404(id)
    db.session.delete(achievement)
    db.session.commit()
    flash('Achievement deleted successfully!', 'success')
    return redirect(url_for('admin.achievements'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    form = AboutMeForm()
    about_me = AboutMe.query.first()
    
    if form.validate_on_submit():
        if about_me:
            about_me.content = form.content.data
            about_me.skills = form.skills.data
            about_me.experience = form.experience.data
            about_me.education = form.education.data
        else:
            about_me = AboutMe(
                content=form.content.data,
                skills=form.skills.data,
                experience=form.experience.data,
                education=form.education.data
            )
            db.session.add(about_me)
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    if about_me:
        form.content.data = about_me.content
        form.skills.data = about_me.skills
        form.experience.data = about_me.experience
        form.education.data = about_me.education
    
    github_repos = GitHubRepo.query.all()
    
    return render_template('admin/settings.html', form=form, github_repos=github_repos)

@admin_bp.route('/sync-github', methods=['POST'])
@login_required
@admin_required
def sync_github():
    github_username = request.form.get('github_username')
    if not github_username:
        flash('Please provide a GitHub username', 'error')
        return redirect(url_for('admin.settings'))
    
    success, message = fetch_github_repos(github_username)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.settings'))

@admin_bp.route('/toggle-repo/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_repo(id):
    repo = GitHubRepo.query.get_or_404(id)
    repo.is_displayed = not repo.is_displayed
    db.session.commit()
    return jsonify({'success': True, 'is_displayed': repo.is_displayed})
