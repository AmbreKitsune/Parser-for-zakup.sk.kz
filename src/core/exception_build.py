# TODO: ДАЖЕ НЕ ЛЕЗЬ СЮДА!!! РУКУ ОТТЯПАЕТ!
class PointException(Exception):
    ...

class ErrorIncorrectType(PointException):
    def __str__(self) -> str:
        return "Не верное значение типа запроса!"
    
class ErrorIncorrectData(PointException):
    def __str__(self) -> str:
        return "Не верно указанный тип данных!"
    
class ErrorInWorking(PointException):
    def __str__(self) -> str:
        return "Не работает, зайди потом"
    
class ErrorMissingConfigFile(PointException):
    def __str__(self) -> str:
        return "Отсутвует файл конфирации. Если вы видите эту ошибку после перезапуска программы, обратитесь к разработчику программы"
