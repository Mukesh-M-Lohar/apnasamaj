FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

# Run in dev mode for local orchestration with hot reload
CMD ["npm", "run", "dev"]
