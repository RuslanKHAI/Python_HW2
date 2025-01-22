from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from user_form_callories import Form, Callories
from user_repository import UserRepository
from user import User
from file_functions import calc_goal_caloric, calc_water_goal, calc_food_callories, CALORIES_PER_MINUTE, calc_burned_food_callories
from client import openfoodfacts_calories
from log_middleware import LoggingMiddleware

router = Router()
user_repository = UserRepository()
router.message.middleware(LoggingMiddleware())

@router.message(Command("start"))  # роутер для обработки команды start
async def cmd_start(message: Message):
    text = (
        "Команды доступные для выбора:\n"
        "/start - Нажмитие для начала работы с teleg-ботом.\n"
        "/set_profile - НАжмите для ввдения данных вашего профиля. Ввод отдельно по каждому параметру.\n"
        "/show_profile - Просмотр вашего профиля.\n"
        "/log_water <количество> - Внести данные о количестве выпитой воды в миллилитрах.\n"
        "/log_food <название продукта> - Внести данные о  количестве съеденных каллорий.\n"
        "/log_workout <тип тренировки> <время (мин)> - ЗВнести данные о  тренировке\n"
        "/check_progress - Просмотреть прогресс по вашему профилю."
    )
    await message.answer(text)



@router.message(Command("set_profile")) # роутер для обработки команды set_profile
async def process_height_command(message: Message, state: FSMContext):
    user_id = user_repository.create_add_new_user()
    await state.update_data(user_id=user_id)
    
    await message.answer("Укажите рост (см): ")
    await state.set_state(Form.height)


