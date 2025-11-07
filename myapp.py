from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
app.secret_key = 'zhrakey'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'portofoliodb'
mysql = MySQL(app)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT nama, bio, photo FROM user LIMIT 1")
    profile = cur.fetchone()
    cur.execute("SELECT * FROM skills")
    skills = cur.fetchall()
    cur.execute("SELECT * FROM project")
    projects = cur.fetchall()
    cur.close()
    return render_template('index.html', profile=profile, skills=skills, projects=projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE username=%s AND password=%s", (uname, pwd))
        user = cur.fetchone()
        cur.close()
        if user:
            session['is_logged_in'] = True
            session['username'] = user[1]
            flash('Login berhasil!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Login gagal! Username atau password salah', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Berhasil logout.', 'info')
    return redirect(url_for('index'))
@app.route('/admin')
def admin():
    if not session.get('is_logged_in'):
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user LIMIT 1")
    profile = cur.fetchone()
    cur.execute("SELECT * FROM skills")
    skills = cur.fetchall()
    cur.execute("SELECT * FROM project")
    projects = cur.fetchall()
    cur.close()
    return render_template('admin.html', profile=profile, skills=skills, projects=projects)

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if not session.get('is_logged_in'):
        return redirect(url_for('login'))
    nama = request.form['name']
    bio = request.form['bio']
    photo = request.files['photo']
    filename = None

    if photo and photo.filename != '':
        filename = photo.filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(path)

    cur = mysql.connection.cursor()
    if filename:
        cur.execute("UPDATE user SET nama=%s, bio=%s, photo=%s WHERE id=1", (nama, bio, filename))
    else:
        cur.execute("UPDATE user SET nama=%s, bio=%s WHERE id=1", (nama, bio))
    mysql.connection.commit()
    cur.close()

    flash('Profil berhasil diperbarui!', 'success')
    return redirect(url_for('admin'))
@app.route('/add_skill', methods=['POST'])
def add_skill():
    name = request.form['name']
    level = request.form['level']
    icon = request.form['icon']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO skills (name, level, icon) VALUES (%s, %s, %s)", (name, level, icon))
    mysql.connection.commit()
    cur.close()

    flash('Skill berhasil ditambahkan!', 'success')
    return redirect(url_for('admin'))

@app.route('/edit_skill/<int:id>', methods=['POST'])
def edit_skill(id):
    name = request.form['name']
    level = request.form['level']
    icon = request.form['icon']

    cur = mysql.connection.cursor()
    cur.execute("UPDATE skills SET name=%s, level=%s, icon=%s WHERE id=%s", (name, level, icon, id))
    mysql.connection.commit()
    cur.close()

    flash('Skill berhasil diperbarui!', 'info')
    return redirect(url_for('admin'))

@app.route('/delete_skill/<int:id>')
def delete_skill(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM skills WHERE id=%s", [id])
    mysql.connection.commit()
    cur.close()

    flash('Skill berhasil dihapus!', 'danger')
    return redirect(url_for('admin'))

@app.route('/add_project', methods=['POST'])
def add_project():
    title = request.form['title']
    desc = request.form['descriptiom']  # sesuai kolom DB
    link = request.form['link']
    photo = request.files['photo']
    filename = None

    if photo and photo.filename != '':
        filename = photo.filename
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO project (title, descriptiom, photo, link) VALUES (%s, %s, %s, %s)",
        (title, desc, filename, link)
    )
    mysql.connection.commit()
    cur.close()

    flash('Project berhasil ditambahkan!', 'success')
    return redirect(url_for('admin'))

@app.route('/edit_project/<int:id>', methods=['POST'])
def edit_project(id):
    title = request.form['title']
    desc = request.form['descriptiom']
    link = request.form['link']
    photo = request.files['photo']
    filename = None

    if photo and photo.filename != '':
        filename = photo.filename
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    cur = mysql.connection.cursor()
    if filename:
        cur.execute(
            "UPDATE project SET title=%s, descriptiom=%s, photo=%s, link=%s WHERE id=%s",
            (title, desc, filename, link, id)
        )
    else:
        cur.execute(
            "UPDATE project SET title=%s, descriptiom=%s, link=%s WHERE id=%s",
            (title, desc, link, id)
        )
    mysql.connection.commit()
    cur.close()

    flash('Project berhasil diperbarui!', 'info')
    return redirect(url_for('admin'))

@app.route('/delete_project/<int:id>')
def delete_project(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM project WHERE id=%s", [id])
    mysql.connection.commit()
    cur.close()

    flash('Project berhasil dihapus!', 'danger')
    return redirect(url_for('admin'))
if __name__ == '__main__':
    app.run(debug=True)

