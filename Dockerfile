FROM golang:alpine
RUN apk add --no-cache git
RUN git config --global http.postBuffer 524288000
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN go build
CMD ["./iith-dashboard-backend"]
