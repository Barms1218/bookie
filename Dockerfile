FROM golang:1.25 AS builder

# Set Destination for COPY
WORKDIR /app

# Download go modules
COPY go.mod go.sum ./
RUN go mod download

# Copying the source code
COPY . . 

# Build
RUN CGO_ENABLED=0 GOOS=linux go build -o /bookie

FROM scratch
COPY --from=builder /bookie /bookie
CMD ["/bookie"]

