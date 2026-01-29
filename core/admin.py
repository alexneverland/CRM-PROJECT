# core/admin.py
from django.contrib import admin
from .models import (
    Customer,
    Product,
    Order,        # Προστέθηκε για καταχώρηση
    OrderItem,    # Προστέθηκε για καταχώρηση
    StockReceipt, # Προστέθηκε για καταχώρηση
    ActivityLog,   # <<< ΠΡΟΣΤΕΘΗΚΕ ΕΔΩ ΤΟ ActivityLog
    Payment,
    SalesRepresentative, Supplier, PurchaseOrder, PurchaseOrderItem
)   
from django.utils.html import format_html
from django.urls import reverse

# # Inline για τα είδη τιμολογίου (ΣΧΟΛΙΑΣΜΕΝΟ ΠΡΟΣΩΡΙΝΑ)
# # class InvoiceItemInline(admin.TabularInline):
# #     model = InvoiceItem # Χρειάζεται το μοντέλο InvoiceItem να υπάρχει
# #     extra = 1

# # Admin για Τιμολόγια (ΣΧΟΛΙΑΣΜΕΝΟ ΠΡΟΣΩΡΙΝΑ)
# # class InvoiceAdmin(admin.ModelAdmin):
# #     list_display = ('customer', 'date', 'total')
# #     inlines = [InvoiceItemInline] # Χρειάζεται το InvoiceItemInline
@admin.register(SalesRepresentative)
class SalesRepresentativeAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'phone', 'commission_rate')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    autocomplete_fields = ['user']

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = "Ονοματεπώνυμο Πωλητή"
# Admin για Πελάτες
@admin.register(Customer) # Χρήση decorator για την καταχώρηση
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'company_name', 'code']
    list_display = ('code', 'first_name', 'last_name', 'email', 'phone', 'city', 'search_link')
    readonly_fields = ('code',)
    list_per_page = 20 # Προσθήκη για καλύτερη σελιδοποίηση

    def search_link(self, obj):
        url = reverse('customer_list')
        return format_html(f'<a href="{url}" target="_blank">🔍 Αναζήτηση Πελατών</a>')
    search_link.short_description = 'Αναζήτηση (Εφαρμογή)'

# Admin για Προϊόντα
@admin.register(Product) # Χρήση decorator
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'stock_quantity', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'unit_of_measurement')
    list_per_page = 20

# Admin για Είδη Παραγγελίας (αν θέλουμε να τα βλέπουμε και ξεχωριστά)
# Συνήθως διαχειρίζονται μέσω inline στις Παραγγελίες
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('total_price',) # Το total_price υπολογίζεται αυτόματα

# Inline για τα OrderItem μέσα στο OrderAdmin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1 # Πόσες κενές φόρμες για νέα είδη θα εμφανίζονται
    readonly_fields = ('total_price',)
    # autocomplete_fields = ['product'] # Αν έχεις πολλά προϊόντα, για καλύτερη επιλογή

# Admin για Παραγγελίες
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'order_date', 'status', 'total_amount_display')
    list_filter = ('status', 'order_date', 'customer')
    search_fields = ('order_number', 'customer__first_name', 'customer__last_name', 'customer__company_name')
    readonly_fields = ('order_number', 'total_amount') # Αυτά δημιουργούνται αυτόματα
    inlines = [OrderItemInline] # Για να επεξεργαζόμαστε τα είδη μέσα στην παραγγελία
    date_hierarchy = 'order_date' # Για πλοήγηση βάσει ημερομηνίας
    list_per_page = 20

    def total_amount_display(self, obj):
        return f"{obj.total_amount} €"
    total_amount_display.short_description = "Συνολικό Ποσό"

# Admin για Παραλαβές Αποθέματος
@admin.register(StockReceipt)
class StockReceiptAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_added', 'date_received', 'user_who_recorded_display')
    list_filter = ('date_received', 'user_who_recorded', 'product')
    search_fields = ('product__name', 'notes', 'user_who_recorded__username')
    autocomplete_fields = ['product'] # Καλό για επιλογή προϊόντος
    date_hierarchy = 'date_received'
    list_per_page = 20

    def user_who_recorded_display(self, obj):
        return str(obj.user_who_recorded) if obj.user_who_recorded else "N/A"
    user_who_recorded_display.short_description = "Χρήστης Καταχώρησης"


