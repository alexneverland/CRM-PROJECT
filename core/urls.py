# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ΒΑΣΙΚΑ URLS ΤΟΥ CORE APP
    path('', views.home, name='home'),

    # URLS ΠΕΛΑΤΩΝ
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # URLS ΠΡΟΪΟΝΤΩΝ
    path('products/', views.product_list, name='product_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
     # --- URLS ΓΙΑ ΠΡΟΜΗΘΕΥΤΕΣ ---
    path('suppliers/', views.supplier_list_view, name='supplier_list'),
    path('suppliers/new/', views.supplier_create_view, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail_view, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit_view, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete_view, name='supplier_delete'),
    

    # --- URLS ΓΙΑ ΠΑΡΑΓΓΕΛΙΕΣ ---
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    

    path('orders/<int:order_pk>/create-invoice/', views.order_create_invoice_view, name='order_create_invoice'),

    # --- ΝΕΟ URL ΓΙΑ ΠΑΡΑΛΑΒΗ ΑΠΟΘΕΜΑΤΩΝ ---
    path('stock/receive/', views.receive_stock_view, name='receive_stock'),
    path('receive-stock/<int:po_pk>/', views.receive_po_view, name='receive_po'), 
    path('stock/receipts/', views.stock_receipt_list, name='stock_receipt_list'),
    path('stock/receipts/<int:pk>/delete/', views.stock_receipt_delete, name='stock_receipt_delete'),
     # --- URL ΓΙΑ ΤΟ ACTIVITY LOG ---
    path('activity-log/', views.activity_log_list_view, name='activity_log_list'),
    #---- URL ΓΙΑ ΕΠΕΞΕΡΓΑΣΙΑ ΧΡΗΣΤΗ
    path('management/users/', views.user_list_view, name='user_list_view'),
    path('management/users/new/', views.user_create_view, name='user_create_view'),
    path('management/users/<int:pk>/edit/', views.user_edit_view, name='user_edit_view'), 
    path('invoices/<int:pk>/edit/', views.invoice_edit_view, name='invoice_edit'),

    # --- URLS ΓΙΑ AJAX ---
    path('ajax/search_customers/', views.search_customers_ajax, name='search_customers_ajax'),
    path('ajax/search_products/', views.search_products_ajax, name='search_products_ajax'),
    path('ajax/get_product_price/', views.get_product_price_ajax, name='get_product_price_ajax'),
    path('ajax/customer_quick_add/', views.customer_quick_add_ajax, name='customer_quick_add_ajax'),
    path('ajax/get_customer_details/<int:pk>/', views.get_customer_details_ajax, name='get_customer_details_ajax'),

    path('payments/new/', views.payment_create_view, name='payment_create'), # Γενική φόρμα προσθήκης
    path('customers/<int:customer_pk>/payments/new/', views.payment_create_view, name='customer_payment_create'), # Προσθήκη πληρωμής για συγκεκριμένο πελάτη
     # --- URL ΓΙΑ AJAX ΦΟΡΤΩΣΗ ΠΑΡΑΓΓΕΛΙΩΝ ΠΕΛΑΤΗ ---
    path('ajax/get_customer_orders/<int:customer_id>/', views.get_customer_orders_ajax, name='get_customer_orders_ajax'),

    # --- URL ΓΙΑ ΟΙΚΟΝΟΜΙΚΗ ΚΑΡΤΕΛΑ ΠΕΛΑΤΗ ---
    path('customers/<int:pk>/financials/', views.customer_financial_detail_view, name='customer_financial_detail'),

     # --- URL ΓΙΑ ΑΚΥΡΩΣΗ ΠΛΗΡΩΜΗΣ ---
    path('payments/<int:pk>/cancel/', views.payment_cancel_view, name='payment_cancel'),
    
    path('payments/<int:pk>/edit/', views.payment_edit_view, name='payment_edit'),

    path('payments/<int:pk>/receipt/', views.view_payment_receipt_pdf, name='view_payment_receipt'),

    # --- URL ΓΙΑ ΛΙΣΤΑ ΟΛΩΝ ΤΩΝ ΠΛΗΡΩΜΩΝ ---
    path('payments/all/', views.all_payments_list_view, name='all_payments_list'),
    # --- URL ΓΙΑ ΕΚΤΥΠΩΣΗ ΠΑΡΑΓΓΕΛΙΑΣ ---
    path('orders/<int:pk>/print/', views.view_order_pdf, name='view_order_pdf'),
    # --- URL ΓΙΑ ΕΞΑΓΩΓΗ ΠΕΛΑΤΩΝ ΣΕ EXCEL ---
    path('customers/export/excel/', views.export_customers_to_excel, name='export_customers_excel'),
    # --- URL ΓΙΑ ΕΞΑΓΩΓΗ ΠΡΟΪΟΝΤΩΝ ΣΕ EXCEL ---
    path('products/export/excel/', views.export_products_to_excel, name='export_products_excel'),
    # --- URL ΓΙΑ ΕΞΑΓΩΓΗ ΠΑΡΑΓΓΕΛΙΩΝ ΣΕ EXCEL ---
    path('orders/export/excel/', views.export_orders_to_excel, name='export_orders_excel'),
    # --- URL ΓΙΑ ΕΞΑΓΩΓΗ ΠΛΗΡΩΜΩΝ ΣΕ EXCEL ---
    path('payments/export/excel/', views.export_payments_to_excel, name='export_payments_excel'),
     # --- URL ΓΙΑ ΕΞΑΓΩΓΗ ΠΑΡΑΛΑΒΩΝ ΣΕ EXCEL ---
    path('stock/receipts/export/excel/', views.export_stock_receipts_to_excel, name='export_stock_receipts_excel'),
    path('credit-notes/export/excel/', views.export_credit_notes_to_excel, name='export_credit_notes_excel'),
    # --- URL ΓΙΑ ΕΠΙΣΚΟΠΗΣΗ ΑΠΟΘΕΜΑΤΩΝ ---
    path('stock/overview/', views.stock_overview_list, name='stock_overview_list'),
    # --- URL ΓΙΑ ΕΞΑΓΩΓΗ ΕΠΙΣΚΟΠΗΣΗΣ ΑΠΟΘΕΜΑΤΩΝ ΣΕ EXCEL ---
    path('stock/overview/export/excel/', views.export_stock_overview_excel, name='export_stock_overview_excel'),

    path('invoices/', views.invoice_list_view, name='invoice_list'),

    path('invoices/<int:pk>/', views.invoice_detail_view, name='invoice_detail'),
    path('invoices/<int:pk>/mark-as-paid/', views.invoice_mark_as_paid_view, name='invoice_mark_as_paid'),
    path('invoices/<int:pk>/mark-as-issued/', views.invoice_mark_as_issued_view, name='invoice_mark_as_issued'),

    path('invoices/<int:pk>/cancel/', views.invoice_cancel_view, name='invoice_cancel'),
    path('orders/<int:order_pk>/create-delivery-note/', views.create_delivery_note_from_order, name='create_delivery_note_from_order'),
    path('invoices/export/excel/', views.export_invoices_to_excel, name='export_invoices_excel'),
    path('invoices/<int:pk>/cancellation-pdf/', views.view_invoice_cancellation_pdf, name='invoice_cancellation_pdf'),

    path('invoices/<int:pk>/pdf/', views.invoice_pdf_view, name='invoice_pdf'),
    path('invoices/<int:invoice_pk>/create-credit-note/', views.create_credit_note_from_invoice, name='create_credit_note'),
    path('management/sales-reps/', views.sales_rep_list_view, name='sales_rep_list'),
    path('management/sales-reps/new/', views.sales_rep_create_view, name='sales_rep_create'),
    path('management/sales-reps/<int:pk>/edit/', views.sales_rep_edit_view, name='sales_rep_edit'),
    path('management/sales-reps/<int:pk>/delete/', views.sales_rep_delete_view, name='sales_rep_delete'),
    path('management/commissions/', views.commission_report_view, name='commission_report'),
    path('profile/settings/', views.user_profile_edit_view, name='user_profile_settings'),
    path('delivery-notes/<int:pk>/cancellation-pdf/', views.view_delivery_note_cancellation_pdf, name='delivery_note_cancellation_pdf'),

    path('credit-notes/', views.credit_note_list_view, name='credit_note_list'),
    path('credit-notes/<int:pk>/', views.credit_note_detail_view, name='credit_note_detail'),
    path('credit-notes/<int:pk>/pdf/', views.credit_note_pdf_view, name='credit_note_pdf'),
    path('profile/', views.my_profile_edit_view, name='my_profile'),
    
    path('reports/', views.reporting_hub_view, name='reporting_hub'),
    path('reports/sales-by-month/', views.report_sales_by_month_view, name='report_sales_by_month'),
    path('reports/vat-analysis/', views.report_vat_analysis_view, name='report_vat_analysis'),
    path('reports/profitability/', views.report_profitability_view, name='report_profitability'),
    path('reports/sales-by-rep/', views.report_sales_by_rep_view, name='report_sales_by_rep'),
    path('reports/sales-by-city/', views.report_sales_by_city_view, name='report_sales_by_city'),

    path('retail-receipts/export/excel/', views.export_retail_receipts_to_excel, name='export_retail_receipts_excel'),
    path('pos/', views.retail_pos_view, name='retail_pos'),
    path('retail-receipts/', views.retail_receipt_list_view, name='retail_receipt_list'),
    path('retail-receipts/<int:pk>/', views.retail_receipt_detail_view, name='retail_receipt_detail'), # <<< ΝΕΟ
    path('retail-receipts/<int:pk>/pdf/', views.retail_receipt_pdf_view, name='retail_receipt_pdf'),     # <<< ΝΕΟ
    path('retail-receipts/<int:pk>/delete/', views.retail_receipt_delete_view, name='retail_receipt_delete'),
     # --- URLS ΓΙΑ ΔΕΛΤΙΑ ΑΠΟΣΤΟΛΗΣ ---
    path('delivery-notes/', views.delivery_note_list, name='delivery_note_list'),
    path('delivery-notes/<int:pk>/', views.delivery_note_detail, name='delivery_note_detail'),
    path('delivery-notes/<int:pk>/edit/', views.delivery_note_edit_view, name='delivery_note_edit'),
    path('delivery-notes/<int:pk>/pdf/', views.delivery_note_pdf_view, name='delivery_note_pdf'),
    path('delivery-notes/new/', views.standalone_delivery_note_create_view, name='standalone_delivery_note_create'),
    path('delivery-notes/<int:pk>/cancel/', views.delivery_note_cancel_view, name='delivery_note_cancel'),
    path('delivery-notes/<int:dn_pk>/create-invoice/', views.create_invoice_from_delivery_note, name='create_invoice_from_dn'),
    path('delivery-notes/<int:pk>/cancel/', views.delivery_note_cancel_view, name='delivery_note_cancel'),
    path('invoices/<int:pk>/cancellation-pdf/', views.view_invoice_cancellation_pdf, name='invoice_cancellation_pdf'),
    path('reports/customer-balance/', views.report_customer_balance_view, name='report_customer_balance'),

    path('orders/<int:pk>/copy/', views.order_copy_view, name='order_copy'),
    path('invoices/<int:pk>/create-order/', views.order_create_from_invoice_view, name='order_create_from_invoice'),
    path('ajax/orders/<int:pk>/change-status/', views.ajax_change_order_status, name='ajax_change_order_status'),
    path('ajax/products/<int:pk>/quick-stock-entry/', views.ajax_quick_stock_entry, name='ajax_quick_stock_entry'),
    path('ajax/invoices/<int:pk>/send-email/', views.ajax_send_invoice_email, name='ajax_send_invoice_email'),
    path('ajax/products/<int:pk>/history/', views.ajax_product_history_view, name='ajax_product_history'),

    # --- URLS ΓΙΑ ΕΝΤΟΛΕΣ ΑΓΟΡΑΣ ---
path('purchase-orders/', views.purchase_order_list_view, name='purchase_order_list'),
path('purchase-orders/new/', views.purchase_order_create_view, name='purchase_order_create'),
path('purchase-orders/<int:pk>/', views.purchase_order_detail_view, name='purchase_order_detail'),
path('purchase-orders/<int:pk>/edit/', views.purchase_order_edit_view, name='purchase_order_edit'),
path('purchase-orders/<int:pk>/delete/', views.purchase_order_delete_view, name='purchase_order_delete'),
path('purchase-orders/<int:pk>/pdf/', views.purchase_order_pdf_view, name='purchase_order_pdf'),
path('purchase-orders/export/excel/', views.export_purchase_orders_excel, name='export_purchase_orders_excel'),
]