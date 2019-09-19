FROM continuumio/miniconda:4.6.14

# Create non-root user to run commands in (see https://medium.com/@mccode/processes-in-containers-should-not-run-as-root-2feae3f0df3b)
RUN groupadd --gid 1000 me && \
    useradd --system --create-home --uid 1000 --gid me me

#############
# As `root` #
#############
RUN apt-get update
    
ENV HOME=/home/me

RUN ln --symbolic ${HOME}/app /app

###########
# As `me` #
###########
USER me

ENV PATH ${HOME}/.local/bin:$PATH

WORKDIR /app

COPY . /app

EXPOSE 22631

RUN conda create --name my && \
    . activate my && \
    conda install \
    --name my \
    python=3.6 && \
    conda clean --all

RUN . activate my && \
    ${HOME}/.conda/envs/my/bin/python -m pip install --user -r requirements.txt

RUN echo ". activate my" >> ~/.bashrc

ENTRYPOINT ${HOME}/.conda/envs/my/bin/python /app/app.py 

