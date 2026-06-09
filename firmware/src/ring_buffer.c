#include "ring_buffer.h"

void rb_init(ring_buffer_t *rb, uint8_t *buffer, size_t size) {
    rb->buffer = buffer;
    rb->size = size;
    rb->head = 0;
    rb->tail = 0;
    rb->is_full = false;
}

void rb_free(ring_buffer_t *rb) {
    rb->buffer = NULL;
    rb->size = 0;
    rb->head = 0;
    rb->tail = 0;
    rb->is_full = false;
}

void rb_push(ring_buffer_t *rb, uint8_t data) {
    if (rb->buffer == NULL || rb->size == 0) return;

    rb->buffer[rb->head] = data;
    rb->head = (rb->head + 1) % rb->size;

    if (rb->is_full) {
        rb->tail = (rb->tail + 1) % rb->size;
    } else if (rb->head == rb->tail) {
        rb->is_full = true;
    }
}

bool rb_pop(ring_buffer_t *rb, uint8_t *data) {
    if (rb->buffer == NULL || rb->size == 0) return false;
    if (!rb->is_full && (rb->head == rb->tail)) return false;

    *data = rb->buffer[rb->tail];
    rb->is_full = false;
    rb->tail = (rb->tail + 1) % rb->size;
    
    return true;
}

size_t rb_available(ring_buffer_t *rb) {
    if (rb->is_full) {
        return rb->size;
    }

    if (rb->head >= rb->tail) {
        return rb->head - rb->tail;
    }

    return rb->size + rb->head - rb->tail;
}