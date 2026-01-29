# core/signals.py
from django.db.models.signals import post_save, post_delete, pre_save, m2m_changed
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from crum import get_current_user
from django.db.models import Max
from .models import Customer

# Βεβαιώσου ότι όλα τα μοντέλα είναι εδώ
from .models import (
    Customer, Order, Product, StockReceipt, ActivityLog, Payment, 
    Invoice, Commission, CreditNote, UserProfile, RetailReceipt,
    DeliveryNote, PurchaseOrder
)

User = get_user_model() # Ορίζουμε το User model μία φορά για χρήση στο αρχείο

# --- Signal Handlers για Αυτόματους Κωδικούς ---

@receiver(pre_save, sender=Customer)
def set_customer_code(sender, instance, **kwargs):
    # Αυτή η λογική εκτελείται μόνο αν ο πελάτης είναι νέος και δεν έχει κωδικό
    if not instance.code:
        # Βρίσκουμε τον μεγαλύτερο υπάρχοντα αριθμητικό κωδικό
        max_code = Customer.objects.aggregate(max_code=Max('code'))['max_code']
        next_code_num = 1
        # Αν βρέθηκε max_code και είναι αριθμός, τότε ο επόμενος είναι +1
        if max_code and max_code.isdigit():
            next_code_num = int(max_code) + 1
        
        # Προληπτικός έλεγχος για να βρούμε έναν σίγουρα μοναδικό αριθμό
        new_code = f"{next_code_num:04d}" # π.χ. 0001, 0002 κ.ο.κ.
        while Customer.objects.filter(code=new_code).exists():
            next_code_num += 1
            new_code = f"{next_code_num:04d}"
            
        instance.code = new_code

@receiver(pre_save, sender=Order)
def set_order_number(sender, instance, **kwargs):
    if not instance.order_number:
        current_year = instance.order_date.year if instance.order_date else timezone.now().year
        prefix = "ORDER"
        last_order = Order.objects.filter(
            order_number__startswith=f'{prefix}-{current_year}-'
        ).order_by('-order_number').first()
        next_sequence = 1
        if last_order:
            try:
                last_sequence_str = last_order.order_number.split('-')[-1]
                next_sequence = int(last_sequence_str) + 1
            except (ValueError, IndexError):
                next_sequence = 1
        instance.order_number = f"{prefix}-{current_year}-{next_sequence:04d}"
@receiver(pre_save, sender=CreditNote)
def set_credit_note_number(sender, instance, **kwargs):
    if not instance.credit_note_number:
        current_year = instance.issue_date.year if instance.issue_date else timezone.now().year
        prefix = "CN" # CN για Credit Note
        last_cn = CreditNote.objects.filter(
            credit_note_number__startswith=f'{prefix}-{current_year}-'
        ).order_by('-credit_note_number').first()
        next_sequence = 1
        if last_cn:
            try:
                last_sequence_str = last_cn.credit_note_number.split('-')[-1]
                next_sequence = int(last_sequence_str) + 1
            except (ValueError, IndexError):
                next_sequence = 1
        instance.credit_note_number = f"{prefix}-{current_year}-{next_sequence:04d}"
# --- Signal Handlers για το ActivityLog ---

# --- Customer ActivityLog ---
@receiver(post_save, sender=Customer)
def log_customer_save(sender, instance, created, **kwargs):
    current_user = get_current_user()
    if created:
        action = ActivityLog.ACTION_TYPE_CREATE
        details = f"Δημιουργήθηκε ο πελάτης: {instance.get_full_name()} (Κωδ: {instance.code})"
    else:
        action = ActivityLog.ACTION_TYPE_UPDATE
        details = f"Ενημερώθηκαν τα στοιχεία του πελάτη: {instance.get_full_name()} (Κωδ: {instance.code})"

    ActivityLog.objects.create(
        user=current_user,
        action_type=action,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance),
        details=details
    )

@receiver(post_delete, sender=Customer)
def log_customer_delete(sender, instance, **kwargs):
    current_user = get_current_user()
    ActivityLog.objects.create(
        user=current_user,
        action_type=ActivityLog.ACTION_TYPE_DELETE,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance),
        details=f"Διαγράφηκε ο πελάτης: {instance.get_full_name()} (Κωδ: {instance.code})"
    )

