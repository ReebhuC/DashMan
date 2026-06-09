#include <stdio.h>
#include <time.h>
#include "../include/ring_buffer.h"
#include "../include/sensor_daemon.h"

void trigger_engine_flush(ring_buffer_t *video_buffer) {
    time_t rawtime;
    struct tm *info;
    char filename[80];
    
    time(&rawtime);
    info = localtime(&rawtime);
    
    strftime(filename, 80, "incident_%Y%m%d_%H%M%S.mp4", info);
    
    printf("Crash detected! Flushing buffer to %s\n", filename);
    
    FILE *fp = fopen(filename, "wb");
    if (fp) {
        size_t available = rb_available(video_buffer);
        uint8_t data;
        while (rb_pop(video_buffer, &data)) {
            fputc(data, fp);
        }
        fclose(fp);
        printf("Flushed %zu bytes to %s\n", available, filename);
    } else {
        printf("Failed to open file %s for writing\n", filename);
    }
}