FROM alpine:3.10.2

# Create non-root user to run commands in (see https://medium.com/@mccode/processes-in-containers-should-not-run-as-root-2feae3f0df3b)
RUN addgroup -S -g 1000 me && \
    adduser -S -D -u 1000 -G me me

#############
# As `root` #
#############
RUN apk add --no-cache \
    dumb-init \
    python3

ENV HOME=/home/me
RUN ln -s ${HOME}/app /app

###########
# As `me` #
###########
USER me
WORKDIR /app

COPY --chown=me:me requirements.txt .
ENV PATH ${HOME}/.local/bin:$PATH
RUN pip3 install --user -r requirements.txt

COPY --chown=me:me . .

EXPOSE 22631
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3", "/app/app.py"]