# --- Order ActivityLog ---
@receiver(post_save, sender=Order)
def log_order_save(sender, instance, created, update_fields=None, **kwargs):
    current_user = get_current_user()
    customer_info = ""
    if instance.customer:
        customer_info = f" για τον πελάτη {instance.customer.get_full_name()}"
    elif hasattr(instance, 'items') and instance.items.exists() and hasattr(instance.items.first(), 'order') and instance.items.first().order.customer:
         customer_info = f" για τον πελάτη {instance.items.first().order.customer.get_full_name()}"

    if created:
        action = ActivityLog.ACTION_TYPE_CREATE
        details = f"Δημιουργήθηκε η παραγγελία {instance.order_number}{customer_info} με κατάσταση '{instance.get_status_display()}'."
    else:
        if update_fields and sorted(list(update_fields)) == sorted(['total_amount']):
            action = ActivityLog.ACTION_TYPE_UPDATE
            details = f"Ενημερώθηκε το συνολικό ποσό της παραγγελίας {instance.order_number}{customer_info} σε {instance.total_amount}€."
        else:
            action = ActivityLog.ACTION_TYPE_UPDATE
            details = f"Ενημερώθηκε η παραγγελία {instance.order_number}{customer_info}. Τρέχουσα κατάσταση: '{instance.get_status_display()}'."

    ActivityLog.objects.create(
        user=current_user,
        action_type=action,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance),
        details=details
    )

@receiver(post_delete, sender=Order)
def log_order_delete(sender, instance, **kwargs):
    current_user = get_current_user()
    customer_info = ""
    if instance.customer: 
        customer_info = f" του πελάτη {instance.customer.get_full_name() if instance.customer else '[Άγνωστος Πελάτης]'}"

    ActivityLog.objects.create(
        user=current_user,
        action_type=ActivityLog.ACTION_TYPE_DELETE,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance), 
        details=f"Διαγράφηκε η παραγγελία {instance.order_number}{customer_info}."
    )

# --- Product ActivityLog ---
@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    current_user = get_current_user()
    if created:
        action = ActivityLog.ACTION_TYPE_CREATE
        details = (f"Δημιουργήθηκε το προϊόν: '{instance.name}' (Κωδ: {instance.code or 'N/A'}). "
                   f"Τιμή: {instance.price}€, Απόθεμα: {instance.stock_quantity} {instance.get_unit_of_measurement_display()}.")
    else:
        action = ActivityLog.ACTION_TYPE_UPDATE
        details = (f"Ενημερώθηκαν τα στοιχεία του προϊόντος: '{instance.name}' (Κωδ: {instance.code or 'N/A'}). "
                   f"Τρέχουσα τιμή: {instance.price}€, Τρέχον απόθεμα: {instance.stock_quantity} {instance.get_unit_of_measurement_display()}.")

    ActivityLog.objects.create(
        user=current_user,
        action_type=action,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance),
        details=details
    )

@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    current_user = get_current_user()
    ActivityLog.objects.create(
        user=current_user,
        action_type=ActivityLog.ACTION_TYPE_DELETE,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance),
        details=f"Διαγράφηκε το προϊόν: '{instance.name}' (Κωδ: {instance.code or 'N/A'})."
    )

# --- StockReceipt ActivityLog ---
@receiver(post_save, sender=StockReceipt)
def log_stock_receipt_save(sender, instance, created, **kwargs):
    if created:
        current_user = get_current_user()
        details = (f"Καταχωρήθηκε παραλαβή {instance.quantity_added} "
                   f"{instance.product.get_unit_of_measurement_display() if instance.product else ''} "
                   f"για το προϊόν '{instance.product.name if instance.product else '[Άγνωστο Προϊόν]'}' "
                   f"(Κωδ: {instance.product.code if instance.product else 'N/A'}).")
        if instance.notes:
            details += f" Σημειώσεις: {instance.notes}"

        ActivityLog.objects.create(
            user=current_user,
            action_type=ActivityLog.ACTION_TYPE_CREATE,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk,
            object_repr=str(instance),
            details=details
        )

