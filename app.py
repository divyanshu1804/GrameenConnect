from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from app.models.database import initialize_db, get_db_connection
from app.models.auth import login_required
from app.translations import translations
from functools import wraps
import traceback

app = Flask(__name__, 
            static_folder='app/static',
            template_folder='app/templates')
app.secret_key = 'grameenconnect_secret_key'  # Change this in production

# Use a simpler absolute path for UPLOAD_FOLDER to avoid path issues
uploads_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'static', 'images', 'uploads'))
app.config['UPLOAD_FOLDER'] = uploads_folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Ensure upload directory exists with proper permissions
try:
    print(f"Debug: Ensuring upload folder exists at: {uploads_folder}")
    os.makedirs(uploads_folder, exist_ok=True)
    
    # Test file creation to ensure write permissions
    test_file_path = os.path.join(uploads_folder, 'test_write_access.txt')
    with open(test_file_path, 'w') as f:
        f.write('Test file to check permissions')
    print(f"Debug: Successfully created test file at: {test_file_path}")
    
    # List directory contents for verification
    print(f"Debug: Files in upload directory: {os.listdir(uploads_folder)}")
except Exception as e:
    print(f"Debug: Error setting up upload folder: {e}")
    print(f"Debug: Full traceback: {traceback.format_exc()}")
    # Try an alternative location as fallback
    try:
        alt_uploads = os.path.abspath('uploads')
        os.makedirs(alt_uploads, exist_ok=True)
        app.config['UPLOAD_FOLDER'] = alt_uploads
        print(f"Debug: Using alternative upload folder at: {alt_uploads}")
    except Exception as inner_e:
        print(f"Debug: Error with alternative upload folder: {inner_e}")

# Initialize the database
with app.app_context():
    initialize_db()

# Make translations available in all templates
@app.context_processor
def inject_translations():
    lang = session.get('language', 'en')
    g.lang = lang  # Make language accessible via g.lang
    translations_dict = translations.get(lang, translations['en'])
    
    # Create a translation function
    def translate(key):
        return translations_dict.get(key, key)
    
    return {
        't': translations_dict,
        '_': translate  # Now '_' is a function that can be called
    }

# Make user info available in all templates
@app.context_processor
def inject_user():
    try:
        if 'user_id' in session:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
            conn.close()
            
            if user:
                # Convert SQLite Row to dict to allow adding custom attributes
                user_dict = dict(user)
                user_dict['is_authenticated'] = True
                
                # Make sure profile_image is safely handled in session
                if 'profile_image' not in session and user['profile_image'] is not None and user['profile_image'].strip() != '':
                    session['profile_image'] = user['profile_image']
                    print(f"Debug: Added missing profile_image to session: {user['profile_image']}")
                    
                return {'current_user': user_dict}
        
        # Default case for users not logged in
        return {'current_user': {'is_authenticated': False}}
    except Exception as e:
        print(f"Debug: Error in inject_user context processor: {e}")
        # Return a safe default to prevent template rendering issues
        return {'current_user': {'is_authenticated': False}}

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Job Board routes
@app.route('/jobs')
def jobs():
    category = request.args.get('category')
    
    print(f"Debug: Accessing jobs route with category filter: {category}")
    
    conn = get_db_connection()
    
    # Debug: Check database connection and job count
    job_count = conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
    print(f"Debug: Total jobs in database: {job_count}")
    
    if job_count == 0:
        print("Debug: No jobs found in database")
    
    if category:
        print(f"Debug: Filtering by category: {category}")
        jobs = conn.execute('SELECT * FROM jobs WHERE category = ? ORDER BY posted_date DESC', (category,)).fetchall()
        print(f"Debug: Found {len(jobs)} jobs matching category")
    else:
        print("Debug: No category filter applied")
        jobs = conn.execute('SELECT * FROM jobs ORDER BY posted_date DESC').fetchall()
        print(f"Debug: Retrieved {len(jobs)} jobs total")
        
        # Print the first job if available for debugging
        if len(jobs) > 0:
            print(f"Debug: First job: ID={jobs[0]['id']}, Title={jobs[0]['title']}, Category={jobs[0]['category']}")
    
    conn.close()
    
    return render_template('jobs.html', jobs=jobs, selected_category=category)

