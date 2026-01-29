# core/models.py
from django.db import models, transaction
from django.utils import timezone
import unicodedata
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Sum
from decimal import Decimal 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# --- Συνάρτηση Κανονικοποίησης Κειμένου για Αναζήτηση ---
def normalize_for_search(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn').lower()

# --- Επιλογές για τη Μονάδα Μέτρησης ---
UNIT_CHOICES = [('pcs', 'Τεμάχια'), ('kg', 'Κιλά'), ('meter', 'Μέτρα'), ('liter', 'Λίτρα'), ('box', 'Κιβώτια'), ('other', 'Άλλο')]

# --- Επιλογές για τον Τρόπο Πληρωμής (για το Customer) ---
PAYMENT_METHOD_CHOICES = [('cash', 'Μετρητά'), ('bank_transfer', 'Κατάθεση σε Τράπεζα'), ('credit_card', 'Πιστωτική/Χρεωστική Κάρτα'), ('cheque', 'Επιταγή'), ('other', 'Άλλο')]

# --- Επιλογές για τους Όρους Πληρωμής (για το Customer) ---
PAYMENT_TERMS_CHOICES = [('due_on_receipt', 'Άμεση Εξόφληση'), ('net_15', 'Επί Πιστώσει 15 Ημερών'), ('net_30', 'Επί Πιστώσει 30 Ημερών'), ('net_60', 'Επί Πιστώσει 60 Ημερών'), ('eom', 'Τέλος Μηνός'), ('other', 'Άλλο')]

class Purpose(models.TextChoices):
    SALE = 'SALE', 'Πώληση'
    SAMPLE = 'SAMPLE', 'Δειγματισμός'
    REPAIR = 'REPAIR', 'Προς Επισκευή'
    RETURN = 'RETURN', 'Επιστροφή'
    INTERNAL = 'INTERNAL', 'Εσωτερική Διακίνηση'
    OTHER = 'OTHER', 'Άλλο'

class SalesRepresentative(models.Model):
    class RepType(models.TextChoices):
        SALESPERSON = 'SALES', 'Εσωτερικός Πωλητής'
        AGENT = 'AGENT', 'Εξωτερικός Αντιπρόσωπος'

    rep_type = models.CharField(
        "Τύπος",
        max_length=10,
        choices=RepType.choices,
        default=RepType.SALESPERSON
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Λογαριασμός Χρήστη")
    phone = models.CharField("Τηλέφωνο", max_length=20, blank=True, null=True)
    commission_rate = models.DecimalField("Ποσοστό Προμήθειας (%)", max_digits=5, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = "Αντιπρόσωπος/Πωλητής"
        verbose_name_plural = "Αντιπρόσωποι/Πωλητές"
        ordering = ['user__username']

    def __str__(self):
        return self.user.get_full_name() or self.user.username
class Customer(models.Model):
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='branches', 
        verbose_name="Κεντρικό Κατάστημα",
        help_text="Επιλέξτε αν αυτός ο πελάτης είναι υποκατάστημα ενός άλλου."
    )
    is_branch = models.BooleanField("Είναι Υποκατάστημα;", default=False)
    can_be_invoiced = models.BooleanField("Δυνατότητα Τιμολόγησης", default=True, help_text="Απο-επιλέξτε το για υποκαταστήματα που δέχονται μόνο Δελτία Αποστολής.")
    
    code = models.CharField("Κωδικός", max_length=100, unique=True, blank=True)
    first_name = models.CharField("Όνομα", max_length=100)
    last_name = models.CharField("Επώνυμο", max_length=100)
    company_name = models.CharField("Επωνυμία Εταιρείας", max_length=200, blank=True, null=True)
    sales_rep = models.ForeignKey(
        SalesRepresentative, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Υπεύθυνος Πωλητής/Αντιπρόσωπος",
        related_name='customers'
    )
    first_name_normalized = models.CharField(max_length=100, editable=False, db_index=True, blank=True)
    last_name_normalized = models.CharField(max_length=100, editable=False, db_index=True, blank=True)
    company_name_normalized = models.CharField(max_length=200, editable=False, db_index=True, blank=True)   
    email = models.EmailField("Email", blank=True, null=True)
    phone = models.CharField("Τηλέφωνο", max_length=20, blank=True, null=True)
    address = models.CharField("Διεύθυνση", max_length=200, blank=True, null=True)
    city = models.CharField("Πόλη", max_length=100, blank=True, null=True)
    postal_code = models.CharField("Ταχ. Κώδικας", max_length=10, blank=True, null=True)
    vat_number = models.CharField("Α.Φ.Μ.", max_length=15, blank=True, null=True)
    doy = models.CharField("Δ.Ο.Υ.", max_length=100, blank=True, null=True)
    
    # --- ΤΑ ΠΕΔΙΑ SHIPPING ΑΦΑΙΡΟΥΝΤΑΙ ΑΠΟ ΕΔΩ ---
    
    contact_person_name = models.CharField("Όνομα Επικοινωνίας", max_length=100, blank=True, null=True)
    contact_person_phone = models.CharField("Τηλ. Επικοινωνίας", max_length=20, blank=True, null=True)
    contact_person_email = models.EmailField("Email Επικοινωνίας", blank=True, null=True)
    payment_method = models.CharField("Τρόπος Πληρωμής", max_length=50, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    payment_terms = models.CharField("Όροι Πληρωμής", max_length=50, choices=PAYMENT_TERMS_CHOICES, default='net_30')
    credit_limit = models.DecimalField("Πιστωτικό Όριο (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    balance = models.DecimalField("Υπόλοιπο (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    comments = models.TextField("Σχόλια", blank=True, null=True)
    created_at = models.DateTimeField("Ημερομηνία Δημιουργίας", auto_now_add=True)
    updated_at = models.DateTimeField("Τελευταία Ενημέρωση", auto_now=True)

    class Meta:
        verbose_name = "Πελάτης"
        verbose_name_plural = "Πελάτες"
        ordering = ['company_name', 'last_name', 'first_name']

    def __str__(self):
        # --- ΒΕΛΤΙΩΣΗ ΓΙΑ ΝΑ ΔΕΙΧΝΕΙ ΤΟ ΥΠΟΚΑΤΑΣΤΗΜΑ ---
        if self.is_branch and self.parent:
            # π.χ. "ΑΒ ΓΕΩΡΓΙΑΔΗΣ (Υποκατάστημα: Θεσσαλονίκη)"
            return f"{self.parent.company_name or self.parent.get_full_name()} ({self.company_name or self.get_full_name()})"
        return self.company_name or self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        self.first_name_normalized = normalize_for_search(self.first_name)
        self.last_name_normalized = normalize_for_search(self.last_name)
        self.company_name_normalized = normalize_for_search(self.company_name) if self.company_name else ""
        super().save(*args, **kwargs)
class Supplier(models.Model):
    name = models.CharField("Επωνυμία Προμηθευτή", max_length=200, unique=True)
    name_normalized = models.CharField(max_length=200, editable=False, db_index=True, blank=True)
    
    contact_person = models.CharField("Όνομα Επικοινωνίας", max_length=100, blank=True, null=True)
    phone = models.CharField("Τηλέφωνο", max_length=20, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)
    
    address = models.CharField("Διεύθυνση", max_length=200, blank=True, null=True)
    city = models.CharField("Πόλη", max_length=100, blank=True, null=True)
    postal_code = models.CharField("Ταχ. Κώδικας", max_length=10, blank=True, null=True)
    
    vat_number = models.CharField("Α.Φ.Μ.", max_length=15, blank=True, null=True)
    doy = models.CharField("Δ.Ο.Υ.", max_length=100, blank=True, null=True)
    
    comments = models.TextField("Σχόλια", blank=True, null=True)
    
    created_at = models.DateTimeField("Ημερομηνία Δημιουργίας", auto_now_add=True)
    updated_at = models.DateTimeField("Τελευταία Ενημέρωση", auto_now=True)

    class Meta:
        verbose_name = "Προμηθευτής"
        verbose_name_plural = "Προμηθευτές"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_normalized = normalize_for_search(self.name)
        super().save(*args, **kwargs)        

class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Πρόχειρη'
        ORDERED = 'ORDERED', 'Παραγγέλθηκε'
        PARTIALLY_RECEIVED = 'PARTIALLY_RECEIVED', 'Μερικώς Παραληφθείσα' 
        COMPLETED = 'COMPLETED', 'Ολοκληρωμένη'
        CANCELLED = 'CANCELLED', 'Ακυρωμένη'

    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders', verbose_name="Προμηθευτής")
    po_number = models.CharField("Αρ. Εντολής Αγοράς", max_length=100, unique=True, blank=True, editable=False)
    order_date = models.DateField("Ημερομηνία Παραγγελίας", default=timezone.now)
    expected_delivery_date = models.DateField("Αναμενόμενη Ημερ. Παράδοσης", null=True, blank=True)
    status = models.CharField("Κατάσταση", max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField("Συνολικό Ποσό (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField("Σημειώσεις", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Εντολή Αγοράς"
        verbose_name_plural = "Εντολές Αγοράς"
        ordering = ['-order_date']

    def __str__(self):
        return f"PO {self.po_number} - {self.supplier.name}"


        

class Product(models.Model):
    name = models.CharField("Όνομα Προϊόντος", max_length=200)
    name_normalized = models.CharField("Κανονικοποιημένο Όνομα", max_length=200, blank=True, null=True, db_index=True, editable=False)
    description = models.TextField("Περιγραφή", blank=True, null=True)
    code = models.CharField("Κωδικός Προϊόντος", max_length=100, unique=True, blank=True, null=True)
    barcode = models.CharField("Barcode", max_length=100, blank=True, null=True)
    price = models.DecimalField("Τιμή Πώλησης (€)", max_digits=10, decimal_places=2)
    
    vat_percentage = models.DecimalField("ΦΠΑ (%)", max_digits=5, decimal_places=2, default=Decimal('24.00'))
    cost_price = models.DecimalField("Τιμή Κόστους (€)", max_digits=10, decimal_places=2, blank=True, null=True, default=Decimal('0.00'))
    unit_of_measurement = models.CharField("Μονάδα Μέτρησης", max_length=50, choices=UNIT_CHOICES, default='pcs')
    stock_quantity = models.DecimalField("Ποσότητα στο Απόθεμα", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    min_stock_level = models.DecimalField("Ελάχιστο Όριο Αποθέματος", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    batch_number = models.CharField("Αριθμός Παρτίδας", max_length=100, blank=True, null=True)
    expiry_date = models.DateField("Ημερομηνία Λήξης", null=True, blank=True)
    is_active = models.BooleanField("Ενεργό", default=True)
    created_at = models.DateTimeField("Ημερομηνία Δημιουργίας", auto_now_add=True)
    updated_at = models.DateTimeField("Τελευταία Ενημέρωση", auto_now=True)

    class Meta:
        verbose_name = "Προϊόν"
        verbose_name_plural = "Προϊόντα"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_normalized = normalize_for_search(self.name)
        super().save(*args, **kwargs)
class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items', verbose_name="Εντολή Αγοράς")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Προϊόν")
    quantity = models.DecimalField("Ποσότητα", max_digits=10, decimal_places=2)
    quantity_received = models.DecimalField("Ποσότητα που Παραλήφθηκε", max_digits=10, decimal_places=2, default=Decimal('0.00'))                               
    cost_price = models.DecimalField("Τιμή Κόστους Μονάδας (€)", max_digits=10, decimal_places=2)
    total_cost = models.DecimalField("Συνολικό Κόστος Γραμμής (€)", max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.cost_price
        super().save(*args, **kwargs)
        # Θα προσθέσουμε λογική για ενημέρωση του συνόλου της Εντολής Αγοράς αργότερα

    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ {self.cost_price}€"        
class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    ORDER_STATUS_CHOICES = [(STATUS_PENDING, 'Εκκρεμής'), (STATUS_PROCESSING, 'Σε Επεξεργασία / Προς Αποστολή'), (STATUS_COMPLETED, 'Ολοκληρωμένη'), (STATUS_CANCELLED, 'Ακυρωμένη')]

    customer = models.ForeignKey(Customer, verbose_name="Πελάτης", on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_date = models.DateField("Ημερομηνία Παραγγελίας", default=timezone.now)
    delivery_date = models.DateField("Ημερομηνία Παράδοσης", null=True, blank=True)
    status = models.CharField("Κατάσταση", max_length=50, choices=ORDER_STATUS_CHOICES, default=STATUS_PENDING)
    shipping_name = models.CharField("Όνομα Παραλήπτη", max_length=200, blank=True, null=True)
    shipping_address = models.CharField("Διεύθυνση Αποστολής", max_length=200, blank=True, null=True)
    shipping_city = models.CharField("Πόλη Αποστολής", max_length=100, blank=True, null=True)
    shipping_postal_code = models.CharField("Τ.Κ. Αποστολής", max_length=10, blank=True, null=True)
    purpose = models.CharField("Σκοπός Διακίνησης", max_length=20, choices=Purpose.choices, default=Purpose.SALE, blank=True, null=True)
    carrier = models.CharField("Μεταφορέας", max_length=100, blank=True, null=True)
    license_plate = models.CharField("Αριθμός Κυκλοφορίας Οχήματος", max_length=20, blank=True, null=True)
    total_amount = models.DecimalField("Συνολικό Ποσό (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    comments = models.TextField("Σχόλια Παραγγελίας", blank=True, null=True)
    order_number = models.CharField("Αριθμός Παραγγελίας", max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField("Ημερομηνία Δημιουργίας", auto_now_add=True)
    updated_at = models.DateTimeField("Τελευταία Ενημέρωση", auto_now=True)

    _original_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    class Meta:
        verbose_name = "Παραγγελία"
        verbose_name_plural = "Παραγγελίες"
        ordering = ['-order_date', 'status']

    def __str__(self):
        customer_str = str(self.customer) if self.customer else "[Δεν υπάρχει πελάτης]"
        return f"Παραγγελία {self.order_number if self.order_number else self.pk} - {customer_str} ({self.get_status_display()})"

    def calculate_and_save(self):
        self.total_amount = self.items.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
        self.save(update_fields=['total_amount'])

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        # Το μπλοκ αυτόματης συμπλήρωσης έχει αφαιρεθεί τελείως από εδώ.
        
        super().save(*args, **kwargs)

        if not is_new and self._original_status != self.status and self.status == self.STATUS_CANCELLED:
            for item in self.items.all():
                if item.product:
                    item.product.stock_quantity += item.quantity
                    item.product.save(update_fields=['stock_quantity', 'updated_at'])
        self._original_status = self.status

    def delete(self, *args, **kwargs):
        if self.status != self.STATUS_CANCELLED:
            for item in self.items.all():
                if item.product:
                    item.product.stock_quantity += item.quantity
                    item.product.save(update_fields=['stock_quantity', 'updated_at'])
        super().delete(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name="Παραγγελία", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Προϊόν", on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField("Ποσότητα", max_digits=10, decimal_places=2, default=1)
    is_gift = models.BooleanField("Δώρο", default=False)
    unit_price = models.DecimalField("Τιμή Μονάδας (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_percentage = models.DecimalField("Έκπτωση Είδους (%)", max_digits=5, decimal_places=2, default=Decimal('0.00'))
    vat_percentage = models.DecimalField("ΦΠΑ (%)", max_digits=5, decimal_places=2, default=Decimal('24.00'))
    total_price = models.DecimalField("Συνολική Τιμή Είδους (με ΦΠΑ)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    comments = models.TextField("Σχόλια Είδους", blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_quantity = self.quantity if self.pk else Decimal('0.00')

    class Meta:
        verbose_name = "Είδος Παραγγελίας"
        verbose_name_plural = "Είδη Παραγγελίας"

    def save(self, *args, **kwargs):
        if self.is_gift:
            self.unit_price = Decimal('0.00')
            self.discount_percentage = Decimal('0.00')

        if self.product and not self.is_gift and self.unit_price == Decimal('0.00'):
            self.unit_price = self.product.price
            self.vat_percentage = self.product.vat_percentage

        price_after_discount = self.unit_price * (Decimal('1') - (self.discount_percentage / Decimal('100')))
        price_with_vat = price_after_discount * (Decimal('1') + (self.vat_percentage / Decimal('100')))
        self.total_price = self.quantity * price_with_vat
        
        # --- ΛΟΓΙΚΗ ΑΠΟΘΕΜΑΤΟΣ ---
        if self.product:
            try:
                with transaction.atomic():
                    # Κλειδώνουμε το προϊόν για να αποφύγουμε race conditions
                    product = Product.objects.select_for_update().get(pk=self.product.pk)
                    quantity_diff = self.quantity - self._old_quantity
                    product.stock_quantity -= quantity_diff # Αφαιρούμε τη διαφορά
                    product.save(update_fields=['stock_quantity', 'updated_at'])
            except Product.DoesNotExist:
                # Handle case where product might have been deleted, though PROTECT should prevent this
                pass

        super().save(*args, **kwargs) # Αποθηκεύουμε το OrderItem
        self._old_quantity = self.quantity # Ενημερώνουμε την "παλιά" ποσότητα
        
        if self.order_id:
            transaction.on_commit(self.order.calculate_and_save)        
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'No Product'} in Order {self.order.pk}"

    def delete(self, *args, **kwargs):
        if self.order.status != Order.STATUS_CANCELLED and self.product:
            self.product.stock_quantity += self.quantity
            self.product.save(update_fields=['stock_quantity', 'updated_at'])
        order_to_update = self.order
        super().delete(*args, **kwargs)
        # Re-fetch the order to ensure it exists before trying to update it
        try:
            Order.objects.get(pk=order_to_update.pk).calculate_and_save()
        except Order.DoesNotExist:
            pass        

class DeliveryNote(models.Model):
    class Status(models.TextChoices):
        PREPARING = 'PREPARING', 'Προετοιμάζεται'
        SHIPPED = 'SHIPPED', 'Απεστάλη'
        DELIVERED = 'DELIVERED', 'Παραδόθηκε'
        CANCELLED = 'CANCELLED', 'Ακυρώθηκε'
        
    order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL,
        verbose_name="Σχετική Παραγγελία",
        related_name='delivery_notes',
        null=True, blank=True
    )
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.PROTECT, 
        related_name='delivery_notes', 
        verbose_name="Πελάτης Χρέωσης"
    )
    
    delivery_note_number = models.CharField("Αρ. Δελτίου Αποστολής", max_length=100, unique=True, blank=True, editable=False)
    issue_date = models.DateField("Ημερομηνία Έκδοσης", default=timezone.now)
    status = models.CharField("Κατάσταση", max_length=20, choices=Status.choices, default=Status.PREPARING)
    purpose = models.CharField("Σκοπός Διακίνησης", max_length=20, choices=Purpose.choices, default=Purpose.SALE)

    shipping_name = models.CharField("Όνομα Παραλήπτη", max_length=200, blank=True, null=True)
    shipping_address = models.CharField("Διεύθυνση Αποστολής", max_length=200, blank=True, null=True)
    shipping_city = models.CharField("Πόλη Αποστολής", max_length=100, blank=True, null=True)
    shipping_postal_code = models.CharField("Τ.Κ. Αποστολής", max_length=10, blank=True, null=True)
    shipping_vat_number = models.CharField("ΑΦΜ Παραλήπτη", max_length=15, blank=True, null=True)

    license_plate = models.CharField("Αριθμός Κυκλοφορίας Οχήματος", max_length=20, blank=True, null=True)
    carrier = models.CharField("Μεταφορέας", max_length=100, blank=True, null=True)
    tracking_number = models.CharField("Αριθμός Αποστολής (Tracking)", max_length=100, blank=True, null=True)
    mark = models.CharField("ΜΑΡΚ myDATA", max_length=100, blank=True, null=True, editable=False)
    qr_code_url = models.URLField(" σύνδεσμος QR Code", blank=True, null=True, editable=False)
    notes = models.TextField("Σημειώσεις Δελτίου", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Δελτίο Αποστολής"
        verbose_name_plural = "Δελτία Αποστολής"
        ordering = ['-issue_date', '-delivery_note_number']

    def __str__(self):
        if self.order:
            return f"Δ.Α. {self.delivery_note_number} για Παραγγελία {self.order.order_number}"
        return f"Δ.Α. {self.delivery_note_number} (Αυτόνομο)"


class DeliveryNoteItem(models.Model):
    """
    Αντιπροσωπεύει ένα είδος μέσα σε ένα Δελτίο Αποστολής.
    """
    delivery_note = models.ForeignKey(
        DeliveryNote, 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name="Δελτίο Αποστολής"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, verbose_name="Προϊόν")
    description = models.CharField("Περιγραφή", max_length=255)
    quantity = models.DecimalField("Ποσότητα", max_digits=10, decimal_places=2)
    
    # Μπορείς να προσθέσεις κι άλλα πεδία αν χρειάζεται, π.χ. αριθμό παρτίδας.

    def __str__(self):
        return f"{self.quantity} x {self.description} στο Δ.Α. {self.delivery_note.delivery_note_number}"        





class StockReceipt(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Προϊόν")
    quantity_added = models.DecimalField("Ποσότητα Εισαγωγής", max_digits=10, decimal_places=2)
    date_received = models.DateTimeField("Ημερομηνία & Ώρα Παραλαβής", default=timezone.now)
    purchase_order_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Γραμμή Εντολής Αγοράς")
    notes = models.TextField("Σημειώσεις Παραλαβής", blank=True, null=True)
    user_who_recorded = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Χρήστης Καταχώρησης")

    class Meta:
        verbose_name = "Παραλαβή Αποθέματος"
        verbose_name_plural = "Παραλαβές Αποθεμάτων"
        ordering = ['-date_received']

    def __str__(self):
        return f"Παραλαβή {self.quantity_added} x {self.product.name} @ {self.date_received.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and self.product:
            self.product.stock_quantity += self.quantity_added
            self.product.save(update_fields=['stock_quantity', 'updated_at'])


class ActivityLog(models.Model):
    ACTION_TYPE_CREATE = 'CREATE'
    ACTION_TYPE_UPDATE = 'UPDATE'
    ACTION_TYPE_DELETE = 'DELETE'
    ACTION_TYPE_LOGIN = 'LOGIN'
    ACTION_TYPE_LOGOUT = 'LOGOUT'
    ACTION_TYPE_STATUS_CHANGE = 'STATUS_CHANGE'
    ACTION_TYPE_CHOICES = [(ACTION_TYPE_CREATE, 'Δημιουργία'), (ACTION_TYPE_UPDATE, 'Ενημέρωση'), (ACTION_TYPE_DELETE, 'Διαγραφή'), (ACTION_TYPE_LOGIN, 'Είσοδος Χρήστη'), (ACTION_TYPE_LOGOUT, 'Έξοδος Χρήστη'), (ACTION_TYPE_STATUS_CHANGE, 'Αλλαγή Κατάστασης')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Χρήστης")
    action_time = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία & Ώρα")
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES, verbose_name="Τύπος Ενέργειας")
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Τύπος Αντικειμένου")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID Αντικειμένου")
    linked_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=255, blank=True, verbose_name="Αναπαράσταση Αντικειμένου")
    details = models.TextField(blank=True, verbose_name="Λεπτομέρειες")

    class Meta:
        verbose_name = "Καταγραφή Ενέργειας"
        verbose_name_plural = "Καταγραφές Ενεργειών"
        ordering = ['-action_time']

    def __str__(self):
        user_display = str(self.user) if self.user else 'Σύστημα'
        time_display = self.action_time.strftime('%d/%m/%Y %H:%M')
        if self.object_repr:
            return f"{self.get_action_type_display()} στο '{self.object_repr}' από {user_display} στις {time_display}"
        return f"{self.get_action_type_display()} από {user_display} στις {time_display}"


class Payment(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_CANCELLED = 'cancelled'
    PAYMENT_STATUS_CHOICES = [(STATUS_ACTIVE, 'Ενεργή'), (STATUS_CANCELLED, 'Ακυρωμένη')]
    PAYMENT_METHOD_CHOICES = [('cash', 'Μετρητά'), ('bank_transfer', 'Κατάθεση σε Τράπεζα'), ('credit_card', 'Πιστωτική/Χρεωστική Κάρτα'), ('cheque', 'Επιταγή'), ('online', 'Online Πληρωμή'), ('other', 'Άλλο')]
    
    receipt_number = models.CharField("Αρ. Απόδειξης Συστήματος", max_length=100, unique=True, blank=True, editable=False)
    customer = models.ForeignKey(Customer, verbose_name="Πελάτης", on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey(Order, verbose_name="Συσχετιζόμενη Παραγγελία (παλαιό)", on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    invoices = models.ManyToManyField('Invoice', verbose_name="Συσχετιζόμενα Τιμολόγια", blank=True, related_name='payments')

    payment_date = models.DateField("Ημερομηνία Πληρωμής/Καταχώρησης", default=timezone.now)
    amount_paid = models.DecimalField("Ποσό Πληρωμής (€)", max_digits=10, decimal_places=2)
    payment_method = models.CharField("Τρόπος Πληρωμής", max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cash')
    value_date = models.DateField("Ημερομηνία Λήξης/Value Date", null=True, blank=True)
    reference_number = models.CharField("Εξωτερικός Αρ. Αναφοράς/Παραστατικού", max_length=100, blank=True, null=True)
    notes = models.TextField("Σημειώσεις", blank=True, null=True)
    status = models.CharField("Κατάσταση Πληρωμής", max_length=20, choices=PAYMENT_STATUS_CHOICES, default=STATUS_ACTIVE)
    cancellation_reason = models.TextField("Λόγος Ακύρωσης", blank=True, null=True)
    cancelled_at = models.DateTimeField("Ημερομηνία Ακύρωσης", null=True, blank=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Ακυρώθηκε από", on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_payments')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Καταχωρήθηκε από", on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_payments')
    created_at = models.DateTimeField("Ημερομηνία Δημιουργίας Εγγραφής", auto_now_add=True)
    updated_at = models.DateTimeField("Τελευταία Ενημέρωση Εγγραφής", auto_now=True)

    _original_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk:
            self._original_status = self.status

    class Meta:
        verbose_name = "Πληρωμή"
        verbose_name_plural = "Πληρωμές"
        ordering = ['-payment_date', '-receipt_number']

    def __str__(self):
        status_display = f" ({self.get_status_display()})" if self.status != self.STATUS_ACTIVE else ""
        return f"Πληρωμή {self.receipt_number or '[Μη οριστικοποιημένη]'} ({self.amount_paid}€) από {self.customer.get_full_name()}{status_display} στις {self.payment_date.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        is_new = not self.pk
        with transaction.atomic():
            customer_to_update = self.customer
            balance_changed = False
            if is_new and self.status == self.STATUS_ACTIVE:
                customer_to_update.balance -= self.amount_paid
                balance_changed = True
            elif not is_new and self._original_status != self.status:
                if self.status == self.STATUS_CANCELLED and self._original_status == self.STATUS_ACTIVE:
                    customer_to_update.balance += self.amount_paid
                    balance_changed = True
                elif self.status == self.STATUS_ACTIVE and self._original_status == self.STATUS_CANCELLED:
                    customer_to_update.balance -= self.amount_paid
                    balance_changed = True
            if balance_changed:
                customer_to_update.save(update_fields=['balance', 'updated_at'])
            super().save(*args, **kwargs)
        if self.pk:
            self._original_status = self.status

    def delete(self, *args, **kwargs):
        if self.status == self.STATUS_ACTIVE:
            self.customer.balance += self.amount_paid
            self.customer.save(update_fields=['balance'])
        super().delete(*args, **kwargs)


class Invoice(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_ISSUED = 'issued'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CREDITED = 'credited'

    INVOICE_STATUS_CHOICES = [
        (STATUS_DRAFT, 'Πρόχειρο'),
        (STATUS_ISSUED, 'Εκδόθηκε'), 
        (STATUS_PAID, 'Εξοφλήθηκε'), 
        (STATUS_CANCELLED, 'Ακυρώθηκε'),
        (STATUS_CREDITED, 'Πιστώθηκε'),
    ]
    
    customer = models.ForeignKey(Customer, verbose_name="Πελάτης", on_delete=models.PROTECT, related_name='invoices')
    
    # Το τιμολόγιο μπορεί να προέρχεται είτε από παραγγελία...
    order = models.OneToOneField(Order, verbose_name="Σχετική Παραγγελία", on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice')
    
    # ...είτε από Δελτίο Αποστολής (για τα υποκαταστήματα)
    delivery_note = models.OneToOneField(
        DeliveryNote, 
        on_delete=models.SET_NULL,
        related_name='invoice',
        verbose_name="Σχετικό Δελτίο Αποστολής",
        null=True, blank=True
    )
    mark = models.CharField("ΜΑΡΚ myDATA", max_length=100, blank=True, null=True, editable=False)
    uid = models.CharField("UID myDATA", max_length=100, blank=True, null=True, editable=False)
    qr_code_url = models.URLField(" σύνδεσμος QR Code", blank=True, null=True, editable=False)
    invoice_number = models.CharField("Αριθμός Τιμολογίου", max_length=100, unique=True, blank=True)
    issue_date = models.DateField("Ημερομηνία Έκδοσης", default=timezone.now)
    due_date = models.DateField("Ημερομηνία Λήξης", null=True, blank=True)
    status = models.CharField("Κατάσταση", max_length=20, choices=INVOICE_STATUS_CHOICES, default=STATUS_DRAFT)
    
    subtotal = models.DecimalField("Υποσύνολο (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_percentage = models.DecimalField("Ποσοστό Έκπτωσης (%)", max_digits=5, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField("Ποσό Έκπτωσης (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    vat_amount = models.DecimalField("Συνολικό Ποσό ΦΠΑ (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField("Συνολικό Ποσό (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    paid_amount = models.DecimalField("Εξοφλημένο Ποσό (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField("Σημειώσεις Τιμολογίου", blank=True, null=True)
    mark = models.CharField("ΜΑΡΚ myDATA", max_length=100, blank=True, null=True, editable=False)
    qr_code_url = models.URLField(" σύνδεσμος QR Code", blank=True, null=True, editable=False)
    purpose = models.CharField("Σκοπός Διακίνησης", max_length=20, choices=Purpose.choices, default=Purpose.SALE, blank=True, null=True)
    carrier = models.CharField("Μεταφορέας", max_length=100, blank=True, null=True)
    license_plate = models.CharField("Αριθμός Κυκλοφορίας Οχήματος", max_length=20, blank=True, null=True)
    shipping_name = models.CharField("Όνομα Παραλήπτη (Αποστολή)", max_length=200, blank=True, null=True)
    shipping_address = models.CharField("Διεύθυνση Αποστολής", max_length=200, blank=True, null=True)
    shipping_city = models.CharField("Πόλη Αποστολής", max_length=100, blank=True, null=True)
    shipping_postal_code = models.CharField("Τ.Κ. Αποστολής", max_length=10, blank=True, null=True)
    shipping_vat_number = models.CharField("ΑΦΜ Παραλήπτη (Αποστολή)", max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    _original_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk:
            self._original_status = self.status

    @property
    def outstanding_amount(self):
        return self.total_amount - self.paid_amount
    @property
    def is_overdue(self):
        # Ένα τιμολόγιο είναι εκπρόθεσμο αν έχει εκδοθεί (δεν έχει πληρωθεί/ακυρωθεί)
        # και η ημερομηνία λήξης του είναι στο παρελθόν.
        if self.status == self.STATUS_ISSUED and self.due_date:
            return self.due_date < timezone.now().date()
        return False

    class Meta:
        verbose_name = "Τιμολόγιο"
        verbose_name_plural = "Τιμολόγια"
        ordering = ['-issue_date', '-invoice_number']

    def __str__(self):
        return f"Τιμολόγιο {self.invoice_number} - {self.customer}"

    # --- ΟΙ ΠΑΡΑΚΑΤΩ ΜΕΘΟΔΟΙ ΕΙΝΑΙ ΤΩΡΑ ΣΩΣΤΑ ΣΤΟΙΧΙΣΜΕΝΕΣ ---
    def calculate_totals(self):
        # We need to make sure we are working with fresh data from the database
        aggregation = self.items.aggregate(
            subtotal=Sum('total_price'),
            vat=Sum('vat_amount')
        )
        self.subtotal = aggregation.get('subtotal') or Decimal('0.00')
        invoice_total_vat = aggregation.get('vat') or Decimal('0.00')

        if self.discount_percentage > 0:
            self.discount_amount = self.subtotal * (self.discount_percentage / Decimal('100'))
        else:
            self.discount_amount = Decimal('0.00')

        subtotal_after_discount = self.subtotal - self.discount_amount
        
        # Adjust VAT based on the overall discount percentage
        self.vat_amount = invoice_total_vat * (Decimal('1') - self.discount_percentage / Decimal('100'))
        
        self.total_amount = subtotal_after_discount + self.vat_amount

    def save(self, *args, **kwargs):
    # Αφαιρούμε ΟΛΗ την παλιά λογική από εδώ.
    # Η view θα αναλάβει πλέον τους υπολογισμούς και την αλλαγή κατάστασης.
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, verbose_name="Τιμολόγιο", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Προϊόν", on_delete=models.PROTECT, null=True, blank=True)
    description = models.CharField("Περιγραφή", max_length=255)
    quantity = models.DecimalField("Ποσότητα", max_digits=10, decimal_places=2)
    unit_price = models.DecimalField("Τιμή Μονάδας (προ ΦΠΑ)", max_digits=10, decimal_places=2)

    # --- ΝΕΑ ΠΕΔΙΑ ---
    is_gift = models.BooleanField("Δώρο", default=False)
    discount_percentage = models.DecimalField("Έκπτωση Είδους (%)", max_digits=5, decimal_places=2, default=Decimal('0.00'))
    # ------------------

    vat_percentage = models.DecimalField("Ποσοστό ΦΠΑ (%)", max_digits=5, decimal_places=2, default=Decimal('24.00'))
    vat_amount = models.DecimalField("Ποσό ΦΠΑ (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))

    total_price = models.DecimalField("Συνολική Αξία (προ ΦΠΑ)", max_digits=10, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = "Είδος Τιμολογίου"
        verbose_name_plural = "Είδη Τιμολογίου"

    def __str__(self):
        return f"{self.quantity} x {self.description} στο Τιμολόγιο {self.invoice.invoice_number}"

    # --- ΤΡΟΠΟΠΟΙΗΜΕΝΗ ΜΕΘΟΔΟΣ SAVE ---
    def save(self, *args, **kwargs):
    # Αφαιρούμε ΟΛΗ την παλιά λογική. Οι υπολογισμοί θα γίνουν στη view.
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        invoice_to_update = self.invoice
        super().delete(*args, **kwargs)
        if invoice_to_update:
            invoice_to_update.save()
class Commission(models.Model):
    class Status(models.TextChoices):
        UNPAID = 'UNPAID', 'Ανεξόφλητη'
        PAID = 'PAID', 'Εξοφλημένη'

    sales_rep = models.ForeignKey(SalesRepresentative, on_delete=models.CASCADE, verbose_name="Πωλητής/Αντιπρόσωπος")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Σχετικό Τιμολόγιο")
    calculated_amount = models.DecimalField("Υπολογισμένο Ποσό Προμήθειας (€)", max_digits=10, decimal_places=2)
    calculation_date = models.DateField("Ημερομηνία Υπολογισμού", auto_now_add=True)
    status = models.CharField("Κατάσταση", max_length=10, choices=Status.choices, default=Status.UNPAID)
    paid_date = models.DateField("Ημερομηνία Πληρωμής", null=True, blank=True)

    class Meta:
        verbose_name = "Προμήθεια"
        verbose_name_plural = "Προμήθειες"
        ordering = ['-calculation_date']

    def __str__(self):
        return f"Προμήθεια για {self.sales_rep} από τιμολόγιο {self.invoice.invoice_number}"
class CreditNote(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Πρόχειρο'
        ISSUED = 'ISSUED', 'Εκδόθηκε'
        # Το 'APPLIED' μπορεί να χρησιμοποιηθεί αν συμψηφιστεί με άλλο τιμολόγιο
        APPLIED = 'APPLIED', 'Εφαρμόστηκε' 

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='credit_notes', verbose_name="Πελάτης")
    
    # Το πιο σημαντικό πεδίο: η σύνδεση με το τιμολόγιο που πιστώνεται
    original_invoice = models.ForeignKey(
        Invoice, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='credit_notes', 
        verbose_name="Αρχικό Τιμολόγιο"
    )
    
    credit_note_number = models.CharField("Αρ. Πιστωτικού", max_length=100, unique=True, blank=True, editable=False)
    issue_date = models.DateField("Ημερομηνία Έκδοσης", default=timezone.now)
    reason = models.TextField("Αιτία Έκδοσης (π.χ. Επιστροφή προϊόντων)", blank=True, null=True)
    status = models.CharField("Κατάσταση", max_length=10, choices=Status.choices, default=Status.DRAFT)
    
    # Οικονομικά πεδία, παρόμοια με του Τιμολογίου
    subtotal = models.DecimalField("Υποσύνολο (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    vat_amount = models.DecimalField("Συνολικό Ποσό ΦΠΑ (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField("Συνολικό Ποσό (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Πιστωτικό Τιμολόγιο"
        verbose_name_plural = "Πιστωτικά Τιμολόγια"
        ordering = ['-issue_date']

    def __str__(self):
        return f"Πιστωτικό {self.credit_note_number} για πελάτη {self.customer}"


class CreditNoteItem(models.Model):
    credit_note = models.ForeignKey(CreditNote, on_delete=models.CASCADE, related_name='items', verbose_name="Πιστωτικό Τιμολόγιο")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, verbose_name="Προϊόν")
    description = models.CharField("Περιγραφή", max_length=255)
    quantity = models.DecimalField("Ποσότητα Επιστροφής", max_digits=10, decimal_places=2)
    unit_price = models.DecimalField("Τιμή Μονάδας (προ ΦΠΑ)", max_digits=10, decimal_places=2)
    
    # Οικονομικά πεδία ανά γραμμή
    vat_percentage = models.DecimalField("Ποσοστό ΦΠΑ (%)", max_digits=5, decimal_places=2)
    total_price = models.DecimalField("Συνολική Αξία Γραμμής (προ ΦΠΑ)", max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField("Ποσό ΦΠΑ Γραμμής (€)", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Είδος Πιστωτικού Τιμολογίου"
        verbose_name_plural = "Είδη Πιστωτικών Τιμολογίων"

    def __str__(self):
        return f"{self.quantity} x {self.description} στο Πιστωτικό {self.credit_note.credit_note_number}"
class UserProfile(models.Model):
    # Σύνδεση ένα-προς-ένα με τον χρήστη του Django
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')

    # --- Ρυθμίσεις Θέματος Εμφάνισης ---
    primary_color = models.CharField(
        "Βασικό Χρώμα Θέματος (π.χ. #0dcaf0)", 
        max_length=7, 
        default='#0dcaf0' # Προεπιλεγμένο γαλάζιο
    )
    background_color = models.CharField(
        "Χρώμα Φόντου Σελίδας (π.χ. #fffaf5)", 
        max_length=7, 
        default='#fffaf5' # Προεπιλεγμένο απαλό πορτοκαλί
    )
    sidebar_color = models.CharField(
        "Χρώμα Πλευρικού Μενού (π.χ. #eef8ff)", 
        max_length=7, 
        default='#eef8ff' # Προεπιλεγμένο απαλό γαλάζιο
    )
    
    class Meta:
        verbose_name = "Προφίλ Χρήστη"
        verbose_name_plural = "Προφίλ Χρηστών"

    def __str__(self):
        return f"Προφίλ για τον χρήστη {self.user.username}"
class RetailReceipt(models.Model):
    class Status(models.TextChoices):
        ISSUED = 'ISSUED', 'Εκδόθηκε'
        CANCELLED = 'CANCELLED', 'Ακυρώθηκε'

    receipt_number = models.CharField("Αρ. Απόδειξης", max_length=100, unique=True, blank=True, editable=False)
    issue_date = models.DateTimeField("Ημερομηνία & Ώρα Έκδοσης", default=timezone.now)
    
    # Προαιρετικά συνδέεται με έναν συγκεκριμένο πελάτη, αλλά συνήθως θα είναι ο "Πελάτης Λιανικής"
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='retail_receipts', verbose_name="Πελάτης")
    
    # Οικονομικά πεδία
    subtotal = models.DecimalField("Υποσύνολο (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    vat_amount = models.DecimalField("Συνολικό Ποσό ΦΠΑ (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField("Συνολικό Ποσό (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    status = models.CharField("Κατάσταση", max_length=10, choices=Status.choices, default=Status.ISSUED)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Απόδειξη Λιανικής"
        verbose_name_plural = "Αποδείξεις Λιανικής"
        ordering = ['-issue_date']

    def __str__(self):
        return f"Απόδειξη {self.receipt_number} - {self.total_amount}€"


class RetailReceiptItem(models.Model):
    receipt = models.ForeignKey(RetailReceipt, on_delete=models.CASCADE, related_name='items', verbose_name="Απόδειξη Λιανικής")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, verbose_name="Προϊόν")
    description = models.CharField("Περιγραφή", max_length=255)
    quantity = models.DecimalField("Ποσότητα", max_digits=10, decimal_places=2)
    
    # Η τιμή λιανικής του προϊόντος (με ΦΠΑ) όπως ήταν τη στιγμή της πώλησης
    unit_price = models.DecimalField("Τιμή Μονάδας (προ ΦΠΑ)", max_digits=10, decimal_places=2)
    
    discount_percentage = models.DecimalField("Έκπτωση Είδους (%)", max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Η τελική αξία της γραμμής μετά την έκπτωση (με ΦΠΑ)
    final_price = models.DecimalField("Τελική Αξία Γραμμής (€)", max_digits=10, decimal_places=2)

    # --- ΝΕΑ ΠΕΔΙΑ ΓΙΑ ΦΠΑ ---
    subtotal = models.DecimalField("Καθαρή Αξία Γραμμής (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    vat_amount = models.DecimalField("Ποσό ΦΠΑ Γραμμής (€)", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    # --- ΤΕΛΟΣ ΝΕΩΝ ΠΕΔΙΩΝ ---

    class Meta:
        verbose_name = "Είδος Απόδειξης Λιανικής"
        verbose_name_plural = "Είδη Απόδειξης Λιανικής"

    def __str__(self):
        return f"{self.quantity} x {self.description}"
class Attachment(models.Model):
    """
    Ένα γενικό μοντέλο για την επισύναψη αρχείων σε οποιοδήποτε άλλο μοντέλο.
    """
    file = models.FileField("Αρχείο", upload_to='attachments/%Y/%m/%d/')
    description = models.CharField("Περιγραφή", max_length=255, blank=True)
    uploaded_at = models.DateTimeField("Ημερομηνία & Ώρα Ανεβάσματος", auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='attachments')

    # Generic Foreign Key fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Επισυναπτόμενο Αρχείο"
        verbose_name_plural = "Επισυναπτόμενα Αρχεία"
        ordering = ['-uploaded_at']

    def __str__(self):
        # Επιστρέφει μόνο το όνομα του αρχείου από το path
        import os
        return os.path.basename(self.file.name)        


                                    