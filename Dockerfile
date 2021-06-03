FROM python:3.8
# EXPOSE 8501

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD streamlit run wifi_new_user_daily.py

#Dockerfile with Conda
#FROM continuumio/miniconda3
#
#COPY . /app
#WORKDIR /app
#RUN conda env create -f environment.yml
#
#SHELL ["conda", "run", "-n", "ibb_dp", "/bin/bash", "-c"]
#
#ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "ibb_dp", "python", "wifi_new_user_daily.py"]