@app.route('/jobs/<int:id>')
def job_details(id):
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if job is None:
        flash('Job not found!')
        return redirect(url_for('jobs'))
    
    # Convert job to a mutable dictionary
    job_dict = dict(job)
    
    # Convert posted_date string to datetime object
    try:
        # Try to parse the date string
        if job_dict['posted_date']:
            job_dict['posted_date'] = datetime.strptime(job_dict['posted_date'], '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        # If parsing fails, use current date
        job_dict['posted_date'] = datetime.now()
        
    return render_template('job_details.html', job=job_dict)

@app.route('/jobs/new', methods=['GET', 'POST'])
@login_required
def new_job():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        contact = request.form['contact']
        category = request.form['category']
        eligibility = request.form['eligibility']
        salary = request.form['salary']
        deadline = request.form['deadline']
        
        if not title or not description or not contact:
            flash('Title, description and contact information are required!')
            return render_template('new_job.html')
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO jobs 
            (title, description, location, contact, category, eligibility, salary, deadline, user_id, posted_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, location, contact, category, eligibility, salary, deadline, session.get('user_id'), datetime.now()))
        conn.commit()
        conn.close()
        
        flash('Job posted successfully!')
        return redirect(url_for('jobs'))
        
    return render_template('new_job.html')

# Government Schemes routes
@app.route('/schemes')
def schemes():
    conn = get_db_connection()
    schemes = conn.execute('SELECT * FROM schemes ORDER BY posted_date DESC').fetchall()
    conn.close()
    return render_template('schemes.html', schemes=schemes)

@app.route('/schemes/<int:id>')
def scheme_details(id):
    conn = get_db_connection()
    scheme = conn.execute('SELECT * FROM schemes WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if scheme is None:
        flash('Scheme not found!')
        return redirect(url_for('schemes'))
        
    return render_template('scheme_details.html', scheme=scheme)

# Infrastructure Reporting routes
@app.route('/issues')
def issues():
    conn = get_db_connection()
    issues = conn.execute('SELECT * FROM issues ORDER BY reported_date DESC').fetchall()
    conn.close()
    return render_template('issues.html', issues=issues)

@app.route('/issues/report', methods=['GET', 'POST'])
@login_required
def report_issue():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        category = request.form['category']
        
        if not title or not description or not location:
            flash('Title, description and location are required!')
            return render_template('report_issue.html')
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)
        
        conn = get_db_connection()
        conn.execute('INSERT INTO issues (title, description, location, category, image, user_id, reported_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                     (title, description, location, category, image_filename, session.get('user_id'), datetime.now(), 'Pending'))
        conn.commit()
        conn.close()
        
        flash('Issue reported successfully!')
        return redirect(url_for('issues'))
        
    return render_template('report_issue.html')

# Marketplace routes
@app.route('/marketplace')
def marketplace():
    conn = get_db_connection()
    
    # Get filter parameters
    category = request.args.get('category')
    search = request.args.get('search')
    
    # Base query
    query = 'SELECT * FROM products'
    params = []
    
    # Apply filters if provided
    if category or search:
        query += ' WHERE'
        
        if category:
            query += ' category = ?'
            params.append(category)
            
        if search:
            if category:  # If category filter is also applied
                query += ' AND'
            query += ' (name LIKE ? OR description LIKE ?)'
            params.append(f'%{search}%')
            params.append(f'%{search}%')
    
    # Add ordering
    query += ' ORDER BY posted_date DESC'
    
    # Execute query with parameters
    products = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('marketplace.html', products=products)

@app.route('/marketplace/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        location = request.form['location']
        contact = request.form['contact']
        category = request.form['category']
        
        if not name or not price or not contact:
            flash('Product name, price and contact information are required!')
            return render_template('new_product.html')
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)
        
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, description, price, location, contact, category, image, user_id, posted_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (name, description, price, location, contact, category, image_filename, session.get('user_id'), datetime.now()))
        conn.commit()
        conn.close()
        
        flash('Product listed successfully!')
        return redirect(url_for('marketplace'))
        
    return render_template('new_product.html')

