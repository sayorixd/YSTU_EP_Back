from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.educational_levels.routes import router as educational_levels_router
from src.educational_forms.routes import router as educational_forms_router
from src.directions.routes import router as directions_router
from src.map_cors.routes import router as map_cors_router
from src.direction_map_cors.routes import router as direction_map_cors_router
from src.departments.routes import router as departments_router
from src.disciplines.routes import router as disciplines_router
from src.activity_types.routes import router as activity_types_router
from src.control_types.routes import router as control_types_router
from src.competency_groups.routes import router as competency_groups_router
from src.competencies.routes import router as competencies_router
from src.indicators.routes import router as indicators_router
from src.indicators_table.routes import router as indicators_table_router
from src.discipline_blocks.routes import router as discipline_blocks_router
from src.discipline_block_competencies.routes import router as discipline_block_competencies_router 
from src.validations.routes import router as validations_router
from src.maps.routes import router as maps_router
from src.maps import routes as plan_routes  # NEW NEW NEW

from src.calendar_plans import router as calendar_plans_router



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://host.docker.internal:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(plan_routes.router) ## NEW NEW NEW
app.include_router(educational_levels_router)
app.include_router(educational_forms_router)
app.include_router(directions_router)
app.include_router(map_cors_router)
app.include_router(direction_map_cors_router)
app.include_router(departments_router)
app.include_router(disciplines_router)
app.include_router(activity_types_router)
app.include_router(control_types_router)
app.include_router(competency_groups_router)
app.include_router(competencies_router)
app.include_router(indicators_router)
app.include_router(indicators_table_router)
app.include_router(discipline_blocks_router)
app.include_router(discipline_block_competencies_router)
app.include_router(validations_router)
app.include_router(maps_router)

app.include_router(calendar_plans_router)