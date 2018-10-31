#include <sys/socket.h>
#include <netinet/in.h>
#include <errno.h>
#define PORT 9003

int main()
{

    //Creating variables for sockets
    int server_fd, new_socket, valread;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char buffer[1024] = {0};
    const char *hello = "Hellooooooooowwwww";


    //Added for creating TCP socket
    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
                                                  &opt, sizeof(opt)))
    {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons( PORT );

    // Forcefully attaching socket to the port 8080
    if (bind(server_fd, (struct sockaddr *)&address, 
                                 sizeof(address))<0)
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    while(1){
        if (listen(server_fd, 3) < 0)
        {
            perror("listen");
            exit(EXIT_FAILURE);
        }
        printf("Waiting for connection.\n" );
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen))<0)
        {
            perror("accept");
            exit(EXIT_FAILURE);
        }
        printf("Client connected.. Sending data !! \n" );

        while (1) {
            //  poll at the rate recommended by the IMU

            usleep(imu->IMUGetPollInterval() * 1000);

            while (imu->IMURead()) {
                RTIMU_DATA imuData = imu->getIMUData();
                sampleCount++;

                now = RTMath::currentUSecsSinceEpoch();

                //  display 10 times per second

                if ((now - displayTimer) > 100000) {
                    hello = RTMath::displayDegrees("", imuData.fusionPose);
                    //double angle = atan2(imuData.compass.y() * RTMATH_RAD_TO_DEGREE , imuData.compass.x() * RTMATH_RAD_TO_DEGREE );
                    int send_result = send(new_socket , hello , strlen(hello) , MSG_NOSIGNAL );
                    printf("Sample rate %d: %s\n", sampleRate, hello);
                    printf("Angle %f \n", angle);
                    fflush(stdout);
                    displayTimer = now;
                    if(send_result<=0){
                        printf("Client disconnected..");
                        close(new_socket);


                        printf("Waiting for connection.\n");
                        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen))<0)
                        {
                            perror("accept");
                            exit(EXIT_FAILURE);
                        }
                        printf("Client connected.. Sending data !! \n" );

                    }
                }

                //  update rate every second

                if ((now - rateTimer) > 1000000) {
                    sampleRate = sampleCount;
                    sampleCount = 0;
                    rateTimer = now;
                }
            }
        }
        close(new_socket);

    }
    //valread = read( new_socket , buffer, 1024);

    //send(new_socket , hello , strlen(hello) , 0 );
    //printf("Hello message sent\n");
    //Socket END

    //close(new_socket);
    close(server_fd);
}

