FROM python:3.8
# EXPOSE 8501

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD streamlit run wifi_new_user_daily.py