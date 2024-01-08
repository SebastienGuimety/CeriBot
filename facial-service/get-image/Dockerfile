FROM i386/python:2.7
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
COPY pynaoqi-python2.7-2.1.4.13-linux32 /pynaoqi
ENV PYTHONPATH "${PYTHONPATH}:/pynaoqi"
CMD ["python", "get_img.py"]