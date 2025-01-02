FROM ubuntu:22.04 AS build

RUN apt-get update -qq && apt-get install -yq build-essential \
    cmake git wget libjpeg-dev linuxdoc-tools libxml2-dev zlib1g-dev libxslt1-dev

RUN apt update && apt install -yq python3 python3-pip 

RUN pip install --no-cache-dir gradio

# build gdcm and the executable
# test with 3.0.20 instead of 3.0.5
RUN cd /root && git clone https://github.com/mmiv-center/DICOMAnonymizer.git && cd DICOMAnonymizer \
    && wget https://github.com/malaterre/GDCM/archive/v3.0.20.tar.gz \
    && tar xzvf v3.0.20.tar.gz \
    && mkdir gdcm-build \
    && cd gdcm-build \
    && cmake -DGDCM_BUILD_SHARED_LIBS=ON -DCMAKE_BUILD_TYPE=Release ../GDCM-3.0.20 \
    && make \
    && cd .. \
    && cmake -DCMAKE_BUILD_TYPE=Release . \
    && make

ENV ND_ENTRYPOINT="/startup.sh"

RUN echo '#!/usr/bin/env bash' >> $ND_ENTRYPOINT \
    && echo 'set +x' >> $ND_ENTRYPOINT \
    && echo 'umask 0000' >> $ND_ENTRYPOINT \
    && echo '/root/DICOMAnonymizer/anonymize $*' >> $ND_ENTRYPOINT \
    && chmod 777 $ND_ENTRYPOINT

# ENTRYPOINT [ "/startup.sh" ]

WORKDIR /root/DICOMAnonymizer
COPY anonymize.py .
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["python3", "anonymize.py"]