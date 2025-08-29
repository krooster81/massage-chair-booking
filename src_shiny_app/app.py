from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Needed for flash messages

# Initialize SQLite database
def init_db():
    if not os.path.exists('bookings.db'):
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE bookings
                     (date TEXT, time TEXT, name TEXT, email TEXT,
                      UNIQUE(date, time))''')
        conn.commit()
        conn.close()

init_db()

# Generate time slots (30-min intervals, 9 AM–5 PM)
def get_time_slots():
    times = []
    start = datetime.strptime("09:00", "%H:%M")
    end = datetime.strptime("17:00", "%H:%M")
    while start < end:
        times.append(start.strftime("%H:%M"))
        start += timedelta(minutes=30)
    return times

# Check available slots for a date
def get_available_slots(date):
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("SELECT time FROM bookings WHERE date = ?", (date,))
    booked = [row[0] for row in c.fetchall()]
    conn.close()
    all_slots = get_time_slots()
    return [slot for slot in all_slots if slot not in booked]

@app.route('/', methods=['GET', 'POST'])
def index():
    today = datetime.now().strftime("%Y-%m-%d")
    selected_date = request.args.get('date', today)
    available_slots = get_available_slots(selected_date)
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        time = request.form['time']
        date = request.form['date']
        
        if not name or not email or not time:
            flash('All fields are required!', 'error')
            return redirect(url_for('index', date=date))
        
        try:
            conn = sqlite3.connect('bookings.db')
            c = conn.cursor()
            c.execute("INSERT INTO bookings (date, time, name, email) VALUES (?, ?, ?, ?)",
                     (date, time, name, email))
            conn.commit()
            conn.close()
            flash('Booking successful!', 'success')
            return redirect(url_for('index', date=date))
        except sqlite3.IntegrityError:
            flash('This slot is already booked!', 'error')
            return redirect(url_for('index', date=date))
    
    # Get booked slots for display
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("SELECT time FROM bookings WHERE date = ?", (selected_date,))
    booked_slots = [row[0] for row in c.fetchall()]
    conn.close()
    
    return render_template('index.html', 
                         date=selected_date,
                         available_slots=available_slots,
                         booked_slots=booked_slots)

if __name__ == '__main__':
    app.run(debug=True)