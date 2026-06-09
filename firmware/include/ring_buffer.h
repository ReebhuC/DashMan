#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct {
    uint8_t *buffer;
    size_t head;
    size_t tail;
    size_t size;
    bool is_full;
} ring_buffer_t;

void rb_init(ring_buffer_t *rb, uint8_t *buffer, size_t size);
void rb_free(ring_buffer_t *rb);
void rb_push(ring_buffer_t *rb, uint8_t data);
bool rb_pop(ring_buffer_t *rb, uint8_t *data);
size_t rb_available(ring_buffer_t *rb);

#endif // RING_BUFFER_H