import math

def tdee_calculator(gender, age, height, weight, activity_level):
    bmr = 0
    tdee = 0
    multiplier = 0
    height = float(height)
    weight = float(weight)
    activity_level = int(activity_level)

    if activity_level == 1:
        multiplier = 1.2
    elif activity_level == 2:
        multiplier = 1.375
    elif activity_level == 3:
        multiplier = 1.55
    elif activity_level == 4:
        multiplier = 1.725
    elif activity_level == 5:
        multiplier = 1.9
    else:
        print("請你輸入你的活動量")

    if gender== 2: #female
        bmr = (-161 + (10 * weight) + (6.25 * height) - (5 * int(age)))
        tdee = bmr * multiplier
    elif  gender== 1: #male
        bmr = (5 + (10 * weight) + (6.25 * height) - (5 * int(age)))
        tdee = bmr * multiplier


    #result=bmr
    #result2=tdee
    print(bmr)
    print(tdee)
    return bmr,tdee


if __name__ == '__main__':

    '''
    tdee_calculator(0, 23, 160, 49, 3)
    '''









