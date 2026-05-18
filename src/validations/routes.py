from fastapi import APIRouter, status
from fastapi.responses import Response
from typing import Any, List, Dict
from pydantic import BaseModel
from enum import Enum

router = APIRouter(
    prefix='/validations',
    tags=['validations']
)


class Discipline(BaseModel):
    id: int
    name: str
    credits: int
    examType: str
    hasCourseWork: bool
    hasPracticalWork: bool
    department: str
    competenceCodes: List[int]
    lectureHours: int
    labHours: int
    practicalHours: int
    sourcePosition: dict | None = None

class Row(BaseModel):
    name: str
    color: str
    data: List[List[Discipline]]

class ValidationSeverity(str, Enum):
    BLOCKING = "blocking"
    WARNING = "warning"

class ValidationResult(BaseModel):
    message: str
    severity: ValidationSeverity
    details: Dict[str, Any] = {}

class ValidationResponse(BaseModel):
    isValid: bool
    results: List[ValidationResult]



def calculate_hours(discipline: Discipline) -> Dict[str, float]:
    total_hours = discipline.credits * 36
    exam_hours = 9 if discipline.examType == "Экзамен" else 0
    exam_prep_hours = 27 if discipline.examType == "Экзамен" else 0
    individual_hours = sum([
        2 if discipline.examType == "Зачет" else 0,
        2 if discipline.examType == "Дифференцированный зачет" else 0,
        2 if discipline.hasCourseWork else 0,
        1 if discipline.hasPracticalWork else 0
    ])
    
    classroom_hours = discipline.lectureHours + discipline.labHours + discipline.practicalHours
    contact_hours = individual_hours + exam_hours + classroom_hours
    total_independent_work = total_hours - contact_hours
    current_independent_work = total_hours - contact_hours - exam_prep_hours
    
    return {
        "total": total_hours,
        "contact": contact_hours,
        "classroom": classroom_hours,
        "total_independent": total_independent_work,
        "current_independent": current_independent_work,
        "exam_prep": exam_prep_hours
    }

