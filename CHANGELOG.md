# Changelog

All notable changes to My Recipe Box will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v2.0.0
- Enhanced frontend user interface
- Improved user experience
- Advanced styling and responsive design
- Additional frontend features

## [1.2.0] - 2024-11-01

### Added
- CSS styling for index, login, and signup pages
- About Us page
- Forgot password link on login page
- Enhanced UI components

### Changed
- Improved visual design and user interface
- Better form styling and layout

## [1.1.0] - 2024-10-30

### Added
- Search results display with editable text boxes
- Session management functionality
- User authentication improvements

### Fixed
- Search functionality improvements
- Session handling fixes

## [1.0.0] - 2024-10-28 🎉 **Backend Complete**

### Added
- **Complete Backend API Functionality**
- User registration and authentication system
- Recipe CRUD operations (Create, Read, Update, Delete)
- Search functionality by ingredients and category
- User login and session management
- Recipe categorization with enum support
- Random recipe selection feature
- Recipe duplication functionality
- Database models for Users, Recipes, and Favorites
- SQLite database integration with proper schema
- Password security with Werkzeug
- Comprehensive error handling
- Unit tests for user and recipe operations

### Backend Features Complete
- ✅ User Management (Register, Login, Authentication)
- ✅ Recipe Management (CRUD Operations)
- ✅ Search and Filter Recipes
- ✅ Category Management
- ✅ Database Schema and Operations
- ✅ API Endpoints
- ✅ Session Management
- ✅ Security Implementation
- **Recipe categories** with enum validation
- **User favorites system** (backend service)
- **Comprehensive test suite** for user and recipe operations

### Security
- Password hashing with Werkzeug
- Session-based authentication
- Input validation and sanitization
- SQL injection protection via SQLAlchemy ORM

## [0.9.0] - 2024-10-30

### Added
- CSS styling for main pages (index, login, signup)
- Search results display with editable interface
- Session persistence across page requests

### Changed
- Improved user interface design
- Enhanced search result presentation

### Fixed
- Search functionality improvements
- Template rendering issues

## [0.8.0] - 2024-10-28

### Added
- **Complete user authentication flow**
- Login and signup HTML templates
- Search functionality with results page
- Recipe display and update capabilities

### Changed
- Major UI/UX improvements with proper templates
- Enhanced recipe management interface

### Fixed
- Template routing and rendering
- Form submission handling

## [0.7.0] - 2024-10-25

### Added
- **Random recipe feature** with dedicated endpoint
- Recipe categories with enum validation
- Enhanced search by ingredients and category
- Comprehensive database population script

### Changed
- Reorganized random recipe functionality
- Improved category management system
- Updated table creation script

### Fixed
- Import issues in random recipe module
- Database schema consistency
- Category validation logic

## [0.6.0] - 2024-10-22

### Added
- **Recipe duplicate functionality** - create copies of existing recipes
- **User login system** with proper authentication
- Recipe update capabilities
- Enhanced database schema

### Changed
- Updated Werkzeug dependency to 3.0.0
- Improved recipe management workflow
- Enhanced user authentication flow

### Fixed
- Database initialization issues
- Recipe update logic
- Authentication handling

## [0.5.0] - 2024-10-20

### Added
- **Search functionality** by ingredients
- **Recipe categories** with proper validation
- Login route and authentication logic
- Random recipe generator with test coverage

### Changed
- Updated table creation script for categories
- Enhanced search capabilities with query parameters
- Improved database schema design

### Fixed
- Search query parameter handling
- Category validation logic
- Test file organization

## [0.4.0] - 2024-10-18

### Added
- **Comprehensive user management** system
- **Recipe management** with CRUD operations
- User authentication and account creation
- Recipe name uniqueness validation
- Database relationship management

### Changed
- Merged user update/delete functionality into main user service
- Merged recipe update/delete functionality into main recipe service
- Enhanced error handling and user feedback

### Fixed
- Recipe creation and validation logic
- User account management
- Database relationship integrity

## [0.3.0] - 2024-10-15

### Added
- **User authentication system**
- User registration and login functionality
- **Favorite recipes service** (backend)
- Password management system
- User account lifecycle management

### Changed
- Enhanced database schema with user relationships
- Improved error handling throughout application
- Better separation of concerns in services

### Fixed
- Database connection issues
- User authentication flow
- Password security implementation

## [0.2.0] - 2024-10-12

### Added
- **Flask application structure** with proper routing
- **Database models** for Users, Recipes, and Favorites
- **SQLite database integration**
- Initial CRUD operations for recipes and users
- Database table creation scripts

### Changed
- Reorganized project structure for better maintainability
- Improved database schema design
- Enhanced error handling

### Fixed
- Database initialization issues
- Model relationship definitions
- Route configuration

## [0.1.0] - 2024-10-10

### Added
- **Initial project setup** with Git repository
- Basic Python scripts for proof of concept
- Hello World implementation for testing
- Initial project structure
- Basic database setup exploration

### Infrastructure
- Git repository initialization
- Initial commit and branch structure
- Development environment setup

---

## Version History Summary

- **v1.0.0**: Full-featured recipe management web application
- **v0.9.0**: UI/UX improvements and session management
- **v0.8.0**: Complete authentication system and templates
- **v0.7.0**: Random recipes and category system
- **v0.6.0**: Recipe duplication and user login
- **v0.5.0**: Search functionality and recipe categories
- **v0.4.0**: Complete CRUD operations
- **v0.3.0**: User authentication system
- **v0.2.0**: Flask app structure and database models
- **v0.1.0**: Initial project setup

## Contributors

- Christie Desnoyer (cdesn2@uis.edu)
- Thuy Weston (tnguy304@uis.edu)