@receiver(post_delete, sender=StockReceipt, dispatch_uid="log_stock_receipt_delete_unique_crm_id") 
def log_stock_receipt_delete(sender, instance, **kwargs):
    current_user = get_current_user()
    product_affected = instance.product
    quantity_from_receipt = instance.quantity_added

    log_details = (f"Διαγράφηκε η παραλαβή ποσότητας {quantity_from_receipt} "
                   f"{product_affected.get_unit_of_measurement_display() if product_affected else ''} "
                   f"για το προϊόν '{product_affected.name if product_affected else '[Άγνωστο Προϊόν]'}' "
                   f"(Κωδ: {product_affected.code if product_affected else 'N/A'}).")

    if product_affected and quantity_from_receipt is not None:
        try:
            with transaction.atomic():
                product_to_update = Product.objects.select_for_update().get(pk=product_affected.pk)
                product_to_update.stock_quantity -= quantity_from_receipt
                product_to_update.save(update_fields=['stock_quantity', 'updated_at'])
                log_details += f" Το απόθεμα του προϊόντος '{product_to_update.name}' ενημερώθηκε σε {product_to_update.stock_quantity}."
        except Product.DoesNotExist:
            log_details += " Το προϊόν δεν βρέθηκε για ενημέρωση αποθέματος."
        except Exception as e:
            log_details += f" Σφάλμα κατά την ενημέρωση αποθέματος: {str(e)}"
            # import logging
            # logger = logging.getLogger(__name__)
            # logger.error(f"Error updating stock for product {product_affected.pk if product_affected else 'N/A'} on StockReceipt delete (ID: {instance.pk}): {e}")
    
    ActivityLog.objects.create(
        user=current_user,
        action_type=ActivityLog.ACTION_TYPE_DELETE,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance),
        details=log_details
    )

# --- Signal Handlers για User Login/Logout ---
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ActivityLog.objects.create(
        user=user, 
        action_type=ActivityLog.ACTION_TYPE_LOGIN,
        content_type=None, 
        object_id=None,
        object_repr=f"Χρήστης: {user.username}",
        details=f"Ο χρήστης '{user.username}' συνδέθηκε επιτυχώς."
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    user_to_log = user
    if not user_to_log:
        user_to_log = get_current_user()

    if user_to_log and user_to_log.is_authenticated:
        username = user_to_log.username
        ActivityLog.objects.create(
            user=user_to_log, 
            action_type=ActivityLog.ACTION_TYPE_LOGOUT,
            content_type=None,
            object_id=None,
            object_repr=f"Χρήστης: {username}",
            details=f"Ο χρήστης '{username}' αποσυνδέθηκε."
        )
    elif user : 
        username = user.username
        ActivityLog.objects.create(
            user=None, 
            action_type=ActivityLog.ACTION_TYPE_LOGOUT,
            content_type=None,
            object_id=None,
            object_repr=f"Χρήστης: {username}",
            details=f"Ο χρήστης '{username}' αποσυνδέθηκε (ή η συνεδρία έληξε)."
        )
    else:
        ActivityLog.objects.create(
            user=None,
            action_type=ActivityLog.ACTION_TYPE_LOGOUT,
            details="Έγινε αποσύνδεση (χωρίς προσδιορισμένο χρήστη)."
        )

# --- Signal Handlers για το User Model (Create, Update, Delete) ---
@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    performing_user = get_current_user()

    if created and not performing_user and instance.is_superuser and User.objects.count() <= 1:
        return # Δεν καταγράφουμε την αρχική δημιουργία superuser μέσω createsuperuser χωρίς request

    if created:
        action = ActivityLog.ACTION_TYPE_CREATE
        details = f"Δημιουργήθηκε ο χρήστης '{instance.username}'"
        if performing_user and performing_user != instance:
            details += f" από τον χρήστη '{performing_user.username}'."
        elif performing_user == instance:
             details += "."
        else: 
            details += " (από σύστημα/διαχειριστική εντολή)."
    else: 
        action = ActivityLog.ACTION_TYPE_UPDATE
        details = f"Ενημερώθηκαν τα στοιχεία του χρήστη '{instance.username}'"
        if performing_user:
            details += f" από τον χρήστη '{performing_user.username}'."
        else:
            details += " (από σύστημα)."

    ActivityLog.objects.create(
        user=performing_user, 
        action_type=action,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance.username), 
        details=details
    )

