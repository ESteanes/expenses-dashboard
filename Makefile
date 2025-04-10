.ONESHELL:


docker:
	docker build --platform linux/arm64 -t esteanes/expenses-dashboard:latest -f Dockerfile .

run:
	streamlit run app/Home_Page.py
