"""
This example display a CircuitPython console and
print which button that is being pressed if any
"""
import board
import time
from adafruit_featherwing import minitft_featherwing
import terminalio
from adafruit_display_text import bitmap_label as label
from display_layouts.absolute_layout import AbsoluteLayout
import neopixel

MAIN_MENU_STATE = 0
# quick timer app
QUICK_TIMER_MENU_STATE = 1
QUICK_TIMER_RUNNING_STATE = 2
QUICK_TIMER_PAUSED_STATE = 3
QUICK_TIMER_FINISHED_STATE = 4
# custom timer app
CUSTOM_TIMER_MENU_STATE = 5
CUSTOM_TIMER_RUNNING_STATE = 6
CUSTOM_TIMER_PAUSED_STATE = 7
CUSTOM_TIMER_FINISHED_STATE = 8
# stopwatch app
STOPWATCH_RUNNING_STATE = 9
STOPWATCH_PAUSED_STATE = 10

CURRENT_STATE = MAIN_MENU_STATE

TIMER_TARGET_TIME = -1
QUICK_TIMER_SETTING = -1
CUSTOM_TIMER_SETTING = 0
PAUSE_START_TIME = -1
STOPWATCH_START_TIME = -1

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.15)
pixels[0] = (0, 0, 0)

minitft = minitft_featherwing.MiniTFTFeatherWing()

f = open("minitft_featherwing_gadget/layouts/main_menu.json", "r")
layout_str = f.read()
f.close()
main_menu_layout = AbsoluteLayout(minitft.display, layout_str)

f = open("minitft_featherwing_gadget/layouts/quick_timer.json", "r")
layout_str = f.read()
f.close()

quick_timer_layout = AbsoluteLayout(minitft.display, layout_str)
quick_timer_5min_lbl = quick_timer_layout.sub_view_by_id("5min_lbl")
quick_timer_10min_lbl = quick_timer_layout.sub_view_by_id("10min_lbl")
quick_timer_25min_lbl = quick_timer_layout.sub_view_by_id("25min_lbl")
quick_timer_50min_lbl = quick_timer_layout.sub_view_by_id("50min_lbl")

f = open("minitft_featherwing_gadget/layouts/quick_timer_running.json", "r")
layout_str = f.read()
f.close()
quick_timer_running_layout = AbsoluteLayout(minitft.display, layout_str)
quick_timer_time_left_lbl = quick_timer_running_layout.sub_view_by_id("time_left_lbl")

f = open("minitft_featherwing_gadget/layouts/custom_timer_menu.json", "r")
layout_str = f.read()
f.close()
custom_timer_menu_layout = AbsoluteLayout(minitft.display, layout_str)
custom_timer_setting_lbl = custom_timer_menu_layout.sub_view_by_id("setting_lbl")

f = open("minitft_featherwing_gadget/layouts/stopwatch.json", "r")
layout_str = f.read()
f.close()
stopwatch_layout = AbsoluteLayout(minitft.display, layout_str)
stopwatch_time_lbl = stopwatch_layout.sub_view_by_id("time_counting_lbl")


