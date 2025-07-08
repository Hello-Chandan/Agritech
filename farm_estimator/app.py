from flask import Flask, render_template, request

app = Flask(__name__)


crop_data = {
    "rice": {"seed_cost": 2000, "labor_cost": 5000, "days": 150, "chemical_cost": 3000, "organic_cost": 4000, "selling_price": 2000, "yield_per_acre": 30},
    "wheat": {"seed_cost": 1500, "labor_cost": 4000, "days": 90, "chemical_cost": 2500, "organic_cost": 3500, "selling_price": 2100, "yield_per_acre": 25},
    "brinjal": {"seed_cost": 3000, "labor_cost": 6000, "days": 150, "chemical_cost": 4000, "organic_cost": 5000, "selling_price": 2000, "yield_per_acre": 200},
    "potato": {"seed_cost": 2500, "labor_cost": 5500, "days": 120, "chemical_cost": 3500, "organic_cost": 4500, "selling_price": 2400, "yield_per_acre": 90},
    "mustard": {"seed_cost": 1800, "labor_cost": 3500, "days": 80, "chemical_cost": 2000, "organic_cost": 3000, "selling_price": 2300, "yield_per_acre": 80},
    "onion": {"seed_cost": 2200, "labor_cost": 5000, "days": 110, "chemical_cost": 3000, "organic_cost": 4000, "selling_price": 2300, "yield_per_acre": 100},
    "strawberry": {"seed_cost": 5000, "labor_cost": 8000, "days": 180, "chemical_cost": 6000, "organic_cost": 7000, "selling_price": 2400, "yield_per_acre": 35},
    "tomato": {"seed_cost": 2500, "labor_cost": 8000, "days": 110, "chemical_cost": 4000, "organic_cost": 8000, "selling_price": 2500, "yield_per_acre": 200}
}

chemicals = {
    "rice": {
        "conventional": ["Urea", "DAP", "MOP", "Zinc Sulfate"],
        "organic": ["Vermicompost", "Neem Cake", "Jeevamrutha"]
    },
    "wheat": {
        "conventional": ["DAP", "Urea", "Potash", "Sulfur"],
        "organic": ["Farmyard Manure", "Panchagavya", "Rock Phosphate"]
    },
    "brinjal": {
        "conventional": ["NPK", "Calcium Nitrate", "Micronutrient Mix", "Imidacloprid"],
        "organic": ["Compost", "Fish Amino Acid", "Trichoderma"]
    },
    "potato": {
        "conventional": ["NPK", "Magnesium Sulfate", "Chlorpyriphos", "Mancozeb"],
        "organic": ["Green Manure", "Wood Ash", "Bordeaux Mixture"]
    },
    "mustard": {
        "conventional": ["SSP", "Urea", "Boron", "Lambda-cyhalothrin"],
        "organic": ["Mustard Cake", "Beejamrutha", "Dasagavya"]
    },
    "onion": {
        "conventional": ["NPK", "Ammonium Sulfate", "Zinc", "Chlorothalonil"],
        "organic": ["Onion Peels Compost", "Garlic Extract", "Cow Urine"]
    },
    "strawberry": {
        "conventional": ["NPK", "Calcium Nitrate", "Micronutrients", "Abamectin"],
        "organic": ["Straw Mulch", "Compost Tea", "Seaweed Extract"]
    },
    "tomato": {
        "conventional": ["NPK", "Calcium Nitrate", "Micronutrients", "Emamectin Benzoate"],
        "organic": ["Tomato Waste Compost", "Panchagavya", "Neem Oil"]
    }
}