@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    performing_user = get_current_user()
    details = f"Διαγράφηκε ο χρήστης '{instance.username}'"
    if performing_user:
        details += f" από τον χρήστη '{performing_user.username}'."
    else:
        details += " (από σύστημα/διαχειριστική εντολή)."

    ActivityLog.objects.create(
        user=performing_user,
        action_type=ActivityLog.ACTION_TYPE_DELETE,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance.username),
        details=details
    )
@receiver(pre_save, sender=Payment)
def set_payment_receipt_number(sender, instance, **kwargs):
    if not instance.receipt_number and not instance.pk: # Μόνο για νέα αντικείμενα που δεν έχουν ήδη αριθμό
        current_year = instance.payment_date.year if instance.payment_date else timezone.now().year
        prefix = "PAY" # Μπορείς να το αλλάξεις σε "GRM" (Γραμμάτιο) ή "RCPT" (Receipt) αν προτιμάς
        
        last_payment_for_year = Payment.objects.filter(
            receipt_number__startswith=f'{prefix}-{current_year}-'
        ).order_by('-receipt_number').first()
        
        next_sequence = 1
        if last_payment_for_year and last_payment_for_year.receipt_number:
            try:
                last_sequence_str = last_payment_for_year.receipt_number.split('-')[-1]
                next_sequence = int(last_sequence_str) + 1
            except (ValueError, IndexError):
                # Εναλλακτικός τρόπος αν η παραπάνω λογική αποτύχει για κάποιο λόγο
                # ή αν θέλεις να είσαι πιο ανθεκτικός σε αλλαγές format χειροκίνητα (δεν θα έπρεπε)
                next_sequence = Payment.objects.filter(receipt_number__startswith=f'{prefix}-{current_year}-').count() + 1
        
        instance.receipt_number = f"{prefix}-{current_year}-{next_sequence:04d}" # Π.χ., PAY-2025-0001
@receiver(post_save, sender=Payment)
def log_payment_save(sender, instance, created, **kwargs):
    current_user = get_current_user()
    user_for_log = current_user

    action_type = ActivityLog.ACTION_TYPE_CREATE if created else ActivityLog.ACTION_TYPE_UPDATE
    details = ""

    if created:
        user_for_log = current_user or instance.recorded_by
        details = f"Καταχωρήθηκε η πληρωμή {instance.receipt_number} ποσού {instance.amount_paid}€ για τον πελάτη {instance.customer.get_full_name()}."
        # ... (οι υπόλοιπες λεπτομέρειες για created όπως τις είχαμε) ...
        if instance.order:
            details += f" (Σχετ. Παραγγελία: {instance.order.order_number if instance.order else 'N/A'})"
        if instance.payment_method:
            details += f" Τρόπος: {instance.get_payment_method_display()}."
        if instance.reference_number:
            details += f" Εξωτερ. Αναφορά: {instance.reference_number}."

    else: # Είναι ενημέρωση (update)
        if instance.status == Payment.STATUS_CANCELLED and hasattr(instance, '_original_status') and instance._original_status == Payment.STATUS_ACTIVE:
            # Το _original_status πρέπει να υπάρχει στο instance αν η __init__ του μοντέλου το θέτει.
            # Η σύγκριση αυτή είναι για να είμαστε σίγουροι ότι όντως *τώρα* ακυρώθηκε.
            details = f"Η πληρωμή {instance.receipt_number} (ποσό: {instance.amount_paid}€, πελάτης: {instance.customer.get_full_name()}) άλλαξε κατάσταση σε Ακυρωμένη."
            if instance.cancellation_reason:
                details += f" Λόγος: {instance.cancellation_reason}"
            if instance.cancelled_by:
                details += f" Η ακύρωση έγινε από: {instance.cancelled_by.username}"
                user_for_log = instance.cancelled_by 
            if instance.cancelled_at:
                details += f" στις {instance.cancelled_at.strftime('%d/%m/%Y %H:%M')}."
        
        # Έλεγχος για άλλες αλλαγές (από την περιορισμένη επεξεργασία)
        elif hasattr(instance, '_change_details_for_log') and instance._change_details_for_log:
            details = f"Ενημερώθηκε η πληρωμή {instance.receipt_number}: {instance._change_details_for_log}"
            # Καθαρίζουμε την προσωρινή μεταβλητή για να μην υπάρχει σε επόμενα saves αν δεν υπάρχουν αλλαγές
            del instance._change_details_for_log 
            if not user_for_log and instance.recorded_by: # Αν δεν πήραμε current_user, βάλε τον αρχικό recorder
                 user_for_log = instance.recorded_by
        elif not (instance.status == Payment.STATUS_CANCELLED): # Απλή αποθήκευση χωρίς εμφανείς αλλαγές (όχι ακύρωση)
            details = f"Ενημερώθηκε/Αποθηκεύτηκε η πληρωμή {instance.receipt_number} για τον πελάτη {instance.customer.get_full_name()} (χωρίς ανιχνεύσιμες αλλαγές πεδίων φόρμας)."
            if not user_for_log and instance.recorded_by:
                 user_for_log = instance.recorded_by


    if details:
        ActivityLog.objects.create(
            user=user_for_log,
            action_type=action_type,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk,
            object_repr=str(instance),
            details=details
        )
