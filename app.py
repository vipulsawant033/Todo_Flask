from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Database initialization
def init_db():
    conn = sqlite3.connect('tododb.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS todos')
    # Create todo table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            description TEXT,  -- Add the 'description' column
            completed BOOLEAN NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Initialize the database
init_db()


# Create
@app.route('/create', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task = request.form['task']
        description = request.form['description']
        completed = False

        conn = sqlite3.connect('tododb.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO todos (task, description, completed) VALUES (?, ?, ?)', (task, description, completed))

        conn.commit()
        conn.close()

        flash('Task created successfully!', 'success')
        return redirect(url_for('get_tasks'))

    return render_template('create_task.html')


# Read
@app.route('/')
def get_tasks():
    conn = sqlite3.connect('tododb.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM todos')
    tasks = cursor.fetchall()

    conn.close()

    return render_template('index_task.html', tasks=tasks)


# Update
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def update_task(id):
    conn = sqlite3.connect('tododb.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        # Check if the form is for updating completed tasks
        if id == -1:
            completed_tasks = request.form.getlist('completed_tasks')
            for task_id in completed_tasks:
                cursor.execute('DELETE FROM todos WHERE id=?', (int(task_id),))
        else:
            task = request.form['task']
            description = request.form['description']
            completed = 'completed' in request.form

            cursor.execute('UPDATE todos SET task=?, description=?, completed=? WHERE id=?',(task, description, completed, id))

        conn.commit()
        conn.close()

        flash('Task(s) updated successfully', 'success')
        return redirect(url_for('get_tasks'))

    else:
        cursor.execute('SELECT * FROM todos WHERE id=?', (id,))
        task_data = cursor.fetchone()

        conn.close()

        if task_data:
            task = {'id': task_data[0], 'task': task_data[1], 'description': task_data[2] if len(task_data) > 2 else '', 'completed': bool(task_data[3]) if len(task_data) > 3 else False}

        else:
            flash('Task not found', 'danger')
            return redirect(url_for('get_tasks'))

        return render_template('update_task.html', task=task)


# Delete
@app.route('/delete/<int:id>')
def delete_task(id):
    conn = sqlite3.connect('tododb.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM todos WHERE id=?', (id,))

    conn.commit()
    conn.close()

    flash('Task deleted successfully', 'success')
    return redirect(url_for('get_tasks'))


if __name__ == '__main__':
    app.run(debug=True)
