# Flask E-commerce Application
## Project Overview

This robust e-commerce platform is built using Flask, SQLAlchemy, and PostgreSQL, offering a seamless shopping experience with secure user management, product handling, and integrated payment processing.

🌐 [Live Demo](https://flask-ecommerce-769r.onrender.com/)

## Key Features
### User Management

- 📝 User registration with email verification
- 🔐 Secure authentication system
- 🔑 Password reset functionality
- 📧 Automated welcome emails for new users
- 👤 Profile management and updates


### Product Handling

- 🛍️ Add products with images, titles, descriptions, and prices
- 🔄 Update and delete product listings
- 🔍 Powerful product search functionality


### Payment Processing

- 💳 Seamless Stripe integration for secure payments
- 💾 Save payment methods for future transactions

### Order Management

- 🛒 Automatic order placement post-payment
- 📊 User dashboard for order tracking

## Technology Stack

- **Backend:** Flask, SQLAlchemy
- **Database:** PostgreSQL
- **Payment:** Stripe API
- **Deployment:** Rende


## Getting Started
### Prerequisites

- Python 3.8+
- PostgreSQL
- Stripe account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/farad-alam/Flask-Ecommerce.git
```


2. Install dependencies:
```bash
pip install -r requirements.txt
```


3. Set up environment variables:
```bash
SECRET_KEY=SECRET_KEY
SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS=False
MAIL_SERVER=smtp.googlemail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=MAIL_USERNAME
MAIL_PASSWORD=MAIL_PASSWORD
STRIPE_SECRET_KEY=STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=STRIPE_PUBLISHABLE_KEY
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the application:
```bash
flask run
```