@receiver(post_delete, sender=Payment)
def log_payment_delete(sender, instance, **kwargs):
    current_user = get_current_user()
    
    # Το instance που περνάει στο post_delete έχει ακόμα τα πεδία του,
    # παρόλο που η εγγραφή έχει διαγραφεί από τη βάση.
    details = (f"Διαγράφηκε οριστικά η πληρωμή {instance.receipt_number or '[Χωρίς Αρ.Συστ.]'} "
               f"(ποσό: {instance.amount_paid}€, "
               f"πελάτης: {instance.customer.get_full_name() if instance.customer else '[Άγνωστος Πελάτης]'}, "
               f"ημερ. πληρωμής: {instance.payment_date.strftime('%d/%m/%Y')}). "
               f"Η κατάστασή της κατά τη διαγραφή ήταν: {instance.get_status_display()}.") # Καταγράφουμε και την κατάσταση που είχε

    ActivityLog.objects.create(
        user=current_user,
        action_type=ActivityLog.ACTION_TYPE_DELETE,
        content_type=ContentType.objects.get_for_model(instance),
        # object_id=instance.pk, # Το instance.pk δεν είναι πλέον έγκυρο για μια διαγραμμένη εγγραφή
        object_repr=str(instance), # Το str(instance) θα δώσει την τελευταία αναπαράσταση πριν τη διαγραφή
        details=details
    )
@receiver(pre_save, sender=Invoice)
def set_invoice_number(sender, instance, **kwargs):
    # Ελέγχουμε αν το τιμολόγιο είναι νέο και δεν έχει ήδη αριθμό
    if not instance.invoice_number:
        # Παίρνουμε το έτος από την ημερομηνία έκδοσης
        current_year = instance.issue_date.year if instance.issue_date else timezone.now().year
        prefix = "INV" # Μπορείς να το αλλάξεις σε ό,τι θέλεις, π.χ., "ΤΙΜ"

        # Βρίσκουμε το τελευταίο τιμολόγιο για το τρέχον έτος
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=f'{prefix}-{current_year}-'
        ).order_by('-invoice_number').first()

        next_sequence = 1
        if last_invoice:
            try:
                # Παίρνουμε τον τελευταίο αριθμό της ακολουθίας και τον αυξάνουμε κατά 1
                last_sequence_str = last_invoice.invoice_number.split('-')[-1]
                next_sequence = int(last_sequence_str) + 1
            except (ValueError, IndexError):
                # Fallback σε περίπτωση που κάτι πάει στραβά με το format
                next_sequence = 1

        # Δημιουργούμε το νέο αριθμό τιμολογίου με padding (π.χ., 0001)
        instance.invoice_number = f"{prefix}-{current_year}-{next_sequence:04d}"
@receiver(post_save, sender=Invoice)
def log_invoice_save(sender, instance, created, **kwargs):
    current_user = get_current_user()
    action = ""
    details = ""

    if created:
        action = ActivityLog.ACTION_TYPE_CREATE
        details = f"Δημιουργήθηκε το τιμολόγιο {instance.invoice_number} για τον πελάτη {instance.customer}."
    else:
        action = ActivityLog.ACTION_TYPE_UPDATE
        # Έλεγχος για αλλαγή κατάστασης
        if instance._original_status != instance.status:
            details = (f"Το τιμολόγιο {instance.invoice_number} άλλαξε κατάσταση από "
                       f"'{dict(Invoice.INVOICE_STATUS_CHOICES).get(instance._original_status, instance._original_status)}' "
                       f"σε '{instance.get_status_display()}'.")
        else:
            details = f"Ενημερώθηκαν τα στοιχεία του τιμολογίου {instance.invoice_number}."

    if details: # Δημιουργούμε log μόνο αν έχουμε κάτι να πούμε
        ActivityLog.objects.create(
            user=current_user,
            action_type=action,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk,
            object_repr=str(instance),
            details=details
        )

