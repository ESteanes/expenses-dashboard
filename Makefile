.ONESHELL:


docker:
	docker build -t esteanes/expenses-dashboard:latest -f Dockerfile .

docker-publish:
	docker buildx build --platform linux/amd64,linux/arm64 -t esteanes/expenses-dashboard:latest --push -f Dockerfile .

run:
	PYTHONPATH=. streamlit run app/Home_Page.py