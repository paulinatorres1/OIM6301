def calculate_bmi(weight, height):
    """Compute the BMI given weight in kg and height in meters."""
    bmi = weight / (height ** 2)
    return bmi

def classify_bmi(bmi):
    """classify the BMI value into categories."""
    if bmi >= 30:
        category = "Obese"
    elif bmi >= 25:
        category = "Overweight"
    elif bmi >= 18.5:
        category = "Normal"
    else:
        category = "Underweight"
        #print category
    return(category)

def main():
    weight = float(input("Enter your weight in kg: "))
    height = float(input("Enter your height in meters: "))
    bmi_value = calculate_bmi(weight, height)
    result = classify_bmi(bmi_value)
    print(f"Your BMI is {bmi_value:.2f}, and you category is {result}.")

main()