.ONESHELL:


docker:
	docker build -t expenses-dashboard:latest -f Dockerfile .

run:
	streamlit run app/main.py
