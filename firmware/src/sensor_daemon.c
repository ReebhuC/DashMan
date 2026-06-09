#include "sensor_daemon.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#define I2C_DEVICE "/dev/i2c-1"
#define MPU6050_ADDR 0x68
#define PWR_MGMT_1_REG 0x6B
#define ACCEL_XOUT_H_REG 0x3B

static int i2c_fd = -1;

bool sensor_init(void) {
    printf("Initializing I2C connection to MPU6050 on %s...\n", I2C_DEVICE);
    
    i2c_fd = open(I2C_DEVICE, O_RDWR);
    if (i2c_fd < 0) {
        perror("Failed to open the i2c bus");
        return false;
    }

    if (ioctl(i2c_fd, I2C_SLAVE, MPU6050_ADDR) < 0) {
        perror("Failed to acquire bus access and/or talk to slave");
        close(i2c_fd);
        i2c_fd = -1;
        return false;
    }

    // Write 0x00 to PWR_MGMT_1 to wake up the MPU6050
    uint8_t wake_buf[2] = {PWR_MGMT_1_REG, 0x00};
    if (write(i2c_fd, wake_buf, 2) != 2) {
        perror("Failed to write to the i2c bus to wake up sensor");
        close(i2c_fd);
        i2c_fd = -1;
        return false;
    }

    return true;
}

bool sensor_poll_for_crash(void) {
    if (i2c_fd < 0) return false;

    // Set the register pointer to ACCEL_XOUT_H
    uint8_t reg = ACCEL_XOUT_H_REG;
    if (write(i2c_fd, &reg, 1) != 1) {
        perror("Failed to write register address");
        return false;
    }

    // Read 6 bytes for X, Y, Z (high and low bytes)
    uint8_t buf[6];
    if (read(i2c_fd, buf, 6) != 6) {
        perror("Failed to read accelerometer data");
        return false;
    }

    // Convert the bytes to 16-bit integers
    int16_t accel_x = (buf[0] << 8) | buf[1];
    int16_t accel_y = (buf[2] << 8) | buf[3];
    int16_t accel_z = (buf[4] << 8) | buf[5];

    // Convert to G-force (default scale is +/- 2g -> 16384 LSB/g)
    float g_x = accel_x / 16384.0f;
    float g_y = accel_y / 16384.0f;
    float g_z = accel_z / 16384.0f;
    
    float total_g = sqrtf(g_x*g_x + g_y*g_y + g_z*g_z);
    
    if (total_g > CRASH_THRESHOLD_G) {
        printf("CRASH DETECTED! Magnitude: %.2fG\n", total_g);
        return true;
    }
    
    return false;
}