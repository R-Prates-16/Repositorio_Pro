import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
from forms import LoginForm, RegisterForm, ProfileForm
from app import db
from utils import save_uploaded_file

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if user.is_owner:
                return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
            return redirect(next_page) if next_page else redirect(url_for('public.index'))
        else:
            flash('Usuário ou senha inválidos', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Check if username or email already exists
            if User.query.filter_by(username=form.username.data).first():
                flash('Nome de usuário já existe', 'error')
                return render_template('auth/register.html', form=form)
            
            if User.query.filter_by(email=form.email.data).first():
                flash('Email já cadastrado', 'error')
                return render_template('auth/register.html', form=form)
            
            password = form.password.data
            if not password:
                flash('Senha é obrigatória', 'error')
                return render_template('auth/register.html', form=form)
            
            user = User(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data,
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash('Cadastro realizado com sucesso! Bem-vindo ao portfólio.', 'success')
            return redirect(url_for('public.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao cadastrar usuário: {str(e)}")
            flash('Erro ao criar conta. Por favor, tente novamente.', 'error')
            return render_template('auth/register.html', form=form)
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('public.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        current_user.linkedin_url = form.linkedin_url.data
        current_user.github_url = form.github_url.data
        
        if form.profile_image.data:
            image_path = save_uploaded_file(form.profile_image.data)
            if image_path:
                current_user.profile_image = image_path
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.profile'))
    
    # Pre-populate form with current user data
    form.full_name.data = current_user.full_name
    form.bio.data = current_user.bio
    form.linkedin_url.data = current_user.linkedin_url
    form.github_url.data = current_user.github_url
    
    return render_template('auth/profile.html', form=form)
