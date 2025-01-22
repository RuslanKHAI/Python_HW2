from user import User
from client import openweathermap_get_weather_key
from config import MY_WEATHER_KEY

CALORIES_PER_MINUTE = {
    "бег": 10,        
    "велосипед": 8,
    "плавание": 7,
    "йога": 4,
    "силовая тренировка": 6,
    "аэробика": 9,
    "танцы": 7,
    "ходьба": 4,
    "кроссфит": 12,
    "единоборства": 10
}


def calc_goal_caloric(user: User) -> float:
    bmr = calculate_bmr(user)
    caloric_goal = bmr + (user.activity / 60) * 200  
    return round(caloric_goal)

def calculate_bmr(user: User) -> float:
    weight = user.weight
    height = user.height
    age = user.age
    gender = user.gender

    if gender == 'Мужской':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    return bmr

def calc_food_callories(callories: float, weight: float) -> float:
    return callories * weight / 100


def calc_burned_food_callories(workout_type: str, duration_minutes: float) -> float:
    return CALORIES_PER_MINUTE[workout_type] * duration_minutes


async def calc_water_goal(user: User) -> float:
    water_level = user.weight * 30
    temp = await openweathermap_get_weather_key(user.city, MY_WEATHER_KEY)

    if temp > 25:
        water_level += 500

    return water_level

