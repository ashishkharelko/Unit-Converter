from django import template
from django.utils.safestring import mark_safe
import re
import logging
import traceback
logger = logging.getLogger(__name__)
register = template.Library()

from django import template

register = template.Library()

@register.filter
def key_exists(dictionary, key):
    if not isinstance(dictionary, dict):
        logger.error(f"key_exists: dictionary is not a dict, got {type(dictionary)}: {dictionary}")
        return False
    return str(key).strip() in [str(k).strip() for k in dictionary.keys()]

@register.filter
def get_item1(dictionary, key):
    result = dictionary.get(str(key).strip())
    keys = [str(k).strip() for k in (dictionary.keys() if dictionary else [])]
    logger.debug(f"get_item: key='{str(key).strip()}', type(key)={type(key)}, dictionary={dictionary}, keys={keys}, result={result}")
    return result

@register.filter
def dict_key(dictionary, key):
    logger.debug(f"dict_key: key='{key}', dictionary={dictionary}")
    return dictionary[key]

@register.simple_tag
def build_cusp_key(house):
    return f"Cusp {house}"

@register.simple_tag
def get_nested_value(dictionary, key):
    logger.debug(f"get_nested_value called with dictionary={dictionary}, key={key}, type(dictionary)={type(dictionary)}, type(key)={type(key)}\nStack trace:\n{''.join(traceback.format_stack())}")
    if not dictionary:
        logger.error(f"get_nested_value: dictionary is empty or None: {dictionary}")
        return None
    if not isinstance(dictionary, dict):
        try:
            import json
            dictionary = json.loads(dictionary) if isinstance(dictionary, str) else dictionary
            logger.debug(f"Converted dictionary to {type(dictionary)}: {dictionary}")
        except (ValueError, TypeError):
            logger.error(f"get_nested_value: Failed to convert dictionary: {dictionary}")
            return None
    value = dictionary.get(str(key).strip())
    logger.debug(f"get_nested_value: Retrieved value={value}, keys in dictionary={list(dictionary.keys())}")
    return value if isinstance(value, dict) else None

@register.filter
def safely_get_item(dictionary, key):
    if not isinstance(dictionary, dict):
        return None
    # print("Ashish",dictionary.get(str(key).strip()))
    return dictionary.get(str(key).strip())  # Convert key to string and strip whitespace
# def safely_get_item(dictionary, key):
#     if not isinstance(dictionary, dict):
#         logger.error(f"safely_get_item: dictionary is not a dict, got {type(dictionary)}: {dictionary}")
#         return None
#     result = dictionary.get(str(key))
#     keys = [str(k).strip() for k in dictionary.keys()]
#     logger.debug(f"safely_get_item: key='{str(key).strip()}', type(key)={type(key)}, dictionary={dictionary}, keys={keys}, result={result}")
#     if result is None and str(key).strip() in keys:
#         logger.warning(f"safely_get_item: key='{str(key).strip()}' found in keys but returned None")
#     return result

@register.filter
def get(d, k): 
    return d.get(k, '')

@register.filter
def replace(value, arg):
    """
    Replace all occurrences of a substring in the value.
    Format: value|replace:"old:new"
    """
    old, new = arg.split(':')
    return value.replace(old, new)

@register.filter
def tex_escape(text):
    """
    Escapes special characters for LaTeX.
    """
    conversions = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde',
        '^': r'\textasciicircum',
        '\\': r'\textbackslash',
    }
    return mark_safe(''.join(conversions.get(c, c) for c in str(text)))

@register.filter
def rashi(house_data):
    return house_data.get('rashi', 'N/A')

@register.filter
def extract_rashi_number(rashi):
    """
    Extracts the rashi number from strings like 'Scorpio(8)', 'Leo(5)', or 'Leo5'.
    Returns the number as a string or None if not found.
    """
    if not rashi:
        return None
    # Debug: Log input
    print(f"extract_rashi_number input: {rashi}")
    match = re.search(r'\((\d+)\)|(\d+)$', rashi)
    if match:
        result = match.group(1) or match.group(2)
        print(f"extract_rashi_number output: {result}")
        return result
    if '(' in rashi:
        result = rashi.split('(')[1].rstrip(')')
        print(f"extract_rashi_number fallback output: {result}")
        return result
    print(f"extract_rashi_number output: None")
    return None

@register.filter
def is_equal(value1, value2):
    """
    Returns True if value1 equals value2, False otherwise.
    """
    result = str(value1).strip() == str(value2).strip()
    print(f"is_equal: '{value1}' == '{value2}' ? {result}")
    return result

@register.filter
def split(value, delimiter):
    """
    Splits a string by delimiter and returns a list.
    """
    result = value.split(delimiter) if value else []
    print(f"split: '{value}' by '{delimiter}' -> {result}")
    return result

@register.filter
def in_list(value, list_str):
    """
    Checks if value is in a comma-separated string.
    Returns True if value is in list_str, False otherwise.
    """
    if not value or not list_str:
        print(f"in_list: value={value}, list_str={list_str} -> False")
        return False
    values = [x.strip() for x in list_str.split(',')]
    result = str(value).strip() in values
    print(f"in_list: {value} in {values} ? {result}")
    return result

