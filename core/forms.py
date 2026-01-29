# core/forms.py

from django import forms
from django.forms import inlineformset_factory, formset_factory
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import CreditNote, CreditNoteItem
from django.db.models import F
from .models import UserProfile
from .models import Attachment
from decimal import Decimal
from .models import (Customer, Invoice, Order, OrderItem, Payment, Product,
                   SalesRepresentative, StockReceipt, DeliveryNote, Purpose, Supplier, RetailReceipt, RetailReceiptItem, PurchaseOrder, PurchaseOrderItem)

User = get_user_model()

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', 'description']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'description': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Προαιρετική περιγραφή...'}),
        }
class SalesRepresentativeForm(forms.ModelForm):
    class Meta:
        model = SalesRepresentative
        # Προσθέτουμε το 'rep_type' στα πεδία
        fields = ['user', 'rep_type', 'phone', 'commission_rate']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'rep_type': forms.Select(attrs={'class': 'form-select'}), # Προσθέτουμε widget και για το νέο πεδίο
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'commission_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }
        labels = {
            'user': 'Λογαριασμός Χρήστη',
            'rep_type': 'Τύπος', # Προσθέτουμε το label
            'phone': 'Τηλέφωνο',
            'commission_rate': 'Ποσοστό Προμήθειας (%)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Αυτή η λογική φιλτράρει τους χρήστες που είναι ήδη πωλητές,
        # και εφαρμόζεται σωστά μόνο κατά τη δημιουργία νέου πωλητή.
        if not self.instance.pk:
            self.fields['user'].queryset = User.objects.filter(salesrepresentative__isnull=True)


class CustomerForm(forms.ModelForm):
    

    class Meta:
        model = Customer
        exclude = ('code', 'first_name_normalized', 'last_name_normalized', 'company_name_normalized', 'balance')
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Αυτό παραμένει σωστό
        self.fields['parent'].queryset = Customer.objects.filter(is_branch=False)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('name_normalized',)
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expiry_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }


class OrderForm(forms.ModelForm):
    customer_search = forms.CharField(label="Πελάτης", required=False, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
    
    class Meta:
        model = Order
        fields = [
            'customer', 
            'order_date', 
            'delivery_date', 
            'status',  # <-- Το πεδίο που έλειπε είναι τώρα εδώ
            'shipping_name', 'shipping_address', 'shipping_city', 'shipping_postal_code',
            'purpose', 'carrier', 'license_plate',
            'comments'
        ]
        widgets = {
            'customer': forms.HiddenInput(),
            'order_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'delivery_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}), # <-- Και το widget του είναι εδώ
            'shipping_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'shipping_address': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'shipping_postal_code': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'purpose': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'carrier': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'comments': forms.Textarea(attrs={'rows': 2, 'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        required_fields = [
            'shipping_name', 'shipping_address', 'shipping_city', 'shipping_postal_code'
        ]
        
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

