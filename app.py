from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, request



# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recycling.db'  # Replace with your database URI if needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class WasteSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    pickup_address = db.Column(db.Text, nullable=False)
    contact_info = db.Column(db.String(100), nullable=False)
    submission_date = db.Column(db.DateTime, default=db.func.current_timestamp())





@app.before_request
def force_https():
    if not request.is_secure:
        return redirect(request.url.replace("http://", "https://"), code=301)

# Routes
@app.route('/')
def home():
    return render_template('index.html')  # Ensure index.html exists

@app.route('/submit', methods=['POST'])
def submit_waste():
    try:
        data = request.get_json()
        material_type = data.get('material_type')
        quantity = data.get('quantity')
        pickup_address = data.get('pickup_address')
        contact_info = data.get('contact_info')

        # Validation
        if not all([material_type, quantity, pickup_address, contact_info]):
            return jsonify({'error': 'All fields are required'}), 400

        # Save to database
        new_submission = WasteSubmission(
            material_type=material_type,
            quantity=quantity,
            pickup_address=pickup_address,
            contact_info=contact_info
        )
        db.session.add(new_submission)
        db.session.commit()

        return jsonify({'message': 'Submission successful'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submissions', methods=['GET'])
def get_submissions():
    try:
        submissions = WasteSubmission.query.all()
        results = [
            {
                'id': sub.id,
                'material_type': sub.material_type,
                'quantity': sub.quantity,
                'pickup_address': sub.pickup_address,
                'contact_info': sub.contact_info,
                'submission_date': sub.submission_date
            } for sub in submissions
        ]
        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    app.run(debug=True)
