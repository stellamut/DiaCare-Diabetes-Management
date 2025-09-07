# 🩺 Diabetes Management App

An AI-powered web application for tracking and managing diabetes, aligned with UN SDG 3 (Good Health & Well-being).

## Features

* **Daily Glucose Tracking**: Log blood sugar levels with meal, activity, and medication notes
* **AI-Powered Insights**: Get personalized trend analysis and health recommendations
* **Visual Analytics**: Interactive charts showing glucose patterns over time
* **Target Range Monitoring**: Track compliance with personalized glucose targets
* **Secure Authentication**: User registration and login system
* **Mobile-Friendly**: Responsive design optimized for mobile devices

## Tech Stack

* **Backend**: Python Flask, SQLAlchemy
* **Frontend**: HTML5, CSS3, JavaScript, Chart.js
* **Database**: SQLite (development), easily upgradeable to PostgreSQL/MySQL
* **AI Integration**: Built-in trend analysis with Hugging Face API support
* **Styling**: Custom CSS with Garamond font family and grey color scheme

## Quick Start

### Prerequisites

* Python 3.7+
* pip (Python package installer)

### Installation

1. **Clone the repository**
  
      git clone <repository-url>
      cd diabetes-management-app
  
2. **Install dependencies**
  
      pip install flask flask-sqlalchemy werkzeug requests
  
3. **Run the application**
  
      python app.py
  
4. **Open your browser**Navigate to `http://localhost:5000`
  

## Project Structure

    diabetes-management-app/
    ├── app.py                 # Main Flask application
    ├── templates/
    │   ├── index.html        # Landing page
    │   └── dashboard.html    # Main dashboard
    ├── static/
    │   ├── css/
    │   └── js/
    ├── diabetes_tracker.db   # SQLite database (created automatically)
    └── README.md

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/register` | User registration |
| POST | `/login` | User authentication |
| POST | `/logout` | User logout |
| POST | `/log` | Log glucose reading |
| GET | `/history` | Get reading history |
| GET | `/analyze` | Get AI insights |
| GET | `/profile` | Get user profile |
| PUT | `/profile` | Update user profile |

## Usage

### Registration & Login

1. Create an account with name, email, and password
2. Login to access your personal dashboard

### Logging Glucose Readings

1. Enter glucose level (20-600 mg/dL)
2. Select reading type (fasting, post-meal, etc.)
3. Add optional notes for meals, activities, and medications
4. Click "Log Reading" to save

### Viewing Analytics

* **Dashboard Stats**: View average glucose, total readings, and compliance rate
* **Trend Chart**: Interactive 7-day glucose level visualization
* **AI Insights**: Get personalized recommendations based on your patterns
* **Recent Readings**: Quick view of your latest entries

## Data Validation

* Glucose levels must be between 20-600 mg/dL
* Email addresses are validated for proper format
* Passwords must be at least 6 characters
* All user inputs are sanitized to prevent security issues

## AI Features

The app includes built-in trend analysis that:

* Calculates average glucose levels and trends
* Identifies increasing/decreasing patterns
* Detects high and low reading clusters
* Provides personalized health insights
* Calculates target range compliance

## Monetization Strategy

**Free Tier:**

* Basic glucose logging
* Simple charts and statistics
* Basic AI insights

**Premium Tier (Future):**

* Advanced analytics and predictions
* Downloadable health reports
* Doctor dashboard sharing
* Medication reminders
* Integration with wearable devices

**Payment Integration:**

* M-Pesa (Kenya/Africa)
* InterSwitch (Nigeria)
* PayPal (Global)
* Visa/Mastercard

## Security Features

* Password hashing with Werkzeug
* Session-based authentication
* Input validation and sanitization
* SQL injection protection via SQLAlchemy ORM
* CSRF protection ready for production

## Deployment

### Development

The app runs with Flask's built-in server on `localhost:5000`

### Production Deployment Options

1. **Heroku**: Easy deployment with PostgreSQL addon
2. **DigitalOcean**: VPS with Gunicorn + Nginx
3. **AWS**: EC2 with RDS database
4. **Google Cloud**: App Engine deployment

### Environment Variables (Production)

    SECRET_KEY=your-production-secret-key
    DATABASE_URL=your-production-database-url
    HUGGINGFACE_API_KEY=your-hf-api-key (optional)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## Health Disclaimer

This application is for informational purposes only and should not replace professional medical advice. Always consult with healthcare providers for medical decisions and diabetes management.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

**Built with ❤️ for better diabetes management and SDG 3: Good Health & Well-being**
