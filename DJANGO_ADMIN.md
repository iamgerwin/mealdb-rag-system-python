# Django Admin Interface Documentation

## Overview
This document provides comprehensive instructions for setting up and using the Django admin interface for the MealDB RAG System. The admin interface provides a web-based management console for configuration, data management, and system monitoring.

## Prerequisites
- Python 3.10+ installed
- Virtual environment activated
- All requirements installed (`pip install -r requirements.txt`)

## Initial Setup

### 1. Database Setup
First, create the database schema:
```bash
python manage.py migrate
```

### 2. Create Admin User
Create a superuser account to access the admin interface:
```bash
python manage.py createsuperuser
```
Follow the prompts to set username, email, and password.

For development/testing, you can use:
- Username: `admin`
- Email: `admin@example.com`
- Password: `admin123`

### 3. Import Existing Data
If you have existing data from the CLI tools:
```bash
# Import from cache
python manage.py import_meals --from-cache

# Or fetch fresh data from API
python manage.py import_meals
```

### 4. Start the Development Server
```bash
python manage.py runserver
```
The admin interface will be available at: http://127.0.0.1:8000/admin

## Admin Modules

### Configuration Management
**Path:** Admin → Configurations

Manage system-wide settings:
- Cache expiry times
- Default model configurations
- System behavior flags

**Fields:**
- `name`: Configuration key
- `value`: Configuration value (can be JSON)
- `description`: Explanation of the setting
- `is_active`: Enable/disable without deletion

### API Configuration
**Path:** Admin → API Configurations

Securely manage API credentials and quotas:

**Features:**
- Masked API key display for security
- Multiple provider support (OpenAI, Anthropic, Google, TheMealDB)
- Quota tracking and monitoring
- Visual quota status indicators

**Supported Providers:**
- OpenAI
- Anthropic
- Google
- TheMealDB

### Meals Database
**Path:** Admin → Meals

Browse and manage meal data:

**Features:**
- Search by name, instructions, or tags
- Filter by category, area, or index status
- Inline ingredient editing
- Thumbnail preview in list and detail views
- Bulk actions for indexing status

**Available Actions:**
- Mark selected meals as indexed
- Mark selected meals as not indexed
- View/edit individual meal details

### Ingredients
**Path:** Admin → Ingredients (or inline within Meals)

Manage meal ingredients:
- Linked to specific meals
- Includes measurements
- Ordered for proper display

### Search Analytics
**Path:** Admin → Search Queries

Monitor system usage:

**Features:**
- Track all search queries
- View response times
- Monitor which model was used
- See result counts
- Date-based filtering

**Insights Available:**
- Most common queries
- Performance metrics
- Model usage patterns
- Search effectiveness

### Search Results
**Path:** Admin → Search Results (or inline within Search Queries)

Detailed result tracking:
- Links queries to specific meals
- Shows relevance scores
- Tracks result positions

### Cache Management
**Path:** Admin → Cache Entries

Monitor and manage cache:

**Features:**
- View all cached entries
- Check expiration status
- Monitor hit counts
- Clear expired entries

**Actions:**
- Clear expired cache entries
- View cache statistics
- Manual cache invalidation

### Indexing Tasks
**Path:** Admin → Indexing Tasks

Track data import and indexing operations:

**Features:**
- Real-time progress tracking
- Visual progress bars
- Status indicators (pending, running, completed, failed)
- Error logging
- Historical task tracking

**Information Displayed:**
- Task status with color coding
- Progress percentage
- Start and completion times
- Error messages if failed

## Common Operations

### Adding API Keys
1. Navigate to Admin → API Configurations
2. Click "Add API Configuration"
3. Select provider
4. Enter API key
5. Set quota limits (optional)
6. Save

### Importing New Meals
1. Run the import command: `python manage.py import_meals`
2. Monitor progress in Admin → Indexing Tasks
3. Check imported meals in Admin → Meals

### Monitoring System Performance
1. Check Admin → Search Queries for usage patterns
2. Review Admin → Cache Entries for cache efficiency
3. Monitor Admin → Indexing Tasks for import health

### Clearing Cache
1. Navigate to Admin → Cache Entries
2. Select entries to clear (or use filters)
3. Choose "Clear expired cache entries" from actions
4. Click "Go"

## Security Best Practices

1. **Production Deployment:**
   - Use strong passwords for admin accounts
   - Enable HTTPS in production
   - Set `DEBUG = False` in production settings
   - Use environment variables for sensitive data

2. **API Key Management:**
   - Never commit API keys to version control
   - Rotate keys regularly
   - Monitor quota usage
   - Use the admin interface for key management

3. **Access Control:**
   - Limit admin access to authorized personnel
   - Use Django's built-in permission system
   - Regularly audit user accounts

## Troubleshooting

### Cannot Access Admin Interface
- Ensure server is running: `python manage.py runserver`
- Check if migrations are applied: `python manage.py migrate`
- Verify superuser exists: `python manage.py createsuperuser`

### Import Fails
- Check data/meals.json exists for cache import
- Verify API keys are configured in Admin → API Configurations
- Check Admin → Indexing Tasks for error messages

### Search Not Working
- Ensure meals are imported and indexed
- Check that FTS5 is available in SQLite
- Verify meals have `is_indexed = True`

## Advanced Configuration

### Custom Settings
Edit `mealdb_admin/settings.py` for:
- Database configuration
- Static file settings
- Allowed hosts
- Additional Django apps

### Extending the Admin
To add custom functionality:
1. Edit `meals/admin.py` for admin customizations
2. Add new models in `meals/models.py`
3. Run `python manage.py makemigrations` and `migrate`

### Production Deployment
For production deployment:
1. Set up a proper database (PostgreSQL recommended)
2. Configure static file serving
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Set up reverse proxy (Nginx, Apache)
5. Enable HTTPS with SSL certificates

## Support

For issues or questions:
1. Check the main README.md for general information
2. Review Django's official documentation
3. Check the project's issue tracker
4. Ensure all dependencies are correctly installed