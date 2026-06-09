#ifndef CAMERA_H
#define CAMERA_H

#include <stdbool.h>
#include "ring_buffer.h"

// Initializes V4L2 device, formats, and mmap buffers
bool camera_init(const char *device_path);

// Polls the camera for a frame and pushes it to the ring buffer
bool camera_capture_frame(ring_buffer_t *rb);

// CLEANS up V4L2 maps and closes FD
void camera_cleanup(void);

#endif // CAMERA_H