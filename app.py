from flask import Flask, render_template, request, redirect, url_for, flash
from email.message import EmailMessage
import smtplib

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a strong secret key
application = app

# Sample tour data
tours = [
    {
        'id': 1,
        'title': 'Masai Mara Adventure',
        'description': 'Witness the Great Migration in Kenya\'s most famous wildlife reserve.',
        'price': 600,
        'duration': '3 Days',
        'image': 'masai-mara.jpg',
        'itinerary': ['Day 1: Arrival and game drive', 'Day 2: Full day safari', 'Day 3: Departure'],
        'includes': ['Transport', 'Accommodation', 'Meals'],
        'excludes': ['Park fees', 'Personal items']
    },
    {
        'id': 2,
        'title': 'Amboseli Expedition',
        'description': 'Marvel at elephants with Mount Kilimanjaro as your backdrop.',
        'price': 550,
        'duration': '3 Days',
        'image': 'amboseli.jpg',
        'itinerary': ['Day 1: Arrival and game drive', 'Day 2: Full day safari', 'Day 3: Departure'],
        'includes': ['Transport', 'Accommodation', 'Meals'],
        'excludes': ['Park fees', 'Personal items']
    },
    {
        'id': 3,
        'title': 'Samburu Wilderness',
        'description': 'Discover the unique wildlife of Northern Kenya.',
        'price': 650,
        'duration': '3 Days',
        'image': 'samburu.jpg',
        'itinerary': ['Day 1: Arrival and game drive', 'Day 2: Full day safari', 'Day 3: Departure'],
        'includes': ['Transport', 'Accommodation', 'Meals'],
        'excludes': ['Park fees', 'Personal items']
    }
]

# === EMAIL CONFIGURATION ===
SMTP_SERVER = 'mail.authenticexpeditionstours.co.ke'
SMTP_PORT = 465
SENDER_EMAIL = 'booking@authenticexpeditionstours.co.ke' # Replace with your email
SENDER_PASSWORD = 'authenticexpeditions@24' # Use App Password if using Gmail
RECEIVER_EMAIL = 'booking@authenticexpeditionstours.co.ke' # Company email to receive bookings

# === EMAIL FUNCTION ===
def send_booking_email(data):
    # First send notification to company
    msg = EmailMessage()
    msg.set_content(f"""
New Booking Request Received:

Name: {data['name']}
Email: {data['email']}
Phone: {data['phone']}
Tour: {data['tour']}
Date: {data['date']}
Number of Guests: {data['guests']}
Message: {data['message']}

Best regards,
Authentic Expeditions Tours Bot
    """)
    msg['Subject'] = f"New Booking Request - {data['tour']}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        # If company notification succeeds, send confirmation to client
        confirmation_sent = send_confirmation_email(data['name'], data['email'], data['tour'], data['date'])
        
        if not confirmation_sent:
            flash("Your booking was received but we couldn't send a confirmation email. Please check your email address.", "warning")
            return False
            
        return True
    except Exception as e:
        print("Failed to send email:", str(e))
        flash(f"Booking submission failed: {str(e)}", "error")
        return False

def send_confirmation_email(name, email, tour, date):
    msg = EmailMessage()
    msg.set_content(f"""
Hi {name},

Thank you for submitting your booking request with Authentic Expeditions Tours.
We have received your request for the following tour:

Tour: {tour}
Date: {date}

Our team will contact you shortly to confirm your booking details.

Best regards,
Authentic Expeditions Team
    """)
    msg['Subject'] = 'Booking Confirmation - Authentic Expeditions Tours'
    msg['From'] = SENDER_EMAIL
    msg['To'] = email

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            # Removed server.starttls() since we're already using SMTP_SSL
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Failed to send confirmation email:", e)
        return False

# === FLASK ROUTES ===
@app.route('/')
def home():
    return render_template('index.html', featured_tours=tours[:3])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tours')
def all_tours():  # Renamed to avoid conflict with tours data
    return render_template('tours.html', tours=tours)

@app.route('/tour/<int:tour_id>')  # Changed to match template references
def tour_detail(tour_id):
    tour = next((t for t in tours if t['id'] == tour_id), None)
    if not tour:
        flash('Tour not found', 'error')
        return redirect(url_for('all_tours'))
    return render_template('tour-detail.html', tour=tour)

@app.route('/destinations')
def destinations():
    return render_template('destinations.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        print("Form data received:", request.form)
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'tour': request.form.get('tour'),
            'date': request.form.get('date'),
            'guests': request.form.get('guests'),
            'message': request.form.get('message')
        }

        if send_booking_email(data):
            flash("Your booking has been submitted successfully!", "success")
        else:
            flash("There was an issue submitting your booking. Please try again.", "error")

        return redirect(url_for('booking'))

    return render_template('booking.html', tours=tours)

if __name__ == '__main__':
    app.run(debug=True)