@receiver(post_delete, sender=Invoice)
def log_invoice_delete(sender, instance, **kwargs):
    current_user = get_current_user()
    ActivityLog.objects.create(
        user=current_user,
        action_type=ActivityLog.ACTION_TYPE_DELETE,
        object_repr=str(instance), # Το object δεν υπάρχει πια, χρησιμοποιούμε την αναπαράστασή του
        details=f"Διαγράφηκε οριστικά το τιμολόγιο {instance.invoice_number} του πελάτη {instance.customer}."
    )
@receiver(m2m_changed, sender=Payment.invoices.through)
@receiver(m2m_changed, sender=Payment.invoices.through)
def update_invoice_status_on_payment(sender, instance, action, pk_set, **kwargs):
    """
    Signal που κατανέμει το ποσό μιας πληρωμής στα συνδεδεμένα τιμολόγια (FIFO)
    και ενημερώνει την κατάστασή τους αν εξοφληθούν.
    """
    # Μας ενδιαφέρει μόνο η στιγμή που προστίθενται τιμολόγια σε μια πληρωμή
    if action == "post_add":
        payment = instance
        # Διασφαλίζουμε ότι η πληρωμή είναι ενεργή
        if payment.status != Payment.STATUS_ACTIVE:
            return

        # Παίρνουμε τα τιμολόγια που συνδέθηκαν, από το παλαιότερο στο νεότερο
        invoices_to_process = payment.invoices.filter(pk__in=pk_set).order_by('issue_date', 'pk')

        with transaction.atomic():
            for invoice in invoices_to_process:
                # Κλειδώνουμε το τιμολόγιο για να αποφύγουμε race conditions
                inv = Invoice.objects.select_for_update().get(pk=invoice.pk)
                
                amount_due = inv.outstanding_amount
                
                if amount_due > 0:
                    # Το ποσό που θα εφαρμοστεί είναι το σύνολο της πληρωμής,
                    # καθώς η λογική είναι ότι μια πληρωμή αφορά συγκεκριμένα τιμολόγια.
                    # Στο μέλλον μπορεί να γίνει πιο σύνθετη λογική (π.χ. μερική κατανομή)
                    amount_to_apply = payment.amount_paid

                    # Δεν θέλουμε να εφαρμόσουμε περισσότερα από όσα χρωστάει ο πελάτης για αυτό το τιμολόγιο
                    if amount_to_apply > amount_due:
                        amount_to_apply = amount_due
                    
                    inv.paid_amount += amount_to_apply
                    
                    # --- ΝΕΑ ΛΟΓΙΚΗ ΕΛΕΓΧΟΥ ΚΑΙ ΑΛΛΑΓΗΣ ΚΑΤΑΣΤΑΣΗΣ ---
                    # Ελέγχουμε αν το υπόλοιπο είναι πλέον μηδέν ή και αρνητικό (π.χ. από υπερπληρωμή)
                    if inv.outstanding_amount <= 0:
                        inv.status = Invoice.STATUS_PAID
                    
                    # Αποθηκεύουμε τις αλλαγές στο τιμολόγιο (είτε μόνο το paid_amount, είτε και το status)
                    inv.save()
