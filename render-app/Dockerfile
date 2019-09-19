FROM continuumio/miniconda:4.6.14

RUN conda create --name renderenv && \
    . activate renderenv && \
    conda install \
    --name renderenv \
    --channel conda-forge \
    --channel dlr-sc \
    --channel pythonocc \
    --channel CadQuery \
    --channel tpaviot \
    --channel defaults \
    --channel oce \
    pythonocc-core==0.18.2 \
    python=3.6 && \
    conda clean --all

RUN echo ". activate renderenv" >> ~/.bashrc
ENV PATH /opt/conda/envs/renderenv/bin:$PATH

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libglu1-mesa && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 me && \
    useradd --system --uid 1000 --gid me me

# USER me

ADD . /code
WORKDIR /code

CMD ["python", "runserver.py", "--port", "22634"]
