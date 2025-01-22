import uuid

class User:
    def __init__(self):
        self.user_id = str(uuid.uuid4())
        self.weight = None
        self.height = None
        self.age = None
        self.gender = None
        self.activity = None
        self.city = None
        self.water_goal = None
        self.calorie_goal = None
        self.logged_water = 0 
        self.logged_calories = 0
        self.burned_calories = 0

    def update_data(self, weight=None, height=None, age=None, gender=None, activity=None, city=None, water_goal=None, calorie_goal=None):
        if weight is not None:
            self.weight = weight
        if height is not None:
            self.height = height
        if age is not None:
            self.age = age
        if gender is not None:
            self.gender = gender
        if activity is not None:
            self.activity = activity
        if city is not None:
            self.city = city
        if water_goal is not None:
            self.water_goal = water_goal
        if calorie_goal is not None:
            self.calorie_goal = calorie_goal

    def log_water(self, amount: float): # количество выпитой воды
  
        if amount < 0:
            raise ValueError("Объем выпитой воды всегда положительный. Вводите данные внимательно!")
        
        self.logged_water += amount

    def add_water(self, amount: float): #Добавляем воду
        self.water_goal += amount


    def total_water_ml(self) -> float: # Сумма всего выпитого количества жидкости
        return self.logged_water

    def reset_water(self):     #Обнуляем количество выпитой воды
        self.logged_water = 0

    def log_food(self, amount: float): # Учитываем потребленные каллории
        self.logged_calories += amount

    def total_calories_ccal(self) -> float:      #считаем общее количество каллорий
        return self.logged_calories
    
    def log_workout(self, calories_burned: float) -> float: #Данные по количеству калорий которые клиент сжжог
        self.burned_calories += calories_burned
    

    def get_profile(self):
        return {
            "user_id": self.user_id,
            "weight": self.weight,
            "height": self.height,
            "age": self.age,
            "activity": self.activity,
            "city": self.city,
            "water_goal": self.water_goal,
            "calorie_goal": self.calorie_goal,
            "logged_water": self.logged_water,
            "logged_calories": self.logged_calories,
            "burned_calories": self.burned_calories,
        }