class OrderItemForm(forms.ModelForm):
    product_search = forms.CharField(label="Προϊόν", required=False, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
    
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'is_gift', 'unit_price', 'discount_percentage', 'vat_percentage', 'comments']
        widgets = {
            'product': forms.HiddenInput(),
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center', 'style': 'max-width: 90px;', 'max': '999'}),
            'is_gift': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm text-end'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center'}),
            'vat_percentage': forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center'}),
            'comments': forms.Textarea(attrs={'rows': 1, 'class': 'form-control form-control-sm'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")

        # Αν δεν υπάρχει προϊόν ή ποσότητα, δεν μπορούμε να κάνουμε έλεγχο
        if not product or not quantity:
            return cleaned_data

        # --- ΕΛΕΓΧΟΣ ΑΠΟΘΕΜΑΤΟΣ ---
        # Υπολογίζουμε το πραγματικά διαθέσιμο απόθεμα.
        # Αν επεξεργαζόμαστε ένα υπάρχον είδος, πρέπει να προσθέσουμε πίσω
        # την ποσότητά του στο απόθεμα πριν κάνουμε τον έλεγχο.
        available_stock = product.stock_quantity
        if self.instance and self.instance.pk:
            available_stock += self.instance._old_quantity # Το _old_quantity το παίρνουμε από το μοντέλο

        if quantity > available_stock:
            error_message = f"Δεν υπάρχει επαρκές απόθεμα. Διαθέσιμο: {int(available_stock) if available_stock % 1 == 0 else available_stock} {product.get_unit_of_measurement_display()}."
            # Χρησιμοποιούμε το self.add_error για να συνδέσουμε το σφάλμα με το συγκεκριμένο πεδίο
            self.add_error('quantity', forms.ValidationError(error_message))
        
        # --- ΕΛΕΓΧΟΣ ΓΙΑ ΑΚΕΡΑΙΟΥΣ ΑΡΙΘΜΟΥΣ ΣΕ ΤΕΜΑΧΙΑ (η λογική σου παραμένει) ---
        if product.unit_of_measurement == 'pcs':
            if quantity % 1 != 0:
                self.add_error('quantity', forms.ValidationError(
                    'Για τα τεμάχια, η ποσότητα πρέπει να είναι ακέραιος αριθμός.'
                ))

        return cleaned_data    

class InvoiceDiscountForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['discount_percentage']
        labels = {'discount_percentage': 'Ποσοστό Έκπτωσης (%)'}
        widgets = {'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})}


class PaymentForm(forms.ModelForm):
    invoices = forms.ModelMultipleChoiceField(
        queryset=Invoice.objects.none(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False, 
        label="Αντιστοίχιση με Ανεξόφλητα Τιμολόγια"
    )
    customer_search = forms.CharField(
        label="Αναζήτηση Πελάτη", 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Πληκτρολογήστε για αναζήτηση πελάτη...'})
    )
    
    class Meta:
        model = Payment
        exclude = ['order', 'status', 'cancellation_reason', 'cancelled_at', 'cancelled_by', 'recorded_by']
        widgets = {
            'customer': forms.HiddenInput(), 
            'payment_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}), 
            'value_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}), 
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}), 
            'payment_method': forms.Select(attrs={'class': 'form-select'}), 
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}), 
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        customer_instance = kwargs.pop('customer_instance', None)
        
        super().__init__(*args, **kwargs)

        customer = customer_instance or (self.instance.pk and self.instance.customer)
        if customer:
            self.fields['invoices'].queryset = Invoice.objects.filter(
                customer=customer,
                status=Invoice.STATUS_ISSUED,
                total_amount__gt=F('paid_amount')
            ).order_by('issue_date')
            
            if 'customer_search' in self.fields:
                self.fields['customer_search'].disabled = True

      
        # Η φόρμα ελέγχει από μόνη της αν είναι σε κατάσταση επεξεργασίας,
        # εξετάζοντας αν της έχει δοθεί ένα υπάρχον 'instance'.
        if self.instance and self.instance.pk:
            if 'amount_paid' in self.fields:
                self.fields['amount_paid'].disabled = True
       


class PaymentCancellationForm(forms.Form):
    cancellation_reason = forms.CharField(label="Λόγος Ακύρωσης", widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}), required=True, help_text="Παρακαλώ περιγράψτε τον λόγο για την ακύρωση αυτής της πληρωμής.")

class StockReceiptForm(forms.ModelForm):
    class Meta:
        model = StockReceipt
        fields = ['product', 'quantity_added', 'date_received', 'notes']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True).order_by('name')


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'is_staff', 'is_active')


class CustomUserChangeForm(UserChangeForm):
    password = None
    new_password1 = forms.CharField(label=_("Νέος κωδικός"), widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), strip=False, required=False)
    new_password2 = forms.CharField(label=_("Επιβεβαίωση νέου κωδικού"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), required=False)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple, required=False, label="Ομάδες Χρηστών")
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'groups')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].disabled = True
        if self.instance and self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.all()
    def clean_new_password2(self):
        pw1 = self.cleaned_data.get("new_password1")
        pw2 = self.cleaned_data.get("new_password2")
        if pw1 and pw1 != pw2: raise forms.ValidationError(_("Οι δύο κωδικοί δεν ταιριάζουν."), code='password_mismatch')
        return pw2
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("new_password1"): user.set_password(self.cleaned_data.get("new_password1"))
        if commit: user.save(); self.save_m2m()
        return user
class CreditNoteForm(forms.ModelForm):
    class Meta:
        model = CreditNote
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'reason': 'Αιτιολογία Έκδοσης'
        }


class CreditNoteItemForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput())
    description = forms.CharField(label="Περιγραφή", required=False, widget=forms.TextInput(attrs={'class': 'form-control-plaintext', 'readonly': True}))
    unit_price = forms.DecimalField(label="Τιμή Μονάδας", required=False, widget=forms.NumberInput(attrs={'class': 'form-control-plaintext text-end', 'readonly': True}))
    original_quantity = forms.DecimalField(label="Ποσότητα Τιμολ.", disabled=True, required=False, widget=forms.NumberInput(attrs={'class': 'form-control-plaintext text-center'}))
    
    # Κάνουμε την ποσότητα ΜΗ υποχρεωτική σε επίπεδο πεδίου
    quantity = forms.DecimalField(label="Ποσότητα Επιστροφής", required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center', 'min': '0'}), initial=0)
    
    vat_percentage = forms.DecimalField(widget=forms.HiddenInput(), required=False)


# Δημιουργούμε μια custom ΒΑΣΙΚΗ κλάση για το formset μας
class BaseCreditNoteItemFormSet(forms.BaseFormSet):
    def clean(self):
        """
        Προσθέτει custom λογική επικύρωσης για ολόκληρο το σετ φορμών.
        """
        if any(self.errors):
            # Μην κάνεις τίποτα αν υπάρχουν ήδη σφάλματα σε μεμονωμένες φόρμες
            return

        for form in self.forms:
            # Παίρνουμε τα δεδομένα της κάθε φόρμας
            quantity = form.cleaned_data.get('quantity')
            original_quantity = form.initial.get('original_quantity')
            is_gift = form.initial.get('is_gift', False)

            # Αν δεν είναι δώρο, η ποσότητα δεν μπορεί να είναι κενή
            if not is_gift and quantity is None:
                raise forms.ValidationError('Πρέπει να ορίσετε ποσότητα για τα είδη που δεν είναι δώρα.')

            # Ο έλεγχος για την υπέρβαση της ποσότητας γίνεται για όλα τα είδη
            if quantity is not None and original_quantity is not None:
                if quantity > original_quantity:
                    # Σηκώνουμε ένα γενικό σφάλμα για το formset
                    raise forms.ValidationError(
                        f"Η ποσότητα επιστροφής για το '{form.initial.get('description')}' "
                        f"({quantity}) δεν μπορεί να ξεπερνά την αρχική ({original_quantity})."
                    )


CreditNoteItemFormSet = forms.formset_factory(CreditNoteItemForm, extra=0)
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['primary_color', 'background_color', 'sidebar_color']
        widgets = {
            # Ορίζουμε το widget για κάθε πεδίο να είναι ένας HTML5 color picker
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'sidebar_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }
        labels = {
            'primary_color': 'Βασικό Χρώμα (μπάρες, κουμπιά)',
            'background_color': 'Χρώμα Φόντου Σελίδας',
            'sidebar_color': 'Χρώμα Πλευρικού Μενού',
        }
class MyProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Όνομα',
            'last_name': 'Επώνυμο',
            'email': 'Email',
        }
# --------------------------------------------------------------------------
# Φόρμες για τη Δημιουργία Απόδειξης Λιανικής (POS Form)
# --------------------------------------------------------------------------

class RetailReceiptItemForm(forms.Form):
    product_search = forms.CharField(
        label="Προϊόν", 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm product-search-pos', 'placeholder': 'Αναζήτηση...'})
    )
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput())
    
    quantity = forms.DecimalField(
        label="Ποσότητα", 
        initial=1, 
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center', 'min': '0.01', 'step': 'any'})
    )
    
    unit_price = forms.DecimalField(
        label="Τιμή Μον.", 
        disabled=True, 
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control-plaintext form-control-sm text-end'})
    )

    # --- ΝΕΟ ΠΕΔΙΟ ΓΙΑ ΤΗΝ ΕΚΠΤΩΣΗ ---
    discount_percentage = forms.DecimalField(
        label="Έκπτ. %",
        initial=0,
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center'})
    )
    
   
class RetailReceiptForm(forms.Form):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False, # Το κάνουμε προαιρετικό
        widget=forms.HiddenInput()
    )
    customer_search = forms.CharField(
        label="Επιλογή Πελάτη (προαιρετικά)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Αναζήτηση πελάτη...'})
    )
RetailReceiptItemFormSet = forms.formset_factory(RetailReceiptItemForm, extra=1, can_delete=True)
class DeliveryNoteEditForm(forms.ModelForm):
    class Meta:
        model = DeliveryNote
        # Τώρα περιλαμβάνει ΟΛΑ τα πεδία που θέλουμε να αλλάζουμε
        fields = [
            'status', 'purpose', 
            'shipping_name', 'shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_vat_number',
            'carrier', 'tracking_number', 'notes'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'shipping_name': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_address': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_vat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'carrier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'π.χ. ACS Courier, Μεταφορική...'}),
            'tracking_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