@receiver(post_save, sender=Invoice)
def create_commission_on_paid_invoice(sender, instance, created, **kwargs):
    """
    Αυτό το signal ενεργοποιείται κάθε φορά που ένα τιμολόγιο αποθηκεύεται.
    Ελέγχει αν η κατάστασή του άλλαξε σε 'Εξοφλήθηκε' και δημιουργεί την
    αντίστοιχη εγγραφή προμήθειας.
    """
    # Συνθήκη 1: Η κατάσταση του τιμολογίου πρέπει ΤΩΡΑ να είναι 'Εξοφλήθηκε'
    # και ΠΡΙΝ την αποθήκευση να ΜΗΝ ήταν 'Εξοφλήθηκε'.
    is_now_paid = instance.status == Invoice.STATUS_PAID
    was_not_paid_before = instance._original_status != Invoice.STATUS_PAID

    if is_now_paid and was_not_paid_before:
        # Συνθήκη 2: Ο πελάτης του τιμολογίου πρέπει να έχει πωλητή
        # και το ποσοστό προμήθειας του πωλητή να είναι πάνω από μηδέν.
        if instance.customer and instance.customer.sales_rep and instance.customer.sales_rep.commission_rate > 0:
            
            sales_rep = instance.customer.sales_rep
            
            # Συνθήκη 3: Έλεγχος για να μην δημιουργηθεί διπλή προμήθεια για το ίδιο τιμολόγιο.
            commission_exists = Commission.objects.filter(invoice=instance).exists()
            
            if not commission_exists:
                # Υπολογίζουμε το ποσό της προμήθειας βάσει του Υποσυνόλου (καθαρή αξία).
                commission_rate = sales_rep.commission_rate
                amount_to_calculate_on = instance.subtotal
                
                calculated_commission = (amount_to_calculate_on * commission_rate) / 100
                
                # Δημιουργούμε τη νέα εγγραφή προμήθειας στη βάση δεδομένων.
                Commission.objects.create(
                    sales_rep=sales_rep,
                    invoice=instance,
                    calculated_amount=calculated_commission
                    # Η κατάσταση по умолчанию είναι 'UNPAID', οπότε δεν χρειάζεται να την ορίσουμε.
                )
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Δημιουργεί ένα UserProfile αυτόματα κάθε φορά που δημιουργείται ένας νέος User.
    """
    if created:
        UserProfile.objects.create(user=instance)
@receiver(pre_save, sender=RetailReceipt)
def set_retail_receipt_number(sender, instance, **kwargs):
    if not instance.receipt_number:
        current_year = instance.issue_date.year if instance.issue_date else timezone.now().year
        prefix = "RETAIL" # ή ΑΛΠ για Απόδειξη Λιανικής Πώλησης

        last_receipt = RetailReceipt.objects.filter(
            receipt_number__startswith=f'{prefix}-{current_year}-'
        ).order_by('-receipt_number').first()

        next_sequence = 1
        if last_receipt:
            try:
                last_sequence_str = last_receipt.receipt_number.split('-')[-1]
                next_sequence = int(last_sequence_str) + 1
            except (ValueError, IndexError):
                next_sequence = 1
        
        instance.receipt_number = f"{prefix}-{current_year}-{next_sequence:05d}" # 5 ψηφία για περισσότερες αποδείξεις
@receiver(pre_save, sender=DeliveryNote)
def set_delivery_note_number(sender, instance, **kwargs):
    if not instance.delivery_note_number:
        current_year = instance.issue_date.year if instance.issue_date else timezone.now().year
        prefix = "DN" # ή ΔΑ αν προτιμάς

        last_dn = DeliveryNote.objects.filter(
            delivery_note_number__startswith=f'{prefix}-{current_year}-'
        ).order_by('-delivery_note_number').first()

        next_sequence = 1
        if last_dn:
            try:
                last_sequence_str = last_dn.delivery_note_number.split('-')[-1]
                next_sequence = int(last_sequence_str) + 1
            except (ValueError, IndexError):
                next_sequence = 1

        instance.delivery_note_number = f"{prefix}-{current_year}-{next_sequence:05d}" # π.χ., DN-2025-00001
@receiver(pre_save, sender=PurchaseOrder)
def set_po_number(sender, instance, **kwargs):
    if not instance.po_number:
        current_year = instance.order_date.year if instance.order_date else timezone.now().year
        prefix = "PO" # PO για Purchase Order
        
        last_po = PurchaseOrder.objects.filter(
            po_number__startswith=f'{prefix}-{current_year}-'
        ).order_by('-po_number').first()
        
        next_sequence = 1
        if last_po and last_po.po_number:
            try:
                last_sequence_str = last_po.po_number.split('-')[-1]
                next_sequence = int(last_sequence_str) + 1
            except (ValueError, IndexError):
                next_sequence = 1
        
        instance.po_number = f"{prefix}-{current_year}-{next_sequence:05d}"                                                                                            