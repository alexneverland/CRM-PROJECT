# core/context_processors.py

from .models import UserProfile

def hex_to_rgb_string(hex_color):
    """Μετατρέπει ένα hex χρώμα (π.χ. #0dcaf0) σε string '13, 202, 240'."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return '13, 202, 240' # Default σε περίπτωση λάθους
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'{r}, {g}, {b}'
    except ValueError:
        return '13, 202, 240' # Default σε περίπτωση λάθους


def theme_colors_processor(request):
    default_theme = {
        'PRIMARY_COLOR': '#0dcaf0',
        'BACKGROUND_COLOR': '#fffaf5',
        'SIDEBAR_COLOR': '#eef8ff',
    }

    theme = default_theme.copy() # Ξεκινάμε με τα default

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            theme['PRIMARY_COLOR'] = profile.primary_color
            theme['BACKGROUND_COLOR'] = profile.background_color
            theme['SIDEBAR_COLOR'] = profile.sidebar_color
        except UserProfile.DoesNotExist:
            pass # Αν δεν υπάρχει προφίλ, απλά μένουν τα default
    
    # Προσθέτουμε την RGB τιμή στο dictionary που στέλνουμε στο template
    theme['PRIMARY_COLOR_RGB'] = hex_to_rgb_string(theme['PRIMARY_COLOR'])
    
    return {'theme': theme}