# --- ΚΑΤΑΧΩΡΗΣΗ ΓΙΑ ΤΟ ActivityLog ---
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user_display', 'action_type', 'linked_object_display', 'details_summary')
    list_filter = ('action_type', 'user', 'action_time', 'content_type')
    search_fields = ('object_repr', 'details', 'user__username')
    readonly_fields = (
        'user', 'action_time', 'action_type',
        'content_type', 'object_id', 'linked_object',
        'object_repr', 'details'
    )

    def user_display(self, obj):
        return str(obj.user) if obj.user else "N/A" # Ή "Σύστημα" αν προτιμάς
    user_display.short_description = "Χρήστης"

    def linked_object_display(self, obj):
        if obj.linked_object:
            # Προσπαθούμε να πάρουμε μια καλή αναπαράσταση του αντικειμένου
            # Αν υπάρχει το object_repr που αποθηκεύσαμε, το χρησιμοποιούμε
            if obj.object_repr:
                return obj.object_repr
            # Αλλιώς, προσπαθούμε να πάρουμε το str() του συνδεδεμένου αντικειμένου
            try:
                return str(obj.linked_object)
            except Exception: # Αν για κάποιο λόγο αποτύχει το str()
                return f"{obj.content_type} (ID: {obj.object_id})"
        return "N/A" # Για ενέργειες χωρίς συνδεδεμένο αντικείμενο (π.χ. login)
    linked_object_display.short_description = "Σχετιζόμενο Αντικείμενο"

    def details_summary(self, obj):
        if obj.details:
            return (obj.details[:75] + '...') if len(obj.details) > 75 else obj.details
        return "-" # Εμφάνιση παύλας αντί για κενό
    details_summary.short_description = "Λεπτομέρειες (Σύνοψη)"

    def has_add_permission(self, request):
        return False # Απαγορεύουμε την προσθήκη ActivityLog από το admin

    def has_change_permission(self, request, obj=None):
        return False # Απαγορεύουμε την τροποποίηση ActivityLog από το admin

    # def has_delete_permission(self, request, obj=None):
    #     # Επίτρεψε τη διαγραφή μόνο σε superusers για λόγους συντήρησης αν χρειαστεί
    #     return request.user.is_superuser

# admin.site.register(Invoice, InvoiceAdmin) # ΣΧΟΛΙΑΣΜΕΝΟ ΠΡΟΣΩΡΙΝΑ
# --- ΚΑΤΑΧΩΡΗΣΗ ΓΙΑ ΤΟ ΜΟΝΤΕΛΟ PAYMENT ---
@admin.register(Payment)

class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_number', # Νέο πεδίο
        'payment_date', 
        'customer_link', 
        'order_link', 
        'amount_paid', 
        'payment_method', 
        'reference_number', # Εξωτερικός Αρ. Αναφοράς
        'recorded_by_user_display' # Χρησιμοποιούμε τη μέθοδο για εμφάνιση username
    )
    list_filter = ('payment_date', 'payment_method', 'customer', 'value_date', 'recorded_by')
    search_fields = (
        'receipt_number', # Νέο πεδίο
        'customer__first_name', 
        'customer__last_name', 
        'customer__company_name', 
        'order__order_number', 
        'reference_number', 
        'notes'
    )
    autocomplete_fields = ['customer', 'order']
    date_hierarchy = 'payment_date'
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('receipt_number', 'customer', 'order', 'payment_date', 'amount_paid', 'payment_method')
        }),
        ('Προαιρετικές Πληροφορίες & Καταγραφή', { # Ενοποίησα την επικεφαλίδα
            'classes': ('collapse',),
            'fields': ('value_date', 'reference_number', 'notes', 'recorded_by') # Το recorded_by εδώ θα είναι επιλέξιμο
        }),
    )
    readonly_fields = ('receipt_number',) # Το receipt_number είναι πάντα readonly καθώς γεννιέται αυτόματα

    def customer_link(self, obj):
        if obj.customer:
            link = reverse("admin:core_customer_change", args=[obj.customer.id])
            return format_html('<a href="{}">{}</a>', link, obj.customer)
        return "-"
    customer_link.short_description = 'Πελάτης'
    customer_link.admin_order_field = 'customer'

    def order_link(self, obj):
        if obj.order:
            link = reverse("admin:core_order_change", args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', link, obj.order.order_number)
        return "-"
    order_link.short_description = 'Παραγγελία'
    order_link.admin_order_field = 'order'
    
    def recorded_by_user_display(self, obj): # Μέθοδος για εμφάνιση στο list_display
        return obj.recorded_by.username if obj.recorded_by else "N/A"
    recorded_by_user_display.short_description = 'Καταχώρηση Από'
    recorded_by_user_display.admin_order_field = 'recorded_by__username'

    # Οι μέθοδοι που ενεργοποίησες για αυτόματη συμπλήρωση/κλείδωμα του recorded_by
    # όταν δημιουργείται νέα πληρωμή ΑΠΕΥΘΕΙΑΣ ΑΠΟ ΤΟ ADMIN:
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj: # Αν είναι νέα πληρωμή (δημιουργία)
            if 'recorded_by' in form.base_fields: # Έλεγχος αν το πεδίο υπάρχει στη φόρμα
                form.base_fields['recorded_by'].initial = request.user
                form.base_fields['recorded_by'].disabled = True # Κάνει το πεδίο μη επεξεργάσιμο
        return form
    
    def save_model(self, request, obj, form, change):
        if not change: # Αν είναι νέα εγγραφή (change is False for new objects)
            obj.recorded_by = request.user # Αυτόματη ανάθεση του χρήστη που την καταχωρεί
        super().save_model(request, obj, form, change)
class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    autocomplete_fields = ['product']
    readonly_fields = ('total_cost',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'supplier', 'order_date', 'status', 'total_amount')
    list_filter = ('status', 'supplier', 'order_date')
    search_fields = ('po_number', 'supplier__name')
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ('po_number', 'total_amount')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    search_fields = ['name', 'contact_person', 'vat_number']
    list_display = ('name', 'phone', 'email', 'contact_person')        