@router.message(Form.height)
async def process_weight(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    try:
        height = float(message.text)
        if height <= 0:
            raise ValueError("Рост не может быть отрицательной величиной.")
        
        user_repository.user_id_retern(user_id).update_data(height=height)
        await message.answer("Напишите ваш вес (кг):")
        await state.set_state(Form.weight)
        
    except ValueError:
        await message.answer("Вы ввелли не корректные данные: Пожалуйста, напишите повторно ваш рост.")


@router.message(Form.weight)
async def process_gender(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    try:
        weight = float(message.text)
        if weight <= 0:
            raise ValueError("Вес должен быть положительным числом.")
        
        user_repository.user_id_retern(user_id).update_data(weight=weight)

        kb = [
            [types.KeyboardButton(text="Мужской")],
            [types.KeyboardButton(text="Женский")]
        ]

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Укажите ваш пол"
        )

        await message.answer("Укажите ваш пол:", reply_markup=keyboard)
        await state.set_state(Form.gender)
        
    except ValueError:
        await message.answer("Вы допустили ошибку: Пожалуйста, введите корректный вес.")


@router.message(Form.gender)
async def process_age(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    gender = message.text
    user_repository.user_id_retern(user_id).update_data(gender=gender)
    
    await message.answer("Напишите ваш возраст (лет):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.age)


@router.message(Form.age)
async def process_activity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    try:
        age = int(message.text)
        if age < 0:
            raise ValueError("Укажите ваш возраст (положительное число).")
        
        user_repository.user_id_retern(user_id).update_data(age=age)
        await message.answer("Напишите сколько минут в день вы совершаете какие-либо упражнения:")
        await state.set_state(Form.activity)
        
    except ValueError:
        await message.answer("Не корректный ввод: Пожалуйста, укажите сколько полных лет.")



@router.message(Form.activity)
async def process_activity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    try:
        activity = int(message.text)
        if activity < 0:
            raise ValueError("Уровень активности всегда больше нуля.")
        
        user_repository.user_id_retern(user_id).update_data(activity=activity)
        
        await message.answer("Напишите ваш город:")
        await state.set_state(Form.city)
        
    except ValueError:
        await message.answer("Допущена ошибка при вводе: введите корректное положительное целое число для активности.")


@router.message(Form.city)
async def process_goal(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    city = message.text

    user = user_repository.user_id_retern(user_id)
    user.update_data(city=city)

    caloric_goal = calc_goal_caloric(user)
    water_goal = await calc_water_goal(user)

    user.update_data(calorie_goal=caloric_goal, water_goal=water_goal)

    kb = [
        [types.KeyboardButton(text="Подтвредить цель")],
        [types.KeyboardButton(text="Изменить цель")]
    ]

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Сохранить цель по калориям"
    )

    await message.answer(
        f"Напишите вашу цель по калориям: {caloric_goal:.0f} ккал. "
        f"Ваша цель по воде: {water_goal:.0f} мл. "
        "Если вам не подошла предложенная цель нажмите 'Подтвредить цель', вы можете изменить ее, для этого нажмите 'Изменить цель'.",
        reply_markup=keyboard
    )
    
    await state.set_state(Form.goal)


@router.message(Form.goal)
async def confirm_goal(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    user_input = message.text
    
    user = user_repository.user_id_retern(user_id)
    
    if user_input == "Подтвредить цель":
        water_level = await calc_water_goal(user)
        user.update_data(water_goal=water_level)
        
        await message.answer("Цель сохранена. Спасибо вам за выбор нашего бота!", reply_markup=types.ReplyKeyboardRemove())
        await cmd_start(message)  
        await state.clear()
        
    elif user_input == "Изменить цель":
        await message.answer("Напишите новое значение для цели:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.goal)  
        
    else:
        try:
            new_goal = float(user_input)
            user.update_data(calorie_goal=new_goal)
            
            water_level = await calc_water_goal(user)
            user.update_data(water_goal=water_level)
            
            await message.answer(f"Новая цель по калориям занесена в базу: {new_goal:.2f} ккал.")
            await cmd_start(message)  
            await state.clear()  
            
        except ValueError:
            await message.reply("Допущена ошибка, введите корректное значение.")


@router.message(Command("show_profile")) # роутер для обработки команды show_profile
async def process_show_profile(message: Message, state: FSMContext):
    user = user_repository.current_user_date()

    if user is None:
        await message.answer("Не удалось найти текущего пользователя.")
        return

    profile_message = (
        f"Ваш профиль:\n"
        f"Вес: {user.weight} кг\n"
        f"Рост: {user.height} см\n"
        f"Пол: {user.gender}\n"
        f"Возраст: {user.age} лет\n"
        f"Уровень активности: {user.activity} минут в день\n"
        f"Город: {user.city}\n"
        f"Цель по калориям: {user.calorie_goal} ккал\n"
        f"Цель по выпитой воде: {user.water_goal} мл\n"
        f"Выпито воды: {user.total_water_ml()} мл\n"
        f"Съедено каллорий: {user.total_calories_ccal()} ккал"
    )

    await message.answer(profile_message, reply_markup=types.ReplyKeyboardRemove())



@router.message(Command("log_water")) # роутер для обработки команды log_water
async def log_water(message: Message, state: FSMContext):
    user = user_repository.current_user_date()

    if user is None:
        await message.answer("Упс! Мы не нашли текущего пользоватя.")
        return
    
    command_text = message.text.split()
    
    if len(command_text) != 2:
        await message.answer("Напишите количество воды которые выпили сегодня для учета в системе в миллилитрах после команды. Например: /log_water 250")
        return
    
    try:
        amount = float(command_text[1])
        user.log_water(amount)
        total_water = user.total_water_ml()
        water_goal = user.water_goal - total_water
        if water_goal > 0:
            await message.answer(f"Сегодня я выпил жидкости: {total_water:.2f} мл. Чтоб достигнуть цель нужно выпить {water_goal:.2f} мл.")
        else:
            await message.answer(f"Сегодня я выпил жидкости: {total_water:.2f} мл. Вы достиглиЦель достигнута.")
            
    except ValueError:
         await message.answer("Ой, что-то пошло не так, просим вас ввести корректное число.")

@router.message(Command("log_food")) # роутер для обработки команды log_food
async def log_food(message: Message, state: FSMContext):
    command_text = message.text.split()

    if len(command_text) != 2:
        await message.answer("Напишите название продукта который вы положили в желудок. Например: /log_food banana")
        return
    
    food_name = command_text[1]

    food_data = await openfoodfacts_calories(food_name)

    if food_data is None:
        await message.answer(f"Для выбранного продукта '{food_name}' мы не нашли информацию.")
        await state.clear()
        return

    callories = food_data['calories']
    
    await state.update_data(food_callories=callories)

    await message.answer(f"{food_name} - {callories} ккал на 100 г. Сколько грамм вы съели?")
    await state.set_state(Callories.food_callories)


@router.message(Callories.food_callories)
async def process_callories(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text) 
        await state.update_data(food_weight=weight) 
        await state.set_state(Callories.food_weight)
        
    except ValueError:
        await message.answer("Ой, что-то пошло не так, просим вас ввести корректное число для веса съеденной еды.")
        return

    if weight < 0:
        await message.answer("Обратите внимание: указанный Вес еды должен быть положительным.")
        return

    data = await state.get_data()
    food_weight = data.get('food_weight')
    food_callories = data.get('food_callories')

    if food_weight is None or food_callories is None:
        await message.answer("Ой, что-то пошло не так: нам не удалось по вашему продукту получить данные о калориях или весе.")
        return

    total_cal = calc_food_callories(food_callories, food_weight)

    user = user_repository.current_user_date()
    user.log_food(total_cal)
    await message.answer(f"Записано: {total_cal} ккал")
    await cmd_start(message)  
    await state.clear()

@router.message(Command("log_workout")) # роутер для обработки команды log_workout
async def log_workout(message: types.Message):
    args = message.text.split()

    user = user_repository.current_user_date()
    
    if len(args) != 3:
        await message.answer("Для записи тренировки используйте формат: /log_workout <тип тренировки> <длительность в минутах>")
        return

    workout_type = args[1].lower()
    duration_minutes = int(args[2])

    if workout_type not in CALORIES_PER_MINUTE:
        await message.answer("Это здорово, Вы занимаетесь неизвестной нам тренировкой. ППредлагаем вам использовать следующие: " + ", ".join(CALORIES_PER_MINUTE.keys()))
        return

    calories_burned = calc_burned_food_callories(workout_type, duration_minutes)
    add_water = duration_minutes * 500 / 30

    user.log_workout(calories_burned)
    user.add_water(add_water)

    await message.answer(
        f"{workout_type.capitalize()} {duration_minutes} минут — {calories_burned} ккал.\n"
        f"Наши рекомендации: попейте {round(add_water)} мл воды."
        )
    

@router.message(Command("check_progress")) # роутер для обработки команды check_progress
async def show_progress(message: types.Message):
    user = user_repository.current_user_date()

    progress_message = (
        f"📊 Прогресс:\n"
        f"Вода:\n"
        f"- Выпито жидкости: {user.logged_water} мл из {user.water_goal} мл.\n"
        f"- Осталось выпить жидкости: {user.water_goal - user.logged_water} мл.\n"
        f"\nКалории:\n"
        f"- Потреблено: {user.logged_calories} ккал из {user.calorie_goal} ккал."
        f"- Вы сожжгли: {user.burned_calories} ккал.\n"
        f"- Итоговый результат: {user.calorie_goal - user.logged_calories + user.burned_calories} ккал.\n"
    )

    await message.answer(progress_message)
