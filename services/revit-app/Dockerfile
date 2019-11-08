
FROM alpine:3.10.2

# Create non-root user to run commands in (see https://medium.com/@mccode/processes-in-containers-should-not-run-as-root-2feae3f0df3b)
RUN addgroup -S -g 1000 me && \
    adduser -S -D -u 1000 -G me me

#############
# As `root` #
#############
RUN apk --no-cache add \
    dumb-init \
    python3 \
    py3-numpy \
    py3-scipy

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

# Copy the TDB_Helpers from the shared folder (now image) into app (Workdir)
COPY --chown=me:me --from=shared_python_functions /app /app


EXPOSE 22633
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3", "/app/app.py"]
