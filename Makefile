.ONESHELL:


docker:
	docker build -t esteanes/expenses-dashboard:latest -f Dockerfile .

run:
	PYTHONPATH=. streamlit run app/Home_Page.py