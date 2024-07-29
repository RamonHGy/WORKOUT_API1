run:
	@uvicorn workout_api.main:app --reload

create-migrations:
	@set PYTHONPATH=. && alembic revision --autogenerate -m "$(d)"

run-migrations:
	@set PYTHONPATH=. && alembic upgrade head
