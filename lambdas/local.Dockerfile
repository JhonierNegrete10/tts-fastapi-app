FROM python:3.12 AS model 
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
RUN apt-get install -y git-lfs 
RUN git lfs install
RUN git clone https://huggingface.co/facebook/mms-tts-spa /tmp/model
RUN rm -rf /tmp/model/.git

FROM python:3.12  
# Copy function code
RUN pip  install torch  --extra-index-url https://download.pytorch.org/whl/cpu

COPY --from=model /tmp/model ./model


COPY ./requirements.txt .

RUN pip install -r requirements.txt 

COPY ./fastapi-tts/* .

# ENTRYPOINT ["tail", "-f", "/dev/null"]
CMD [ "python", "main.py" ]