def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    return weight_kg / (height_m ** 2)

def bmi_label(bmi):
    if bmi < 18.5: return "Below adult reference range"
    if bmi < 25: return "Adult reference range"
    if bmi < 30: return "Above adult reference range"
    return "High adult BMI range"
