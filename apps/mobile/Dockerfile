FROM node:20-alpine

WORKDIR /app

# Expose Metro bundler and Expo developer tools ports
EXPOSE 8081
EXPOSE 19000
EXPOSE 19001
EXPOSE 19002

COPY package*.json ./

RUN npm install -g expo-cli
RUN npm install

COPY . .

# Run Expo start binding to all network interfaces so the host can connect
CMD ["npx", "expo", "start", "--host", "lan"]
