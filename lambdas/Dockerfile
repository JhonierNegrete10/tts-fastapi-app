FROM public.ecr.aws/lambda/python:3.12 AS model

RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | bash
RUN dnf install -y git-lfs 
RUN git lfs install
RUN git clone https://huggingface.co/facebook/mms-tts-spa /tmp/model
RUN rm -rf /tmp/model/.git

FROM public.ecr.aws/lambda/python:3.12

RUN pip  install torch  --extra-index-url https://download.pytorch.org/whl/cpu
COPY ./requirements.txt .
RUN pip install -r requirements.txt 

COPY --from=model /tmp/model ${LAMBDA_TASK_ROOT}/model

COPY ./fastapi-tts/* ${LAMBDA_TASK_ROOT}
CMD [ "main.handler" ]