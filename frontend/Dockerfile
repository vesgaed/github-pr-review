FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Expose Vite port
EXPOSE 5173

# Run in dev mode with host exposed
CMD ["npm", "run", "dev", "--", "--host"]
