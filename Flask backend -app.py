from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import requests
import os
from werkzeug.utils import secure_filename
import base64
import json
import statistics
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///diabetes_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
CORS(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    diabetes_type = db.Column(db.String(20))  # Type 1, Type 2, Gestational
    target_glucose_min = db.Column(db.Float, default=80.0)
    target_glucose_max = db.Column(db.Float, default=180.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BloodSugarReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    glucose_level = db.Column(db.Float, nullable=False)
    measurement_time = db.Column(db.String(20))  # Before meal, After meal, Bedtime, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class MealEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_name = db.Column(db.String(200), nullable=False)
    carbs = db.Column(db.Float)
    calories = db.Column(db.Float)
    meal_type = db.Column(db.String(20))  # Breakfast, Lunch, Dinner, Snack
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    photo_path = db.Column(db.String(200))

class MedicationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_time = db.Column(db.Time)
    taken = db.Column(db.Boolean, default=False)

class ExerciseLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_type = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Integer)
    intensity = db.Column(db.String(20))  # Low, Moderate, High
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    calories_burned = db.Column(db.Float)

class AIInsight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    insight_type = db.Column(db.String(50))  # Alert, Tip, Prediction
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

# AI Service Functions
def analyze_meal_photo(image_data):
    """
    Placeholder for meal photo analysis using Hugging Face Vision API
    In production, you would use a food recognition model
    """
    # For demo purposes, return sample data
    sample_foods = [
        {"name": "Grilled Chicken Breast", "carbs": 0, "calories": 185},
        {"name": "Brown Rice", "carbs": 45, "calories": 220},
        {"name": "Mixed Vegetables", "carbs": 10, "calories": 50},
        {"name": "Apple", "carbs": 25, "calories": 95},
        {"name": "Whole Grain Bread", "carbs": 15, "calories": 80}
    ]
    
    import random
    selected_food = random.choice(sample_foods)
    return {
        "recognized_food": selected_food["name"],
        "estimated_carbs": selected_food["carbs"],
        "estimated_calories": selected_food["calories"],
        "confidence": 0.85
    }

def generate_glucose_prediction(user_id):
    """
    AI-powered glucose level prediction based on recent data
    """
    # Get recent data for the user
    recent_readings = BloodSugarReading.query.filter_by(user_id=user_id)\
        .order_by(BloodSugarReading.timestamp.desc()).limit(10).all()
    
    recent_meals = MealEntry.query.filter_by(user_id=user_id)\
        .filter(MealEntry.timestamp >= datetime.utcnow() - timedelta(hours=24))\
        .all()
    
    recent_exercise = ExerciseLog.query.filter_by(user_id=user_id)\
        .filter(ExerciseLog.timestamp >= datetime.utcnow() - timedelta(hours=24))\
        .all()
    
    if not recent_readings:
        return None
    
    # Simple prediction algorithm (in production, use ML model)
    recent_glucose_levels = [reading.glucose_level for reading in recent_readings]
    avg_glucose = statistics.mean(recent_glucose_levels)
    
    total_carbs_today = sum(meal.carbs or 0 for meal in recent_meals)
    total_exercise_today = sum(exercise.duration_minutes or 0 for exercise in recent_exercise)
    
    # Basic prediction logic
    predicted_change = 0
    if total_carbs_today > 100:  # High carb intake
        predicted_change += 20
    if total_exercise_today > 30:  # Good exercise
        predicted_change -= 15
    
    predicted_glucose = avg_glucose + predicted_change
    
    return {
        "predicted_level": round(predicted_glucose, 1),
        "confidence": 0.75,
        "factors": {
            "recent_average": round(avg_glucose, 1),
            "carbs_today": total_carbs_today,
            "exercise_minutes": total_exercise_today
        }
    }

def generate_ai_insights(user_id):
    """
    Generate personalized AI insights and alerts
    """
    insights = []
    user = User.query.get(user_id)
    
    # Check recent glucose trends
    recent_readings = BloodSugarReading.query.filter_by(user_id=user_id)\
        .filter(BloodSugarReading.timestamp >= datetime.utcnow() - timedelta(days=7))\
        .order_by(BloodSugarReading.timestamp.desc()).all()
    
    if recent_readings:
        high_readings = [r for r in recent_readings if r.glucose_level > user.target_glucose_max]
        low_readings = [r for r in recent_readings if r.glucose_level < user.target_glucose_min]
        
        if len(high_readings) > len(recent_readings) * 0.3:  # More than 30% high readings
            insights.append({
                "type": "alert",
                "priority": "high",
                "message": f"You've had {len(high_readings)} high glucose readings in the past week. Consider reviewing your meal portions and medication timing with your healthcare provider."
            })
        
        if len(low_readings) > 2:
            insights.append({
                "type": "alert",
                "priority": "medium",
                "message": f"You've experienced {len(low_readings)} low glucose episodes this week. Make sure you're eating regular meals and carrying glucose tablets."
            })
    
    # Exercise recommendations
    recent_exercise = ExerciseLog.query.filter_by(user_id=user_id)\
        .filter(ExerciseLog.timestamp >= datetime.utcnow() - timedelta(days=7))\
        .all()
    
    total_exercise_week = sum(e.duration_minutes or 0 for e in recent_exercise)
    
    if total_exercise_week < 150:  # Less than WHO recommendation
        insights.append({
            "type": "tip",
            "priority": "medium",
            "message": f"You exercised {total_exercise_week} minutes this week. Aim for 150 minutes of moderate activity weekly to improve glucose control."
        })
    
    return insights

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user profile"""
    data = request.json
    
    user = User(
        name=data.get('name'),
        email=data.get('email'),
        age=data.get('age'),
        diabetes_type=data.get('diabetes_type'),
        target_glucose_min=data.get('target_glucose_min', 80),
        target_glucose_max=data.get('target_glucose_max', 180)
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully", "user_id": user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/users/<int:user_id>/blood-sugar', methods=['POST'])
def log_blood_sugar(user_id):
    """Log a blood sugar reading"""
    data = request.json
    
    reading = BloodSugarReading(
        user_id=user_id,
        glucose_level=data.get('glucose_level'),
        measurement_time=data.get('measurement_time'),
        notes=data.get('notes', '')
    )
    
    db.session.add(reading)
    db.session.commit()
    
    # Generate insights after new reading
    insights = generate_ai_insights(user_id)
    for insight in insights:
        ai_insight = AIInsight(
            user_id=user_id,
            insight_type=insight['type'],
            message=insight['message'],
            priority=insight['priority']
        )
        db.session.add(ai_insight)
    
    db.session.commit()
    
    return jsonify({"message": "Blood sugar reading logged successfully", "insights": insights})

@app.route('/api/users/<int:user_id>/meals', methods=['POST'])
def log_meal(user_id):
    """Log a meal entry"""
    data = request.json
    
    meal = MealEntry(
        user_id=user_id,
        meal_name=data.get('meal_name'),
        carbs=data.get('carbs'),
        calories=data.get('calories'),
        meal_type=data.get('meal_type')
    )
    
    db.session.add(meal)
    db.session.commit()
    
    return jsonify({"message": "Meal logged successfully"})

@app.route('/api/users/<int:user_id>/meals/analyze-photo', methods=['POST'])
def analyze_meal_photo_endpoint(user_id):
    """Analyze meal photo for carb and calorie estimation"""
    if 'photo' not in request.files:
        return jsonify({"error": "No photo provided"}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Analyze the photo (using placeholder function)
        analysis = analyze_meal_photo(file_path)
        
        # Create meal entry with AI analysis
        meal = MealEntry(
            user_id=user_id,
            meal_name=analysis['recognized_food'],
            carbs=analysis['estimated_carbs'],
            calories=analysis['estimated_calories'],
            meal_type=request.form.get('meal_type', 'Snack'),
            photo_path=file_path
        )
        
        db.session.add(meal)
        db.session.commit()
        
        return jsonify({
            "message": "Meal photo analyzed successfully",
            "analysis": analysis,
            "meal_id": meal.id
        })

@app.route('/api/users/<int:user_id>/medications', methods=['POST'])
def log_medication(user_id):
    """Log medication intake"""
    data = request.json
    
    medication = MedicationLog(
        user_id=user_id,
        medication_name=data.get('medication_name'),
        dosage=data.get('dosage'),
        taken=data.get('taken', True)
    )
    
    db.session.add(medication)
    db.session.commit()
    
    return jsonify({"message": "Medication logged successfully"})

@app.route('/api/users/<int:user_id>/exercise', methods=['POST'])
def log_exercise(user_id):
    """Log exercise activity"""
    data = request.json
    
    exercise = ExerciseLog(
        user_id=user_id,
        exercise_type=data.get('exercise_type'),
        duration_minutes=data.get('duration_minutes'),
        intensity=data.get('intensity'),
        calories_burned=data.get('calories_burned')
    )
    
    db.session.add(exercise)
    db.session.commit()
    
    return jsonify({"message": "Exercise logged successfully"})

@app.route('/api/users/<int:user_id>/dashboard')
def get_dashboard_data(user_id):
    """Get dashboard data for user"""
    # Recent blood sugar readings
    recent_readings = BloodSugarReading.query.filter_by(user_id=user_id)\
        .order_by(BloodSugarReading.timestamp.desc()).limit(10).all()
    
    # Today's meals
    today = datetime.utcnow().date()
    today_meals = MealEntry.query.filter_by(user_id=user_id)\
        .filter(MealEntry.timestamp >= today).all()
    
    # Recent medications
    recent_medications = MedicationLog.query.filter_by(user_id=user_id)\
        .filter(MedicationLog.taken_at >= today).all()
    
    # AI insights
    unread_insights = AIInsight.query.filter_by(user_id=user_id, read=False)\
        .order_by(AIInsight.timestamp.desc()).all()
    
    # Glucose prediction
    prediction = generate_glucose_prediction(user_id)
    
    return jsonify({
        "recent_readings": [{
            "glucose_level": r.glucose_level,
            "measurement_time": r.measurement_time,
            "timestamp": r.timestamp.isoformat()
        } for r in recent_readings],
        
        "today_meals": [{
            "meal_name": m.meal_name,
            "carbs": m.carbs,
            "calories": m.calories,
            "meal_type": m.meal_type,
            "timestamp": m.timestamp.isoformat()
        } for m in today_meals],
        
        "recent_medications": [{
            "medication_name": m.medication_name,
            "dosage": m.dosage,
            "taken": m.taken,
            "taken_at": m.taken_at.isoformat()
        } for m in recent_medications],
        
        "unread_insights": [{
            "id": i.id,
            "type": i.insight_type,
            "message": i.message,
            "priority": i.priority,
            "timestamp": i.timestamp.isoformat()
        } for i in unread_insights],
        
        "glucose_prediction": prediction
    })

@app.route('/api/users/<int:user_id>/reports')
def generate_report(user_id):
    """Generate comprehensive health report"""
    # Last 30 days data
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    readings = BloodSugarReading.query.filter_by(user_id=user_id)\
        .filter(BloodSugarReading.timestamp >= thirty_days_ago).all()
    
    meals = MealEntry.query.filter_by(user_id=user_id)\
        .filter(MealEntry.timestamp >= thirty_days_ago).all()
    
    exercise = ExerciseLog.query.filter_by(user_id=user_id)\
        .filter(ExerciseLog.timestamp >= thirty_days_ago).all()
    
    medications = MedicationLog.query.filter_by(user_id=user_id)\
        .filter(MedicationLog.taken_at >= thirty_days_ago).all()
    
    user = User.query.get(user_id)
    
    # Calculate statistics
    if readings:
        glucose_levels = [r.glucose_level for r in readings]
        avg_glucose = statistics.mean(glucose_levels)
        glucose_std = statistics.stdev(glucose_levels) if len(glucose_levels) > 1 else 0
        in_range_count = len([g for g in glucose_levels if user.target_glucose_min <= g <= user.target_glucose_max])
        time_in_range = (in_range_count / len(glucose_levels)) * 100
    else:
        avg_glucose = glucose_std = time_in_range = 0
    
    total_exercise_minutes = sum(e.duration_minutes or 0 for e in exercise)
    avg_daily_carbs = statistics.mean([m.carbs for m in meals if m.carbs]) if meals else 0
    
    report = {
        "user_name": user.name,
        "report_period": "Last 30 Days",
        "generated_at": datetime.utcnow().isoformat(),
        
        "glucose_summary": {
            "average_glucose": round(avg_glucose, 1),
            "glucose_variability": round(glucose_std, 1),
            "time_in_range_percent": round(time_in_range, 1),
            "total_readings": len(readings)
        },
        
        "lifestyle_summary": {
            "total_exercise_minutes": total_exercise_minutes,
            "exercise_sessions": len(exercise),
            "average_daily_carbs": round(avg_daily_carbs, 1),
            "meals_logged": len(meals),
            "medications_taken": len([m for m in medications if m.taken])
        },
        
        "recommendations": [
            "Continue regular glucose monitoring for better diabetes management",
            "Maintain consistent meal timing to stabilize blood sugar levels",
            "Consider increasing exercise frequency if below 150 minutes per week",
            "Share this report with your healthcare provider during your next appointment"
        ]
    }
    
    return jsonify(report)

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)