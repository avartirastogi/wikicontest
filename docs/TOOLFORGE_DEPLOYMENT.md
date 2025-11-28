# WikiContest Toolforge Deployment Guide

This guide will help you deploy the WikiContest Flask application to Wikimedia Toolforge.

## 🚀 **Prerequisites**

- A Toolforge account
- SSH access to Toolforge
- Basic knowledge of Python and Flask

## 📋 **Step-by-Step Deployment**

### **Step 1: Create Your Tool Account**

1. Follow the [Toolforge quickstart guide](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Quickstart) to create your tool
2. SSH into Toolforge: `ssh <your-username>@login.toolforge.org`
3. Switch to your tool user: `become wikicontest`

### **Step 2: Prepare Your Application**

1. **Run the deployment script:**
   ```bash
   cd backend
   chmod +x deploy_to_toolforge.sh
   ./deploy_to_toolforge.sh
   ```

2. **Or manually create the structure:**
   ```bash
   mkdir -p $HOME/www/python/src
   mkdir -p $HOME/www/python/src/templates
   mkdir -p $HOME/www/python/src/static
   mkdir -p $HOME/www/python/src/models
   mkdir -p $HOME/www/python/src/routes
   mkdir -p $HOME/www/python/src/middleware
   ```

### **Step 3: Set Up Virtual Environment**

1. **Start Kubernetes shell:**
   ```bash
   webservice python3.13 shell
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv $HOME/www/python/venv
   source $HOME/www/python/venv/bin/activate
   pip install --upgrade pip
   ```

3. **Install dependencies:**
   ```bash
   pip install -r $HOME/www/python/src/requirements.txt
   ```

4. **Exit Kubernetes shell:**
   ```bash
   exit
   ```

### **Step 4: Configure OAuth**

1. **Register OAuth consumer:**
   - Go to: https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration
   - **Callback URL:** `https://wikicontest.toolforge.org/oauth-callback`
   - **Contact email:** Your Wikimedia account email
   - **Grant settings:** Request authorization for specific permissions (Basic rights)

2. **Update configuration:**
   ```bash
   # Generate secret keys
   python3 -c "import secrets; print('SECRET_KEY = \"' + secrets.token_urlsafe(48) + '\"')"
   python3 -c "import secrets; print('JWT_SECRET_KEY = \"' + secrets.token_urlsafe(48) + '\"')"
   
   # Edit config file
   nano $HOME/www/python/src/config.toml
   ```

3. **Update config.toml with your values:**
   ```toml
   GREETING = "Welcome to WikiContest on Toolforge!"
   
   # Security (use generated keys)
   SECRET_KEY = "your-generated-secret-key"
   JWT_SECRET_KEY = "your-generated-jwt-secret-key"
   
   # Database
   SQLALCHEMY_DATABASE_URI = "sqlite:///wikicontest.db"
   SQLALCHEMY_TRACK_MODIFICATIONS = false
   
   # JWT Configuration
   JWT_ACCESS_TOKEN_EXPIRES = 86400
   
   # Debug mode
   DEBUG = false
   
   # OAuth Configuration
   OAUTH_MWURI = "https://meta.wikimedia.org/w/index.php"
   CONSUMER_KEY = "your-consumer-key-from-oauth-registration"
   CONSUMER_SECRET = "your-consumer-secret-from-oauth-registration"
   ```

### **Step 5: Set File Permissions**

```bash
# Make config file secure (only tool user can read)
chmod u=rw,go= $HOME/www/python/src/config.toml
```

### **Step 6: Start the Webservice**

```bash
webservice python3.13 start
```

### **Step 7: Test Your Deployment**

1. **Visit your tool:** https://wikicontest.toolforge.org/
2. **Test API health:** https://wikicontest.toolforge.org/api/health
3. **Test OAuth login:** https://wikicontest.toolforge.org/login

## 🔧 **File Structure on Toolforge**

```
$HOME/
├── uwsgi.log
├── error.log
└── www/
    └── python/
        ├── src/
        │   ├── app.py                 # Main Flask application
        │   ├── config.toml            # Configuration file
        │   ├── requirements.txt       # Python dependencies
        │   ├── templates/
        │   │   ├── index.html         # Main page template
        │   │   └── login.html         # Login page template
        │   ├── static/
        │   │   └── app.js             # Frontend JavaScript
        │   ├── models/
        │   │   ├── user.py            # User model
        │   │   ├── contest.py         # Contest model
        │   │   └── submission.py      # Submission model
        │   ├── routes/
        │   │   ├── user_routes.py     # User API routes
        │   │   ├── contest_routes.py  # Contest API routes
        │   │   └── submission_routes.py # Submission API routes
        │   └── middleware/
        │       └── auth.py            # Authentication middleware
        └── venv/                      # Python virtual environment
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Webservice won't start:**
   ```bash
   # Check logs
   tail -n 50 $HOME/uwsgi.log
   tail -n 50 $HOME/error.log
   ```

2. **Import errors:**
   ```bash
   # Check if virtual environment is activated
   webservice python3.13 shell
   source $HOME/www/python/venv/bin/activate
   pip list
   ```

3. **OAuth errors:**
   - Verify CONSUMER_KEY and CONSUMER_SECRET in config.toml
   - Check callback URL matches exactly
   - Ensure OAuth consumer is approved

4. **Database errors:**
   ```bash
   # Check if database file exists
   ls -la $HOME/www/python/src/
   ```

### **Useful Commands**

```bash
# Restart webservice
webservice restart

# Stop webservice
webservice stop

# Check webservice status
webservice status

# View real-time logs
tail -f $HOME/uwsgi.log

# Test database connection
webservice python3.13 shell
python3 -c "from app import app, db; app.app_context().push(); print('Database OK')"
```

## 🔒 **Security Considerations**

1. **Never commit secrets:** Keep config.toml out of version control
2. **File permissions:** Ensure config.toml is only readable by tool user
3. **OAuth secrets:** Keep consumer key and secret secure
4. **Database:** SQLite file should be in a secure location

## 📈 **Production Optimizations**

1. **Enable caching:** Consider Redis for session storage
2. **Database optimization:** Add proper indexing
3. **Static files:** Use CDN for better performance
4. **Monitoring:** Set up proper logging and monitoring

## 🔄 **Updates and Maintenance**

1. **Update code:**
   ```bash
   # Copy new files
   cp new_file.py $HOME/www/python/src/
   
   # Restart webservice
   webservice restart
   ```

2. **Update dependencies:**
   ```bash
   webservice python3.13 shell
   source $HOME/www/python/venv/bin/activate
   pip install -r $HOME/www/python/src/requirements.txt
   exit
   webservice restart
   ```

## 📚 **Additional Resources**

- [Toolforge Documentation](https://wikitech.wikimedia.org/wiki/Help:Toolforge)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OAuth Documentation](https://www.mediawiki.org/wiki/OAuth)
- [Toolforge Python Guide](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Python)

## 🆘 **Getting Help**

- **Toolforge IRC:** #wikimedia-cloud on Freenode
- **Toolforge Mailing List:** cloud@lists.wikimedia.org
- **Toolforge Phabricator:** #Cloud-Services project

---

**Note:** This deployment uses SQLite for simplicity. For production use with many users, consider migrating to MySQL or PostgreSQL.
