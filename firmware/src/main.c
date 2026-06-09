#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include "../include/ring_buffer.h"
#include "../include/sensor_daemon.h"
#include "../include/camera.h"

#define BUFFER_SIZE (10 * 1024 * 1024) // 10MB

extern void trigger_engine_flush(ring_buffer_t *video_buffer);
extern void *run_local_server(void *arg);

int main() {
    printf("Dashman Firmware v0.1 Starting...\n");
    
    uint8_t *mem = malloc(BUFFER_SIZE);
    if (!mem) {
        printf("Failed to allocate ring buffer\n");
        return 1;
    }
    ring_buffer_t video_buffer;
    rb_init(&video_buffer, mem, BUFFER_SIZE);
    
    if (!sensor_init()) {
        printf("Failed to init I2C MPU6050\n");
        return 1;
    }
    
    pthread_t server_thread;
    if (pthread_create(&server_thread, NULL, run_local_server, NULL) != 0) {
        printf("Failed to start server thread\n");
        return 1;
    }
    
    if (!camera_init("/dev/video0")) {
        printf("Failed to init V4L2 camera interface on /dev/video0. Continuing with dummy data if needed...\n");
    }

    printf("Starting video capture loop...\n");
    int loop_counter = 0;
    
    while (1) {
        camera_capture_frame(&video_buffer);
        
        if (loop_counter % 10 == 0) { // Poll IMU occasionally to avoid blocking too much
            if (sensor_poll_for_crash()) {
                trigger_engine_flush(&video_buffer);
                rb_free(&video_buffer);
                rb_init(&video_buffer, mem, BUFFER_SIZE);
            }
        }
        
        loop_counter++;
    }
    
    camera_cleanup();
    free(mem);
    return 0;
}