class StandaloneDeliveryNoteItemForm(forms.Form):
    product_search = forms.CharField(label="Προϊόν", required=False, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput(), required=False)
    quantity = forms.DecimalField(label="Ποσότητα", initial=1, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center', 'min': '0.01'}))
    description = forms.CharField(label="Περιγραφή", required=False, help_text="Αν δεν επιλέξετε προϊόν, συμπληρώστε εδώ.", widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        description = cleaned_data.get('description')

        if not product and not description:
            raise forms.ValidationError("Πρέπει είτε να επιλέξετε ένα προϊόν είτε να συμπληρώσετε μια περιγραφή για το είδος.")
        return cleaned_data
StandaloneDeliveryNoteItemFormSet = forms.formset_factory(StandaloneDeliveryNoteItemForm, extra=1, can_delete=True)

class StandaloneDeliveryNoteForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        widget=forms.HiddenInput()
    )
    customer_search = forms.CharField(
        label="Επιλογή Πελάτη (προαιρετικά)",
        help_text="Επιλέξτε πελάτη για αυτόματη συμπλήρωση στοιχείων ή αφήστε κενό.",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = DeliveryNote
        fields = [
            'customer', 'customer_search', 'issue_date', 'purpose', 'license_plate',
            'shipping_name', 'shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_vat_number',
            'carrier', 'tracking_number',
            'notes'
        ]
        widgets = {
            'issue_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_name': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_address': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_vat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'carrier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'π.χ. ACS Courier, Μεταφορική...'}),
            'tracking_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }

    # --- ΝΕΑ ΠΡΟΣΘΗΚΗ: ΚΑΝΟΥΜΕ ΤΑ ΠΕΔΙΑ ΥΠΟΧΡΕΩΤΙΚΑ ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Λίστα με τα πεδία που θέλουμε να είναι ΥΠΟΧΡΕΩΤΙΚΑ
        required_fields = [
            'issue_date', 'purpose', 'license_plate',
            'shipping_name', 'shipping_address', 'shipping_city', 
            'shipping_postal_code', 'shipping_vat_number', 'carrier'
        ]
        
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
class InvoiceEditForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'issue_date', 'due_date', 'notes', 
            'purpose', 'carrier', 'license_plate'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'carrier': forms.TextInput(attrs={'class': 'form-control'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Διορθωμένη συνθήκη που χρησιμοποιεί την ανεξάρτητη κλάση Purpose
        if self.instance and self.instance.purpose == Purpose.SALE:
            self.fields['carrier'].required = True
            self.fields['license_plate'].required = True
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        # Εξαιρούμε πεδία που δεν θέλουμε να εμφανίζονται στη φόρμα
        exclude = ('name_normalized',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'doy': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        } 
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'order_date', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'order_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.all().order_by('name')

class PurchaseOrderItemForm(forms.ModelForm):
    # Νέο πεδίο για την αναζήτηση με Select2
    product_search = forms.CharField(label="Προϊόν", required=False, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))

    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity', 'cost_price']
        widgets = {
            'product': forms.HiddenInput(), # Κρύβουμε το πεδίο που αποθηκεύει το ID
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center quantity-field', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm text-end cost-price-field', 'step': '0.01'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True).order_by('name')


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True
)
class ReceivePOItemForm(forms.Form):
    """
    Μια φόρμα για ένα μεμονωμένο είδος σε μια παραλαβή.
    Τα περισσότερα πεδία είναι disabled, καθώς είναι μόνο για εμφάνιση.
    """
    # Χρειαζόμαστε ένα κρυφό πεδίο για να ξέρουμε σε ποιο PurchaseOrderItem αναφερόμαστε
    purchase_order_item_id = forms.IntegerField(widget=forms.HiddenInput())

    product_name = forms.CharField(
        label="Προϊόν", 
        disabled=True, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control-plaintext form-control-sm'})
    )
    quantity_ordered = forms.DecimalField(
        label="Ποσ. Παραγγελίας", 
        disabled=True, 
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control-plaintext form-control-sm text-center'})
    )
    quantity_already_received = forms.DecimalField(
        label="Ήδη Παραλήφθηκε", 
        disabled=True, 
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control-plaintext form-control-sm text-center'})
    )
    quantity_to_receive = forms.DecimalField(
        label="Ποσότητα Παραλαβής",
        required=False, # Το κάνουμε false για να μην βγάζει σφάλμα αν ο χρήστης δεν συμπληρώσει τίποτα
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center', 'step': 'any'})
    )

    def clean_quantity_to_receive(self):
        # Εξασφαλίζουμε ότι αν το πεδίο είναι κενό, θα αντιμετωπιστεί ως 0
        return self.cleaned_data['quantity_to_receive'] or Decimal('0.00')


# Δημιουργούμε το FormSet με βάση την παραπάνω φόρμα
ReceivePOItemFormSet = formset_factory(ReceivePOItemForm, extra=0)                                                                  