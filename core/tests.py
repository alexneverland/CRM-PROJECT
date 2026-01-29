# core/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
import datetime

# Εισάγουμε τα μοντέλα και τις φόρμες που θέλουμε να ελέγξουμε
from .models import Customer, Product, Invoice, Order, OrderItem
from .forms import OrderItemForm

User = get_user_model()


class CustomerModelTests(TestCase):
    """
    Μια κλάση που ομαδοποιεί tests για το Customer.
    (Αυτό είναι το test που είχες ήδη).
    """
    def test_customer_str_representation(self):
        customer1 = Customer.objects.create(
            first_name="Γιάννης",
            last_name="Παπαδόπουλος",
            company_name=""
        )
        customer2 = Customer.objects.create(
            first_name="Μαρία",
            last_name="Ιωάννου",
            company_name="Μαρία Ιωάννου Ο.Ε."
        )
        self.assertEqual(str(customer1), "Γιάννης Παπαδόπουλος")
        self.assertEqual(str(customer2), "Μαρία Ιωάννου Ο.Ε.")


class CoreFunctionalityTests(TestCase):
    """
    Μια νέα σουίτα από tests για τις βασικές λειτουργίες της εφαρμογής.
    """
    def setUp(self):
        """
        Αυτή η μέθοδος εκτελείται ΠΡΙΝ από κάθε test function.
        Είναι ιδανική για να δημιουργήσουμε δεδομένα που θα χρησιμοποιήσουμε σε πολλά tests.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.customer = Customer.objects.create(
            first_name="Δοκιμαστικός",
            last_name="Πελάτης",
            code="TEST01"
        )
        self.product = Product.objects.create(
            name="Test Product",
            code="TP01",
            price=Decimal("100.00"),
            stock_quantity=Decimal("20.00")
        )

    def test_create_customer_end_to_end(self):
        """
        Ελέγχει ολόκληρη τη ροή δημιουργίας ενός νέου πελάτη,
        από την υποβολή της φόρμας μέχρι την αποθήκευση στη βάση.
        """
        # Βήμα 1: Συνδέουμε τον χρήστη μας
        self.client.login(username='testuser', password='password123')
        
        # Βήμα 2: Ορίζουμε τα δεδομένα που θα στέλναμε μέσω της φόρμας
        customer_data = {
            'first_name': 'Αννα',
            'last_name': 'Δοκιμή',
            'company_name': 'Αννα Δοκιμή Α.Ε.',
            'email': 'anna@example.com',
            'phone': '2109876543',
            'address': 'Οδός Δοκιμής 123',
            'city': 'Αθήνα',
            'postal_code': '12345',
            'vat_number': '123456789',
            'doy': 'ΔΟΥ Αθηνών',
            'payment_method': 'bank_transfer',
            'payment_terms': 'net_30',
            'is_branch': False,
            'can_be_invoiced': True,
            'credit_limit': Decimal('0.00') # <-- Η ΠΡΟΣΘΗΚΗ ΠΟΥ ΛΥΝΕΙ ΤΟ ΠΡΟΒΛΗΜΑ
        }
        
        # Βήμα 3: Προσομοιώνουμε την υποβολή της φόρμας (POST request)
        response = self.client.post(reverse('customer_create'), data=customer_data)
       
        
        # Βήμα 4: Κάνουμε τους ελέγχους μας
        
        # Έλεγχος 4.1: Επιβεβαιώνουμε ότι δημιουργήθηκε ένας νέος πελάτης στη βάση.
        # (Είχαμε 1 από το setUp, τώρα πρέπει να έχουμε 2)
        self.assertEqual(Customer.objects.count(), 2)
        
        # Παίρνουμε τον νέο πελάτη που δημιουργήθηκε
        new_customer = Customer.objects.get(email='anna@example.com')
        
        # Έλεγχος 4.2: Τα στοιχεία του είναι σωστά;
        self.assertEqual(new_customer.first_name, 'Αννα')
        self.assertEqual(new_customer.company_name, 'Αννα Δοκιμή Α.Ε.')
        
        # Έλεγχος 4.3: Το signal έτρεξε και του έδωσε κωδικό;
        self.assertIsNotNone(new_customer.code)
        
        # Έλεγχος 4.4: Η σελίδα μας έκανε redirect στη σελίδα λεπτομερειών του νέου πελάτη;
        self.assertRedirects(response, reverse('customer_detail', kwargs={'pk': new_customer.pk}))        

    # --- Test για Μοντέλο (Model) ---
    def test_invoice_properties(self):
        """
        Ελέγχει αν οι properties 'outstanding_amount' και 'is_overdue' του Invoice λειτουργούν σωστά.
        """
        invoice = Invoice.objects.create(
            customer=self.customer,
            status=Invoice.STATUS_ISSUED,  # <-- Η ΠΡΟΣΘΗΚΗ ΠΟΥ ΛΥΝΕΙ ΤΟ ΠΡΟΒΛΗΜΑ
            total_amount=Decimal("124.00"),
            paid_amount=Decimal("50.00"),
            issue_date=datetime.date.today(),
            due_date=datetime.date.today() - datetime.timedelta(days=5) # Έληξε πριν 5 μέρες
        )
        # Έλεγχος 1: Το ανεξόφλητο ποσό είναι σωστό;
        self.assertEqual(invoice.outstanding_amount, Decimal("74.00"))
        
        # Έλεγχος 2: Το τιμολόγιο είναι όντως ληξιπρόθεσμο;
        self.assertTrue(invoice.is_overdue)

    # --- Test για Φόρμα (Form) ---
    def test_order_item_form_insufficient_stock(self):
        """
        Ελέγχει αν η OrderItemForm αποτυγχάνει σωστά όταν η ζητούμενη ποσότητα
        υπερβαίνει το διαθέσιμο απόθεμα.
        """
        form_data = {
            'product': self.product.pk,
            'quantity': Decimal("25.00"), # Ζητάμε 25, ενώ έχουμε 20
            'unit_price': self.product.price
        }
        form = OrderItemForm(data=form_data)
        
        # Έλεγχος 1: Η φόρμα ΔΕΝ πρέπει να είναι έγκυρη (is_valid() == False)
        self.assertFalse(form.is_valid())
        
        # Έλεγχος 2: Το σφάλμα πρέπει να είναι στο πεδίο 'quantity'
        self.assertIn('quantity', form.errors)
        self.assertIn('Δεν υπάρχει επαρκές απόθεμα', form.errors['quantity'][0])

    # --- Tests για View ---
    def test_customer_list_view_requires_login(self):
        """
        Ελέγχει αν η σελίδα της λίστας πελατών απαιτεί σύνδεση.
        """
        response = self.client.get(reverse('customer_list'))
        
        # Έλεγχος 1: Ο μη-συνδεδεμένος χρήστης πρέπει να κάνει redirect (status code 302)
        self.assertEqual(response.status_code, 302)
        
        # Έλεγχος 2: Η ανακατεύθυνση πρέπει να οδηγεί στη σελίδα login
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('customer_list')}")

    def test_customer_list_view_authenticated(self):
        """
        Ελέγχει αν η λίστα πελατών εμφανίζεται σωστά για έναν συνδεδεμένο χρήστη.
        """
        # Συνδέουμε τον test user που φτιάξαμε στο setUp
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('customer_list'))
        
        # Έλεγχος 1: Η σελίδα πρέπει να φορτώνει επιτυχώς (status code 200)
        self.assertEqual(response.status_code, 200)
        
        # Έλεγχος 2: Το όνομα του πελάτη μας πρέπει να υπάρχει μέσα στο HTML της σελίδας
        self.assertContains(response, self.customer.get_full_name())
        
        # Έλεγχος 3: Το σωστό template πρέπει να χρησιμοποιείται
        self.assertTemplateUsed(response, 'core/customers_list.html')
        
    # --- Test για Signal ---
    def test_customer_code_auto_generation_signal(self):
        """
        Ελέγχει αν το signal που δημιουργεί αυτόματα κωδικό πελάτη λειτουργεί.
        """
        # Δημιουργούμε έναν πελάτη ΧΩΡΙΣ να του δώσουμε κωδικό
        new_customer = Customer.objects.create(
            first_name="Άλλος",
            last_name="Πελάτης"
        )
        
        # O Django ανακτά το αντικείμενο από τη βάση για να είμαστε σίγουροι ότι έχει τις τελευταίες αλλαγές
        new_customer.refresh_from_db()

        # Έλεγχος: Ο κωδικός ΔΕΝ πρέπει να είναι κενός
        self.assertIsNotNone(new_customer.code)
        self.assertNotEqual(new_customer.code, "")