@register.filter
def extract_rashi_name(rashi):
    """
    Extracts the rashi name from strings like 'Leo(5)', 'Leo5', or 'Leo'.
    """
    if not rashi:
        return None
    # Match alphabetic characters at the start
    match = re.match(r'^([A-Za-z]+)', rashi)
    return match.group(1) if match else rashi

@register.filter
def clean_tithi(tithi):
    if isinstance(tithi, str) and tithi.startswith('['):
        try:
            tithi_list = ast.literal_eval(tithi)
            return tithi_list[0] if tithi_list else 'N/A'
        except (ValueError, SyntaxError):
            return 'N/A'
    return tithi

@register.filter
def house_meaning(house_num):
    meanings = {
        1: "आत्म, व्यक्तित्व, स्वास्थ्य",
        2: "धन, वाणी, परिवार",
        3: "संचार, भाई-बहन, साहस",
        4: "घर, माता, सुख",
        5: "बुद्धि, संतान, रचनात्मकता",
        6: "स्वास्थ्य, शत्रु, सेवा",
        7: "विवाह, साझेदारी, रिश्ते",
        8: "परिवर्तन, रहस्य, दीर्घायु",
        9: "भाग्य, धर्म, उच्च शिक्षा",
        10: "करियर, प्रतिष्ठा, सामाजिक स्थिति",
        11: "लाभ, मित्र, इच्छापूर्ति",
        12: "हानि, आध्यात्मिकता, एकांत"
    }
    return meanings.get(house_num, "अज्ञात")

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, {})

@register.filter
def format_date_brit(value):
    try:
        # Assuming value is in yyyy-mm-dd format
        if value and value != 'N/A':
            from datetime import datetime
            date_obj = datetime.strptime(value, '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y')
        return value  # Return original value if it's 'N/A' or invalid
    except (ValueError, TypeError):
        return value  # Return original value if conversion fails
    
@register.filter
def lookup(dictionary, key):
    """
    Custom filter to access dictionary values by key in templates.
    """
    return dictionary.index(key)

@register.filter
def mul(value, arg):
    """
    Custom filter to multiply two numbers in templates.
    Example: {{ 2|mul:10 }} returns 20
    """
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value  # Return original value if conversion fails
    
@register.filter
def extract_house_number(value):
    if not value:
        return ""
    # Use regex to extract the first number (1-12) from the string
    match = re.search(r'\d+', value)
    return match.group(0) if match else value

def decimal_to_dms(value, direction_type='lat'):
    try:
        value = float(value)
        is_positive = value >= 0
        abs_value = abs(value)
        degrees = int(abs_value)
        minutes_full = (abs_value - degrees) * 60
        minutes = int(minutes_full)
        seconds = round((minutes_full - minutes) * 60, 2)
        direction = 'N' if is_positive else 'S' if direction_type == 'lat' else 'E' if is_positive else 'W'
        return f"{degrees}° {minutes}' {seconds}\" {direction}"
    except (ValueError, TypeError):
        return ""

@register.filter
def dms(value, direction_type='lat'):
    return decimal_to_dms(value, direction_type)
    
@register.filter
def multiply(value, arg):
    return int(value) + (int(arg) * 20)
    
@register.filter
def split(value, delimiter=','):
    return value.split(delimiter)

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def has_number(cell, number):
    return str(number) in cell if cell else False
@register.filter
def add_spaces(value):
    return ' '.join(value) if value else ''

@register.filter
def highlight(value, search):
    if not search:
        return value
    value = str(value)  # Convert to string if it's an int or other type
    pattern = re.compile(re.escape(search), re.IGNORECASE)
    highlighted = pattern.sub(lambda m: f'<span class="highlight">{m.group(0)}</span>', value)
    return mark_safe(highlighted)

@register.filter
def get_dict_item(dictionary, key):
    return dictionary.get(str(key))

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def get_year_value(row, year):
    """Safe dictionary access for year columns"""
    return row.get(f'year_{year}', 0)

@register.filter
def range_filter(value):
    """Returns a range from 0 to the specified value"""
    return range(value)

@register.filter
def is_correct(user_answer, correct_answer):
    return user_answer == correct_answer

@register.filter
def get_option(question, opt):
    return getattr(question, f'option_{opt.lower()}')

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def get_item(dictionary, key_prefix):
    """
    Gets an item from dictionary using a prefix and the current year context
    Usage: {{ row|get_item:"y"|add:year }}
    """
    if hasattr(dictionary, 'get'):
        # Handle direct dictionary access
        return dictionary.get(key_prefix, 0)
    return 0

@register.filter
def get_balance_id(dictionary, key):
    return dictionary.get(key, {}).get('id', 0)

@register.filter
def sub(value, arg):
    """Subtracts the arg from the value"""
    return float(value) - float(arg)

@register.filter
def days_since(value, arg):
    """Returns days between two dates"""
    return (value - arg).days

@register.filter
def index(list_obj, i):
    return list_obj[int(i)]

@register.filter
def get_row(board, row):
    return board[int(row)]

@register.filter
def get_col(row, col):
    return row[int(col)]