def format_min_sec(total_seconds):
    return "{}m {}s".format(total_seconds // 60, total_seconds % 60)


def reset_lbls():
    quick_timer_5min_lbl.view.background_color = 0x4472c4
    quick_timer_10min_lbl.view.background_color = 0x4472c4
    quick_timer_25min_lbl.view.background_color = 0x4472c4
    quick_timer_50min_lbl.view.background_color = 0x4472c4


minitft.display.show(main_menu_layout.view)
prev_btns = minitft.buttons

while True:
    buttons = minitft.buttons
    now = time.monotonic()

    if CURRENT_STATE == MAIN_MENU_STATE:

        if buttons.right and not prev_btns.right:
            CURRENT_STATE = CUSTOM_TIMER_MENU_STATE
            minitft.display.show(custom_timer_menu_layout.view)
            prev_btns = buttons
        if buttons.down and not prev_btns.down:
            pass

        if buttons.left and not prev_btns.left:
            CURRENT_STATE = STOPWATCH_PAUSED_STATE
            minitft.display.show(stopwatch_layout.view)
            prev_btns = buttons
            STOPWATCH_START_TIME = now
            PAUSE_START_TIME = now

        if buttons.up and not prev_btns.up:
            CURRENT_STATE = QUICK_TIMER_MENU_STATE
            minitft.display.show(quick_timer_layout.view)
            prev_btns = buttons

    if CURRENT_STATE == QUICK_TIMER_MENU_STATE:
        if buttons.right and not prev_btns.right:
            reset_lbls()
            QUICK_TIMER_SETTING = 600
            quick_timer_10min_lbl.view.background_color = 0x70ad47

        if buttons.down and not prev_btns.down:
            reset_lbls()
            QUICK_TIMER_SETTING = 1500
            quick_timer_25min_lbl.view.background_color = 0x70ad47

        if buttons.left and not prev_btns.left:
            reset_lbls()
            QUICK_TIMER_SETTING = 3000
            quick_timer_50min_lbl.view.background_color = 0x70ad47

        if buttons.up and not prev_btns.up:
            reset_lbls()
            quick_timer_5min_lbl.view.background_color = 0x70ad47
            QUICK_TIMER_SETTING = 300

        if buttons.a and not prev_btns.a:
            if QUICK_TIMER_SETTING != -1:
                CURRENT_STATE = QUICK_TIMER_RUNNING_STATE
                # quick_timer_running_layout
                minitft.display.show(quick_timer_running_layout.view)
                prev_btns = buttons
                TIMER_TARGET_TIME = time.monotonic() + QUICK_TIMER_SETTING
                print(str(int(TIMER_TARGET_TIME - now)))
                quick_timer_time_left_lbl.view.color = 0x4472c4
                quick_timer_time_left_lbl.view.text = format_min_sec(int(TIMER_TARGET_TIME - now))

        if buttons.b and not prev_btns.b:
            CURRENT_STATE = MAIN_MENU_STATE
            minitft.display.show(main_menu_layout.view)
            prev_btns = buttons
            TIMER_TARGET_TIME = -1
            QUICK_TIMER_SETTING = -1
            reset_lbls()

    if CURRENT_STATE == QUICK_TIMER_RUNNING_STATE:

        if now >= TIMER_TARGET_TIME:
            CURRENT_STATE = QUICK_TIMER_FINISHED_STATE
        else:

            if format_min_sec(int(TIMER_TARGET_TIME - now)) != quick_timer_time_left_lbl.view.text:
                quick_timer_time_left_lbl.view.text = format_min_sec(int(TIMER_TARGET_TIME - now))
        if buttons.a and not prev_btns.a:
            print("paused")
            CURRENT_STATE = QUICK_TIMER_PAUSED_STATE
            prev_btns = buttons
            PAUSE_START_TIME = now
            quick_timer_time_left_lbl.view.color = 0xed7d31

    if CURRENT_STATE == QUICK_TIMER_PAUSED_STATE:
        if buttons.a and not prev_btns.a:
            print("resumed")
            CURRENT_STATE = QUICK_TIMER_RUNNING_STATE
            prev_btns = buttons
            TIMER_TARGET_TIME += now - PAUSE_START_TIME
            quick_timer_time_left_lbl.view.color = 0x4472c4

        if buttons.b and not prev_btns.b:
            CURRENT_STATE = MAIN_MENU_STATE
            minitft.display.show(main_menu_layout.view)
            prev_btns = buttons
            TIMER_TARGET_TIME = -1
            QUICK_TIMER_SETTING = -1
            reset_lbls()

    if CURRENT_STATE == CUSTOM_TIMER_MENU_STATE:
        if buttons.up and not prev_btns.up:
            CUSTOM_TIMER_SETTING += 1

        if buttons.right and not prev_btns.right:
            CUSTOM_TIMER_SETTING += 5

        if buttons.down and not prev_btns.down:
            CUSTOM_TIMER_SETTING -= 1

        if buttons.left and not prev_btns.left:
            CUSTOM_TIMER_SETTING -= 5

        if CUSTOM_TIMER_SETTING < 0:
            CUSTOM_TIMER_SETTING = 0

        if quick_timer_time_left_lbl.view.text != CUSTOM_TIMER_SETTING:
            custom_timer_setting_lbl.view.text = str(CUSTOM_TIMER_SETTING)

        if buttons.a and not prev_btns.a:
            if CUSTOM_TIMER_SETTING != 0:
                CURRENT_STATE = CUSTOM_TIMER_RUNNING_STATE
                # quick_timer_running_layout
                minitft.display.show(quick_timer_running_layout.view)
                prev_btns = buttons
                TIMER_TARGET_TIME = time.monotonic() + CUSTOM_TIMER_SETTING * 60
                print(str(int(TIMER_TARGET_TIME - now)))
                quick_timer_time_left_lbl.view.color = 0x70ad47
                quick_timer_time_left_lbl.view.text = format_min_sec(int(TIMER_TARGET_TIME - now))

        if buttons.b and not prev_btns.b:
            CURRENT_STATE = MAIN_MENU_STATE
            minitft.display.show(main_menu_layout.view)
            prev_btns = buttons
            TIMER_TARGET_TIME = -1
            CUSTOM_TIMER_SETTING = 0
            reset_lbls()

    if CURRENT_STATE == CUSTOM_TIMER_RUNNING_STATE:
        if now >= TIMER_TARGET_TIME:
            CURRENT_STATE = CUSTOM_TIMER_FINISHED_STATE
        else:
            if format_min_sec(int(TIMER_TARGET_TIME - now)) != quick_timer_time_left_lbl.view.text:
                quick_timer_time_left_lbl.view.text = format_min_sec(int(TIMER_TARGET_TIME - now))

        if buttons.a and not prev_btns.a:
            print("paused")
            CURRENT_STATE = CUSTOM_TIMER_PAUSED_STATE
            prev_btns = buttons
            PAUSE_START_TIME = now
            quick_timer_time_left_lbl.view.color = 0xed7d31

    if CURRENT_STATE == CUSTOM_TIMER_PAUSED_STATE:
        if buttons.a and not prev_btns.a:
            print("resumed")
            CURRENT_STATE = CUSTOM_TIMER_RUNNING_STATE
            prev_btns = buttons
            TIMER_TARGET_TIME += now - PAUSE_START_TIME
            quick_timer_time_left_lbl.view.color = 0x70ad47

        if buttons.b and not prev_btns.b:
            CURRENT_STATE = MAIN_MENU_STATE
            minitft.display.show(main_menu_layout.view)
            prev_btns = buttons
            TIMER_TARGET_TIME = -1
            CUSTOM_TIMER_SETTING = 0

    if CURRENT_STATE == STOPWATCH_PAUSED_STATE:
        if buttons.a and not prev_btns.a:
            print("resumed")
            CURRENT_STATE = STOPWATCH_RUNNING_STATE
            prev_btns = buttons
            STOPWATCH_START_TIME += now - PAUSE_START_TIME
            stopwatch_time_lbl.view.color = 0x70ad47

        if buttons.b and not prev_btns.b:
            CURRENT_STATE = MAIN_MENU_STATE
            minitft.display.show(main_menu_layout.view)
            prev_btns = buttons
            TIMER_TARGET_TIME = -1
            CUSTOM_TIMER_SETTING = 0

    if CURRENT_STATE == STOPWATCH_RUNNING_STATE:
        print(format_min_sec(int(now - STOPWATCH_START_TIME)))
        if stopwatch_time_lbl.view.text != format_min_sec(int(now - STOPWATCH_START_TIME)):
            print("setting time in label")
            stopwatch_time_lbl.view.text = format_min_sec(int(now - STOPWATCH_START_TIME))

        if buttons.a and not prev_btns.a:
            print("paused")
            CURRENT_STATE = STOPWATCH_PAUSED_STATE
            prev_btns = buttons
            PAUSE_START_TIME = now
            stopwatch_time_lbl.view.color = 0xed7d31

    if buttons.select:
        pass

    if buttons.a:
        pass

    if buttons.b:
        pass

    prev_btns = buttons
    time.sleep(0.001)
