# IMM Data Visualization Project


[Turkish Article](https://engineering.teknasyon.com/python-ile-nas%C4%B1l-etkileyici-veri-hikayeleri-yarat%C4%B1l%C4%B1r-4f8de884d5fb)

[English Article](https://towardsdatascience.com/how-to-reveal-impressive-data-stories-with-python-848a2611bfb3)

This project's aim is to demonstrate how to reveal impressive data stories with Python and its libraries. Please, feel free to contribute to the project. The whole project is written as modular as possible.

Files can be run manually by using the following commands, or it can be used Dockerfile

```python file.py```

```streamlit run file.py```

*I had a hard time running Dockerfile because of M1 Chip. Nevertheless, I was able to put a sample Dockerfile for a python file. The sh file can be used to run other python files in batches, or there is another option for this situation; Every py file should be run in a separate container.*

It can be run Dockerfile with the below commands.

```docker build -t imm .```

```docker run -p 8501:8501 imm:latest```
