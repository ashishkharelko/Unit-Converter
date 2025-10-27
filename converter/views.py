from django.shortcuts import render
from django.http import JsonResponse
from .forms import ConversionForm
from .models import Unit
import logging
import requests

logger = logging.getLogger(__name__)

def index(request):
    form = ConversionForm()
    if request.method == 'GET' and 'unit_type' in request.GET:
        try:
            unit_type_id = int(request.GET.get('unit_type'))
            logger.debug(f"Fetching units for unit_type_id: {unit_type_id}")
            units = Unit.objects.filter(unit_type_id=unit_type_id).values('id', 'name')
            if not units:
                logger.warning(f"No units found for unit_type_id: {unit_type_id}")
                return JsonResponse({'from_unit': '', 'to_unit': ''}, status=404)
            unit_options = ''.join([f'<option value="{unit["id"]}">{unit["name"]}</option>' for unit in units])
            return JsonResponse({
                'from_unit': unit_options,
                'to_unit': unit_options
            })
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid unit_type_id: {request.GET.get('unit_type')} - {str(e)}")
            return JsonResponse({'from_unit': '', 'to_unit': ''}, status=400)
    return render(request, 'converter/index.html', {'form': form})

def convert(request):
    if request.method == 'POST':
        form = ConversionForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data['value']
            from_unit = form.cleaned_data['from_unit']
            to_unit = form.cleaned_data['to_unit']
            
            logger.debug(f"Converting {value} from {from_unit} to {to_unit}")

            # Initialize rates and attribution for Currency conversions
            rates_info = None
            attribution = 'Rates By <a href="https://www.exchangerate-api.com">Exchange Rate API</a>' if from_unit.unit_type.name == 'Currency' else ''
            
            # Update USD, GBP, and EUR rates if Currency conversion
            if from_unit.unit_type.name == 'Currency':
                try:
                    response = requests.get('https://open.er-api.com/v6/latest/INR')
                    response.raise_for_status()
                    data = response.json()
                    if data.get('result') == 'success':
                        rates = data['rates']
                        # Update to_base_factor for USD, GBP, EUR
                        for currency, name in [('USD', 'US Dollar (USD)'), ('GBP', 'British Pound (GBP)'), ('EUR', 'Euro (EUR)')]:
                            if currency in rates:
                                to_base_factor = 1 / rates[currency]
                                Unit.objects.filter(unit_type__name='Currency', name=name).update(to_base_factor=to_base_factor)
                                logger.debug(f"Updated {name}: {to_base_factor:.2f} INR")
                        # Refresh from_unit and to_unit to get updated rates
                        from_unit.refresh_from_db()
                        to_unit.refresh_from_db()
                        # Build rates_info for only the currencies involved
                        involved_currencies = []
                        for unit, name in [(from_unit, 'from_unit'), (to_unit, 'to_unit')]:
                            if unit.name in ['US Dollar (USD)', 'British Pound (GBP)', 'Euro (EUR)']:
                                currency_code = unit.name.split('(')[-1].strip(')')
                                rate = 1 / rates[currency_code]
                                involved_currencies.append(f"{currency_code}: {rate:.2f} INR")
                        if involved_currencies:
                            rates_info = ", ".join(involved_currencies)
                        else:
                            rates_info = None  # No API-fetched currencies involved
                    else:
                        logger.warning("API error, using existing rates")
                        rates_info = "Using fallback rates for USD, GBP, EUR"
                except requests.RequestException as e:
                    logger.warning(f"Failed to fetch rates: {str(e)}, using existing rates")
                    rates_info = "Using fallback rates for USD, GBP, EUR"

            # Handle temperature conversions
            if from_unit.unit_type.name == 'Temperature':
                # Convert to Celsius (base unit)
                if from_unit.name == 'Celsius':
                    base_value = value
                elif from_unit.name == 'Fahrenheit':
                    base_value = (value - 32) * 5/9
                elif from_unit.name == 'Kelvin':
                    base_value = value - 273.15
                
                # Convert from Celsius to target unit
                if to_unit.name == 'Celsius':
                    result = base_value
                elif to_unit.name == 'Fahrenheit':
                    result = (base_value * 9/5) + 32
                elif to_unit.name == 'Kelvin':
                    result = base_value + 273.15
            else:
                # Standard conversion for other unit types
                base_value = value * from_unit.to_base_factor
                result = base_value / to_unit.to_base_factor
            
            return render(request, 'converter/result.html', {
                'form': form,
                'result': result,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'value': value,
                'rates_info': rates_info,
                'attribution': attribution
            })
        else:
            logger.warning(f"Form invalid: {form.errors}")
    else:
        form = ConversionForm()
    return render(request, 'converter/index.html', {'form': form})