def generate_study_plan(
        discipline_blocks
):
    result = []

    for block in discipline_blocks:

        total_hours = (
                block.lecture_hours
                + block.practice_hours
                + block.lab_hours
        )

        self_study_hours = (
                block.credit_units * 36
                - total_hours
        )

        result.append({
            "discipline_id":
                block.discipline_id,

            "semester_number":
                block.semester_number,

            "credit_units":
                block.credit_units,

            "lecture_hours":
                block.lecture_hours,

            "practice_hours":
                block.practice_hours,

            "lab_hours":
                block.lab_hours,

            "total_hours":
                total_hours,

            "self_study_hours":
                max(
                    self_study_hours,
                    0
                ),

            "control_type_ids":
                getattr(
                    block,
                    "control_type_ids",
                    []
                ),

            "has_course_work":
                block.has_course_work
        })

    return result