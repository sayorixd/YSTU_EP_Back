# from fastapi import APIRouter, status, Path, Response
# from typing import Annotated
# from src.dependencies import MapsServiceDep
# from .schemas import MapLoad, MapUnload, MapCoreUnload
from openpyxl.styles import PatternFill

from fastapi import APIRouter, status, Path, Response
from typing import Annotated
from fastapi.responses import StreamingResponse  # <‑‑ добавили
from io import StringIO, BytesIO
import csv
from openpyxl import Workbook

from src.dependencies import MapsServiceDep
from .schemas import MapLoad, MapUnload, MapCoreUnload


router = APIRouter(
    tags=['maps']
)


@router.post(
    '/directions/{direction_id}/maps/load',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Educational map successfully loaded'},
        404: {'description': 'Direction not found'}
    },
    summary='Load the educational map into the database'
)
def load_map(direction_id: Annotated[int, Path(gt=0)], data: MapLoad, maps_service: MapsServiceDep) -> Response:
    maps_service.load_map(direction_id, data)
    return {'success': 'ok'}


@router.get(
    '/directions/{direction_id}/maps/unload',
    responses={
        200: {'description': 'Educational map successfully unloaded'},
        404: {'description': 'Direction not found'}
    },
    summary='Unload the educational map from the database'
)
def unload_map(direction_id: Annotated[int, Path(gt=0)], maps_service: MapsServiceDep) -> MapUnload:
    return maps_service.unload_map(direction_id)

@router.get(
    '/directions/{direction_id}/maps/export/excel',
    responses={
        200: {'description': 'Educational map successfully exported (Excel file)'},
        404: {'description': 'Direction not found'}
    },
    summary='Export the educational map as Excel file'
)
def export_map_excel(direction_id: Annotated[int, Path(gt=0)],
                     maps_service: MapsServiceDep) -> StreamingResponse:
    # 1. Get the same data as for JSON unload
    map_data: MapUnload = maps_service.unload_map(direction_id)


    # 2. Create Excel workbook in memory
    wb = Workbook()
    ws = wb.active
    ws.title = "Educational Plan"


    # 3. Импорты стилей для красной подсветки
    from openpyxl.styles import PatternFill
    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")


    # 4. Новая структура заголовков
    headers = [
        'Семестр', 'Ядро', 'Дисциплина', 'Кафедра', 'Зед', 'Зед(час)',
        'Экзамен', 'Зачёт', 'Диф. зачёт',
        'КП', 'КР', 'РЗ', 'РГР', 'Реферат',
        'Лекционные часы', 'Практические часы', 'Лабораторные часы', 'Сумма часов', 'Разница часов'
    ]
    ws.append(headers)


    # 5. Заполняем данные
    for map_core in map_data.map_cors:
        for block in map_core.discipline_blocks:
            # 1. Зед(час) = Зед * 36
            zed_hours = block.credit_units * 36
           
            # 2. Типы контроля (с DEBUG для отладки)
            control_type = block.control_type.name  # БЕЗ strip()!
            print(f"DEBUG: control_type='{control_type}'")  # Временно для теста


            exam_col = '+' if control_type == 'Экзамен' else ''
            course_project_col = '+' if (control_type == 'Курсовой проект' or block.has_course_project) else ''
            kursach_col = '+' if (control_type == 'Курсовая работа' or block.has_course_work) else ''
            rz_col = '+' if (control_type == 'РЗ' or block.has_rz) else ''
            rgr_col = '+' if (control_type == 'РГР' or block.has_rgr) else ''
            referat_col = '+' if (control_type == 'Реферат' or block.has_referat) else ''
            diff_zachet_col = '+' if control_type == 'Диф. Зачёт' else ''
            zachet_col = '+' if control_type == 'Зачёт' else ''


           # 3. Сумма часов
            base_hours = (block.lecture_hours or 0) + (block.practice_hours or 0) + (block.lab_hours or 0)
            # 3. Сумма часов — только аудиторные часы
            lecture_hours = block.lecture_hours or 0
            practical_hours = block.practice_hours or 0
            lab_hours = block.lab_hours or 0
            total_hours = lecture_hours + practical_hours + lab_hours

            # 4. Разница часов = Зед(час) - сумма аудиторных часов
            hours_diff = zed_hours - total_hours

            # Формируем строку
            row = [
                block.semester_number,
                map_core.name,
                block.discipline.name,
                block.discipline.department.name,
                block.credit_units,
                zed_hours,

                exam_col,
                zachet_col,
                diff_zachet_col,

                course_project_col,
                kursach_col,
                rz_col,
                rgr_col,
                referat_col,

                lecture_hours,
                practical_hours,
                lab_hours,
                total_hours,
                hours_diff
            ]
            ws.append(row)
           
            # 4.1 Красная подсветка для отрицательной разницы (последний столбец)
            if hours_diff < 0:
                ws.row_dimensions[ws.max_row].height = 18  # Немного повысим высоту строки
                for col_num in range(1, len(headers) + 1):  # Подсвечиваем всю строку
                    cell = ws.cell(row=ws.max_row, column=col_num)
                    cell.fill = red_fill


    # 5. Автоподбор ширины столбцов
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 20)
        ws.column_dimensions[column_letter].width = adjusted_width


    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)


    headers = {
        "Content-Disposition": 'attachment; filename="plan.xlsx"',
        "Access-Control-Expose-Headers": "Content-Disposition",
    }


    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers=headers,
    )


@router.get(
    '/map-cors/{map_core_id}/unload',
    responses={
        200: {'description': 'Map core successfully unloaded'},
        404: {'description': 'Map core not found'}
    },
    summary='Unload the map core from the database'
)
def unload_map_core(map_core_id: Annotated[int, Path(gt=0)], maps_service: MapsServiceDep) -> MapCoreUnload:
    return maps_service.unload_map_core(map_core_id)