# Auth routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already logged in, redirect to home page
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        village = request.form['village']
        contact = request.form['contact']
        
        # Enhanced validation
        validation_errors = []
        
        if not username or len(username) < 3:
            validation_errors.append('Username must be at least 3 characters long.')
        
        if not password or len(password) < 6:
            validation_errors.append('Password must be at least 6 characters long.')
            
        if not contact:
            validation_errors.append('Contact information is required.')
            
        if validation_errors:
            for error in validation_errors:
                flash(error)
            return render_template('register.html')
            
        conn = get_db_connection()
        existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        
        if existing_user:
            flash('Username already exists! Please choose another one.')
            conn.close()
            return render_template('register.html')
            
        try:
            conn.execute('INSERT INTO users (username, password, fullname, village, contact, joined_date) VALUES (?, ?, ?, ?, ?, ?)',
                      (username, password, fullname, village, contact, datetime.now()))
            conn.commit()
            
            # Get the newly created user to log them in automatically
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            
            # Auto login after registration
            if user:
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['fullname'] = user['fullname'] if user['fullname'] else user['username']
                session['profile_image'] = user['profile_image']
                
            conn.close()
            
            flash('Registration successful! Welcome to GrameenConnect.')
            # Use redirect with explicit return
            return redirect(url_for('index'))
        except Exception as e:
            conn.close()
            flash('An error occurred during registration. Please try again.')
            print(f"Registration error: {e}")
            return render_template('register.html')
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Debug: Login route accessed")
    
    # If user is already logged in, redirect to home page
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"Debug: Login attempt for username: {username}")
        
        if not username or not password:
            flash('Username and password are required!')
            print("Debug: Username or password missing in form")
            return render_template('login.html')
            
        conn = get_db_connection()
        
        # First check if the user exists
        user_exists = conn.execute('SELECT id FROM users WHERE username = ?', 
                              (username,)).fetchone()
        
        if not user_exists:
            conn.close()
            flash('Invalid username or password!')
            print(f"Debug: User {username} not found in database")
            return render_template('login.html')
            
        # Then validate the credentials
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                          (username, password)).fetchone()
        conn.close()
        
        if user:
            try:
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['fullname'] = user['fullname'] if user['fullname'] else user['username']
                
                # Safely store profile image in session
                if user['profile_image'] is not None and user['profile_image'].strip() != '':
                    session['profile_image'] = user['profile_image']
                    print(f"Debug: Set profile_image in session: {user['profile_image']}")
                else:
                    # Ensure profile_image is not set in session if it's not in the database
                    session.pop('profile_image', None)
                    print("Debug: No profile image found for user")
                
                print(f"Debug: Login successful. Session user_id set to {session['user_id']}")
                print(f"Debug: Current session data: {session}")
                
                # Test if we can access the session data
                test_user_id = session.get('user_id')
                print(f"Debug: Test retrieving user_id from session: {test_user_id}")
                
                flash('Login successful! Welcome back, ' + session['username'] + '!')
                # Use redirect with explicit return
                return redirect(url_for('index'))
            except Exception as e:
                print(f"Debug: Error during login session setup: {e}")
                flash('An error occurred during login. Please try again.')
                return render_template('login.html')
        else:
            flash('Invalid password! Please try again.')
            print(f"Debug: Invalid password for user {username}")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

