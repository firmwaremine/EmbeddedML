idf_component_register(SRCS "main.c" INCLUDE_DIRS "." REQUIRES camera_capture esp_timer esp_driver_gpio heap esp_psram)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror)
