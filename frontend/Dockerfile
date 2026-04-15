FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

ARG VITE_API_URL=http://localhost:8000/api
ENV VITE_API_URL=${VITE_API_URL}

ARG VITE_THINGSPEAK_CHANNEL_ID=
ENV VITE_THINGSPEAK_CHANNEL_ID=${VITE_THINGSPEAK_CHANNEL_ID}

ARG VITE_THINGSPEAK_READ_API_KEY=
ENV VITE_THINGSPEAK_READ_API_KEY=${VITE_THINGSPEAK_READ_API_KEY}

RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
