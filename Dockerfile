FROM ubuntu

RUN apt-get update
RUN apt-get install -y g++
RUN apt-get install -y default-jre
RUN apt-get install -y default-jdk
RUN apt-get install -y time
