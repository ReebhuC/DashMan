#include "camera.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <poll.h>
#include <linux/videodev2.h>

#define MAX_BUFFERS 4

struct v4l2_buffer_map {
    void   *start;
    size_t  length;
};

static int cam_fd = -1;
static struct v4l2_buffer_map *buffers = NULL;
static unsigned int n_buffers = 0;

static void push_chunk(ring_buffer_t *rb, const uint8_t *data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        rb_push(rb, data[i]);
    }
}

bool camera_init(const char *device_path) {
    cam_fd = open(device_path, O_RDWR | O_NONBLOCK, 0);
    if (cam_fd == -1) {
        perror("Opening video device");
        return false;
    }

    struct v4l2_format fmt;
    memset(&fmt, 0, sizeof(fmt));
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width       = 1280;
    fmt.fmt.pix.height      = 720;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_H264;
    fmt.fmt.pix.field       = V4L2_FIELD_ANY;

    if (-1 == ioctl(cam_fd, VIDIOC_S_FMT, &fmt)) {
        perror("Setting Pixel Format");
        return false;
    }

    struct v4l2_requestbuffers req;
    memset(&req, 0, sizeof(req));
    req.count = MAX_BUFFERS;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;

    if (-1 == ioctl(cam_fd, VIDIOC_REQBUFS, &req)) {
        perror("Requesting Buffer");
        return false;
    }

    buffers = calloc(req.count, sizeof(*buffers));
    for (n_buffers = 0; n_buffers < req.count; ++n_buffers) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type        = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory      = V4L2_MEMORY_MMAP;
        buf.index       = n_buffers;

        if (-1 == ioctl(cam_fd, VIDIOC_QUERYBUF, &buf)) {
            perror("Querying Buffer");
            return false;
        }

        buffers[n_buffers].length = buf.length;
        buffers[n_buffers].start =
            mmap(NULL, buf.length, PROT_READ | PROT_WRITE,
                 MAP_SHARED, cam_fd, buf.m.offset);

        if (MAP_FAILED == buffers[n_buffers].start) {
            perror("mmap");
            return false;
        }
    }

    for (unsigned int i = 0; i < n_buffers; ++i) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        if (-1 == ioctl(cam_fd, VIDIOC_QBUF, &buf)) {
            perror("Queue Buffer");
            return false;
        }
    }

    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (-1 == ioctl(cam_fd, VIDIOC_STREAMON, &type)) {
        perror("Start Capture");
        return false;
    }

    return true;
}

bool camera_capture_frame(ring_buffer_t *rb) {
    if (cam_fd == -1) return false;

    struct pollfd fds;
    fds.fd = cam_fd;
    fds.events = POLLIN;

    int r = poll(&fds, 1, 100);
    if (r == -1) {
        perror("poll");
        return false;
    }
    if (r == 0) {
        // Timeout
        return true;
    }

    struct v4l2_buffer buf;
    memset(&buf, 0, sizeof(buf));
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;

    if (-1 == ioctl(cam_fd, VIDIOC_DQBUF, &buf)) {
        perror("Dequeue Buffer");
        return false;
    }

    // Push the actual V4L2 buffer payload to the ring buffer memory
    push_chunk(rb, (const uint8_t *)buffers[buf.index].start, buf.bytesused);

    if (-1 == ioctl(cam_fd, VIDIOC_QBUF, &buf)) {
        perror("Requeue Buffer");
        return false;
    }

    return true;
}

void camera_cleanup(void) {
    if (cam_fd != -1) {
        enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        ioctl(cam_fd, VIDIOC_STREAMOFF, &type);
        for (unsigned int i = 0; i < n_buffers; ++i)
            munmap(buffers[i].start, buffers[i].length);
        free(buffers);
        close(cam_fd);
        cam_fd = -1;
    }
}