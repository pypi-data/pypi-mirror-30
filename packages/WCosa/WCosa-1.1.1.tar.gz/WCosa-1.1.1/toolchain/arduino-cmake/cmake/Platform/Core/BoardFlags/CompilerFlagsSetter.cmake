# ToDo: Comment
function(set_board_compiler_flags COMPILER_FLAGS NORMALIZED_SDK_VERSION BOARD_ID IS_MANUAL)

    _get_board_property(${BOARD_ID} build.f_cpu FCPU)
    _get_board_property(${BOARD_ID} build.mcu MCU)
    set(COMPILE_FLAGS "-DF_CPU=${FCPU} -DARDUINO=${NORMALIZED_SDK_VERSION} -mmcu=${MCU}")

    _try_get_board_property(${BOARD_ID} build.vid VID)
    _try_get_board_property(${BOARD_ID} build.pid PID)
    if (VID)
        set(COMPILE_FLAGS "${COMPILE_FLAGS} -DUSB_VID=${VID}")
    endif ()
    if (PID)
        set(COMPILE_FLAGS "${COMPILE_FLAGS} -DUSB_PID=${PID}")
    endif ()

    if (NOT IS_MANUAL)
        _get_board_property(${BOARD_ID} build.core BOARD_CORE)
        set(COMPILE_FLAGS "${COMPILE_FLAGS} -I\"${${BOARD_CORE}.path}\" -I\"${ARDUINO_LIBRARIES_PATH}\"")
        if (${ARDUINO_PLATFORM_LIBRARIES_PATH})
            set(COMPILE_FLAGS "${COMPILE_FLAGS} -I\"${ARDUINO_PLATFORM_LIBRARIES_PATH}\"")
        endif ()
    endif ()
    if (ARDUINO_SDK_VERSION VERSION_GREATER 1.0 OR ARDUINO_SDK_VERSION VERSION_EQUAL 1.0)
        if (NOT IS_MANUAL)
            _get_board_property(${BOARD_ID} build.variant VARIANT)
            set(PIN_HEADER ${${VARIANT}.path})
            if (PIN_HEADER)
                set(COMPILE_FLAGS "${COMPILE_FLAGS} -I\"${PIN_HEADER}\"")
            endif ()
        endif ()
    endif ()

    set(${COMPILER_FLAGS} "${COMPILE_FLAGS}" PARENT_SCOPE)

endfunction()
