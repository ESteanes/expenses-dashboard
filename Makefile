.ONESHELL:


docker:
	docker build -t expenses-dashboard:latest -f Dockerfile .

run:
	PYTHONPATH=. streamlit run app/Home_Page.py