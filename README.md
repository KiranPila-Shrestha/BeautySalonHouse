# BeautySalonHouse
BeautySalonHouse simplifies salon management by offering tools for appointments, staff management, inventory, payments, and analytics, ensuring efficiency for owners and clients alike.

## Features of BeautySalonHouse:
1. Booking Appointment: CLient can schedule appointment for various services and choose date and staff and book appointment and respective staff can approve or reject these requests.
2. Product Search: Customer can search product on the basis of category and product name.
3. Billing Mangement: The platform provides an integrated billing system for tracking payments.
4. Cash on Delivery: Customer can choose cash on delivery while checkout and it is track by admin who will notify complete or cancel order.
5. Stylist Management: Salon owners can manage their team of stylists, including adding new staff, performance tracking, and payroll management.
6. Inventory Management: Keep track of salon inventory, including beauty products, equipment, and supplies.
7. Customer Profiles: Maintain profiles for clients, including appointment history, payment history and personal information.
8. Analytics Dashboard: Detailed analytics and reporting tools to track salon performance, customer.
9. Feedback and Reviews: Clients can provide feedback and reviews on services, stylists, and overall salon experience.
10. Reward: loyal customer can rewards points.

## Installation
To run the Beautysalon locally, follow below steps:

1. Install Python
Install python-3.7.2 and python-pip. Follow the steps from the below reference document based on your Operating System. Reference: https://docs.python-guide.org/starting/installation/

2. Setup virtual environment

  Install Virtual environment
   py -m venv .venv_

   Activate the venv
   .\venv_\scripts\activate

3. Clone git repository

git clone "https://github.com/KiranPila-Shrestha/BeautySalonHouse"

4. Install requirements

    cd BeautySalonHouse/
    pip install -r requirements.txt


6. Run the server

  #### Make migrations
  -python manage.py makemigrations
  -python manage.py migrate


  # Run the server
  python manage.py runserver 8000 
# for payment due to server error
 python manage.py runserver 9999