@router.post('/validate-up', response_model=ValidationResponse)
def validate_up(request: List[Row]) -> ValidationResponse:
    validation_results = []
    
    # Проверка на пустой ввод
    if not request or len(request) == 0:
        return ValidationResponse(
            isValid=False,
            results=[ValidationResult(
                message="Нет данных для проверки. Добавьте дисциплины в учебный план.",
                severity=ValidationSeverity.BLOCKING,
                details={}
            )]
        )
    
    semesters_count = len(request[0].data)
    
    # ===== ПРОВЕРКИ БЛОКИРУЮЩИХ КРИТЕРИЕВ =====
    total_credits = 0
    for semester_idx in range(semesters_count):
        semester_credits = sum(
            row.data[semester_idx][i].credits 
            for row in request 
            for i in range(len(row.data[semester_idx]))
        )
        total_credits += semester_credits
        
        # Проверяем количество зачетных единиц в семестре
        if not 24 <= semester_credits <= 36:
            validation_results.append(ValidationResult(
                message=f"В семестре {semester_idx + 1} количество з.е.: {semester_credits} (должно быть 30 ± 6)",
                severity=ValidationSeverity.BLOCKING,
                details={
                    "semester": semester_idx + 1,
                    "credits": semester_credits,
                }
            ))
            
        # Подсчет курсовых работ в семестре
        course_works_count = sum(
            1 
            for row in request 
            for discipline in row.data[semester_idx] 
            if discipline.hasCourseWork
        )
        
        if course_works_count > 2:
            validation_results.append(ValidationResult(
                message=f"В семестре {semester_idx + 1} количество курсовых работ: {course_works_count} (должно быть не больше 2)",
                severity=ValidationSeverity.WARNING,
                details={
                    "semester": semester_idx + 1,
                    "course_works_count": course_works_count,
                }
            ))
    
    # Проверяем общее количество зачетных единиц
    expected_credits = 240 if semesters_count == 8 else 120
    if total_credits != expected_credits:
        validation_results.append(ValidationResult(
            message=f"Общее количество з.е.: {total_credits} (должно быть {expected_credits})",
            severity=ValidationSeverity.BLOCKING,
            details={
                "total_credits": total_credits,
                "expected_credits": expected_credits
            }
        ))
    
    # ===== ПРОВЕРКИ ИНДИКАТИВНЫХ КРИТЕРИЕВ =====
    for row in request:
        for semester_disciplines in row.data:
            for discipline in semester_disciplines:
                hours = calculate_hours(discipline)
                
                # Проверка аудиторной работы (не более 40% от общего объема)
                classroom_percentage = (hours["classroom"] / hours["total"]) * 100
                if classroom_percentage > 40:
                    validation_results.append(ValidationResult(
                        message=f"Дисциплина '{discipline.name}' имеет превышение аудиторной нагрузки: {classroom_percentage:.1f}% (должно быть не более 40%)",
                        severity=ValidationSeverity.WARNING,
                        details={
                            "discipline": discipline.name,
                            "classroom_hours": hours["classroom"],
                            "total_hours": hours["total"],
                            "percentage": classroom_percentage
                        }
                    ))
                
                # Подсчет часов самостоятельной работы для каждой дисциплины
                if hours["total_independent"] <= 0:
                    validation_results.append(ValidationResult(
                        message=f"Дисциплина '{discipline.name}' имеет‚ некорректное количество часов самостоятельной работы: {hours['total_independent']}",
                        severity=ValidationSeverity.BLOCKING,
                        details={
                            "discipline": discipline.name,
                            "total_hours": hours["total"],
                            "contact_hours": hours["contact"],
                            "exam_prep_hours": hours["exam_prep"],
                            "total_independent": hours["total_independent"],
                        }
                    ))

    # Проверка баланса форм контроля по семестрам
    for semester_idx in range(semesters_count):
        semester_total = 0
        semester_exam = 0
        semester_credit = 0
        semester_diff_credit = 0
        
        for row in request:
            for discipline in row.data[semester_idx]:
                semester_total += 1
                if discipline.examType == "Экзамен":
                    semester_exam += 1
                elif discipline.examType == "Зачет":
                    semester_credit += 1
                elif discipline.examType == "Дифференцированный зачет":
                    semester_diff_credit += 1
        
        if semester_total > 0:
            exam_percentage = (semester_exam / semester_total) * 100
            credit_percentage = (semester_credit / semester_total) * 100
            diff_credit_percentage = (semester_diff_credit / semester_total) * 100

            if not (25 <= exam_percentage <= 35):
                validation_results.append(ValidationResult(
                    message=f"Семестр {semester_idx + 1}: процент экзаменов ({exam_percentage:.1f}%) не соответствует рекомендуемому диапазону (30% ± 5%)",
                    severity=ValidationSeverity.WARNING,
                    details={
                        "semester": semester_idx + 1,
                        "exam_count": semester_exam,
                        "total_count": semester_total,
                        "percentage": exam_percentage
                    }
                ))
            
            if not (30 <= credit_percentage <= 40):
                validation_results.append(ValidationResult(
                    message=f"Семестр {semester_idx + 1}: процент зачетов ({credit_percentage:.1f}%) не соответствует рекомендуемому диапазону (35% ± 5%)",
                    severity=ValidationSeverity.WARNING,
                    details={
                        "semester": semester_idx + 1,
                        "credit_count": semester_credit,
                        "total_count": semester_total,
                        "percentage": credit_percentage
                    }
                ))
            
            if not (30 <= diff_credit_percentage <= 40):
                validation_results.append(ValidationResult(
                    message=f"Семестр {semester_idx + 1}: процент дифференцированных зачетов ({diff_credit_percentage:.1f}%) не соответствует рекомендуемому диапазону (35% ± 5%)",
                    severity=ValidationSeverity.WARNING,
                    details={
                        "semester": semester_idx + 1,
                        "diff_credit_count": semester_diff_credit,
                        "total_count": semester_total,
                        "percentage": diff_credit_percentage
                    }
                ))

    return ValidationResponse(
        isValid=not any(r.severity == ValidationSeverity.BLOCKING for r in validation_results),
        results=validation_results,
    )