# User Profile
@app.route('/profile')
@login_required
def profile():
    print("Debug: Profile route accessed")
    print(f"Debug: Session data in profile route: {session}")
    user_id = session.get('user_id')
    print(f"Debug: user_id from session: {user_id}")
    
    conn = get_db_connection()
    
    # Fetch user data
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    print(f"Debug: User query result: {user}")
    
    if not user:
        print(f"Debug: User with ID {user_id} not found in database")
        conn.close()
        flash('User not found!')
        return redirect(url_for('index'))
    
    # Fetch user's jobs
    jobs = conn.execute('''
        SELECT * FROM jobs
        WHERE user_id = ?
        ORDER BY posted_date DESC
    ''', (user_id,)).fetchall()
    
    # Fetch user's issues
    issues = conn.execute('''
        SELECT * FROM issues
        WHERE user_id = ?
        ORDER BY reported_date DESC
    ''', (user_id,)).fetchall()
    
    # Fetch user's products
    products = conn.execute('''
        SELECT * FROM products
        WHERE user_id = ?
        ORDER BY posted_date DESC
    ''', (user_id,)).fetchall()
    
    # Fetch user's job applications
    try:
        applications = conn.execute('''
            SELECT ja.*, j.title as job_title
            FROM job_applications ja
            JOIN jobs j ON ja.job_id = j.id
            WHERE ja.user_id = ?
            ORDER BY ja.application_date DESC
        ''', (user_id,)).fetchall()
    except Exception as e:
        print(f"Debug: Error fetching applications: {e}")
        applications = []
    
    print(f"Debug: User has {len(jobs)} jobs, {len(issues)} issues, {len(products)} products, and {len(applications)} applications")
    
    conn.close()
    
    return render_template('profile.html', 
                          user=user, 
                          jobs=jobs, 
                          issues=issues, 
                          products=products,
                          applications=applications)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    print(f"Debug: Edit profile route accessed, session data: {session}")
    print(f"Debug: User ID in session: {session.get('user_id')}")
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if user is None:
        print(f"Debug: User not found for ID: {session.get('user_id')}")
        conn.close()
        flash('User not found!')
        return redirect(url_for('index'))
    
    print(f"Debug: User found: {user['username']}")
    
    if request.method == 'POST':
        fullname = request.form.get('fullname', '')
        village = request.form.get('village', '')
        contact = request.form.get('contact', '')
        
        # Basic validation
        if not contact:
            flash('Contact information is required!')
            return render_template('edit_profile.html', user=user)
        
        # Handle profile image upload
        profile_image = user['profile_image'] if 'profile_image' in user.keys() else None  # Default to current image or None
        try:
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                print(f"Debug: Profile image file received: {file}")
                
                if file and file.filename and file.filename != '':
                    print(f"Debug: Filename: {file.filename}")
                    
                    # Simple validation first
                    if not allowed_file(file.filename):
                        flash("Invalid file type. Only JPG, JPEG, PNG, and GIF files are allowed.")
                        return render_template('edit_profile.html', user=user)
                    
                    # Create a safe filename
                    filename = secure_filename(file.filename)
                    timestamp = int(datetime.now().timestamp())
                    new_filename = f"{session['username']}_profile_{timestamp}_{filename}"
                    
                    # Ensure the upload folder exists
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    # Save the file
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                    print(f"Debug: Saving to {file_path}")
                    
                    # Store the file data in memory first
                    file_data = file.read()
                    
                    # Then write it to disk
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    
                    print(f"Debug: File saved, checking if it exists")
                    if os.path.exists(file_path):
                        print(f"Debug: File exists at {file_path}")
                        profile_image = new_filename
                    else:
                        print(f"Debug: File does not exist at {file_path}")
        except Exception as e:
            print(f"Debug: Error uploading profile image: {e}")
            print(f"Debug: Traceback: {traceback.format_exc()}")
            flash('Error uploading profile image. Please try the alternative upload method.')
        
        # Handle banner image upload
        banner_image = user['banner_image'] if 'banner_image' in user.keys() else None  # Default to current image or None
        try:
            if 'banner_image' in request.files:
                file = request.files['banner_image']
                
                if file and file.filename and file.filename != '':
                    # Simple validation first
                    if not allowed_file(file.filename):
                        flash("Invalid file type. Only JPG, JPEG, PNG, and GIF files are allowed.")
                        return render_template('edit_profile.html', user=user)
                    
                    # Create a safe filename
                    filename = secure_filename(file.filename)
                    timestamp = int(datetime.now().timestamp())
                    new_filename = f"{session['username']}_banner_{timestamp}_{filename}"
                    
                    # Ensure the upload folder exists
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    # Save the file
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                    
                    # Store the file data in memory first
                    file_data = file.read()
                    
                    # Then write it to disk
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    
                    if os.path.exists(file_path):
                        banner_image = new_filename
        except Exception as e:
            print(f"Debug: Error uploading banner image: {e}")
            print(f"Debug: Traceback: {traceback.format_exc()}")
            flash('Error uploading banner image. Please try again later.')
        
        try:
            # Update user information
            conn.execute('''
                UPDATE users 
                SET fullname = ?, village = ?, contact = ?, profile_image = ?, banner_image = ?
                WHERE id = ?
            ''', (fullname, village, contact, profile_image, banner_image, session['user_id']))
            
            # If user changes fullname, update the session
            if user['fullname'] != fullname:
                session['fullname'] = fullname if fullname else user['username']
            
            # Update profile_image in session if changed
            if 'profile_image' in user.keys() and user['profile_image'] != profile_image:
                session['profile_image'] = profile_image
                print(f"Debug: Updated session with new profile_image: {profile_image}")
            
            conn.commit()
            flash('Profile updated successfully!')
        except Exception as e:
            conn.rollback()
            print(f"Debug: Error updating user profile in database: {e}")
            print(f"Debug: Traceback: {traceback.format_exc()}")
            flash(f'Error updating profile: {str(e)}')
        finally:
            conn.close()
            
        return redirect(url_for('profile'))
    
    conn.close()
    return render_template('edit_profile.html', user=user)

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/settings')
@login_required
def settings():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('settings.html', user=user)

