.PHONY: run test install lint

install:
	pip install -r requirements.txt

run:
	streamlit run app.py

test:
	pytest tests/ -v

lint:
	python -m py_compile app.py utils/scoring.py utils/visualizer.py utils/validators.py && echo "✅ No syntax errors"
