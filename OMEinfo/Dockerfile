FROM continuumio/miniconda3
COPY conda_requirements.txt /tmp/
COPY pip_requirements.txt /tmp/
COPY ./app /app
WORKDIR "/app"
RUN conda config --add channels conda-forge
RUN conda install --file /tmp/conda_requirements.txt
RUN pip install -r /tmp/pip_requirements.txt
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
