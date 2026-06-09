#ifndef SENSOR_DAEMON_H
#define SENSOR_DAEMON_H

#include <stdbool.h>

#define CRASH_THRESHOLD_G 2.5f

// Initializes the I2C connection to MPU6050
bool sensor_init(void);

// Polls the sensor and returns true if a crash (exceeding threshold) is detected
bool sensor_poll_for_crash(void);

#endif // SENSOR_DAEMON_H