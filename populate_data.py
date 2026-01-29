# populate_data.py

import os
import django
from datetime import date # Πρόσθεσε την import για το date

# Ρύθμιση των Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')

# Αρχικοποίηση του Django
django.setup()

# Τώρα μπορείτε να εισάγετε τα μοντέλα σας
from core.models import Customer, Product

print("Ξεκινάει η εισαγωγή δοκιμαστικών δεδομένων...")

# --- Δημιουργία Δοκιμαστικών Πελατών ---
customers_data = [
    {
        'first_name': 'Γιώργος', 'last_name': 'Παπαδόπουλος', 'company_name': 'Παπαδόπουλος Α.Ε.',
        'phone': '2101234567', 'email': 'g.papadopoulos@example.com', 'address': 'Οδός Α 123',
        'city': 'Αθήνα', 'postal_code': '10555', 'vat_number': '123456789', 'doy': 'ΔΟΥ Α Αθηνών',
        'payment_method': 'bank_transfer', 'payment_terms': 'net_30', 'credit_limit': 5000.00,
        'balance': 1500.00, 'comments': 'Σημαντικός πελάτης.', 'shipping_address': 'Οδός Β 45',
        'shipping_city': 'Πειραιάς', 'shipping_postal_code': '18531',
        'contact_person_name': 'Μαρία Παπαδοπούλου', 'contact_person_phone': '2107654321',
        'contact_person_email': 'm.papadopoulou@example.com'
    },
    {
        'first_name': 'Ελένη', 'last_name': 'Βασιλείου', 'company_name': 'Βασιλείου & ΣΙΑ',
        'phone': '2310987654', 'email': 'e.vasileiou@example.com', 'address': 'Λεωφόρος Κ 45',
        'city': 'Θεσσαλονίκη', 'postal_code': '54621', 'vat_number': '987654321', 'doy': 'ΔΟΥ Δ Θεσσαλονίκης',
        'payment_method': 'credit_card', 'payment_terms': 'due_on_receipt', 'credit_limit': 2000.00,
        'balance': -500.00,
    },
    {
        'first_name': 'Νίκος', 'last_name': 'Γεωργίου', 'company_name': '',
        'phone': '6901122333', 'email': 'n.georgiou@example.com', 'address': 'Πλατεία Λ 7',
        'city': 'Πάτρα', 'postal_code': '26221', 'vat_number': '112233445', 'doy': 'ΔΟΥ Πατρών',
        'payment_method': 'cash', 'payment_terms': 'net_15', 'credit_limit': 0.00,
    },
]

print("Δημιουργία πελατών...")
for data in customers_data:
    try:
        customer_exists = False
        if data.get('phone'):
            customer_exists = customer_exists or Customer.objects.filter(phone=data.get('phone')).exists()
        if data.get('email'):
             customer_exists = customer_exists or Customer.objects.filter(email=data.get('email')).exists()
        
        if not customer_exists:
            customer = Customer.objects.create(**data)
            print(f"Δημιουργήθηκε πελάτης: {customer}")
        else:
            print(f"Ο πελάτης με τηλέφωνο/email {data.get('phone')}/{data.get('email')} υπάρχει ήδη. Παράλειψη.")
    except Exception as e:
        print(f"Σφάλμα κατά τη δημιουργία πελάτη {data.get('first_name')} {data.get('last_name')}: {e}")


print("\n--- Δημιουργία Δοκιμαστικών Προϊόντων ---")
products_data = [
    {
        'name': 'Laptop Model X', 'description': 'Ισχυρός φορητός υπολογιστής', 'code': 'LP001',
        'price': 850.00, 'cost_price': 700.00, 'stock_quantity': 15, 'unit_of_measurement': 'pcs',
        'barcode': '1234567890128', 'batch_number': 'LTX-2023-Batch-A', 'expiry_date': date(2025, 12, 31)
    },
    {
        'name': 'Οθόνη 27 ιντσών', 'description': 'Οθόνη Full HD για υπολογιστή', 'code': 'SC001',
        'price': 200.00, 'cost_price': 150.00, 'stock_quantity': 30, 'unit_of_measurement': 'pcs',
        'barcode': '9876543210987', # Δεν έχει ημερομηνία λήξης ή παρτίδα αυτό
    },
    {
        'name': 'Εκτυπωτής Laser', 'description': 'Ασπρόμαυρος εκτυπωτής laser', 'code': 'PR001',
        'price': 150.00, 'cost_price': 100.00, 'stock_quantity': 10, 'unit_of_measurement': 'pcs',
        'barcode': '4567890123456', 'batch_number': 'PR-2024-01',
    },
    {
        'name': 'Χαρτί Α4 (Πακέτο 500)', 'description': 'Πακέτο χαρτί γραφείου Α4', 'code': 'PA001',
        'price': 5.50, 'cost_price': 3.00, 'stock_quantity': 100, 'unit_of_measurement': 'box',
        'barcode': '1122334455667',
    },
    {
        'name': 'Καλώδιο HDMI (2 μέτρα)', 'description': 'Καλώδιο HDMI υψηλής ποιότητας', 'code': 'CB001',
        'price': 10.00, 'cost_price': 5.00, 'stock_quantity': 50, 'unit_of_measurement': 'pcs',
        'expiry_date': None # Αυτό δεν έχει ημερομηνία λήξης
    },
    {
        'name': 'Γιαούρτι Στραγγιστό 2%', 'description': 'Γιαούρτι με χαμηλά λιπαρά', 'code': 'YG001',
        'price': 1.20, 'cost_price': 0.70, 'stock_quantity': 200, 'unit_of_measurement': 'pcs',
        'barcode': '5200000111222', 'batch_number': 'YG-Batch-005', 'expiry_date': date(2025, 6, 15)
    },
]

print("\nΔημιουργία προϊόντων...")
for data_item in products_data: # Άλλαξα το όνομα της μεταβλητής για να μην συγχέεται με το from datetime import date
    try:
        product_exists = False
        if data_item.get('name'):
            product_exists = product_exists or Product.objects.filter(name=data_item.get('name')).exists()
        if data_item.get('barcode'): # Έλεγχος barcode μόνο αν παρέχεται
             product_exists = product_exists or Product.objects.filter(barcode=data_item.get('barcode')).exists()
        
        if not product_exists:
            product = Product.objects.create(**data_item)
            print(f"Δημιουργήθηκε προϊόν: {product.name}")
        else:
             print(f"Το προϊόν με όνομα/barcode {data_item.get('name')}/{data_item.get('barcode')} υπάρχει ήδη. Παράλειψη.")

    except Exception as e:
        print(f"Σφάλμα κατά τη δημιουργία προϊόντος {data_item.get('name')}: {e}")


print("\nΟλοκληρώθηκε η εισαγωγή δοκιμαστικών δεδομένων.")