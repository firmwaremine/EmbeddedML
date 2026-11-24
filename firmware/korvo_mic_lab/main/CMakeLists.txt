idf_component_register(SRCS "main.c" "features.c" INCLUDE_DIRS "."
 REQUIRES esp_driver_i2c esp_driver_i2s esp_driver_gpio esp_timer esp_codec_dev heap)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror)
