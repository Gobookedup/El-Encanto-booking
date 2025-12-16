# El Encanto Barbershop – Host Ready

## Local run
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

## Render settings
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app

Set Environment Variables on Render:
- SECRET_KEY=your-long-random-string
- ADMIN_USER=admin
- ADMIN_PASS=your-strong-password
- DEPOSIT_AMOUNT=10
