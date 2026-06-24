from fastapi import HTTPException, status


class EducationalLevelNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Уровень образования с указанным id не найден.'
        )


class EducationalLevelNameIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Данный уровень образования уже существует.'
        )


class EducationalFormNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Форма образования с указанным id не найдена.'
        )


class EducationalFormNameIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Данная форма образования уже существует.'
        )


class ActivityTypeNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Вид учебных занятий с указанным id не найден.'
        )


class ActivityTypeNameIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Данный вид учебных занятий уже существует.'
        )


class CompetencyGroupNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Группа компетенций с указанным id не найдена.'
        )


class CompetencyGroupNameIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Данная группа компетенций уже существует.'
        )


class CompetencyNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Компетенция с указанным id не найдена.'
        )


class ControlTypeNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Вид контроля дисциплин с указанным id не найден.'
        )


class ControlTypeNameIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Данный вид контроля дисциплин уже существует.'
        )


class DepartmentNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафедра с указанным id не найдена.'
        )


class DepartmentNameIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Кафедра с таким наименованием уже существует.'
        )


class DepartmentShortNameIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Кафедра с таким кратким наименованием уже существует.'
        )


class DepartmentIsNotActualException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Кафедра неактуальна, дисциплину к ней нельзя привязать.'
        )


class DirectionNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Направление подготовки с указанным id не найдено.'
        )


class DirectionNameIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Данное направление подготовки уже существует.'
        )


class DisciplineBlockNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Блок дисциплины с указанным id не найден.'
        )


class DisciplineNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Дисциплина с указанным id не найдена.'
        )


class DisciplineNameIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Дисциплина с таким наименованием уже существует.'
        )


class DisciplineShortNameIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Дисциплина с таким кратким наименованием уже существует.'
        )


class DisciplineBlockCompetencyNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Записи о связи блока дисциплины и компетенции с указанным id не найдено.'
        )


class DirectionMapCoreNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Записи о связи направления подготовки и ядра карты с указанным id не найдено.'
        )


class IndicatorNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Индикатор дисциплины с указанным id не найден.'
        )


class IndicatorCodeIsNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Индикатор дисциплины с таким кодом уже существует.'
        )


class MapCoreNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ядро карты с указанным id не найдено.'
        )
