# Pulau Harapan Tourism Management Application 🌴🏝️

A comprehensive, full-stack management application for Pulau Harapan's tourism ecosystem. This platform handles everything from destination management and tour guide bookings to automated ticketing and real-time analytics.

## ✨ Features

- **Multi-Role RBAC System**: 9 distinct roles including Super Admin, Area Manager, Operator, UMKM, and more.
- **Smart Booking**: Integrated booking system with QRIS payment simulation and automated e-ticket generation.
- **Camping Equipment Rental**: Specialized rental management for island adventures.
- **Tour Guide Marketplace**: Browse and book "Temen Main" (local guides) with rating systems.
- **Dynamic CMS**: Manage landing page content, news, and events in real-time.
- **Advanced Analytics**: Visual dashboards using Chart.js to track visitor trends and revenue.
- **Automated CI/CD**: High code quality with Pylint (10/10) and comprehensive Pytest suite.

## 🛠️ Tech Stack

- **Frontend**: Flask (Python), Jinja2, Vanilla CSS, JavaScript (Firebase Auth).
- **Backend API**: FastAPI, SQLAlchemy (SQLite), Pydantic.
- **Automation**: Github Actions (Pylint, Pytest, Smoke Tests).
- **Deployment**: Render.com Blueprint support.

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- `pip` or `conda`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/zrdimr/wetouree.git
   cd pulau_harapan_tourism
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Seed the database:
   ```bash
   python seed_db.py
   ```
5. Start the application:
   ```bash
   ./start_app.sh
   # Or manually:
   # uvicorn backend.main:app --port 8000 &
   # python frontend/app.py
   ```

## 🧪 Testing

Run the automated test suite with:
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```

## 🌐 Deployment (Render.com)

The project includes a `render.yaml` blueprint.
1. Connect your repository to Render.
2. Render will automatically detect the settings and deploy the stack.
3. Ensure you set the `SECRET_KEY` environment variable in the dashboard.

## 📈 Code Quality

We maintain a strict **10.00/10** Pylint score. To check quality locally:
```bash
export PYTHONPATH=$PYTHONPATH:.
pylint --rcfile=.pylintrc backend/ frontend/ seed_db.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
