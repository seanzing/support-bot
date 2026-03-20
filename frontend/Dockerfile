# Build stage
FROM node:20-alpine AS builder
RUN corepack enable pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
# Note: Using regular install for POC (lockfile may be out of sync)
# For production, ensure lockfile is up-to-date and use --frozen-lockfile
RUN pnpm install
COPY . .

# Build args from docker-compose.yml
ARG VITE_SUPPORT_API_BASE
ARG VITE_SUPPORT_CHATKIT_API_URL
ARG VITE_SUPPORT_CUSTOMER_URL
ARG VITE_SUPPORT_TICKET_URL
ARG VITE_SUPPORT_UPLOAD_URL
ARG VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY

RUN pnpm build

# Runtime stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
