FROM node:18-alpine AS builder

# Accept build argument
ARG REACT_APP_API_URL
ARG REACT_APP_DEFAULT_VIEW=dashboard
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_DEFAULT_VIEW=$REACT_APP_DEFAULT_VIEW

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY public ./public
COPY src ./src

# Build application
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app

# Install serve to run the app
RUN npm install -g serve

# Copy built application from builder
COPY --from=builder /app/build ./build
COPY serve.json ./build/serve.json

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

USER nodejs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["serve", "-s", "build", "-l", "3000", "-c", "serve.json"]
