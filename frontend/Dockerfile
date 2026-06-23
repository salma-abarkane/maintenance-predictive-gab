FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
COPY tsconfig.json tsconfig.node.json tailwind.config.ts postcss.config.js ./
COPY public ./public
COPY src ./src

RUN npm install

EXPOSE 4173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4173"]
