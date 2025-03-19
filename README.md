# ZenSports ERP

A comprehensive Enterprise Resource Planning (ERP) system for sports equipment retailers, built with Django.

## Features

### Inventory Management
- **Product Management**: Add, edit, and delete products with details like name, description, price, and stock level
- **Category Management**: Organize products by categories
- **Stock Alerts**: Automatic alerts for low stock items based on reorder levels
- **Stock Reports**: Generate detailed reports on current inventory status

### Customer Management
- **Customer Database**: Store and manage customer information
- **Customer History**: Track purchase history for each customer
- **Contact Details**: Maintain comprehensive contact information

### Billing System
- **Invoice Generation**: Create professional invoices for customers
- **PDF Generation**: Export invoices as PDFs for printing or sharing
- **Payment Tracking**: Monitor invoice payment status (Paid/Pending)
- **Due Date Calculation**: Automatic 30-day due date from billing date

### Dashboard
- **Overview**: Quick summary of key business metrics
- **Recent Activities**: View recent invoices, products, and customers
- **Low Stock Alerts**: Highlighted warnings for items needing restock

## Installation

### Prerequisites
- Python 3.8+
- Django 5.1+
- Pip (Python package manager)

### Setup
1. Clone the repository:
   ```
   git clone <repository-url>
   cd zensports
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Navigate to the project directory:
   ```
   cd erp
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

8. Access the application at http://127.0.0.1:8000/

## Usage

### Inventory Management
- Navigate to the Inventory section to add/edit products and categories
- Set reorder levels for automatic low stock alerts
- Use the Stock Report to get a complete overview of your inventory

### Customer Management
- Add new customers with contact details and shipping information
- View customer purchase history
- Edit customer information as needed

### Billing
- Create new invoices by selecting a customer and adding products
- View all invoices in the invoice list
- Update payment status as payments are received
- Print or download invoices as PDFs

### Dashboard
- Get a quick overview of your business at login
- See recent invoices, customers, and products
- Identify low stock items that need attention

## Security Features
- User authentication and authorization
- Login required for all operations
- Session management and timeout

## Development

### Project Structure
- `erp/` - Main project directory
  - `billing/` - Invoice and payment handling
  - `customers/` - Customer management
  - `inventory/` - Product and stock management
  - `templates/` - HTML templates
  - `static/` - CSS, JavaScript, and images

### Technology Stack
- **Backend**: Django
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: SQLite (default), easily configurable for PostgreSQL or MySQL
- **PDF Generation**: ReportLab

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support or questions, please contact [support@zensports.com](mailto:support@zensports.com). 