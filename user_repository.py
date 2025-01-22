from user import User

class UserRepository:
    def __init__(self):
        self.users = {}
        self.current_user = None

    def create_add_new_user(self):
        new_user = User()
        self.users[new_user.user_id] = new_user
        self.current_user = new_user.user_id
        return new_user.user_id

    def user_id_retern(self, user_id):
        return self.users.get(user_id)

    def add_current_user(self, user_id):
        if user_id in self.users:
            self.current_user = user_id
        else:
            raise ValueError("Упс, что-то пошло не так, пользователь не найден.")

    def current_user_date(self):
        return self.user_id_retern(self.current_user) if self.current_user else None

    def reset_user_water(self, user_id):
        user = self.user_id_retern(user_id)
        if user:
            user.reset_water()

