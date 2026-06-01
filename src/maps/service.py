from src.directions.repository import DirectionsRepository
from src.map_cors.repository import MapCorsRepository
from src.direction_map_cors.repository import DirectionMapCorsRepository
from src.discipline_blocks.repository import DisciplineBlocksRepository
from src.discipline_block_competencies.repository import DisciplineBlockCompetenciesRepository
from src.disciplines.repository import DisciplinesRepository
from src.departments.repository import DepartmentsRepository
from src.control_types.repository import ControlTypesRepository
from src.competencies.repository import CompetenciesRepository
from .schemas import (
    MapLoad, MapUnload, MapCoreUnload, DisciplineBlockUnload, DisciplineUnload, DepartmentUnload, ControlTypeUnload,
    CompetencyUnload
)
from src.exceptions import DirectionNotFoundException, MapCoreNotFoundException


class MapsService:
    def __init__(
            self,
            directions_repository: DirectionsRepository,
            map_cors_repository: MapCorsRepository,
            direction_map_cors_repository: DirectionMapCorsRepository,
            discipline_blocks_repository: DisciplineBlocksRepository,
            discipline_block_competencies_repository: DisciplineBlockCompetenciesRepository,
            disciplines_repository: DisciplinesRepository,
            departments_repository: DepartmentsRepository,
            control_types_repository: ControlTypesRepository,
            competencies_repository: CompetenciesRepository
    ):
        self.directions_repository: DirectionsRepository = directions_repository
        self.map_cors_repository: MapCorsRepository = map_cors_repository
        self.direction_map_cors_repository: DirectionMapCorsRepository = direction_map_cors_repository
        self.discipline_blocks_repository: DisciplineBlocksRepository = discipline_blocks_repository
        self.discipline_block_competencies_repository: DisciplineBlockCompetenciesRepository = \
            discipline_block_competencies_repository
        self.disciplines_repository: DisciplinesRepository = disciplines_repository
        self.departments_repository: DepartmentsRepository = departments_repository
        self.control_types_repository: ControlTypesRepository = control_types_repository
        self.competencies_repository: CompetenciesRepository = competencies_repository

    def load_map(self, direction_id: int, data: MapLoad) -> None:

        if not self.directions_repository.get_by_id(direction_id):
            raise DirectionNotFoundException()

        # если есть связанные с направлением ядра карты, удаляем связи, но ядра пока остаются в БД
        if direction_map_cors := self.direction_map_cors_repository.filter_by(direction_id=direction_id):
            for direction_map_core in direction_map_cors:
                self.direction_map_cors_repository.delete(direction_map_core.id)

        for map_core in data.map_cors:
            map_core_id = map_core.id

            # если ядро существует, нужно пройтись его блокам дисциплин и удалить их
            # прежде чем удалить блоки дисциплин, нужно удалить их связи с компетенциями

            # получаем блоки дисциплин
            discipline_blocks = self.discipline_blocks_repository.filter_by(map_core_id=map_core_id)
            for discipline_block in discipline_blocks:

                # получаем связи блоков с компетенциями
                discipline_block_competencies = self.discipline_block_competencies_repository.filter_by(
                    discipline_block_id=discipline_block.id
                )

                # удаляем связи блоков с компетенциями
                for discipline_block_competency in discipline_block_competencies:
                    self.discipline_block_competencies_repository.delete(discipline_block_competency.id)

                # удаляем сам блок дисциплины
                self.discipline_blocks_repository.delete(discipline_block.id)

            # если ядро новое, просто создаем его в базе данных
            if not map_core_id:
                map_core_id = self.map_cors_repository.create({
                    'name': map_core.name,
                    'semesters_count': map_core.semesters_count
                }).id

            # привязываем ядро к карте направления
            self.direction_map_cors_repository.create({
                'direction_id': direction_id,
                'map_core_id': map_core_id
            })

            for discipline_block in map_core.discipline_blocks:
                discipline_block_id = self.discipline_blocks_repository.create({
                    'discipline_id': discipline_block.discipline_id,
                    'credit_units': discipline_block.credit_units,
                    'control_type_id': discipline_block.control_type_id,
                    'lecture_hours': discipline_block.lecture_hours,
                    'practice_hours': discipline_block.practice_hours,
                    'lab_hours': discipline_block.lab_hours,
                    'semester_number': discipline_block.semester_number,
                    'has_course_project': discipline_block.has_course_project,
                    'has_course_work': discipline_block.has_course_work,
                    'has_rz': discipline_block.has_rz,
                    'has_rgr': discipline_block.has_rgr,
                    'has_referat': discipline_block.has_referat,
                    'map_core_id': map_core_id
                }).id

                for competency in discipline_block.competencies:
                    self.discipline_block_competencies_repository.create({
                        'discipline_block_id': discipline_block_id,
                        'competency_id': competency.id
                    })

    def unload_map_core(self, map_core_id: int) -> MapCoreUnload:
        if not self.map_cors_repository.get_by_id(map_core_id):
            raise MapCoreNotFoundException()

        # получаем ядро карты
        map_core = self.map_cors_repository.get_by_id(map_core_id)

        # получаем блоки дисциплин внутри ядра
        discipline_blocks = self.discipline_blocks_repository.filter_by(map_core_id=map_core.id)

        discipline_blocks_unload = []
        for discipline_block in discipline_blocks:

            # получаем дисциплину блока
            discipline = self.disciplines_repository.get_by_id(discipline_block.discipline_id)

            # получаем кафедру дисциплины
            department = self.departments_repository.get_by_id(discipline.department_id)

            # получаем объект кафедры для выгрузки
            department_unload = DepartmentUnload.model_validate(department)

            # получаем объект дисциплины для выгрузки
            discipline_unload = DisciplineUnload(
                id=discipline.id,
                name=discipline.name,
                short_name=discipline.short_name,
                department=department_unload
            )

            # получаем вид контроля для блока дисциплины
            control_type = self.control_types_repository.get_by_id(discipline_block.control_type_id)

            # получаем вид контроля для выгрузки
            control_type_unload = ControlTypeUnload.model_validate(control_type)

            # получаем связи блока дисциплины с компетенциями
            discipline_block_competencies = self.discipline_block_competencies_repository.filter_by(
                discipline_block_id=discipline_block.id
            )

            competencies_unload = []
            for discipline_block_competency in discipline_block_competencies:
                # получаем компетенцию
                competency = self.competencies_repository.get_by_id(discipline_block_competency.competency_id)

                if not competency:
                    continue

                # формируем объект компетенции для выгрузки
                competency_unload = CompetencyUnload(
                    id=competency.id,
                    code=competency.code,
                    name=competency.name,
                    description=competency.description,
                    competency_group_id=competency.competency_group_id
                )

                # формируем список компетенций для выгрузки
                competencies_unload.append(competency_unload)

            # формируем объект блока дисциплины для выгрузки
            discipline_block_unload = DisciplineBlockUnload(
                id=discipline_block.id,
                discipline=discipline_unload,
                credit_units=discipline_block.credit_units,
                control_type=control_type_unload,
                lecture_hours=discipline_block.lecture_hours,
                practice_hours=discipline_block.practice_hours,
                lab_hours=discipline_block.lab_hours,
                semester_number=discipline_block.semester_number,
                has_course_project=discipline_block.has_course_project,
                has_course_work=discipline_block.has_course_work,
                has_rz=discipline_block.has_rz,
                has_rgr=discipline_block.has_rgr,
                has_referat=discipline_block.has_referat,
                competencies=competencies_unload
            )

            # формируем список блоков дисциплин для выгрузки
            discipline_blocks_unload.append(discipline_block_unload)

        # формируем объект ядра карты для выгрузки
        map_core_unload = MapCoreUnload(
            id=map_core.id,
            name=map_core.name,
            semesters_count=map_core.semesters_count,
            discipline_blocks=discipline_blocks_unload
        )

        return map_core_unload

    def unload_map(self, direction_id) -> MapUnload:
        if not self.directions_repository.get_by_id(direction_id):
            raise DirectionNotFoundException()

        # получаем все связанные с направлением ядра
        direction_map_cors = self.direction_map_cors_repository.filter_by(direction_id=direction_id)

        map_cors_unload = []
        for direction_map_core in direction_map_cors:

            # получаем объект ядра карты для выгрузки
            map_core_unload = self.unload_map_core(direction_map_core.map_core_id)

            # формируем список ядер карты для выгрузки
            map_cors_unload.append(map_core_unload)

        return MapUnload(map_cors=map_cors_unload)
