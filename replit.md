# Overview

This is a Flask-based digital portfolio system that allows users to showcase their projects, achievements, and professional information. The application features a complete content management system with separate admin and public interfaces, user authentication, social features like likes and comments, and GitHub integration for automatically importing repositories.

The system is designed as a personal portfolio platform where the portfolio owner can manage content through an admin dashboard while visitors can browse projects, interact through likes and comments, and register for accounts to participate in the community.

# User Preferences

Preferred communication style: Simple, everyday language.
Design preferences: Professional and technical appearance with modern UX/UI standards.
Data policy: Only use authentic data, never add synthetic/mock projects or content.

# System Architecture

## Backend Framework
- **Flask**: Python web framework chosen for its simplicity and flexibility
- **SQLAlchemy**: ORM for database operations with declarative base model structure
- **Flask-Login**: Session management and user authentication
- **Flask-WTF**: Form handling and CSRF protection
- **Werkzeug**: File upload handling and password security

## Database Design
- **SQLite/PostgreSQL**: Flexible database configuration supporting both development (SQLite) and production (PostgreSQL) environments
- **Models**: User, Project, Achievement, Comment, Like, AboutMe, GitHubRepo
- **Relationships**: Proper foreign key relationships with cascade deletions for data integrity
- **User Management**: Role-based access with portfolio owner privileges

## Frontend Architecture
- **Server-side Rendering**: Jinja2 templates for dynamic HTML generation
- **Bootstrap**: Dark theme CSS framework for responsive design
- **Material Design Icons**: Consistent iconography throughout the interface
- **Progressive Enhancement**: JavaScript for interactive features like AJAX likes and form validation

## Authentication System
- **Password Hashing**: Werkzeug's secure password hashing
- **Session Management**: Flask-Login for user session handling
- **Role-based Access**: Admin decorator for restricting owner-only functionality
- **User Registration**: Complete signup flow with validation

## File Management
- **Upload System**: Secure file handling with type validation and unique naming
- **Static Files**: Organized structure for uploads, CSS, and JavaScript
- **Image Processing**: Basic image upload support for projects and profiles

## Application Structure
- **Blueprint Architecture**: Modular route organization (auth, admin, public)
- **Form Validation**: WTForms integration for server-side validation
- **Error Handling**: Flash message system for user feedback
- **Utility Functions**: Helper functions for file handling and GitHub integration

## Security Features
- **CSRF Protection**: Built into all forms via Flask-WTF
- **File Upload Security**: Filename sanitization and type checking
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- **Session Security**: Configurable secret key for session encryption

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and connection management
- **Flask-Login**: User session and authentication management
- **Flask-WTF & WTForms**: Form handling and validation
- **Werkzeug**: WSGI utilities and security functions

## Frontend Dependencies
- **Bootstrap**: CSS framework with dark theme support
- **Material Design Icons**: Icon library for UI consistency
- **JavaScript**: Vanilla JS for interactive features and AJAX requests

## Development Tools
- **Python Logging**: Application logging and debugging support
- **ProxyFix**: WSGI middleware for deployment behind reverse proxies

## Database Support
- **SQLite**: Development database (default)
- **PostgreSQL**: Production database support via DATABASE_URL environment variable
- **Connection Pooling**: SQLAlchemy engine options for connection management

## External API Integrations
- **GitHub API**: Repository fetching functionality for portfolio integration
- **LinkedIn Sharing**: Client-side integration for project sharing

## File Handling
- **File Upload**: Image and document upload support
- **Static File Serving**: Flask static file handling for uploads and assets

## Environment Configuration
- **Environment Variables**: DATABASE_URL, SESSION_SECRET, GITHUB_TOKEN
- **Flexible Configuration**: Development and production environment support
- **Upload Directory**: Configurable file storage location