# Language toggle
@app.route('/language/<lang>')
def set_language(lang):
    next_page = request.args.get('next', '/')
    session['language'] = lang
    return redirect(next_page)

@app.route('/jobs/<int:id>/apply', methods=['GET', 'POST'])
@login_required
def apply_for_job(id):
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (id,)).fetchone()
    
    if job is None:
        flash('Job not found!')
        return redirect(url_for('jobs'))
    
    job_dict = dict(job)
    
    # Check if user has already applied
    application = conn.execute(
        'SELECT * FROM job_applications WHERE user_id = ? AND job_id = ?', 
        (session.get('user_id'), id)
    ).fetchone()
    
    if request.method == 'POST':
        name = request.form.get('name', '')
        phone = request.form.get('phone', '')
        experience = request.form.get('experience', '')
        message = request.form.get('message', '')
        
        if not name or not phone:
            flash('Name and phone number are required!')
            return render_template('apply_job.html', job=job_dict, already_applied=application is not None)
        
        # If already applied, update the application
        if application:
            conn.execute(
                '''UPDATE job_applications 
                   SET name = ?, phone = ?, experience = ?, message = ?, application_date = ?
                   WHERE user_id = ? AND job_id = ?''',
                (name, phone, experience, message, datetime.now(), session.get('user_id'), id)
            )
            flash('Your application has been updated!')
        else:
            # Otherwise create a new application
            conn.execute(
                '''INSERT INTO job_applications 
                   (job_id, user_id, name, phone, experience, message, application_date, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (id, session.get('user_id'), name, phone, experience, message, datetime.now(), 'Pending')
            )
            flash('Your application has been submitted!')
        
        conn.commit()
        conn.close()
        return redirect(url_for('job_details', id=id))
    
    # For GET request, show the application form
    user = None
    if session.get('user_id'):
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session.get('user_id'),)).fetchone()
    
    conn.close()
    return render_template('apply_job.html', job=job_dict, user=user, already_applied=application is not None)

@app.route('/my-applications')
@login_required
def my_applications():
    conn = get_db_connection()
    
    # Get all applications for the current user with job details
    applications = conn.execute('''
        SELECT a.*, j.title as job_title, j.category as job_category, j.location as job_location, j.deadline as job_deadline
        FROM job_applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE a.user_id = ?
        ORDER BY a.application_date DESC
    ''', (session.get('user_id'),)).fetchall()
    
    conn.close()
    
    return render_template('my_applications.html', applications=applications)

# Direct upload fallback route (can be removed or protected in production)
@app.route('/direct-upload', methods=['GET', 'POST'])
@login_required
def direct_upload():
    if request.method == 'POST':
        try:
            # Get the file from the request
            if 'file' not in request.files:
                return 'No file part in the request', 400
                
            file = request.files['file']
            if file.filename == '':
                return 'No file selected', 400
                
            # Check file type
            if not allowed_file(file.filename):
                return 'Invalid file type. Only JPG, JPEG, PNG, and GIF files are allowed.', 400
                
            # Save the file with a unique name
            timestamp = int(datetime.now().timestamp())
            filename = secure_filename(file.filename)
            new_filename = f"{session['username']}_direct_{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Read file data into memory and then write to disk
            file_data = file.read()
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Verify file exists
            if not os.path.exists(file_path):
                return 'Failed to save the file, please try again', 500
            
            # Update the user's profile image in the database
            conn = get_db_connection()
            conn.execute('UPDATE users SET profile_image = ? WHERE id = ?', 
                         (new_filename, session['user_id']))
            conn.commit()
            conn.close()
            
            # Update in session as well
            session['profile_image'] = new_filename
            
            return f"File uploaded successfully as {new_filename}", 200
            
        except Exception as e:
            print(f"Debug: Error in direct upload: {e}")
            print(f"Debug: Traceback: {traceback.format_exc()}")
            return f"Error: {str(e)}", 500
    
    # Simple upload form for GET requests
    return '''
    <!doctype html>
    <html>
    <head>
        <title>Direct Profile Picture Upload</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { max-width: 500px; margin: 0 auto; padding: 20px; }
            .preview { width: 100px; height: 100px; margin: 15px auto; border-radius: 50%; object-fit: cover; }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h3 class="mb-0">Upload Profile Picture</h3>
            </div>
            <div class="card-body">
                <p>Use this simple form to directly upload your profile picture.</p>
                
                <div class="mb-3">
                    <label for="file" class="form-label">Select image:</label>
                    <input type="file" class="form-control" id="file" name="file" accept=".jpg,.jpeg,.png,.gif">
                </div>
                
                <div class="text-center">
                    <img id="preview" src="" class="preview hidden" alt="Preview">
                </div>
                
                <div class="d-grid mt-3">
                    <button onclick="uploadFile()" class="btn btn-primary">Upload</button>
                </div>
                
                <div id="result" class="alert mt-3 hidden"></div>
                
                <div class="mt-3 text-center">
                    <a href="/profile" class="btn btn-outline-secondary btn-sm">Return to Profile</a>
                </div>
            </div>
        </div>
                
        <script>
            // Preview image
            document.getElementById('file').addEventListener('change', function(e) {
                const file = this.files[0];
                if (!file) return;
                
                const preview = document.getElementById('preview');
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.classList.remove('hidden');
                }
                
                reader.readAsDataURL(file);
            });
            
            function uploadFile() {
                const fileInput = document.getElementById('file');
                const resultDiv = document.getElementById('result');
                const btn = document.querySelector('button');
                
                if (!fileInput.files.length) {
                    showResult('Please select a file first.', 'warning');
                    return;
                }
                
                // Show loading state
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
                resultDiv.classList.add('hidden');
                
                const file = fileInput.files[0];
                const formData = new FormData();
                formData.append('file', file);
                
                fetch('/direct-upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(text || 'Failed to upload image');
                        });
                    }
                    return response.text();
                })
                .then(text => {
                    showResult('Image uploaded successfully! Redirecting to your profile...', 'success');
                    setTimeout(() => {
                        window.location.href = '/profile';
                    }, 2000);
                })
                .catch(error => {
                    showResult(error.message || 'Error uploading file', 'danger');
                })
                .finally(() => {
                    btn.disabled = false;
                    btn.innerHTML = 'Upload';
                });
            }
            
            function showResult(message, type) {
                const resultDiv = document.getElementById('result');
                resultDiv.textContent = message;
                resultDiv.className = `alert alert-${type} mt-3`;
                resultDiv.classList.remove('hidden');
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 