FROM node:6.2
MAINTAINER Manatsawin Hanmongkolchai <manatsawin@gmail.com>
COPY .  /grader
WORKDIR /grader
RUN npm install
ENV GRADER_DOCKER_SOCKET /var/run/docker.sock
ENTRYPOINT ["node", "index.js"]
