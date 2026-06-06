# Frontend: Next.js 16 (build standalone) servido con Node.
FROM node:22-slim AS builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# La URL del WS se incrusta en build (variable NEXT_PUBLIC_*). Apunta al backend
# público al que se conecta el navegador del alumno.
ARG NEXT_PUBLIC_BACKEND_WS_URL=ws://localhost:8000/ws
ENV NEXT_PUBLIC_BACKEND_WS_URL=${NEXT_PUBLIC_BACKEND_WS_URL}
RUN npm run build

FROM node:22-slim AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