irrigation_required_crops = ["rice", "wheat", "onion", "potato", "brinjal", "strawberry", "tomato"]
machinery_required_crops = ["rice", "wheat", "potato", "onion", "brinjal", "strawberry", "tomato"]

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/result', methods=['POST'])
def result():
    mode = request.form.get('mode', 'acre')

    try:
        name = request.form['name']
        age = request.form['age']
        village = request.form['village']
        land_type = request.form['land1']
        lease_cost = float(request.form.get('land2', 0))
        land_size = float(request.form['land_size'])
        land_unit = request.form['land_unit']
        budget = float(request.form['budget'])
        crop = request.form['crop']
        chemical_use = request.form['chemical']
        farming_type = request.form['type']
        selling_price = float(request.form['selling_price'])

        conversion_factor = 0.33 if land_unit == 'bigha' else 1
        land_size_acres = land_size * conversion_factor

        if mode == 'bigha' and request.form.get('total_mun'):
            total_mun = float(request.form['total_mun'])
            expected_yield = total_mun * land_size * 0.4
        elif request.form.get('expected_yield'):
            yield_per_acre = float(request.form['expected_yield'])
            expected_yield = yield_per_acre * land_size_acres
        else:
            yield_per_acre = crop_data[crop]['yield_per_acre']
            expected_yield = yield_per_acre * land_size_acres

        if farming_type == 'organic':
            chemical_use = 'no'
            expected_yield *= 0.85

        expected_revenue = selling_price * expected_yield
        crop_info = crop_data[crop]

        seed_cost = crop_info['seed_cost'] * land_size_acres
        labor_cost = crop_info['labor_cost'] * land_size_acres
        days_needed = crop_info['days']

        if chemical_use == 'yes':
            chemical_name = ', '.join(chemicals[crop]['conventional'])
            chemical_cost = crop_info['chemical_cost'] * land_size_acres
        else:
            chemical_name = 'None'
            chemical_cost = 0

        if farming_type == 'organic':
            if land_unit == 'bigha':
                organic_cost_per_bigha = crop_info['organic_cost'] * 0.33
                additional_cost = organic_cost_per_bigha * land_size
            else:
                additional_cost = crop_info['organic_cost'] * land_size_acres
        else:
            additional_cost = 0

        if land_unit == 'bigha':
            irrigation_cost = 600 * land_size if crop in irrigation_required_crops else 0
            transport_cost = 400 * land_size
            machinery_cost = 700 * land_size if crop in machinery_required_crops else 0
        else:
            irrigation_cost = 1800 * land_size if crop in irrigation_required_crops else 0
            transport_cost = 1200 * land_size
            machinery_cost = 2000 * land_size if crop in machinery_required_crops else 0

        total_cost = seed_cost + labor_cost + chemical_cost + additional_cost + lease_cost + irrigation_cost + transport_cost + machinery_cost

        min_cost = 15000 * land_size_acres
        if total_cost < min_cost:
            total_cost = min_cost

        profit = expected_revenue - total_cost
        profit_margin = (profit / expected_revenue) * 100 if expected_revenue > 0 else 0
        roi_percentage = (profit / total_cost) * 100 if total_cost > 0 else 0
        roi_in_rupees = expected_revenue - budget

        budget_warning = f"\u26a0\ufe0f Your budget is \u20b9{budget:,.2f}, but the estimated cost is \u20b9{total_cost:,.2f}." if budget < total_cost else ""
        optimistic_warning = "\u26a0\ufe0f This looks too profitable. Please recheck yield and selling price." if roi_percentage > 150 else ""

        result_data = {
            'name': name,
            'age': age,
            'village': village,
            'land_type': land_type.capitalize(),
            'lease_cost': f"\u20b9{lease_cost:,.2f}",
            'land_size': land_size,
            'land_unit': land_unit,
            'land_size_acres': f"{land_size_acres:.2f}",
            'budget': f"\u20b9{budget:,.2f}",
            'crop': crop.capitalize(),
            'chemical_use': chemical_use.capitalize(),
            'chemical_name': chemical_name,
            'chemical_cost': f"\u20b9{chemical_cost:,.2f}" if chemical_cost else "None",
            'farming_type': farming_type.capitalize(),
            'seed_cost': f"\u20b9{seed_cost:,.2f}",
            'labor_cost': f"\u20b9{labor_cost:,.2f}",
            'days_needed': days_needed,
            'additional_cost': f"\u20b9{additional_cost:,.2f}" if additional_cost else "None",
            'irrigation_cost': f"\u20b9{irrigation_cost:,.2f}" if irrigation_cost else "Not Used",
            'transport_cost': f"\u20b9{transport_cost:,.2f}",
            'machinery_cost': f"\u20b9{machinery_cost:,.2f}" if machinery_cost else "Not Used",
            'total_cost': f"\u20b9{total_cost:,.2f}",
            'expected_yield': f"{expected_yield:.2f} quintals of {crop}",
            'yield_per_acre': f"{expected_yield / land_size_acres:.2f} quintals/acre" if land_size_acres else "N/A",
            'expected_revenue': f"\u20b9{expected_revenue:,.2f}",
            'selling_price': f"\u20b9{selling_price:,.2f} per quintal of {crop}",
            'profit': f"\u20b9{profit:,.2f}",
            'profit_margin': f"{profit_margin:.2f}%",
            'roi_percentage': f"{roi_percentage:.2f}%",
            'roi_in_rupees': f"\u20b9{roi_in_rupees:,.2f}"
        }

        return render_template('result.html', data=result_data, budget_warning=budget_warning, optimistic_warning=optimistic_warning)

    except Exception as e:
        return f"An error occurred: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)
