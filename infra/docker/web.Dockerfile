FROM node:20-alpine

WORKDIR /app

COPY package.json ./
COPY apps/web/package.json ./apps/web/package.json
RUN npm install

COPY apps/web ./apps/web

CMD ["npm", "--workspace", "apps/web", "run", "dev"]

