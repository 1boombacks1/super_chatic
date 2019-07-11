from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class Post:
    #id пользователя
    user: str
    #date:
    text: str

    def __init__(self, user:str, text: str):
        self.user = user
        self.text = text

    def __str__(self):
        return f"{self.user}: {self.text}"


class Client(Protocol):
    ip: str = None
    login: str = None
    factory: 'Chat'

    def __init__(self, factory):
        #Инициалищация фабрики клиента

        self.factory = factory


    def __eq__(self,other):
        #сравнение объектов по их логину
        self.login.lower() == other.login.lower()


    def connectionMade(self):
        # Oбработчик подключения нового клиента

        self.ip = self.transport.getHost().host
        self.factory.clients.append(self)
        print(f"Client connected: {self.login}")
        self.transport.write("Welcome to the pidorski chat v.0.2\n".encode())



    def dataReceived(self, data: bytes):
        # Обработчие нового сообщения от клиента

        message = data.decode().replace('\n', '')

        if self.login is not None:

            new_post = Post(self.login, message)
            self.factory.posts.append(new_post)

            self.factory.notify_all_users(new_post)

            print(new_post)
        else:
            if message.startswith("login:"):
                self.login = message.replace("login:", "")

                duplicate_user = self.factory.clients.count(self)

                if duplicate_user == 1:
                    notification = f"New user connected : {self.login}"
                    self.factory.notify_all_users(notification)
                    print(notification)

                    #формируем историю сообщения для новго пользователя
                    last_posts = self.get_history(3)
                    history = self.format_history(last_posts)

                    self.factory.notify_current_users(self, history)
                else:
                    print(f"Error: Duplicate user = {self.login}")
                    self.factory.clients.remove(self)
                    self.factory.notify_current_users(self, "Access deneid")
            else:
                print("Error: invalid client login")

    def get_history(self, amount: int = 10):
        return self.factory.posts[amount * (-1):]


    def format_history(self, posts: list):
        if len(posts) > 0:
            return '\n'.join(str(p) for p in posts) + "\n" + "*" * 20 + "\n"
        else:
            return "No one has written here...\n"


    def connectionLost(self, reason=None):
        #Обработчик отключения клиента
        self.factory.clients.remove(self)
        print(f"Client disconnected: {self.login}")


class Chat(Factory):
    clients: list
    posts: list

    def __init__(self):
        #Инициализация сервера
        self.clients = []
        self.posts = []
        print("*" * 10, "\nStart server \nCompleted [OK]")



    def startFactory(self):
        #информация о состоянии сервера

        print("\n\nStart listening for the clients...")


    def buildProtocol(self, addr):
        #Инициализация нового клиента

        return Client(self)


    def notify_all_users(self,data: str):
        #Отправка сообщенний всем текущим пользовотелям

        for user in self.clients:
            user.transport.write(f"{data}\n".encode())


    @staticmethod
    def notify_current_users(user: Client, data: str):
        user.transport.write(f"{data}\n".encode())




if __name__ == '__main__':
    reactor.listenTCP(7410, Chat())
    reactor.run()
