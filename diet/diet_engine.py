
def get_diet_plan(condition):
    plans = {
        'Diabetes':['Oats','Brown Rice','Vegetables'],
        'Heart Disease':['Low Sodium Foods','Fruits','Whole Grains']
    }
    return plans.get(condition,['Balanced Diet'])
