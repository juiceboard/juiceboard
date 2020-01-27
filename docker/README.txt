Running docker-compose
--------------------------
Prequisites:
docker/docker-compose environment set up on your system.
See https://docs.docker.com/ for information.

1) To build and launch the postgresql database and juiceboard app services, run the command from the current directory:

docker-compose up

You can add the -d argument to detach the process (run in background).

This will build both docker images and run the postgresql and juiceboard (python) services.
Note: If you require a rebuild, run: > docker-compose up --build < to rebuild the images.

2) Then you can access the app from your browser by navigating to: (Note: The port 500 is configured in the docker-compose.yml)

http://localhost:5000

# Some useful Docker commands
1) To list the running docker containers
docker ps
2) To stop a running container (You can get the CONTAINER ID by running the command "docker ps -a")
docker stop <CONTAINER NAME/ID>
3) To remove a stopped container (You can get the CONTAINER ID by running the command "docker ps -a")
docker rm <CONTAINER NAME/ID>
4) To list the docker images
docker images
5) To remove a docker image (You can get the IMGAGE ID by running the command "docker images")
docker rmi <IMAGE ID>
