# IMM Data Visualization Project

This project's aim is to demonstrate how to reveal impressive data stories with Python and its libraries. Please, feel free to contribute the project. The whole project is written as modular as possible.

Files can be run manually by using the following commands, or it can be used Dockerfile

```python file.py```

```streamlit run file.py```

*I had a hard time running Dockerfile because of M1 Chip. I put a sample Dockerfile for a python file though. The sh file can be used to run other python files in batches.*

It can be run Dockerfile with the below commands.

```docker build -t imm .```

```docker run -p 8501:8501 imm:latest```