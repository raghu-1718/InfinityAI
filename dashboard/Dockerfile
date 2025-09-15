# Use an official Node.js runtime as a parent image
FROM node:20-slim

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the application's source code
COPY . .

# Expose the port the app runs on (default for many dev servers is 3000)
EXPOSE 3000

# Command to run the development server
CMD ["npm", "start"]